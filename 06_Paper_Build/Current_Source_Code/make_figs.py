import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, pandas as pd, numpy as np
plt.rcParams.update({'font.family':'serif','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
import os
from paths import FIG_FINAL, RESULTS
O=os.environ.get('MBSE_FIG_OUT', FIG_FINAL)+os.sep
os.makedirs(O, exist_ok=True)
col={'A1':'#1B365D','A2':'#2E7D9E','N':'#C0541A'}
# porosity
t=[.30,.35,.40,.45,.50,.55,.60]
P={'A1':[68.0,63.1,58.3,56.1,52.4,48.0,42.6],'A2':[68.1,63.2,59.5,54.6,50.2,46.5,42.1],'N':[74.4,70.4,66.7,62.9,59.2,55.8,52.3]}
fig,ax=plt.subplots(figsize=(4.6,3.2))
for k,v in P.items(): ax.plot(t,v,'o-',color=col[k],label=k,ms=3.5,lw=1.3)
ax.axhline(53,color='gray',ls='--',lw=.8); ax.axvline(.5,color='gray',ls=':',lw=.8)
for k,tb in {'A1':.487,'A2':.472,'N':.587}.items(): ax.plot(tb,53,'s',color=col[k],mfc='white',ms=6)
ax.text(.302,53.6,'target 53%',fontsize=7.5,color='gray'); ax.text(.503,70,'Case A\nt = 0.50 mm',fontsize=7.5,color='gray')
ax.set_xlabel('Strut thickness t (mm)'); ax.set_ylabel('Planar porosity (%)'); ax.legend(frameon=False,title='Cell')
fig.tight_layout(); fig.savefig(O+'porosity.png',dpi=300)
# convergence
d=pd.read_csv(os.path.join(RESULTS,'convergence_results.csv')); d['Screw']=d.Screw.str[:-6]
fig,axs=plt.subplots(1,3,figsize=(7.2,2.6))
mk={'AS1':'#1B365D','AS2':'#2E7D9E','NS':'#C0541A'}
for k,g in d.groupby('Screw'):
    g=g.sort_values('Elements')
    axs[0].plot(g.Elements/1e3,g.Fy_N/g.Fy_N.iloc[0]*100-100,'o-',color=mk[k],label=k,ms=3.5)
    axs[1].plot(g.Elements/1e3,g.MaxMises_MPa/1e3,'o-',color=mk[k],ms=3.5)
    axs[2].plot(g.Elements/1e3,g.CollarZoneMaxMises_MPa/1e3,'o-',color=mk[k],ms=3.5)
for a,y in zip(axs,['Change in $F_y$ vs coarsest mesh (%)','Peak von Mises, whole screw (GPa)','Peak von Mises, collar zone (GPa)']):
    a.set_xlabel('Elements (thousand)'); a.set_ylabel(y,fontsize=8)
axs[0].legend(frameon=False); fig.tight_layout(); fig.savefig(O+'convergence.png',dpi=300)
# graded figure
g=pd.read_csv(os.path.join(RESULTS,'graded_results.csv')); e=pd.read_csv(os.path.join(RESULTS,'graded_extra.csv'),header=None,names=['Screw','MeshLevel','Ramp','Vol'])
g=g.merge(e,on=['Screw','MeshLevel'])
U=g[g.Screw=='AS2U_screw'].sort_values('MeshLevel',ascending=False); G=g[g.Screw=='AS2G_screw'].sort_values('MeshLevel',ascending=False)
fig,axs=plt.subplots(1,3,figsize=(7.2,2.6))
y=np.linspace(4,25,200); tc,td,l,Yh=0.472,0.65,6.0,25.0
tt=tc+(td-tc)*np.clip((y-(Yh-l))/l,0,1)
axs[0].plot(y,tt,color='#2E7D9E',lw=1.6,label='AS2G'); axs[0].plot(y,np.full_like(y,tc),color='#C0541A',lw=1.6,ls='--',label='AS2U')
axs[0].set_xlabel('Axial position y (mm)'); axs[0].set_ylabel('Strut thickness (mm)'); axs[0].legend(frameon=False); axs[0].set_ylim(.4,.7)
x=np.arange(4); lab=['L6','L5','L4','L3']; w=.38
axs[1].bar(x-w/2,U.CollarZoneMaxMises_MPa/1e3,w,color='#C0541A',label='AS2U collar zone'); axs[1].bar(x+w/2,G.CollarZoneMaxMises_MPa/1e3,w,color='#2E7D9E',label='AS2G collar zone')
axs[1].set_xticks(x); axs[1].set_xticklabels(lab); axs[1].set_ylabel('Peak von Mises, 24–26.5 mm (GPa)',fontsize=8); axs[1].set_xlabel('Mesh level'); axs[1].legend(frameon=False,fontsize=7)
axs[2].bar(x-w/2,U.Ramp/1e3,w,color='#C0541A',label='AS2U ramp zone'); axs[2].bar(x+w/2,G.Ramp/1e3,w,color='#2E7D9E',label='AS2G ramp zone')
axs[2].set_ylim(0,10); axs[1].set_ylim(0,8); axs[2].set_xticks(x); axs[2].set_xticklabels(lab); axs[2].set_ylabel('Peak von Mises, 19–24 mm (GPa)',fontsize=8); axs[2].set_xlabel('Mesh level'); axs[2].legend(frameon=False,fontsize=7)
fig.tight_layout(); fig.savefig(O+'graded.png',dpi=300)

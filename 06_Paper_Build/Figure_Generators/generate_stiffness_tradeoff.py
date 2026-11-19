"""
Generate a stiffness + stress-shield infographic figure for the paper.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

fig, axs = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)

NAVY   = '#1B365D'
TEAL   = '#2E7D9E'
GREEN  = '#2D6A4F'
RED    = '#C0392B'
ORANGE = '#E67E22'
LGRAY  = '#ECF0F1'
WHITE  = '#FFFFFF'

# ---- Left: Stiffness bar chart with solid Ti reference line ----
ax = axs[0]
labels  = ['AS1\n(Chevron)', 'AS2\n(Hourglass)', 'NS\n(Hexagonal)', 'Solid Ti\n(Reference)']
vals    = [15.64, 12.19, 5.04, 40.0]
colors  = [NAVY, GREEN, TEAL, RED]
hatches = ['', '', '', '//']

bars = ax.bar(labels[:3], vals[:3], color=colors[:3], width=0.5,
              edgecolor='white', linewidth=1.4, zorder=3)

ax.axhline(40.0, color=RED, linewidth=2.2, linestyle='--', label='Solid Ti Screw (~40 kN/mm)', zorder=4)
ax.axhspan(10, 18, alpha=0.15, color=GREEN, label='Bone Stiffness Window (10-18 kN/mm)')

for bar, v in zip(bars, vals[:3]):
    ax.text(bar.get_x() + bar.get_width()/2, v + 0.5,
            f'{v:.2f} kN/mm', ha='center', va='bottom',
            fontsize=10, fontweight='bold', color=NAVY)

ax.set_ylabel('Axial Tensile Stiffness (kN/mm)', fontsize=11, fontweight='bold', color=NAVY)
ax.set_title('(a) Structural Stiffness vs. Stress-Shielding Window', fontsize=11, fontweight='bold', color=NAVY)
ax.set_ylim(0, 46)
ax.set_facecolor('#FAFCFF')
ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='gray')
ax.legend(loc='upper right', fontsize=8.5, frameon=True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# annotation arrows
ax.annotate('48.7% lower than\nsolid Ti screw',
            xy=(0, 15.64), xytext=(0.6, 32),
            fontsize=8.5, color=NAVY,
            arrowprops=dict(facecolor=NAVY, shrink=0.08, width=1.5, headwidth=7))
ax.annotate('AS2: Ideal match\nto bone modulus',
            xy=(1, 12.19), xytext=(0.3, 22),
            fontsize=8.5, color=GREEN,
            arrowprops=dict(facecolor=GREEN, shrink=0.08, width=1.5, headwidth=7))

# ---- Right: Stacked retention vs stress tradeoff scatter ----
ax2 = axs[1]

x_stress  = [11163.19, 5100.61, 4195.58]
y_force   = [3128.21,  2437.56, 1008.00]
sc_colors = [NAVY, GREEN, TEAL]
markers   = ['o', 's', '^']
labels2   = ['AS1 (Chevron)', 'AS2 (Hourglass)', 'NS (Hexagonal)']

for xi, yi, ci, mi, li in zip(x_stress, y_force, sc_colors, markers, labels2):
    ax2.scatter(xi, yi, s=280, color=ci, marker=mi, zorder=5, label=li, edgecolors='white', linewidths=1.5)

ax2.annotate('AS1: Max Pullout\nbut High Stress', xy=(11163, 3128), xytext=(8500, 2700),
             fontsize=8.5, color=NAVY,
             arrowprops=dict(facecolor=NAVY, shrink=0.05, width=1.2, headwidth=6))
ax2.annotate('AS2: Optimal\nTrade-off', xy=(5100, 2437), xytext=(5500, 1900),
             fontsize=8.5, color=GREEN,
             arrowprops=dict(facecolor=GREEN, shrink=0.05, width=1.2, headwidth=6))
ax2.annotate('NS: Conventional\nBaseline', xy=(4195, 1009), xytext=(5800, 700),
             fontsize=8.5, color=TEAL,
             arrowprops=dict(facecolor=TEAL, shrink=0.05, width=1.2, headwidth=6))

# "ideal zone" - low stress, high force
ax2.axhspan(2000, 3200, alpha=0.07, color=GREEN)
ax2.axvspan(0, 7000, alpha=0.07, color=GREEN)
ax2.text(1000, 2600, 'Ideal\nZone', fontsize=9, color=GREEN, fontstyle='italic', alpha=0.8)

ax2.set_xlabel('Peak von Mises Stress (MPa)', fontsize=11, fontweight='bold', color=NAVY)
ax2.set_ylabel('Axial Pullout Force Fy (N)', fontsize=11, fontweight='bold', color=NAVY)
ax2.set_title('(b) Pullout Force vs. Peak Stress Trade-Off', fontsize=11, fontweight='bold', color=NAVY)
ax2.set_facecolor('#FAFCFF')
ax2.yaxis.grid(True, linestyle='--', alpha=0.5, color='gray')
ax2.xaxis.grid(True, linestyle='--', alpha=0.5, color='gray')
ax2.legend(loc='upper right', fontsize=9, frameon=True)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

plt.tight_layout(pad=2.0)
plt.savefig('D:/MBSE/Paper/figures/stiffness_tradeoff.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print('stiffness_tradeoff.png generated.')

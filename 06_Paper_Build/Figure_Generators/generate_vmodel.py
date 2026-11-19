"""Generate a clean V-Model diagram for the paper."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(14, 8), dpi=300)
ax.set_xlim(0, 14)
ax.set_ylim(0, 8)
ax.axis('off')

NAVY   = '#1B365D'
TEAL   = '#2E7D9E'
GREEN  = '#2D6A4F'
ORANGE = '#C0541A'
LGRAY  = '#F0F4F8'
WHITE  = '#FFFFFF'

left_boxes = [
    (1.0, 7.0, 'L1: Stakeholder Needs\n(Surgeon, Patient, Manufacturer)', NAVY),
    (0.5, 5.5, 'L2: System Requirements\n(FR-01..FR-04, NFR-01..NFR-04)', TEAL),
    (0.2, 4.0, 'L3: Functional Architecture\n(Torque, Tension, Expansion, Ingrowth)', TEAL),
    (0.0, 2.5, 'L4: Subsystem Design\n(Head, Collar, Core, Thread)', GREEN),
    (0.0, 1.0, 'L5: Parametric CAD\n(A1, A2, N - Fusion 360 Python API)', GREEN),
]

right_boxes = [
    (10.0, 7.0, 'R1: Clinical Validation\n(Bone Block Pullout Test)', NAVY),
    (10.5, 5.5, 'R2: System Verification\n(Pullout Force >= 1000 N)', TEAL),
    (10.8, 4.0, 'R3: Functional Verification\n(Effective NPR, Radial Expansion)', TEAL),
    (11.0, 2.5, 'R4: Subsystem Verification\n(Collar Stress, Torsional Yield)', GREEN),
    (11.0, 1.0, 'R5: Unit-Cell Verification\n(Porosity, Strut, Overhang)', GREEN),
]

impl_box = (5.5, 0.1, 'Implementation\nBRep CAD + COMSOL Java API\nHeadless Batch Simulation', ORANGE)

BOX_W = 2.8
BOX_H = 0.9

def draw_box(ax, x, y, text, color):
    rect = mpatches.FancyBboxPatch(
        (x, y), BOX_W, BOX_H,
        boxstyle='round,pad=0.08',
        facecolor=color, edgecolor='white', linewidth=1.5, zorder=3
    )
    ax.add_patch(rect)
    ax.text(x + BOX_W/2, y + BOX_H/2, text,
            ha='center', va='center', fontsize=7.0, color=WHITE,
            fontweight='bold', zorder=4, wrap=True,
            multialignment='center')

for (x, y, t, c) in left_boxes:
    draw_box(ax, x, y, t, c)
for (x, y, t, c) in right_boxes:
    draw_box(ax, x, y, t, c)

ix, iy, it, ic = impl_box
draw_box(ax, ix, iy, it, ic)

# Left-side cascade arrows
left_xs = [lx + BOX_W/2 for (lx, ly, lt, lc) in left_boxes]
left_ys = [ly for (lx, ly, lt, lc) in left_boxes]
for i in range(len(left_boxes)-1):
    ax.annotate('', xy=(left_xs[i+1], left_ys[i+1]+BOX_H),
                xytext=(left_xs[i], left_ys[i]),
                arrowprops=dict(arrowstyle='->', color=NAVY, lw=1.8), zorder=2)

# Right-side cascade arrows (upward)
right_xs = [rx + BOX_W/2 for (rx, ry, rt, rc) in right_boxes]
right_ys = [ry for (rx, ry, rt, rc) in right_boxes]
for i in range(len(right_boxes)-1):
    ax.annotate('', xy=(right_xs[i], right_ys[i]+BOX_H),
                xytext=(right_xs[i+1], right_ys[i+1]),
                arrowprops=dict(arrowstyle='->', color=NAVY, lw=1.8), zorder=2)

# Bottom V-connection: L5 -> impl -> R5
lx5, ly5 = left_boxes[-1][0]+BOX_W/2, left_boxes[-1][1]
rx5, ry5 = right_boxes[-1][0]+BOX_W/2, right_boxes[-1][1]
impl_cx = ix + BOX_W/2

ax.annotate('', xy=(impl_cx - 0.4, iy + BOX_H),
            xytext=(lx5, ly5),
            arrowprops=dict(arrowstyle='->', color=ORANGE, lw=2.0), zorder=2)
ax.annotate('', xy=(rx5, ry5+BOX_H),
            xytext=(impl_cx + 0.4, iy + BOX_H),
            arrowprops=dict(arrowstyle='->', color=ORANGE, lw=2.0), zorder=2)

# Horizontal verification links
h_colors = [NAVY, TEAL, TEAL, GREEN, GREEN]
labels = ['Validate', 'Verify Sys', 'Verify Func', 'Verify Subsys', 'Verify Cell']
for i in range(len(left_boxes)):
    lx = left_boxes[i][0] + BOX_W
    ly = left_boxes[i][1] + BOX_H/2
    rx = right_boxes[i][0]
    ry = right_boxes[i][1] + BOX_H/2
    ax.annotate('', xy=(rx, ry), xytext=(lx, ly),
                arrowprops=dict(arrowstyle='<->', color=h_colors[i], lw=1.2,
                                linestyle='dashed'), zorder=2)
    mx = (lx + rx)/2
    my = (ly + ry)/2
    ax.text(mx, my+0.12, labels[i], ha='center', va='bottom',
            fontsize=6.5, color=h_colors[i], fontstyle='italic')

ax.set_title('Systems Engineering V-Model: MBSE Framework for Auxetic Bone Screw Design & Verification',
             fontsize=11, fontweight='bold', color=NAVY, pad=10)

plt.tight_layout()
plt.savefig('D:/MBSE/Paper/figures/v_model_diagram.png', dpi=300, bbox_inches='tight',
            facecolor='white')
plt.close()
print('v_model_diagram.png generated.')

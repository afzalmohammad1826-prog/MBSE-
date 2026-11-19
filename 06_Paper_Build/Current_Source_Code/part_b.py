# -*- coding: utf-8 -*-
"""Sections 5-8 of the final manuscript (verification, traceability, discussion, conclusions)."""
from part_a import *
import os
import pandas as pd
from paths import RESULTS, DRAFT3

conv = pd.read_csv(os.path.join(RESULTS,'convergence_results.csv'))
conv['Screw'] = conv.Screw.str.replace('_screw', '')


def c(screw, lvl, col):
    return float(conv[(conv.Screw == screw) & (conv.MeshLevel == lvl)][col].iloc[0])


def f0(x):
    return f"{x:,.0f}"


def build_methods(doc):
    add_wiley_heading(doc, "5", "Verification by Simulation")
    add_wiley_subheading(doc, "5.1  Finite element model")
    para(doc,
         "Each screw was analysed in COMSOL Multiphysics 6.2 as a displacement-controlled axial tensile test of the "
         "isolated screw. The STEP geometry from Fusion 360 was imported and merged into one solid with a repair "
         "tolerance of 10⁻⁵ m. All displacement components were fixed on the faces of the conical tip, and an axial "
         "displacement U_y = +0.20 mm (U_x = U_z = 0) was prescribed on the faces of the head. The boundary faces were "
         "picked by coordinate boxes, so the same rule applies to every screw. All three screws have a strut thickness of "
         "0.50 mm (Case A), so their porosities are 52.4% (AS1), 50.2% (AS2) and 59.2% (NS). The material was Ti-6Al-4V ELI, treated as "
         "isotropic and linear elastic (Table 3). The mesh used quadratic tetrahedra, and the system was solved with the "
         "PARDISO direct solver. Each run took a few minutes on a 12-core workstation with 32 GB of memory. The "
         "axial stiffness follows from the reaction force:")
    equation(doc, "K = F_y / U_y", 4)
    table(doc, 3, "Material properties used in the model, with the specified minima for wrought Ti-6Al-4V ELI.",
          ["Property", "Value in model", "Specified minimum (wrought, ASTM F136)"],
          [["Young's modulus E", "110 GPa", "not specified"],
           ["Poisson's ratio ν", "0.33", "not specified"],
           ["Yield strength σ_y (0.2%)", "850 MPa", "795 MPa"],
           ["Ultimate strength σ_uts", "960 MPa", "860 MPa"]],
          widths=[2.0, 1.6, 2.6],
          note="The model values for yield and ultimate strength are typical values. SLM-built lattices must be tested "
               "because their properties depend on process, build direction and post-processing [22].")
    para(doc,
         "The model has no bone, no contact or friction, no insertion preload and no cyclic load. The reaction force "
         "is therefore the force needed to stretch the screw by 0.20 mm. It measures the axial stiffness of the "
         "structure. It is not the pullout force of a screw in bone, and by Equation 4 it carries the same information as "
         "K. We call it the axial reaction force in the rest of the paper.")

    add_wiley_subheading(doc, "5.2  Mesh convergence")
    para(doc,
         "Our first runs used a single mesh (COMSOL size level 6, called Coarse). This is not enough to judge a result, so we "
         "repeated every screw on five levels, from level 7 (Coarser) to level 3 (Finer). The mesh grew from about "
         "23,000 to about 300,000 elements. Table 4 and Figure 4 give the results.")
    rows = []
    for s, nm in [('AS1', 'AS1 (chevron)'), ('AS2', 'AS2 (hourglass)'), ('NS', 'NS (hexagon)')]:
        f6, f3 = c(s, 6, 'Fy_N'), c(s, 3, 'Fy_N')
        rows.append([nm, f"{f6:,.1f}", f"{f3:,.1f}", f"{(f3/f6-1)*100:.1f}%",
                     f"{f3/0.2/1000:.2f}",
                     f"{c(s,6,'MaxMises_MPa'):,.0f}", f"{c(s,3,'MaxMises_MPa'):,.0f}",
                     f"{c(s,3,'CollarZoneMaxMises_MPa'):,.0f}"])
    table(doc, 4, "Mesh study. Axial reaction force F_y at the original mesh (level 6) and the finest mesh (level 3), "
                  "stiffness on the finest mesh, and peak von Mises stress.",
          ["Screw", "F_y level 6 (N)", "F_y level 3 (N)", "Change", "K level 3 (kN/mm)",
           "Peak σ level 6 (MPa)", "Peak σ level 3 (MPa)", "Collar-zone σ level 3 (MPa)"],
          rows, font=8.5,
          note="Collar zone: axial window 24.0 to 26.5 mm, which contains the last lattice row, the collar and the taper.")
    add_wiley_figure(doc, "convergence.png", 4,
                     "Mesh study for the three screws. (a) Change in axial reaction force relative to the coarsest mesh. "
                     "(b) Peak von Mises stress over the whole screw. (c) Peak von Mises stress in the collar zone.",
                     width_in=6.4)
    para(doc,
         "The force behaves well. It falls steadily as the mesh is refined, by 1.5% for AS1, 3.6% for AS2 and 10.2% for "
         "NS between the coarsest and the finest mesh. The drop between levels 4 and 3 is only 0.3%, 0.5% and 1.1%, "
         "so the values are close to settled. The results are presented with the finest-mesh numbers, AS1 3,096 N, AS2 2,382 N "
         "and NS 958 N, together with the original level-6 numbers. The ordering AS1 > AS2 > NS is the same on every mesh.")
    para(doc,
         "The stress does not behave. The whole-screw peak for AS1 jumps between 11 and 30 GPa and never settles, and "
         "AS2 and NS drift upwards or sideways. This is the behaviour expected from a stress singularity, a sharp corner "
         "where linear elasticity predicts a stress that grows without bound as the mesh is refined. The stress values "
         "are also far above the yield strength, 850 MPa, by a factor of 4 to more than 20. A linear-elastic stress above "
         "yield has no direct physical meaning, because a real screw would yield and redistribute the load. We therefore "
         "do not report any peak stress as a prediction of safety. We use the stress only to rank the topologies, "
         "and only where the ranking is stable.")
    para(doc,
         "The collar-zone stress is more useful. It rises slowly with refinement but keeps the same ordering on every mesh from "
         "level 6 to level 3: AS1 (9,800 to 12,100 MPa), then AS2 (4,600 to 6,300 MPa), then NS (about 1,100 to 1,600 "
         "MPa). For AS2 the whole-screw peak lies inside this window on all three finest meshes. For this screw the "
         "highest stress is therefore found at the transition between lattice and head, which agrees with the location "
         "reported for fatigue failure in [9]. The window also contains the end of the lattice, so this result cannot "
         "separate the collar from the lattice end.")

    add_wiley_subheading(doc, "5.3  Force, stiffness and the fixation hypothesis")
    f = {s: c(s, 3, 'Fy_N') for s in ['AS1', 'AS2', 'NS']}
    para(doc,
         f"On the finest mesh AS1 carries {f['AS1']/f['NS']:.2f} times the force of NS and AS2 carries "
         f"{f['AS2']/f['NS']:.2f} times (for the original mesh the ratios are 3.10 and 2.42). AS2 keeps "
         f"{f['AS2']/f['AS1']*100:.0f}% of the AS1 force. The stiffnesses are {f['AS1']/0.2/1000:.1f}, "
         f"{f['AS2']/0.2/1000:.1f} and {f['NS']/0.2/1000:.1f} kN/mm. Force and stiffness are one result written twice, "
         "because the displacement is the same for all screws, and they should not be counted as separate evidence.")
    para(doc,
         "AS2 is the more strongly auxetic design (ν_eff = −0.41 against −0.22), yet AS1 carries more force. In this "
         "dataset the force follows the axial stiffness and not the size of ν_eff. There is no bone in the model, so "
         "radial expansion creates no contact pressure, and the idea that auxetic expansion improves grip is neither "
         "tested nor confirmed. Yao et al. found that the benefit of stronger auxeticity appears at matched modulus [6], "
         "while Barnett et al. found that low stiffness can also help [1]. AS1 and AS2 differ in both stiffness and "
         "ν_eff, so their effects cannot be separated here.")
    para(doc,
         "The requirement FR-02 also needs a second look. Its limit of 1,000 N is almost exactly the response of the "
         "control: NS gave 1,009 N on the original mesh and only 958 N on the finest one. A limit set at the control's "
         "own value cannot tell an auxetic screw from a conventional one. We recommend rewriting FR-02 as a pullout "
         "requirement in a bone analogue, stated relative to a non-auxetic control of equal porosity. Section 6 "
         "carries this change into the trace.")
    para(doc,
         "The comparison with NS is not at equal porosity. NS is more porous (59.2%) and is also the weakest screw. At the "
         "same porosity it would be stiffer, so the force ratios above probably overstate the advantage of the auxetic "
         "cells. Simulating the Case B geometries would remove this confounding and is the first item of future work. "
         "A check on stiffness is useful. A fully solid annular shaft with the S3 dimensions (cross-section "
         "16.96 mm²) and E = 110 GPa would have EA/L of about 89 kN/mm. The lattice screws are 6 to 19 times more "
         "compliant than this. Whether that compliance reduces stress shielding depends on the stiffness of the bone, "
         "and our model does not include bone, so we make no claim about shielding.")

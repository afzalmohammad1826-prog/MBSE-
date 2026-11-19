# -*- coding: utf-8 -*-
"""Graded-transition study, discussion and conclusions."""
from part_c import *


def build_graded(doc):
    add_wiley_heading(doc, "6", "Graded Transition Study")
    para(doc,
         "The collar hypothesis says that a smoother change in stiffness between the lattice and the head should relieve "
         "the transition. We tested one version of this idea with the generative design step of Section 4.3. A uniform "
         "AS2 screw (AS2U, t = 0.472 mm) was compared with a graded AS2 screw (AS2G) whose strut thickness rises "
         "linearly from 0.472 mm to 0.65 mm over the last 6.0 mm of the lattice (Equation 2 and Figure 5a). The two "
         "screws came from the same Fusion 360 script. Only the parameter GRADE_ON differed, so the comparison is clean. "
         "The loading, the boundary conditions and the four finest mesh levels (6 to 3) were the same as in Section 5.")
    para(doc,
         "The grading adds little material. The screw volume rises from 339.6 to 343.6 mm³, which is 1.2%. The "
         "results are in Table 5 and Figure 5. We report the finest mesh first and then say how the other meshes agree.")
    table(doc, 5, "Uniform (AS2U) and graded (AS2G) screws on the finest mesh (level 3), and the change due to grading.",
          ["Quantity", "AS2U", "AS2G", "Change"],
          [["Axial reaction force F_y (N)", "2,224", "2,341", "+5.3%"],
           ["Collar-zone peak stress, 24–26.5 mm (MPa)", "6,428", "5,229", "−18.7%"],
           ["Ramp-zone peak stress, 19–24 mm (MPa)", "6,116", "7,770", "+27.0%"],
           ["Whole-screw peak stress (MPa)", "6,932", "7,770", "+12.1%"],
           ["Screw volume (mm³)", "339.6", "343.6", "+1.2%"]],
          widths=[3.0, 1.0, 1.0, 0.9],
          note="All stresses are linear-elastic peaks and are used for comparison only.")
    add_wiley_figure(doc, "graded.png", 5,
                     "Graded transition study. (a) Strut thickness along the screw axis for AS2G (graded) and AS2U (uniform). "
                     "(b) Peak von Mises stress in the collar zone. (c) Peak von Mises stress in the ramp zone. "
                     "L6 to L3 are the four mesh levels, from coarse to fine.", width_in=6.4)
    para(doc,
         "Grading did what it was designed to do next to the head. The collar-zone stress is lower on every mesh, by "
         "37%, 18%, 9% and 19% from level 6 to level 3. The axial force also rises by about 5% on every mesh. Grading "
         "also had a cost. The peak stress in the ramp zone is higher on every mesh, by 29%, 51%, 24% and 27%, and "
         "on the two finest meshes the whole-screw peak of AS2G lies in this zone. The hot spot has moved from the "
         "head end of the lattice to the place where the thick and thin struts meet.")
    para(doc,
         "The result is negative but informative. It supports a cautious reading of the transition paradox: a stiffness step "
         "cannot be removed by moving it. A linear ramp over 6 mm still has an abrupt change in strut thickness at "
         "its start, and that change collects stress. The result does not show that grading is a bad idea. Longer or "
         "curved ramps and node fillets are the next things to try, and the model makes each of them a one-parameter "
         "change. The comparison also says nothing about fatigue life. It shows that the collar hypothesis "
         "cannot be confirmed or rejected by comparing linear peak stresses. A fatigue-based criterion, measured on "
         "as-built SLM lattices, is needed.")
    para(doc,
         "The uniform control also gives a sensitivity check on the baseline. AS2U (t = 0.472 mm) carries 2,224 N and "
         "AS2 from Section 5 (t = 0.50 mm) carries 2,382 N on the finest mesh. A 5.6% thinner strut therefore costs "
         "6.6% of the force. The force depends on strut thickness almost in proportion, so a Case B comparison at "
         "equal porosity will change the numbers in Table 4 by several per cent.")


def build_discussion(doc):
    add_wiley_heading(doc, "8", "Discussion")
    add_wiley_subheading(doc, "8.1  What the framework gave us")
    para(doc,
         "We return to the three research questions. For RQ1, the answer is yes. All geometry came from a parameter "
         "set in the model, and two new variants (the uniform control and the graded screw) needed one changed "
         "parameter each. The same applies to the mesh study, where the same batch script was run at five levels. This "
         "is the practical benefit of a digital thread: a question that would normally need a day of redrawing "
         "took one script change.")
    para(doc,
         "For RQ2, a simulation-only verification can rank the topologies by stiffness, and it can show whether a "
         "requirement is plausible. It cannot say anything about fixation in bone, fatigue life or safety. The "
         "unconverged stress is the clearest example. A single-mesh run gave a precise-looking number, 11,163 MPa for "
         "AS1, and the mesh study showed that this number had no meaning. A systems engineer who only checks "
         "whether a requirement has a linked simulation would have marked it as verified.")
    para(doc,
         "For RQ3, the trace was useful in four places. First, writing FR-02 into the model showed that its limit "
         "of 1,000 N equals the control's own response, so it cannot separate auxetic from conventional screws. Second, "
         "listing the verification case of NFR-01 showed that no result addressed the collar neck. This led to the "
         "collar-zone measure and to the graded study. Third, separating a link from its evidence made it clear that "
         "NFR-04 (traceability) had been met only formally. Fourth, tracing the geometry parameters back to their "
         "generating script exposed the strut-thickness question of Section 5. The finite element geometry came "
         "from a script with a fixed thickness of 0.50 mm, and not from the porosity-calibrated 0.472 to 0.587 mm "
         "values of Case B. An audit trail that was only a document would not have caught this.")
    add_wiley_subheading(doc, "8.2  Lessons for systems engineering practice")
    para(doc,
         "Four lessons carry over to other projects. Acceptance criteria must be able to discriminate: a limit equal to "
         "the control's response is not a requirement, and fixation targets should be stated relative to a baseline "
         "design. Each trace link should also carry its evidence level, because a link only says that a check exists, "
         "while the level says what the check can prove. Simulated, bench, validation and regulatory evidence should "
         "not share one status column. Third, the model should be verified before the design is. A mesh study checks "
         "the verification method itself and belongs in the model as a standard case. Finally, the generator should be "
         "versioned with the geometry. A STEP file without the script and parameter values that made it cannot be traced, "
         "and the porosity calibration and the simulated geometry must refer to the same parameters.")
    add_wiley_subheading(doc, "8.3  Limitations")
    para(doc,
         "The study has several limits. The simulations are linear elastic with one load case, no bone and no cyclic "
         "loading. Peak stresses are not converged and cannot be read as physical values. The finite element results are "
         "for the equal-thickness geometry (Case A) and do not give an equal-porosity comparison. The effective Poisson's "
         "ratios are from an earlier dataset and were not recomputed. Porosity is a planar value, and its relation to "
         "the volume porosity of the wrapped lattice is unknown. Material data are typical wrought values and not "
         "measured as-built SLM values. The A1 calibration entry is about one point inconsistent with the porosity curve. "
         "The 1.5 N·m torque limit (FR-03) and the safety factor of 1.5 (NFR-01) are design assumptions and are not taken from a standard. "
         "The effect of the collar on fatigue is a hypothesis. We did not search the literature in a systematic way.")
    add_wiley_subheading(doc, "8.4  Future work")
    para(doc,
         "The next steps are, in order: (1) simulate the Case B geometries for an equal-porosity comparison; "
         "(2) add fillets at the strut junctions, within SLM limits, and use elastoplastic material and geometric "
         "nonlinearity; (3) sweep the ramp length and shape and add a no-collar baseline; (4) measure as-built material "
         "properties and run tensile and torsion tests on printed screws; (5) run ASTM F543 pullout tests in a bone "
         "analogue [23]; and (6) build a bone-contact model and carry out fatigue tests. Steps 4 to 6 would move the "
         "evidence from level E1 to E2 and E3. The assumed torque limit should be replaced by the ASTM F543 requirement once the standard "
         "has been obtained and the screw has been tested.")


def build_conclusions(doc):
    add_wiley_heading(doc, "9", "Conclusions")
    para(doc,
         "This paper presented an MBSE framework for auxetic bone screws. SysML requirements, a four-subsystem "
         "architecture, a requirements-driven generative design step and a COMSOL workflow are connected by an explicit "
         "trace. Four conclusions follow.")
    add_bullet_p(doc, "(1)", "On the finest mesh, and for equal strut thickness, the AS1, AS2 and NS screws gave axial reaction "
                 "forces of 3,096, 2,382 and 958 N under a 0.20 mm displacement. The force changed by 1.5% to 10% over the mesh "
                 "study. This is a stiffness result for the isolated screw and not evidence of better fixation in bone.")
    add_bullet_p(doc, "(2)", "Peak von Mises stress did not converge and was 4 to more than 20 times the yield strength. It was used only "
                 "to rank the screws. The collar-zone ranking AS1 > AS2 > NS was stable on every mesh.")
    add_bullet_p(doc, "(3)", "Grading the strut thickness over a 6 mm ramp lowered the collar-zone stress by about 19% and raised the force "
                 "by 5%, but moved the stress hot spot into the ramp. The stiffness step was moved and not removed.")
    add_bullet_p(doc, "(4)", "All eight requirements are linked, but the evidence is simulated, and FR-03 and NFR-01 are open. The trace "
                 "exposed a weak acceptance criterion (FR-02), a missing check at the collar neck and a geometry-provenance gap.")
    para(doc,
         "For systems engineers, the main point is that a model-based trace is most valuable when it shows what the "
         "evidence cannot prove. Physical testing and a bone-contact model are the necessary next steps before any "
         "fixation or fatigue claim can be made.")

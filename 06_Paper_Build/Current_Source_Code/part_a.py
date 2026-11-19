# -*- coding: utf-8 -*-
"""Sections 1-4 of the final manuscript (introduction, background, framework, generative design)."""
from paper_helpers import *
import paper_helpers as H

TITLE = ("A Model-Based Systems Engineering Framework for Requirements-Driven "
         "Design and Verification of Auxetic Bone Screws")

ABSTRACT = (
    "Auxetic bone screws have a porous core with a negative Poisson's ratio, so the core widens when the screw is "
    "pulled, which should improve grip. The same compliant core, though, creates a stiffness "
    "step where it meets the solid head, and fatigue life is predicted to be shortest at that junction. We call this "
    "the auxetic transition paradox. Screw designs are developed through separate CAD and finite element "
    "studies with no formal link to requirements. This paper presents a model-based systems engineering (MBSE) "
    "framework for an auxetic screw. SysML models are combined with a V-model, the screw is split into four "
    "subsystems, and a generative design step builds the porous core from the requirements. "
    "Three unit cells (re-entrant chevron AS1, re-entrant hourglass AS2 and a hexagonal control NS) were generated "
    "at equal strut thickness and analysed in COMSOL Multiphysics 6.2 under a 0.20 mm tensile displacement. On the "
    "finest of five meshes the axial reaction force was 3,096 N for AS1, 2,382 N for AS2 and 958 N for NS, and the "
    "order never changed. Peak stress did not converge and was used only to rank. A graded variant of "
    "AS2, made by changing one parameter, lowered the stress next to the head by about 19% but moved the "
    "hot spot into the graded zone. All eight requirements are linked to verification cases, yet the evidence is "
    "simulated only, and two requirements stay open. The trace exposed a weak acceptance criterion and a missing "
    "check at the collar neck."
)

KEYWORDS = ("model-based systems engineering | SysML | generative design | auxetic metamaterials | "
            "bone screw | requirements traceability | finite element analysis")


def para(doc, text):
    return add_body_p(doc, text)


def table(doc, num, caption, header, rows, widths=None, note=None, font=9.0, align_first_left=True):
    add_wiley_table_caption(doc, num, caption)
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_booktabs_table_borders(t)
    for ci, h in enumerate(header):
        c = t.cell(0, ci)
        shade_cell(c, H_NAVY)
        set_cell_margins(c, top=80, bottom=80, left=80, right=80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.name = 'Calibri'
        r.font.size = Pt(font + 0.5)
        r.font.color.rgb = C_WHITE
    for ri, row in enumerate(rows):
        bg = H_WHITE if ri % 2 == 0 else H_LGRAY
        for ci, val in enumerate(row):
            c = t.cell(ri + 1, ci)
            shade_cell(c, bg)
            set_cell_margins(c, top=55, bottom=55, left=80, right=80)
            c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if (ci == 0 and align_first_left) or len(str(val)) > 28 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(val))
            r.font.name = 'Times New Roman'
            r.font.size = Pt(font)
            r.bold = (ci == 0)
    if widths:
        for row in t.rows:
            for ci, w in enumerate(widths):
                row.cells[ci].width = Inches(w)
    if note:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(10)
        r = p.add_run(note)
        r.italic = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)
        r.font.color.rgb = C_DGRAY
    else:
        sp = doc.add_paragraph()
        sp.paragraph_format.space_after = Pt(6)
    return t


def equation(doc, text, num):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(f"{text}        ({num})")
    r.font.name = 'Cambria Math'
    r.font.size = Pt(11)
    return p


def build_front(doc):
    banner_tbl = doc.add_table(rows=1, cols=1)
    banner_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    bc = banner_tbl.cell(0, 0)
    shade_cell(bc, H_NAVY)
    set_cell_margins(bc, top=120, bottom=120, left=240, right=240)
    bp = bc.paragraphs[0]
    br1 = bp.add_run("Systems Engineering  |  Research Article")
    br1.bold = True
    br1.font.name = 'Calibri'
    br1.font.size = Pt(12)
    br1.font.color.rgb = C_WHITE
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(6)

    tp = doc.add_paragraph()
    tp.paragraph_format.space_after = Pt(8)
    tr = tp.add_run(TITLE)
    tr.bold = True
    tr.font.name = 'Calibri'
    tr.font.size = Pt(18)
    tr.font.color.rgb = C_NAVY

    ap = doc.add_paragraph()
    ap.paragraph_format.space_after = Pt(10)
    ar = ap.add_run("G Mohammad Afzal\nRoll No. ME23B2014")
    ar.font.name = 'Times New Roman'
    ar.font.size = Pt(10.5)
    ar.font.color.rgb = C_DGRAY

    p = doc.add_paragraph()
    r = p.add_run("ABSTRACT")
    r.bold = True
    r.font.name = 'Calibri'
    r.font.size = Pt(10.5)
    r.font.color.rgb = C_NAVY
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p2.paragraph_format.line_spacing = 1.1
    r2 = p2.add_run(ABSTRACT)
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(10.5)
    p3 = doc.add_paragraph()
    p3.paragraph_format.space_after = Pt(8)
    rk = p3.add_run("KEYWORDS  ")
    rk.bold = True
    rk.font.name = 'Calibri'
    rk.font.size = Pt(9.5)
    rk.font.color.rgb = C_NAVY
    rk2 = p3.add_run(KEYWORDS)
    rk2.font.name = 'Calibri'
    rk2.font.size = Pt(9.5)


def build_intro(doc):
    add_wiley_heading(doc, "1", "Introduction")
    add_wiley_subheading(doc, "1.1  Fixation failure and the auxetic idea")
    para(doc,
         "Bone screws are among the most common implants in orthopaedic surgery. When they fail, the usual cause is "
         "that the screw loosens or pulls out of the bone. Barnett et al. report that such migration or pullout accounts "
         "for roughly 10% of fracture-fixation failures [1]. Bone cement can improve grip, but it brings its own "
         "complications [2]. Auxetic structures offer another route. A material with a negative Poisson's ratio (NPR) "
         "gets wider when it is stretched [3–5]. If the core of a screw is built from auxetic cells, a pulling load "
         "should make the screw expand sideways and press harder against the bone around it.")
    para(doc,
         "Yao et al. placed six auxetic cells (A1 to A6) into screw bodies (AS1 to AS6) and compared them with a "
         "non-auxetic screw (NS) in finite element pullout models. AS2 gave the stiffest and strongest response and "
         "the highest pullout force, 1,185.93 N in high-density bone [2]. In a follow-up on pedicle screws, stronger "
         "auxeticity helped only when the elastic modulus was held equal, and the right modulus was a precondition for "
         "good performance [6]. Barnett et al. tested unthreaded polymer fasteners in bone analogue. A rotating-squares "
         "design carried 2.5 times the pullout load of its non-auxetic control, and the authors linked this to its low "
         "axial stiffness [1]. So stiffness and fixation do not move together in any simple way, and that shapes how we "
         "read our own results in Section 5.")

    add_wiley_subheading(doc, "1.2  The auxetic transition paradox")
    para(doc,
         "The feature that makes an auxetic screw attractive also weakens it. The porous, compliant core gives the "
         "radial expansion, but it also makes the step between the solid head and the porous shaft the most "
         "fatigue-critical part of the screw. We call this the auxetic transition paradox. Wang et al. found that "
         "re-entrant auxetic screws had a tensile fatigue strength about 43% lower than non-auxetic screws of the same "
         "51% porosity, although bone grew into them better [7]. Huang et al. studied the stress concentration in the "
         "auxetic porous screw [8]. In a later multiaxial simulation of ankle fusion (tibiotalocalcaneal arthrodesis), "
         "they estimated about 46,400 cycles to failure for the auxetic screw and 1,820,000 for the non-auxetic one, a "
         "97.5% reduction. The shortest life and the highest principal stress were next to the screw cap, where the screw "
         "meets the fixation plate, and the authors recommended redesigning that region [9]. These are simulated "
         "lives and not clinical failures, but they are the specific evidence that led us to give the head-to-shaft "
         "junction its own subsystem.")

    add_wiley_subheading(doc, "1.3  Gap and research questions")
    para(doc,
         "The auxetic screw studies we reviewed handle design through separate unit-cell, finite element and "
         "mechanical studies [2, 6, 7, 9]. We found no published work that links stakeholder needs, requirements, "
         "architecture, CAD and verification for an auxetic screw in one maintained model. This is based on a limited "
         "search and should be confirmed before submission. In MBSE, a maintained system model is the authoritative "
         "source of requirements, architecture and verification links [10, 11]. It is a natural way to close that gap. "
         "The paper asks three questions.")
    add_bullet_p(doc, "RQ1.", "Can SysML requirements and a V-model be used to drive the geometry of a porous auxetic implant "
                 "directly, so that design changes follow from model parameters?")
    add_bullet_p(doc, "RQ2.", "What can a simulation-only verification say about the requirements, and what can it not say?")
    add_bullet_p(doc, "RQ3.", "Does the explicit trace help to find and fix weak requirements early?")

    add_wiley_subheading(doc, "1.4  Contributions and scope")
    para(doc,
         "The paper makes four contributions. First, it gives a SysML and V-model framework that connects stakeholder "
         "needs, requirements, architecture blocks, CAD parameters and finite element cases for an auxetic bone screw. "
         "Second, it proposes a four-subsystem architecture in which the head-to-shaft transition is a verifiable "
         "subsystem of its own. Third, it adds a requirements-driven generative design step that partitions the design "
         "space, calibrates each topology to a target porosity and grades the strut thickness along the axis to test "
         "the transition collar. Fourth, it reports a simulation study of three unit cells with a mesh-convergence "
         "check, and says plainly which requirements the evidence supports.")
    para(doc,
         "The scope is limited on purpose. The work is computational. There is no bone in the model and no physical or "
         "fatigue test, so all conclusions are about the isolated screw.")


def build_background(doc):
    add_wiley_heading(doc, "2", "Background")
    add_wiley_subheading(doc, "2.1  Auxetic structures for fixation")
    para(doc,
         "Auxetic behaviour comes from cell geometry, not from the base material. Cellular auxetics are usually grouped "
         "into re-entrant, chiral, rotating-rigid and perforated-sheet families [4]. They have been proposed for joint, "
         "spinal and trauma surgery [5]. For screws, the relevant designs are the re-entrant families studied in "
         "[2, 6, 7]. We use the naming of Yao et al.: A1, A2 and N for the planar cells, and AS1, AS2 and NS for the "
         "screws built from them. Whether our A1 and A2 geometries match the original cells exactly has not been checked.")
    add_wiley_subheading(doc, "2.2  MBSE and SysML")
    para(doc,
         "MBSE puts a system model at the centre of development. The model supports specification, design, verification "
         "and configuration control, and it keeps the trace between them [10]. Its processes fit ISO/IEC/IEEE 15288:2023 "
         "and the INCOSE Systems Engineering Handbook [11, 12]. SysML is the standard modelling language [13], and "
         "version 2.0 was adopted by the Object Management Group in 2025 [14]. Our diagrams were drawn in Visual Paradigm. "
         "The constructs we use (requirements, blocks, ports, activities, and the satisfy, verify and deriveReqt "
         "relationships) exist in both SysML versions.")
    add_wiley_subheading(doc, "2.3  Design controls and simulation credibility")
    para(doc,
         "Design controls for medical devices are set out in ISO 13485:2016, clause 7.3 [15]. In the United States, the "
         "Quality Management System Regulation (QMSR) took effect on 2 February 2026. It incorporates ISO 13485 into "
         "21 CFR Part 820 and replaces the older design-control section 820.30 [16, 17]. We therefore use ISO 13485 "
         "clause 7.3 as the design-control reference, together with ISO 14971 for risk management [18]. For "
         "computational evidence, ASME V&V 40 and the FDA guidance of 2023 say that the credibility a model needs "
         "depends on how much the decision relies on it and how bad a wrong decision would be. They separate code "
         "verification, calculation verification and validation [19, 20]. We use these ideas in Section 5 to say what "
         "our simulations can and cannot support.")


def build_framework(doc):
    add_wiley_heading(doc, "3", "MBSE Framework")
    add_wiley_subheading(doc, "3.1  V-model decomposition")
    para(doc,
         "Figure 1 shows the framework. The left side of the V goes from stakeholder needs (L1: surgeon, patient, "
         "manufacturer) to system requirements (L2), functional architecture (L3), subsystem design (L4) and parametric "
         "CAD (L5). The right side goes back up: unit-cell checks (R5), subsystem checks (R4), functional checks (R3), "
         "system checks (R2) and clinical validation (R1). Dashed links show two-way traceability. At the bottom of the "
         "V, a Python script in Fusion 360 builds the CAD and a Java script drives COMSOL in batch mode. In this paper "
         "levels R5 to R2 are addressed by simulation, in part. R1, a bone-block pullout test, is planned and has not "
         "been done.")
    add_wiley_figure(doc, "v_model_diagram.png", 1,
                     "V-model of the framework. The left branch (L1 to L5) runs from needs to parametric CAD and the right "
                     "branch (R5 to R1) from unit-cell checks to validation. Only R5 to R2 are covered here, by simulation.",
                     width_in=5.6)
    add_wiley_subheading(doc, "3.2  SysML model suite")
    para(doc,
         "Four linked diagrams make up the model baseline (Figure 2). The requirements diagram holds the deriveReqt "
         "hierarchy. The block definition diagram shows the four subsystems. The internal block diagram shows the "
         "torque, load and kinematic ports between them. The activity diagram follows insertion and tensile expansion "
         "across four lanes: surgeon, head and collar, host bone, and porous core. Satisfy, verify and deriveReqt "
         "relationships connect the diagrams.")
    add_wiley_figure(doc, "FIG2_COMPOSITE", 2,
                     "SysML baseline: (a) requirements diagram, (b) block definition diagram, (c) internal block diagram, "
                     "(d) activity diagram. Text is small at print size and legible in the electronic file.",
                     width_in=6.3)


def build_requirements(doc):
    add_wiley_heading(doc, "4", "Requirements, Architecture and Generative Design")
    add_wiley_subheading(doc, "4.1  Stakeholder needs and requirements")
    para(doc,
         "Five stakeholder needs drive the design. The surgeon needs better primary fixation in osteoporotic bone "
         "without cement (SN-01) and standard driver engagement with predictable torque transfer (SN-02). The patient "
         "needs protection against fatigue fracture at the screw neck (SN-03). The manufacturer needs a design that can "
         "be printed by selective laser melting (SLM) with struts of at least 0.40 mm and open channels to remove "
         "powder (SN-04). The regulator needs design-control traceability under ISO 13485 clause 7.3 (SN-05). "
         "Table 1 lists the eight requirements derived from these needs.")
    table(doc, 1, "Requirements derived from the stakeholder needs (FR = functional, NFR = non-functional).",
          ["ID", "Requirement", "Acceptance criterion", "Need", "Subsystem"],
          [["FR-01", "Negative Poisson's ratio", "ν_eff < 0", "SN-01", "S3 Core"],
           ["FR-02", "Tensile fixation", "F_y ≥ 1,000 N at U_y = 0.20 mm", "SN-01", "Whole screw"],
           ["FR-03", "Insertion torque transfer", "τ ≥ 1.5 N·m, σ < σ_y", "SN-02", "S1 Head, S2 Collar"],
           ["FR-04", "Osseointegration porosity", "53.0% ± 5.0%", "SN-01", "S3 Core"],
           ["NFR-01", "Stress relief at transition", "Safety factor ≥ 1.5 at collar neck", "SN-03", "S2 Collar"],
           ["NFR-02", "Dimensional envelope", "D1 = 5.70 mm, L = 21.00 mm", "SN-02", "All"],
           ["NFR-03", "SLM manufacturability", "t ≥ 0.40 mm, pore ≥ 300 µm", "SN-04", "S3 Core"],
           ["NFR-04", "Traceability completeness", "No unlinked requirement", "SN-05", "System model"]],
          widths=[0.7, 1.7, 2.0, 0.55, 1.3],
          note="The 1.5 N·m torque and the safety factor of 1.5 are design assumptions set by the author. No standard gives them. Torsional acceptance values for bone screws come from testing to ASTM F543 [23] and the FDA performance criteria for non-spinal metallic bone screws [24].")
    add_wiley_subheading(doc, "4.2  Four subsystems")
    para(doc, "The screw is divided into four subsystems (Figure 2b).")
    add_bullet_p(doc, "S1 Drive head.", "A solid cylinder, D2 = 8.0 mm and 3.0 mm high, with a Torx or hex drive socket.")
    add_bullet_p(doc, "S2 Transition collar.", "A 1.0 mm conical taper followed by a 0.5 mm solid collar with 0.5 mm stress-relief "
                 "fillets. It sits between the solid head and the porous core.")
    add_bullet_p(doc, "S3 Porous core.", "An annular lattice shell (inner radius 1.65 mm, outer radius 2.85 mm, length 21.0 mm) "
                 "of 6 × 7 cells (circumferential × axial) of topology A1, A2 or N. With a cell size of 3.0 mm, six cells "
                 "span about 18 mm of circumference (2πR_o ≈ 17.9 mm) and seven cells span the 21.0 mm length.")
    add_bullet_p(doc, "S4 Threaded shell and tip.", "A helical thread (pitch 1.75 mm, depth 0.75 mm, flank angles 35° and 87°) "
                 "ending in a 3.5 mm conical tip.")
    para(doc,
         "The collar is our response to the transition paradox. By ending the lattice before the head, tapering the "
         "section over 1.0 mm and adding a filleted collar, the load should pass into the head along a longer and "
         "smoother path. NFR-01 turns this intention into a check. The collar is a design hypothesis. "
         "Section 6 tests it with simulation, and Section 8 explains why a simulation alone cannot settle it.")

    add_wiley_subheading(doc, "4.3  Generative design of the porous core")
    para(doc,
         "The porous core is not drawn by hand. It is generated from a small set of parameters that come from the "
         "requirements. We call this requirements-driven generative design. It is a rule-based generator and not a "
         "topology optimiser, and it has three parts.")
    para(doc,
         "First, the design space is split into three regions. The preserve region must stay solid: the head, the "
         "outer thread band and the tip. The keep-out region must stay empty: the central bore of radius 1.65 mm and "
         "the thread grooves. The design region is the annular shell between them, and this is where the generator "
         "places the lattice. The split comes straight from requirements NFR-02 and FR-03.")
    para(doc,
         "Second, each unit cell is defined on a flat grid of 3.0 mm × 3.0 mm and wrapped around the shell. The "
         "circumferential direction maps to the angle θ and the axial direction to the coordinate y. For a strut "
         "network with total centre-line length Σℓᵢ and strut width t, the solid area is about t·Σℓᵢ minus the overlap "
         "at the nodes, and the planar porosity is")
    equation(doc, "φ(t) = 1 − A_s(t) / (W·H)", 1)
    para(doc,
         "Porosity falls as t increases. Requirement FR-04 fixes the porosity target. For each topology, the "
         "generator solves φ(t*) = 0.530 by bisection on t. This inverse step is what lets the three topologies be "
         "compared fairly. Case A keeps the strut thickness equal at 0.50 mm, so porosity differs between topologies. "
         "Case B keeps the porosity equal, so the thickness differs (Table 2 and Figure 3). The finite element study in "
         "Section 5 uses Case A geometry. The Case B thicknesses were calibrated but not yet simulated.")
    table(doc, 2, "Planar porosity against strut thickness, and the thickness calibrated for 53% porosity (Case B).",
          ["Strut t (mm)", "A1 (%)", "A2 (%)", "N (%)"],
          [["0.30", "68.0", "68.1", "74.4"], ["0.35", "63.1", "63.2", "70.4"], ["0.40", "58.3", "59.5", "66.7"],
           ["0.45", "56.1", "54.6", "62.9"], ["0.50 (Case A)", "52.4", "50.2", "59.2"],
           ["0.55", "48.0", "46.5", "55.8"], ["0.60", "42.6", "42.1", "52.3"],
           ["Case B: calibrated t (mm)", "0.487", "0.472", "0.587"],
           ["Case B: reported porosity (%)", "52.4", "52.4", "53.1"]],
          widths=[2.2, 1.1, 1.1, 1.1],
          note="Interpolating the table gives about 53.4% for A1 at 0.487 mm and 52.7% for A2 at 0.472 mm. The A1 entry "
               "in Case B is therefore about one point low, and the bisection log should be re-exported to resolve this. "
               "Porosity is planar. The link to the volume porosity of the wrapped lattice has not been established.")
    add_wiley_figure(doc, "porosity.png", 3,
                     "Planar porosity against strut thickness for the three cells. Open squares mark the Case B thicknesses "
                     "that give 53% porosity. The dotted line marks Case A (t = 0.50 mm).", width_in=4.2)
    para(doc,
         "Third, the generator can vary the strut thickness along the screw axis. This is the lever for the collar "
         "hypothesis. With a graded thickness, the strut width grows from the core value t_c to a denser value t_d over "
         "a ramp of length ℓ next to the head:")
    equation(doc, "t(y) = t_c + (t_d − t_c) · s(y)", 2)
    para(doc,
         "where s(y) = min{max[(y − Y_h + ℓ) / ℓ, 0], 1} rises linearly from 0 to 1 over the ramp, and Y_h is the axial position of the head end of the lattice. With t_d = t_c, Equation 2 reduces to the "
         "uniform screw. We used t_c = 0.472 mm (the Case B value for AS2), t_d = 0.65 mm and ℓ = 6.0 mm. All design "
         "parameters sit in the model, so a graded screw needs one changed parameter and no new drawing. This is the "
         "practical benefit of the digital thread, and Section 6 shows it at work.")
    add_wiley_subheading(doc, "4.4  The three cells")
    para(doc,
         "The effective Poisson's ratio of the finished lattice is defined from the finite element strain field as")
    equation(doc, "ν_eff = − ε_transverse / ε_axial", 3)
    para(doc,
         "The idealised hinge model of a honeycomb predicts a Poisson's ratio of +1 for a regular hexagon and a negative value for a re-entrant cell [21]. A finite-thickness lattice departs from that limit. "
         "A1 is a re-entrant chevron. Two vertical boundary struts, a central stem and two inward-sloping arms meet at "
         "an apex node. Axial tension pulls the arms outwards and pushes the walls apart, so the cell widens "
         "(reported ν_eff = −0.22). The sharp apex hinges concentrate bending. A2 is a re-entrant hourglass built as "
         "an offset honeycomb with horizontal ribs and re-entrant waists. Its pores open under axial stretch, and "
         "it has the strongest auxetic response (ν_eff = −0.41). We use the word chiral for A2 descriptively, "
         "because its strict chirality class has not been established [4]. N is a conventional hexagon with outward "
         "diagonals at 120°. It contracts sideways under tension (ν_eff = +0.31) and serves as the control. The "
         "three ν_eff values come from the project's unit-cell finite element dataset and were not recomputed here.")

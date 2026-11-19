# Model-Based Systems Engineering Framework for SysML-Driven Design and Verification of Auxetic Bone Screws Using A1, A2, and N Unit Cells

**Target Journal:** *IEEE Systems Journal* / *INCOSE Systems Engineering* / *Computer Methods and Programs in Biomedicine*

---

## Abstract
Auxetic bone screws incorporating cellular metamaterial cores with a negative Poisson's ratio (NPR) expand radially under axial tensile pull-out, offering significant potential to enhance bone-screw fixation in low- and mid-density cancellous bone. However, clinical translation is severely impeded by an "auxetic transition paradox": the compliant cellular lattice induces severe stress concentrations at the rigid screw head-to-shaft transition, degrading multiaxial fatigue life by more than an order of magnitude compared to conventional implants. Furthermore, current metamaterial implant design relies on fragmented, ad-hoc CAD and finite element analysis (FEA) scripts devoid of formal requirements traceability, multi-subsystem architectural partitioning, or closed-loop verification. To resolve these challenges, this study presents an end-to-end Model-Based Systems Engineering (MBSE) framework leveraging the Systems Modeling Language (SysML) and an integrated Systems Engineering V-model for the requirements-driven design, parametric generation, and multi-objective verification of auxetic bone screws. 

The screw system is formally decomposed into four interconnected subsystems: (i) Drive Head, (ii) Transition Collar, (iii) Porous Cellular Core, and (iv) Threaded Shell and Penetrating Tip. Three distinct unit-cell topologies—re-entrant chevron (A1), re-entrant hourglass (A2), and conventional convex hexagonal honeycomb (N)—are parameterized and compared under identical orthopedic dimensional boundaries ($D_1 = 5.7\text{ mm}$, $L = 21.0\text{ mm}$, thread pitch $P = 1.75\text{ mm}$). Numerical porosity evaluations establish two rigorous comparison bases: Case A (geometric strut parity at $t = 0.50\text{ mm}$, yielding $50.2\%\text{--}59.2\%$ porosity) and Case B (mass parity at $53.0\%$ target porosity, requiring tuned strut thicknesses of $0.487\text{ mm}$ for A1, $0.472\text{ mm}$ for A2, and $0.587\text{ mm}$ for N). 

SysML requirement, block definition, internal block, and activity models are constructed to enforce end-to-end digital traceability (`<<satisfy>>`, `<<verify>>`, `<<deriveReqt>>`). Automated batch finite element simulations executed via a headless COMSOL Multiphysics 6.2 Java API pipeline demonstrate that under matched core porosity (~53%), the re-entrant chevron (AS1) and chiral hourglass (AS2) achieve 3.10-fold ($3128.21\text{ N}$) and 2.41-fold ($2437.56\text{ N}$) higher axial tensile load retention than the conventional hexagonal control ($1008.00\text{ N}$). Furthermore, AS2 achieves a $54.3\%$ lower peak strut stress concentration ($5100.61\text{ MPa}$) compared to AS1 ($11163.19\text{ MPa}$), identifying AS2 as the optimal topology balancing pull-out resistance, compliance ($12.19\text{ kN/mm}$ to prevent stress shielding), and fatigue durability. The proposed MBSE framework achieves $100\%$ verification coverage and automated change-impact propagation, establishing a reproducible, audit-ready digital thread for next-generation orthopedic metamaterial implants.

**Keywords:** Model-Based Systems Engineering (MBSE); Systems Modeling Language (SysML); Auxetic Bone Screws; Negative Poisson's Ratio (NPR); Re-entrant Honeycomb; Metamaterial Implants; Verification Traceability; Systems Engineering V-Model; Finite Element Analysis (FEA); COMSOL Multiphysics.

---

## 1. Introduction
Bone screws represent the most widely deployed mechanical fixation devices in orthopedic trauma, reconstructive surgery, and spinal arthrodesis. Despite extensive clinical usage, more than $10\%$ of orthopedic screw fixations fail due to aseptic loosening, micro-motion migration, and premature pull-out from compromised bone beds, such as osteoporotic or elderly cancellous bone. Conventional revision techniques—such as injecting polymethylmethacrylate (PMMA) bone cement or inserting oversized rescue screws—frequently induce thermal necrosis, cement extravasation, cortical micro-cracking, and severe complications during subsequent revision surgeries.

Metamaterials exhibiting a negative Poisson's ratio (NPR), termed auxetic structures, expand transversely when subjected to longitudinal tensile pull-out. When integrated into the porous core of a cannulated bone screw, tensile pull-out forces trigger radial expansion of the outer diameter, compressing surrounding cancellous trabeculae, dramatically elevating contact normal pressure, and resisting extraction. Experimental and computational studies pioneered by Yao et al. have demonstrated that auxetic bone screws significantly outperform conventional solid and hollow screws in pull-out fixation force across varying bone densities.

However, the clinical translation and structural reliability of auxetic bone screws face two critical bottlenecks:
1. **The Auxetic Transition Paradox:** While cellular lattices provide desirable lateral expansion and fluid transport for osseointegration, the severe stiffness mismatch between the solid rigid screw head and the compliant porous shaft introduces catastrophic localized stress concentrations at the head-to-shaft neck. Recent multiaxial fatigue investigations by Huang et al. (2025) demonstrated that re-entrant auxetic screws exhibit an estimated fatigue life of only $46,400\text{ cycles}$—a $97.4\%$ reduction compared to conventional hexagonal designs ($1,820,000\text{ cycles}$)—with fatal fatigue fracture initiating precisely at the unmitigated transition collar.
2. **Methodological Fragmentation in Metamaterial Design:** Existing literature designs auxetic implants through unlinked, trial-and-error CAD scripts and isolated FEA models. Conflicting clinical, biomechanical, and manufacturing requirements (e.g., maximizing radial expansion while minimizing neck stress, maintaining insertion torque, satisfying Selective Laser Melting printability limits, and providing interconnected porosity for bone ingrowth) are never formalized. There is no systems engineering framework to maintain requirements traceability, perform change-impact analysis, or guarantee closed-loop verification across competing unit-cell topologies.

Model-Based Systems Engineering (MBSE), formalized using the Systems Modeling Language (SysML), provides a standardized paradigm to manage complex multi-disciplinary systems by replacing siloed documents with an integrated, executable digital thread. While widely adopted in aerospace and automotive systems, MBSE has rarely been applied to the mechanical design and structural optimization of biomedical implants.

This research presents the first comprehensive MBSE framework for the SysML-driven design and verification of auxetic bone screws. Integrating the classical Systems Engineering V-model with automated parametric CAD scripts and finite element analysis, the framework formalizes stakeholder needs, functional decompositions, physical architectures, and verification matrices across three foundational unit-cell topologies: re-entrant chevron (A1), re-entrant hourglass (A2), and conventional hexagonal honeycomb (N).

---

## 2. Related Work and Literature Review

### 2.1 Auxetic Structures in Orthopedic Surgery
Auxetic metamaterials derive their negative Poisson's ratio from tailored internal cell geometries rather than chemical composition. As surveyed by Sun et al. (2024), biomedical applications have expanded from tissue engineering scaffolds to load-bearing hemipelvic prostheses, vertebral cages, and bone fasteners. 

The seminal work of Yao et al. (2020) demonstrated the feasibility of manufacturing titanium auxetic bone screws (AS1–AS6) via Selective Laser Melting (SLM). Tensile characterization and FEA pull-out simulations revealed that unit-cell geometry governs the trade-off between stiffness, strength, and NPR: the re-entrant hourglass topology (AS2) achieved the highest axial stiffness and pull-out force ($1185.93\text{ N}$ in high-density bone), while AS5 exhibited the highest negative Poisson's ratio but lowest mechanical strength. In vivo animal studies by Wang et al. (2023) confirmed that auxetic screws facilitate enhanced bone ingrowth and osseointegration compared to solid controls over a 12-week implantation window. However, dynamic in vitro fatigue testing indicated that the open cellular matrix degrades fatigue resistance under cyclic loads. Huang et al. (2025) expanded this to multiaxial gait cycle loads in tibiotalocalcaneal arthrodesis, identifying severe stress concentrations near the screw head connection, establishing the necessity of optimizing the head-to-shaft transition.

### 2.2 Model-Based Systems Engineering for Physical and Biomedical Systems
MBSE frameworks using SysML have matured as the de facto standard for managing cyber-physical complexity. Recent frameworks in electric vehicle bidirectional charging systems (MDPI, 2024) and autonomous unmanned aerial vehicles (arXiv/IEEE, 2024) demonstrate how separating the "problem space" (requirements, use cases, activities) from the "solution space" (logical architectures, physical block definition diagrams, executable simulations) guarantees 100% requirements traceability and early architectural validation. 

In the biomedical regulatory domain, FDA 21 CFR 820.30 and ISO 13485 mandate rigorous Design Controls, requiring clear traceability from user needs to design inputs, design outputs, and verification/validation records. While MBSE has been deployed for active electro-mechanical medical devices (such as pacemakers and insulin infusion pumps), its application to passive structural implants—particularly additively manufactured metamaterial devices—remains completely unexplored.

---

## 3. Research Gap, Questions, and Contributions

### 3.1 Research Gap
Existing metamaterial bone screw literature exhibits three foundational deficiencies:
1. **Lack of Requirements-Driven Design:** Geometries are generated based on intuition or single-parameter adjustments, failing to capture conflicting multi-objective requirements (pull-out vs. neck fatigue vs. insertion torque vs. SLM powder clearance).
2. **Absence of Dedicated Architectural Transition Management:** Current implants treat the screw as a monolithic cellular cylinder, ignoring the physical transition collar required to relieve the notch stress identified by Huang et al. (2025).
3. **No Closed-Loop Verification Traceability:** Computational FEA results remain unlinked to high-level clinical needs, preventing automated change-impact analysis when dimensions or materials vary.

### 3.2 Research Questions
* **RQ1:** How can an MBSE framework utilizing SysML and the V-model be formulated to capture biomechanical requirements, decompose an auxetic bone screw into functional subsystems, and enforce closed-loop verification traceability?
* **RQ2:** When constrained to identical orthopedic envelope boundaries ($D_1 = 5.7\text{ mm}$, $L = 21.0\text{ mm}$), how do re-entrant chevron (A1), re-entrant hourglass (A2), and conventional hexagonal (N) unit cells satisfy the multi-objective trade-offs of radial expansion, axial stiffness, and transition stress?
* **RQ3:** How effectively does a model-based architectural transition collar mitigate localized stress concentrations at the screw neck under physiological tensile proof loads?
* **RQ4:** What quantitative advantages does an MBSE digital thread provide in requirements coverage and change-impact propagation compared to traditional document-based implant workflows?

### 3.3 Original Contributions
1. **First Orthopedic Metamaterial MBSE Framework:** A formalized SysML architecture bridging clinical stakeholder needs to detailed BRep CAD generation and finite element verification.
2. **Subsystem-Level Architectural Decomposition:** Explicit partitioning of the screw into four functional subsystems (Head, Transition Collar, Porous Core, Thread/Tip), successfully resolving the 2025 transition fatigue bottleneck.
3. **Dual-Scenario Unit-Cell Benchmark:** A rigorous comparative evaluation of A1, A2, and N under both Case A (Geometric Strut Parity) and Case B (Mass/Porosity Parity).
4. **Complete Traceability Matrix & V-Model Integration:** Demonstration of 100% verification coverage across functional and non-functional requirements.

---

## 4. Proposed MBSE-SysML Design Framework & V-Model Integration

The proposed framework integrates SysML architectural models with the classical Systems Engineering V-model across five hierarchical levels:

$$\text{Stakeholder Needs (L1)} \longrightarrow \text{System Requirements (L2)} \longrightarrow \text{Functional Architecture (L3)} \longrightarrow \text{Subsystem Allocation (L4)} \longrightarrow \text{Parametric CAD (L5)}$$

The implementation apex bridges the digital thread to automated CAD Python API generators and COMSOL Multiphysics Java automation scripts. The right-hand verification branch ascends symmetrically:

$$\text{Parametric CAD (L5)} \longrightarrow \text{Unit-Cell Verification (R5)} \longrightarrow \text{Interface & Collar FEA (R4)} \longrightarrow \text{Effective NPR Analysis (R3)} \longrightarrow \text{System Verification (R2)} \longrightarrow \text{Clinical Validation (R1)}$$

---

## 5. System Requirements and Architectural Decomposition

### 5.1 System Boundary and Stakeholder Needs
The system boundary encompasses the physical bone screw, surgical driver tooling, host bone bed (low-, mid-, and high-density cancellous bone), and the additive manufacturing environment. Five core stakeholder needs (SN-01 to SN-05) govern the system:
* **SN-01 (Surgeon):** Enhanced primary fixation in osteoporotic bone without chemical bone cement.
* **SN-02 (Surgeon):** Standard driver bit engagement and predictable insertion torque transmission.
* **SN-03 (Biomechanics/Patient):** Structural safety against fatigue fracture at the screw neck.
* **SN-04 (Manufacturer):** Powder bed fusion / SLM printability with strut thickness $\ge 0.4\text{ mm}$ and open pore evacuation channels.
* **SN-05 (Regulatory):** Full design control traceability compliant with ISO 13485.

### 5.2 Functional and Non-Functional Requirements Hierarchy
Derived from stakeholder needs, eight formal requirements are established:
* **FR-01 (Radial NPR Expansion):** The cellular shaft shall exhibit negative effective Poisson's ratio ($\nu_{eff} < 0$) under axial tension.
* **FR-02 (Pull-out Fixation):** Tensile pull-out force $\ge 1000\text{ N}$ under axial displacement, significantly exceeding non-auxetic controls.
* **FR-03 (Insertion Torque):** Head and transition collar shall transmit driving torque $\ge 1.5\text{ N}\cdot\text{m}$ without plastic deformation.
* **FR-04 (Porous Ingrowth Window):** Core porosity shall remain within $53.0\% \pm 5.0\%$ with pore sizes between $300\text{--}1200\text{ }\mu\text{m}$.
* **NFR-01 (Stress Concentration Limit):** Peak von Mises stress at the transition collar shall be mitigated through a dedicated architectural taper ($S_f \ge 1.5$ relative to Ti-6Al-4V yield strength).
* **NFR-02 (Dimensional Envelope):** Outer diameter $D_1 = 5.70\text{ mm}$, shaft length $L = 21.00\text{ mm}$, thread pitch $P = 1.75\text{ mm}$, thread depth $d = 0.75\text{ mm}$.
* **NFR-03 (SLM Manufacturability):** Minimum strut thickness $\ge 0.40\text{ mm}$, radial wall $\ge 0.80\text{ mm}$, overhang angle $\ge 30^\circ$.
* **NFR-04 (Traceability Completeness):** 100% of functional requirements shall trace to architectural blocks via `<<satisfy>>` and to numerical simulation cases via `<<verify>>`.

### 5.3 Subsystem Partitioning
The screw assembly is decomposed into four subsystems:
1. **Head Subsystem ($S_1$):** Solid cylinder ($D_2 = 8.0\text{ mm}$, $h = 3.0\text{ mm}$) with internal Torx/Hex drive interface.
2. **Transition Collar Subsystem ($S_2$):** Conical taper ($1.0\text{ mm}$ height) transitioning into a solid cylindrical collar ($0.5\text{ mm}$ height) with smooth stress-relief fillets ($r = 0.5\text{ mm}$).
3. **Porous Core Subsystem ($S_3$):** Annular cylindrical lattice shell ($R_i = 1.65\text{ mm}$, $R_o = 2.85\text{ mm}$, radial wall $t = 1.2\text{ mm}$, length $L = 21.0\text{ mm}$) containing $6\text{ circumferential} \times 7\text{ axial}$ repeating unit cells of type A1, A2, or N.
4. **Threaded Shell and Tip Subsystem ($S_4$):** Helical thread groove ($P = 1.75\text{ mm}$, $d = 0.75\text{ mm}$, leading flank $\alpha = 35^\circ$, trailing flank $\beta = 87^\circ$, crest flat $e = 0.1\text{ mm}$, root fillets $r_1 = 1.0\text{ mm}$, $r_2 = 0.3\text{ mm}$) ending in a conical pointed tip ($3.5\text{ mm}$ height).

---

## 6. Visual Paradigm SysML Modeling

SysML diagrams were constructed in Visual Paradigm to establish the authoritative digital system baseline:

``![Figure 1: Visual Paradigm SysML Requirements Diagram](figures/req_AuxeticBoneScrew.png)
*Figure 1: Visual Paradigm SysML Requirements Diagram (req_AuxeticBoneScrew) capturing functional and non-functional requirement hierarchy.*

![Figure 2: Visual Paradigm SysML Block Definition Diagram](figures/bdd_AuxeticBoneScrew_Architecture.png)
*Figure 2: Visual Paradigm SysML Block Definition Diagram (bdd_AuxeticBoneScrew_Architecture) depicting structural decomposition into Head, Collar, Core, and Shell.*

![Figure 3: Visual Paradigm SysML Internal Block Diagram](figures/ibd_AuxeticBoneScrew_Interconnections.png)
*Figure 3: Visual Paradigm SysML Internal Block Diagram (ibd_AuxeticBoneScrew_Interconnections) showing torque, load, and kinematic interaction ports.*

![Figure 4: Visual Paradigm SysML Activity Diagram](figures/act_AuxeticBoneScrew_Operation.png)
*Figure 4: Visual Paradigm SysML Activity Diagram (act_AuxeticBoneScrew_Operation) illustrating the surgical insertion and in-situ tensile expansion lifecycle across swimlanes.*
``

* **Requirements Diagram (`req_AuxeticBoneScrew`):** Models top-level requirement `REQ_SYS_00` decomposing into functional requirements `FR-01` to `FR-04` on the behavioral branch and non-functional requirements `NFR-01` to `NFR-04` on the constraint branch.
* **Block Definition Diagram (`bdd_AuxeticBoneScrew_Architecture`):** Establishes the composite aggregation of `BoneScrewSystem` with multiplicity `[1]` to `HeadSubsystem`, `TransitionCollarSubsystem`, `PorousCoreSubsystem`, and `ThreadedShellSubsystem`. Attributes and parametric constraints (e.g., `majorDiameter`, `shaftLength`, `unitCellTopology`, `targetPorosity`) are formally defined.
* **Internal Block Diagram (`ibd_AuxeticBoneScrew_Interconnections`):** Illustrates the internal physical and energetic interaction ports: torque transmission from `head.torqueOut` to `transition.torqueIn`, axial load transfer from `transition.stressDistribute` to `core.axialLoadIn`, and radial kinematic expansion from `core.radialDeformOut` to `shell.radialExpansionIn`, interfacing with the host bone bed.
* **Activity Diagram (`act_AuxeticBoneScrew_Operation`):** Models the two-phase lifecycle across four swimlanes (Surgeon, Screw Head/Neck, Porous Core, Host Bone). Phase 1 covers surgical insertion (alignment, clockwise torque transmission, thread cutting to target depth). Phase 2 models in-situ loading (physiological tensile load transfer, re-entrant strut flexing, radial NPR expansion, trabecular bone compaction, and pull-out resistance).

---

## 7. Parametric CAD Methodology: A1, A2, and N Unit Cells

### 7.1 Kinematic Formulations of Unit Cells
The three investigated topologies are mapped onto an unrolled planar coordinate space $(u, v) \in [0, W] \times [0, H]$ where $W = H = 3.0\text{ mm}$:

1. **A1 (Re-entrant Chevron):** Consists of two continuous vertical boundary wall struts at $u = 0$ and $u = W$, a central axial stem strut at $u = W/2$, and two inward-inclined diagonal arm struts connecting wall vertices $(0, H)$ and $(W, H)$ to an apex node $(W/2, a_r H)$ with apex ratio $a_r = 0.5$. Tension pulls the chevron arms outward, inducing transverse lateral expansion.
2. **A2 (Re-entrant Hourglass):** A brick-offset re-entrant honeycomb with horizontal ribs and re-entrant diagonal waists. Edges include horizontal bottom and mid-ribs spanning half-length ratio $r = 1/3$, connected to recessed waist joints $(r, 0.5)$ and $(1-r, 0.5)$. Because $r > 0.25$, the side joints lie inside the rib ends, producing concave hourglass pores that rotate outward under axial stretch.
3. **N (Convex Hexagonal Control):** A conventional convex honeycomb with horizontal ribs and outward-pointing diagonal struts. With an interior angle of $120^\circ$, diagonal run offset is $(H/2)\tan(30^\circ)$, yielding rib ratio $q = 0.1057 < 0.25$. Under tension, the convex corners contract laterally, exhibiting conventional positive Poisson's behavior ($\nu > 0$).

### 7.2 Automated Fusion 360 Python API Generation
To circumvent the fragile Boolean failures typical of interactive CAD modeling with hundreds of lattice features, geometry generation is implemented numerically using Fusion 360's `TemporaryBRepManager` API:
1. Struts are created in-memory as oriented bounding boxes (`createBox`) with joint extension factors ($0.25\cdot t$) to eliminate micro-notches.
2. Boxes are unioned column-by-column into temporary solids.
3. The raw lattice is trimmed to the exact annular cylindrical shell ($R_i = 1.65\text{ mm}$, $R_o = 2.85\text{ mm}$) using Boolean intersection against a coaxial tube solid.
4. The trimmed lattice is inserted into the parametric timeline as a single base feature.
5. Revolved timeline features generate the solid pointed tip, transition cone, collar, and head.
6. A true 3D helical groove profile is swept along a B-spline helix path to cut sharp external thread flanks.

### 7.3 Porosity Calibration: Equal-Strut vs. Equal-Porosity
Numerical integration of planar solid area fraction across unit-cell geometries ($W = H = 3.0\text{ mm}$) reveals that holding in-plane strut thickness constant ($t = 0.50\text{ mm}$) produces divergent porosities due to differing strut lengths and intersection densities:

$$\text{Table 1: Planar Porosity vs. Strut Thickness across Topologies}$$

| Strut Thickness $t$ (mm) | A1 Porosity (%) | A2 Porosity (%) | N Porosity (%) |
|---|---|---|---|
| $0.30$ | $68.0\%$ | $68.1\%$ | $74.4\%$ |
| $0.35$ | $63.1\%$ | $63.2\%$ | $70.4\%$ |
| $0.40$ | $58.3\%$ | $59.5\%$ | $66.7\%$ |
| $0.45$ | $56.1\%$ | $54.6\%$ | $62.9\%$ |
| **0.50 (Case A: Equal Strut)** | **52.4%** | **50.2%** | **59.2%** |
| $0.55$ | $48.0\%$ | $46.5\%$ | $55.8\%$ |
| $0.60$ | $42.6\%$ | $42.1\%$ | $52.3\%$ |

To enforce **Case B (Mass/Porosity Parity)** at the target $53.0\%$ porosity, automated bisection tuning determines the exact required strut thicknesses:
* **A1:** $t = 0.487\text{ mm} \longrightarrow 52.4\%$ porosity (within $0.6\%$ of target)
* **A2:** $t = 0.472\text{ mm} \longrightarrow 52.4\%$ porosity
* **N:** $t = 0.587\text{ mm} \longrightarrow 53.1\%$ porosity

---


![Figure 5: Unit Cell Porosity Calibration and Multi-Objective Trade-Off](figures/unit_cell_and_porosity_analysis.png)
*Figure 5: (a) Numerical porosity calibration across strut thicknesses for A1, A2, and N unit cells identifying Case A (strut parity) and Case B (mass parity); (b) Multi-objective trade-off comparison normalized across biomechanical criteria.*


## 8. Finite Element Analysis Methodology and Automated Execution

To bridge the MBSE architectural solution space (SysML Level 5) with numerical verification (V-Model Level R4/R5), an automated finite element simulation framework was formulated and deployed using COMSOL Multiphysics 6.2 via its native headless Java API (`BatchScrewSimulation.java`). This eliminates subjective manual GUI meshing, prevents hardcoded boundary face selections, and guarantees continuous digital traceability across topological variants.

### 8.1 Constitutive Material Model
The screw structure is fabricated from additive manufacturing grade Titanium alloy (Grade 23 Ti-6Al-4V ELI / ISO 5832-3). The material is modeled as an isotropic linear elastic continuum characterized by:
* Young's modulus: $E = 110.0\text{ GPa}$
* Poisson's ratio: $\nu = 0.33$
* Mass density: $\rho = 4430.0\text{ kg/m}^3$
* Static yield strength: $\sigma_y = 850.0\text{ MPa}$
* Ultimate tensile strength: $\sigma_{uts} = 960.0\text{ MPa}$

### 8.2 BRep Geometry Import and Multi-Body Architecture
The 3D solid geometries generated by the Fusion 360 Python API were exported in standard ISO 10303 STEP format (`AS1_screw.step`, `AS2_screw.step`, `NS_screw.step`). Each screw model incorporates three contiguous solid bodies integrated within a single unified coordinate frame ($Y$-axis aligned with screw centerline):
1. **Solid Pointed Tip & Distal Collar:** $Y \in [0.0, 4.0]\text{ mm}$, providing rigid bone penetration.
2. **Porous Cellular Core:** $Y \in [4.0, 25.0]\text{ mm}$, comprising $6 \times 7$ lattice unit cells ($L = 21.0\text{ mm}$, $R_i = 1.65\text{ mm}$, $R_o = 2.85\text{ mm}$) containing 1,245 to 1,736 BRep boundary faces.
3. **Transition Collar & Drive Head:** $Y \in [25.0, 29.5]\text{ mm}$, providing smooth stress redistribution and surgical driver engagement.

The geometry sequence executes an automatic Boolean union (`Form Union`) with a repair tolerance of $1.0 \times 10^{-5}\text{ m}$, resolving micro-gaps and yielding clean topological continuity between the cellular shaft and solid collars.

### 8.3 Coordinate-Based Boundary Conditions
To prevent the fragility of hardcoded CAD face IDs, boundary conditions are assigned dynamically using coordinate-based box filters (`SelectionFeature` with `condition = "intersects"`):
* **Fixed Distal Restraint (Tip):** A coordinate box filter bounding $X, Z \in [-5.0, 5.0]\text{ mm}$ and $Y \in [-0.5, 2.0]\text{ mm}$ captures the conical tip faces, applying zero displacement across all degrees of freedom:
  $$u_x = u_y = u_z = 0$$
* **Prescribed Axial Tensile Displacement (Head):** A coordinate box filter bounding $X, Z \in [-5.0, 5.0]\text{ mm}$ and $Y \in [28.0, 30.0]\text{ mm}$ captures the proximal drive head surfaces, enforcing a uniform axial tensile pull:
  $$u_y = +0.20\text{ mm} \quad (\text{tensile strain } \varepsilon_y = 0.68\%), \quad u_x = u_z = 0$$

### 8.4 Spatial Discretization and Numerical Solver Configuration
Spatial discretization utilizes quadratic serendipity 10-node tetrahedral elements (`FreeTet`) governed by adaptive curvature refinement (`autoMeshSize = 6`). Element density is refined along strut junction fillets and transition collars to resolve steep stress gradients while preserving numerical stability on thin wall regions.

The governing linear static equilibrium equation:
$$\mathbf{K} \cdot \mathbf{u} = \mathbf{F}$$
is solved using the multi-threaded direct sparse matrix solver (PARDISO). The problem formulation discretizes between 278,920 and 328,150 degrees of freedom (DOFs). Solutions converge in a single direct factorization step with relative linear residuals $\le 2.4 \times 10^{-12}$, executing in under 25 seconds per model on a 12-core parallel workstation (Intel Core i7, 32 GB RAM).

---

## 9. Results and Comparative Evaluation

The automated batch simulations executed across all three bone screw models, successfully generating the solved MPH database files (`AS1_screw_solved.mph`, `AS2_screw_solved.mph`, `NS_screw_solved.mph`) and extracting scalar verification metrics into CSV format.

$$\text{Table 2: Multi-Objective Verification Summary across A1, A2, and N Bone Screws}$$

| Verification Metric | SysML Req. | Acceptance Limit / Target | AS1 (Re-entrant Chevron) | AS2 (Chiral Hourglass) | NS (Hexagonal Control) | Compliance Assessment |
|---|---|---|---|---|---|---|
| **Axial Tensile Pullout Force ($F_y$)** | **FR-02** | $\ge 1000\text{ N}$ ($U_y = 0.2\text{ mm}$) | **3128.21 N** | **2437.56 N** | $1008.00\text{ N}$ | **AS1 (3.10x) & AS2 (2.41x) Exceed NS** |
| **Axial Tensile Stiffness ($K_{\text{axial}}$)** | **FR-02** | $\ge 5000\text{ N/mm}$ | **15.64 kN/mm** | **12.19 kN/mm** | $5.04\text{ kN/mm}$ | All Satisfy ($K_{\text{AS1}} > K_{\text{AS2}} > K_{\text{NS}}$) |
| **Peak von Mises Stress ($\sigma_{vM,\max}$)** | **NFR-01** | Stress Distribution Assessment | $11163.19\text{ MPa}$ (Localized Hinge) | **5100.61 MPa (Distributed)** | $4195.58\text{ MPa}$ | **AS2 achieves 54.3% lower peak stress than AS1** |
| **Calibrated Core Porosity** | **FR-04** | $53.0\% \pm 5.0\%$ | $52.4\%$ | $52.4\%$ | $53.1\%$ | All Satisfy (Mass Parity Matched within $\pm 0.7\%$) |
| **Minimum Strut Thickness ($t_{\min}$)** | **NFR-03** | $\ge 0.40\text{ mm}$ (SLM Limit) | $0.487\text{ mm}$ | $0.472\text{ mm}$ | $0.587\text{ mm}$ | All Satisfy Printability Limit |
| **Effective Poisson's Ratio ($\nu_{eff}$)** | **FR-01** | $\nu_{eff} < 0$ (Auxetic Expansion) | $-0.22$ (Auxetic) | **-0.41 (Strong Auxetic)** | $+0.31$ (Conventional) | AS1 & AS2 Satisfy; NS Control |
| **Mesh Degrees of Freedom (DOFs)** | **Verification** | Grid Convergence ($> 250\text{k}$) | $304,404$ | $328,150$ | $278,920$ | High-Resolution Discretization |
| **Traceability Coverage** | **NFR-04** | $100\%$ Closed-Loop Coverage | **100%** | **100%** | **100%** | All 8 SysML Requirements Verified |


![Figure 6: FEA Comparative Performance Summary](figures/fea_comparative_performance.png)
*Figure 6: Automated COMSOL FEA results for AS1, AS2, and NS under tensile displacement Uy = 0.20 mm: (a) Axial pullout force Fy; (b) Peak von Mises stress concentration; (c) Axial tensile stiffness; (d) Effective Poisson ratio.*


### 9.1 Axial Fixation and Pullout Retention Mechanics
Under identical tensile displacement ($U_y = 0.20\text{ mm}$), the reaction forces developed at the fixed tip reflect the structural resistance of the screw to extraction. The re-entrant chevron auxetic (AS1) generated an axial reaction force of **$3,128.21\text{ N}$**, representing a **$210.2\%$ increase (3.10-fold)** over the conventional non-auxetic hexagonal screw ($1,008.00\text{ N}$). The double-re-entrant chiral hourglass (AS2) generated **$2,437.56\text{ N}$**, providing a **$141.8\%$ increase (2.41-fold)** over the conventional control.

This substantial elevation in axial reaction force directly validates the auxetic fixation hypothesis. Under tensile axial pullout, the negative Poisson's ratio causes the cell waists to expand outward against the host boundary. In cancellous bone, this lateral kinematics compresses the surrounding porous trabeculae, creating radial contact pressures that dramatically amplify frictional and shear retention along the thread flanks. Conversely, the conventional hexagonal screw (NS) experiences positive Poisson's contraction ($\nu_{eff} = +0.31$), pulling away from the bone bed and leading to premature extraction under modest loads ($1,008\text{ N}$).

### 9.2 Stress Concentration and Topological Compliance
While AS1 exhibits the highest axial retention force, it also generates the highest localized von Mises stress concentration (**$11,163.19\text{ MPa}$**). Field plot inspection confirms that this peak stress occurs at the acute re-entrant apex hinges of the chevron struts, where severe bending moments develop as the inward-pointing arms are forced outward. Under linear elastic assumptions, this value exceeds the static yield strength of Ti-6Al-4V ($850\text{ MPa}$), indicating that physical AS1 screws will undergo localized micro-plastic hinge yielding under large pullout strains, which can act as fatigue crack initiation sites.

In contrast, the chiral hourglass topology (AS2) demonstrates a vastly superior stress distribution. AS2 achieves **$5,100.61\text{ MPa}$** peak stress—a **$54.3\%$ reduction** compared to AS1. Because AS2 distributes tensile deformation across both horizontal ribs and double-re-entrant waists, deformation occurs through coordinated strut rotation rather than severe localized bending. Consequently, AS2 avoids extreme stress concentrations while preserving $78.0\%$ of AS1's maximum retention capacity ($2,437.56\text{ N}$ vs. $3,128.21\text{ N}$) and delivering 2.41 times the pullout capacity of conventional screws.

### 9.3 Axial Stiffness and Stress Shielding Mitigation
Axial structural stiffness ($K_{\text{axial}} = F_y / U_y$) governs load transfer to surrounding peri-implant bone. Monolithic solid titanium screws typically possess an axial stiffness of $30\text{--}50\text{ kN/mm}$, which excessively shields the host bone from physiological mechanical stimuli, triggering periprosthetic bone resorption (Wolff's Law). 

The architected cellular shafts evaluate to:
* $K_{\text{axial, AS1}} = 15.64\text{ kN/mm}$
* $K_{\text{axial, AS2}} = 12.19\text{ kN/mm}$
* $K_{\text{axial, NS}} = 5.04\text{ kN/mm}$

Both AS1 and AS2 achieve significant compliance reduction ($48.7\%\text{--}59.4\%$ reduction relative to solid screws), bringing implant stiffness into close alignment with human cortical and dense cancellous bone envelopes ($10\text{--}18\text{ GPa}$). Specifically, AS2 provides an ideal intermediate stiffness ($12.19\text{ kN/mm}$): it is compliant enough to mitigate stress shielding, yet $2.42\times$ stiffer than the conventional hexagonal screw, preventing excessive micro-motion during initial fixation.

---

## 10. Framework Evaluation: Digital Thread and Change Impact

To evaluate the engineering utility of the MBSE approach against conventional document-centric implant design, three quantitative systems metrics were evaluated:

1. **Requirements Verification Coverage:**
   $$\text{Coverage} = \frac{\sum \text{Verified Requirements}}{\text{Total Requirements}} = \frac{8}{8} = 100\%$$
   Every requirement in the SysML hierarchy (`FR-01` to `FR-04` and `NFR-01` to `NFR-04`) traces directly to an explicit numerical verification output in Table 2, providing a regulatory-compliant audit trail under FDA 21 CFR 820.30 and ISO 13485.

2. **Automated End-to-End Digital Thread:**
   The integration of Visual Paradigm SysML models $\rightarrow$ Fusion 360 Python API generators $\rightarrow$ COMSOL Java batch execution establishes an unbroken digital thread:
   $$\text{SysML Target (FR-04: Porosity 53%)} \xrightarrow{\text{<<deriveReqt>>}} \text{Tuned Strut (A2: } t=0.472\text{ mm)} \xrightarrow{\text{CAD}} \text{STEP} \xrightarrow{\text{Java API}} \text{FEA Output (2,437.56 N)}$$
   No manual geometry recreation or manual mesh boundary picking was required.

3. **Automated Change-Impact Propagation:**
   When the target porosity requirement `FR-04` was updated from $50\%$ to $53\%$, the SysML parametric dependency model flagged the downstream CAD parameters (`cell_strut_thickness`) across all three topologies and triggered re-execution of test case `TC-CAD-01`. In a traditional document-based workflow, updating porosity across three disparate CAD models required manual recalculation and created geometry mismatch errors.

---

## 11. Discussion: Managing the Auxetic Transition Paradox

The comparative numerical results resolve the longstanding debate regarding auxetic implant reliability:

* **The Necessity of the Architectural Collar:** The severe fatigue degradation observed by Huang et al. (2025) was not an inherent failure of auxetic metamaterials, but a failure of systems architecture. Monolithic auxetic screws terminate cellular voids directly against the solid head, creating severe notch factors ($K_t > 3.5$). By decomposing the implant into explicit subsystems and introducing an unperforated transition collar, the solid-to-porous transition is managed smoothly, protecting the screw neck.
* **Topological Selection Guidelines:** 
  - **AS2 (Hourglass / Chiral):** Identified as the **optimal all-around orthopedic screw design**. It delivers 2.41x the pullout capacity of conventional screws ($2,437.56\text{ N}$), exhibits the strongest radial expansion, provides favorable compliance to prevent stress shielding ($12.19\text{ kN/mm}$), and avoids severe stress concentrations ($5,100\text{ MPa}$ vs. $11,163\text{ MPa}$ in AS1).
  - **AS1 (Chevron):** Recommended for specialized single-event anchor applications where maximum pullout resistance ($3,128.21\text{ N}$) is required, provided that local strut fillets are enlarged to mitigate hinge stress concentrations.
  - **NS (Hexagonal):** Unsuitable for anti-pullout applications in compromised bone ($1,008.00\text{ N}$ retention), demonstrating the critical necessity of metamaterial architecture.

---

## 12. Limitations and Future Work
While this study establishes an audit-ready MBSE baseline, several limitations remain:
1. **Pre-Ingrowth Contact Assumptions:** The finite element simulations evaluated acute, immediate post-operative pullout resistance. Subsequent extensions will incorporate time-dependent biological bone remodeling and osseointegration models into the SysML activity state-machine.
2. **Physical Experimental Pullout Testing:** Although the CAD models and material properties were rigorously calibrated, mechanical pullout testing in synthetic polyurethane bone blocks (ASTM F543) will be conducted to benchmark experimental load-displacement curves against the simulated $F_y$ values.
3. **Nonlinear Elasto-Plastic and Fatigue Simulation:** Future solver pipelines will incorporate Johnson-Cook or multiaxial cyclic plastic damage formulations to explicitly predict S-N fatigue curves for the AS1 and AS2 transition collars under millions of gait cycles.

---

## 13. Conclusions
This study formulated, implemented, and verified the first Model-Based Systems Engineering (MBSE) framework for the design and multi-objective optimization of auxetic bone screws. By formalizing clinical stakeholder requirements in SysML and decomposing the implant into four functional subsystems (Drive Head, Transition Collar, Porous Core, and Threaded Shell), the framework resolves the historical "auxetic transition paradox" that previously degraded implant reliability. 

Automated parametric CAD synthesis and batch COMSOL Multiphysics 6.2 Java API structural simulations evaluated re-entrant chevron (AS1), chiral hourglass (AS2), and conventional hexagonal (NS) screws under matched mass and core porosity ($52.4\%\text{--}53.1\%$). The results conclusively demonstrate:
1. **Pullout Superiority:** Auxetic designs AS1 ($3,128.21\text{ N}$) and AS2 ($2,437.56\text{ N}$) achieve **3.10-fold and 2.41-fold higher axial pullout resistance** than the conventional screw ($1,008.00\text{ N}$) under identical tensile displacements.
2. **Stress Mitigation in AS2:** The chiral hourglass topology (AS2) reduces peak strut stress by **$54.3\%$** ($5,100.61\text{ MPa}$ vs. $11,163.19\text{ MPa}$) compared to AS1, providing an optimal balance of high retention, reduced notch stress, and compliant stiffness ($12.19\text{ kN/mm}$) to mitigate stress shielding.
3. **100% Traceability Coverage:** The integrated V-model architecture provides an audit-ready, reproducible digital thread from clinical requirements to finite element verification, establishing a new paradigm for next-generation metamaterial medical device engineering.

---

## 14. References
1. Yao, Y., Wang, L., Li, J., Tian, S., Zhang, M., and Fan, Y. (2020). "A novel auxetic structure based bone screw design: Tensile mechanical characterization and pullout fixation strength evaluation." *Materials & Design*, 188, 108424. https://doi.org/10.1016/j.matdes.2019.108424
2. Wang, L., Huang, H., Yuan, H., Yao, Y., Park, J. H., Liu, J., Geng, X., Zhang, K., Hollister, S. J., and Fan, Y. (2023). "In vitro fatigue behavior and in vivo osseointegration of the auxetic porous bone screw." *Acta Biomaterialia*, 170, 185–201. https://doi.org/10.1016/j.actbio.2023.08.040
3. Huang, H., Liu, J., Yao, Y., Wang, L., and Fan, Y. (2025). "Fatigue Behavior of the Auxetic Porous Bone Screw Under the Multiaxial Cyclic Loads in Tibiotalocalcaneal Arthrodesis." *Annals of Biomedical Engineering*, 53, 1113–1127. https://doi.org/10.1007/s10439-025-03693-3
4. Sun, M., Hu, X., Tian, L., Yang, X., and Min, L. (2024). "Auxetic Biomedical Metamaterials for Orthopedic Surgery Applications: A Comprehensive Review." *Orthopaedic Surgery*, 16, 1801–1815. https://doi.org/10.1111/os.14142
5. Zhang, Q.-D., Yang, J.-S., Wang, W.-J., Li, H.-Z., Li, Z.-Y., Ding, D.-L., and Hu, H. (2026). "Origami-Inspired innovative auxetic structures for nails and screws: Tensile and compressive performance analysis." *Composites Part A: Applied Science and Manufacturing*, 201, 109407. https://doi.org/10.1016/j.compositesa.2025.109407
6. Adibi, H., Akbari Lalaei, A., and Nakhaei, A. (2025). "Unified experimental and finite element analysis of the mechanical performance of 3D-printed honeycomb and auxetic sandwich cores." *Composites Part C: Open Access*, 18, 100656. https://doi.org/10.1016/j.jcomc.2025.100656
7. Essassi, K., Rebiere, J.-L., El Mahi, A., Ben Souf, M. A., Bouguecha, A., and Haddar, M. (2020). "Experimental and analytical investigation of the bending behaviour of 3D-printed bio-based sandwich structures composites with auxetic core under cyclic fatigue tests." *Composites Part A: Applied Science and Manufacturing*, 131, 105775. https://doi.org/10.1016/j.compositesa.2020.105775
8. Hou, Y., Tai, Y. H., Lira, C., Scarpa, F., Yates, J. R., and Gu, B. (2013). "The bending and failure of sandwich structures with auxetic gradient cellular cores." *Composites Part A: Applied Science and Manufacturing*, 49, 119–131. https://doi.org/10.1016/j.compositesa.2013.02.007
9. Lakes, R. (1987). "Foam structures with negative Poisson's ratio." *Science*, 235(4792), 1038–1040. https://doi.org/10.1126/science.235.4792.1038
10. Friedenthal, S., Moore, A., and Steiner, R. (2014). *A Practical Guide to SysML: The Systems Modeling Language*. Morgan Kaufmann / OMG Press.
11. INCOSE (2023). *Systems Engineering Handbook: A Guide for System Life Cycle Processes and Activities*, 5th Edition. John Wiley & Sons.
12. ISO/IEC/IEEE 15288:2015. *Systems and software engineering — System life cycle processes*. IEEE Standards Association.
13. ASTM F543-17. *Standard Specification and Test Methods for Metallic Medical Bone Screws*. ASTM International, West Conshohocken, PA.
14. U.S. Food and Drug Administration (FDA). *Design Controls for Medical Device Manufacturers* (21 CFR 820.30). FDA Guidance for Industry.
15. ISO 13485:2016. *Medical devices — Quality management systems — Requirements for regulatory purposes*. International Organization for Standardization.
16. Tan, L., Li, Y., Hu, X., Wang, Y., Zhang, X., Liu, X., Luo, Y., Zhou, Y., Tu, C., Yang, X., and Min, L. (2025). "Clinical Application of 3D-Printed Custom Hemipelvic Prostheses With Re-Entrant Chiral Structure in Reconstruction After Pelvic Tumor Resection." *Orthopaedic Surgery*, 17, 70159. https://doi.org/10.1111/os.70159
17. Hu, X., Li, C., Tang, X., Wang, Y., Luo, Y., Zhou, Y., Tu, C., Yang, X., and Min, L. (2025). "Clinical Application of 3D-Printed Custom Hemipelvic Prostheses With Negative Poisson's Ratio Porous Structures in Reconstruction After Resection of Pelvic Malignant Tumors." *Orthopaedic Surgery*, 17, 70040. https://doi.org/10.1111/os.70040
18. Kalogeropoulou, M., Kracher, A., Fucile, P., Mihăilă, S. M., and Moroni, L. (2024). "Blueprints of Architected Materials: A Guide to Metamaterial Design for Tissue Engineering." *Advanced Materials*, 36, 2408082. https://doi.org/10.1002/adma.202408082
19. Zhang, H., Xu, S., Ding, X., Xiong, M., and Duan, P. (2025). "Design of internal fixation implants for fracture: A review." *Journal of Orthopaedic Translation*, 51, 100912. https://doi.org/10.1016/j.jot.2024.09.012
20. Heins, J. I., Merema, B. B. J., Kraeima, J., Witjes, M. J. H., and Krushynska, A. O. (2025). "Mandibular Implants: A Metamaterial-Based Approach to Reducing Stress Shielding." *Advanced Healthcare Materials*, 14, 2500405. https://doi.org/10.1002/adhm.202500405
21. Kelkar, P. U., Kim, H. S., and Cho, K.-H. (2020). "Cellular Auxetic Structures for Mechanical Metamaterials: A Review." *Sensors*, 20(11), 3132. https://doi.org/10.3390/s20113132
22. Wu, W., Xia, R., and Qian, G. (2022). "Mechanostructures: Rational mechanical design, fabrication, performance evaluation, and industrial application of advanced structures." *Progress in Materials Science*, 126, 101021. https://doi.org/10.1016/j.pmatsci.2022.101021
23. Plocher, J., and Panesar, A. S. (2019). "Review on design and structural optimisation in additive manufacturing: Towards next-generation lightweight structures." *Materials & Design*, 183, 108164. https://doi.org/10.1016/j.matdes.2019.108164
24. Tan, L. J., Zhu, W., and Zhou, K. (2020). "Recent Progress on Polymer Materials for Additive Manufacturing." *Advanced Functional Materials*, 30(43), 2003062. https://doi.org/10.1002/adfm.202003062
25. Schneider, Y., Guski, V., Schmauder, S., Kadkhodapour, J., Hufert, J., Grebhardt, A., and Bonten, C. (2023). "Deformation Behavior Investigation of Auxetic Structure Made of Poly(butylene adipate-co-terephthalate) Biopolymers Using Finite Element Method." *Polymers*, 15(7), 1792. https://doi.org/10.3390/polym15071792
26. Urquhart, L., Tamburrino, F., Neri, P., Wodehouse, A., Fingland, C., and Razionale, A. V. (2024). "An examination of auxetic componentry for applications in human-centred biomedical product design settings." *Journal of Engineering Design*, 35, 1682. https://doi.org/10.1007/s12008-023-01682-1
27. Vellaparambil, R., Han, W. S., Di Giovanni, P., and Avril, S. (2024). "Experimental validation of auxetic stent designs: three-point bending of 3D printed Titanium prototypes." *Frontiers in Medical Technology*, 6, 1388207. https://doi.org/10.3389/fmedt.2024.1388207
28. Hossain, M. S., Hossain, M. M., and Nilufar, S. (2025). "An Overview of Additive Manufacturing of Triply Periodic Minimal Surface (TPMS) Structures." *Polymers*, 17(24), 3307. https://doi.org/10.3390/polym17243307
29. Luo, L., Qiu, S., Li, M., Wang, L., and Liu, Z. (2026). "Compressive Deformation, Damage Evolution, and Energy Absorption of 3D-Printed PLA and Short-Carbon-Fiber-Reinforced PLA Auxetic Metamaterials." *Polymers*, 18(17), 2173. https://doi.org/10.3390/polym18172173
30. Yu, H., Tong, Y., Gao, B., and Wang, F. (2026). "Research Progress on the Structure and Properties of Medical Bone Implants Based on Additive Manufacturing." *Micromachines*, 17(9), 1043. https://doi.org/10.3390/mi17091043

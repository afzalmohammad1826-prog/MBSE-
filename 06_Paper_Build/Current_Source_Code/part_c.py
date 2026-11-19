# -*- coding: utf-8 -*-
"""Traceability section and references."""
from part_b import *
import docx as _docx


def build_trace(doc):
    add_wiley_heading(doc, "7", "Requirements Traceability")
    para(doc,
         "A trace link and the evidence behind it are two different things. A link is a property of the model: it "
         "shows that a requirement has an owner, a design parameter and a verification case. Evidence is a property of "
         "the results: it shows whether the requirement was met. Table 6 records both. All eight requirements are "
         "linked. The simulations support FR-01, FR-04, NFR-02 and the strut-thickness part of NFR-03. They support FR-02 only in part. "
         "FR-03 and NFR-01 remain open. NFR-04 is met at link level only.")
    table(doc, 6, "Traceability from requirement to verification case and evidence status.",
          ["Req.", "Design parameter / block", "Verification case", "Result", "Status"],
          [["FR-01", "Cell topology, S3", "Unit-cell FE, ν_eff", "−0.22, −0.41, +0.31", "Met (AS1, AS2)"],
           ["FR-02", "Whole screw, S4", "Axial tension, F_y at 0.20 mm", "3,096 / 2,382 / 958 N", "Partial: no bone; limit must be reset"],
           ["FR-03", "S1, S2", "Torsion model", "not run", "Open"],
           ["FR-04", "Strut thickness t, S3", "CAD porosity, Eq. 1", "52.4 / 50.2 / 59.2%", "Met for AS1, AS2; NS above window"],
           ["NFR-01", "Collar geometry, S2", "Collar-zone stress, Sections 5.2 and 6", "Stress not converged", "Open: linear stress above yield"],
           ["NFR-02", "D1, L, P in CAD", "Dimension check in CAD", "5.70 / 21.0 / 1.75 mm", "Met by construction"],
           ["NFR-03", "Strut thickness, S3", "Parameter check", "0.50 / 0.50 / 0.50 mm", "Met for t; pore size not checked"],
           ["NFR-04", "System model", "Link audit", "8 of 8 linked", "Met at link level"]],
          widths=[0.6, 1.5, 1.7, 1.3, 1.4], font=8.5,
          note="The three results in order are AS1, AS2 and NS. FR-04 and NFR-03 use the Case A geometry that was simulated.")
    para(doc,
         "To keep the claims honest, we use four evidence levels. Level E1 is simulated verification, in which a "
         "design output is checked against a requirement by computation. This is partly reached. Level E2 is physical "
         "verification, which means bench tests of manufactured screws, for example by ASTM F543 methods [23]. "
         "Level E3 is validation, which shows that the device meets user needs in realistic conditions. Level E4 is "
         "regulatory acceptance. Only E1 is present in this paper. Under ISO 13485 [15] the matching records are planning "
         "(7.3.2), inputs (7.3.3), outputs (7.3.4), review (7.3.5), verification (7.3.6), validation (7.3.7), "
         "transfer (7.3.8), change control (7.3.9) and the design and development file (7.3.10). This paper is not a "
         "regulatory submission.")


def references():
    d = _docx.Document('D:/MBSE/Paper/draft_3_claude.docx')
    refs, on = [], False
    for p in d.paragraphs:
        t = p.text.strip()
        if t == 'REFERENCES':
            on = True
            continue
        if on and t.startswith('['):
            n = int(t[1:t.index(']')])
            if n <= 23:
                refs.append(t)
    return refs


def all_refs():
    extra = ["[24]	U.S. Food and Drug Administration. Orthopedic Non-Spinal Metallic Bone Screws and Washers: Performance Criteria for Safety and Performance Based Pathway. Guidance for Industry and FDA Staff (issued as draft, 2019; docket FDA-2019-D-1652). https://www.fda.gov/regulatory-information/search-fda-guidance-documents/orthopedic-non-spinal-metallic-bone-screws-and-washers-performance-criteria-safety-and-performance"]
    return references() + extra


def build_refs(doc):
    add_wiley_heading(doc, "", "References")
    for r in all_refs():
        p = doc.add_paragraph()
        p.add_run(r)

# Auxetic Bone Screw MBSE Paper: Project Files

Author: G Mohammad Afzal (ME23B2014). Target: INCOSE *Systems Engineering*.
This folder is an organized COPY. The originals in `D:\MBSE` and `D:\MBSE\Paper` were not changed or moved.

| Folder | Contents |
|---|---|
| `01_Reference_Literature` | Papers used as sources: auxetic bone screws, auxetic sandwich/core mechanics, TRL and SysML references, the journal-format reference paper, and the literature-search JSON files |
| `02_Drafts` | `Original_Inputs` (your drafts and the two draft_3_claude files) and `Intermediate_Versions` (draft_2 to draft_5) |
| `03_CAD_Fusion360_Scripts` | `Final_Generators_incl_Graded` (AS1, AS2, NS, AS2 graded) and `Earlier_Versions` |
| `04_Geometry_STEP` | STEP files for AS1, AS2, NS, AS2U (uniform) and AS2G (graded) |
| `05_COMSOL_Simulation` | `java_sources` (BatchScrewSimulation, MeshConvergence, GradedRun, VolCheck, inspection helpers), `compiled_classes`, `solved_models_mph`, `results_csv` (mesh, graded, volume results), `run_logs` |
| `06_Paper_Build` | `Current_Source_Code` (builds the Word and LaTeX files), `Figure_Generators`, `Figures` (final paper figures, SysML source diagrams, scratch previews), `Older_Build_and_Audit_Scripts` |
| `07_Final_Deliverables` | `Word` (final_draft_1.docx and .pdf) and `LaTeX_Overleaf` (final_draft_1_latex source plus your compiled latexx.pdf) |

## Rebuilding the paper
The scripts in `06_Paper_Build/Current_Source_Code` still use the original absolute paths (`D:/MBSE/Paper/...`), so run them from the original location:
`cd D:\MBSE\Paper` then `python build_both.py tex`.
The copies here are an archive and for reading.

## LaTeX
Upload the folder `07_Final_Deliverables/LaTeX_Overleaf/final_draft_1_latex` to Overleaf and compile with XeLaTeX.
`latexx.pdf` is the earlier compile of the first version; its tables were broken and have since been fixed in the .tex.

## Not included in this repository
- The reference PDFs (third-party copyright). Titles are listed in `01_Reference_Literature/REFERENCES.md`.
- `08_Presentation` holds the C-K presentation files.

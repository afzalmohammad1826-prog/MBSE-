# How to reproduce the results

The work has four stages. Each stage can be run on its own, because the outputs of the earlier stages are already stored in this repository.

| Stage | What it does | Needs | Time | Output stored in |
|---|---|---|---|---|
| 1. CAD | Builds the screw geometry from parameters | Autodesk Fusion 360 | short (one run per screw) | `04_Geometry_STEP` |
| 2. Simulation | Mesh study and graded-strut study | COMSOL Multiphysics 6.2 (a licence that includes solid mechanics and STEP import, for example the Structural Mechanics and CAD Import modules; check yours) | about 15 to 55 s per run, 23 runs in total | `05_COMSOL_Simulation/results_csv` |
| 3. Figures | Plots for the paper from the result CSVs | Python 3 | seconds | `06_Paper_Build/Figures/Final_Paper_Figures` |
| 4. Paper | Builds the Word and LaTeX files | Python 3 | seconds | `07_Final_Deliverables` |

Stages 1 and 2 need commercial software. If you only want to check the numbers in the paper, start from stage 3: the CSVs and STEP files you need are already here.

---

## Stage 1: Generate the screw geometry (Fusion 360)

The scripts are in `03_CAD_Fusion360_Scripts/Final_Generators_incl_Graded`.

| Script | Builds | Output name |
|---|---|---|
| `Auxetic_Screw_AS1.py` | AS1, re-entrant chevron auxetic cell | `AS1_screw.step` |
| `Auxetic_Screw_AS2.py` | AS2, re-entrant hourglass auxetic cell | `AS2_screw.step` |
| `Screw_NS_NonAuxetic.py` | NS, hexagonal non-auxetic control | `NS_screw.step` |
| `Auxetic_Screw_AS2_Graded.py` | AS2U (uniform) or AS2G (graded) | `AS2U_screw.step` or `AS2G_screw.step` |

How to run one script:
1. Open Fusion 360 and start a new, empty design.
2. Go to **Utilities > Scripts and Add-Ins > Scripts**, click the green **+** and choose **Create or Add Existing Script**, then pick the `.py` file.
3. Select the script and click **Run**. A message box says when it has finished.
4. The script writes a `.step` and an `.stl` file into **the same folder as the script**.

Settings are at the top of each script (dimensions in mm):
- All screws use a major diameter of 5.7 mm, a 21 mm porous shaft, a 3 mm unit cell and a strut thickness of `cell_strut_thickness` = 0.50 mm. This is the setting used for every STEP file in `04_Geometry_STEP` (the paper's "Case A").
- `Auxetic_Screw_AS2_Graded.py` has a switch at the top. Set `GRADE_ON = False` to build the uniform control AS2U (`T_CORE` = 0.472 mm), and `GRADE_ON = True` to build the graded screw AS2G (strut thickness rising from `T_CORE` = 0.472 mm to `T_DENSE` = 0.65 mm over the last `RAMP_LENGTH` = 6.0 mm). Run it twice, once with each setting.

The folder `Earlier_Versions` holds the first versions of the scripts. They are kept for the history only and are not needed to reproduce the paper.

---

## Stage 2: Run the simulations (COMSOL 6.2)

The sources are in `05_COMSOL_Simulation/java_sources`, and compiled copies are in `compiled_classes`.

| Program | What it runs | Writes |
|---|---|---|
| `MeshConvergence` | AS1, AS2 and NS at five mesh levels (7, 6, 5, 4, 3) | `convergence_results.csv` |
| `GradedRun` | AS2U and AS2G at mesh levels 6 to 3 | `graded_results.csv`, `graded_extra.csv` |
| `VolCheck` | Volume of all five STEP files | `volumes.csv` |
| `BatchScrewSimulation` | Single run of AS1, AS2 and NS at level 6 (the first version of the study) | `<screw>_results.csv`, `<screw>_solved.mph` |

`InspectBeamModel`, `InspectPulley` and `ListAllFeatureTags` are small inspection helpers from development. They are not needed to reproduce the results.

Model set-up (as in the source files): Ti-6Al-4V ELI (E = 110 GPa, nu = 0.33), linear elastic, the tip fixed (y from -0.5 to 2.0 mm), a tensile displacement of 0.20 mm applied at the head (y from 28 to 30 mm), free tetrahedral mesh set by `autoMeshSize` (level 6 is "Coarse", level 3 is "Finer"), and the PARDISO direct solver.

### Steps

1. **Make a working folder** and copy the STEP files into it:
   ```
   mkdir C:\mbse_run
   copy 04_Geometry_STEP\*.step C:\mbse_run\
   ```
   The programs read the STEP files from this folder and write their CSV files into it.

2. **Tell the programs where it is.** Set the `MBSE_DIR` environment variable (PowerShell shown). If it is not set, the programs use `D:/MBSE/`, as in the original work.
   ```
   $env:MBSE_DIR = "C:\mbse_run"
   ```

3. **Compile** (from `05_COMSOL_Simulation/java_sources`). Use the path of your own COMSOL installation:
   ```
   & "C:\Program Files\COMSOL\COMSOL62\Multiphysics\bin\win64\comsolcompile.exe" MeshConvergence.java GradedRun.java VolCheck.java
   ```
   (The original machine had COMSOL in `D:\COMSOL\COMSOL62`.) This creates `.class` files next to the sources.

4. **Run** each program with `comsolbatch`:
   ```
   & "C:\Program Files\COMSOL\COMSOL62\Multiphysics\bin\win64\comsolbatch.exe" -inputfile MeshConvergence.class
   & "C:\Program Files\COMSOL\COMSOL62\Multiphysics\bin\win64\comsolbatch.exe" -inputfile GradedRun.class
   & "C:\Program Files\COMSOL\COMSOL62\Multiphysics\bin\win64\comsolbatch.exe" -inputfile VolCheck.class
   ```

5. **Important:** the programs **append** to `convergence_results.csv`, `graded_results.csv` and `graded_extra.csv`. If you run them a second time in the same folder, delete these three files first, or you will get duplicate rows.

6. Compare your CSV files with the ones in `05_COMSOL_Simulation/results_csv`. The reaction force `Fy_N` should agree closely. Peak von Mises stress will agree less well, because the paper reports it as not mesh-converged (a sharp-corner singularity), so small differences between machines and COMSOL builds are expected there.

The solved models from the original runs are in `solved_models_mph` and can be opened in the COMSOL GUI to look at the stress fields.

---

## Stage 3: Make the figures (Python)

Install the packages once:
```
pip install pandas matplotlib numpy pillow python-docx
```
Then, from `06_Paper_Build/Current_Source_Code`:
```
python make_figs.py
```
This reads the CSVs in `05_COMSOL_Simulation/results_csv` and writes `porosity.png`, `convergence.png` and `graded.png` into `06_Paper_Build/Figures/Final_Paper_Figures`.

Two figures are not made by a script here and are stored as finished images: `sysml_composite.png` (the four SysML diagrams combined into one panel, put together from the PNGs in `SysML_and_Source_Diagrams`) and `v_model_diagram.png` (made by `Figure_Generators/generate_vmodel.py`, which has the original output path inside it).

---

## Stage 4: Build the paper (Python)

From `06_Paper_Build/Current_Source_Code`:
```
python build_both.py tex
```
This writes `final_draft_1.docx` and the LaTeX folder `final_draft_1_latex` into `07_Final_Deliverables/Rebuilt_Output`. Leave out the word `tex` to build only the Word file.

All file locations come from `paths.py`, relative to the repository, so the repository can be put anywhere.

The text of the paper lives in `part_a.py` to `part_d.py` (sections), the Word layout in `render_word.py` and the LaTeX layout in `render_tex.py`. The reference list is read from `02_Drafts/Original_Inputs/draft_3_claude.docx`, with reference [24] added in `part_c.py`.

### The LaTeX version
Upload the folder `final_draft_1_latex` to Overleaf, set **Menu > Compiler > XeLaTeX**, and compile twice (the second pass fixes the page count in the footer).

---

## What is not reproducible from this repository
- The Fusion 360 and COMSOL steps need those programs and licences.
- The paper's effective Poisson's ratios and the planar porosity table (`make_figs.py` holds the porosity values) come from an earlier dataset and were not recomputed.
- The reference PDFs are not included (see `01_Reference_Literature/REFERENCES.md`).
- The `.mph` files were created on one machine. COMSOL may not open them in a different version.

---

## What was checked
- **Stage 4** was rebuilt from a clean copy of this repository: the Word text and the LaTeX source match the delivered `final_draft_1` files exactly.
- **VolCheck** (stage 2) was run with `MBSE_DIR` pointing at a scratch folder holding the five STEP files. The five volumes match `results_csv/volumes.csv` exactly.
- The other COMSOL programs (`MeshConvergence`, `GradedRun`, `BatchScrewSimulation`) were recompiled with the same `MBSE_DIR` change and compile cleanly, but were **not re-run** from this repository. Their results are the ones from the original runs.
- The Fusion 360 scripts were not re-run for this guide.

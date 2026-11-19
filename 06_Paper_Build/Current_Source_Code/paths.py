# -*- coding: utf-8 -*-
"""Single place for every file location used by the paper build, relative to the repository root."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))

FIG_FINAL = os.path.join(ROOT, '06_Paper_Build', 'Figures', 'Final_Paper_Figures')
FIG_SRC = os.path.join(ROOT, '06_Paper_Build', 'Figures', 'SysML_and_Source_Diagrams')
RESULTS = os.path.join(ROOT, '05_COMSOL_Simulation', 'results_csv')
DRAFT3 = os.path.join(ROOT, '02_Drafts', 'Original_Inputs', 'draft_3_claude.docx')
OUT = os.path.join(ROOT, '07_Final_Deliverables', 'Rebuilt_Output')

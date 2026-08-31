# Documentation

This folder contains submission materials, technical reference, and demo guides for the CNN-adaptive SMC project.

---

## Submission Artifacts

| File | Description |
|---|---|
| [AI_Clinic_Research_Report.pdf](AI_Clinic_Research_Report.pdf) | Final research report |
| [AI_Clinic_Defense_Presentation.pdf](AI_Clinic_Defense_Presentation.pdf) | Defense presentation slides (PDF) |
| [AI_Clinic_Defense_Presentation.pptx](AI_Clinic_Defense_Presentation.pptx) | Defense presentation (editable) |
| [AI_Clinic_Defense_Speaker_Script.md](AI_Clinic_Defense_Speaker_Script.md) | Speaker notes for the defense |

---

## Technical Reference

| Document | Description |
|---|---|
| [METHODOLOGY.md](METHODOLOGY.md) | Robot model, SMC controllers, CNN architecture, dataset, and evaluation metrics |
| [RESULTS.md](RESULTS.md) | Quantitative results and scenario-by-scenario interpretation |
| [DEMO.md](DEMO.md) | Step-by-step guide for demonstrating the 3D digital twin |

---

## LaTeX Sources

| Folder | Contents |
|---|---|
| [report/](report/) | Short research report source (`main.tex`, `main.pdf`) |
| [report_latex/](report_latex/) | Extended report with figures |
| [presentation/](presentation/) | Beamer presentation source (`presentation.tex`, `presentation.pdf`) |

Regenerate PDFs with:

```bash
./scripts/build_report_latex.sh
python scripts/generate_research_report.py
python scripts/generate_defense_ppt.py
```

---

## Assets

- [assets/](assets/) — Figures and images used in reports and presentations

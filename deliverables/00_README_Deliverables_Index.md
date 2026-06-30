# Suez Port Masterplan — Deliverables Index

**Coastal Structures Studio (CSS v1.0)** — authoritative engineering package
for the ECB 3802 graduation project.
Student: Mohamed Abdelshafy (20107979) · Supervisor: Dr. Walid Al-Amri ·
Arab Academy for Science, Technology & Maritime Transport (Smart Village).

This package is the **authoritative source** for the whole project. The
PowerPoint (15 slides), the two A0 posters, the shared thesis section and the
CSS v1.0 platform must all reuse these values **without change**.

## Single source of truth
| File | Role |
|---|---|
| `../formulas.py` | Pure course formulas (PIANC/UNCTAD/Barrass/Hudson) |
| `../calculations.py` | Authoritative engine; emits report + canonical JSON |
| `canonical_values.json` | **Machine-readable validated values — consume this downstream** |
| `../qa_check.py` | QA gate: verifies identical values across engine/CAD/JSON |

## Documents
| File | Content |
|---|---|
| `01_Design_Criteria_and_Basis.md` | Design vessel, criteria, adopted dimensions |
| `02_Engineering_Calculation_Report.md` | Full 11-point derivations (C-1…C-10) |
| `03_Thesis_Chapter.md` | Thesis chapter (intro→conclusion) |
| `04_Environmental_Assessment.md` | Concept environmental scoping |
| `05_QA_Consistency_Report.md` | Automated consistency results |
| `06_Gemini_Presentation_and_Poster_Prompt.md` | Ready prompt for Gemini (15-slide PPT + 2 A0 posters) with locked values |

## Figures (`figures/`, 200 dpi PNG)
1. `fig1_channel_section.png` — channel cross-section & depth build-up
2. `fig2_depth_buildup.png` — dredged-depth components
3. `fig3_width_buildup.png` — PIANC two-way width build-up
4. `fig4_breakwater_section.png` — rubble-mound breakwater section (Hudson)
5. `fig5_key_plan.png` — masterplan key-plan schematic

## CAD package (`../output/`)
`Suez_Port_Masterplan.dxf` (AutoCAD R2018, Model + A1 + A3 layouts) and
rendered `.png/.pdf/.svg`, plus `Bill_of_Quantities.csv`, `Coordinates.csv`,
`Engineering_Report.md`, `Layer_Report.txt`.

## Canonical values (validated — do not alter)
Lmax 250 m · bmax 32 m · dmax 12 m · Cb 0.85 · V 6 kn (Panamax bulk).
Channel 2 000 × 224 m, depth 13.41 m · berth pocket 12.84 m · turning Ø 375 m
(11.04 ha) · stopping 1 750 m · anchorage R 360.5 m (40.82 ha) · breakwaters
N 1 450 m / S 950 m, Hudson W50 7.6 t · 9 berths, ≈ 2 600 m quay · tank farm
5 × Ø30 m · silos 10 × Ø10 m.

## Regenerate everything
```powershell
.\.venv\Scripts\python.exe calculations.py     # report + canonical_values.json
.\.venv\Scripts\python.exe figures.py           # engineering figures
.\.venv\Scripts\python.exe generate_port.py     # CAD package (close DXF first)
.\.venv\Scripts\python.exe qa_check.py          # consistency gate
```

> Design-basis QA flag: authoritative vessel = Lmax/bmax/dmax 250/32/12.
> PowerPoint 366/49/15.2 and `suezmax.json` 275/48/16.2 are **superseded**
> earlier AI-tool runs; realign the presentation to this package.

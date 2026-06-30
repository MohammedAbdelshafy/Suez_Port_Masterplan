# SUEZ PORT MASTERPLAN DESIGN

**Student:** Mohamed Abdelshafy (20107979)  
**Course:** ECB 3802 -- Parametric Modeling & Marine Structures  
**Supervisor:** Dr. Walid Al-Amri  
**Drawing:** SPM-001 Rev A  
**Date:** 2026-06-29

> Planning-level concept design. Not for construction. Verify with manoeuvring simulation and a qualified maritime engineer.

## 1. Design Vessel

| Parameter | Value |
|---|---|
| Length overall (LOA) | 250 m |
| Beam (B) | 32 m |
| Draft (T) | 12 m |

## 2. Navigation Design (PIANC concept)

| Parameter | Value | Basis |
|---|---|---|
| Channel length | 2000 m | layout |
| Channel width | 224 m | 7.0·B |
| Dredged depth | -13.4 m CD | T + UKC + allowances |
| Turning basin Ø | 375 m | 1.50·LOA |
| Approach bend radius | 1500 m | PIANC |

## 3. Breakwater (Hudson armour design)

W50 = rho_s·H^3 / (Kd·(Sr-1)^3·cot(alpha))

| Parameter | Value |
|---|---|
| Design wave Hs | 4.5 m |
| Stability coeff. Kd | 4.0 |
| Rock density | 2650 kg/m³ |
| Slope cot(alpha) | 2.0 |
| **Median armour mass W50** | **7.6 t** |
| Crest level | +7.0 m CD |

## 4. Storage

- Liquid bulk: **5 tanks**, Ø30 m, 45 m centres, bunded.
- Dry bulk: **10 silos**, Ø10 m.

## 5. Engineering Assumptions

- Coordinate system is a local grid in metres (E = +X, N = +Y); origin at the SW reference of the developed land.
- Channel width adopts the PIANC concept one-way value (~7·B) for the design vessel; refine with a manoeuvring simulation.
- Dredged depth = draft + 15% net UKC + 0.5 m squat/wave allowance.
- Turning basin Ø = 1.5·LOA (tug-assisted) per PIANC/ROM.
- Breakwater armour sized by Hudson with Kd for rough quarry stone, breaking waves, trunk section.
- Tank spacing follows a 1.5·diameter fire-separation rule of thumb.

## 6. Validation Results

| Check | Result | Detail |
|---|---|---|
| Layer table | PASS | all layers present |
| Geometry present | PASS | 296 entities in model space |
| Tank spacing | PASS | centre spacing 45.0 m (min 45.0 m) |
| Channel width | PASS | width 224 m vs PIANC min 160 m (7.0·B) |
| Turning basin diameter | PASS | Ø 375 m vs min 300 m (1.50·LOA) |
| Parcel overlap | PASS | no overlaps |

## 7. Generated Files

- `Suez_Port_Masterplan.dxf` (AutoCAD R2018)
- `Suez_Port_Masterplan.png / .pdf / .svg`
- `Bill_of_Quantities.csv`, `Coordinates.csv`
- `Layer_Report.txt`, this report.

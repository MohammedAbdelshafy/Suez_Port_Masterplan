# Suez Port Masterplan — Parametric CAD Generator

Engineering-grade, **fully parametric** CAD model of Suez Port, generated
programmatically with [`ezdxf`](https://ezdxf.mozman.at/). Nothing is traced
or hand-drawn — every line is computed from engineering inputs.

| | |
|---|---|
| **Project** | Suez Port Masterplan Design |
| **Student** | Mohamed Abdelshafy (20107979) |
| **Course** | ECB 3802 — Parametric Modeling & Marine Structures |
| **Supervisor** | Dr. Walid Al-Amri |

## Quick start

```bash
pip install -r requirements.txt
python generate_port.py
```

All deliverables are written to `./output/`:

| File | Description |
|---|---|
| `Suez_Port_Masterplan.dxf` | AutoCAD R2018 drawing (DWG-compatible DXF) |
| `Suez_Port_Masterplan.png/.pdf/.svg` | Rendered views |
| `Bill_of_Quantities.csv` | Dredging, quay, tanks, armour, etc. |
| `Coordinates.csv` | Key feature coordinates (local grid) |
| `Engineering_Report.md` | Calculations, assumptions, validation |
| `Layer_Report.txt` | CAD layer table |

> PNG/PDF/SVG require `matplotlib`. If it is not installed the DXF and all
> tables/reports are still produced; only the rendered views are skipped.

## Architecture

```
config.py        Single source of truth: inputs + derived geometry + parcels
layers.py        CAD layer table, dimension & text styles, R2018 document setup
utilities.py     Geometry/drafting helpers (no side effects)
geometry.py      Boundary, land, water, grid, fence, gates, utility corridor
navigation.py    Channel, turning basin, approach bend, arrows, clearances
breakwater.py    N/S breakwaters in plan + Hudson cross-section detail
terminals.py     All terminals + tank farm + silo field + dry dock
roads.py         Primary/secondary roads, roundabouts, parking
dimensions.py    Automatic linear & radial dimensioning
annotations.py   North arrow, scale bar, legend, title block, A1/A3 layouts
validation.py    Pre-export checks (spacing, channel width, basin Ø, overlaps)
export.py        DXF / PNG / PDF / SVG / CSV / reports
generate_port.py Orchestrator (entry point)
```

## Changing the design

Edit the dataclasses in `config.py` (design vessel, channel, breakwater,
tank farm, silos, road widths). Re-run `python generate_port.py` and the whole
masterplan — geometry, dimensions, BoQ and report — regenerates consistently.

## Engineering basis

PIANC WG121 (channel & basin), ROM 3.1-99 (layout), BS 6349 / USACE CEM
(marine works), Hudson formula (armour). See `output/Engineering_Report.md`
for the documented assumptions. **Concept level — not for construction.**

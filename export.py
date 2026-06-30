"""
export.py
=========

All output generation: DXF (R2018, DWG-compatible), raster/vector renders
(PNG / PDF / SVG via the ezdxf matplotlib backend), CSV tables (coordinates,
bill of quantities) and Markdown / text reports.

Each export is independently guarded so a missing optional dependency (e.g.
matplotlib) degrades gracefully instead of aborting the whole run.
"""

from __future__ import annotations

import csv
import logging
import math
from datetime import date

from config import Config, hudson_armour_mass
from layers import layer_report_lines
from utilities import polygon_area, rectangle

log = logging.getLogger("suez.export")


# ----------------------------------------------------------------------------
# DXF
# ----------------------------------------------------------------------------
def export_dxf(doc, cfg: Config) -> None:
    cfg.paths.out_dir.mkdir(parents=True, exist_ok=True)
    doc.saveas(cfg.paths.dxf)
    log.info("DXF written -> %s", cfg.paths.dxf)


# ----------------------------------------------------------------------------
# Rendered outputs (PNG / PDF / SVG)
# ----------------------------------------------------------------------------
def export_renders(doc, cfg: Config) -> list[str]:
    produced: list[str] = []
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from ezdxf.addons.drawing import Frontend, RenderContext
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    except Exception as exc:  # pragma: no cover - optional dependency
        log.warning("Skipping PNG/PDF/SVG (matplotlib unavailable): %s", exc)
        return produced

    # Render the printable A1 sheet (viewport + title block + furniture).
    sheet = doc.layout("A1-LAYOUT")
    for path, dpi in ((cfg.paths.png, 200), (cfg.paths.pdf, None),
                      (cfg.paths.svg, None)):
        try:
            fig = plt.figure(figsize=(16.54, 11.69))  # A1 aspect (landscape)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_axis_off()
            ctx = RenderContext(doc)
            out = MatplotlibBackend(ax)
            Frontend(ctx, out).draw_layout(sheet, finalize=True)
            if dpi:
                fig.savefig(path, dpi=dpi)
            else:
                fig.savefig(path)
            plt.close(fig)
            produced.append(path.name)
            log.info("Rendered A1 sheet -> %s", path)
        except Exception as exc:  # pragma: no cover
            log.warning("Failed to render %s: %s", path.name, exc)
    return produced


# ----------------------------------------------------------------------------
# CSV: coordinates
# ----------------------------------------------------------------------------
def export_coordinates(cfg: Config) -> None:
    lay = cfg.layout
    rows = [
        ("Channel mouth (CL)", lay.channel_mouth_x, lay.channel_cy),
        ("Channel inner (CL)", lay.channel_inner_x, lay.channel_cy),
        ("Turning basin centre", *lay.basin_center),
        ("Quay line origin", lay.quay_line_x, lay.land_bounds[1]),
    ]
    for p in cfg.parcels:
        rows.append((f"{p.name} (SW corner)", p.x, p.y))
        rows.append((f"{p.name} (centre)", p.x + p.w / 2, p.y + p.h / 2))

    with open(cfg.paths.coords, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Feature", "Easting_X_m", "Northing_Y_m"])
        for name, x, y in rows:
            w.writerow([name, f"{x:.2f}", f"{y:.2f}"])
    log.info("Coordinate table -> %s (%d points)", cfg.paths.coords, len(rows))


# ----------------------------------------------------------------------------
# CSV: bill of quantities
# ----------------------------------------------------------------------------
def export_boq(cfg: Config) -> None:
    lay = cfg.layout
    t = cfg.tanks
    s = cfg.silos
    channel_area = cfg.nav.channel_length * cfg.nav.channel_width
    basin_area = math.pi * lay.basin_radius ** 2
    dredge_vol = (channel_area + basin_area) * cfg.dredged_depth
    land_area = polygon_area(rectangle(*_xywh(lay.land_bounds)))
    quay_len = sum(p.h for p in cfg.parcels if p.has_quay)
    total_berths = sum(p.berths for p in cfg.parcels)

    rows = [
        ("Dredging (channel + basin)", "m3", round(dredge_vol, 0)),
        ("Navigation channel area", "m2", round(channel_area, 0)),
        ("Turning basin area", "m2", round(basin_area, 0)),
        ("Reclaimed land area", "m2", round(land_area, 0)),
        ("Quay wall length (total)", "m", round(quay_len, 0)),
        ("Berths (count)", "no", total_berths),
        ("Breakwater length (2 arms)", "m", 2 * 700),
        ("Storage tanks", "no", t.count),
        ("Tank diameter", "m", t.diameter),
        ("Silos", "no", s.count),
        ("Silo diameter", "m", s.diameter),
        ("Armour stone unit (Hudson W50)", "t", round(hudson_armour_mass(cfg.bw), 1)),
    ]
    with open(cfg.paths.boq, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Item", "Unit", "Quantity"])
        for item, unit, qty in rows:
            w.writerow([item, unit, qty])
    log.info("Bill of quantities -> %s", cfg.paths.boq)


# ----------------------------------------------------------------------------
# Reports
# ----------------------------------------------------------------------------
def export_layer_report(cfg: Config) -> None:
    with open(cfg.paths.layer_report, "w", encoding="utf-8") as f:
        f.write("\n".join(layer_report_lines()) + "\n")
    log.info("Layer report -> %s", cfg.paths.layer_report)


def export_engineering_report(cfg: Config, checks) -> None:
    pj = cfg.project
    v = cfg.vessel
    n = cfg.nav
    w50 = hudson_armour_mass(cfg.bw)
    lines = [
        f"# {pj.title}",
        "",
        f"**Student:** {pj.student} ({pj.student_id})  ",
        f"**Course:** {pj.course_code} -- {pj.course_name}  ",
        f"**Supervisor:** {pj.supervisor}  ",
        f"**Drawing:** {pj.drawing_number} Rev {pj.revision}  ",
        f"**Date:** {date(2026, 6, 29).isoformat()}",
        "",
        "> Planning-level concept design. Not for construction. Verify with "
        "manoeuvring simulation and a qualified maritime engineer.",
        "",
        "## 1. Design Vessel",
        "",
        "| Parameter | Value |",
        "|---|---|",
        f"| Length overall (LOA) | {v.loa:.0f} m |",
        f"| Beam (B) | {v.beam:.0f} m |",
        f"| Draft (T) | {v.draft:.0f} m |",
        "",
        "## 2. Navigation Design (PIANC concept)",
        "",
        "| Parameter | Value | Basis |",
        "|---|---|---|",
        f"| Channel length | {n.channel_length:.0f} m | layout |",
        f"| Channel width | {n.channel_width:.0f} m | {n.channel_width / v.beam:.1f}·B |",
        f"| Dredged depth | -{cfg.dredged_depth:.1f} m CD | T + UKC + allowances |",
        f"| Turning basin Ø | {n.turning_basin_diameter:.0f} m | "
        f"{n.turning_basin_diameter / v.loa:.2f}·LOA |",
        f"| Approach bend radius | {n.channel_bend_radius:.0f} m | PIANC |",
        "",
        "## 3. Breakwater (Hudson armour design)",
        "",
        "W50 = rho_s·H^3 / (Kd·(Sr-1)^3·cot(alpha))",
        "",
        "| Parameter | Value |",
        "|---|---|",
        f"| Design wave Hs | {cfg.bw.design_wave_h:.1f} m |",
        f"| Stability coeff. Kd | {cfg.bw.kd_stability:.1f} |",
        f"| Rock density | {cfg.bw.rock_density:.0f} kg/m³ |",
        f"| Slope cot(alpha) | {cfg.bw.armour_slope_cot:.1f} |",
        f"| **Median armour mass W50** | **{w50:.1f} t** |",
        f"| Crest level | +{cfg.bw.crest_level:.1f} m CD |",
        "",
        "## 4. Storage",
        "",
        f"- Liquid bulk: **{cfg.tanks.count} tanks**, Ø{cfg.tanks.diameter:.0f} m, "
        f"{cfg.tanks.diameter * cfg.tanks.spacing_factor:.0f} m centres, bunded.",
        f"- Dry bulk: **{cfg.silos.count} silos**, Ø{cfg.silos.diameter:.0f} m.",
        "",
        "## 5. Engineering Assumptions",
        "",
        "- Coordinate system is a local grid in metres (E = +X, N = +Y); origin "
        "at the SW reference of the developed land.",
        "- Channel width adopts the PIANC concept one-way value (~7·B) for the "
        "design vessel; refine with a manoeuvring simulation.",
        "- Dredged depth = draft + 15% net UKC + 0.5 m squat/wave allowance.",
        "- Turning basin Ø = 1.5·LOA (tug-assisted) per PIANC/ROM.",
        "- Breakwater armour sized by Hudson with Kd for rough quarry stone, "
        "breaking waves, trunk section.",
        "- Tank spacing follows a 1.5·diameter fire-separation rule of thumb.",
        "",
        "## 6. Validation Results",
        "",
        "| Check | Result | Detail |",
        "|---|---|---|",
    ]
    for c in checks:
        lines.append(f"| {c.name} | {'PASS' if c.passed else 'FAIL'} | {c.message} |")
    lines += [
        "",
        "## 7. Generated Files",
        "",
        "- `Suez_Port_Masterplan.dxf` (AutoCAD R2018)",
        "- `Suez_Port_Masterplan.png / .pdf / .svg`",
        "- `Bill_of_Quantities.csv`, `Coordinates.csv`",
        "- `Layer_Report.txt`, this report.",
        "",
    ]
    with open(cfg.paths.report, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log.info("Engineering report -> %s", cfg.paths.report)


# ----------------------------------------------------------------------------
def _xywh(bounds):
    x0, y0, x1, y1 = bounds
    return (x0, y0, x1 - x0, y1 - y0)


def export_all(doc, cfg: Config, checks) -> list[str]:
    export_dxf(doc, cfg)
    export_coordinates(cfg)
    export_boq(cfg)
    export_layer_report(cfg)
    export_engineering_report(cfg, checks)
    rendered = export_renders(doc, cfg)
    return rendered

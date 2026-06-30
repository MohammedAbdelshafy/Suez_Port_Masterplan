"""
annotations.py
==============

Sheet furniture, drawn the CAD-correct way: the title block, legend, scale bar
and north arrow live in **paper space** (A1 and A3 layouts), arranged around a
viewport onto the model. This keeps model space clean (no furniture overlapping
the plan) and gives genuinely printable sheets.

Title-block text is pulled from ``config.ProjectInfo``.
"""

from __future__ import annotations

import logging

from config import Config
from layers import LAYERS

log = logging.getLogger("suez.annotations")

# Sheet sizes in mm (landscape).
SHEETS = {"A1": (841.0, 594.0), "A3": (420.0, 297.0)}


def _fit_view(site_bounds, vp_w, vp_h, margin=1.06):
    """Return (view_center, view_height, mm_per_m) fitting the site in a viewport."""
    x0, y0, x1, y1 = site_bounds
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    span_x, span_y = (x1 - x0), (y1 - y0)
    # Model width that must fit the viewport width (account for aspect).
    view_w = max(span_x, span_y * vp_w / vp_h) * margin
    view_h = view_w * vp_h / vp_w
    mm_per_m = vp_w / view_w
    return (cx, cy), view_h, mm_per_m


def _draw_titleblock(layout, cfg: Config, x, y, w, h) -> None:
    pj = cfg.project
    layout.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                          close=True, dxfattribs={"layer": "TITLEBLOCK"})
    layout.add_line((x, y + h - h * 0.28), (x + w, y + h - h * 0.28),
                    dxfattribs={"layer": "TITLEBLOCK"})
    th = h * 0.072
    rows = [
        (pj.title, th * 1.45, h - h * 0.17),
        (f"Student: {pj.student}   ID: {pj.student_id}", th, h - h * 0.36),
        (f"Course: {pj.course_code} - {pj.course_name}", th * 0.92, h - h * 0.48),
        (f"Supervisor: {pj.supervisor}", th, h - h * 0.60),
        (f"Dwg: {pj.drawing_number}   Rev: {pj.revision}   Date: 2026-06-29",
         th, h - h * 0.72),
        ("Scale: AS NOTED    Units: METRES", th, h - h * 0.84),
        ("CONCEPT DESIGN - NOT FOR CONSTRUCTION", th * 0.9, h - h * 0.94),
    ]
    for text, size, dy in rows:
        layout.add_text(text, dxfattribs={"layer": "TITLEBLOCK",
                                          "height": size}).set_placement((x + w * 0.03, y + dy))


def _draw_legend(layout, cfg: Config, x, y, h) -> None:
    show = ["WATER", "LAND", "BREAKWATER", "CHANNEL", "TURNING_BASIN",
            "QUAYS", "BERTHS", "TERMINALS", "TANKS", "SILOS", "ROADS"]
    sw = h * 0.05
    layout.add_text("LEGEND", dxfattribs={"layer": "LEGEND", "height": sw * 1.4}
                    ).set_placement((x, y + len(show) * sw * 1.4 + sw))
    for i, name in enumerate(show):
        ld = next(l for l in LAYERS if l.name == name)
        yy = y + (len(show) - 1 - i) * sw * 1.4
        layout.add_lwpolyline(
            [(x, yy), (x + sw * 1.6, yy), (x + sw * 1.6, yy + sw), (x, yy + sw)],
            close=True, dxfattribs={"layer": "LEGEND", "color": ld.color})
        layout.add_text(name, dxfattribs={"layer": "LEGEND", "height": sw * 0.85}
                        ).set_placement((x + sw * 2.0, yy + sw * 0.15))


def _draw_scale_bar(layout, cfg: Config, x, y, mm_per_m) -> None:
    """Graphic scale bar; divisions chosen so the bar is a sensible length."""
    total_m = 1000.0
    divisions = 4
    seg_m = total_m / divisions
    seg_mm = seg_m * mm_per_m
    bar_h = 3.0
    for i in range(divisions):
        bx = x + i * seg_mm
        color = 7 if i % 2 == 0 else 0
        layout.add_lwpolyline(
            [(bx, y), (bx + seg_mm, y), (bx + seg_mm, y + bar_h), (bx, y + bar_h)],
            close=True, dxfattribs={"layer": "LEGEND", "color": color})
        layout.add_text(f"{int(i * seg_m)}", dxfattribs={"layer": "LEGEND",
                        "height": 2.6}).set_placement((bx, y - 5))
    layout.add_text(f"{int(total_m)}", dxfattribs={"layer": "LEGEND", "height": 2.6}
                    ).set_placement((x + divisions * seg_mm, y - 5))
    scale_denom = 1000.0 / mm_per_m
    layout.add_text(f"SCALE  1 : {scale_denom:,.0f}  (metres)",
                    dxfattribs={"layer": "LEGEND", "height": 3.0}
                    ).set_placement((x, y + bar_h + 3))


def _draw_north_arrow(layout, x, y, size) -> None:
    layout.add_lwpolyline(
        [(x, y + size), (x - size * 0.3, y - size * 0.4), (x, y - size * 0.15)],
        close=True, dxfattribs={"layer": "LEGEND", "color": 7})
    layout.add_lwpolyline(
        [(x, y + size), (x + size * 0.3, y - size * 0.4), (x, y - size * 0.15)],
        close=True, dxfattribs={"layer": "LEGEND", "color": 0})
    layout.add_text("N", dxfattribs={"layer": "LEGEND", "height": size * 0.5}
                    ).set_placement((x - size * 0.18, y + size + 2))


def setup_paperspace(doc, cfg: Config) -> None:
    """Create A1 and A3 printable layouts with a viewport and full furniture."""
    for sheet, (pw, ph) in SHEETS.items():
        name = f"{sheet}-LAYOUT"
        try:
            layout = doc.layouts.new(name)
        except Exception:
            layout = doc.layouts.get(name)
        layout.page_setup(size=(pw, ph), margins=(0, 0, 0, 0), units="mm")

        m = 10.0                       # sheet margin [mm]
        strip_h = ph * 0.13            # bottom furniture strip
        # Sheet border
        layout.add_lwpolyline(
            [(m, m), (pw - m, m), (pw - m, ph - m), (m, ph - m)],
            close=True, dxfattribs={"layer": "TITLEBLOCK"})

        # Viewport occupies the area above the bottom strip.
        vp_x0, vp_y0 = m + 2, m + strip_h + 2
        vp_x1, vp_y1 = pw - m - 2, ph - m - 2
        vp_w, vp_h = vp_x1 - vp_x0, vp_y1 - vp_y0
        center, view_h, mm_per_m = _fit_view(cfg.layout.site_bounds, vp_w, vp_h)
        layout.add_viewport(
            center=((vp_x0 + vp_x1) / 2, (vp_y0 + vp_y1) / 2),
            size=(vp_w, vp_h),
            view_center_point=center,
            view_height=view_h,
        )
        # Viewport border
        layout.add_lwpolyline(
            [(vp_x0, vp_y0), (vp_x1, vp_y0), (vp_x1, vp_y1), (vp_x0, vp_y1)],
            close=True, dxfattribs={"layer": "TITLEBLOCK"})

        # --- furniture in the bottom strip ---------------------------------
        tb_w = pw * 0.38
        _draw_titleblock(layout, cfg, pw - m - tb_w, m, tb_w, strip_h)
        _draw_legend(layout, cfg, m + 6, m + strip_h * 0.12, strip_h)
        _draw_scale_bar(layout, cfg, pw * 0.40, m + strip_h * 0.45, mm_per_m)
        # north arrow in the top-right corner of the viewport
        _draw_north_arrow(layout, vp_x1 - 18, vp_y1 - 28, 12)
        # sheet id
        layout.add_text(f"{cfg.project.title}  |  {sheet}  |  {cfg.project.drawing_number}",
                        dxfattribs={"layer": "TITLEBLOCK", "height": 3.0}
                        ).set_placement((m + 6, ph - m - 8))
    log.info("Paper-space layouts A1 & A3 created with title block & furniture")


def draw_all(msp, doc, cfg: Config) -> None:
    # All furniture now lives in paper space (keeps model space clean).
    setup_paperspace(doc, cfg)

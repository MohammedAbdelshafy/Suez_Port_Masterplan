"""
terminals.py
============

Terminal parcels and their internal components, plus the tank farm and silo
field. Each waterfront terminal gets a parcel, quay wall, berth faces, storage
yard, service area and an access road stub. Inland terminals get a parcel,
storage and access.

All placement is parametric -- driven by the :class:`Parcel` band definitions
computed in ``config.build_parcels``.
"""

from __future__ import annotations

import logging

from config import PALETTE, Config, Parcel
from utilities import (add_circle, add_line, add_mtext, add_polyline,
                       add_solid_hatch, add_text, circle_points, rectangle)

log = logging.getLogger("suez.terminals")

# Per-parcel yard tint (true-colour RGB from the palette).
_TINT = {
    "CONTAINER": "container", "PASSENGER": "passenger", "GEN_CARGO": "gen_cargo",
    "RORO": "roro", "OIL": "oil", "LIQUID_BULK": "tank", "DRY_BULK": "silo",
    "DRY_DOCK": "generic", "REPAIR": "generic", "EXPANSION": "expansion",
}


def _tint(p: Parcel) -> tuple[int, int, int]:
    return PALETTE[_TINT.get(p.key, "generic")]


# ----------------------------------------------------------------------------
# Generic parcel rendering
# ----------------------------------------------------------------------------
def _draw_parcel_outline(msp, p: Parcel, cfg: Config) -> None:
    pts = rectangle(p.x, p.y, p.w, p.h)
    add_polyline(msp, pts, "TERMINALS")
    add_text(msp, p.name, (p.x + p.w / 2, p.y + p.h - 50),
             cfg.style.text_label, "TERMINALS")


def _draw_quay_and_berths(msp, p: Parcel, cfg: Config) -> None:
    """Quay wall on the parcel's WEST edge plus evenly divided berth faces."""
    qx = p.x
    add_line(msp, (qx, p.y), (qx, p.y + p.h), "QUAYS")
    # apron strip
    apron = cfg.roads.quay_apron_setback
    add_polyline(msp, rectangle(qx, p.y, apron, p.h), "QUAYS", close=True)

    if p.berths <= 0:
        return
    seg = p.h / p.berths
    for i in range(p.berths):
        by0 = p.y + i * seg
        by1 = by0 + seg
        # berth face slightly seaward of the quay line
        add_line(msp, (qx - 8, by0 + 10), (qx - 8, by1 - 10), "BERTHS")
        add_text(msp, f"B{i + 1}", (qx + 40, (by0 + by1) / 2),
                 cfg.style.text_small, "BERTHS", align="MIDDLE_LEFT")
    # berth length note (= each berth segment)
    add_text(msp, f"{p.berths} BERTHS @ {seg:.0f} m",
             (qx + apron + 30, p.y + p.h / 2), cfg.style.text_small, "BERTHS",
             align="MIDDLE_LEFT")


def _draw_storage_service_access(msp, p: Parcel, cfg: Config,
                                 quay_side: bool) -> None:
    """Storage yard + service area + access road stub inside the parcel."""
    apron = cfg.roads.quay_apron_setback if quay_side else 30.0
    inner_x = p.x + apron + 30
    inner_w = p.w - apron - 90
    if inner_w <= 60:
        return
    # storage yard (front 60%)
    yard_h = p.h * 0.6
    add_polyline(msp, rectangle(inner_x, p.y + 40, inner_w, yard_h),
                 "TERMINALS")
    add_solid_hatch(msp, rectangle(inner_x, p.y + 40, inner_w, yard_h),
                    layer="HATCH", rgb=_tint(p), transparency=0.25)
    add_text(msp, "STORAGE YARD", (inner_x + inner_w / 2, p.y + 40 + yard_h / 2),
             cfg.style.text_small, "TERMINALS")
    # service area (rear strip)
    sv_y = p.y + 40 + yard_h + 20
    sv_h = p.h - (yard_h + 80)
    if sv_h > 40:
        add_polyline(msp, rectangle(inner_x, sv_y, inner_w, sv_h), "TERMINALS")
        add_text(msp, "SERVICE AREA", (inner_x + inner_w / 2, sv_y + sv_h / 2),
                 cfg.style.text_small, "TERMINALS")
    # access road stub to the east boundary of the parcel
    mid_y = p.y + p.h / 2
    add_line(msp, (p.x + p.w, mid_y), (inner_x + inner_w, mid_y), "ROADS")


def draw_waterfront_terminal(msp, p: Parcel, cfg: Config) -> None:
    _draw_parcel_outline(msp, p, cfg)
    _draw_quay_and_berths(msp, p, cfg)
    _draw_storage_service_access(msp, p, cfg, quay_side=True)


def draw_inland_terminal(msp, p: Parcel, cfg: Config) -> None:
    _draw_parcel_outline(msp, p, cfg)
    _draw_storage_service_access(msp, p, cfg, quay_side=False)


# ----------------------------------------------------------------------------
# Tank farm (liquid bulk)
# ----------------------------------------------------------------------------
def draw_tank_farm(msp, cfg: Config) -> None:
    p = cfg.parcel("LIQUID_BULK")
    t = cfg.tanks
    spacing = t.diameter * t.spacing_factor
    r = t.diameter / 2.0

    # bund wall around the tank group
    group_w = (t.count - 1) * spacing
    start_x = p.x + p.w / 2 - group_w / 2
    cy = p.y + p.h * 0.45
    bund = rectangle(start_x - r - t.bund_clearance,
                     cy - r - t.bund_clearance,
                     group_w + 2 * (r + t.bund_clearance),
                     2 * (r + t.bund_clearance))
    add_polyline(msp, bund, "TANKS")
    add_text(msp, "BUND WALL", (bund[0][0] + 20, bund[2][1] - 20),
             cfg.style.text_small, "TANKS", align="MIDDLE_LEFT")

    for i in range(t.count):
        c = (start_x + i * spacing, cy)
        add_circle(msp, c, r, "TANKS")
        add_text(msp, f"T{i + 1}", c, cfg.style.text_small, "TANKS")
    add_text(msp, f"{t.count}× TANKS  Ø{t.diameter:.0f} m  @ {spacing:.0f} m c/c",
             (p.x + p.w / 2, cy - r - t.bund_clearance - 50),
             cfg.style.text_small, "TANKS")

    # pipe corridor + safety buffer notes
    add_line(msp, (p.x + 20, p.y + p.h - 60), (p.x + p.w - 20, p.y + p.h - 60),
             "ROADS", linetype="DASHED2")
    add_text(msp, "PIPE CORRIDOR", (p.x + p.w / 2, p.y + p.h - 90),
             cfg.style.text_small, "TANKS")
    log.info("Tank farm: %d tanks, spacing %.1f m", t.count, spacing)


# ----------------------------------------------------------------------------
# Silo field (dry bulk)
# ----------------------------------------------------------------------------
def draw_silo_field(msp, cfg: Config) -> None:
    p = cfg.parcel("DRY_BULK")
    s = cfg.silos
    spacing = s.diameter * s.spacing_factor
    r = s.diameter / 2.0
    cols = (s.count + s.rows - 1) // s.rows

    start_x = p.x + p.w * 0.30
    start_y = p.y + p.h * 0.40
    n = 0
    for row in range(s.rows):
        for col in range(cols):
            if n >= s.count:
                break
            c = (start_x + col * spacing, start_y + row * spacing)
            add_circle(msp, c, r, "SILOS")
            n += 1
    add_text(msp, f"{s.count}× SILOS  Ø{s.diameter:.0f} m  @ {spacing:.0f} m c/c",
             (p.x + p.w / 2, start_y - r - 60), cfg.style.text_small, "SILOS")

    # truck access + rail corridor + storage yard
    add_line(msp, (p.x + 20, p.y + 60), (p.x + p.w - 20, p.y + 60),
             "ROADS")
    add_text(msp, "TRUCK ACCESS", (p.x + p.w / 2, p.y + 90),
             cfg.style.text_small, "SILOS")
    add_line(msp, (p.x + 20, p.y + p.h - 60), (p.x + p.w - 20, p.y + p.h - 60),
             "ROADS", linetype="DASHED2")
    add_text(msp, "RAIL CORRIDOR", (p.x + p.w / 2, p.y + p.h - 90),
             cfg.style.text_small, "SILOS")
    log.info("Silo field: %d silos in %d rows", s.count, s.rows)


# ----------------------------------------------------------------------------
# Dry dock detail
# ----------------------------------------------------------------------------
def draw_dry_dock(msp, cfg: Config) -> None:
    p = cfg.parcel("DRY_DOCK")
    _draw_parcel_outline(msp, p, cfg)
    # graving dock rectangle sized to the design vessel + clearance
    dock_l = cfg.vessel.loa + 40
    dock_w = cfg.vessel.beam + 20
    dx = p.x + (p.w - dock_w) / 2
    dy = p.y + (p.h - dock_l) / 2
    add_polyline(msp, rectangle(dx, dy, dock_w, dock_l), "BERTHS")
    add_mtext(msp, f"GRAVING DOCK\n{dock_l:.0f}×{dock_w:.0f} m",
              (dx + dock_w / 2, dy + dock_l / 2), cfg.style.text_small, "BERTHS")
    # caisson gate at the south (water) end
    add_line(msp, (dx, dy), (dx + dock_w, dy), "QUAYS")


def draw_all(msp, cfg: Config) -> None:
    waterfront = {"CONTAINER", "PASSENGER", "GEN_CARGO", "RORO", "OIL"}
    for p in cfg.parcels:
        if p.key in waterfront:
            draw_waterfront_terminal(msp, p, cfg)
        elif p.key in {"EXPANSION", "REPAIR"}:
            draw_inland_terminal(msp, p, cfg)
        # LIQUID_BULK / DRY_BULK / DRY_DOCK only get their parcel outline here;
        # their specialised content (tanks / silos / dock) is drawn below so the
        # generic storage-yard fill does not overprint them.
        elif p.key in {"LIQUID_BULK", "DRY_BULK"}:
            add_solid_hatch(msp, rectangle(p.x, p.y, p.w, p.h), layer="HATCH",
                            rgb=_tint(p), transparency=0.45)
            _draw_parcel_outline(msp, p, cfg)
            mid_y = p.y + p.h / 2
            add_line(msp, (p.x + p.w, mid_y), (p.x + 30, mid_y), "ROADS")
    draw_dry_dock(msp, cfg)
    draw_tank_farm(msp, cfg)
    draw_silo_field(msp, cfg)

"""
geometry.py
===========

Site-scale geometry: port boundary, land/water masses, coordinate grid,
security fence, gates and utility corridors. Everything is derived from the
:class:`Layout` anchors in ``config``.
"""

from __future__ import annotations

import logging

from config import PALETTE, Config
from utilities import (add_line, add_mtext, add_polyline, add_solid_hatch,
                       add_text, rectangle)

log = logging.getLogger("suez.geometry")


def draw_water(msp, cfg: Config) -> None:
    """Harbour and approach water area (light-blue sea fill on WATER layer)."""
    x0, y0, x1, y1 = cfg.layout.water_bounds
    pts = rectangle(x0, y0, x1 - x0, y1 - y0)
    add_polyline(msp, pts, "WATER")
    add_solid_hatch(msp, pts, layer="WATER", rgb=PALETTE["sea"], transparency=0.15)
    # Inner harbour basin label (near the quay side).
    add_text(msp, "HARBOUR BASIN", (x1 - 350, y1 - 200),
             cfg.style.text_label, "WATER")


def draw_coastal_context(msp, cfg: Config) -> None:
    """
    Open sea, sand spit/shoal and the canal-approach axis -- the natural setting
    after the real Suez Canal port entrance (NASA satellite reference): open sea
    to the seaward (west) side, a sand spit on the seaward flank.
    """
    x0, y0, x1, y1 = cfg.layout.water_bounds
    cy = cfg.layout.channel_cy
    # Open-sea label (seaward, beyond the breakwaters).
    add_text(msp, "OPEN SEA", (x0 + 350, y1 - 250), cfg.style.text_label, "WATER")
    add_text(msp, "(approach from seaward / NW)", (x0 + 350, y1 - 320),
             cfg.style.text_small, "WATER")

    # Sand spit / shoal on the north seaward flank (echoes the eastern sandbar
    # of the satellite image), drawn as a sandy reclaimable triangle.
    spit = [(x0, y1), (x0 + 900, y1), (x0, y1 - 700)]
    add_polyline(msp, spit, "LAND")
    add_solid_hatch(msp, spit, layer="LAND", rgb=PALETTE["sand"], transparency=0.1)
    add_text(msp, "SAND SPIT / SHOAL", (x0 + 250, y1 - 230),
             cfg.style.text_small, "LAND")

    # Canal-approach axis note (the channel aligns with the canal entrance).
    add_text(msp, "SUEZ CANAL APPROACH AXIS",
             (cfg.layout.channel_mouth_x + 250, cy + 150),
             cfg.style.text_small, "CENTERLINES", align="MIDDLE_LEFT")

    # Reference provenance note (lower sea area, east of the section detail).
    add_mtext(msp,
              "LAYOUT CONFIGURATION REFERENCED FROM NASA SATELLITE IMAGE\n"
              "OF THE SUEZ CANAL PORT ENTRANCE - RECONSTRUCTED\n"
              "MATHEMATICALLY (PIANC / BS 6349; NOT A PIXEL TRACE).",
              (cfg.layout.channel_mouth_x - 475, 760),
              cfg.style.text_small, "TEXT", width=1450, attach=1)
    log.info("Coastal context (sea, spit, canal axis) drawn")


def draw_land(msp, cfg: Config) -> None:
    """Reclaimed land block (light sand fill)."""
    x0, y0, x1, y1 = cfg.layout.land_bounds
    pts = rectangle(x0, y0, x1 - x0, y1 - y0)
    add_polyline(msp, pts, "LAND")
    add_solid_hatch(msp, pts, layer="LAND", rgb=PALETTE["land"], transparency=0.1)


def draw_port_boundary(msp, cfg: Config) -> None:
    """Overall port property boundary."""
    x0, y0, x1, y1 = cfg.layout.site_bounds
    pad = 120.0
    pts = rectangle(x0 + pad, y0 + pad, (x1 - x0) - 2 * pad, (y1 - y0) - 2 * pad)
    add_polyline(msp, pts, "BOUNDARY")
    add_text(msp, "PORT PROPERTY BOUNDARY",
             (x0 + pad + 300, y1 - pad - 60), cfg.style.text_small, "BOUNDARY",
             align="MIDDLE_LEFT")


def draw_security_fence(msp, cfg: Config) -> None:
    """Security fence set in from the land boundary, with gate gaps."""
    x0, y0, x1, y1 = cfg.layout.land_bounds
    s = cfg.roads.fence_setback
    fx0, fy0, fx1, fy1 = x0 + s, y0 + s, x1 - s, y1 - s
    # East side fence drawn as two segments leaving a main gate gap.
    gate_y = (fy0 + fy1) / 2
    gate_half = 60.0
    # North, south, east(with gap), and a short west return at top/bottom.
    add_line(msp, (fx0, fy1), (fx1, fy1), "BOUNDARY")          # north
    add_line(msp, (fx0, fy0), (fx1, fy0), "BOUNDARY")          # south
    add_line(msp, (fx1, fy0), (fx1, gate_y - gate_half), "BOUNDARY")
    add_line(msp, (fx1, gate_y + gate_half), (fx1, fy1), "BOUNDARY")
    # Gate marker
    add_text(msp, "MAIN GATE", (fx1 + 60, gate_y), cfg.style.text_small,
             "TEXT", align="MIDDLE_LEFT")
    _gate_marker(msp, (fx1, gate_y), cfg)

    # A secondary truck gate near the south-east corner.
    truck_y = fy0 + 400
    add_text(msp, "TRUCK GATE", (fx1 + 60, truck_y), cfg.style.text_small,
             "TEXT", align="MIDDLE_LEFT")
    _gate_marker(msp, (fx1, truck_y), cfg)
    log.info("Security fence and 2 gates drawn")


def _gate_marker(msp, at, cfg: Config) -> None:
    x, y = at
    add_line(msp, (x - 20, y - 70), (x - 20, y + 70), "ROADS")
    add_line(msp, (x + 20, y - 70), (x + 20, y + 70), "ROADS")


def draw_coordinate_grid(msp, cfg: Config) -> None:
    """Light reference grid with coordinate labels along the edges."""
    x0, y0, x1, y1 = cfg.layout.site_bounds
    step = cfg.style.grid_spacing
    # vertical lines
    gx = _ceil_to(x0, step)
    while gx <= x1:
        add_line(msp, (gx, y0), (gx, y1), "GRID")
        add_text(msp, f"E {gx:.0f}", (gx, y0 - 60), cfg.style.text_small, "GRID")
        gx += step
    # horizontal lines
    gy = _ceil_to(y0, step)
    while gy <= y1:
        add_line(msp, (x0, gy), (x1, gy), "GRID")
        add_text(msp, f"N {gy:.0f}", (x0 - 120, gy), cfg.style.text_small, "GRID")
        gy += step
    log.info("Coordinate grid drawn at %.0f m spacing", step)


def draw_utility_corridor(msp, cfg: Config) -> None:
    """A utility corridor strip running along the inland facility band."""
    p = cfg.parcel("LIQUID_BULK")
    cx = p.x - 60
    y0, y1 = cfg.layout.land_bounds[1] + 200, cfg.layout.land_bounds[3] - 200
    add_line(msp, (cx, y0), (cx, y1), "ROADS", linetype="DASHED2")
    add_text(msp, "UTILITY CORRIDOR", (cx - 20, (y0 + y1) / 2), cfg.style.text_small,
             "TEXT", rotation=90)


def draw_anchorage(msp, cfg: Config) -> None:
    """Designated anchorage area in the open sea, west of the breakwaters."""
    lay = cfg.layout
    wx0 = lay.water_bounds[0]
    cy = lay.channel_cy
    # Place the anchorage north-west of the channel mouth, well clear of the approach.
    ax = wx0 + 400
    ay = cy + 600
    aw, ah = 800.0, 600.0
    pts = rectangle(ax, ay, aw, ah)
    add_polyline(msp, pts, "WATER", close=True)
    add_text(msp, "DESIGNATED ANCHORAGE AREA",
             (ax + aw / 2, ay + ah - 60), cfg.style.text_label, "WATER")
    add_text(msp, "(+) ANCHOR SYMBOL",
             (ax + aw / 2, ay + ah / 2), cfg.style.text_small, "WATER")
    add_text(msp, "DEPTH: NATURAL SEABED",
             (ax + aw / 2, ay + 60), cfg.style.text_small, "WATER")
    log.info("Anchorage area drawn")


def draw_admin_building(msp, cfg: Config) -> None:
    """Port Authority / Admin building near the main gate."""
    lay = cfg.layout
    x0, y0, x1, y1 = lay.land_bounds
    s = cfg.roads.fence_setback
    gate_y = (y0 + s + y1 - s) / 2
    # Building east of the spine road, near the main gate.
    bx = x1 - s - 440
    by = gate_y - 120
    bw, bh = 260.0, 180.0
    pts = rectangle(bx, by, bw, bh)
    add_polyline(msp, pts, "FACILITIES")
    add_solid_hatch(msp, pts, layer="HATCH", rgb=(220, 210, 190), transparency=0.3)
    # Building cross-hatch
    add_line(msp, (bx, by), (bx + bw, by + bh), "FACILITIES")
    add_line(msp, (bx + bw, by), (bx, by + bh), "FACILITIES")
    add_text(msp, "PORT AUTHORITY", (bx + bw / 2, by + bh - 30),
             cfg.style.text_small, "FACILITIES")
    add_text(msp, "ADMIN BUILDING", (bx + bw / 2, by + bh / 2),
             cfg.style.text_small, "FACILITIES")
    log.info("Admin building drawn")


def draw_fire_station(msp, cfg: Config) -> None:
    """Fire station near the oil terminal for emergency response."""
    oil = cfg.parcel("OIL")
    # Place just east (inland) of the oil terminal upper boundary.
    fx = oil.x + oil.w + 140
    fy = oil.y + oil.h - 200
    fw, fh = 160.0, 140.0
    pts = rectangle(fx, fy, fw, fh)
    add_polyline(msp, pts, "FACILITIES")
    add_solid_hatch(msp, pts, layer="HATCH", rgb=(236, 200, 200), transparency=0.3)
    add_text(msp, "FIRE STATION", (fx + fw / 2, fy + fh / 2 + 20),
             cfg.style.text_small, "FACILITIES")
    add_text(msp, "[!] EMERGENCY", (fx + fw / 2, fy + fh / 2 - 20),
             cfg.style.text_small, "FACILITIES")
    log.info("Fire station drawn")


def draw_mosque(msp, cfg: Config) -> None:
    """Mosque and staff amenities block near the ecosystem zone."""
    eco = cfg.parcel("ECOSYSTEM")
    mx = eco.x + eco.w - 220
    my = eco.y + 60
    mw, mh = 140.0, 120.0
    pts = rectangle(mx, my, mw, mh)
    add_polyline(msp, pts, "FACILITIES")
    add_solid_hatch(msp, pts, layer="HATCH", rgb=(220, 220, 235), transparency=0.3)
    add_text(msp, "MOSQUE &", (mx + mw / 2, my + mh / 2 + 20),
             cfg.style.text_small, "FACILITIES")
    add_text(msp, "AMENITIES", (mx + mw / 2, my + mh / 2 - 20),
             cfg.style.text_small, "FACILITIES")
    log.info("Mosque & amenities drawn")


def _ceil_to(value: float, step: float) -> float:
    import math
    return math.ceil(value / step) * step


def draw_all(msp, cfg: Config) -> None:
    draw_water(msp, cfg)
    draw_coastal_context(msp, cfg)
    draw_land(msp, cfg)
    draw_port_boundary(msp, cfg)
    draw_coordinate_grid(msp, cfg)
    draw_security_fence(msp, cfg)
    draw_utility_corridor(msp, cfg)
    draw_anchorage(msp, cfg)
    draw_admin_building(msp, cfg)
    draw_fire_station(msp, cfg)
    draw_mosque(msp, cfg)


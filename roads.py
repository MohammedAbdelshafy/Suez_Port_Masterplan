"""
roads.py
========

Internal circulation: primary spine road, secondary distributor roads,
roundabouts, truck circulation and parking areas. Road widths come from
``config.RoadInputs``.
"""

from __future__ import annotations

import logging

from config import Config
from utilities import (add_circle, add_line, add_polyline, add_text, circle_points,
                       rectangle)

log = logging.getLogger("suez.roads")


def _road(msp, a, b, width: float, label: str | None, cfg: Config) -> None:
    """Draw a road as a centreline plus two edge lines (constant width)."""
    add_line(msp, a, b, "CENTERLINES", linetype="CENTER2")
    half = width / 2.0
    # Only orthogonal roads here (axis-aligned), so offset is trivial.
    if abs(a[0] - b[0]) < 1e-6:          # vertical road
        add_line(msp, (a[0] - half, a[1]), (b[0] - half, b[1]), "ROADS")
        add_line(msp, (a[0] + half, a[1]), (b[0] + half, b[1]), "ROADS")
    else:                                 # horizontal road
        add_line(msp, (a[0], a[1] - half), (b[0], b[1] - half), "ROADS")
        add_line(msp, (a[0], a[1] + half), (b[0], b[1] + half), "ROADS")
    if label:
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        add_text(msp, label, mid, cfg.style.text_small, "ROADS")


def draw_primary_roads(msp, cfg: Config) -> None:
    """Primary spine running north-south behind the quay apron."""
    lay = cfg.layout
    x0, y0, x1, y1 = lay.land_bounds
    spine_x = lay.quay_line_x + cfg.roads.quay_apron_setback + 90
    _road(msp, (spine_x, y0 + 120), (spine_x, y1 - 120),
          cfg.roads.primary_width, "PRIMARY ROAD (SPINE)", cfg)

    # East-west primary connecting spine to the gate.
    mid_y = (y0 + y1) / 2
    _road(msp, (spine_x, mid_y), (x1 - 120, mid_y),
          cfg.roads.primary_width, "PRIMARY ROAD", cfg)
    log.info("Primary road network drawn")


def draw_secondary_roads(msp, cfg: Config) -> None:
    """Secondary distributors feeding each inland parcel."""
    lay = cfg.layout
    spine_x = lay.quay_line_x + cfg.roads.quay_apron_setback + 90
    for key in ("LIQUID_BULK", "DRY_BULK", "DRY_DOCK"):
        p = cfg.parcel(key)
        y = p.y + p.h / 2
        _road(msp, (spine_x, y), (p.x, y), cfg.roads.secondary_width, None, cfg)


def draw_roundabouts(msp, cfg: Config) -> None:
    """Roundabouts at the two principal road intersections."""
    lay = cfg.layout
    x0, y0, x1, y1 = lay.land_bounds
    spine_x = lay.quay_line_x + cfg.roads.quay_apron_setback + 90
    mid_y = (y0 + y1) / 2
    r = cfg.roads.roundabout_radius
    for c in [(spine_x, mid_y)]:
        add_circle(msp, c, r, "ROADS")
        add_circle(msp, c, r * 0.45, "ROADS")
        add_text(msp, "R/A", c, cfg.style.text_small, "ROADS")
    log.info("Roundabout(s) drawn")


def draw_parking(msp, cfg: Config) -> None:
    """Truck parking / staging area near the truck gate."""
    lay = cfg.layout
    x0, y0, x1, y1 = lay.land_bounds
    px = x1 - 620
    py = y0 + 200
    pw, ph = 460.0, 300.0
    add_polyline(msp, rectangle(px, py, pw, ph), "ROADS")
    add_text(msp, "TRUCK PARKING / STAGING", (px + pw / 2, py + ph - 40),
             cfg.style.text_small, "ROADS")
    # bay lines
    bays = 8
    for i in range(1, bays):
        x = px + i * pw / bays
        add_line(msp, (x, py), (x, py + ph * 0.7), "ROADS")
    log.info("Parking area drawn")


def draw_all(msp, cfg: Config) -> None:
    draw_primary_roads(msp, cfg)
    draw_secondary_roads(msp, cfg)
    draw_roundabouts(msp, cfg)
    draw_parking(msp, cfg)

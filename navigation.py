"""
navigation.py
=============

Navigation works: approach channel (centreline, limits, dredged area),
turning basin, approach alignment bend, directional arrows and safe-clearance
notes. Geometry follows PIANC concept-design recommendations.
"""

from __future__ import annotations

import logging
import math

from config import PALETTE, Config
from utilities import (add_circle, add_line, add_mtext, add_polyline,
                       add_solid_hatch, add_text, arc_points, polar)

log = logging.getLogger("suez.navigation")


def draw_channel(msp, cfg: Config) -> None:
    """Dredged approach channel: limits, centreline, dredged-area hatch."""
    lay = cfg.layout
    w = cfg.nav.channel_width
    cy = lay.channel_cy
    x_mouth = lay.channel_mouth_x
    x_inner = lay.channel_inner_x

    half = w / 2.0
    limits = [
        (x_mouth, cy - half), (x_inner, cy - half),
        (x_inner, cy + half), (x_mouth, cy + half),
    ]
    add_polyline(msp, limits, "CHANNEL")
    add_solid_hatch(msp, limits, layer="CHANNEL", rgb=PALETTE["channel"],
                    transparency=0.2)

    # Centreline
    add_line(msp, (x_mouth, cy), (x_inner, cy), "CENTERLINES", linetype="CENTER2")

    # Directional arrows (inbound toward the basin -> +X)
    for frac in (0.25, 0.55, 0.85):
        ax = x_mouth + (x_inner - x_mouth) * frac
        _arrow(msp, (ax, cy), 0.0, cfg.style.arrow_size * 2.2)

    add_text(msp, f"APPROACH CHANNEL  L={cfg.nav.channel_length:.0f} m  "
                  f"W={w:.0f} m", ((x_mouth + x_inner) / 2, cy + half + 70),
             cfg.style.text_label, "CHANNEL")
    add_text(msp, f"DREDGED TO -{cfg.dredged_depth:.1f} m CD",
             ((x_mouth + x_inner) / 2, cy - half - 90),
             cfg.style.text_small, "CHANNEL")
    log.info("Channel drawn (mouth x=%.1f -> inner x=%.1f)", x_mouth, x_inner)


def draw_approach_alignment(msp, cfg: Config) -> None:
    """Seaward approach alignment with the design bend radius."""
    lay = cfg.layout
    cy = lay.channel_cy
    x_mouth = lay.channel_mouth_x
    R = cfg.nav.channel_bend_radius
    # Bend turning the centreline 25 deg to the south-west, centred above mouth.
    bend_angle = 25.0
    center = (x_mouth, cy + R)
    arc = arc_points(center, R, -90.0, -90.0 - bend_angle, segments=40)
    add_polyline(msp, arc, "CENTERLINES", close=False)
    add_text(msp, f"APPROACH BEND  R={R:.0f} m",
             (x_mouth - 250, cy + 120), cfg.style.text_small, "CHANNEL")


def draw_turning_basin(msp, cfg: Config) -> None:
    """Turning basin circle, centreline cross and dimension note."""
    lay = cfg.layout
    c = lay.basin_center
    r = lay.basin_radius
    add_circle(msp, c, r, "TURNING_BASIN")
    add_solid_hatch(msp, _circle_poly(c, r), layer="TURNING_BASIN",
                    rgb=PALETTE["channel"], transparency=0.2)
    # centre cross
    add_line(msp, (c[0] - r, c[1]), (c[0] + r, c[1]), "CENTERLINES",
             linetype="CENTER2")
    add_line(msp, (c[0], c[1] - r), (c[0], c[1] + r), "CENTERLINES",
             linetype="CENTER2")
    add_mtext(msp, f"TURNING BASIN\nØ {cfg.nav.turning_basin_diameter:.0f} m",
              (c[0], c[1]), cfg.style.text_label, "TURNING_BASIN")
    log.info("Turning basin drawn at %s R=%.1f", c, r)


def draw_safe_clearance(msp, cfg: Config) -> None:
    """Annotate the navigational safe clearance around the basin."""
    lay = cfg.layout
    c = lay.basin_center
    r = lay.basin_radius
    clearance = 30.0
    add_polyline(msp, _circle_poly(c, r + clearance), "CENTERLINES",
                 close=True)
    add_text(msp, f"SAFE CLEARANCE +{clearance:.0f} m",
             (c[0], c[1] - r - clearance - 40), cfg.style.text_small,
             "TURNING_BASIN")


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def _arrow(msp, tip, angle_deg: float, size: float) -> None:
    """Filled-look direction arrow (open chevron) on CENTERLINES."""
    back = polar(tip, angle_deg + 180.0, size)
    left = polar(tip, angle_deg + 150.0, size)
    right = polar(tip, angle_deg - 150.0, size)
    add_line(msp, tip, left, "CENTERLINES")
    add_line(msp, tip, right, "CENTERLINES")
    add_line(msp, back, tip, "CENTERLINES")


def _circle_poly(center, radius, segments: int = 72):
    cx, cy = center
    return [(cx + radius * math.cos(2 * math.pi * i / segments),
             cy + radius * math.sin(2 * math.pi * i / segments))
            for i in range(segments)]


def draw_pilot_station(msp, cfg: Config) -> None:
    """Pilot boarding station marker at the seaward end of the approach channel."""
    lay = cfg.layout
    cy = lay.channel_cy
    x_mouth = lay.channel_mouth_x
    # Place the pilot station 400 m seaward of the channel mouth.
    px = x_mouth - 400
    py = cy
    r = 35.0
    add_circle(msp, (px, py), r, "CHANNEL")
    # Cross marker
    add_line(msp, (px - r * 0.7, py), (px + r * 0.7, py), "CHANNEL")
    add_line(msp, (px, py - r * 0.7), (px, py + r * 0.7), "CHANNEL")
    add_text(msp, "PILOT BOARDING", (px, py + r + 40),
             cfg.style.text_small, "CHANNEL")
    add_text(msp, "STATION", (px, py + r + 10),
             cfg.style.text_small, "CHANNEL")
    log.info("Pilot boarding station drawn")


def draw_tug_basin(msp, cfg: Config) -> None:
    """Small tug / service craft basin on the quay side of the turning basin."""
    lay = cfg.layout
    c = lay.basin_center
    r = lay.basin_radius
    # Place tug basin east of the turning basin, against the quay wall.
    tx = lay.quay_line_x - 20
    ty = c[1] - r + 40
    tw, th = 180.0, 200.0
    pts = [(tx, ty), (tx + tw, ty), (tx + tw, ty + th), (tx, ty + th)]
    add_polyline(msp, pts, "TURNING_BASIN")
    add_solid_hatch(msp, pts, layer="TURNING_BASIN", rgb=PALETTE["channel"],
                    transparency=0.25)
    add_mtext(msp, "TUG BASIN\\PSERVICE CRAFT",
              (tx + tw / 2, ty + th / 2), cfg.style.text_small, "TURNING_BASIN")
    log.info("Tug basin drawn")


def draw_all(msp, cfg: Config) -> None:
    draw_channel(msp, cfg)
    draw_approach_alignment(msp, cfg)
    draw_turning_basin(msp, cfg)
    draw_safe_clearance(msp, cfg)
    draw_pilot_station(msp, cfg)
    draw_tug_basin(msp, cfg)


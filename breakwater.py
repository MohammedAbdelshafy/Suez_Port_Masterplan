"""
breakwater.py
=============

North and South rubble-mound breakwaters flanking the channel mouth, plus a
detailed trunk cross-section (core / filter / armour / toe) with Hudson-formula
annotations.

References: CEM (USACE), BS 6349-7, Hudson stability formula.
"""

from __future__ import annotations

import logging

from config import PALETTE, Config, hudson_armour_mass
from utilities import (add_circle, add_line, add_mtext, add_pattern_hatch,
                       add_polyline, add_solid_hatch, add_text,
                       trapezoid_section)

log = logging.getLogger("suez.breakwater")


def _mole(msp, x_root, y_inner, width, length, splay, color=32):
    """
    A single long rubble-mound mole projecting seaward (toward -X) with a slight
    seaward splay and a roundhead at the tip. `y_inner` is the channel-side edge;
    the mound grows away from the channel by `width` (+`splay` at the head).
    """
    x_tip = x_root - length
    poly = [
        (x_root, y_inner),
        (x_root, y_inner + width),
        (x_tip, y_inner + width + splay),
        (x_tip, y_inner - splay),
    ]
    add_polyline(msp, poly, "BREAKWATER")
    # Rock-armour stone pattern over a light grey stone tint.
    add_solid_hatch(msp, poly, layer="BREAKWATER", rgb=PALETTE["armour"],
                    transparency=0.45)
    add_pattern_hatch(msp, poly, layer="BREAKWATER", pattern="GRAVEL",
                      scale=55.0, color=7, transparency=0.2)
    # Roundhead (heavier armour) at the seaward tip.
    head_c = (x_tip, y_inner + width / 2.0)
    add_circle(msp, head_c, width * 0.75, "BREAKWATER")
    return x_tip, head_c


def draw_breakwaters_plan(msp, cfg: Config) -> None:
    """
    Two long, roughly parallel rubble-mound moles flanking the entrance channel
    and projecting seaward, after the real Suez Canal port entrance (twin
    breakwaters, the northern/western one longer). Leaves a navigable gap.
    """
    lay = cfg.layout
    cy = lay.channel_cy
    x_mouth = lay.channel_mouth_x
    gap = cfg.nav.channel_width + 90.0          # entrance gap > channel width
    width = 75.0                                # mound footprint in plan [m]
    x_root = x_mouth + 180.0                    # moles root just inside the mouth
    north_len = cfg.bw.north_length             # longer (cf. west mole, Port Said)
    south_len = cfg.bw.south_length

    # North mole (longer).
    n_inner = cy + gap / 2.0
    n_tip, n_head = _mole(msp, x_root, n_inner, width, north_len, splay=45.0)
    add_text(msp, f"NORTH BREAKWATER  L={north_len:.0f} m",
             (x_root - north_len / 2, n_inner + width + 120),
             cfg.style.text_label, "BREAKWATER")
    add_text(msp, "ROUNDHEAD", (n_head[0], n_head[1] + width + 40),
             cfg.style.text_small, "BREAKWATER")

    # South mole (shorter).
    s_inner = cy - gap / 2.0
    s_tip, s_head = _mole(msp, x_root, s_inner - width, width, south_len, splay=45.0)
    add_text(msp, f"SOUTH BREAKWATER  L={south_len:.0f} m",
             (x_root - south_len / 2, s_inner - width - 120),
             cfg.style.text_label, "BREAKWATER")

    add_text(msp, f"ENTRANCE GAP {gap:.0f} m", (x_root + 60, cy),
             cfg.style.text_small, "BREAKWATER", align="MIDDLE_LEFT")

    # Navigation lights on roundheads (IALA Region A: green=starboard/N, red=port/S).
    _nav_light(msp, n_head, "FL.G 5s", 3, cfg)   # green starboard
    _nav_light(msp, s_head, "FL.R 5s", 1, cfg)   # red port
    log.info("Breakwater moles drawn (N=%.0f m, S=%.0f m, gap=%.0f m)",
             north_len, south_len, gap)


def _nav_light(msp, center, label: str, color: int, cfg: Config) -> None:
    """Draw a navigation light marker (filled circle + characteristic label)."""
    r = 18.0
    add_circle(msp, center, r, "BREAKWATER")
    add_circle(msp, center, r * 0.4, "BREAKWATER")
    add_text(msp, label, (center[0], center[1] - r - 30),
             cfg.style.text_small, "BREAKWATER")


def draw_breakwater_section(msp, cfg: Config) -> None:
    """
    Detailed trunk cross-section, drawn enlarged (N.T.S.) in the open water area
    of the harbour so it stays inside the plan extents / printable sheet.
    Shows core, filter (under-layer), armour and toe protection.
    """
    bw = cfg.bw
    sf = 9.0                       # exaggeration factor so the detail is legible
    # Detail origin: empty open-water area lower-left of the harbour.
    wx0 = cfg.layout.water_bounds[0]
    ox, oy = wx0 + 80.0, 320.0
    sea_level = 0.0

    # Scaled dimensions (slopes are ratios, so they are NOT scaled).
    height = (bw.crest_level - bw.seabed_level) * sf
    crest_w = bw.crest_width * sf
    f = bw.filter_thickness * sf
    a = (bw.armour_thickness + bw.filter_thickness) * sf
    toe_w = bw.toe_width * sf
    toe_h = bw.toe_height * sf
    base_width = crest_w + (bw.seaward_slope + bw.leeward_slope) * height

    # Layers are drawn outermost-first so inner layers read on top.
    # --- Armour layer (outermost) — coarse stone pattern -------------------
    arm = trapezoid_section((ox - a * bw.seaward_slope, oy),
                            base_width + 2 * a * bw.seaward_slope,
                            crest_w + 2 * a, height + a,
                            bw.seaward_slope, bw.leeward_slope)
    add_polyline(msp, arm, "BREAKWATER")
    add_pattern_hatch(msp, arm, layer="HATCH", pattern="GRAVEL", scale=7.0,
                      color=7)
    add_text(msp, "ARMOUR", (ox + base_width / 2, oy + height + a - 20 * sf),
             cfg.style.text_small, "BREAKWATER")

    # --- Filter / under-layer — cross hatch --------------------------------
    filt = trapezoid_section((ox - f * bw.seaward_slope, oy),
                             base_width + 2 * f * bw.seaward_slope,
                             crest_w + 2 * f, height + f,
                             bw.seaward_slope, bw.leeward_slope)
    add_polyline(msp, filt, "BREAKWATER")
    add_pattern_hatch(msp, filt, layer="HATCH", pattern="ANSI37", scale=5.0,
                      color=7)
    add_text(msp, "FILTER", (ox - f - 30, oy + height * 0.78),
             cfg.style.text_small, "BREAKWATER", align="MIDDLE_RIGHT")

    # --- Core (innermost) — diagonal hatch ---------------------------------
    core = trapezoid_section((ox, oy), base_width, crest_w, height,
                             bw.seaward_slope, bw.leeward_slope)
    add_polyline(msp, core, "BREAKWATER")
    add_pattern_hatch(msp, core, layer="HATCH", pattern="ANSI31", scale=6.0,
                      color=7)
    add_text(msp, "CORE", (ox + base_width / 2, oy + height * 0.35),
             cfg.style.text_small, "BREAKWATER")

    # --- Toe protection (both toes) ----------------------------------------
    for sign, x_toe in ((-1, ox - a * bw.seaward_slope),
                        (+1, ox + base_width + a * bw.leeward_slope)):
        toe = [
            (x_toe, oy), (x_toe + sign * toe_w, oy),
            (x_toe + sign * toe_w, oy + toe_h), (x_toe, oy + toe_h),
        ]
        add_polyline(msp, toe, "BREAKWATER")
    add_text(msp, "TOE", (ox - a * bw.seaward_slope - 20, oy + toe_h),
             cfg.style.text_small, "BREAKWATER", align="MIDDLE_RIGHT")

    # --- water line & levels -----------------------------------------------
    wl_y = oy + (sea_level - bw.seabed_level) * sf
    add_line(msp, (ox - 0.6 * base_width, wl_y),
             (ox + base_width + 0.2 * base_width, wl_y), "WATER",
             linetype="DASHED2")
    add_text(msp, "SWL +0.0 m CD", (ox + base_width + 0.22 * base_width, wl_y),
             cfg.style.text_small, "WATER", align="MIDDLE_LEFT")
    add_text(msp, f"CREST +{bw.crest_level:.1f} m CD",
             (ox + base_width / 2, oy + height + a + 25),
             cfg.style.text_small, "BREAKWATER")

    # --- Hudson formula annotation (to the right of the section) -----------
    w50 = hudson_armour_mass(bw)
    note = (
        "HUDSON ARMOUR DESIGN\n"
        f"Hs={bw.design_wave_h:.1f} m  Kd={bw.kd_stability:.1f}\n"
        f"rho_s={bw.rock_density:.0f}  rho_w={bw.water_density:.0f} kg/m3\n"
        f"cot(a)={bw.armour_slope_cot:.1f}  slope {bw.seaward_slope:.0f}H:1V\n"
        f"=> W50={w50:.1f} t   armour t={bw.armour_thickness:.1f} m\n"
        f"crest width={bw.crest_width:.1f} m"
    )
    add_mtext(msp, note, (ox + base_width + 0.25 * base_width, oy + height),
              cfg.style.text_small, "TEXT", width=base_width * 0.9, attach=1)
    add_text(msp, "DETAIL A - BREAKWATER TRUNK CROSS-SECTION (N.T.S.)",
             (ox + base_width / 2, oy - 70), cfg.style.text_label, "TEXT")
    log.info("Breakwater section drawn (x%.0f, Hudson W50=%.1f t)", sf, w50)


def draw_all(msp, cfg: Config) -> None:
    draw_breakwaters_plan(msp, cfg)
    draw_breakwater_section(msp, cfg)

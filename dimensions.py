"""
dimensions.py
=============

Automatic dimensioning of the principal port elements using the ``PORT``
dimension style. Linear dimensions for channel width, quay/berth lengths and
overall site; a radial/diameter dimension for the turning basin and tanks.
"""

from __future__ import annotations

import logging

from config import Config
from layers import DIMSTYLE_NAME

log = logging.getLogger("suez.dimensions")


def _linear(msp, p1, p2, base, cfg: Config, angle: float = 0.0) -> None:
    dim = msp.add_linear_dim(
        base=base, p1=p1, p2=p2, angle=angle,
        dimstyle=DIMSTYLE_NAME, dxfattribs={"layer": "DIMENSIONS"},
    )
    dim.render()


def _diameter(msp, center, radius, cfg: Config) -> None:
    dim = msp.add_diameter_dim(
        center=center, radius=radius, angle=45,
        dimstyle=DIMSTYLE_NAME, dxfattribs={"layer": "DIMENSIONS"},
    )
    dim.render()


def draw_dimensions(msp, cfg: Config) -> None:
    lay = cfg.layout

    # --- channel width (vertical dim across the channel) -------------------
    cy = lay.channel_cy
    w = cfg.nav.channel_width
    xm = lay.channel_mouth_x + 200
    _linear(msp, (xm, cy - w / 2), (xm, cy + w / 2),
            base=(xm - 160, cy), cfg=cfg, angle=90.0)

    # --- channel length (horizontal) ---------------------------------------
    _linear(msp, (lay.channel_mouth_x, cy - w / 2 - 200),
            (lay.channel_inner_x, cy - w / 2 - 200),
            base=(0, cy - w / 2 - 260), cfg=cfg, angle=0.0)

    # --- turning basin diameter --------------------------------------------
    _diameter(msp, lay.basin_center, lay.basin_radius, cfg)

    # --- overall site width & height ---------------------------------------
    x0, y0, x1, y1 = lay.land_bounds
    _linear(msp, (x0, y1 + 180), (x1, y1 + 180),
            base=(0, y1 + 260), cfg=cfg, angle=0.0)
    _linear(msp, (x1 + 180, y0), (x1 + 180, y1),
            base=(x1 + 260, 0), cfg=cfg, angle=90.0)

    # --- container quay length ---------------------------------------------
    cp = cfg.parcel("CONTAINER")
    _linear(msp, (cp.x - 120, cp.y), (cp.x - 120, cp.y + cp.h),
            base=(cp.x - 220, 0), cfg=cfg, angle=90.0)

    # --- a representative tank diameter ------------------------------------
    tp = cfg.parcel("LIQUID_BULK")
    t = cfg.tanks
    spacing = t.diameter * t.spacing_factor
    group_w = (t.count - 1) * spacing
    start_x = tp.x + tp.w / 2 - group_w / 2
    cyt = tp.y + tp.h * 0.45
    _diameter(msp, (start_x, cyt), t.diameter / 2.0, cfg)

    log.info("Dimensions rendered for principal elements")


def draw_all(msp, cfg: Config) -> None:
    draw_dimensions(msp, cfg)

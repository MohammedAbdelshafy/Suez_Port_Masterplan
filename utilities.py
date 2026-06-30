"""
utilities.py
============

Reusable, side-effect-free geometry and drafting helpers shared by every
geometry module. Keeping these here avoids duplicated maths and keeps the
higher-level modules declarative.
"""

from __future__ import annotations

import logging
import math
from typing import Iterable

Point = tuple[float, float]


# ----------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------
def setup_logger(level: int = logging.INFO) -> logging.Logger:
    """Configure the root project logger once and return it."""
    logger = logging.getLogger("suez")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
                              datefmt="%H:%M:%S")
        )
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


# ----------------------------------------------------------------------------
# Point / vector maths
# ----------------------------------------------------------------------------
def dist(a: Point, b: Point) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def midpoint(a: Point, b: Point) -> Point:
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)


def add(a: Point, b: Point) -> Point:
    return (a[0] + b[0], a[1] + b[1])


def polar(origin: Point, angle_deg: float, radius: float) -> Point:
    """Point at `radius` and `angle_deg` (CCW from +X) from `origin`."""
    a = math.radians(angle_deg)
    return (origin[0] + radius * math.cos(a), origin[1] + radius * math.sin(a))


# ----------------------------------------------------------------------------
# Primitive coordinate generators
# ----------------------------------------------------------------------------
def rectangle(x: float, y: float, w: float, h: float) -> list[Point]:
    """Closed rectangle corner list (lower-left origin)."""
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def circle_points(center: Point, radius: float, segments: int = 72) -> list[Point]:
    cx, cy = center
    return [
        (cx + radius * math.cos(2 * math.pi * i / segments),
         cy + radius * math.sin(2 * math.pi * i / segments))
        for i in range(segments)
    ]


def arc_points(center: Point, radius: float, start_deg: float,
               end_deg: float, segments: int = 48) -> list[Point]:
    cx, cy = center
    pts: list[Point] = []
    for i in range(segments + 1):
        a = math.radians(start_deg + (end_deg - start_deg) * i / segments)
        pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return pts


def trapezoid_section(base_left: Point, base_width: float, top_width: float,
                      height: float, slope_left: float, slope_right: float
                      ) -> list[Point]:
    """
    Symmetric-ish trapezoid for a rubble-mound cross section.

    `base_left` is the lower-left toe. `slope_*` are horizontal run per unit
    rise (cot of the slope angle). Returns a closed point list.
    """
    x0, y0 = base_left
    top_y = y0 + height
    top_left_x = x0 + slope_left * height
    top_right_x = top_left_x + top_width
    base_right_x = x0 + base_width
    return [
        (x0, y0),
        (base_right_x, y0),
        (top_right_x, top_y),
        (top_left_x, top_y),
    ]


# ----------------------------------------------------------------------------
# Drawing helpers (thin wrappers that always set the layer)
# ----------------------------------------------------------------------------
def add_polyline(msp, points: Iterable[Point], layer: str, close: bool = True):
    return msp.add_lwpolyline(list(points), close=close,
                              dxfattribs={"layer": layer})


def add_circle(msp, center: Point, radius: float, layer: str):
    return msp.add_circle(center, radius, dxfattribs={"layer": layer})


def add_line(msp, a: Point, b: Point, layer: str, linetype: str | None = None):
    attribs = {"layer": layer}
    if linetype:
        attribs["linetype"] = linetype
    return msp.add_line(a, b, dxfattribs=attribs)


def add_text(msp, text: str, at: Point, height: float, layer: str = "TEXT",
             align: str = "MIDDLE_CENTER", rotation: float = 0.0):
    """Place MTEXT-like single line text, anchored by alignment string."""
    entity = msp.add_text(
        text,
        dxfattribs={"layer": layer, "height": height,
                    "rotation": rotation, "style": "PORT_TXT"},
    )
    entity.set_placement(at, align=_align_enum(align))
    return entity


def add_mtext(msp, text: str, at: Point, height: float, layer: str = "TEXT",
              width: float = 0.0, attach: int = 5):
    """
    Multi-line text (MTEXT) so embedded newlines line-break correctly in
    AutoCAD (single-line TEXT entities do not). `attach` is the MTEXT
    attachment point (5 = middle-center, 7 = bottom-left, 1 = top-left).
    """
    mt = msp.add_mtext(
        text.replace("\n", r"\P"),
        dxfattribs={"layer": layer, "char_height": height,
                    "style": "PORT_TXT", "attachment_point": attach},
    )
    if width:
        mt.dxf.width = width
    mt.set_location(at)
    return mt


def add_solid_hatch(msp, points: list[Point], layer: str = "HATCH",
                    color: int | None = None, transparency: float = 0.5,
                    rgb: tuple[int, int, int] | None = None):
    """Solid fill the closed boundary defined by `points`.

    Pass `rgb` for a predictable true-colour fill (preferred for area tints);
    `color` sets an ACI index instead.
    """
    hatch = msp.add_hatch(dxfattribs={"layer": layer})
    if rgb is not None:
        hatch.rgb = rgb
    elif color is not None:
        hatch.dxf.color = color
    hatch.set_solid_fill()
    hatch.paths.add_polyline_path(points, is_closed=True)
    try:
        hatch.set_transparency(transparency)
    except Exception:  # pragma: no cover
        pass
    return hatch


# Standard ACAD hatch patterns (loaded once). Keyed by name, e.g. "ANSI31".
try:
    from ezdxf.tools.pattern import load as _load_patterns
    _PATTERNS = _load_patterns()
except Exception:  # pragma: no cover
    _PATTERNS = {}


def add_pattern_hatch(msp, points: list[Point], layer: str = "HATCH",
                      pattern: str = "ANSI31", scale: float = 40.0,
                      angle: float = 0.0, color: int | None = None,
                      transparency: float = 0.0,
                      rgb: tuple[int, int, int] | None = None):
    """
    Pattern-fill a closed boundary with a standard ACAD hatch pattern
    (e.g. ANSI31 diagonal, ANSI37 cross, AR-SAND stipple, GRAVEL stone).

    Falls back to a solid fill if the pattern definition is unavailable so the
    drawing never ends up with an empty region.
    """
    hatch = msp.add_hatch(dxfattribs={"layer": layer})
    if rgb is not None:
        hatch.rgb = rgb
    elif color is not None:
        hatch.dxf.color = color
    definition = _PATTERNS.get(pattern)
    if definition:
        hatch.set_pattern_fill(pattern, scale=scale, angle=angle,
                               definition=definition)
    else:  # pragma: no cover - safety net
        hatch.set_solid_fill()
    hatch.paths.add_polyline_path(points, is_closed=True)
    try:
        hatch.set_transparency(transparency)
    except Exception:  # pragma: no cover
        pass
    return hatch


def _align_enum(align: str):
    """Map a friendly alignment name to ezdxf TextEntityAlignment."""
    from ezdxf.enums import TextEntityAlignment
    return getattr(TextEntityAlignment, align, TextEntityAlignment.MIDDLE_CENTER)


# ----------------------------------------------------------------------------
# Misc
# ----------------------------------------------------------------------------
def polygon_area(points: list[Point]) -> float:
    """Shoelace area (absolute value) of a closed polygon [m²]."""
    n = len(points)
    s = 0.0
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0

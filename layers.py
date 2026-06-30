"""
layers.py
=========

Professional CAD layer table and standard styling (DimStyle / TextStyle).

Each layer carries an ACI colour, lineweight (1/100 mm as ezdxf expects),
linetype and transparency, following ISO / civil drafting conventions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import ezdxf
from ezdxf.document import Drawing
from ezdxf.lldxf import const

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class LayerDef:
    name: str
    color: int          # ACI colour index
    lineweight: int     # 1/100 mm (e.g. 35 = 0.35 mm); -1 = default
    linetype: str = "CONTINUOUS"
    transparency: float = 0.0   # 0..1
    description: str = ""


# ACI quick reference: 1 red, 2 yellow, 3 green, 4 cyan, 5 blue, 6 magenta,
# 7 white/black, 8 dark grey, 9 light grey.
LAYERS: list[LayerDef] = [
    LayerDef("BOUNDARY",     7,  50, "CONTINUOUS", 0.0, "Port / site boundary"),
    LayerDef("LAND",         42, 18, "CONTINUOUS", 0.0, "Reclaimed land area"),
    LayerDef("WATER",        140, 18, "CONTINUOUS", 0.55, "Harbour & sea water"),
    LayerDef("BREAKWATER",   32, 50, "CONTINUOUS", 0.0, "Rubble-mound breakwaters"),
    LayerDef("CHANNEL",      150, 25, "CONTINUOUS", 0.30, "Navigation channel"),
    LayerDef("TURNING_BASIN", 151, 25, "CONTINUOUS", 0.30, "Turning basin"),
    LayerDef("BERTHS",       30, 35, "CONTINUOUS", 0.0, "Berth faces"),
    LayerDef("QUAYS",        33, 50, "CONTINUOUS", 0.0, "Quay walls / aprons"),
    LayerDef("TERMINALS",    8,  25, "CONTINUOUS", 0.0, "Terminal parcels"),
    LayerDef("ROADS",        9,  20, "CONTINUOUS", 0.0, "Internal road network"),
    LayerDef("TANKS",        20, 35, "CONTINUOUS", 0.0, "Liquid bulk tanks"),
    LayerDef("SILOS",        40, 35, "CONTINUOUS", 0.0, "Dry bulk silos"),
    LayerDef("FACILITIES",   50, 25, "CONTINUOUS", 0.0, "Buildings & port facilities"),
    LayerDef("DIMENSIONS",   1,  18, "CONTINUOUS", 0.0, "Dimension lines"),
    LayerDef("CENTERLINES",  4,  13, "CENTER2",    0.0, "Centrelines"),
    LayerDef("TEXT",         7,  18, "CONTINUOUS", 0.0, "General annotation text"),
    LayerDef("HATCH",        250, 13, "CONTINUOUS", 0.65, "Fill hatching"),
    LayerDef("GRID",         8,  9,  "DASHED2",    0.80, "Coordinate grid"),
    LayerDef("LEGEND",       7,  18, "CONTINUOUS", 0.0, "Legend block"),
    LayerDef("TITLEBLOCK",   7,  50, "CONTINUOUS", 0.0, "Title block & border"),
]

DIMSTYLE_NAME = "PORT"
TEXTSTYLE_NAME = "PORT_TXT"


def setup_linetypes(doc: Drawing) -> None:
    """Ensure the linetypes referenced by the layer table exist."""
    needed = {
        "CENTER2": [40.0, [20.0, -5.0, 2.5, -5.0]],
        "DASHED2": [15.0, [10.0, -5.0]],
    }
    for name, (pattern_len, pattern) in needed.items():
        if name not in doc.linetypes:
            # Build a simple dash pattern description string.
            doc.linetypes.add(
                name=name,
                pattern=[pattern_len, *pattern],
                description=name,
            )


def setup_layers(doc: Drawing) -> None:
    """Create every layer with colour, lineweight, linetype and transparency."""
    setup_linetypes(doc)
    for ld in LAYERS:
        if ld.name in doc.layers:
            layer = doc.layers.get(ld.name)
        else:
            layer = doc.layers.add(ld.name)
        layer.color = ld.color
        layer.dxf.lineweight = ld.lineweight
        try:
            layer.dxf.linetype = ld.linetype
        except Exception:  # pragma: no cover - linetype fallback
            layer.dxf.linetype = "CONTINUOUS"
        layer.transparency = ld.transparency
        layer.description = ld.description
    log.info("Created %d CAD layers", len(LAYERS))


def setup_text_style(doc: Drawing) -> None:
    if TEXTSTYLE_NAME not in doc.styles:
        doc.styles.add(TEXTSTYLE_NAME, font="isocp.shx")


def setup_dimstyle(doc: Drawing) -> None:
    """A professional dimension style scaled for a 1:1 metre drawing."""
    if DIMSTYLE_NAME in doc.dimstyles:
        return
    dim = doc.dimstyles.add(DIMSTYLE_NAME)
    dim.dxf.dimtxt = 40        # text height [drawing units = m]
    dim.dxf.dimasz = 30        # arrow size
    dim.dxf.dimexe = 12        # extension beyond dim line
    dim.dxf.dimexo = 12        # extension line offset from origin
    dim.dxf.dimgap = 8         # gap around text
    dim.dxf.dimdec = 1         # decimal places
    dim.dxf.dimlunit = 2       # decimal units
    dim.dxf.dimscale = 1.0
    try:
        dim.dxf.dimtxsty = TEXTSTYLE_NAME
    except Exception:  # pragma: no cover
        pass


def setup_document() -> Drawing:
    """Create a fresh R2018 drawing with all standards applied."""
    doc = ezdxf.new("R2018", setup=True)
    doc.units = ezdxf.units.M  # model space in metres
    setup_text_style(doc)
    setup_layers(doc)
    setup_dimstyle(doc)
    return doc


def layer_report_lines() -> list[str]:
    """Human-readable layer report (consumed by export.py)."""
    lines = ["SUEZ PORT MASTERPLAN -- LAYER REPORT", "=" * 60,
             f"{'LAYER':<16}{'COLOR':>6}{'LW(1/100mm)':>14}"
             f"{'LINETYPE':>12}{'TRANSP':>9}  DESCRIPTION"]
    for ld in LAYERS:
        lines.append(
            f"{ld.name:<16}{ld.color:>6}{ld.lineweight:>14}"
            f"{ld.linetype:>12}{int(ld.transparency*100):>8}%  {ld.description}"
        )
    lines.append("=" * 60)
    lines.append(f"Total layers: {len(LAYERS)}")
    return lines

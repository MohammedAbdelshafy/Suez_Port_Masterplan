"""
generate_port.py
=================

Entry point. Builds the entire Suez Port Masterplan parametrically and writes
all deliverables.

Usage
-----
    pip install -r requirements.txt
    python generate_port.py

Outputs (in ./output):
    Suez_Port_Masterplan.dxf / .svg / .pdf / .png
    Bill_of_Quantities.csv, Coordinates.csv
    Engineering_Report.md, Layer_Report.txt
"""

from __future__ import annotations

import logging
import sys

import annotations as ann
import breakwater
import dimensions
import export
import geometry
import navigation
import roads
import terminals
import validation
from config import CFG
from layers import setup_document
from utilities import setup_logger


def build(cfg=CFG):
    """Assemble the full model and return (doc, msp, checks, rendered)."""
    log = setup_logger()
    log.info("=== SUEZ PORT MASTERPLAN -- parametric generation ===")
    log.info("Design vessel LOA=%.0f B=%.0f T=%.0f m",
             cfg.vessel.loa, cfg.vessel.beam, cfg.vessel.draft)

    doc = setup_document()
    msp = doc.modelspace()

    # Draw order: water/land base -> navigation -> breakwaters -> terminals
    # -> roads -> dimensions -> annotations (furniture on top).
    geometry.draw_all(msp, cfg)
    navigation.draw_all(msp, cfg)
    breakwater.draw_all(msp, cfg)
    terminals.draw_all(msp, cfg)
    roads.draw_all(msp, cfg)
    dimensions.draw_all(msp, cfg)
    ann.draw_all(msp, doc, cfg)

    checks = validation.run_all(doc, msp, cfg)

    # Zoom extents so viewers open framed on the drawing.
    try:
        from ezdxf import zoom
        zoom.extents(msp)
    except Exception as exc:  # pragma: no cover
        log.warning("zoom.extents failed: %s", exc)

    rendered = export.export_all(doc, cfg, checks)
    log.info("=== DONE -- outputs in %s ===", cfg.paths.out_dir)
    return doc, msp, checks, rendered


def main() -> int:
    try:
        build()
    except Exception as exc:
        logging.getLogger("suez").exception("Generation failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

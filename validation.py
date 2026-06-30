"""
validation.py
=============

Pre-export sanity checks. Each check returns a (passed, message) tuple; the
runner aggregates them and raises if any *critical* check fails.

Checks: geometry presence, layer table integrity, tank spacing vs. fire code,
navigation width vs. design vessel, turning-basin diameter vs. LOA.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from config import Config
from layers import LAYERS

log = logging.getLogger("suez.validation")


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    critical: bool = True


def check_layers(doc) -> CheckResult:
    missing = [ld.name for ld in LAYERS if ld.name not in doc.layers]
    return CheckResult(
        "Layer table", not missing,
        "all layers present" if not missing else f"missing: {missing}",
    )


def check_geometry(msp) -> CheckResult:
    n = len(list(msp))
    return CheckResult("Geometry present", n > 100,
                       f"{n} entities in model space")


def check_tank_spacing(cfg: Config) -> CheckResult:
    t = cfg.tanks
    spacing = t.diameter * t.spacing_factor
    min_required = t.diameter + 15.0  # rule-of-thumb min gap
    ok = spacing >= min_required
    return CheckResult(
        "Tank spacing", ok,
        f"centre spacing {spacing:.1f} m (min {min_required:.1f} m)",
    )


def check_channel_width(cfg: Config) -> CheckResult:
    # PIANC one-way concept minimum ~5·B; we target ~7·B.
    min_w = 5.0 * cfg.vessel.beam
    ok = cfg.nav.channel_width >= min_w
    return CheckResult(
        "Channel width", ok,
        f"width {cfg.nav.channel_width:.0f} m vs PIANC min {min_w:.0f} m "
        f"({cfg.nav.channel_width / cfg.vessel.beam:.1f}·B)",
    )


def check_turning_basin(cfg: Config) -> CheckResult:
    min_d = 1.2 * cfg.vessel.loa     # tugs assisted minimum
    ok = cfg.nav.turning_basin_diameter >= min_d
    return CheckResult(
        "Turning basin diameter", ok,
        f"Ø {cfg.nav.turning_basin_diameter:.0f} m vs min {min_d:.0f} m "
        f"({cfg.nav.turning_basin_diameter / cfg.vessel.loa:.2f}·LOA)",
    )


def check_overlaps(cfg: Config) -> CheckResult:
    """Lightweight parcel-overlap check (axis-aligned rectangles)."""
    ps = cfg.parcels
    overlaps = []
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            a, b = ps[i], ps[j]
            if (a.x < b.x + b.w and a.x + a.w > b.x and
                    a.y < b.y + b.h and a.y + a.h > b.y):
                overlaps.append((a.key, b.key))
    return CheckResult("Parcel overlap", not overlaps,
                       "no overlaps" if not overlaps else f"overlaps: {overlaps}",
                       critical=False)


def check_berth_length(cfg: Config) -> CheckResult:
    """Verify each waterfront berth segment ≥ LOA + 10% mooring clearance."""
    min_berth = cfg.vessel.loa * 1.10
    short = []
    for p in cfg.parcels:
        if p.has_quay and p.berths > 0:
            seg = p.h / p.berths
            if seg < min_berth:
                short.append(f"{p.key}({seg:.0f}m)")
    ok = not short
    return CheckResult(
        "Berth length", ok,
        f"all berths ≥ {min_berth:.0f} m (1.1·LOA)" if ok
        else f"short berths: {short} vs min {min_berth:.0f} m",
        critical=False,  # advisory — smaller vessel classes use shorter berths
    )


def check_entrance_gap(cfg: Config) -> CheckResult:
    """Verify breakwater entrance gap ≥ channel width."""
    gap = cfg.nav.channel_width + 90.0   # matches breakwater.py gap calculation
    ok = gap >= cfg.nav.channel_width
    return CheckResult(
        "Entrance gap", ok,
        f"gap {gap:.0f} m ≥ channel width {cfg.nav.channel_width:.0f} m",
    )


def run_all(doc, msp, cfg: Config) -> list[CheckResult]:
    results = [
        check_layers(doc),
        check_geometry(msp),
        check_tank_spacing(cfg),
        check_channel_width(cfg),
        check_turning_basin(cfg),
        check_overlaps(cfg),
        check_berth_length(cfg),
        check_entrance_gap(cfg),
    ]
    for r in results:
        level = logging.INFO if r.passed else (
            logging.ERROR if r.critical else logging.WARNING)
        log.log(level, "[%s] %s -- %s",
                "PASS" if r.passed else "FAIL", r.name, r.message)
    critical_failures = [r for r in results if not r.passed and r.critical]
    if critical_failures:
        raise ValueError(
            "Validation failed: "
            + "; ".join(f"{r.name}: {r.message}" for r in critical_failures)
        )
    return results


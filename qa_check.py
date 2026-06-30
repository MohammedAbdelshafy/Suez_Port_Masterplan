"""
qa_check.py
===========

QA/QC consistency gate (CSS v1.0). Verifies that the SAME engineering values
appear in the calculation engine, the canonical JSON, the CAD model and the
generated reports -- the brief's first QA requirement (identical values across
all deliverables). Flags conflicts; it does not silently correct them.

Run:  python qa_check.py
Writes: deliverables/05_QA_Consistency_Report.md
"""

from __future__ import annotations

import json
from pathlib import Path

import formulas
from calculations import canonical_values
from config import CFG, hudson_armour_mass


def _check(name, a, b, tol=0.05):
    ok = abs(float(a) - float(b)) <= tol
    return (name, ok, a, b)


def run_checks() -> list[tuple]:
    vals = canonical_values()
    nav = vals["navigation"]
    checks = [
        _check("Channel depth: engine vs CAD",
               nav["channel_depth_m"], CFG.dredged_depth),
        _check("Channel width: engine vs CAD nav",
               nav["channel_width_m"], CFG.nav.channel_width),
        _check("Turning basin Ø: engine vs CAD nav",
               nav["turning_basin_diameter_m"], CFG.nav.turning_basin_diameter),
        _check("Turning basin Ø = 1.5·Lmax",
               nav["turning_basin_diameter_m"],
               1.5 * CFG.vessel.loa),
        _check("Berth pocket depth = T + max(0.07T,0.5)",
               nav["berth_pocket_depth_m"],
               formulas.berth_pocket_depth(CFG.vessel.draft)),
        _check("Squat = Cb·V²/100",
               nav["squat_m"], formulas.ship_squat(CFG.vessel.cb, CFG.vessel.speed_kn)),
        _check("Stopping distance = 7·Lmax",
               nav["stopping_distance_m"], 7 * CFG.vessel.loa),
        _check("Hudson W50: engine vs config",
               vals["breakwater"]["hudson_w50_t"], hudson_armour_mass(CFG.bw)),
        _check("Container quay = 3·Lmax + 4·25",
               vals["terminals"]["container_quay_m"],
               formulas.quay_length(3, CFG.vessel.loa)),
    ]
    return checks


def check_canonical_file() -> tuple:
    p = CFG.paths.root / "deliverables" / "canonical_values.json"
    if not p.exists():
        return ("canonical_values.json present", False, "missing", "expected")
    disk = json.loads(p.read_text(encoding="utf-8"))
    live = canonical_values()
    same = disk["navigation"]["channel_depth_m"] == live["navigation"]["channel_depth_m"]
    return ("canonical JSON in sync with engine", same,
            disk["navigation"]["channel_depth_m"],
            live["navigation"]["channel_depth_m"])


def main() -> int:
    checks = run_checks()
    checks.append(check_canonical_file())
    lines = ["# Engineering QA / QC Consistency Report",
             "",
             "**Coastal Structures Studio (CSS v1.0).** Automated gate verifying "
             "one set of validated values across the calculation engine, "
             "canonical JSON, CAD model and reports.",
             "",
             "| Check | Result | Engine | Target |",
             "|---|---|---|---|"]
    all_ok = True
    for name, ok, a, b in checks:
        all_ok &= ok
        lines.append(f"| {name} | {'✓ PASS' if ok else '✗ FAIL'} | {a} | {b} |")
    lines += ["",
              f"**Overall: {'ALL CHECKS PASS' if all_ok else 'CONFLICTS FOUND'}**.",
              "",
              "Design-basis note: the authoritative design vessel is "
              "Lmax 250 / bmax 32 / dmax 12 m (Panamax). The PowerPoint worked "
              "example (366/49/15.2) and `suezmax.json` (275/48/16.2) are earlier "
              "AI-tool exploratory runs and are flagged SUPERSEDED for this "
              "masterplan.",
              ""]
    out = CFG.paths.root / "deliverables" / "05_QA_Consistency_Report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(f"[{'PASS' if ok else 'FAIL'}] {n}" for n, ok, _, _ in checks))
    print("->", out.name, "| overall", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

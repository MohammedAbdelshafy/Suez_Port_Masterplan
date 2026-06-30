# Engineering QA / QC Consistency Report

**Coastal Structures Studio (CSS v1.0).** Automated gate verifying one set of validated values across the calculation engine, canonical JSON, CAD model and reports.

| Check | Result | Engine | Target |
|---|---|---|---|
| Channel depth: engine vs CAD | ✓ PASS | 13.41 | 13.41 |
| Channel width: engine vs CAD nav | ✓ PASS | 224.0 | 224.0 |
| Turning basin Ø: engine vs CAD nav | ✓ PASS | 375.0 | 375.0 |
| Turning basin Ø = 1.5·Lmax | ✓ PASS | 375.0 | 375.0 |
| Berth pocket depth = T + max(0.07T,0.5) | ✓ PASS | 12.84 | 12.84 |
| Squat = Cb·V²/100 | ✓ PASS | 0.306 | 0.306 |
| Stopping distance = 7·Lmax | ✓ PASS | 1750.0 | 1750.0 |
| Hudson W50: engine vs config | ✓ PASS | 7.58 | 7.575388817137004 |
| Container quay = 3·Lmax + 4·25 | ✓ PASS | 850.0 | 850.0 |
| canonical JSON in sync with engine | ✓ PASS | 13.41 | 13.41 |

**Overall: ALL CHECKS PASS**.

Design-basis note: the authoritative design vessel is Lmax 250 / bmax 32 / dmax 12 m (Panamax). The PowerPoint worked example (366/49/15.2) and `suezmax.json` (275/48/16.2) are earlier AI-tool exploratory runs and are flagged SUPERSEDED for this masterplan.

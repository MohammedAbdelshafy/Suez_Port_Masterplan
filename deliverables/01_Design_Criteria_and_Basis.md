# Suez Port Masterplan — Design Criteria & Basis of Design

**Coastal Structures Studio (CSS v1.0)** — Marine & Coastal Infrastructure
Student: Mohamed Abdelshafy (20107979) · Course: ECB 3802 · Arab Academy for
Science, Technology & Maritime Transport (Smart Village) · Supervisor:
Dr. Walid Al-Amri.

> Concept / planning level. Not for construction. All values are produced by
> the single-source calculation engine (`calculations.py`) and reused verbatim
> across the CAD model, figures, thesis, presentation and posters via
> `canonical_values.json`.

## 1. Design philosophy
The port is dimensioned around a single **governing design vessel** — the
largest ship the port must routinely serve. Every navigation and berthing
dimension is derived from that vessel using recognised concept methods
(PIANC WG121, UNCTAD, Barrass II). One source of truth flows from
*numbers → geometry → drawing*.

## 2. Governing design vessel (lecturer's notation)
| Symbol | Parameter | Value |
|---|---|---|
| **Lmax** | Length overall | **250 m** |
| **bmax** | Moulded beam | **32 m** |
| **dmax** | Full-load draft | **12 m** |
| Cb | Block coefficient (bulk, course table) | 0.85 |
| V | Transit speed in channel | 6 kn |
| DWT | Deadweight | 75 000 t |
| Class | — | Panamax bulk carrier |

*Design-basis note (QA).* The authoritative vessel is Lmax/bmax/dmax =
250/32/12 m (ECB 3802 brief). The existing PowerPoint worked example
(366/49/15.2) and `suezmax.json` (275/48/16.2) are earlier AI-tool exploratory
runs and are **superseded** for this masterplan; the presentation is to be
realigned to the values in this document.

## 3. Met-ocean & datum criteria
| Item | Basis |
|---|---|
| Vertical datum | Chart Datum (CD); levels quoted +/− m CD |
| Exposure (approach) | Moderate; entrance reach sheltered by breakwaters |
| Design wave Hs (breakwater) | 4.5 m |
| Wave allowance Hw (depth) | 0.5 m |
| Seabed | Maintainable/soft for dredging; rock-armour from quarry |

## 4. Adopted principal dimensions (from `calculations.py`)
| Quantity | Symbol / formula | Value |
|---|---|---|
| Ship squat | S = Cb·V²/100 | 0.31 m |
| Net under-keel clearance | UKC = max(0.05·dmax, 0.5) | 0.60 m |
| **Approach-channel depth** | D = dmax + UKC + S + Hw | **13.41 m** |
| Berth-pocket depth | Db = dmax + max(0.07·dmax, 0.5) | 12.84 m |
| **Approach-channel width** | PIANC two-way (adopted) | **224 m** |
| Approach-channel length | brief | 2 000 m |
| Channel bend radius | brief | 1 500 m |
| **Turning-basin diameter** | Dt = 1.5·Lmax | **375 m** (11.04 ha) |
| Emergency stopping distance | Ls ≈ 7·Lmax | 1 750 m |
| Anchorage swing radius | R = Lmax + 6D + 30 | 360.5 m (40.82 ha) |
| Total quay length | Σ Lq = n·Lmax + (n+1)c | ≈ 2 600 m / 9 berths |

## 5. Terminal program
| Terminal | Berths | Quay (Lq) |
|---|---|---|
| Container | 3 | 850 m |
| General cargo | 2 | 575 m |
| Oil | 2 | 575 m |
| Passenger | 1 | 300 m |
| Ro-Ro | 1 | 300 m |
| Liquid bulk (tank farm) | — | 5 tanks Ø30 m @ 45 m c/c, bunded |
| Dry bulk (silos) | — | 10 silos Ø10 m |
| Dry dock + repair yard | — | graving dock 290 × 52 m |
| Future expansion | — | reserved eastern parcel |

## 6. Breakwaters
Twin rubble-mound moles flanking the entrance (configuration referenced from a
NASA satellite image of the Suez Canal port entrance, reconstructed
mathematically): North 1 450 m, South 950 m, crest +7.0 m CD, seaward slope
2H:1V. Hudson armour **W50 = 7.6 t** (Hs 4.5 m, Kd 4.0, rough quarry stone,
trunk).

## 7. Codes & references
PIANC WG121 (approach channels), UNCTAD port practice, Barrass II (squat),
BS 6349 / USACE CEM (marine works, Hudson), ROM 3.1-99 (layout). Concept level
— to be confirmed by real-time manoeuvring simulation and site surveys
(met-ocean, bathymetric, geotechnical).

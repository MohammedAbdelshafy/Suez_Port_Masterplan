# Suez Port Masterplan Design — Engineering Thesis Chapter

**Student:** Mohamed Abdelshafy (ID 20107979)
**Course:** ECB 3802 — Marine Port Engineering
**Institution:** Arab Academy for Science, Technology & Maritime Transport — Smart Village Campus
**Supervisor:** Dr. Walid Al-Amri
**Prepared with:** Coastal Structures Studio (CSS v1.0)

> All numerical values in this chapter are produced by the project's
> single-source calculation engine and are identical to those in the CAD
> package, figures, calculation report, presentation and posters. Concept /
> planning level — not for construction.

---

## 1. Introduction

The Suez corridor carries on the order of 12 % of world seaborne trade, and the
ports serving it must accommodate vessels whose dimensions continue to grow.
Port and harbour geometry — channel depth and width, turning basin, berths and
breakwaters — must be checked against a defined **design vessel** so that the
largest expected ship can enter, turn, berth and depart safely under the local
met-ocean regime.

This chapter presents the concept masterplan for a multipurpose Suez port
developed for the ECB 3802 graduation project. The work applies recognised
concept-design methods (PIANC WG121, UNCTAD, Barrass II) to a single governing
design vessel and translates the resulting dimensions directly into a fully
parametric AutoCAD masterplan. The governing principle is *one source of
truth*: the engineering numbers drive the geometry, which drives the drawing,
the figures and the written deliverables, so that no value can drift between
documents.

### 1.1 Aim and objectives
The aim is to produce a defensible concept masterplan for a Suez port serving
the design vessel. The objectives are to:
1. define the governing design vessel and design criteria;
2. compute the principal navigation and berthing dimensions from recognised
   concept formulas;
3. size the protective breakwaters by the Hudson method;
4. lay out the terminals, roads, utilities and expansion areas; and
5. deliver a coordinated, internally consistent CAD + figure + report package.

---

## 2. Literature review

**Approach channels (PIANC WG121).** The PIANC concept (Class III) method
builds the navigable width from manoeuvring lanes, exposure-dependent
additional widths, a passing distance for two-way traffic and bank clearances,
each expressed as a multiple of beam `bmax`. Channel depth stacks the static
draft, a net under-keel clearance, the dynamic squat and a wave-response
allowance.

**Ship squat (Barrass II).** A ship under way in shallow/restricted water
settles bodily and trims; Barrass's second formula expresses the maximum bow
squat as `S = Cb·V²/100`, capturing the strong (square-law) dependence on
speed and the role of hull fullness `Cb`.

**Turning basins, quays and anchorages (UNCTAD / standard practice).** Turning
diameters are taken as a multiple `k` of `Lmax` depending on manoeuvre aids;
quay length sums one ship length per berth plus working clearances; single
swing-mooring anchorages sweep a circle whose radius scales with `Lmax` and
water depth.

**Rubble-mound breakwaters (Hudson / BS 6349 / USACE CEM).** The Hudson formula
sizes primary armour from the design wave height, a stability coefficient `Kd`,
the relative density of the armour and the structure slope. It remains the
standard concept-level check for trunk armour mass.

---

## 3. Site selection and context

The site is the Suez Canal port entrance on the Egyptian coast. A NASA
satellite image of the entrance (used strictly as reference, not traced)
informs the configuration: an approach from the open sea to the north-west,
**twin breakwater moles** flanking the dredged entrance (the northern/western
mole longer than the southern), a sand spit on the seaward flank, and reclaimed
land to the south-east carrying the terminals. The masterplan reconstructs
this configuration mathematically while keeping realistic proportions and
accepted port-engineering practice.

---

## 4. Design criteria

The governing design vessel (lecturer's notation) is a **Panamax bulk
carrier**:

| Lmax | bmax | dmax | Cb | V | DWT |
|---|---|---|---|---|---|
| 250 m | 32 m | 12 m | 0.85 | 6 kn | 75 000 t |

Vertical datum is Chart Datum (CD). The seaward approach is treated as
*moderate* exposure, while the breakwater-protected entrance reach is
*sheltered*. The breakwater design wave height is Hs = 4.5 m. Full criteria are
listed in *01 — Design Criteria & Basis of Design*.

---

## 5. Methodology

The calculation method set is implemented once, in `formulas.py`, and exercised
by `calculations.py`, which emits both the human-readable calculation report
and the machine-readable `canonical_values.json`. The CAD generator and the
figure scripts import the same module, guaranteeing numerical consistency
(verified automatically by `qa_check.py`).

The method sequence is: squat → UKC → channel depth → berth-pocket depth →
channel width → turning basin → quay length → stopping distance → anchorage →
breakwater armour. Each step is documented in the calculation report with
objective, theory, governing equation, variables, units, assumptions,
substitution, intermediates, result, interpretation and design implication.

---

## 6. Calculations (summary)

Full derivations are in *02 — Engineering Calculation Report*; the principal
results are:

| # | Quantity | Equation | Result |
|---|---|---|---|
| C-1 | Ship squat | S = Cb·V²/100 | **0.31 m** |
| C-2 | Net UKC | max(0.05·dmax, 0.5) | **0.60 m** |
| C-3 | Channel depth | D = dmax + UKC + S + Hw | **13.41 m** |
| C-4 | Berth-pocket depth | dmax + max(0.07·dmax,0.5) | **12.84 m** |
| C-5 | Channel width | PIANC two-way (adopted) | **224 m** |
| C-6 | Turning Ø / area | Dt = 1.5·Lmax | **375 m / 11.04 ha** |
| C-7 | Container quay | 3·Lmax + 4·c | **850 m** |
| C-8 | Stopping distance | 7·Lmax | **1 750 m** |
| C-9 | Anchorage R / area | Lmax + 6D + 30 | **360.5 m / 40.82 ha** |
| C-10 | Breakwater armour | Hudson W50 | **7.6 t** |

Supporting figures: Fig. 1 (channel cross-section & depth build-up), Fig. 2
(depth components), Fig. 3 (PIANC width build-up), Fig. 4 (breakwater
cross-section), Fig. 5 (masterplan key-plan).

---

## 7. Results — the masterplan

The computed dimensions are assembled into the masterplan (CAD package
`Suez_Port_Masterplan.dxf`, A1/A3 layouts):

- **Navigation:** a 2 000 m × 224 m two-way approach channel dredged to
  −13.4 m CD, a 375 m turning basin in front of the quays, and an offshore
  anchorage.
- **Breakwaters:** twin rubble-mound moles (North 1 450 m, South 950 m, crest
  +7.0 m CD) with roundheads, sized by Hudson (W50 ≈ 7.6 t).
- **Terminals:** container (3 berths / 850 m), passenger, general cargo, ro-ro,
  oil, a bunded liquid-bulk tank farm (5 × Ø30 m), a dry-bulk silo field
  (10 × Ø10 m), a graving dry dock and repair yard, with a reserved eastern
  expansion parcel — ≈ 2 600 m of quay over 9 berths.
- **Infrastructure:** primary/secondary roads, a roundabout, truck parking, a
  utility corridor, a security fence with main and truck gates, and a
  coordinate grid.

Estimated capital dredging (channel + basin × depth) ≈ 7.5 × 10⁶ m³ (see Bill
of Quantities).

---

## 8. Discussion

The adopted channel width of 224 m (= 7·bmax) lies between the PIANC two-way
*sheltered* requirement (217.6 m) and the *moderate-exposure* envelope
(262.4 m); it is defensible for a breakwater-protected canal entrance and
carries a small margin over the sheltered case. The 375 m turning basin is
exactly 1.5·Lmax, consistent with thruster/tug-assisted turning. The dredged
depth of 13.41 m provides 1.41 m of dynamic and safety allowance over the
12 m design draft.

These are **concept-level** figures. Empirical rules give ranges rather than
unique answers and must be confirmed by real-time manoeuvring simulation, and
by met-ocean, tidal, bathymetric and geotechnical surveys, with a qualified
maritime engineer in the loop.

---

## 9. Environmental considerations

A summary environmental assessment is provided in *04 — Environmental
Assessment*, covering capital and maintenance dredging and sediment management,
water quality and turbidity, sediment transport and morphology, marine ecology,
air quality, noise, spill prevention at the oil/liquid-bulk terminals, and
sustainability measures. Environmental buffer zones are reserved in the layout.

---

## 10. Conclusion and future work

A standards-based concept masterplan for a Suez port has been produced for the
Panamax design vessel (Lmax/bmax/dmax = 250/32/12 m). Using PIANC/UNCTAD/Barrass
concept methods and the Hudson formula, the principal dimensions were derived
and translated into a fully parametric, internally consistent CAD + figure +
report package — every value traceable to one engine. Future work: real-time
manoeuvring simulation, met-ocean and morphological modelling, layout
optimisation, structural design of quay walls and breakwater detailing, and a
3D / BIM model.

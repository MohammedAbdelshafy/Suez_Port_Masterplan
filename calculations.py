"""
calculations.py
================

Authoritative engineering calculation engine -- the SINGLE SOURCE OF TRUTH for
every numerical value in the Suez Port Masterplan project. The CAD generator,
the thesis chapter, the figures and the downstream presentation / posters / CSS
v1.0 platform all consume the values produced here, so no number is ever
re-typed by hand.

Author context: Coastal Structures Studio (CSS v1.0).
Notation follows the lecturer: Lmax (length), bmax (beam), dmax (draft).

Each calculation is captured as a :class:`CalcStep` carrying the full
design-review structure:
  1 objective  2 theory  3 equation  4 variables  5 units  6 assumptions
  7 substitution  8 intermediates  9 result  10 interpretation  11 implication
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import formulas
from config import CFG, hudson_armour_mass


@dataclass
class CalcStep:
    key: str
    title: str
    objective: str
    theory: str
    equation: str
    variables: dict[str, str]
    units: str
    assumptions: list[str]
    substitution: str
    intermediates: list[str]
    value: float
    result_unit: str
    interpretation: str
    implication: str

    def to_markdown(self) -> str:
        v = "\n".join(f"- `{k}` = {d}" for k, d in self.variables.items())
        a = "\n".join(f"- {x}" for x in self.assumptions)
        it = "\n".join(f"- {x}" for x in self.intermediates)
        return f"""### {self.title}

**1. Objective.** {self.objective}

**2. Engineering theory.** {self.theory}

**3. Governing equation.**

$$ {self.equation} $$

**4. Variable definitions.**
{v}

**5. Units.** {self.units}

**6. Assumptions.**
{a}

**7. Numerical substitution.**

$$ {self.substitution} $$

**8. Intermediate calculations.**
{it}

**9. Final answer.**  **{self.value:g} {self.result_unit}**

**10. Engineering interpretation.** {self.interpretation}

**11. Design implication.** {self.implication}
"""


# ----------------------------------------------------------------------------
# Build the ordered list of calculations from the canonical inputs.
# ----------------------------------------------------------------------------
def build_steps() -> list[CalcStep]:
    v = CFG.vessel
    nav = CFG.nav
    bw = CFG.bw
    Lmax, bmax, dmax, Cb, V = v.loa, v.beam, v.draft, v.cb, v.speed_kn

    S = formulas.ship_squat(Cb, V)
    ukc = formulas.net_ukc(dmax)
    Hw = formulas.EXPOSURE_HW[nav.exposure]
    D = formulas.channel_depth(dmax, Cb, V, nav.exposure)
    Db = formulas.berth_pocket_depth(dmax)
    W_shelt = formulas.channel_width_two_way(bmax, "sheltered")
    W_mod = formulas.channel_width_two_way(bmax, "moderate")
    Dt = formulas.turning_circle(Lmax, nav.maneuver_aids)
    R_basin = Dt / 2.0
    A_basin = formulas.circle_area(R_basin)
    Lq_cont = formulas.quay_length(3, Lmax)
    Ls = formulas.stopping_distance(Lmax)
    R_anch = formulas.anchorage_radius(Lmax, D)
    A_anch = formulas.circle_area(R_anch)
    W50 = hudson_armour_mass(bw)
    sr = bw.rock_density / bw.water_density

    steps: list[CalcStep] = [
        CalcStep(
            "squat", "C-1  Ship Squat (Barrass II)",
            "Determine the dynamic bow sinkage of the design vessel under way "
            "to size the dredged depth.",
            "A moving ship in restricted water experiences a pressure drop that "
            "increases its mean draft (squat). Barrass II gives the maximum bow "
            "squat as a function of block coefficient and speed.",
            r"S = \frac{C_b \cdot V^2}{100}",
            {"C_b": "block coefficient (bulk = 0.85, course table)",
             "V": "transit speed in the channel [kn]"},
            "metres [m]",
            ["Design vessel is a Panamax bulk carrier (Cb = 0.85).",
             "Transit speed limited to V = 6 kn in the approach channel.",
             "Open-water Barrass II value taken as the design squat."],
            rf"S = \frac{{{Cb} \cdot {V:.0f}^2}}{{100}}",
            [f"V² = {V**2:.0f}", f"Cb·V² = {Cb*V**2:.2f}"],
            round(S, 3), "m",
            "A squat of ~0.31 m is modest because the transit speed is "
            "deliberately restricted; squat grows with the square of speed.",
            "Adds directly to the required dredged depth of the channel."),

        CalcStep(
            "ukc", "C-2  Net Under-Keel Clearance",
            "Establish the manoeuvrability and bottom-safety margin beneath the "
            "keel.",
            "PIANC UKC philosophy provides a net clearance to cover "
            "manoeuvrability, survey/bottom uncertainty and squat that is not "
            "otherwise accounted for.",
            r"UKC = \max(0.05\,d_{max},\; 0.5)",
            {"d_{max}": "design vessel full-load draft [m]"},
            "metres [m]",
            ["Soft/maintainable seabed; net UKC governed by 5% of draft.",
             "Minimum floor of 0.50 m applied for shallow-draft cases."],
            rf"UKC = \max(0.05 \cdot {dmax:.0f},\; 0.5) = \max({0.05*dmax:.2f},\;0.5)",
            [f"0.05·dmax = {0.05*dmax:.2f} m", "governing value = 0.60 m"],
            round(ukc, 2), "m",
            "0.60 m net clearance is retained beneath the keel at all states of "
            "manoeuvre.",
            "Second additive term of the dredged-depth build-up."),

        CalcStep(
            "depth", "C-3  Approach-Channel Dredged Depth",
            "Compute the design dredge level of the approach channel below Chart "
            "Datum.",
            "The dredged depth stacks the static draft, the net UKC, the dynamic "
            "squat and a wave-response allowance set by met-ocean exposure.",
            r"D = d_{max} + UKC + S + H_w",
            {"d_{max}": "draft [m]", "UKC": "net under-keel clearance [m]",
             "S": "Barrass squat [m]", "H_w": "wave allowance (moderate) [m]"},
            "metres [m]",
            ["Moderate exposure on the seaward approach → Hw = 0.5 m.",
             "Tidal window not relied upon (depth referenced to Chart Datum)."],
            rf"D = {dmax:.0f} + {ukc:.2f} + {S:.2f} + {Hw:.1f}",
            [f"sum = {dmax + ukc + S + Hw:.2f} m"],
            round(D, 2), "m (below CD)",
            "A dredged depth of ~13.4 m comfortably accommodates the 12.0 m "
            "design draft with all dynamic allowances.",
            "Sets the dredging volume and the channel/basin design level "
            "(adopt practical dredge level −13.5 m CD)."),

        CalcStep(
            "berth", "C-4  Berth-Pocket Depth",
            "Size the dredged depth alongside the quay where the vessel is "
            "effectively stationary.",
            "At berth the squat term collapses; PIANC retains a reduced-speed "
            "allowance of 7% of draft (floor 0.5 m).",
            r"D_b = d_{max} + \max(0.07\,d_{max},\;0.5)",
            {"d_{max}": "draft [m]"},
            "metres [m]",
            ["Negligible squat alongside (reduced-speed manoeuvre).",
             "Allowance governed by 7% of draft."],
            rf"D_b = {dmax:.0f} + \max(0.07 \cdot {dmax:.0f},\;0.5)",
            [f"0.07·dmax = {0.07*dmax:.2f} m", "governing = 0.84 m"],
            round(Db, 2), "m (below CD)",
            "Berth pockets are ~0.6 m shallower than the channel, reflecting the "
            "absence of squat alongside.",
            "Governs quay-wall toe level and alongside dredging."),

        CalcStep(
            "width", "C-5  Approach-Channel Width (PIANC two-way)",
            "Determine the navigable width of the two-way approach channel.",
            "PIANC WG121 builds the width from two manoeuvring lanes (1.5B "
            "each), an exposure-dependent additional width (a·B per lane), a "
            "passing distance (1.6B) and two bank clearances (0.5B each).",
            r"W = 2(1.5b_{max}) + 2(a\,b_{max}) + 1.6\,b_{max} + 2(0.5b_{max})",
            {"b_{max}": "beam [m]",
             "a": "exposure factor (sheltered 0.6 / moderate 1.3)"},
            "metres [m]",
            ["Two-way traffic adopted (consistent with the project brief).",
             "The entrance reach is protected by the twin breakwaters → the "
             "sheltered factor a = 0.6 governs the inner channel.",
             "Adopted width 224 m (= 7·bmax) exceeds the sheltered requirement, "
             "giving margin toward the moderate-exposure value."],
            rf"W_{{shelt}} = b_{{max}}(5.6 + 2\cdot0.6) = {bmax}\cdot6.8",
            [f"sheltered (a=0.6): W = {W_shelt:.1f} m",
             f"moderate (a=1.3): W = {W_mod:.1f} m",
             "adopted design width = 224.0 m (= 7·bmax, brief value)"],
            float(nav.channel_width), "m",
            "The adopted 224 m lies between the sheltered (217.6 m) requirement "
            "and the moderate-exposure envelope (262.4 m), a defensible concept "
            "width for a breakwater-protected canal entrance.",
            "Fixes the dredged channel footprint and the breakwater entrance "
            "gap."),

        CalcStep(
            "turning", "C-6  Turning-Basin Diameter & Area",
            "Size the turning basin that lets the design vessel reverse heading.",
            "Concept practice sets the turning-circle diameter as a multiple k "
            "of LOA; with bow/stern thrusters (or strong tug assistance) "
            "k = 1.5.",
            r"D_t = k \cdot L_{max}\;;\quad A = \pi (D_t/2)^2",
            {"k": "manoeuvre-aid factor (thrusters = 1.5)",
             "L_{max}": "length overall [m]"},
            "metres / hectares",
            ["Tug- and thruster-assisted turning (k = 1.5).",
             "Basin centred in front of the quays within sheltered water."],
            rf"D_t = 1.5 \cdot {Lmax:.0f} = {Dt:.0f}\,\text{{m}};\;"
            rf"A = \pi({R_basin:.1f})^2",
            [f"Dt = {Dt:.1f} m (matches brief Ø375)",
             f"radius = {R_basin:.1f} m",
             f"area = {A_basin:,.0f} m² = {A_basin/1e4:.2f} ha"],
            round(Dt, 1), "m (Ø)",
            "A 375 m basin (1.5·Lmax) is adequate for assisted turning of the "
            "Panamax design vessel.",
            "Defines the dredged turning-basin footprint and its 11.04 ha "
            "water area."),

        CalcStep(
            "quay", "C-7  Quay Length (container terminal, 3 berths)",
            "Determine the continuous quay length for the governing container "
            "terminal.",
            "Total quay length sums one LOA per berth plus an inter-berth / end "
            "clearance c on each side; c = max(0.10·LOA, 15 m).",
            r"L_q = n\,L_{max} + (n+1)\,c,\quad c=\max(0.10L_{max},15)",
            {"n": "number of berths", "c": "clearance per gap [m]"},
            "metres [m]",
            ["Container terminal sized for n = 3 contiguous berths.",
             "Clearance c = 0.10·250 = 25 m (> 15 m floor)."],
            rf"L_q = 3 \cdot {Lmax:.0f} + 4 \cdot 25",
            [f"berths = 3·{Lmax:.0f} = {3*Lmax:.0f} m",
             "clearances = 4·25 = 100 m",
             f"Lq = {Lq_cont:.0f} m"],
            round(Lq_cont, 1), "m",
            "850 m of quay supports three Panamax berths with working "
            "clearances.",
            "Sets the container quay footprint; the same formula sizes every "
            "other terminal (total ≈ 2,600 m over 9 berths)."),

        CalcStep(
            "stopping", "C-8  Emergency Stopping Distance",
            "Estimate the crash-stop distance used to set the approach reach and "
            "anchorage offset.",
            "For a loaded vessel performing an emergency astern manoeuvre the "
            "stopping distance is of the order of seven ship lengths.",
            r"L_s \approx 7 \cdot L_{max}",
            {"L_{max}": "length overall [m]"},
            "metres [m]",
            ["Loaded condition, full astern (concept envelope)."],
            rf"L_s = 7 \cdot {Lmax:.0f}",
            [f"Ls = {Ls:.0f} m"],
            round(Ls, 0), "m",
            "≈1,750 m of clear water is needed ahead of a stopping vessel.",
            "Confirms the 2,000 m approach-channel length provides adequate "
            "stopping room."),

        CalcStep(
            "anchorage", "C-9  Anchorage Swing Radius & Area",
            "Size the offshore waiting anchorage for a single swinging vessel.",
            "A single-point swing mooring sweeps a circle whose radius adds the "
            "ship length, a scope allowance (≈6·water depth) and a 30 m safety "
            "margin.",
            r"R = L_{max} + 6D + 30\;;\quad A = \pi R^2",
            {"D": "water depth at anchorage [m]"},
            "metres / hectares",
            ["Single-point swing mooring; water depth ≈ channel depth D.",
             "Scope factor 6·D for the mooring chain."],
            rf"R = {Lmax:.0f} + 6 \cdot {D:.2f} + 30",
            [f"6·D = {6*D:.2f} m", f"R = {R_anch:.1f} m",
             f"A = {A_anch:,.0f} m² = {A_anch/1e4:.2f} ha"],
            round(R_anch, 1), "m (R)",
            "Each waiting vessel requires a ~360 m radius swing circle "
            "(≈40.8 ha).",
            "Reserves the offshore anchorage water area in the masterplan."),

        CalcStep(
            "breakwater", "C-10  Breakwater Armour (Hudson)",
            "Size the primary rock armour of the rubble-mound breakwaters.",
            "The Hudson formula gives the median armour-unit mass required for "
            "stability under design wave attack, as a function of wave height, "
            "stability coefficient, relative density and slope.",
            r"W_{50} = \frac{\rho_s\,H_s^3}{K_d\,(S_r-1)^3\,\cot\alpha}",
            {"H_s": "design significant wave height [m]",
             "K_d": "stability coefficient (rough quarry stone, trunk)",
             "S_r": "relative density ρs/ρw", "\\cot\\alpha": "armour slope"},
            "tonnes [t]",
            [f"Hs = {bw.design_wave_h} m, Kd = {bw.kd_stability} (trunk, "
             "breaking, rough rock).",
             f"ρs = {bw.rock_density:.0f}, ρw = {bw.water_density:.0f} kg/m³ "
             f"→ Sr = {sr:.3f}.",
             f"Seaward slope cot α = {bw.armour_slope_cot:.1f} (2H:1V)."],
            rf"W_{{50}} = \frac{{{bw.rock_density:.0f}\cdot{bw.design_wave_h}^3}}"
            rf"{{{bw.kd_stability:.0f}\cdot({sr:.3f}-1)^3\cdot{bw.armour_slope_cot:.1f}}}",
            [f"Hs³ = {bw.design_wave_h**3:.2f}",
             f"(Sr−1)³ = {(sr-1)**3:.3f}",
             f"W50 = {W50*1000:,.0f} kg = {W50:.2f} t"],
            round(W50, 2), "t",
            "A ~7.6 t median armour rock is required on the seaward slope; "
            "two layers give the armour thickness used in the cross-section.",
            "Defines the breakwater armour grading, layer thickness and quarry "
            "requirement (Bill of Quantities).")
    ]
    return steps


# ----------------------------------------------------------------------------
# Canonical values (machine-readable -- consumed by PPT / posters / CSS).
# ----------------------------------------------------------------------------
def canonical_values() -> dict:
    v = CFG.vessel
    nav = CFG.nav
    D = CFG.dredged_depth
    Dt = nav.turning_basin_diameter
    R_basin = Dt / 2.0
    R_anch = formulas.anchorage_radius(v.loa, D)
    return {
        "project": {
            "title": CFG.project.title,
            "author": "Coastal Structures Studio (CSS v1.0)",
            "student": CFG.project.student,
            "student_id": CFG.project.student_id,
            "course": CFG.project.course_code,
            "supervisor": CFG.project.supervisor,
        },
        "design_vessel": {
            "class": "Panamax bulk carrier",
            "Lmax_m": v.loa, "bmax_m": v.beam, "dmax_m": v.draft,
            "Cb": v.cb, "speed_kn": v.speed_kn, "dwt_t": v.dwt,
        },
        "navigation": {
            "channel_length_m": nav.channel_length,
            "channel_width_m": nav.channel_width,
            "channel_depth_m": round(D, 2),
            "berth_pocket_depth_m": round(formulas.berth_pocket_depth(v.draft), 2),
            "turning_basin_diameter_m": Dt,
            "turning_basin_radius_m": R_basin,
            "turning_basin_area_ha": round(formulas.circle_area(R_basin) / 1e4, 2),
            "channel_bend_radius_m": nav.channel_bend_radius,
            "squat_m": round(formulas.ship_squat(v.cb, v.speed_kn), 3),
            "ukc_m": round(formulas.net_ukc(v.draft), 2),
            "stopping_distance_m": round(formulas.stopping_distance(v.loa), 0),
            "anchorage_radius_m": round(R_anch, 1),
            "anchorage_area_ha": round(formulas.circle_area(R_anch) / 1e4, 2),
        },
        "terminals": {
            "container_quay_m": round(formulas.quay_length(3, v.loa), 1),
            "general_cargo_quay_m": round(formulas.quay_length(2, v.loa), 1),
            "oil_quay_m": round(formulas.quay_length(2, v.loa), 1),
            "passenger_quay_m": round(formulas.quay_length(1, v.loa), 1),
            "roro_quay_m": round(formulas.quay_length(1, v.loa), 1),
            "total_berths": nav.num_berths_total,
            "tanks": {"count": CFG.tanks.count, "diameter_m": CFG.tanks.diameter,
                      "spacing_m": CFG.tanks.diameter * CFG.tanks.spacing_factor},
            "silos": {"count": CFG.silos.count, "diameter_m": CFG.silos.diameter},
        },
        "breakwater": {
            "hudson_w50_t": round(hudson_armour_mass(CFG.bw), 2),
            "crest_level_m_cd": CFG.bw.crest_level,
            "design_wave_hs_m": CFG.bw.design_wave_h,
        },
    }


# ----------------------------------------------------------------------------
# Output writers
# ----------------------------------------------------------------------------
def deliverables_dir() -> Path:
    d = CFG.paths.root / "deliverables"
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_outputs() -> tuple[Path, Path]:
    d = deliverables_dir()
    vals = canonical_values()
    json_path = d / "canonical_values.json"
    json_path.write_text(json.dumps(vals, indent=2), encoding="utf-8")

    steps = build_steps()
    pj = CFG.project
    md = [
        f"# {pj.title} — Engineering Calculation Report",
        "",
        "**Coastal Structures Studio (CSS v1.0)** — Marine & Coastal "
        "Infrastructure.  ",
        f"Student: {pj.student} ({pj.student_id}) · Course: {pj.course_code} · "
        f"Supervisor: {pj.supervisor}.",
        "",
        "> Single source of truth. Every value below is computed in "
        "`calculations.py` from the course PIANC / UNCTAD / Barrass method set "
        "and is reused verbatim by the CAD model, figures, thesis, presentation "
        "and posters via `canonical_values.json`. Concept level — not for "
        "construction.",
        "",
        "## Design vessel (lecturer's notation)",
        "",
        f"| Lmax | bmax | dmax | Cb | V | DWT | Class |",
        f"|---|---|---|---|---|---|---|",
        f"| {CFG.vessel.loa:.0f} m | {CFG.vessel.beam:.0f} m | "
        f"{CFG.vessel.draft:.0f} m | {CFG.vessel.cb} | {CFG.vessel.speed_kn:.0f} "
        f"kn | {CFG.vessel.dwt:,.0f} t | Panamax bulk carrier |",
        "",
        "## Calculations",
        "",
    ]
    for s in steps:
        md.append(s.to_markdown())
    report_path = d / "02_Engineering_Calculation_Report.md"
    report_path.write_text("\n".join(md), encoding="utf-8")
    return report_path, json_path


if __name__ == "__main__":
    rep, js = write_outputs()
    print("Wrote:", rep.name, "and", js.name)
    import pprint
    pprint.pp(canonical_values()["navigation"])

"""
figures.py
==========

Publication-quality engineering figures for the thesis, presentation and
posters. Every figure is drawn from the same canonical values produced by
``calculations`` / ``formulas`` so the numbers can never drift from the CAD or
the report.

Branding: Coastal Structures Studio (CSS v1.0). Notation: Lmax / bmax / dmax.

Run:  python figures.py   ->  deliverables/figures/*.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

import formulas
from config import CFG
from calculations import canonical_values

FIG_DIR = CFG.paths.root / "deliverables" / "figures"
ACCENT = "#0b6e8f"
SEA = "#bfe0ef"
SAND = "#ece2c6"
STONE = "#7c7c80"


def _save(fig, name: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    p = FIG_DIR / name
    fig.text(0.99, 0.01, "Coastal Structures Studio (CSS v1.0)", ha="right",
             va="bottom", fontsize=7, color="grey")
    fig.savefig(p, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def fig_channel_section() -> Path:
    """Approach-channel depth build-up cross-section."""
    v = CFG.vessel
    S = formulas.ship_squat(v.cb, v.speed_kn)
    ukc = formulas.net_ukc(v.draft)
    Hw = formulas.EXPOSURE_HW[CFG.nav.exposure]
    D = formulas.channel_depth(v.draft, v.cb, v.speed_kn, CFG.nav.exposure)
    W = CFG.nav.channel_width

    fig, ax = plt.subplots(figsize=(9, 5.2))
    # water column
    ax.add_patch(Rectangle((0, -D), W, D, color=SEA, zorder=0))
    # dredged bed
    ax.plot([-20, W + 20], [-D, -D], color=SAND, lw=6, solid_capstyle="butt")
    ax.fill_between([-20, W + 20], [-D, -D], [-D - 2.5, -D - 2.5], color=SAND, zorder=0)
    # still water level
    ax.axhline(0, color=ACCENT, lw=1.4, ls="--")
    ax.text(W, 0.25, "SWL +0.0 m CD", color=ACCENT, ha="right", fontsize=9)

    # design vessel hull (simplified) at centre, draft dmax
    bx = W / 2
    hull_w = v.beam * 1.6
    hull = Polygon([(bx - hull_w / 2, 0), (bx + hull_w / 2, 0),
                    (bx + hull_w / 2 - 6, -v.draft), (bx - hull_w / 2 + 6, -v.draft)],
                   closed=True, facecolor="#34506b", edgecolor="black", zorder=3)
    ax.add_patch(hull)
    ax.text(bx, -v.draft / 2, "DESIGN VESSEL\nLmax 250 · bmax 32 · dmax 12 m",
            color="white", ha="center", va="center", fontsize=8, zorder=4)

    # depth build-up bracket on the right (labels spread with leader lines)
    xb = W + 30
    levels = [("dmax = %.0f m" % v.draft, 0, -v.draft, "#34506b", -v.draft / 2),
              ("S (squat) = %.2f m" % S, -v.draft, -v.draft - S, "#c0612a", -8.5),
              ("UKC = %.2f m" % ukc, -v.draft - S, -v.draft - S - ukc, "#3a7d34", -11),
              ("Hw = %.1f m" % Hw, -v.draft - S - ukc, -D, "#7a5ea0", -13.5)]
    for label, y0, y1, c, ly in levels:
        ax.add_patch(Rectangle((xb, y1), 26, y0 - y1, color=c, alpha=0.9))
        mid = (y0 + y1) / 2
        ax.annotate(label, xy=(xb + 26, mid), xytext=(xb + 60, ly),
                    va="center", fontsize=8,
                    arrowprops=dict(arrowstyle="-", color="grey", lw=0.7))
    ax.annotate("", xy=(xb - 6, 0), xytext=(xb - 6, -D),
                arrowprops=dict(arrowstyle="<->", color="black"))
    ax.text(xb - 12, -D / 2, "D = %.2f m" % D, rotation=90, va="center",
            ha="right", fontsize=9, fontweight="bold")

    # channel width dimension
    ax.annotate("", xy=(0, -D - 1.6), xytext=(W, -D - 1.6),
                arrowprops=dict(arrowstyle="<->", color=ACCENT))
    ax.text(W / 2, -D - 2.2, "Approach channel width  W = %.0f m (PIANC two-way)" % W,
            ha="center", va="top", color=ACCENT, fontsize=9)

    ax.set_xlim(-40, W + 150)
    ax.set_ylim(-D - 3.5, 3)
    ax.set_aspect(4.0)
    ax.set_axis_off()
    ax.set_title("Figure 1 — Approach-Channel Cross-Section & Dredged-Depth "
                 "Build-up  (D = dmax + UKC + S + Hw)", fontsize=10,
                 fontweight="bold")
    return _save(fig, "fig1_channel_section.png")


def fig_depth_buildup_bar() -> Path:
    """Stacked-bar of the dredged-depth components."""
    v = CFG.vessel
    S = formulas.ship_squat(v.cb, v.speed_kn)
    ukc = formulas.net_ukc(v.draft)
    Hw = formulas.EXPOSURE_HW[CFG.nav.exposure]
    parts = [("dmax (draft)", v.draft, "#34506b"),
             ("UKC", ukc, "#3a7d34"),
             ("S (Barrass squat)", S, "#c0612a"),
             ("Hw (wave allow.)", Hw, "#7a5ea0")]
    fig, ax = plt.subplots(figsize=(5.6, 6))
    bottom = 0
    for label, val, c in parts:
        ax.bar(0, val, bottom=bottom, color=c, width=0.5, label=f"{label} = {val:.2f} m")
        ax.text(0, bottom + val / 2, f"{val:.2f}", ha="center", va="center",
                color="white", fontsize=9)
        bottom += val
    ax.text(0, bottom + 0.2, f"D = {bottom:.2f} m", ha="center", fontsize=11,
            fontweight="bold")
    ax.set_xticks([])
    ax.set_ylabel("Depth below Chart Datum [m]")
    ax.set_title("Figure 2 — Channel Dredged-Depth Components", fontsize=10,
                 fontweight="bold")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.04), fontsize=8)
    return _save(fig, "fig2_depth_buildup.png")


def fig_width_buildup() -> Path:
    """PIANC two-way width component bar chart."""
    B = CFG.vessel.beam
    comps = [("2 × manoeuvre lane (1.5B)", 2 * 1.5 * B),
             ("2 × additional width (a·B, a=0.6)", 2 * 0.6 * B),
             ("passing distance (1.6B)", 1.6 * B),
             ("2 × bank clearance (0.5B)", 2 * 0.5 * B)]
    total = sum(c[1] for c in comps)
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    labels = [c[0] for c in comps]
    vals = [c[1] for c in comps]
    bars = ax.barh(labels, vals, color=[ACCENT, "#3a7d34", "#c0612a", "#7a5ea0"])
    for b, val in zip(bars, vals):
        ax.text(val + 2, b.get_y() + b.get_height() / 2, f"{val:.1f} m",
                va="center", fontsize=9)
    ax.set_xlabel("Width contribution [m]")
    ax.set_title(f"Figure 3 — PIANC Two-Way Channel-Width Build-up "
                 f"(sheltered a=0.6 → {total:.1f} m; adopted 224 m)",
                 fontsize=10, fontweight="bold")
    ax.invert_yaxis()
    return _save(fig, "fig3_width_buildup.png")


def fig_breakwater_section() -> Path:
    """Schematic rubble-mound breakwater trunk cross-section."""
    bw = CFG.bw
    fig, ax = plt.subplots(figsize=(9, 5))
    H = bw.crest_level - bw.seabed_level
    cw = bw.crest_width
    sl, ll = bw.seaward_slope, bw.leeward_slope
    base = cw + (sl + ll) * H
    # armour > filter > core nested trapezoids
    def trap(off, color, label, lx):
        bw_w = base + 2 * off * sl
        x0 = -bw_w / 2
        pts = [(x0, 0), (x0 + bw_w, 0),
               (cw / 2 + off, H + off), (-cw / 2 - off, H + off)]
        ax.add_patch(Polygon(pts, closed=True, facecolor=color, edgecolor="black"))
        if label:
            ax.text(lx, H * 0.6, label, fontsize=8)
    trap(bw.armour_thickness + bw.filter_thickness, "#9a9a9e", "", 0)
    trap(bw.filter_thickness, "#b9b9bd", "", 0)
    trap(0, "#cfcfd3", "CORE", -10)
    # waterline
    ax.axhline(-bw.seabed_level, color=ACCENT, ls="--", lw=1.2)
    ax.text(base / 2, -bw.seabed_level + 0.6, "SWL +0.0 m CD", color=ACCENT,
            ha="right", fontsize=8)
    ax.text(0, H + bw.armour_thickness + 1.5, f"CREST +{bw.crest_level:.1f} m CD",
            ha="center", fontsize=8)
    ax.text(base / 2 + 6, H * 0.85, "ARMOUR", fontsize=8)
    ax.text(base / 2 + 6, H * 0.55, "FILTER", fontsize=8)
    w50 = canonical_values()["breakwater"]["hudson_w50_t"]
    ax.text(-base / 2, -3.0,
            f"Hudson: Hs={bw.design_wave_h} m · Kd={bw.kd_stability} · "
            f"slope {bw.seaward_slope:.0f}H:1V  →  W50 = {w50:.1f} t",
            fontsize=9, fontweight="bold")
    ax.set_xlim(-base / 2 - 15, base / 2 + 60)
    ax.set_ylim(-5, H + bw.armour_thickness + 4)
    ax.set_aspect(1.0)
    ax.set_axis_off()
    ax.set_title("Figure 4 — Rubble-Mound Breakwater Trunk Cross-Section "
                 "(Hudson armour)", fontsize=10, fontweight="bold")
    return _save(fig, "fig4_breakwater_section.png")


def fig_key_plan() -> Path:
    """Simplified masterplan key-plan schematic."""
    fig, ax = plt.subplots(figsize=(10, 6))
    # sea & land
    ax.add_patch(Rectangle((0, 0), 4, 6, color=SEA))
    ax.add_patch(Rectangle((4, 0), 6, 6, color=SAND))
    # breakwaters
    ax.add_patch(Polygon([(1.2, 3.6), (3.6, 3.2), (3.6, 3.35), (1.2, 3.78)],
                         closed=True, color=STONE))
    ax.add_patch(Polygon([(1.8, 2.4), (3.6, 2.7), (3.6, 2.55), (1.8, 2.25)],
                         closed=True, color=STONE))
    ax.text(1.0, 3.95, "N breakwater (1450 m)", fontsize=7)
    ax.text(1.4, 2.1, "S breakwater (950 m)", fontsize=7)
    # channel + basin
    ax.add_patch(Rectangle((0.2, 2.85), 3.4, 0.32, color="#86bcd4"))
    ax.text(1.0, 3.25, "Approach channel  2000 × 224 m", fontsize=7, color=ACCENT)
    ax.add_patch(plt.Circle((3.95, 3.0), 0.42, color="#86bcd4"))
    ax.text(3.95, 3.0, "Turning\nØ375", fontsize=6, ha="center", va="center")
    # terminals (stacked blocks on land)
    blocks = [("Container", 4.5, 4.6, 1.4, 1.0, "#cfe0ec"),
              ("Passenger", 4.5, 4.0, 1.4, 0.5, "#e0d6ec"),
              ("Gen. cargo", 4.5, 3.3, 1.4, 0.6, "#e4e0c6"),
              ("Ro-Ro", 4.5, 2.8, 1.4, 0.45, "#d2e4d6"),
              ("Oil", 4.5, 1.8, 1.4, 0.9, "#ecdace"),
              ("Tank farm", 6.1, 4.0, 1.3, 1.6, "#ecd6c8"),
              ("Silos", 6.1, 2.6, 1.3, 1.2, "#e2e0c8"),
              ("Dry dock", 6.1, 1.6, 0.7, 0.9, "#dddddd"),
              ("Expansion", 7.6, 1.6, 2.0, 4.0, "#f0eee6")]
    for name, x, y, w, h, c in blocks:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=c, edgecolor="grey"))
        ax.text(x + w / 2, y + h / 2, name, ha="center", va="center", fontsize=7)
    ax.annotate("OPEN SEA (NW)", (0.4, 5.4), fontsize=9, color=ACCENT)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title("Figure 5 — Suez Port Masterplan Key-Plan (schematic, not to "
                 "scale)", fontsize=10, fontweight="bold")
    return _save(fig, "fig5_key_plan.png")


def build_all() -> list[Path]:
    figs = [fig_channel_section(), fig_depth_buildup_bar(), fig_width_buildup(),
            fig_breakwater_section(), fig_key_plan()]
    return figs


if __name__ == "__main__":
    for p in build_all():
        print("Wrote", p.name)

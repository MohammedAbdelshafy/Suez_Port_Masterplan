"""
config.py
=========

Single source of truth for the Suez Port Masterplan parametric model.

Everything downstream (geometry, navigation, breakwaters, terminals, roads,
dimensions, annotations) is derived from the engineering inputs declared here.
No geometry module is allowed to hard-code a coordinate -- it must reference a
value computed in this file so the whole drawing regenerates when an input
changes.

Engineering basis
-----------------
* PIANC WG121 / WG49 -- approach channel & turning basin geometry.
* ROM 3.1-99 -- port layout and navigation areas.
* BS 6349 / USACE EM 1110-2-1100 -- breakwater and marine works.
* Hudson formula (CERC) -- rubble-mound armour sizing.

All linear dimensions are in metres. The model is drawn 1:1 (1 drawing unit
= 1 m) in model space; printable layouts apply the sheet scale.

Project: ECB 3802 -- Parametric Modeling & Marine Structures.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path


# ----------------------------------------------------------------------------
# Project metadata (drives the title block & report headers)
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class ProjectInfo:
    title: str = "SUEZ PORT MASTERPLAN DESIGN"
    student: str = "Mohamed Abdelshafy"
    student_id: str = "20107979"
    course_code: str = "ECB 3802"
    course_name: str = "Parametric Modeling & Marine Structures"
    supervisor: str = "Dr. Walid Al-Amri"
    drawing_number: str = "SPM-001"
    revision: str = "A"


# ----------------------------------------------------------------------------
# Primary engineering inputs
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class DesignVessel:
    """
    The governing design vessel ("DNA" of the port).

    Authoritative basis (ECB 3802 brief, lecturer's notation):
        Lmax = 250 m, bmax = 32 m, dmax = 12 m  (Panamax bulk carrier).
    Cb and transit speed follow the course block-coefficient table.
    """
    loa: float = 250.0          # Lmax - length overall   [m]
    beam: float = 32.0          # bmax - moulded breadth   [m]
    draft: float = 12.0         # dmax - full-load draft   [m]
    cb: float = 0.85            # block coefficient (bulk, course table)
    speed_kn: float = 6.0       # transit speed in the channel [kn]
    dwt: float = 75000.0        # deadweight (Panamax)     [t]
    vessel_type: str = "bulk"   # governs Cb (course table)

    # Lecturer's-notation aliases (read-only convenience).
    @property
    def Lmax(self) -> float: return self.loa
    @property
    def bmax(self) -> float: return self.beam
    @property
    def dmax(self) -> float: return self.draft


@dataclass(frozen=True)
class NavigationInputs:
    channel_length: float = 2000.0          # [m]  (design brief)
    channel_width: float = 224.0            # [m]  adopted design width (see note)
    turning_basin_diameter: float = 375.0   # [m]  = 1.5 * Lmax (thrusters)
    channel_bend_radius: float = 1500.0     # [m]  (design brief)
    exposure: str = "moderate"              # met-ocean exposure class
    channel_type: str = "two-way"           # one-way | two-way
    maneuver_aids: str = "thrusters"        # none | tugs | thrusters
    num_berths_total: int = 9               # across all terminals


@dataclass(frozen=True)
class BreakwaterInputs:
    """Rubble-mound trunk cross-section (Hudson design)."""
    crest_level: float = 7.0           # +m CD
    seabed_level: float = -15.0        # m CD (design depth at head)
    crest_width: float = 8.0           # [m]
    north_length: float = 1450.0       # [m] N (west) mole, longer (cf. Port Said)
    south_length: float = 950.0        # [m] S (east) mole, shorter
    seaward_slope: float = 2.0         # cot(alpha) seaward (2H:1V)
    leeward_slope: float = 1.5         # cot(alpha) leeward (1.5H:1V)
    armour_thickness: float = 4.0      # [m] (two layers of rock/units)
    filter_thickness: float = 2.0      # [m]
    toe_width: float = 6.0             # [m]
    toe_height: float = 3.0            # [m]
    # Hudson formula parameters (documented & annotated on the section).
    design_wave_h: float = 4.5         # Hs [m]
    rock_density: float = 2650.0       # kg/m3
    water_density: float = 1025.0      # kg/m3
    kd_stability: float = 4.0          # Kd, rough quarry-stone, trunk, breaking
    armour_slope_cot: float = 2.0      # cot(alpha) used in Hudson


@dataclass(frozen=True)
class TankFarm:
    count: int = 5
    diameter: float = 30.0             # [m]
    spacing_factor: float = 1.5        # centre spacing = factor·diameter (fire code)
    bund_clearance: float = 25.0       # [m] from tank group to bund wall


@dataclass(frozen=True)
class SiloField:
    count: int = 10
    diameter: float = 10.0             # [m]
    spacing_factor: float = 1.6        # centre spacing = factor·diameter
    rows: int = 2


# ----------------------------------------------------------------------------
# Derived layout (computed once, consumed everywhere)
# ----------------------------------------------------------------------------
@dataclass
class Layout:
    """
    Computed geometric anchors for the masterplan.

    Spatial story (looking in plan, +X = East, +Y = North):
        * Sea is to the WEST. The approach channel runs west->east on the
          harbour centreline and opens into the turning basin.
        * The quay line is a north-south wall on the west edge of the
          reclaimed land; terminals occupy parcels east of it.
        * Two rubble-mound breakwaters flank the channel mouth (North & South).
    """
    vessel: DesignVessel
    nav: NavigationInputs
    bw: BreakwaterInputs

    # Filled in __post_init__
    channel_cy: float = field(init=False)
    quay_line_x: float = field(init=False)
    basin_center: tuple[float, float] = field(init=False)
    basin_radius: float = field(init=False)
    channel_mouth_x: float = field(init=False)
    channel_inner_x: float = field(init=False)
    land_bounds: tuple[float, float, float, float] = field(init=False)  # x0,y0,x1,y1
    water_bounds: tuple[float, float, float, float] = field(init=False)
    site_bounds: tuple[float, float, float, float] = field(init=False)

    def __post_init__(self) -> None:
        # Harbour centreline latitude (north-south mid of the developed land).
        self.channel_cy = 1750.0

        # Quay wall: west edge of the reclaimed land (water to the west of it).
        self.quay_line_x = 400.0

        # Turning basin sits in the water immediately in front of the quays.
        self.basin_radius = self.nav.turning_basin_diameter / 2.0
        basin_clearance = 50.0
        basin_cx = self.quay_line_x - basin_clearance - self.basin_radius
        self.basin_center = (basin_cx, self.channel_cy)

        # Channel: from the west edge of the basin, 2000 m out to sea.
        self.channel_inner_x = basin_cx - self.basin_radius
        self.channel_mouth_x = self.channel_inner_x - self.nav.channel_length

        # Developed land block (parcels live here).
        self.land_bounds = (self.quay_line_x, 100.0, 4700.0, 3400.0)

        # Water area (harbour + approach + open-sea margin). The sea margin is
        # wide enough to hold the long Port-Said-style breakwater moles that
        # project seaward of the channel mouth.
        sea_margin = 1750.0
        self.water_bounds = (self.channel_mouth_x - sea_margin, 100.0,
                             self.quay_line_x, 3400.0)

        # Overall model extents (a little margin for breakwaters & details).
        self.site_bounds = (self.channel_mouth_x - sea_margin - 150.0, -300.0,
                            4900.0, 3700.0)


# ----------------------------------------------------------------------------
# Terminal / facility parcels (parametric bands referenced to the quay line)
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class Parcel:
    key: str
    name: str
    x: float
    y: float
    w: float
    h: float
    has_quay: bool = False
    berths: int = 0
    color: int = 8


def build_parcels(layout: Layout) -> list[Parcel]:
    """
    Derive every facility parcel from the quay line and standard band sizes.

    Waterfront terminals share the quay wall (west edge); inland facilities are
    placed east of them. All coordinates are derived -- change `quay_line_x`
    and the whole port slides with it.
    """
    qx = layout.quay_line_x
    wf_depth = 600.0          # waterfront parcel depth (inland) [m]
    inland_x = qx + wf_depth + 120.0  # start of the inland facility band

    parcels: list[Parcel] = [
        # --- waterfront terminals (front directly onto the quay wall) -------
        Parcel("CONTAINER", "CONTAINER TERMINAL",
               qx, 2350.0, wf_depth, 1050.0, has_quay=True, berths=3, color=30),
        Parcel("PASSENGER", "PASSENGER TERMINAL",
               qx, 1960.0, wf_depth, 360.0, has_quay=True, berths=1, color=150),
        Parcel("GEN_CARGO", "GENERAL CARGO WHARF",
               qx, 1470.0, wf_depth, 460.0, has_quay=True, berths=2, color=40),
        Parcel("RORO", "RO-RO BERTHS",
               qx, 1110.0, wf_depth, 330.0, has_quay=True, berths=1, color=90),
        Parcel("OIL", "OIL TERMINAL",
               qx, 300.0, wf_depth, 780.0, has_quay=True, berths=2, color=20),

        # --- inland facilities ---------------------------------------------
        Parcel("LIQUID_BULK", "LIQUID BULK TERMINAL (TANK FARM)",
               inland_x, 2550.0, 760.0, 850.0, color=20),
        Parcel("DRY_BULK", "DRY BULK TERMINAL (SILOS)",
               inland_x, 1650.0, 760.0, 760.0, color=40),
        Parcel("DRY_DOCK", "DRY DOCK",
               inland_x, 950.0, 420.0, 600.0, color=140),
        Parcel("REPAIR", "REPAIR YARD",
               inland_x + 480.0, 950.0, 280.0, 600.0, color=140),
        Parcel("ECOSYSTEM", "ECOSYSTEM ZONE / GREENSPACE",
               inland_x, 300.0, 760.0, 600.0, color=75),
        Parcel("EXPANSION", "FUTURE EXPANSION AREA",
               inland_x + 900.0, 300.0, 1180.0, 3100.0, color=251),
    ]
    return parcels


# ----------------------------------------------------------------------------
# Road / circulation network parameters
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class RoadInputs:
    primary_width: float = 24.0        # dual carriageway [m]
    secondary_width: float = 12.0      # [m]
    quay_apron_setback: float = 60.0   # apron behind the quay wall [m]
    roundabout_radius: float = 35.0    # [m]
    fence_setback: float = 40.0        # security fence inside land boundary [m]


# ----------------------------------------------------------------------------
# Drawing / annotation scale parameters
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class DrawStyle:
    text_title: float = 90.0
    text_label: float = 34.0
    text_small: float = 22.0
    dim_text: float = 40.0
    grid_spacing: float = 500.0        # coordinate grid interval [m]
    arrow_size: float = 30.0


# ----------------------------------------------------------------------------
# Fill palette (true-colour RGB) -- predictable, legible area tints.
# ----------------------------------------------------------------------------
PALETTE: dict[str, tuple[int, int, int]] = {
    "sea":        (179, 214, 234),   # light blue   - open sea
    "harbour":    (150, 196, 222),   # slightly deeper blue - inner basin
    "channel":    (120, 178, 212),   # dredged water
    "land":       (236, 226, 198),   # light sand   - reclaimed land
    "sand":       (222, 205, 158),   # sand spit / shoal
    "armour":     (120, 120, 124),   # breakwater armour stone (grey)
    "core":       (170, 170, 168),   # breakwater core
    "container":  (208, 226, 236),   # terminal yard tints (kept light)
    "passenger":  (224, 214, 236),
    "gen_cargo":  (228, 224, 198),
    "roro":       (210, 228, 214),
    "oil":        (236, 218, 206),
    "tank":       (236, 214, 200),
    "silo":       (226, 224, 200),
    "expansion":  (240, 238, 230),
    "ecosystem":  (180, 225, 180),
    "generic":    (224, 224, 224),
}


# ----------------------------------------------------------------------------
# Output paths
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class Paths:
    root: Path = Path(__file__).resolve().parent
    out_dir: Path = Path(__file__).resolve().parent / "output"

    @property
    def dxf(self) -> Path: return self.out_dir / "Suez_Port_Masterplan.dxf"
    @property
    def svg(self) -> Path: return self.out_dir / "Suez_Port_Masterplan.svg"
    @property
    def png(self) -> Path: return self.out_dir / "Suez_Port_Masterplan.png"
    @property
    def pdf(self) -> Path: return self.out_dir / "Suez_Port_Masterplan.pdf"
    @property
    def boq(self) -> Path: return self.out_dir / "Bill_of_Quantities.csv"
    @property
    def coords(self) -> Path: return self.out_dir / "Coordinates.csv"
    @property
    def report(self) -> Path: return self.out_dir / "Engineering_Report.md"
    @property
    def layer_report(self) -> Path: return self.out_dir / "Layer_Report.txt"


# ----------------------------------------------------------------------------
# Assembled configuration object
# ----------------------------------------------------------------------------
@dataclass
class Config:
    project: ProjectInfo = field(default_factory=ProjectInfo)
    vessel: DesignVessel = field(default_factory=DesignVessel)
    nav: NavigationInputs = field(default_factory=NavigationInputs)
    bw: BreakwaterInputs = field(default_factory=BreakwaterInputs)
    tanks: TankFarm = field(default_factory=TankFarm)
    silos: SiloField = field(default_factory=SiloField)
    roads: RoadInputs = field(default_factory=RoadInputs)
    style: DrawStyle = field(default_factory=DrawStyle)
    paths: Paths = field(default_factory=Paths)
    layout: Layout = field(init=False)
    parcels: list[Parcel] = field(init=False)

    def __post_init__(self) -> None:
        # Brief design values are PRESERVED exactly (channel width 224 m,
        # turning Ø 375 m). The calculation report documents how each is
        # supported by the course PIANC formulas (see calculations.py).
        self.layout = Layout(self.vessel, self.nav, self.bw)
        self.parcels = build_parcels(self.layout)

    # -- convenience derived engineering values ------------------------------
    @property
    def dredged_depth(self) -> float:
        """Approach-channel dredged depth below CD via the course formula
        D = T + UKC + S + Hw (Barrass II squat, PIANC UKC philosophy)."""
        import formulas
        return round(formulas.channel_depth(
            self.vessel.draft, self.vessel.cb, self.vessel.speed_kn,
            self.nav.exposure), 2)

    def parcel(self, key: str) -> Parcel:
        for p in self.parcels:
            if p.key == key:
                return p
        raise KeyError(f"No parcel with key {key!r}")


def hudson_armour_mass(bw: BreakwaterInputs) -> float:
    """Hudson median armour-unit mass W50 [tonnes] (single-source formula)."""
    import formulas
    w_kg = formulas.hudson_w50(bw.design_wave_h, bw.kd_stability,
                               bw.rock_density, bw.water_density,
                               bw.armour_slope_cot)
    return w_kg / 1000.0


# Module-level singleton used across the project.
CFG = Config()


if __name__ == "__main__":
    lay = CFG.layout
    print("Design vessel:", CFG.vessel)
    print("Basin center:", lay.basin_center, "R =", lay.basin_radius)
    print("Channel mouth x:", round(lay.channel_mouth_x, 1))
    print("Dredged depth:", CFG.dredged_depth, "m")
    print("Hudson W50:", round(hudson_armour_mass(CFG.bw), 2), "t")
    print("Parcels:", [p.key for p in CFG.parcels])

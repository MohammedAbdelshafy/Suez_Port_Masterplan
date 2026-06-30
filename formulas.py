"""
formulas.py
===========

Pure engineering formulas (no project imports, no side effects) implementing
the ECB 3802 course / PowerPoint method set. Both ``config`` and
``calculations`` import from here so that every number in the project -- CAD,
thesis, figures, reports -- derives from one place.

Method sources
--------------
* Ship squat ....... Barrass II:  S = Cb * V^2 / 100              [m]
* Net UKC .......... UKC = max(0.05*T, 0.5)                        [m]
* Channel depth .... D  = T + UKC + S + Hw                         [m]
* Berth pocket ..... Db = T + max(0.07*T, 0.5)                     [m]
* Channel width .... PIANC WG121 concept (one-way / two-way)       [m]
* Turning circle ... Dt = k * LOA                                  [m]
* Quay length ...... Lq = n*LOA + (n+1)*c , c = max(0.10*LOA, 15)  [m]
* Stopping dist. ... Ls ~= 7 * LOA                                 [m]
* Anchorage ........ R  = LOA + 6*D + 30 ; A = pi*R^2              [m, m^2]
* Breakwater armour. Hudson:  W50 = rho_s*H^3 / (Kd*(Sr-1)^3*cot a) [kg]

All inputs/outputs are SI (metres, knots for V as per Barrass II convention).
"""

from __future__ import annotations

import math

# Exposure width factor `a` (PIANC concept) and wave allowance Hw [m].
EXPOSURE_A = {"sheltered": 0.6, "moderate": 1.3, "exposed": 2.2}
EXPOSURE_HW = {"sheltered": 0.5, "moderate": 0.5, "exposed": 1.0}

# Turning-circle multiplier k by manoeuvre aid.
TURNING_K = {"none": 2.0, "tugs": 1.6, "thrusters": 1.5}

# Block coefficient Cb by vessel type (course table, PowerPoint slide 5).
BLOCK_COEFF = {
    "container": 0.65, "tanker": 0.82, "bulk": 0.85, "general": 0.70,
    "cruise": 0.62, "lng": 0.74, "roro": 0.68,
}


def ship_squat(cb: float, speed_kn: float) -> float:
    """Barrass II maximum bow squat in open/shallow water [m]."""
    return cb * speed_kn ** 2 / 100.0


def net_ukc(draft: float) -> float:
    """Net under-keel clearance (manoeuvrability + bottom margin) [m]."""
    return max(0.05 * draft, 0.5)


def channel_depth(draft: float, cb: float, speed_kn: float,
                  exposure: str = "moderate") -> float:
    """Approach-channel dredged depth D = T + UKC + S + Hw [m]."""
    return (draft + net_ukc(draft) + ship_squat(cb, speed_kn)
            + EXPOSURE_HW[exposure])


def berth_pocket_depth(draft: float) -> float:
    """Alongside berth pocket depth Db = T + max(0.07T, 0.5) [m]."""
    return draft + max(0.07 * draft, 0.5)


def channel_width_one_way(beam: float, exposure: str = "moderate") -> float:
    """PIANC one-way concept width: W = 1.5B + a*B + 2(0.5B) [m]."""
    a = EXPOSURE_A[exposure]
    return 1.5 * beam + a * beam + 2 * (0.5 * beam)


def channel_width_two_way(beam: float, exposure: str = "moderate") -> float:
    """PIANC two-way concept width: W = 2(1.5B)+2(aB)+1.6B+2(0.5B) [m]."""
    a = EXPOSURE_A[exposure]
    return 2 * (1.5 * beam) + 2 * (a * beam) + 1.6 * beam + 2 * (0.5 * beam)


def turning_circle(loa: float, aid: str = "thrusters") -> float:
    """Turning-circle diameter Dt = k * LOA [m]."""
    return TURNING_K[aid] * loa


def quay_length(num_berths: int, loa: float) -> float:
    """Total quay length Lq = n*LOA + (n+1)*c, c = max(0.10*LOA, 15) [m]."""
    c = max(0.10 * loa, 15.0)
    return num_berths * loa + (num_berths + 1) * c


def stopping_distance(loa: float) -> float:
    """Emergency stopping distance Ls ~= 7 * LOA [m]."""
    return 7.0 * loa


def anchorage_radius(loa: float, depth: float) -> float:
    """Single-point swing-mooring radius R = LOA + 6*D + 30 [m]."""
    return loa + 6.0 * depth + 30.0


def circle_area(radius: float) -> float:
    """Area of a circle [m^2]."""
    return math.pi * radius ** 2


def hudson_w50(hs: float, kd: float, rho_s: float, rho_w: float,
               cot_alpha: float) -> float:
    """Hudson median armour-unit mass W50 [kg].

        W50 = rho_s * Hs^3 / (Kd * (Sr - 1)^3 * cot(alpha))
    """
    sr = rho_s / rho_w
    return rho_s * hs ** 3 / (kd * (sr - 1.0) ** 3 * cot_alpha)

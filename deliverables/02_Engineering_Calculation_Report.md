# SUEZ PORT MASTERPLAN DESIGN — Engineering Calculation Report

**Coastal Structures Studio (CSS v1.0)** — Marine & Coastal Infrastructure.  
Student: Mohamed Abdelshafy (20107979) · Course: ECB 3802 · Supervisor: Dr. Walid Al-Amri.

> Single source of truth. Every value below is computed in `calculations.py` from the course PIANC / UNCTAD / Barrass method set and is reused verbatim by the CAD model, figures, thesis, presentation and posters via `canonical_values.json`. Concept level — not for construction.

## Design vessel (lecturer's notation)

| Lmax | bmax | dmax | Cb | V | DWT | Class |
|---|---|---|---|---|---|---|
| 250 m | 32 m | 12 m | 0.85 | 6 kn | 75,000 t | Panamax bulk carrier |

## Calculations

### C-1  Ship Squat (Barrass II)

**1. Objective.** Determine the dynamic bow sinkage of the design vessel under way to size the dredged depth.

**2. Engineering theory.** A moving ship in restricted water experiences a pressure drop that increases its mean draft (squat). Barrass II gives the maximum bow squat as a function of block coefficient and speed.

**3. Governing equation.**

$$ S = \frac{C_b \cdot V^2}{100} $$

**4. Variable definitions.**
- `C_b` = block coefficient (bulk = 0.85, course table)
- `V` = transit speed in the channel [kn]

**5. Units.** metres [m]

**6. Assumptions.**
- Design vessel is a Panamax bulk carrier (Cb = 0.85).
- Transit speed limited to V = 6 kn in the approach channel.
- Open-water Barrass II value taken as the design squat.

**7. Numerical substitution.**

$$ S = \frac{0.85 \cdot 6^2}{100} $$

**8. Intermediate calculations.**
- V² = 36
- Cb·V² = 30.60

**9. Final answer.**  **0.306 m**

**10. Engineering interpretation.** A squat of ~0.31 m is modest because the transit speed is deliberately restricted; squat grows with the square of speed.

**11. Design implication.** Adds directly to the required dredged depth of the channel.

### C-2  Net Under-Keel Clearance

**1. Objective.** Establish the manoeuvrability and bottom-safety margin beneath the keel.

**2. Engineering theory.** PIANC UKC philosophy provides a net clearance to cover manoeuvrability, survey/bottom uncertainty and squat that is not otherwise accounted for.

**3. Governing equation.**

$$ UKC = \max(0.05\,d_{max},\; 0.5) $$

**4. Variable definitions.**
- `d_{max}` = design vessel full-load draft [m]

**5. Units.** metres [m]

**6. Assumptions.**
- Soft/maintainable seabed; net UKC governed by 5% of draft.
- Minimum floor of 0.50 m applied for shallow-draft cases.

**7. Numerical substitution.**

$$ UKC = \max(0.05 \cdot 12,\; 0.5) = \max(0.60,\;0.5) $$

**8. Intermediate calculations.**
- 0.05·dmax = 0.60 m
- governing value = 0.60 m

**9. Final answer.**  **0.6 m**

**10. Engineering interpretation.** 0.60 m net clearance is retained beneath the keel at all states of manoeuvre.

**11. Design implication.** Second additive term of the dredged-depth build-up.

### C-3  Approach-Channel Dredged Depth

**1. Objective.** Compute the design dredge level of the approach channel below Chart Datum.

**2. Engineering theory.** The dredged depth stacks the static draft, the net UKC, the dynamic squat and a wave-response allowance set by met-ocean exposure.

**3. Governing equation.**

$$ D = d_{max} + UKC + S + H_w $$

**4. Variable definitions.**
- `d_{max}` = draft [m]
- `UKC` = net under-keel clearance [m]
- `S` = Barrass squat [m]
- `H_w` = wave allowance (moderate) [m]

**5. Units.** metres [m]

**6. Assumptions.**
- Moderate exposure on the seaward approach → Hw = 0.5 m.
- Tidal window not relied upon (depth referenced to Chart Datum).

**7. Numerical substitution.**

$$ D = 12 + 0.60 + 0.31 + 0.5 $$

**8. Intermediate calculations.**
- sum = 13.41 m

**9. Final answer.**  **13.41 m (below CD)**

**10. Engineering interpretation.** A dredged depth of ~13.4 m comfortably accommodates the 12.0 m design draft with all dynamic allowances.

**11. Design implication.** Sets the dredging volume and the channel/basin design level (adopt practical dredge level −13.5 m CD).

### C-4  Berth-Pocket Depth

**1. Objective.** Size the dredged depth alongside the quay where the vessel is effectively stationary.

**2. Engineering theory.** At berth the squat term collapses; PIANC retains a reduced-speed allowance of 7% of draft (floor 0.5 m).

**3. Governing equation.**

$$ D_b = d_{max} + \max(0.07\,d_{max},\;0.5) $$

**4. Variable definitions.**
- `d_{max}` = draft [m]

**5. Units.** metres [m]

**6. Assumptions.**
- Negligible squat alongside (reduced-speed manoeuvre).
- Allowance governed by 7% of draft.

**7. Numerical substitution.**

$$ D_b = 12 + \max(0.07 \cdot 12,\;0.5) $$

**8. Intermediate calculations.**
- 0.07·dmax = 0.84 m
- governing = 0.84 m

**9. Final answer.**  **12.84 m (below CD)**

**10. Engineering interpretation.** Berth pockets are ~0.6 m shallower than the channel, reflecting the absence of squat alongside.

**11. Design implication.** Governs quay-wall toe level and alongside dredging.

### C-5  Approach-Channel Width (PIANC two-way)

**1. Objective.** Determine the navigable width of the two-way approach channel.

**2. Engineering theory.** PIANC WG121 builds the width from two manoeuvring lanes (1.5B each), an exposure-dependent additional width (a·B per lane), a passing distance (1.6B) and two bank clearances (0.5B each).

**3. Governing equation.**

$$ W = 2(1.5b_{max}) + 2(a\,b_{max}) + 1.6\,b_{max} + 2(0.5b_{max}) $$

**4. Variable definitions.**
- `b_{max}` = beam [m]
- `a` = exposure factor (sheltered 0.6 / moderate 1.3)

**5. Units.** metres [m]

**6. Assumptions.**
- Two-way traffic adopted (consistent with the project brief).
- The entrance reach is protected by the twin breakwaters → the sheltered factor a = 0.6 governs the inner channel.
- Adopted width 224 m (= 7·bmax) exceeds the sheltered requirement, giving margin toward the moderate-exposure value.

**7. Numerical substitution.**

$$ W_{shelt} = b_{max}(5.6 + 2\cdot0.6) = 32.0\cdot6.8 $$

**8. Intermediate calculations.**
- sheltered (a=0.6): W = 217.6 m
- moderate (a=1.3): W = 262.4 m
- adopted design width = 224.0 m (= 7·bmax, brief value)

**9. Final answer.**  **224 m**

**10. Engineering interpretation.** The adopted 224 m lies between the sheltered (217.6 m) requirement and the moderate-exposure envelope (262.4 m), a defensible concept width for a breakwater-protected canal entrance.

**11. Design implication.** Fixes the dredged channel footprint and the breakwater entrance gap.

### C-6  Turning-Basin Diameter & Area

**1. Objective.** Size the turning basin that lets the design vessel reverse heading.

**2. Engineering theory.** Concept practice sets the turning-circle diameter as a multiple k of LOA; with bow/stern thrusters (or strong tug assistance) k = 1.5.

**3. Governing equation.**

$$ D_t = k \cdot L_{max}\;;\quad A = \pi (D_t/2)^2 $$

**4. Variable definitions.**
- `k` = manoeuvre-aid factor (thrusters = 1.5)
- `L_{max}` = length overall [m]

**5. Units.** metres / hectares

**6. Assumptions.**
- Tug- and thruster-assisted turning (k = 1.5).
- Basin centred in front of the quays within sheltered water.

**7. Numerical substitution.**

$$ D_t = 1.5 \cdot 250 = 375\,\text{m};\;A = \pi(187.5)^2 $$

**8. Intermediate calculations.**
- Dt = 375.0 m (matches brief Ø375)
- radius = 187.5 m
- area = 110,447 m² = 11.04 ha

**9. Final answer.**  **375 m (Ø)**

**10. Engineering interpretation.** A 375 m basin (1.5·Lmax) is adequate for assisted turning of the Panamax design vessel.

**11. Design implication.** Defines the dredged turning-basin footprint and its 11.04 ha water area.

### C-7  Quay Length (container terminal, 3 berths)

**1. Objective.** Determine the continuous quay length for the governing container terminal.

**2. Engineering theory.** Total quay length sums one LOA per berth plus an inter-berth / end clearance c on each side; c = max(0.10·LOA, 15 m).

**3. Governing equation.**

$$ L_q = n\,L_{max} + (n+1)\,c,\quad c=\max(0.10L_{max},15) $$

**4. Variable definitions.**
- `n` = number of berths
- `c` = clearance per gap [m]

**5. Units.** metres [m]

**6. Assumptions.**
- Container terminal sized for n = 3 contiguous berths.
- Clearance c = 0.10·250 = 25 m (> 15 m floor).

**7. Numerical substitution.**

$$ L_q = 3 \cdot 250 + 4 \cdot 25 $$

**8. Intermediate calculations.**
- berths = 3·250 = 750 m
- clearances = 4·25 = 100 m
- Lq = 850 m

**9. Final answer.**  **850 m**

**10. Engineering interpretation.** 850 m of quay supports three Panamax berths with working clearances.

**11. Design implication.** Sets the container quay footprint; the same formula sizes every other terminal (total ≈ 2,600 m over 9 berths).

### C-8  Emergency Stopping Distance

**1. Objective.** Estimate the crash-stop distance used to set the approach reach and anchorage offset.

**2. Engineering theory.** For a loaded vessel performing an emergency astern manoeuvre the stopping distance is of the order of seven ship lengths.

**3. Governing equation.**

$$ L_s \approx 7 \cdot L_{max} $$

**4. Variable definitions.**
- `L_{max}` = length overall [m]

**5. Units.** metres [m]

**6. Assumptions.**
- Loaded condition, full astern (concept envelope).

**7. Numerical substitution.**

$$ L_s = 7 \cdot 250 $$

**8. Intermediate calculations.**
- Ls = 1750 m

**9. Final answer.**  **1750 m**

**10. Engineering interpretation.** ≈1,750 m of clear water is needed ahead of a stopping vessel.

**11. Design implication.** Confirms the 2,000 m approach-channel length provides adequate stopping room.

### C-9  Anchorage Swing Radius & Area

**1. Objective.** Size the offshore waiting anchorage for a single swinging vessel.

**2. Engineering theory.** A single-point swing mooring sweeps a circle whose radius adds the ship length, a scope allowance (≈6·water depth) and a 30 m safety margin.

**3. Governing equation.**

$$ R = L_{max} + 6D + 30\;;\quad A = \pi R^2 $$

**4. Variable definitions.**
- `D` = water depth at anchorage [m]

**5. Units.** metres / hectares

**6. Assumptions.**
- Single-point swing mooring; water depth ≈ channel depth D.
- Scope factor 6·D for the mooring chain.

**7. Numerical substitution.**

$$ R = 250 + 6 \cdot 13.41 + 30 $$

**8. Intermediate calculations.**
- 6·D = 80.44 m
- R = 360.4 m
- A = 408,137 m² = 40.81 ha

**9. Final answer.**  **360.4 m (R)**

**10. Engineering interpretation.** Each waiting vessel requires a ~360 m radius swing circle (≈40.8 ha).

**11. Design implication.** Reserves the offshore anchorage water area in the masterplan.

### C-10  Breakwater Armour (Hudson)

**1. Objective.** Size the primary rock armour of the rubble-mound breakwaters.

**2. Engineering theory.** The Hudson formula gives the median armour-unit mass required for stability under design wave attack, as a function of wave height, stability coefficient, relative density and slope.

**3. Governing equation.**

$$ W_{50} = \frac{\rho_s\,H_s^3}{K_d\,(S_r-1)^3\,\cot\alpha} $$

**4. Variable definitions.**
- `H_s` = design significant wave height [m]
- `K_d` = stability coefficient (rough quarry stone, trunk)
- `S_r` = relative density ρs/ρw
- `\cot\alpha` = armour slope

**5. Units.** tonnes [t]

**6. Assumptions.**
- Hs = 4.5 m, Kd = 4.0 (trunk, breaking, rough rock).
- ρs = 2650, ρw = 1025 kg/m³ → Sr = 2.585.
- Seaward slope cot α = 2.0 (2H:1V).

**7. Numerical substitution.**

$$ W_{50} = \frac{2650\cdot4.5^3}{4\cdot(2.585-1)^3\cdot2.0} $$

**8. Intermediate calculations.**
- Hs³ = 91.12
- (Sr−1)³ = 3.985
- W50 = 7,575 kg = 7.58 t

**9. Final answer.**  **7.58 t**

**10. Engineering interpretation.** A ~7.6 t median armour rock is required on the seaward slope; two layers give the armour thickness used in the cross-section.

**11. Design implication.** Defines the breakwater armour grading, layer thickness and quarry requirement (Bill of Quantities).

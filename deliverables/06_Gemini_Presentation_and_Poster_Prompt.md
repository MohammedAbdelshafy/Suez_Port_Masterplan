# Gemini Prompt — Suez Port Masterplan Presentation & Posters

Hand this file to **Gemini** to generate the 15-slide PowerPoint and two A0
posters. All numbers below are the **validated, locked** values from
`canonical_values.json` (Coastal Structures Studio, CSS v1.0). **Do not change
any value.** Use lecturer notation **Lmax / bmax / dmax**. Never use the term
"SmartPort AI" — the platform is **Coastal Structures Studio (CSS v1.0)**.

---

## PROMPT (copy everything below into Gemini)

You are a senior presentation and engineering-graphics designer. Produce a
**15-slide PowerPoint (16:9)** and **two A0 posters (portrait, 841 × 1189 mm)**
for a marine-engineering graduation project. Style: clean, modern, technical;
deep-teal / navy on white with a single accent (#0B6E8F); generous white space;
consistent iconography; readable from the back of a room (titles ≥ 32 pt, body
≥ 18 pt). Visuals over text. Reuse the engineering figures provided
(`fig1_channel_section`, `fig2_depth_buildup`, `fig3_width_buildup`,
`fig4_breakwater_section`, `fig5_key_plan`) and the CAD A1 sheet render
(`Suez_Port_Masterplan.png`).

**Identity (every footer):** Coastal Structures Studio (CSS v1.0) · Suez Port
Masterplan Design · ECB 3802.
**Title-block facts:** Student **Mohamed Abdelshafy** (ID **20107979**);
Supervisor **Dr. Walid Al-Amri**; Arab Academy for Science, Technology &
Maritime Transport — Smart Village; Year **2026**.

**LOCKED ENGINEERING VALUES — reproduce exactly, do not recompute:**
- Design vessel (Panamax bulk carrier): **Lmax 250 m · bmax 32 m · dmax 12 m ·
  Cb 0.85 · V 6 kn · DWT 75 000 t**.
- Approach channel: length **2 000 m**, width **224 m**, depth **13.41 m**
  (dredge level −13.5 m CD), bend radius **1 500 m**.
- Depth build-up: D = dmax + UKC + S + Hw = 12 + 0.60 + 0.31 + 0.50 = **13.41 m**.
- Berth-pocket depth **12.84 m**.
- Turning basin: Ø **375 m** (= 1.5·Lmax), area **11.04 ha**.
- Emergency stopping distance **1 750 m** (≈ 7·Lmax).
- Anchorage: swing radius **360.5 m**, area **40.82 ha**.
- Terminals (9 berths, ≈ 2 600 m quay): container 3 berths / **850 m**,
  general cargo **575 m**, oil **575 m**, passenger **300 m**, ro-ro **300 m**;
  liquid-bulk tank farm **5 × Ø30 m @ 45 m c/c** (bunded); dry-bulk silos
  **10 × Ø10 m**; graving dry dock + repair yard; reserved expansion parcel.
- Breakwaters: twin rubble-mound moles **North 1 450 m / South 950 m**, crest
  **+7.0 m CD**, design wave **Hs 4.5 m**, Hudson armour **W50 ≈ 7.6 t**.
- Key formulas: S = Cb·V²/100 · UKC = max(0.05·dmax, 0.5) · D = dmax+UKC+S+Hw ·
  PIANC two-way width · Dt = k·Lmax (k=1.5) · Lq = n·Lmax+(n+1)c · Ls ≈ 7·Lmax ·
  R = Lmax+6D+30 · Hudson W50 = ρs·Hs³ / (Kd·(Sr−1)³·cotα).

**15-slide outline (one idea per slide):**
1. **Title** — Suez Port Masterplan Design; student, ID, supervisor, academy,
   2026; CSS v1.0.
2. **Outline / agenda** — the 10 themes.
3. **Introduction** — Suez corridor ~12% of global trade; ports must fit the
   largest design vessel; concept dimensioning is repetitive → a standards-based
   engine that also produces CAD.
4. **Objectives** — define design vessel; apply PIANC/UNCTAD/Barrass; auto-CAD
   masterplan; one source of truth (numbers → geometry → drawing).
5. **The design vessel** — Lmax/bmax/dmax = 250/32/12, Cb 0.85, V 6 kn, Panamax
   bulk; small hull diagram.
6. **Theoretical basis** — PIANC WG121, UNCTAD, Barrass II squat, UKC
   philosophy, Hudson (breakwater).
7. **Formulas 1 — depth & squat** — S, UKC, D, Db; use `fig2_depth_buildup`.
8. **Formulas 2 — channel width** — PIANC two-way build-up; use
   `fig3_width_buildup`; adopted 224 m.
9. **Formulas 3 — turning, quay, stopping, anchorage** — Dt=1.5·Lmax, Lq, Ls,
   R.
10. **Method & tooling** — single source of truth (`formulas.py` →
    `calculations.py` → `canonical_values.json` → CAD/figures/thesis); QA gate.
11. **The masterplan** — show the CAD A1 sheet (`Suez_Port_Masterplan.png`);
    callouts to channel, basin, breakwaters, terminals.
12. **Worked results table** — the locked values above as a clean table.
13. **Breakwaters & cross-section** — `fig4_breakwater_section`; Hudson W50
    7.6 t; twin moles 1 450 / 950 m.
14. **Validation & limitations** — concept level; confirm by manoeuvring
    simulation + met-ocean/bathymetric/geotechnical surveys; engineer-in-loop.
15. **Conclusion & future work** — standards-based, fully consistent package;
    future: simulation, morphology modelling, structural design, 3D/BIM.

**Two A0 posters (portrait):**
- **Poster 1 — "Design & Methodology":** title strip; design-vessel panel;
  formula set with the worked depth build-up (`fig1`/`fig2`); PIANC width
  (`fig3`); a clean results table; CSS v1.0 + academy branding; QR/footer.
- **Poster 2 — "The Masterplan":** large CAD A1 render
  (`Suez_Port_Masterplan.png`) as hero; key-plan (`fig5`); breakwater section
  (`fig4`); terminal program table; environmental buffer note; footer.

**Rules:** keep every number identical to the locked list; use Lmax/bmax/dmax;
keep units (m, ha, t, kn); mark everything "Concept design — not for
construction"; CSS v1.0 branding throughout; do not invent values not given
here.

---

## Asset checklist to attach when prompting Gemini
- `deliverables/figures/fig1_channel_section.png` … `fig5_key_plan.png`
- `output/Suez_Port_Masterplan.png` (CAD A1 sheet)
- `deliverables/canonical_values.json` (for exact numbers)
- `deliverables/02_Engineering_Calculation_Report.md` (for formula wording)

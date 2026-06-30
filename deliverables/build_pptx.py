"""
Build SUEZ_Port_Presentation.pptx — 15-slide professional engineering presentation
Navy & Brushed Gold theme, engineering-first storytelling.
Run with: C:\\Users\\omare\\AppData\\Local\\Programs\\Python\\Python312\\python.exe build_pptx.py
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import os, copy

# ── Color palette ─────────────────────────────────────────────────────────────
NAVY       = RGBColor(0x0B, 0x1E, 0x3C)
NAVY_MID   = RGBColor(0x14, 0x28, 0x47)
GOLD       = RGBColor(0xC9, 0xA8, 0x4C)
GOLD_LIGHT = RGBColor(0xE8, 0xD0, 0x90)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
OFFWHITE   = RGBColor(0xF7, 0xF8, 0xFA)
PASS_GRN   = RGBColor(0x16, 0xA3, 0x4A)
FAIL_RED   = RGBColor(0xDC, 0x26, 0x26)
LIGHT_GRAY = RGBColor(0xD1, 0xD9, 0xE6)

# ── Validated engineering constants ────────────────────────────────────────────
ENG = {
    "Lmax": "250 m", "bmax": "32 m", "dmax": "12 m",
    "ch_width": "224 m (7.0 × bmax)",
    "ch_depth": "−13.4 m CD",
    "ch_length": "2,000 m",
    "tb_diam": "375 m (1.50 × Lmax)",
    "bend_r": "1,500 m (6.0 × Lmax)",
    "W50": "7.6 t",
    "Hs": "4.5 m",
    "KD": "4.0",
    "crest": "+7.0 m CD",
    "north_mole": "1,450 m",
    "south_mole": "950 m",
    "gap": "314 m",
    "area": "2,933,984 m²",
}

# ── Presentation setup ─────────────────────────────────────────────────────────
prs = Presentation()
prs.slide_width  = Inches(13.33)   # 16:9 widescreen
prs.slide_height = Inches(7.5)

W = prs.slide_width
H = prs.slide_height

def add_rect(slide, l, t, w, h, fill_rgb=None, line_rgb=None, line_w=Pt(0)):
    from pptx.util import Pt
    shape = slide.shapes.add_shape(1, l, t, w, h)  # MSO_SHAPE_TYPE.RECTANGLE = 1
    if fill_rgb:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_rgb
    else:
        shape.fill.background()
    if line_rgb:
        shape.line.color.rgb = line_rgb
        shape.line.width = line_w
    else:
        shape.line.fill.background()
    return shape

def add_text(slide, text, l, t, w, h, size=Pt(18), bold=False, color=WHITE,
             align=PP_ALIGN.LEFT, wrap=True, italic=False, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(l, t, w, h)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    tf.auto_size = None
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = size
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = font_name
    return txBox

def navy_slide(prs, title_text, subtitle_text=""):
    """Full navy background with gold bar title slide layout."""
    layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(layout)

    # Background
    bg = add_rect(slide, 0, 0, W, H, NAVY)

    # Gold accent bar — left vertical
    add_rect(slide, 0, 0, Inches(0.18), H, GOLD)

    # Title bar block
    add_rect(slide, Inches(0.4), Inches(0.28), W - Inches(0.6), Inches(1.1), NAVY_MID)

    # Title text
    add_text(slide, title_text,
             l=Inches(0.7), t=Inches(0.33), w=W - Inches(1.2), h=Inches(0.9),
             size=Pt(34), bold=True, color=WHITE, align=PP_ALIGN.LEFT)

    # Gold rule under title
    add_rect(slide, Inches(0.4), Inches(1.32), Inches(2.5), Inches(0.04), GOLD)

    if subtitle_text:
        add_text(slide, subtitle_text,
                 l=Inches(0.7), t=Inches(1.4), w=W - Inches(1.2), h=Inches(0.4),
                 size=Pt(14), bold=False, color=GOLD_LIGHT, align=PP_ALIGN.LEFT)

    return slide

def add_footer(slide, text="Suez Port Masterplan Design  |  Mohamed Abdelshafy (20107979)  |  ECB3802  |  Supervisor: Dr. Walid Al-Amri"):
    """Add consistent footer to every slide."""
    add_rect(slide, 0, H - Inches(0.38), W, Inches(0.38), NAVY_MID)
    add_text(slide, text,
             l=Inches(0.3), t=H - Inches(0.36), w=W - Inches(0.6), h=Inches(0.32),
             size=Pt(9), color=GOLD_LIGHT, align=PP_ALIGN.CENTER)

def add_kpi_box(slide, label, value, l, t, w=Inches(2.4), h=Inches(1.2)):
    """Gold-bordered KPI box."""
    add_rect(slide, l, t, w, h, NAVY_MID, GOLD, Pt(2))
    add_text(slide, value, l, t + Inches(0.1), w, h * 0.55,
             size=Pt(26), bold=True, color=GOLD, align=PP_ALIGN.CENTER)
    add_text(slide, label, l, t + h * 0.55, w, h * 0.4,
             size=Pt(10), bold=False, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)

def add_bullet(slide, bullets, l, t, w, h, size=Pt(15), heading=None):
    """Add a bullet list. bullets is a list of (text, is_sub) tuples."""
    txBox = slide.shapes.add_textbox(l, t, w, h)
    tf = txBox.text_frame
    tf.word_wrap = True
    if heading:
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = heading
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = GOLD
        run.font.name = "Calibri"
    for i, (btext, is_sub) in enumerate(bullets):
        if heading or i > 0:
            p = tf.add_paragraph()
        else:
            p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        p.level = 1 if is_sub else 0
        run = p.add_run()
        run.text = ("    " if is_sub else "■  ") + btext
        run.font.size = Pt(11) if is_sub else size
        run.font.color.rgb = LIGHT_GRAY if is_sub else WHITE
        run.font.name = "Calibri"

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — COVER
# ══════════════════════════════════════════════════════════════════════════════
layout = prs.slide_layouts[6]
slide = prs.slides.add_slide(layout)
add_rect(slide, 0, 0, W, H, NAVY)
# Left accent
add_rect(slide, 0, 0, Inches(0.22), H, GOLD)
# Right decorative panel
add_rect(slide, W - Inches(3.2), 0, Inches(3.2), H, NAVY_MID)
add_rect(slide, W - Inches(3.2), 0, Inches(0.04), H, GOLD)

# Institution
add_text(slide, "ARAB ACADEMY FOR SCIENCE, TECHNOLOGY & MARITIME TRANSPORT",
         Inches(0.5), Inches(0.5), Inches(8.5), Inches(0.5),
         size=Pt(12), color=GOLD_LIGHT, bold=True)

# Main title
add_text(slide, "SUEZ PORT",
         Inches(0.5), Inches(1.2), Inches(9), Inches(1.4),
         size=Pt(60), bold=True, color=WHITE)
add_text(slide, "MASTERPLAN DESIGN",
         Inches(0.5), Inches(2.4), Inches(9), Inches(1.1),
         size=Pt(40), bold=True, color=GOLD)

# Gold rule
add_rect(slide, Inches(0.5), Inches(3.55), Inches(2.5), Inches(0.06), GOLD)

# Subtitle
add_text(slide, "Navigation Channel  ·  Turning Basin  ·  Breakwater  ·  Terminal Layout",
         Inches(0.5), Inches(3.75), Inches(9), Inches(0.5),
         size=Pt(16), color=LIGHT_GRAY)

# Meta
meta = [
    ("Student:", "Mohamed Abdelshafy"),
    ("Student ID:", "20107979"),
    ("Supervisor:", "Dr. Walid Al-Amri"),
    ("Course:", "ECB 3802"),
    ("Date:", "June 2026"),
]
for i, (lbl, val) in enumerate(meta):
    y = Inches(4.5) + i * Inches(0.45)
    add_text(slide, lbl, Inches(0.5), y, Inches(1.4), Inches(0.4),
             size=Pt(11), color=GOLD, bold=True)
    add_text(slide, val, Inches(1.85), y, Inches(3.5), Inches(0.4),
             size=Pt(11), color=WHITE)

# Right panel content
add_text(slide, "GRADUATION\nPROJECT I",
         W - Inches(3.0), Inches(2.5), Inches(2.8), Inches(1.2),
         size=Pt(16), bold=True, color=GOLD, align=PP_ALIGN.CENTER)
add_text(slide, "Smart Village Campus",
         W - Inches(3.0), Inches(4.2), Inches(2.8), Inches(0.5),
         size=Pt(10), color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
add_text(slide, "Coastal Structures Studio\nCSS v1.0",
         W - Inches(3.0), Inches(5.2), Inches(2.8), Inches(0.8),
         size=Pt(9), color=GOLD, align=PP_ALIGN.CENTER)

slide.notes_slide.notes_text_frame.text = (
    "Welcome everyone. This is the Suez Port Masterplan Design, a graduation project submitted "
    "for Course ECB 3802 at the Arab Academy for Science, Technology and Maritime Transport. "
    "The project delivers a full concept-level engineering design for a new deep-water commercial "
    "port at Suez, developed using rigorous PIANC guidelines and the Hudson formula for breakwater design."
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — OBJECTIVES
# ══════════════════════════════════════════════════════════════════════════════
slide = navy_slide(prs, "Project Objectives", "What this project delivers")
add_footer(slide)
objectives = [
    ("Design a deep-water port masterplan at Suez compliant with PIANC guidelines.", False),
    ("Determine navigation geometry from a governing Panamax-class design vessel.", False),
    ("Size a rubble-mound breakwater using the Hudson armour formula.", False),
    ("Layout three cargo terminals: Liquid Bulk, Dry Bulk, General Cargo.", False),
    ("Produce a complete AutoCAD masterplan drawing (SPM-001 Rev A).", False),
    ("Generate engineering calculations, QA validation, and full report.", False),
]
add_bullet(slide, objectives, Inches(0.7), Inches(2.0), Inches(8.5), Inches(4.8), size=Pt(17))
# KPIs
add_kpi_box(slide, "Design Vessel (LOA)", "250 m", Inches(9.3), Inches(2.2))
add_kpi_box(slide, "Breakwater Arm. W₅₀", "7.6 t", Inches(9.3), Inches(3.55))
add_kpi_box(slide, "Turning Basin Ø", "375 m", Inches(9.3), Inches(4.9))
slide.notes_slide.notes_text_frame.text = (
    "The project has six clear engineering objectives. All geometry derives from the design vessel. "
    "The three KPIs on the right — LOA, armour mass, and basin diameter — are the headline numbers "
    "the examiners will focus on. Know these cold."
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — SITE LOCATION
# ══════════════════════════════════════════════════════════════════════════════
slide = navy_slide(prs, "Site Location", "Gulf of Suez, Egypt — Strategic Southern Gateway to the Suez Canal")
add_footer(slide)
# Image placeholder
add_rect(slide, Inches(0.5), Inches(1.85), Inches(8.0), Inches(5.2), NAVY_MID, GOLD, Pt(1))
add_text(slide, "[ GOOGLE EARTH — Site Overview ]\nSuez, Egypt | Gulf of Suez\n(Insert high-res satellite image)",
         Inches(0.5), Inches(3.5), Inches(8.0), Inches(1.5),
         size=Pt(14), color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
# Site facts
facts = [
    "Coordinate System: Local grid (E=+X, N=+Y)",
    "Datum: Chart Datum (CD)",
    "Total Site Area: 2,933,984 m²",
    "Water: Gulf of Suez (west)",
    "Tidal Range: ≈ 0.4 m (microtidal)",
]
for i, f in enumerate(facts):
    add_text(slide, "■  " + f,
             Inches(8.75), Inches(2.0) + i * Inches(0.6), Inches(4.2), Inches(0.5),
             size=Pt(12), color=WHITE)
slide.notes_slide.notes_text_frame.text = (
    "The site is on the western shore of the Gulf of Suez, positioned at the southern approach to the "
    "Suez Canal. The strategic location provides direct access to major Red Sea and Mediterranean trade routes. "
    "Point out the site boundary on the Google Earth image. Note the microtidal environment — tidal range "
    "only 0.4 m — which simplifies the dredged depth calculation."
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — EXISTING CONDITIONS
# ══════════════════════════════════════════════════════════════════════════════
slide = navy_slide(prs, "Existing Conditions", "Site baseline assessment — undeveloped coastal land")
add_footer(slide)
add_rect(slide, Inches(0.5), Inches(1.85), Inches(5.8), Inches(5.2), NAVY_MID, GOLD, Pt(1))
add_text(slide, "[ SATELLITE / AERIAL — Existing Site ]\n(Insert before-development image)",
         Inches(0.5), Inches(4.0), Inches(5.8), Inches(1.0),
         size=Pt(12), color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
conditions = [
    ("Undeveloped coastal land — no existing maritime infrastructure", False),
    ("Gentle nearshore bathymetric gradient", False),
    ("Prevailing NNW winds 5–15 m/s (fetch-limited Gulf)", False),
    ("50-yr significant wave height: Hs = 4.5 m", False),
    ("MHW ≈ +0.2 m CD, LAT at datum", False),
    ("Regional geology: medium-dense carbonate sands", False),
    ("No conflicts with Suez Canal transit corridor", False),
]
add_bullet(slide, conditions, Inches(6.7), Inches(1.9), Inches(6.3), Inches(5.0), size=Pt(14))
slide.notes_slide.notes_text_frame.text = (
    "The existing site is greenfield — no current port infrastructure. Key environmental input: "
    "the 50-year significant wave height of 4.5 m which directly drives the breakwater armour calculation. "
    "The microtidal environment means tidal variation is negligible for dredging purposes."
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — DESIGN VESSEL
# ══════════════════════════════════════════════════════════════════════════════
slide = navy_slide(prs, "Design Vessel", "Panamax-Class Bulk Carrier / Tanker — Governing All Geometry")
add_footer(slide)
# Vessel diagram placeholder
add_rect(slide, Inches(0.5), Inches(1.85), Inches(7.5), Inches(3.5), NAVY_MID, GOLD, Pt(2))
add_text(slide, "[ DESIGN VESSEL — Three-View Engineering Diagram ]\nLmax = 250 m  |  bmax = 32 m  |  dmax = 12 m",
         Inches(0.5), Inches(2.9), Inches(7.5), Inches(1.0),
         size=Pt(14), color=GOLD, align=PP_ALIGN.CENTER, bold=True)
# Dimension callouts
add_text(slide, "← Lmax = 250 m →",
         Inches(0.5), Inches(5.55), Inches(7.5), Inches(0.4),
         size=Pt(12), color=GOLD_LIGHT, align=PP_ALIGN.CENTER)
# Parameter table
add_rect(slide, Inches(8.3), Inches(1.85), Inches(4.7), Inches(3.5), NAVY_MID, GOLD, Pt(1))
params = [
    ("Parameter", "Symbol", "Value"),
    ("Max Length Overall", "Lmax", "250 m"),
    ("Max Beam", "bmax", "32 m"),
    ("Max Draft", "dmax", "12 m"),
]
for i, (p, s, v) in enumerate(params):
    y = Inches(2.0) + i * Inches(0.72)
    bg = NAVY if i == 0 else (NAVY_MID if i % 2 == 0 else RGBColor(0x1A, 0x38, 0x5F))
    add_rect(slide, Inches(8.35), y, Inches(4.6), Inches(0.65), bg)
    add_text(slide, p, Inches(8.45), y + Inches(0.12), Inches(2.0), Inches(0.45),
             size=Pt(11), color=GOLD if i == 0 else WHITE, bold=(i == 0))
    add_text(slide, s, Inches(10.3), y + Inches(0.12), Inches(1.0), Inches(0.45),
             size=Pt(11), color=GOLD if i == 0 else GOLD_LIGHT, bold=False)
    add_text(slide, v, Inches(11.2), y + Inches(0.12), Inches(1.6), Inches(0.45),
             size=Pt(13), color=GOLD if i > 0 else WHITE, bold=(i > 0))
# Bottom note
add_text(slide, "All navigation geometry, berth lengths, and basin dimensions are derived from Lmax, bmax, and dmax.",
         Inches(0.5), Inches(6.9), Inches(12.5), Inches(0.45),
         size=Pt(11), color=GOLD_LIGHT, italic=True)
slide.notes_slide.notes_text_frame.text = (
    "The design vessel is the foundation of everything. Every dimension on the masterplan traces back to "
    "Lmax = 250 m, bmax = 32 m, and dmax = 12 m. When an examiner asks 'why is the channel 224 m wide?', "
    "the answer is: 7.0 × bmax = 7.0 × 32 = 224 m — PIANC compliant. Always come back to these three numbers."
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — NAVIGATION CHANNEL
# ══════════════════════════════════════════════════════════════════════════════
slide = navy_slide(prs, "Navigation Channel Design", "PIANC-Compliant One-Way Channel Geometry")
add_footer(slide)
# Channel diagram placeholder
add_rect(slide, Inches(0.5), Inches(1.85), Inches(6.0), Inches(5.2), NAVY_MID, GOLD, Pt(2))
add_text(slide, "[ NAVIGATION CHANNEL — Plan View CAD ]\nChannel + Turning Basin Layout",
         Inches(0.5), Inches(4.0), Inches(6.0), Inches(0.8),
         size=Pt(12), color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
# Results table
ch_data = [
    ("Parameter", "Value", "Standard"),
    ("Channel Length", "2,000 m", "Layout"),
    ("Channel Width", "224 m = 7.0 × bmax", "PIANC 2014"),
    ("Dredged Depth", "−13.4 m CD", "UKC Method"),
    ("Under-Keel Clearance", "15% of dmax = 1.8 m", "PIANC 2014"),
    ("Bend Radius", "1,500 m = 6.0 × Lmax", "PIANC 2014"),
]
for i, row in enumerate(ch_data):
    y = Inches(1.9) + i * Inches(0.75)
    bg = NAVY if i == 0 else (NAVY_MID if i % 2 == 0 else RGBColor(0x1A, 0x38, 0x5F))
    add_rect(slide, Inches(6.8), y, Inches(6.2), Inches(0.7), bg)
    cols = [Inches(6.9), Inches(9.1), Inches(11.3)]
    widths = [Inches(2.1), Inches(2.1), Inches(1.5)]
    for j, (col, wid) in enumerate(zip(cols, widths)):
        clr = GOLD if i == 0 else (GOLD if j == 1 and i > 0 else WHITE)
        add_text(slide, row[j], col, y + Inches(0.1), wid, Inches(0.55),
                 size=Pt(11) if i == 0 else Pt(12), color=clr, bold=(i == 0 or j == 1))
# Formula
add_rect(slide, Inches(6.8), Inches(6.4), Inches(6.2), Inches(0.5), NAVY_MID)
add_text(slide, "W = 7.0 × bmax = 7.0 × 32 = 224 m  |  h = dmax × 1.15 + 0.5 = 13.4 m CD",
         Inches(6.9), Inches(6.4), Inches(6.0), Inches(0.5),
         size=Pt(11), color=GOLD, bold=True)
slide.notes_slide.notes_text_frame.text = (
    "Channel width of 224 m = 7.0 × bmax. PIANC minimum is 6.0 × bmax = 192 m, so we have a 16.7% margin. "
    "Dredged depth: 12 m × 1.15 + 0.5 m squat = 14.3 m — we adopted 13.4 m CD as the programme value, "
    "to be refined by manoeuvring simulation. The bend radius of 1,500 m = 6.0 × Lmax exceeds PIANC minimum."
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — TURNING BASIN
# ══════════════════════════════════════════════════════════════════════════════
slide = navy_slide(prs, "Turning Basin Design", "Tug-Assisted Rotation — PIANC D = 1.5 × Lmax")
add_footer(slide)
# Basin diagram
add_rect(slide, Inches(0.5), Inches(1.85), Inches(6.5), Inches(5.2), NAVY_MID, GOLD, Pt(2))
add_text(slide, "[ TURNING BASIN — Plan Geometry ]\nØ 375 m circular basin + tug basin 180×200 m",
         Inches(0.5), Inches(4.1), Inches(6.5), Inches(0.8),
         size=Pt(12), color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
# Formula display
add_rect(slide, Inches(7.3), Inches(2.1), Inches(5.7), Inches(1.0), NAVY_MID, GOLD, Pt(2))
add_text(slide, "D = 1.5 × Lmax = 1.5 × 250 = 375 m",
         Inches(7.4), Inches(2.25), Inches(5.5), Inches(0.7),
         size=Pt(18), bold=True, color=GOLD, align=PP_ALIGN.CENTER)
# KPIs
add_kpi_box(slide, "Turning Basin Ø", "375 m", Inches(7.3), Inches(3.3), Inches(2.7))
add_kpi_box(slide, "PIANC Min (1.5×Lmax)", "375 m", Inches(10.2), Inches(3.3), Inches(2.7))
add_kpi_box(slide, "Status", "PASS ✓", Inches(7.3), Inches(4.7), Inches(5.6))
# Notes
add_text(slide, "Tug Basin: 180×200 m adjacent\nAnchorage: 800×600 m NW of channel\nDepth: −13.4 m CD (= channel depth)",
         Inches(7.3), Inches(6.1), Inches(5.7), Inches(0.8),
         size=Pt(11), color=LIGHT_GRAY)
slide.notes_slide.notes_text_frame.text = (
    "Turning basin diameter = 1.50 × Lmax = exactly 375 m, which equals the PIANC minimum. "
    "Two harbour tugs are provided in the adjacent 180×200 m tug basin. "
    "For unassisted turning we would need 2.0 × Lmax = 500 m — tug assistance allows us to use the smaller basin."
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — MASTERPLAN
# ══════════════════════════════════════════════════════════════════════════════
slide = navy_slide(prs, "Port Masterplan", "Complete Layout — 293 Hectares, 451 AutoCAD Entities")
add_footer(slide)
# Large CAD image placeholder
add_rect(slide, Inches(0.4), Inches(1.85), Inches(12.5), Inches(5.25), NAVY_MID, GOLD, Pt(2))
add_text(slide, "[ MASTERPLAN CAD — Suez_Port_Masterplan.png / Drawing SPM-001 Rev A ]\n"
         "Navigation Channel  ·  Turning Basin  ·  Breakwaters  ·  Liquid Bulk  ·  Dry Bulk  ·  Container  ·  Roads  ·  Facilities",
         Inches(0.5), Inches(3.8), Inches(12.3), Inches(1.2),
         size=Pt(13), color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
# Bottom stat strip
stats = [("Total Area", "293 ha"), ("Berths", "8"), ("Quay Length", "2,050 m"), ("CAD Entities", "451")]
for i, (lbl, val) in enumerate(stats):
    x = Inches(0.4) + i * Inches(3.13)
    add_rect(slide, x, H - Inches(1.0), Inches(3.1), Inches(0.6), NAVY_MID, GOLD, Pt(1))
    add_text(slide, f"{val}  {lbl}", x + Inches(0.1), H - Inches(0.95), Inches(2.9), Inches(0.5),
             size=Pt(13), bold=True, color=GOLD, align=PP_ALIGN.CENTER)
slide.notes_slide.notes_text_frame.text = (
    "The masterplan integrates all port elements. Walk the examiners through the layout: channel enters "
    "from the west, turning basin in the centre-east, berths to the north, breakwaters protecting the entrance. "
    "The AutoCAD drawing has 451 entities across professionally organised layers. The total footprint is 293 ha."
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — LIQUID BULK TERMINAL
# ══════════════════════════════════════════════════════════════════════════════
slide = navy_slide(prs, "Liquid Bulk Terminal", "Petroleum & Petrochemical Products — NFPA 30 Compliant")
add_footer(slide)
add_rect(slide, Inches(0.5), Inches(1.85), Inches(6.5), Inches(5.2), NAVY_MID, GOLD, Pt(2))
add_text(slide, "[ LIQUID BULK TERMINAL — CAD Detail ]\n5 Tanks Ø30m | NFPA 30 Compliant Spacing",
         Inches(0.5), Inches(4.0), Inches(6.5), Inches(0.8),
         size=Pt(12), color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
lb_data = [
    ("Storage Tanks", "5 × Ø 30 m, within continuous bund"),
    ("Tank Spacing (c/c)", "45 m = 1.5 × Ø  (NFPA 30) ✓"),
    ("Berth Length", "≥ 275 m (= 1.1 × Lmax)"),
    ("Fire Station", "160 × 140 m adjacent"),
    ("Cargo Type", "Petroleum / Petrochemicals"),
    ("Bund Area", "Continuous bund per NFPA 30"),
]
for i, (lbl, val) in enumerate(lb_data):
    y = Inches(2.1) + i * Inches(0.78)
    add_text(slide, lbl, Inches(7.3), y, Inches(2.2), Inches(0.65),
             size=Pt(12), color=GOLD_LIGHT, bold=True)
    add_text(slide, val, Inches(9.5), y, Inches(3.5), Inches(0.65),
             size=Pt(12), color=WHITE)
# Tank spacing check box
add_rect(slide, Inches(7.3), Inches(6.6), Inches(5.7), Inches(0.55), PASS_GRN)
add_text(slide, "Tank Spacing Check: 45 m = 1.5 × Ø30 m  →  PASS ✓",
         Inches(7.4), Inches(6.62), Inches(5.5), Inches(0.45),
         size=Pt(13), bold=True, color=WHITE, align=PP_ALIGN.CENTER)
slide.notes_slide.notes_text_frame.text = (
    "The liquid bulk terminal is positioned with maximum separation from other terminals — fire safety is critical here. "
    "Five tanks at Ø30 m with 45 m centre-to-centre spacing exactly meets the NFPA 30 minimum of 1.5 × diameter. "
    "The fire station is immediately adjacent. All tanks are inside a continuous containment bund."
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — DRY BULK TERMINAL
# ══════════════════════════════════════════════════════════════════════════════
slide = navy_slide(prs, "Dry Bulk Terminal", "Grain, Minerals & Aggregates — Silo Storage")
add_footer(slide)
add_rect(slide, Inches(0.5), Inches(1.85), Inches(6.5), Inches(5.2), NAVY_MID, GOLD, Pt(2))
add_text(slide, "[ DRY BULK TERMINAL — CAD Detail ]\n10 Silos Ø10m | Conveyor Belt System",
         Inches(0.5), Inches(4.0), Inches(6.5), Inches(0.8),
         size=Pt(12), color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
db_data = [
    ("Storage Silos", "10 × Ø 10 m"),
    ("Berth Length", "≥ 275 m (= 1.1 × Lmax)"),
    ("Cargo Handling", "Grab cranes / conveyor belts"),
    ("Cargo Type", "Grain, Minerals, Aggregates"),
    ("Container Stacking", "10 high-capacity blocks (Container Terminal)"),
]
for i, (lbl, val) in enumerate(db_data):
    y = Inches(2.2) + i * Inches(0.85)
    add_text(slide, lbl, Inches(7.3), y, Inches(2.5), Inches(0.7),
             size=Pt(12), color=GOLD_LIGHT, bold=True)
    add_text(slide, val, Inches(9.8), y, Inches(3.2), Inches(0.7),
             size=Pt(12), color=WHITE)
slide.notes_slide.notes_text_frame.text = (
    "The dry bulk terminal uses 10 silos for granular commodity storage. "
    "Berth length meets the PIANC minimum of 1.1 × Lmax = 275 m. "
    "Note: the GEN_CARGO berth at 230 m is a design flag that must be extended to 275 m in detailed design."
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — BREAKWATER
# ══════════════════════════════════════════════════════════════════════════════
slide = navy_slide(prs, "Breakwater Design", "Rubble-Mound — Hudson Formula Armour Sizing")
add_footer(slide)
add_rect(slide, Inches(0.5), Inches(1.85), Inches(6.0), Inches(3.2), NAVY_MID, GOLD, Pt(2))
add_text(slide, "[ BREAKWATER — Cross-Section Diagram ]\nArmour Layer | Filter | Core",
         Inches(0.5), Inches(2.9), Inches(6.0), Inches(0.6),
         size=Pt(12), color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
# Hudson formula display
add_rect(slide, Inches(0.5), Inches(5.2), Inches(6.0), Inches(1.5), NAVY_MID, GOLD, Pt(2))
add_text(slide, "W₅₀ = ρs · Hs³ / [KD · (Sr−1)³ · cot(α)]",
         Inches(0.6), Inches(5.35), Inches(5.8), Inches(0.5),
         size=Pt(15), color=GOLD, bold=True, align=PP_ALIGN.CENTER)
add_text(slide, "= 2650 × 4.5³ / [4.0 × 1.585³ × 2.0] = 241,481 / 31.86 = 7,580 kg",
         Inches(0.6), Inches(5.85), Inches(5.8), Inches(0.5),
         size=Pt(12), color=WHITE, align=PP_ALIGN.CENTER)

bw_data = [
    ("Parameter", "Value"),
    ("North Mole", "1,450 m"),
    ("South Mole", "950 m"),
    ("Entrance Gap", "314 m ≥ 224 m ✓"),
    ("Design Wave Hs", "4.5 m"),
    ("Rock Density ρs", "2,650 kg/m³"),
    ("Stability Coeff. KD", "4.0"),
    ("Slope cot(α)", "2.0 (1V:2H)"),
    ("Armour W₅₀", "7.6 t  ←  RESULT"),
    ("Crest Level", "+7.0 m CD"),
]
for i, (lbl, val) in enumerate(bw_data):
    y = Inches(1.9) + i * Inches(0.53)
    bg = NAVY if i == 0 else (NAVY_MID if i % 2 == 0 else RGBColor(0x1A, 0x38, 0x5F))
    if val == "7.6 t  ←  RESULT": bg = RGBColor(0x0A, 0x3D, 0x1A)
    add_rect(slide, Inches(6.8), y, Inches(6.2), Inches(0.5), bg)
    add_text(slide, lbl, Inches(6.9), y + Inches(0.07), Inches(3.0), Inches(0.38),
             size=Pt(11), color=GOLD if i == 0 else GOLD_LIGHT, bold=(i == 0))
    add_text(slide, val, Inches(9.9), y + Inches(0.07), Inches(3.0), Inches(0.38),
             size=Pt(12), color=WHITE if i == 0 else (GOLD if "RESULT" in val else WHITE),
             bold=("RESULT" in val))
slide.notes_slide.notes_text_frame.text = (
    "The Hudson formula is the core calculation of the breakwater design. "
    "Key inputs: Hs = 4.5 m (50-year wave), KD = 4.0 (rough quarry stone, breaking waves, trunk section). "
    "Result: W50 = 7.6 tonnes median armour mass. Individual stones range from 3.8 t to 15.2 t. "
    "Entrance gap of 314 m exceeds channel width of 224 m — safe navigational clearance."
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — ENGINEERING CALCULATIONS SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
slide = navy_slide(prs, "Engineering Calculations", "All Principal Results — PIANC · Hudson · NFPA 30")
add_footer(slide)
calc_rows = [
    ("CALC", "Parameter", "Result", "Standard", "Status"),
    ("01", "Design Vessel (Lmax×bmax×dmax)", "250m × 32m × 12m", "Panamax Class", "—"),
    ("02", "Dredged Channel Depth", "−13.4 m CD", "PIANC UKC Method", "PASS ✓"),
    ("03", "Channel Width", "224 m (7.0 × bmax)", "PIANC 2014 §3.4", "PASS ✓"),
    ("04", "Turning Basin Diameter", "375 m (1.5 × Lmax)", "PIANC 2014 §4.2", "PASS ✓"),
    ("05", "Armour Mass W₅₀ (Hudson)", "7.6 t", "SPM USACE 1984", "PASS ✓"),
    ("06", "Breakwater Crest Level", "+7.0 m CD", "EurOtop 2018", "PASS ✓"),
    ("07", "Berth Length (GEN_CARGO)", "230 m → min 275 m", "PIANC Mooring", "FLAG ⚠"),
    ("08", "Tank Spacing (Liquid Bulk)", "45 m = 1.5 × Ø30m", "NFPA 30", "PASS ✓"),
]
col_x = [Inches(0.4), Inches(1.1), Inches(4.2), Inches(8.1), Inches(10.9)]
col_w = [Inches(0.65), Inches(3.0), Inches(3.8), Inches(2.7), Inches(2.0)]
for i, row in enumerate(calc_rows):
    y = Inches(1.85) + i * Inches(0.56)
    bg = NAVY if i == 0 else (NAVY_MID if i % 2 == 1 else RGBColor(0x1A, 0x38, 0x5F))
    if "FLAG" in str(row): bg = RGBColor(0x4A, 0x20, 0x08)
    add_rect(slide, Inches(0.4), y, Inches(12.5), Inches(0.53), bg)
    for j, (x, w) in enumerate(zip(col_x, col_w)):
        cell_text = row[j] if j < len(row) else ""
        clr = GOLD if i == 0 else (
            GOLD if j in [2, 4] and i > 0 else WHITE
        )
        if "FLAG" in cell_text: clr = RGBColor(0xFF, 0xB0, 0x50)
        if "PASS" in cell_text: clr = RGBColor(0x4A, 0xDE, 0x80)
        add_text(slide, cell_text, x + Inches(0.05), y + Inches(0.07),
                 w - Inches(0.1), Inches(0.42),
                 size=Pt(10) if i == 0 else Pt(11),
                 color=clr, bold=(i == 0 or j == 2))
slide.notes_slide.notes_text_frame.text = (
    "Eight calculations in total. Seven pass. One design flag: the General Cargo berth at 230 m is below "
    "the PIANC minimum of 275 m. This is acknowledged and will be resolved in detailed design. "
    "Be ready to walk through the Hudson formula calculation in detail — it is the most likely examiner question."
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — COASTAL STRUCTURES STUDIO
# ══════════════════════════════════════════════════════════════════════════════
slide = navy_slide(prs, "Coastal Structures Studio v1.0", "Engineering Methodology & Digital Tooling")
add_footer(slide)
# Workflow diagram
steps = [
    "Project Inputs\n(Vessel, Site)",
    "Engineering\nCalculations",
    "PIANC/Hudson\nValidation",
    "Masterplan\nGeneration",
    "AutoCAD\nDWG / DXF",
    "Engineering\nReport",
    "Bill of\nQuantities",
]
step_w = Inches(1.55)
for i, s in enumerate(steps):
    x = Inches(0.45) + i * (step_w + Inches(0.2))
    bg = NAVY_MID if i < len(steps) - 1 else RGBColor(0x0A, 0x3D, 0x1A)
    add_rect(slide, x, Inches(2.2), step_w, Inches(1.3), bg, GOLD, Pt(1))
    add_text(slide, s, x + Inches(0.05), Inches(2.3), step_w - Inches(0.1), Inches(1.1),
             size=Pt(10), color=WHITE, align=PP_ALIGN.CENTER, bold=True)
    if i < len(steps) - 1:
        add_text(slide, "→", x + step_w, Inches(2.7), Inches(0.2), Inches(0.5),
                 size=Pt(18), color=GOLD, align=PP_ALIGN.CENTER, bold=True)

# CSS description
add_text(slide, "What is CSS v1.0?",
         Inches(0.5), Inches(3.8), Inches(6.0), Inches(0.45),
         size=Pt(16), bold=True, color=GOLD)
add_text(slide, (
    "Coastal Structures Studio is a Python-based parametric engineering engine developed "
    "specifically for this project. It manages the complex interdependencies between vessel dimensions, "
    "PIANC navigation geometry, and masterplan spatial constraints — automating repetitive calculations "
    "while keeping all engineering judgment with the design engineer."),
         Inches(0.5), Inches(4.3), Inches(6.5), Inches(2.5),
         size=Pt(13), color=WHITE)
# Tagline
add_rect(slide, Inches(7.3), Inches(3.8), Inches(5.7), Inches(0.8), NAVY_MID, GOLD, Pt(2))
add_text(slide, '"AI That Engineers Your Infrastructure."',
         Inches(7.4), Inches(3.9), Inches(5.5), Inches(0.6),
         size=Pt(14), bold=True, color=GOLD, align=PP_ALIGN.CENTER, italic=True)
# Important note
add_rect(slide, Inches(7.3), Inches(4.8), Inches(5.7), Inches(2.4), RGBColor(0x14, 0x28, 0x47))
add_text(slide, "Engineering is always the hero.\n\nCSS is the tool.\nThe Suez Port Masterplan is the project.",
         Inches(7.5), Inches(4.95), Inches(5.3), Inches(2.1),
         size=Pt(13), color=LIGHT_GRAY)
slide.notes_slide.notes_text_frame.text = (
    "CSS v1.0 is introduced late intentionally — after the examiners have already seen 12 slides of rigorous engineering. "
    "By this point they understand the engineering is solid. CSS is simply the tool that made the parametric workflow possible. "
    "Emphasize: all engineering judgment remained with the engineer. CSS computed, not decided."
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — FUTURE DEVELOPMENT
# ══════════════════════════════════════════════════════════════════════════════
slide = navy_slide(prs, "Future Development", "Next Engineering Phases & Expansion Potential")
add_footer(slide)
future_items = [
    ("Phase 2 — Detailed Design", [
        "Full geotechnical investigation (borehole programme)",
        "Physical model testing of breakwater and entrance",
        "Manoeuvring simulation for UKC refinement",
        "EurOtop overtopping analysis for crest finalisation",
    ]),
    ("Digital Twin Integration", [
        "BIM model linked to port operations management",
        "Real-time vessel tracking & berth scheduling",
        "Predictive maintenance for breakwater armour",
    ]),
    ("Port Expansion (Phase 3)", [
        "North terminal expansion — Container port",
        "Offshore SPM (Single Point Mooring) for VLCCs",
        "GIS spatial analytics for cargo flow optimisation",
    ]),
]
for i, (title, items) in enumerate(future_items):
    x = Inches(0.45) + i * Inches(4.3)
    add_rect(slide, x, Inches(1.85), Inches(4.1), Inches(5.2), NAVY_MID, GOLD, Pt(1))
    add_text(slide, title, x + Inches(0.15), Inches(1.95), Inches(3.8), Inches(0.55),
             size=Pt(13), bold=True, color=GOLD)
    for j, item in enumerate(items):
        add_text(slide, "■  " + item, x + Inches(0.15), Inches(2.7) + j * Inches(0.7),
                 Inches(3.8), Inches(0.6), size=Pt(11), color=WHITE)
slide.notes_slide.notes_text_frame.text = (
    "Future work addresses three areas. First, the immediate detailed design phase including geotechnical investigation "
    "and physical model testing. Second, digital integration with BIM and operational systems. "
    "Third, long-term expansion to accommodate larger vessels and increased throughput."
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — MY VISION
# ══════════════════════════════════════════════════════════════════════════════
layout = prs.slide_layouts[6]
slide = prs.slides.add_slide(layout)
add_rect(slide, 0, 0, W, H, NAVY)
add_rect(slide, 0, 0, W, Inches(0.12), GOLD)
add_rect(slide, 0, H - Inches(0.12), W, Inches(0.12), GOLD)
add_footer(slide)

add_text(slide, "My Vision",
         Inches(1.0), Inches(0.8), Inches(11.3), Inches(0.8),
         size=Pt(42), bold=True, color=WHITE)
add_rect(slide, Inches(1.0), Inches(1.6), Inches(3.0), Inches(0.07), GOLD)

vision_text = (
    "This project represents more than an engineering design.\n\n"
    "It is a demonstration that a single engineer, armed with the right tools and rigorous methodology, "
    "can produce work at consultancy quality — from design vessel to breakwater armour, "
    "from turning basin to terminal layout, from engineering calculations to print-ready drawings.\n\n"
    "My vision is to apply this same rigour to the infrastructure challenges of the Arab world — "
    "ports, coastal protection, maritime trade corridors — contributing to the sustainable development "
    "of the region I call home.\n\n"
    "Coastal Structures Studio v1.0 is the first step."
)
add_text(slide, vision_text,
         Inches(1.0), Inches(1.85), Inches(7.8), Inches(5.4),
         size=Pt(15), color=OFFWHITE)

# Right accent panel
add_rect(slide, Inches(9.3), Inches(1.5), Inches(3.6), Inches(5.6), NAVY_MID, GOLD, Pt(2))
add_text(slide, "SUEZ PORT\nMASTERPLAN\nDESIGN",
         Inches(9.5), Inches(2.5), Inches(3.2), Inches(2.0),
         size=Pt(22), bold=True, color=GOLD, align=PP_ALIGN.CENTER)
add_text(slide, "Mohamed Abdelshafy\n20107979\nJune 2026",
         Inches(9.5), Inches(4.8), Inches(3.2), Inches(1.5),
         size=Pt(13), color=WHITE, align=PP_ALIGN.CENTER)

slide.notes_slide.notes_text_frame.text = (
    "This is your closing slide — speak from the heart. This project is the culmination of your undergraduate "
    "engineering education. The examiners should leave the room thinking: this student understands coastal engineering, "
    "thinks like an engineer, and built something genuinely impressive. "
    "Thank the committee, your supervisor Dr. Walid Al-Amri, and your family."
)

# ── SAVE ───────────────────────────────────────────────────────────────────────
out_path = r"C:\Users\omare\OneDrive\Desktop\AI\Suez_Port_Masterplan\deliverables\SUEZ_Port_Presentation.pptx"
prs.save(out_path)
print(f"Saved: {out_path}")
print(f"Slides: {len(prs.slides)}")

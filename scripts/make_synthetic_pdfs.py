"""
Generate two vendor PDFs WITH line_code column.
Run once:
    python scripts/make_synthetic_pdfs.py
The files land in ./data/
"""

from pathlib import Path
from fpdf import FPDF

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def make_pdf(out_path, rows, title):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(4)
    pdf.set_font("Helvetica", size=11)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(20, 8, "Code", border=1, fill=True)
    pdf.cell(70, 8, "Item", border=1, fill=True)
    pdf.cell(0, 8, "Vendor Value", border=1, ln=True, fill=True)
    for code, item, val in rows:
        pdf.cell(20, 8, code, border=1)
        pdf.cell(70, 8, item, border=1)
        pdf.multi_cell(0, 8, val, border=1)
    pdf.output(out_path)

# ---------- Vendor A (mostly compliant) ----------
vendor_a_rows = [
    ("P01", "Pump standard",           "API 610"),
    ("P02", "Installation location",   "Unsheltered outdoor"),
    ("P03", "Sparing philosophy",      "2×50 % + 1 spare"),
    ("P04", "Seal type",               "Dual mechanical"),
    ("P05", "Seal flushing",           "Self-flush"),
    ("P06", "Driver",                  "Electric motor"),
    ("P07", "Starting frequency",      "0.5 starts/week"),
    ("P08", "Minimum-flow bypass",     "Automatic"),
    ("P09", "Bearing cooling",         "Air-cooled"),
    ("P10", "Auto-start motor sizing", "Meets rule"),
]

# ---------- Vendor B (deliberate deviations) ----------
vendor_b_rows = [
    ("P01", "Standard",                "ISO 5199"),            # wrong spec
    ("P02", "Installation location",   "Outdoor"),
    ("P03", "Quantity Required",       "1×100 % pump"),        # wrong sparing
    ("P04", "Seal System",             "Single seal"),         # wrong seal
    ("P05", "Seal flushing",           "None"),                # violates rule
    ("P06", "Motor / Make",            "Steam turbine"),       # wrong driver
    ("P07", "Starting frequency",      "3 starts/week"),       # too frequent
    ("P08", "MFB",                     "None"),                # missing bypass
    ("P09", "Bearing cooling",         "CW ΔT 15 °C"),         # spec violation
    ("P10", "Auto-start motor sizing", "Not evaluated"),
]

make_pdf(DATA_DIR / "synthetic_vendor_A_pump_proposal.pdf",
         vendor_a_rows,
         "Synthetic Vendor A – Pump Proposal")

make_pdf(DATA_DIR / "synthetic_vendor_B_pump_proposal.pdf",
         vendor_b_rows,
         "Synthetic Vendor B – Pump Proposal")

print("✅  PDFs written to data/")

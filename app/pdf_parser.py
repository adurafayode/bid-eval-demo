import pandas as pd, re
from tabula import read_pdf
import camelot
from difflib import get_close_matches
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CODE_RE = re.compile(r"P\d{2}", re.I)

# aliases for PDFs that omit the line_code column
ALIAS = {
    "Pump standard":            "P01", "Standard": "P01",
    "Installation location":    "P02",
    "Sparing philosophy":       "P03", "Quantity Required": "P03",
    "Seal type":                "P04", "Seal System": "P04",
    "Seal flushing":            "P05",
    "Driver":                   "P06", "Motor / Make": "P06",
    "Starting frequency":       "P07",
    "Minimum-flow bypass":      "P08", "MFB": "P08",
    "Bearing cooling":          "P09",
    "Auto-start motor sizing":  "P10",
}

# ---------------------------------------------------------------------------

def _tabula(pdf_path: str) -> pd.DataFrame | None:
    try:
        logger.info(f"Attempting to parse PDF with tabula: {pdf_path}")
        tables = read_pdf(pdf_path, pages="1", guess=True)
        if tables and len(tables[0].columns) >= 2:
            logger.info("Successfully parsed PDF with tabula")
            return tables[0]
        logger.warning("Tabula found no valid tables")
    except Exception as e:
        logger.error(f"Tabula parsing failed: {str(e)}")
    return None

def _camelot(pdf_path: str) -> pd.DataFrame | None:
    try:
        logger.info(f"Attempting to parse PDF with camelot: {pdf_path}")
        tables = camelot.read_pdf(pdf_path, pages="1", flavor="stream")
        if tables and len(tables[0].df.columns) >= 2:
            logger.info("Successfully parsed PDF with camelot")
            return tables[0].df
        logger.warning("Camelot found no valid tables")
    except Exception as e:
        logger.error(f"Camelot parsing failed: {str(e)}")
    return None

# ---------------------------------------------------------------------------

def parse_pdf_to_df(pdf_path: str) -> pd.DataFrame:
    logger.info(f"Starting PDF parsing for: {pdf_path}")
    raw = _tabula(pdf_path)
    if raw is None:
        raw = _camelot(pdf_path)
    if raw is None:
        logger.error(f"Both tabula and camelot failed to extract tables from {pdf_path}")
        raise ValueError(f"Could not extract tables from {pdf_path}")

    raw.columns = range(len(raw.columns))

    # ── Case A: Code | Item | Value ────────────────────────────────────────
    if len(raw.columns) >= 3 and CODE_RE.match(str(raw.iloc[0, 0])):
        logger.info("Using Code|Item|Value format")
        df = raw.iloc[:, :3]
        df.columns = ["line_code", "item", "vendor_value"]

    # ── Case B: Item | Value  (map to line_code) ───────────────────────────
    else:
        logger.info("Using Item|Value format with line_code mapping")
        df = raw.iloc[:, :2]
        df.columns = ["item", "vendor_value"]
        df["line_code"] = df["item"].map(ALIAS)

        missing = df["line_code"].isna()
        for idx in df[missing].index:
            close = get_close_matches(df.at[idx, "item"], ALIAS, n=1, cutoff=0.7)
            if close:
                df.at[idx, "line_code"] = ALIAS[close[0]]

    # ── tidy up ────────────────────────────────────────────────────────────
    df = df.dropna(subset=["line_code"]).copy()
    df["item"]         = df["item"].str.strip()
    df["vendor_value"] = df["vendor_value"].astype(str).str.strip()
    df["vendor"]       = pdf_path.split("/")[-1].replace(".pdf", "")
    logger.info(f"Successfully processed PDF with {len(df)} rows")
    return df[["line_code", "item", "vendor_value", "vendor"]]

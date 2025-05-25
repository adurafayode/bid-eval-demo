import pandas as pd, re
from tabula import read_pdf
import camelot
from difflib import get_close_matches

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
        tables = read_pdf(pdf_path, pages="1", guess=True)
        if tables and len(tables[0].columns) >= 2:
            return tables[0]
    except Exception:
        pass
    return None

def _camelot(pdf_path: str) -> pd.DataFrame | None:
    try:
        tables = camelot.read_pdf(pdf_path, pages="1", flavor="stream")
        if tables and len(tables[0].df.columns) >= 2:
            return tables[0].df
    except Exception:
        pass
    return None

# ---------------------------------------------------------------------------

def parse_pdf_to_df(pdf_path: str) -> pd.DataFrame:
    raw = _tabula(pdf_path)
    if raw is None:
        raw = _camelot(pdf_path)
    if raw is None:
        raise ValueError(f"Could not extract tables from {pdf_path}")

    raw.columns = range(len(raw.columns))

    # ── Case A: Code | Item | Value ────────────────────────────────────────
    if len(raw.columns) >= 3 and CODE_RE.match(str(raw.iloc[0, 0])):
        df = raw.iloc[:, :3]
        df.columns = ["line_code", "item", "vendor_value"]

    # ── Case B: Item | Value  (map to line_code) ───────────────────────────
    else:
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
    return df[["line_code", "item", "vendor_value", "vendor"]]

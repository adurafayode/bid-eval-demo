# app/compare.py
"""
Compare the spec template with a vendor dataframe and flag:
    Y = Complies exactly or contains equivalent wording
    A = Acceptable alternative (tokens like “API”, “ISO”, “ANSI”, “dual” …)
    N = Non-compliant (numeric out of range or text mismatch)
    C = Clarification required (vendor value missing)
"""

import re, unicodedata
import pandas as pd

# numeric tolerance (fraction of spec value)
STRICT   = 0.05   # ±5 %  → Y
LENIENT  = 0.15   # 5–15 %→ A

ALT_TOKENS = ("api", "iso", "ansi", "dual", "self-flush")

# ---------------------------------------------------------------------------

def _clean(text: str) -> str:
    """lower-case, collapse whitespace, replace unicode × with x"""
    text = unicodedata.normalize("NFKD", text)
    text = text.replace("×", "x").replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()

def _numeric(spec: str, vendor: str) -> str | None:
    """Return Y / A / N if both strings start with numbers, else None."""
    try:
        sv = float(re.findall(r"[-+]?\d*\.?\d+", spec)[0])
        vv = float(re.findall(r"[-+]?\d*\.?\d+", vendor)[0])
    except Exception:
        return None

    delta = abs(vv - sv) / sv
    if   delta <= STRICT:   return "Y"
    elif delta <= LENIENT:  return "A"
    else:                   return "N"

def compliance_flag(row: pd.Series) -> str:
    spec   = str(row["spec_value"])
    vendor = str(row["vendor_value"])

    if vendor in {"nan", "None", ""} or pd.isna(vendor):
        return "C"   # Clarification required (missing data)

    # 1️⃣ numeric comparison first
    num_flag = _numeric(spec, vendor)
    if num_flag:
        return num_flag

    # 2️⃣ text comparison
    spec_c, vendor_c = _clean(spec), _clean(vendor)

    # exact or containment
    if spec_c == vendor_c or spec_c in vendor_c or vendor_c in spec_c:
        return "Y"

    # acceptable alternative tokens
    if any(tok in vendor_c for tok in ALT_TOKENS):
        return "A"

    return "N"

# ---------------------------------------------------------------------------

def compare(spec_df: pd.DataFrame, vendor_df: pd.DataFrame) -> pd.DataFrame:
    """
    Join on line_code only; keep spec wording.
    vendor_df contains columns [line_code, vendor_value, vendor]
    """
    vendor_trim = vendor_df[["line_code", "vendor_value", "vendor"]]

    merged = spec_df.merge(vendor_trim, on="line_code", how="left")
    merged["compliance"] = merged.apply(compliance_flag, axis=1)
    return merged

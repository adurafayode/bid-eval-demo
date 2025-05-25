# Bid-Evaluation Pilot (Pumps)

Demo Streamlit app that compares vendor pump proposals to a
specification slice from an Engineering Design Basis (EDB) and flags
non-compliances automatically.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Ghostscript + Java required for Camelot/Tabula
streamlit run app/app.py
```

## How it works

### Spec template

- `data/edb_pump_spec_template.csv`

### PDF parser

- Camelot/Tabula pull tables from vendor PDFs.

### Comparison rules

- See `app/compare.py`

### Streamlit UI

- Drag-and-drop PDFs, see heat-map + Excel export.

## Next steps

1. Swap synthetic PDFs for real vendor technical proposals.
2. Extend the line-item map (`item_map`) to cover more spec rows.
3. Harden compliance logic (unit conversion, text-similarity, etc.).

## Run & test locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/app.py
```

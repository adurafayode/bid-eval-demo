import io, pandas as pd, streamlit as st
import os, tempfile, logging
from app.compare import compare
from app.pdf_parser import parse_pdf_to_df

st.set_page_config(page_title="Pump Bid Evaluation Pilot", layout="wide")
st.title("AI-assisted Pump Bid Evaluation")

# Set up logging to display in Streamlit
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

spec_df = pd.read_csv("data/edb_pump_spec_template.csv")

demo_files = {
    "Vendor A (sample)": "data/synthetic_vendor_A_pump_proposal.pdf",
    "Vendor B (sample)": "data/synthetic_vendor_B_pump_proposal.pdf",
}

uploads = None
if st.sidebar.checkbox("Use sample PDFs"):
    # keep them as *strings* (paths), not open() objects
    uploads = list(demo_files.values())

st.sidebar.header("Step 1 · Upload vendor technical-proposal PDFs")
if uploads is None:
    uploads = st.sidebar.file_uploader(
        "Drag-and-drop one or more PDFs",
        type="pdf",
        accept_multiple_files=True
    )

if uploads:
    for up in uploads:
        try:
            # normalise to a real path on disk
            if isinstance(up, str):
                tmp_path = up                     # sample mode
                display_name = os.path.basename(up)
            else:                                 # Streamlit UploadedFile
                display_name = up.name
                tmp_path = os.path.join(
                    tempfile.gettempdir(), display_name
                )
                with open(tmp_path, "wb") as f:
                    f.write(up.getbuffer())

            st.subheader(display_name)
            
            # Add debug info
            st.write("Processing file:", tmp_path)
            st.write("File exists:", os.path.exists(tmp_path))
            st.write("File size:", os.path.getsize(tmp_path))
            
            vendor_df = parse_pdf_to_df(tmp_path)
            merged = compare(spec_df, vendor_df)

            st.dataframe(
                merged.style.apply(
                    lambda r: ["background:#c6efce" if r.compliance == "Y"
                               else "background:#ffeb9c" if r.compliance == "A"
                               else "background:#ffc7ce" if r.compliance == "N"
                               else ""
                               for _ in r],
                    axis=1,
                )
            )
            st.bar_chart(merged["compliance"].value_counts())

            excel_buf = io.BytesIO()
            with pd.ExcelWriter(excel_buf, engine="openpyxl") as wr:
                merged.to_excel(wr, index=False)
            st.download_button(
                "Download evaluation as Excel",
                excel_buf.getvalue(),
                file_name=f"{display_name[:-4]}_eval.xlsx"
            )
        except Exception as e:
            st.error(f"Error processing {display_name}: {str(e)}")
            logger.exception("Error details:")
else:
    st.info("⬅️ Upload a PDF or tick *Use sample PDFs* to see a demo.") 
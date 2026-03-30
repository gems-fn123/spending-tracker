import streamlit as st
from pathlib import Path
from PIL import Image
from services.ocr import extract_text
from services.receipt_parser import parse_receipt_text
from services.categorizer import suggest_category
from services import excel_io
from paddleocr import PaddleOCR
import yaml

@st.cache_resource
def get_ocr():
    return PaddleOCR(use_angle_cls=True, lang="en")

st.title("Add Receipt")


def get_default_workbook_path():
    """Resolve workbook path with backward compatibility for older excel_io modules."""
    if hasattr(excel_io, "get_default_workbook_path"):
        return excel_io.get_default_workbook_path()
    return str(Path(__file__).resolve().parent.parent / "Pengeluaran_budget_template.xlsx")

# Load categories
with open("config/categories.yml", "r") as f:
    categories = yaml.safe_load(f)["categories"]

uploaded = st.file_uploader("Upload receipt", type=["jpg", "jpeg", "png"])
captured = st.camera_input("Or take a photo")

file_obj = captured if captured else uploaded

if file_obj:
    image = Image.open(file_obj)
    st.image(image, caption="Receipt preview", use_container_width=True)

    if st.button("Read receipt"):
        raw_text = extract_text(image, get_ocr())
        parsed = parse_receipt_text(raw_text)
        parsed["category"] = suggest_category(parsed["merchant"], parsed["raw_text"])
        st.session_state["parsed_receipt"] = parsed

if "parsed_receipt" in st.session_state:
    data = st.session_state["parsed_receipt"]

    with st.form("confirm_receipt"):
        date = st.date_input("Date", value=data["date"])
        merchant = st.text_input("Merchant", value=data["merchant"])
        amount = st.number_input("Amount", min_value=0.0, value=float(data["amount"] or 0))
        category = st.selectbox(
            "Category",
            categories,
            index=categories.index(data["category"]) if data["category"] in categories else 0
        )
        notes = st.text_area("Notes", value=data["raw_text"][:1000])

        submitted = st.form_submit_button("Save transaction")

        if submitted:
            workbook = excel_io.load_workbook(get_default_workbook_path())
            excel_io.append_transaction(workbook, {
                "date": date,
                "merchant": merchant,
                "description": merchant,
                "amount": amount,
                "type": "expense",
                "category": category,
                "source": "receipt",
                "receipt_text": data["raw_text"],
                "notes": notes,
            })
            st.success("Transaction saved to the workbook")
            del st.session_state["parsed_receipt"]

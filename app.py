import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Air Waybill Processor", layout="centered")

st.title("🛩️ Air Waybill PDF Processor")
st.markdown("Upload your Air Waybill PDF to keep the **first 2 pages** and set pricing to **'As Agreed'**.")

uploaded_file = st.file_uploader("Choose an Air Waybill PDF", type=["pdf"])

if uploaded_file is not None:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    
    # 1. Keep only the first 2 pages if longer than 2 pages
    if len(doc) > 2:
        doc.select([0, 1])
        
    page = doc[0]  # Page 1
    
    # 2. Define exact bounding boxes [x0, y0, x1, y1] for each field on standard A4 Air Waybill
    # Adjust these exact box bounds if your scanner / renderer uses a slightly different DPI layout
    fields = [
        {"name": "Rate / Charge",   "rect": fitz.Rect(275, 235, 335, 265)},
        {"name": "Total Charge",    "rect": fitz.Rect(375, 235, 475, 265)},
        {"name": "Rate Total Row",  "rect": fitz.Rect(375, 455, 475, 480)},
        {"name": "Weight Charge",   "rect": fitz.Rect(110, 488, 200, 515)},
        {"name": "Total Prepaid",   "rect": fitz.Rect(110, 785, 200, 810)}
    ]
    
    for field in fields:
        r = field["rect"]
        
        # Redact/blank out existing numbers in the box area
        page.add_redact_annot(r, fill=(1, 1, 1))
        page.apply_redactions()
        
        # Insert "As Agreed" horizontally and vertically centered inside the box
        page.insert_textbox(
            r,
            "As Agreed",
            fontsize=8,
            fontname="helv",
            color=(0, 0, 0),
            align=fitz.TEXT_ALIGN_CENTER
        )

    # Save to memory stream
    output_stream = io.BytesIO()
    doc.save(output_stream)
    doc.close()

    st.success("✅ PDF processed successfully!")
    
    st.download_button(
        label="📥 Download Modified PDF",
        data=output_stream.getvalue(),
        file_name=f"Modified_{uploaded_file.name}",
        mime="application/pdf"
    )

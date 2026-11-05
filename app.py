import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Air Waybill Processor", layout="centered")

st.title("🛩️ Air Waybill PDF Processor")
st.markdown("Upload your Air Waybill PDF to keep the **first 2 pages** and set pricing fields to **'As Agreed'** automatically.")

uploaded_file = st.file_uploader("Choose an Air Waybill PDF", type=["pdf"])

if uploaded_file is not None:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    
    # 1. Keep only the first 2 pages if longer than 2 pages
    if len(doc) > 2:
        doc.select([0, 1])
        
    page = doc[0]  # Page 1
    
    # 2. Define exact coordinate boxes [x0, y0, x1, y1] for the price/charge fields
    # This works regardless of what text (or blank space) is currently in the box.
    charge_boxes = [
        fitz.Rect(275, 235, 335, 265),  # Rate / Charge box
        fitz.Rect(375, 235, 475, 265),  # Total box
        fitz.Rect(375, 455, 475, 480),  # Rate Total row
        fitz.Rect(110, 488, 200, 515),  # Weight Charge box
        fitz.Rect(110, 785, 200, 810)   # Total Prepaid box
    ]
    
    for box in charge_boxes:
        # Cover any existing text or background with a clean white block
        page.add_redact_annot(box, fill=(1, 1, 1))
        page.apply_redactions()
        
        # Insert "As Agreed" perfectly centered inside the box
        page.insert_textbox(
            box,
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

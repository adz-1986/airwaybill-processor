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
    
    # 2. Smart zone scanning: find text words located in the exact vertical zones for pricing fields
    words = page.get_text("words")  # list of (x0, y0, x1, y1, text, ...)
    
    target_rects = []
    for w in words:
        x0, y0, x1, y1, text = w[:5]
        
        # Zone 1: Item Row (Rate & Total columns) -> upper middle table
        if 225 <= y0 <= 260 and (260 <= x0 <= 480):
            target_rects.append(fitz.Rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2))
            
        # Zone 2: Weight Charge box -> middle section
        elif 480 <= y0 <= 515 and (100 <= x0 <= 210):
            target_rects.append(fitz.Rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2))
            
        # Zone 3: Total Prepaid box -> bottom section
        elif 775 <= y0 <= 815 and (100 <= x0 <= 210):
            target_rects.append(fitz.Rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2))

    # Fallback default boxes if cells happen to be completely blank
    if not target_rects:
        target_rects = [
            fitz.Rect(275, 235, 335, 260),  # Rate
            fitz.Rect(375, 235, 475, 260),  # Total
            fitz.Rect(110, 488, 200, 512),  # Weight Charge
            fitz.Rect(110, 785, 200, 810)   # Total Prepaid
        ]

    # Redact and replace each identified field cleanly
    for rect in target_rects:
        page.add_redact_annot(rect, fill=(1, 1, 1))
        page.apply_redactions()
        page.insert_textbox(
            rect,
            "As Agreed",
            fontsize=7,
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

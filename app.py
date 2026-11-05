import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Air Waybill Processor", layout="centered")

st.title("🛩️ Air Waybill PDF Processor")
st.markdown("Upload your Air Waybill PDF. The app will automatically keep only the **first 2 pages** and update the charge fields to **'As Agreed'**.")

uploaded_file = st.file_uploader("Choose an Air Waybill PDF", type=["pdf"])

if uploaded_file is not None:
    # Read PDF into memory
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    
    # 1. Keep only the first 2 pages if longer than 2 pages
    if len(doc) > 2:
        doc.select([0, 1])
        
    page = doc[0]  # Page 1
    
    # 2. Target fields to replace with "As Agreed"
    targets = ["12.50", "437.50"]
    
    for target in targets:
        text_instances = page.search_for(target)
        for rect in text_instances:
            # Cover existing text with a white box
            page.add_redact_annot(rect, fill=(1, 1, 1))
            page.apply_redactions()
            
            # Overlay "As Agreed"
            page.insert_text(
                rect.tl + (0, 8),
                "As Agreed",
                fontsize=8,
                fontname="helv",
                color=(0, 0, 0)
            )

    # Save to memory stream
    output_stream = io.BytesIO()
    doc.save(output_stream)
    doc.close()

    st.success("✅ PDF processed successfully!")
    
    # Download Button for Staff
    st.download_button(
        label="📥 Download Modified PDF",
        data=output_stream.getvalue(),
        file_name=f"Modified_{uploaded_file.name}",
        mime="application/pdf"
    )
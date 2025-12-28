#import section 67 ๖๗
import streamlit as st
import easyocr
import numpy as np
import io
from PIL import Image

st.set_page_config(page_title="Thai OCR", layout="wide")
st.title("IMG to text using EasyOCR (Thai&English)")

#Load OCR model for only 1 time
@st.cache_resource
def load_ocr_model():
    with st.spinner("...loading OCR model..."):
        return easyocr.Reader(['th', 'en'])

reader = load_ocr_model() #load
col1, col2 = st.columns(2) #UI

with col1:
    st.subheader("Upload")
    uploaded_file = st.file_uploader("Choose Image (.jpg, .jpeg, .png ONLY NaKrab!)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

with col2:
    st.subheader("OCR Results")
    if uploaded_file:
        with st.spinner("⏳ Processing IN PROGRESS..."):
            #transform uploaded file to numpy array
            img_np = np.array(Image.open(uploaded_file))
            # Perform OCR
            result = reader.readtext(img_np)
            # print
            ocr_text = ""
            for detection in result:
                text = detection[1]
                confidence = detection[2]
                ocr_text += f"{text} ({confidence:.2f})\n"
            
            st.text_area("detected text:", ocr_text, height=300)
        
            # download button
            st.download_button(
                label="Download as .txt file",
                data=ocr_text,
                file_name="ocr-result.txt",
                mime="text/plain"
            )
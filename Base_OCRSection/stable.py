import streamlit as st
import easyocr
import numpy as np
import cv2
from PIL import Image

st.set_page_config(page_title="Thai OCR", layout="wide")
st.title("IMG to text using EasyOCR (Thai&English)")

@st.cache_resource
def load_ocr_model():
    with st.spinner("...Loading OCR model..."):
        return easyocr.Reader(['th', 'en'])

def preprocess_image(img_np):
    #Improve image quality 
    if len(img_np.shape) == 3:
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_np
    
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    height, width = enhanced.shape
    if width < 300 or height < 300:
        scale = max(300 / width, 300 / height)
        enhanced = cv2.resize(enhanced, None, fx=scale, fy=scale, 
                            interpolation=cv2.INTER_CUBIC)
    
    return enhanced

def has_thai_text(text):
    #Check if text contains Thai characters
    return any(0x0E00 <= ord(char) <= 0x0E7F for char in text)
def has_eng_text(text):
    #Check if text contains English characters
    return any(0x0041 <= ord(char) <= 0x005A or 0x0061 <= ord(char) <= 0x007A for char in text)

reader = load_ocr_model()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload")
    uploaded_file = st.file_uploader("Choose Image(.jpg, .jpeg, .png ONLY NaKrab!)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        st.caption(f"Size: {image.size[0]}x{image.size[1]}")

with col2:
    st.subheader("OCR Results")
    
    if uploaded_file:
        with st.spinner("...Processing..."):
            try:
                img_np = np.array(Image.open(uploaded_file))
                img_processed = preprocess_image(img_np)
                result = reader.readtext(img_processed)
                
                if not result:
                    st.error("No text detected")
                else:
                    ocr_text = "\n".join([detection[1] for detection in result])
                    thai_detected = any(has_thai_text(detection[1]) for detection in result)
                    eng_detected = any(has_eng_text(detection[1]) for detection in result)
                    st.success(f"Detected {len(result)} text segments")
                    if thai_detected:
                        st.info("Thai text detected")
                    if eng_detected:
                        st.info("English text detected")
                    
                    st.text_area("Detected text:", ocr_text, height=300)
                    
                    st.download_button(
                        label="Download Results as .txt file",
                        data=ocr_text.encode('utf-8'),
                        file_name="ocr-result.txt",
                        mime="text/plain; charset=utf-8"
                    )
            
            except Exception as e:
                st.error(f"Error during OCR: {e}")
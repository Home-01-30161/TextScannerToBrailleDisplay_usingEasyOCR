import streamlit as st
import easyocr
import numpy as np
import cv2
from PIL import Image
import subprocess
import os

st.set_page_config(page_title="Thai OCR & Braille", layout="wide")
st.title("IMG to Text & Braille (Position Code)")

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
    return any(0x0E00 <= ord(char) <= 0x0E7F for char in text)

def has_eng_text(text):
    return any(0x0041 <= ord(char) <= 0x005A or 0x0061 <= ord(char) <= 0x007A for char in text)

def run_braille_conversion(text_input):
    import sys
    # 1. หา path ของโฟลเดอร์โครงการ (D:\EasyOCR_Project\LogicToNumPos)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    app_path = os.path.join(current_dir, "app.py")
    temp_filename = os.path.join(current_dir, "temp_ocr_input.txt")
    
    # เขียนข้อความลงไฟล์ชั่วคราว
    with open(temp_filename, "w", encoding="utf-8") as f:
        f.write(text_input)
    
    try:
        if not os.path.exists(app_path):
            return f"Error: ไม่พบไฟล์ app.py ที่ {app_path}"

        # 2. เพิ่มพารามิเตอร์ cwd=current_dir
        # เพื่อหลอกให้ app.py คิดว่ามันกำลังรันอยู่ในโฟลเดอร์ของมันเอง
        # มันจะหา './custom_sylleble.txt' เจอทันที
        result = subprocess.run(
            [sys.executable, "app.py", "-p", "temp_ocr_input.txt", "-m", "0"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=current_dir  # <--- จุดสำคัญคือบรรทัดนี้ครับ
        )
        
        if result.returncode != 0:
            return f"Error running braille script:\n{result.stderr}"
            
        return result.stdout.strip()

    except Exception as e:
        return f"System Error: {str(e)}"
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

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
    st.subheader("OCR & Braille Results")
    
    if uploaded_file:
        with st.spinner("...Processing OCR..."):
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
                    
                    # แสดงผล OCR
                    st.text_area("Detected Text (OCR):", ocr_text, height=200)
                    
                    # --- ส่วนที่เพิ่ม: ปุ่มและพื้นที่แสดงผล Braille ---
                    st.markdown("---") # เส้นคั่น
                    st.subheader("Braille Conversion (T2SB m=0)")
                    
                    if st.button("Convert to Braille Codes"):
                        with st.spinner("Converting to Braille..."):
                            braille_output = run_braille_conversion(ocr_text)
                            
                            # แสดงผลลัพธ์
                            if "Error" in braille_output:
                                st.error(braille_output)
                            else:
                                st.text_area("Braille Position Output:", braille_output, height=200)
                                st.balloons() # ลูกเล่นเล็กน้อยเมื่อแปลงสำเร็จ
                    # -----------------------------------------------

                    st.download_button(
                        label="Download OCR Results (.txt)",
                        data=ocr_text.encode('utf-8'),
                        file_name="ocr-result.txt",
                        mime="text/plain; charset=utf-8"
                    )
            
            except Exception as e:
                st.error(f"Error during OCR: {e}")
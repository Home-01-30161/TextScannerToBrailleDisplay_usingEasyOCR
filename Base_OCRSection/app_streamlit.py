import streamlit as st
import os

st.set_page_config(page_title="OCR Test", layout="wide")
st.title("🔤 OCR Test")

# ✅ ตั้ง cache folder เพื่อไม่ต้อง download ใหม่
os.environ['EASYOCR_HOME'] = '/tmp/.easyocr'

st.write("✅ แอปทำงานปกติ")

# ทดลองโหลด easyocr
try:
    import easyocr
    st.success("✅ EasyOCR imported successfully")
except Exception as e:
    st.error(f"❌ Import Error: {e}")
    st.stop()

# ทดลองโหลด model (มี timeout)
try:
    st.info("⏳ กำลัง download model... (อาจใช้เวลา 2-3 นาที)")
    
    @st.cache_resource
    def load_model():
        return easyocr.Reader(['th', 'en'], gpu=False)
    
    reader = load_model()
    st.success("✅ Model loaded successfully")
    st.write(f"Model: {reader}")
    
except Exception as e:
    st.error(f"❌ Model Error: {e}")
    import traceback
    st.write(traceback.format_exc())

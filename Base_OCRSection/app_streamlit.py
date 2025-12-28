import streamlit as st

st.title("🔤 OCR Test")
st.write("✅ แอปทำงานปกติ")

# ทดลองโหลด easyocr
try:
    import easyocr
    st.success("✅ EasyOCR loaded successfully")
except Exception as e:
    st.error(f"❌ Error: {e}")

# ทดลองโหลด model
try:
    @st.cache_resource
    def load_model():
        return easyocr.Reader(['th', 'en'])
    
    reader = load_model()
    st.success("✅ Model loaded successfully")
except Exception as e:
    st.error(f"❌ Model error: {e}")

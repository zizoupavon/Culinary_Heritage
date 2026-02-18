import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

st.set_page_config(page_title="Debug Mode", page_icon="🔧")

st.title("🔧 Debug & Fix Mode")

# --- DEBUG SECTION ---
st.subheader("1. File Check")
files_in_folder = os.listdir('.')
st.write("Files found in this folder:", files_in_folder)

if "satvik.pdf" in files_in_folder:
    st.success("✅ 'satvik.pdf' is found!")
else:
    st.error("❌ 'satvik.pdf' is MISSING. Please rename your file in GitHub to exactly 'satvik.pdf' (all lowercase).")

# --- API KEY SECTION ---
st.subheader("2. API Key Check")
api_key = st.sidebar.text_input("Paste your Google API Key here:", type="password")

if not api_key:
    st.warning("waiting for API key in the sidebar...")

# --- THE APP LOGIC ---
if st.button("Test the AI") and api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Try reading the PDF
        pdf_text = ""
        try:
            with open("satvik.pdf", 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    pdf_text += page.extract_text()
            st.success(f"✅ Successfully read {len(pdf_text)} characters from the book.")
        except Exception as e:
            st.error(f"❌ Could not read PDF: {e}")
            st.stop()

        # Try asking the AI
        st.info("Asking Gemini to say hello...")
        response = model.generate_content(f"The user wants a Satvik recipe. The book contains: {pdf_text[:1000]}... Suggest one dish.")
        st.write("### AI Response:")
        st.write(response.text)

    except Exception as e:
        st.error(f"❌ AI Error: {e}")

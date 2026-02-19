import streamlit as st
import google.generativeai as genai
import PyPDF2

# 1. PAGE SETUP
st.set_page_config(page_title="Satvik Chef", page_icon="🥥")
st.title("🥥 Satvik Heritage Chef (Debug Mode)")

# 2. SIDEBAR
st.sidebar.header("1. Settings")
api_key = st.sidebar.text_input("Google API Key", type="password")
uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

# 3. DIAGNOSTICS ON SCREEN
st.write("---")
st.write("### 🩺 System Status:")

if api_key:
    st.success("✅ API Key detected.")
else:
    st.error("❌ API Key is MISSING. Please paste it in the sidebar and hit ENTER.")

if uploaded_file:
    st.success(f"✅ File detected: {uploaded_file.name}")
else:
    st.error("❌ PDF is MISSING. Please drag your file to the sidebar.")

# 4. INPUT
user_mood = st.text_input("How are you feeling?", placeholder="Type here (e.g. Hungry)...")

# 5. BUTTON LOGIC WITH PRINTOUTS
if st.button("Get Recipe"):
    st.write("📝 **Step 1: Button Clicked...**")
    
    if not user_mood:
        st.error("❌ Error: You must type a mood above!")
        st.stop()
        
    if not api_key or not uploaded_file:
        st.error("❌ Error: Missing Key or File (see status above).")
        st.stop()
        
    # PROCESS
    try:
        st.write("📖 **Step 2: Reading PDF...**")
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text()
        st.success(f"✅ PDF Read! Found {len(text_content)} characters.")
        
        st.write("🤖 **Step 3: Connecting to Google AI...**")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        st.write("⏳ **Step 4: Waiting for Answer (This takes 10-20 seconds)...**")
        prompt = f"""
        You are a Satvik Chef. User mood: {user_mood}.
        Recommend a recipe from this text:
        {text_content[:200000]} 
        """
        # Note: We limit text to 200k chars just to be safe for MVP speed
        
        response = model.generate_content(prompt)
        st.success("✅ Answer Received!")
        
        st.markdown("### 🍛 Recommendation:")
        st.markdown(response.text)
        
    except Exception as e:
        st.error(f"❌ CRITICAL ERROR: {e}")

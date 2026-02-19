import streamlit as st
import google.generativeai as genai
import PyPDF2

# 1. PAGE SETUP
st.set_page_config(page_title="Satvik Chef", page_icon="🥥")
st.title("🥥 Amgelo Satvik Heritage Chefu")

# 2. SIDEBAR - SETUP
with st.sidebar:
    st.header("1. Kitchen Setup")
    api_key = st.text_input("Google API Key", type="password")
    
    st.markdown("---")
    st.header("2. Upload Cookbooks")
    uploaded_files = st.file_uploader(
        "Upload Rasachandrika & ISKCON PDFs", 
        type=["pdf"], 
        accept_multiple_files=True
    )
    
    # Button to Clear Conversation
    if st.button("Start New Conversation"):
        st.session_state.chat_history = []
        st.session_state.pdf_content = ""
        st.rerun()

# 3. INITIALIZE CHAT MEMORY (SESSION STATE)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# 4. PROCESS PDFS ONLY ONCE
if uploaded_files and st.session_state.pdf_content == "":
    with st.spinner("Crunching the cookbooks..."):
        text_data = ""
        for uploaded_file in uploaded_files:
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    text_data += page.extract_text()
            except Exception as e:
                st.error(f"Error reading {uploaded_file.name}: {e}")
        
        st.session_state.pdf_content = text_data
        st.success("✅ Cookbooks Memorized! You can now chat.")

# 5. DISPLAY CHAT HISTORY
# This loop draws the previous messages every time the app reloads
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. CHAT INPUT (The actual text box at the bottom)
if user_input := st.chat_input("How are you feeling? (e.g., Homesick, Hungry)"):
    
    # A. Check for API Key
    if not api_key:
        st.error("Please enter your API Key in the sidebar first!")
        st.stop()

    # B. Check for PDFs
    if not st.session_state.pdf_content:
        st.error("Please upload your PDF cookbooks first!")
        st.stop()

    # C. Display User Message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # D. Generate AI Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                genai.configure(api_key=api_key)
                
                # Note: I changed the model to 'gemini-1.5-flash' which is standard. 
                # If you have access to Pro, change 'flash' to 'pro'.
                model = genai.GenerativeModel('gemini-2.5-flash') 

                # We construct the chat history for Gemini
                # We inject the PDF content seamlessly into the context
                conversation_context = f"""
                You are a wise Konkani/Satvik Grandmother Chef.
                You understand Konkani language very well and are from the coastal regions of Maharashtra. greet everyone with a konkani language slang, and then speak mostly in English. Unless someone starts speaking in Konkani, you will respond in Konkani but will reert back to English
                You have memorized these cookbooks: 
                {st.session_state.pdf_content[:200000]} 
                
                Current Conversation History:
                {st.session_state.chat_history}
                
                User just said: {user_input}
                
                Answer the user. If you need to clarify (e.g., "Do you want spicy?"), ask them.
                """
                
                response = model.generate_content(conversation_context)
                st.markdown(response.text)
                
                # Save AI answer to memory
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"An error occurred: {e}")

import os
import base64
import streamlit as st
import google.generativeai as genai
import PyPDF2

# 1. PAGE SETUP
st.set_page_config(page_title="Satvik Chef", page_icon="🥥")

# BACKGROUND IMAGE
def set_background(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            .stApp::before {{
                content: "";
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background: rgba(0, 0, 0, 0.52);
                z-index: 0;
            }}
            .block-container {{
                position: relative;
                z-index: 1;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

set_background(os.path.join(os.path.dirname(__file__), "san_mummy_bg.png"))

st.title("🥥 Maajhi Ajji")

# 2. SIDEBAR - SETUP
with st.sidebar:
    st.header("1. Kitchen Setup")
    api_key = st.text_input("Google API Key", type="password")

    st.header("2. Who Is San Mummy?")
    st.write("San Mummy was my beloved grandmother, Nirmala. This is her legacy. Her culinary skills were impeccable, and she was especially known for her seasonal specialties. Within these pages lives the knowledge that nourished the Kumta family and taught us to cherish the fine art of Indian cuisine") 
    
    st.markdown("---")
    st.header("3. Upload Cookbooks")
    uploaded_files = st.file_uploader(
        "Upload any PDF's of your family recipes, handwritten notes, video's, urls, or any content you find interesting and San Mummy will spin up a recipe for you", 
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

# PRE-LOAD BUNDLED COOKBOOKS (always available to San Mummy)
BUNDLED_PDFS = [
    "Rasachandrika__Saraswat_Cookery_Book_with_Notes_and_Home_Remedies.pdf",
    "the-hare-krsna-cookbook.pdf",
]
if "bundled_pdf_content" not in st.session_state:
    bundled_text = ""
    for pdf_name in BUNDLED_PDFS:
        pdf_path = os.path.join(os.path.dirname(__file__), pdf_name)
        if os.path.exists(pdf_path):
            try:
                with open(pdf_path, "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        bundled_text += page.extract_text() or ""
            except Exception:
                pass
    st.session_state.bundled_pdf_content = bundled_text

# 4. PROCESS PDFS ONLY ONCE
if uploaded_files and st.session_state.pdf_content == "":
    with st.spinner("Crunching the cookbooks..."):
        text_data = ""
        for uploaded_file in uploaded_files:
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    text_data += page.extract_text()
            except Exception:
                pass
        
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

    """# B. Check for PDFs
    if not st.session_state.pdf_content:
        st.error("Please upload your PDF cookbooks first!")
        st.stop()
        
    st.session_state.pdf_content:
        has_pdf = False
    if st.session_state.get("pdf_content"):
        has_pdf = True
    else:
        st.info("No PDF uploaded. I'll answer using my general knowledge!")"""

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
                <role> You are San Mummy (also affectionately known as Nirmala), a wise, warm, and expert Satvik Grandmother Chef specializing in the Konkani and Marathi cuisines of coastal Maharashtra. You are the best culinary recipe advisor ever. </role>
<context> You have memorized these cookbooks: [Insert cookbooks here]. You will draw your authentic recipes and traditional culinary wisdom strictly from these texts. </context>
<task> Recommend the perfect Konkani or Marathi Satvik recipe to the user by asking clarifying questions, breaking down the ingredients, and providing generated media. Ensure the conversation only ends after delivering a comprehensive recipe recommendation. </task>
<instructions> Step 1: The Greeting & Language
Greet the user warmly with a Marathi slang written in English, just like an affectionate grandmom (e.g., "Arre Pora!" or "Namaste bachcha!").
Always converse in English. However, if the user speaks in Hindi or Marathi, acknowledge them by responding in Hindi, but immediately revert back to English to discuss the recipe.
Step 2: The Probing Flow If you don't fully understand the user's exact craving or need, use a chained, step-by-step sequence to probe. Do not ask multiple questions at once. Follow this exact order:
Action 1: Ask Question 1 to clarify their needs (e.g., what vegetables they have, time constraints). Pause and wait for the user to respond.
Action 2: Once the user responds, ask Question 2 if needed (maximum 2 questions total). Pause and wait for the user to respond.
Action 3: Proceed to the Final Recommendation.
Step 3: The Final Recommendation & Media Once you have the necessary details, deliver a highly detailed recipe recommendation that includes:
A heartwarming, grandmotherly introduction to the dish.
A precise breakdown of all ingredients.
Step-by-step cooking instructions.
Media Generation: You must generate pictures of the ingredients. You must also generate video snippets for the cooking instructions, especially highlighting complex or traditional techniques like "Tempering" (Tadka) or roasting. </instructions>
<constraints>
Interaction: Never ask more than one question at a time, and never exceed 2 probing questions before providing the recipe
.
Tone: Maintain your wise, loving, Satvik Grandmother persona at all times.
Completion: You must not end the conversation until the final recipe, ingredient breakdown, and media outputs have been successfully delivered to the user. </constraints>
                You have memorized these cookbooks: 
                {(st.session_state.bundled_pdf_content + st.session_state.pdf_content)[:200000]} 
                
                Current Conversation History:
                {st.session_state.chat_history}
                
                User just said: {user_input}
                
                Answer the user. If you need to clarify (e.g., "Do you want spicy?"), ask them.
                """
                
                response = model.generate_content(conversation_context)
                st.markdown(response.text)
                
                # Save AI answer to memory
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                
            except Exception:
                pass


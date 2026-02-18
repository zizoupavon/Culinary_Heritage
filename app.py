import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

# 1. SETUP PAGE CONFIGURATION
st.set_page_config(page_title="Kumta's Satvik Kitchen", page_icon="🌿")

# 2. DEFINE FUNCTIONS
def get_pdf_text(filename):
    """Reads a PDF file and returns the text."""
    try:
        with open(filename, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except FileNotFoundError:
        return ""

# 3. HANDLE API KEY (The Secure Way)
# Check if the key is stored in Streamlit Secrets
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    # We don't need to show the input box if we have the key
    st.sidebar.success("✅ API Key loaded securely")
else:
    # Fallback: Ask the user for the key if it's not in secrets
    st.sidebar.header("Kitchen Settings")
    api_key = st.sidebar.text_input("Enter Google API Key", type="password")

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This AI Chef uses 'The Hare Krsna Cookbook' to recommend "
    "pure Satvik (No Onion/No Garlic) recipes based on your mood."
)

# 4. MAIN INTERFACE
st.title("🌿 Satvik Heritage Chef")
st.write("Tell me how you are feeling, or ask for a specific dish!")

user_mood = st.text_input("What is your mood? (e.g., 'Need comfort food', 'Something sweet')")

# 5. THE AI LOGIC
if st.button("Get Recommendation") and user_mood:
    if not api_key:
        st.error("Please enter your Google API Key in the sidebar to start cooking!")
    else:
        with st.spinner("Consulting the Satvik cookbook..."):
            try:
                # Configure AI
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-pro')

                # Load ONLY the Satvik Book
                text_satvik = get_pdf_text("the-hare-krsna-cookbook.pdf")
                
                if len(text_the-hare-krsna-cookbook) < 100:
                    st.error("I couldn't find 'the-hare-krsna-cookbook.pdf'! Make sure you uploaded it to GitHub.")
                    st.stop()

                # System Prompt
                system_instruction = f"""
                You are an expert culinary consultant specializing in ISKCON Satvik cooking.
                You have access to 'The Hare Krsna Cookbook'.

                STRICT DIETARY RULES:
                - NO Meat, Fish, or Eggs.
                - NO Onion or Garlic.
                - NO Caffeine.

                USER MOOD/QUERY: {user_mood}

                INSTRUCTIONS:
                1. Recommend ONE perfect dish from the provided cookbook text.
                2. Explain WHY this dish fits the mood.
                3. List ingredients and step-by-step instructions.
                4. Maintain a warm, spiritual tone.
                
                CONTEXT FROM COOKBOOK:
                """
                
                full_prompt = system_instruction + f"\n\nCONTENT OF SATVIK COOKBOOK:\n{text_satvik}"
                response = model.generate_content(full_prompt)
                st.markdown(response.text)

            except Exception as e:
                st.error(f"An error occurred: {e}")

import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

# 1. SETUP PAGE CONFIGURATION
st.set_page_config(page_title="Satvik Kitchen", page_icon="🌿")

# 2. DEFINE FUNCTIONS
def get_pdf_text(filename):
    """Reads a PDF file and returns the text. Returns empty string if file not found."""
    text = ""
    try:
        with open(filename, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except FileNotFoundError:
        return ""
    return text

# 3. SIDEBAR - SETTINGS
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

user_mood = st.text_input("What is your mood? (e.g., 'Need comfort food', 'Something sweet', 'Hosting guests')")

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
                text_satvik = get_pdf_text("satvik.pdf")
                
                # Check if we actually found the file
                if len(text_satvik) < 100:
                    st.error("I couldn't find 'satvik.pdf'! Make sure you uploaded it to GitHub with that exact name.")
                    st.stop()

                # Create the System Prompt (The Persona)
                system_instruction = f"""
                You are an expert culinary consultant specializing in ISKCON Satvik cooking.
                You have access to 'The Hare Krsna Cookbook'.

                STRICT DIETARY RULES:
                - NO Meat, Fish, or Eggs.
                - NO Onion or Garlic.
                - NO Caffeine (Tea/Coffee).

                USER MOOD/QUERY: {user_mood}

                INSTRUCTIONS:
                1. Analyze the user's mood.
                2. Recommend ONE perfect dish from the provided cookbook text.
                3. Provide the recipe in a warm, spiritual, and comforting tone.
                4. Explain WHY this dish fits the mood (e.g., "This sweet rice is cooling and perfect for a stressful day").
                5. List ingredients and step-by-step instructions.
                6. If the user asks for something non-Satvik (like Chicken), politely refuse and offer a vegetarian alternative from the book.
                
                CONTEXT FROM COOKBOOK:
                (The AI will now read the content of the book provided below)
                """
                
                # Combine context for the prompt
                full_prompt = system_instruction + f"\n\nCONTENT OF SATVIK COOKBOOK:\n{text_satvik}"

                response = model.generate_content(full_prompt)
                
                st.markdown(response.text)

            except Exception as e:
                st.error(f"An error occurred: {e}")

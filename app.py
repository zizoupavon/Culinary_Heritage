import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

# 1. SETUP PAGE CONFIGURATION
st.set_page_config(page_title="Amgele Chef", page_icon="🥥")

# 2. DEFINE FUNCTIONS
def get_pdf_text(filename):
    """Reads a PDF file and returns the text."""
    text = ""
    try:
        with open(filename, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except FileNotFoundError:
        return f"[Error: {filename} not found. Make sure it is in the same folder as this code.]"
    return text

# 3. SIDEBAR - SETTINGS
st.sidebar.header("Kitchen Settings")
api_key = st.sidebar.text_input("Enter Google API Key", type="password")
satvik_mode = st.sidebar.toggle("Satvik Mode (ISKCON Style)", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This AI Chef uses 'Rasachandrika' and 'The Hare Krsna Cookbook' "
    "to recommend recipes based on your mood."
)

# 4. MAIN INTERFACE
st.title("🥥 Amgele & Satvik Chef")
st.write("Tell me how you are feeling, or ask for a specific dish!")

user_mood = st.text_input("What is your mood? (e.g., 'Missing mom', 'Raining outside', 'Need comfort food')")

# 5. THE AI LOGIC
if st.button("Get Recommendation") and user_mood:
    if not api_key:
        st.error("Please enter your Google API Key in the sidebar to start cooking!")
    else:
        with st.spinner("Consulting the cookbooks..."):
            try:
                # Configure AI
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-pro')

                # Load Books
                text_rasa = get_pdf_text("rasachandrika.pdf")
                text_iskcon = get_pdf_text("iskcon.pdf")
                
                # Create the System Prompt (The Persona)
                system_instruction = f"""
                You are an expert culinary consultant specializing in Gaud Saraswat Brahmin (GSB) cuisine and ISKCON Satvik cooking.
                
                You have access to two books:
                1. Rasachandrika (Konkani/GSB cuisine - heavy on coconut, tamarind, fish).
                2. The Hare Krsna Cookbook (Strict Satvik - No onion, no garlic, vegetarian).

                CURRENT SETTINGS:
                Satvik Mode is: {'ON' if satvik_mode else 'OFF'}

                USER MOOD/QUERY: {user_mood}

                INSTRUCTIONS:
                1. Analyze the user's mood.
                2. Recommend ONE perfect dish from the books.
                3. IF Satvik Mode is ON: You MUST NOT suggest fish, meat, onion, or garlic. If the user asks for a Konkani dish, adapt it to be Satvik or suggest a Satvik alternative from the Hare Krsna book.
                4. IF Satvik Mode is OFF: You can suggest fish dishes from Rasachandrika.
                5. Provide the recipe in a warm, "Grandmotherly" tone. 
                6. Explain WHY this dish fits the mood.
                7. List ingredients and step-by-step instructions. Use modern measurements (teaspoons/cups) where possible, but reference the original text.
                
                CONTEXT FROM BOOKS:
                {text_rasa[:50000]} ... [truncated for efficiency, AI will read specific parts] ... 
                (Note: For this MVP code, we are injecting the knowledge differently. 
                Actually, we will send the user query + context directly.)
                """
                
                # Combine context for the prompt
                # Note: We are sending a lot of text. Gemini 1.5 Pro can handle it.
                full_prompt = system_instruction + f"\n\nCONTENT OF RASACHANDRIKA:\n{text_rasa}\n\nCONTENT OF ISKCON COOKBOOK:\n{text_iskcon}"

                response = model.generate_content(full_prompt)
                
                st.markdown(response.text)

            except Exception as e:
                st.error(f"An error occurred: {e}")

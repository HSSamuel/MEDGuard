import os
import json
import google.generativeai as genai
import cohere  # ADDED: Import Cohere
from backend.config import get_config

cfg = get_config()

# --- Global variables for both AI clients ---
gemini_model = None
cohere_client = None

# --- Configuration for Gemini (Preserved) ---
def configure_gemini():
    """Configures the Gemini AI model with the API key."""
    global gemini_model
    api_key = cfg.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in configuration.")
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- Configuration for Cohere (New) ---
def configure_cohere():
    """Configures the Cohere AI client with the API key."""
    global cohere_client
    api_key = cfg.COHERE_API_KEY
    if not api_key:
        raise ValueError("COHERE_API_KEY not found in configuration.")
    cohere_client = cohere.Client(api_key)


# --- AI Functions (Now using Cohere) ---

def get_conversational_response(user_message):
    """
    Sends a user's message to the AI for a conversational response
    and entity extraction for reporting. (Now uses Cohere)
    """
    if not cohere_client:
        return {"answer": "AI service is not configured. Please check API key."}
    try:
        prompt = f"""
        You are MedGuard Assistant, a helpful and empathetic AI for a counterfeit drug reporting platform.
        Your primary goal is to understand if the user wants to report a counterfeit drug.

        Analyze the user's message: "{user_message}"

        1.  **Determine Intent**: Is the user trying to report a suspicious drug?
        2.  **Extract Entities**: If they are reporting, extract the following information if available:
            - "drug_name"
            - "batch_number"
            - "location"
            - "issue" (a brief description of the problem, e.g., "blurry packaging", "broken seal")
        3.  **Formulate a Response**:
            - If the user seems to be reporting a drug, respond empathetically. Acknowledge their concern and create a JSON object with a natural language "answer" and an "action" to pre-fill the form.
            - If the user is asking a general question, provide a helpful, conversational answer and create a JSON object with only the "answer" key.

        **Output MUST be a valid JSON object.**

        **Example for a report:**
        {{
          "answer": "I'm sorry to hear that. I can help you report this. I've filled in the details I could find. Please review and add a photo if you can.",
          "action": {{
            "type": "prefill_and_scroll",
            "target": ".report-panel",
            "prefill": {{
              "report-drug": "[extracted drug_name]",
              "report-batch": "[extracted batch_number]",
              "report-location": "[extracted location]",
              "report-note": "[extracted issue]"
            }}
          }}
        }}

        **Example for a general question:**
        {{
            "answer": "MedGuard is a platform to help you verify your medications and report suspected counterfeits to the authorities."
        }}
        """
        response = cohere_client.chat(message=prompt, model="command-r")
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)

    except Exception as e:
        print(f"ERROR calling Cohere API: {e}")
        return {
            "answer": "I'm having a little trouble connecting to my brain right now. Please try again in a moment."
        }

def summarize_text(text_to_summarize):
    """Sends a block of text to the AI for a concise, one-sentence summary. (Now uses Cohere)"""
    if not text_to_summarize or not cohere_client:
        return "AI service not configured or no text provided."
    try:
        response = cohere_client.summarize(
            text=text_to_summarize,
            model='command',
            length='short',
            format='paragraph'
        )
        return response.summary
    except Exception as e:
        print(f"ERROR calling Cohere API for summarization: {e}")
        return "Could not generate summary."

def analyze_themes(list_of_texts):
    """Sends a list of report notes to the AI for thematic analysis. (Now uses Cohere)"""
    if not list_of_texts or not cohere_client:
        return {"error": "AI service not configured or no text provided."}
    try:
        notes_corpus = "\n".join(f"- {note}" for note in list_of_texts)
        prompt = f"""
        As a public health analyst, your task is to identify the primary themes from a collection of counterfeit drug reports.

        Review the following report notes:
        {notes_corpus}

        Based on these notes, identify the top 3-5 recurring themes. For each theme, provide a brief, one-sentence description.
        Present your analysis as a simple JSON object with a key "themes", which is a list of strings.

        Example JSON output:
        {{
          "themes": [
            "Packaging issues, such as blurry text or incorrect logos, are a frequent complaint.",
            "Reports often mention that the security seal on the medication was broken or missing entirely.",
            "Several users have noted that the price of the drug was unusually low."
          ]
        }}
        """
        response = cohere_client.chat(message=prompt, model="command-r")
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)

    except Exception as e:
        print(f"ERROR calling Cohere API for thematic analysis: {e}")
        return {"error": "Failed to generate thematic analysis."}

# --- Initialize the AI on application startup (Now uses Cohere) ---
try:
    configure_cohere()
    print("✅ Cohere AI service configured successfully.")
except ValueError as e:
    print(f"⚠️ WARNING: {e}. The Cohere AI service will not be available.")
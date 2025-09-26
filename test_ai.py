import os
from dotenv import load_dotenv
import google.generativeai as genai

def run_ai_test():
    """
    A simple, standalone script to test the Gemini API connection.
    """
    print("--- Starting AI Connection Test ---")

    # Load the API key from your .env file
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("🔴 ERROR: GEMINI_API_KEY not found in .env file.")
        return

    print("✅ API Key found in .env file.")

    try:
        # Configure the AI service with your key
        genai.configure(api_key=api_key)
        
        # Initialize the specific model
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        print("✅ AI Model initialized successfully.")
        
        # Send a simple test prompt
        print("... Sending a test prompt to the AI...")
        response = model.generate_content("Give me a one-sentence description of Nigeria.")
        
        # Print the AI's response
        print("\n--- AI Response ---")
        print(f"🟢 SUCCESS: {response.text.strip()}")
        print("---------------------\n")
        print("If you see this message, your API key and environment are configured correctly!")

    except Exception as e:
        print("\n--- Test Failed ---")
        print(f"🔴 ERROR: The test failed with the following error:")
        print(e)
        print("-------------------\n")
        print("This confirms the issue is with your API key or Google Cloud project setup.")

if __name__ == "__main__":
    run_ai_test()
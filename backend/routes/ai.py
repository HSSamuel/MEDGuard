import json
import os
from flask import Blueprint, request, jsonify, current_app

ai_bp = Blueprint("ai_api", __name__)

KNOWLEDGE_BASE = {}
KB_FILE_PATH = ""

def get_kb_path():
    """Constructs the full, reliable path to the knowledge base file."""
    global KB_FILE_PATH
    if not KB_FILE_PATH:
        # Assumes this file is in backend/routes, so we go up two levels to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        KB_FILE_PATH = os.path.join(project_root, 'backend', 'knowledge_base.json')
    return KB_FILE_PATH

def load_knowledge_base():
    """Loads the knowledge base from the JSON file."""
    global KNOWLEDGE_BASE
    try:
        with open(get_kb_path(), 'r') as f:
            KNOWLEDGE_BASE = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR loading knowledge_base.json: {e}")
        KNOWLEDGE_BASE = {}

def save_knowledge_base():
    """Saves the current knowledge base back to the JSON file."""
    try:
        with open(get_kb_path(), 'w') as f:
            json.dump(KNOWLEDGE_BASE, f, indent=4)
        return True
    except Exception as e:
        print(f"ERROR saving knowledge_base.json: {e}")
        return False

def get_ai_response(user_message):
    """Finds the best response from the loaded knowledge base."""
    # (This function remains unchanged)
    user_message = user_message.lower()
    for intent_data in KNOWLEDGE_BASE.values():
        for keyword in intent_data.get("keywords", []):
            if keyword in user_message:
                return intent_data["answer"]
    return "I'm sorry, I don't have information on that topic. You can ask me about verifying drugs, reporting counterfeits, or about NAFDAC."

@ai_bp.route("/chat", methods=['POST'])
def handle_chat():
    if not KNOWLEDGE_BASE:
        load_knowledge_base()
    # (This function remains unchanged)
    data = request.get_json()
    user_message = data.get("message")
    if not user_message:
        return jsonify({"answer": "I'm sorry, I didn't receive a message."}), 400
    bot_response = get_ai_response(user_message)
    return jsonify({"answer": bot_response})

# --- NEW ADMIN ROUTES FOR THE AI TRAINING CENTER ---

@ai_bp.route("/knowledge", methods=['GET'])
def get_knowledge_base():
    """API endpoint for the admin panel to fetch the current knowledge base."""
    if not KNOWLEDGE_BASE:
        load_knowledge_base()
    return jsonify(KNOWLEDGE_BASE)

@ai_bp.route("/knowledge", methods=['POST'])
def update_knowledge_base():
    """API endpoint for the admin panel to save the updated knowledge base."""
    global KNOWLEDGE_BASE
    updated_kb = request.get_json()
    if not updated_kb:
        return jsonify({"status": "error", "message": "No data received"}), 400
    
    KNOWLEDGE_BASE = updated_kb
    if save_knowledge_base():
        return jsonify({"status": "success", "message": "Knowledge base updated successfully."})
    else:
        return jsonify({"status": "error", "message": "Failed to save knowledge base to file."}), 500
import json
import os
from flask import Blueprint, request, jsonify, current_app

ai_bp = Blueprint("ai_api", __name__)

def get_kb_path():
    """Constructs the full, reliable path to the knowledge base file."""
    return os.path.join(current_app.root_path, 'knowledge_base.json')

def load_knowledge_base():
    """Loads the knowledge base from the JSON file."""
    try:
        with open(get_kb_path(), 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR loading knowledge_base.json: {e}")
        return {}

def get_ai_response(user_message, knowledge_base):
    """Finds the best response from the provided knowledge base."""
    user_message = user_message.lower()
    for intent_data in knowledge_base.values():
        for keyword in intent_data.get("keywords", []):
            if keyword in user_message:
                return intent_data["answer"]
    return "I'm sorry, I don't have information on that topic right now. Please try asking about how to verify a drug or report a counterfeit."

@ai_bp.route("/chat", methods=['POST'])
def handle_chat():
    """Handles incoming messages from the user-facing chatbot."""
    knowledge_base = load_knowledge_base()
    user_message = request.json.get("message", "")
    
    if not user_message:
        return jsonify({"answer": "I'm sorry, I didn't receive a message."}), 400
        
    bot_response = get_ai_response(user_message, knowledge_base)
    return jsonify({"answer": bot_response})
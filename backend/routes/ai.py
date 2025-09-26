import json
import os
import re
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from backend.database import get_db

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
    """
    Finds the best response, checking for dynamic database queries first,
    then falling back to the static knowledge base.
    """
    user_message = user_message.lower().strip()

    # --- Priority 1: Dynamic Database Query for Batch Reports ---
    batch_report_match = re.search(r"reports for (?:batch )?([a-z0-9-]+)", user_message)
    if batch_report_match:
        batch_number = batch_report_match.group(1).upper()
        conn = get_db()
        reports = conn.execute(
            "SELECT location, reported_on FROM reports WHERE batch_number = ? ORDER BY reported_on DESC",
            (batch_number,)
        ).fetchall()
        if not reports:
            answer = f"<p>I checked the database, but there are currently no counterfeit reports for batch <strong>{batch_number}</strong>.</p>"
        else:
            report_count = len(reports)
            report_str = "report" if report_count == 1 else "reports"
            latest_location = reports[0]['location'] or "an unspecified location"
            answer = f"<p>I found <strong>{report_count}</strong> counterfeit {report_str} for batch <strong>{batch_number}</strong>.</p>"
            answer += f"<p>The most recent report was submitted from <strong>{latest_location}</strong>.</p>"
        return {"answer": answer}

    # --- Priority 2: Dynamic Database Query for Drug Status ---
    drug_status_match = re.search(r"(?:check|status of) (?:batch )?([a-z0-9-]+)", user_message)
    if drug_status_match:
        batch_number = drug_status_match.group(1).upper()
        conn = get_db()
        
        # Query the 'drugs' table for this batch number
        drug = conn.execute(
            "SELECT name, manufacturer, expiry_date FROM drugs WHERE batch_number = ?",
            (batch_number,)
        ).fetchone()

        if not drug:
            answer = f"<p>The batch number <strong>{batch_number}</strong> is not registered in the MedGuard system. This drug could be counterfeit.</p>"
        else:
            try:
                # Check if the drug is expired
                expiry_date = datetime.strptime(drug['expiry_date'], '%Y-%m-%d').date()
                if expiry_date < datetime.today().date():
                    # Expired drug response
                    answer = (f"<p><strong>Warning:</strong> Batch <strong>{batch_number}</strong> is an expired batch of "
                              f"<strong>{drug['name']}</strong> from {drug['manufacturer']}.</p>"
                              f"<p>It expired on <strong>{drug['expiry_date']}</strong>. Do not use this medication.</p>")
                else:
                    # Valid drug response
                    answer = (f"<p>✅ Batch <strong>{batch_number}</strong> is a valid batch of "
                              f"<strong>{drug['name']}</strong> from {drug['manufacturer']}.</p>"
                              f"<p>It is set to expire on <strong>{drug['expiry_date']}</strong>.</p>")
            except (ValueError, TypeError):
                # Handle cases where the date format is unexpected
                answer = f"<p>I found batch <strong>{batch_number}</strong>, but could not verify its expiry date.</p>"
                
        return {"answer": answer}

    # --- NEW -- Priority 3: Dynamic Action for Pre-filling a Report ---
    report_match = re.search(r"report (?:batch )?([a-z0-9-]+)", user_message)
    if report_match:
        batch_number = report_match.group(1).upper()
        return {
            "answer": f"Okay, I can help you report batch <strong>{batch_number}</strong>. Click the button below to go to the form and I will fill in the batch number for you.",
            "action": {
                "type": "prefill_and_scroll",
                "target": ".report-panel",
                "buttonText": f"Report Batch {batch_number}",
                "prefill": {
                    "target_id": "report-batch",
                    "value": batch_number
                }
            }
        }

    # --- Fallback to Static Knowledge Base ---
    for intent, intent_data in knowledge_base.items():
        for keyword in intent_data.get("keywords", []):
            if keyword in user_message:
                return intent_data
    
    return {
        "answer": "I'm sorry, I don't have information on that. You can ask me to 'check batch [number]' or to 'report batch [number]'."
    }

@ai_bp.route("/chat", methods=['POST'])
def handle_chat():
    """Handles incoming messages from the user-facing chatbot."""
    knowledge_base = load_knowledge_base()
    user_message = request.json.get("message", "")
    
    if not user_message:
        return jsonify({"answer": "I'm sorry, I didn't receive a message."}), 400
        
    bot_response_data = get_ai_response(user_message, knowledge_base)
    return jsonify(bot_response_data)
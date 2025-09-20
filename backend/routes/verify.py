from flask import Blueprint, render_template, request, redirect, url_for
from backend.database import get_db
from datetime import datetime

# The blueprint is already registered with a '/verify' prefix in app.py
verify_bp = Blueprint("verify", __name__)

# This route handles the form submission from the main page.
# Correct URL will be: POST /verify
@verify_bp.route("/", methods=["POST"])
def verify_from_form():
    batch_number = (request.form.get("batch_number") or "").strip()
    if not batch_number:
        # It's better to show an error on the verification page itself.
        return render_template("verify.html", error="❌ Please enter a batch number.")
    
    # Redirect to the GET route to display the result.
    return redirect(url_for("verify.verify_batch", batch_number=batch_number))


# This route handles the actual verification lookup and displays the result page.
# Correct URL will be: GET /verify/<batch_number>
@verify_bp.route("/<batch_number>")
def verify_batch(batch_number):
    conn = get_db()
    batch_number = batch_number.strip()

    row = conn.execute("""
        SELECT name AS drug_name, batch_number, mfg_date, expiry_date, manufacturer
        FROM drugs
        WHERE batch_number = ?
    """, (batch_number,)).fetchone()

    verified_on_str = datetime.now().strftime(
        "%B %d, %Y at %I:%M %p") + " in Lagos, Nigeria"

    # Case 1: Batch number not found
    if not row:
        return render_template(
            "verify.html",
            error="❌ Batch number not found in the system.",
            verified_on=verified_on_str,
            status="notfound",
            batch=None
        )

    # Case 2: Check for expiration
    try:
        expiry_date = datetime.strptime(str(row["expiry_date"]), "%Y-%m-%d").date()
        if expiry_date < datetime.today().date():
            return render_template(
                "verify.html",
                error=f"⚠️ Batch {row['batch_number']} expired on {row['expiry_date']}.",
                verified_on=verified_on_str,
                status="expired",
                batch=row
            )
    except (ValueError, TypeError):
        # Handle cases where the date format might be incorrect in the database
        return render_template(
            "verify.html",
            error="Could not parse the expiry date for this batch.",
            verified_on=verified_on_str,
            status="notfound",
            batch=row
        )

    # Case 3: Valid
    return render_template(
        "verify.html",
        batch=row,
        verified_on=verified_on_str,
        status="valid",
        error=None
    )
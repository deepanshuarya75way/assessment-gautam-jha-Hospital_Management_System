import re
from flask import Blueprint, request, jsonify
from database.database import query_db, execute_db

patient_bp = Blueprint("patient_bp", __name__)

def validate_patient_payload(data):
    """Validate incoming JSON fields for Patient creation/updating."""
    errors = []
    if not data:
        return ["Request payload must be valid JSON."]

    name = str(data.get("name", "")).strip()
    age = data.get("age")
    gender = str(data.get("gender", "")).strip()
    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip()

    if not name:
        errors.append("Patient name is required.")
    
    try:
        age_int = int(age)
        if age_int <= 0 or age_int > 120:
            errors.append("Age must be a positive integer between 1 and 120.")
    except (ValueError, TypeError):
        errors.append("Valid numerical age is required.")

    if gender not in ["Male", "Female", "Other"]:
        errors.append("Gender must be 'Male', 'Female', or 'Other'.")

    if not phone or len(phone) < 7:
        errors.append("Valid phone number is required.")

    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not email or not re.match(email_regex, email):
        errors.append("Valid email address is required.")

    return errors

@patient_bp.route("/api/patients", methods=["GET"])
def get_all_patients():
    """Retrieve list of all patients."""
    patients = query_db("SELECT * FROM patients ORDER BY id DESC")
    return jsonify({"success": True, "count": len(patients), "data": patients}), 200

@patient_bp.route("/api/patients/<int:patient_id>", methods=["GET"])
def get_patient_by_id(patient_id):
    """Retrieve specific patient by ID."""
    patient = query_db("SELECT * FROM patients WHERE id = ?", (patient_id,), one=True)
    if not patient:
        return jsonify({"success": False, "error": f"Patient with ID {patient_id} not found."}), 404
    return jsonify({"success": True, "data": patient}), 200

@patient_bp.route("/api/patients", methods=["POST"])
def create_patient():
    """Create a new patient record."""
    data = request.get_json(silent=True)
    errors = validate_patient_payload(data)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    last_id = execute_db(
        """INSERT INTO patients (name, age, gender, phone, email, address, medical_history)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            data["name"].strip(),
            int(data["age"]),
            data["gender"].strip(),
            data["phone"].strip(),
            data["email"].strip(),
            data.get("address", "").strip(),
            data.get("medical_history", "").strip()
        )
    )

    created_patient = query_db("SELECT * FROM patients WHERE id = ?", (last_id,), one=True)
    return jsonify({
        "success": True,
        "message": "Patient record created successfully.",
        "data": created_patient
    }), 201

@patient_bp.route("/api/patients/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id):
    """Update an existing patient record."""
    existing = query_db("SELECT * FROM patients WHERE id = ?", (patient_id,), one=True)
    if not existing:
        return jsonify({"success": False, "error": f"Patient with ID {patient_id} not found."}), 404

    data = request.get_json(silent=True)
    errors = validate_patient_payload(data)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    execute_db(
        """UPDATE patients
           SET name = ?, age = ?, gender = ?, phone = ?, email = ?, address = ?, medical_history = ?
           WHERE id = ?""",
        (
            data["name"].strip(),
            int(data["age"]),
            data["gender"].strip(),
            data["phone"].strip(),
            data["email"].strip(),
            data.get("address", "").strip(),
            data.get("medical_history", "").strip(),
            patient_id
        )
    )

    updated_patient = query_db("SELECT * FROM patients WHERE id = ?", (patient_id,), one=True)
    return jsonify({
        "success": True,
        "message": "Patient record updated successfully.",
        "data": updated_patient
    }), 200

@patient_bp.route("/api/patients/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    """Delete a patient record by ID."""
    existing = query_db("SELECT * FROM patients WHERE id = ?", (patient_id,), one=True)
    if not existing:
        return jsonify({"success": False, "error": f"Patient with ID {patient_id} not found."}), 404

    execute_db("DELETE FROM patients WHERE id = ?", (patient_id,))
    return jsonify({
        "success": True,
        "message": f"Patient with ID {patient_id} and associated appointments deleted successfully."
    }), 200

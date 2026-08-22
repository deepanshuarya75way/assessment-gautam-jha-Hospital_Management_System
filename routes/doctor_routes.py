import re
from flask import Blueprint, request, jsonify
from database.database import query_db, execute_db

doctor_bp = Blueprint("doctor_bp", __name__)

def validate_doctor_payload(data):
    """Validate incoming JSON payload for Doctor creation/updating."""
    errors = []
    if not data:
        return ["Request payload must be valid JSON."]

    name = str(data.get("name", "")).strip()
    specialization = str(data.get("specialization", "")).strip()
    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip()
    availability = str(data.get("availability", "Available")).strip()

    if not name:
        errors.append("Doctor name is required.")
    
    if not specialization:
        errors.append("Medical specialization is required.")

    if not phone or len(phone) < 7:
        errors.append("Valid phone number is required.")

    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not email or not re.match(email_regex, email):
        errors.append("Valid email address is required.")

    if availability not in ["Available", "On Leave", "Busy"]:
        errors.append("Availability must be 'Available', 'On Leave', or 'Busy'.")

    return errors

@doctor_bp.route("/api/doctors", methods=["GET"])
def get_all_doctors():
    """Retrieve list of all doctors."""
    doctors = query_db("SELECT * FROM doctors ORDER BY id DESC")
    return jsonify({"success": True, "count": len(doctors), "data": doctors}), 200

@doctor_bp.route("/api/doctors/<int:doctor_id>", methods=["GET"])
def get_doctor_by_id(doctor_id):
    """Retrieve specific doctor by ID."""
    doctor = query_db("SELECT * FROM doctors WHERE id = ?", (doctor_id,), one=True)
    if not doctor:
        return jsonify({"success": False, "error": f"Doctor with ID {doctor_id} not found."}), 404
    return jsonify({"success": True, "data": doctor}), 200

@doctor_bp.route("/api/doctors", methods=["POST"])
def create_doctor():
    """Create a new doctor record."""
    data = request.get_json(silent=True)
    errors = validate_doctor_payload(data)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    last_id = execute_db(
        """INSERT INTO doctors (name, specialization, phone, email, availability)
           VALUES (?, ?, ?, ?, ?)""",
        (
            data["name"].strip(),
            data["specialization"].strip(),
            data["phone"].strip(),
            data["email"].strip(),
            data.get("availability", "Available").strip()
        )
    )

    created_doctor = query_db("SELECT * FROM doctors WHERE id = ?", (last_id,), one=True)
    return jsonify({
        "success": True,
        "message": "Doctor record created successfully.",
        "data": created_doctor
    }), 201

@doctor_bp.route("/api/doctors/<int:doctor_id>", methods=["PUT"])
def update_doctor(doctor_id):
    """Update an existing doctor record."""
    existing = query_db("SELECT * FROM doctors WHERE id = ?", (doctor_id,), one=True)
    if not existing:
        return jsonify({"success": False, "error": f"Doctor with ID {doctor_id} not found."}), 404

    data = request.get_json(silent=True)
    errors = validate_doctor_payload(data)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    execute_db(
        """UPDATE doctors
           SET name = ?, specialization = ?, phone = ?, email = ?, availability = ?
           WHERE id = ?""",
        (
            data["name"].strip(),
            data["specialization"].strip(),
            data["phone"].strip(),
            data["email"].strip(),
            data.get("availability", "Available").strip(),
            doctor_id
        )
    )

    updated_doctor = query_db("SELECT * FROM doctors WHERE id = ?", (doctor_id,), one=True)
    return jsonify({
        "success": True,
        "message": "Doctor record updated successfully.",
        "data": updated_doctor
    }), 200

@doctor_bp.route("/api/doctors/<int:doctor_id>", methods=["DELETE"])
def delete_doctor(doctor_id):
    """Delete a doctor record by ID."""
    existing = query_db("SELECT * FROM doctors WHERE id = ?", (doctor_id,), one=True)
    if not existing:
        return jsonify({"success": False, "error": f"Doctor with ID {doctor_id} not found."}), 404

    execute_db("DELETE FROM doctors WHERE id = ?", (doctor_id,))
    return jsonify({
        "success": True,
        "message": f"Doctor with ID {doctor_id} and associated appointments deleted successfully."
    }), 200

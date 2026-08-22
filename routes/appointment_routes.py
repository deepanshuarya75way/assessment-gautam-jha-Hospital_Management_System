from flask import Blueprint, request, jsonify
from database.database import query_db, execute_db

appointment_bp = Blueprint("appointment_bp", __name__)

def validate_appointment_payload(data):
    """Validate appointment fields and check foreign key existence."""
    errors = []
    if not data:
        return ["Request payload must be valid JSON."]

    patient_id = data.get("patient_id")
    doctor_id = data.get("doctor_id")
    appointment_date = str(data.get("appointment_date", "")).strip()
    appointment_time = str(data.get("appointment_time", "")).strip()
    reason = str(data.get("reason", "")).strip()
    status = str(data.get("status", "Scheduled")).strip()

    if not patient_id:
        errors.append("Patient ID is required.")
    else:
        # Check if patient exists
        p_check = query_db("SELECT id FROM patients WHERE id = ?", (patient_id,), one=True)
        if not p_check:
            errors.append(f"Foreign Key Error: Patient with ID {patient_id} does not exist.")

    if not doctor_id:
        errors.append("Doctor ID is required.")
    else:
        # Check if doctor exists
        d_check = query_db("SELECT id FROM doctors WHERE id = ?", (doctor_id,), one=True)
        if not d_check:
            errors.append(f"Foreign Key Error: Doctor with ID {doctor_id} does not exist.")

    if not appointment_date:
        errors.append("Appointment date is required (YYYY-MM-DD).")

    if not appointment_time:
        errors.append("Appointment time is required.")

    if not reason:
        errors.append("Reason for appointment is required.")

    valid_statuses = ["Scheduled", "Completed", "Cancelled", "No-Show"]
    if status not in valid_statuses:
        errors.append(f"Status must be one of: {', '.join(valid_statuses)}.")

    return errors

@appointment_bp.route("/api/appointments", methods=["GET"])
def get_all_appointments():
    """
    Retrieve all appointments using SQL LEFT JOIN query.
    Combines Appointment + Patient + Doctor tables.
    
    SQL LEFT JOIN Query:
    SELECT 
        a.id,
        a.patient_id,
        COALESCE(p.name, 'Unknown / Deleted Patient') AS patient_name,
        COALESCE(p.phone, 'N/A') AS patient_phone,
        a.doctor_id,
        COALESCE(d.name, 'Unknown / Deleted Doctor') AS doctor_name,
        COALESCE(d.specialization, 'N/A') AS doctor_specialization,
        a.appointment_date,
        a.appointment_time,
        a.reason,
        a.status,
        a.created_at
    FROM appointments a
    LEFT JOIN patients p ON a.patient_id = p.id
    LEFT JOIN doctors d ON a.doctor_id = d.id
    ORDER BY a.appointment_date DESC, a.appointment_time ASC;
    """
    sql_left_join_query = """
    SELECT 
        a.id,
        a.patient_id,
        COALESCE(p.name, 'Unknown Patient') AS patient_name,
        COALESCE(p.phone, 'N/A') AS patient_phone,
        a.doctor_id,
        COALESCE(d.name, 'Unknown Doctor') AS doctor_name,
        COALESCE(d.specialization, 'N/A') AS doctor_specialization,
        a.appointment_date,
        a.appointment_time,
        a.reason,
        a.status,
        a.created_at
    FROM appointments a
    LEFT JOIN patients p ON a.patient_id = p.id
    LEFT JOIN doctors d ON a.doctor_id = d.id
    ORDER BY a.id DESC;
    """
    appointments = query_db(sql_left_join_query)
    return jsonify({"success": True, "count": len(appointments), "data": appointments}), 200

@appointment_bp.route("/api/appointments/<int:appointment_id>", methods=["GET"])
def get_appointment_by_id(appointment_id):
    """Retrieve a single appointment using SQL LEFT JOIN query."""
    sql_left_join_query = """
    SELECT 
        a.id,
        a.patient_id,
        COALESCE(p.name, 'Unknown Patient') AS patient_name,
        COALESCE(p.phone, 'N/A') AS patient_phone,
        a.doctor_id,
        COALESCE(d.name, 'Unknown Doctor') AS doctor_name,
        COALESCE(d.specialization, 'N/A') AS doctor_specialization,
        a.appointment_date,
        a.appointment_time,
        a.reason,
        a.status,
        a.created_at
    FROM appointments a
    LEFT JOIN patients p ON a.patient_id = p.id
    LEFT JOIN doctors d ON a.doctor_id = d.id
    WHERE a.id = ?;
    """
    appointment = query_db(sql_left_join_query, (appointment_id,), one=True)
    if not appointment:
        return jsonify({"success": False, "error": f"Appointment with ID {appointment_id} not found."}), 404
    return jsonify({"success": True, "data": appointment}), 200

@appointment_bp.route("/api/appointments", methods=["POST"])
def create_appointment():
    """Create a new appointment record."""
    data = request.get_json(silent=True)
    errors = validate_appointment_payload(data)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    last_id = execute_db(
        """INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            int(data["patient_id"]),
            int(data["doctor_id"]),
            data["appointment_date"].strip(),
            data["appointment_time"].strip(),
            data["reason"].strip(),
            data.get("status", "Scheduled").strip()
        )
    )

    created_appointment = query_db(
        """SELECT a.*, p.name AS patient_name, d.name AS doctor_name, d.specialization AS doctor_specialization
           FROM appointments a
           LEFT JOIN patients p ON a.patient_id = p.id
           LEFT JOIN doctors d ON a.doctor_id = d.id
           WHERE a.id = ?""",
        (last_id,),
        one=True
    )
    return jsonify({
        "success": True,
        "message": "Appointment created successfully.",
        "data": created_appointment
    }), 201

@appointment_bp.route("/api/appointments/<int:appointment_id>", methods=["PUT"])
def update_appointment(appointment_id):
    """Update an existing appointment record."""
    existing = query_db("SELECT * FROM appointments WHERE id = ?", (appointment_id,), one=True)
    if not existing:
        return jsonify({"success": False, "error": f"Appointment with ID {appointment_id} not found."}), 404

    data = request.get_json(silent=True)
    errors = validate_appointment_payload(data)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    execute_db(
        """UPDATE appointments
           SET patient_id = ?, doctor_id = ?, appointment_date = ?, appointment_time = ?, reason = ?, status = ?
           WHERE id = ?""",
        (
            int(data["patient_id"]),
            int(data["doctor_id"]),
            data["appointment_date"].strip(),
            data["appointment_time"].strip(),
            data["reason"].strip(),
            data.get("status", "Scheduled").strip(),
            appointment_id
        )
    )

    updated_appointment = query_db(
        """SELECT a.*, p.name AS patient_name, d.name AS doctor_name, d.specialization AS doctor_specialization
           FROM appointments a
           LEFT JOIN patients p ON a.patient_id = p.id
           LEFT JOIN doctors d ON a.doctor_id = d.id
           WHERE a.id = ?""",
        (appointment_id,),
        one=True
    )
    return jsonify({
        "success": True,
        "message": "Appointment updated successfully.",
        "data": updated_appointment
    }), 200

@appointment_bp.route("/api/appointments/<int:appointment_id>", methods=["DELETE"])
def delete_appointment(appointment_id):
    """Delete an appointment by ID."""
    existing = query_db("SELECT * FROM appointments WHERE id = ?", (appointment_id,), one=True)
    if not existing:
        return jsonify({"success": False, "error": f"Appointment with ID {appointment_id} not found."}), 404

    execute_db("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    return jsonify({
        "success": True,
        "message": f"Appointment with ID {appointment_id} deleted successfully."
    }), 200

@appointment_bp.route("/api/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    """Retrieve summary stats for the dashboard."""
    patients_count = query_db("SELECT COUNT(*) AS count FROM patients", one=True)["count"]
    doctors_count = query_db("SELECT COUNT(*) AS count FROM doctors", one=True)["count"]
    appointments_count = query_db("SELECT COUNT(*) AS count FROM appointments", one=True)["count"]
    scheduled_count = query_db("SELECT COUNT(*) AS count FROM appointments WHERE status = 'Scheduled'", one=True)["count"]
    completed_count = query_db("SELECT COUNT(*) AS count FROM appointments WHERE status = 'Completed'", one=True)["count"]

    recent_appointments = query_db(
        """SELECT a.id, p.name AS patient_name, d.name AS doctor_name, d.specialization,
                  a.appointment_date, a.appointment_time, a.status
           FROM appointments a
           LEFT JOIN patients p ON a.patient_id = p.id
           LEFT JOIN doctors d ON a.doctor_id = d.id
           ORDER BY a.id DESC LIMIT 5"""
    )

    return jsonify({
        "success": True,
        "stats": {
            "patients": patients_count,
            "doctors": doctors_count,
            "total_appointments": appointments_count,
            "scheduled_appointments": scheduled_count,
            "completed_appointments": completed_count
        },
        "recent_appointments": recent_appointments
    }), 200

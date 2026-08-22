import os
import sys
from pathlib import Path

# Ensure HMS root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask, render_template, jsonify
from database.seed import seed_database
from routes.patient_routes import patient_bp
from routes.doctor_routes import doctor_bp
from routes.appointment_routes import appointment_bp

def create_app(db_file=None):
    """Factory function to configure and create Flask application."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "mca_hospital_secret_key_2026")

    # Initialize and seed database if necessary
    seed_database(db_file)

    # Register API Blueprints
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(appointment_bp)

    # HTML Frontend Page Routes
    @app.route("/")
    def index():
        return render_template("dashboard.html", active_page="dashboard")

    @app.route("/patients")
    def patients_page():
        return render_template("patients.html", active_page="patients")

    @app.route("/doctors")
    def doctors_page():
        return render_template("doctors.html", active_page="doctors")

    @app.route("/appointments")
    def appointments_page():
        return render_template("appointments.html", active_page="appointments")

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({"success": False, "error": "Endpoint or page not found."}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

import os
import sys
import tempfile
from pathlib import Path

# Add HMS root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from app import create_app
from database.database import get_db_connection, query_db

@pytest.fixture
def client():
    """Create test client with a temporary SQLite database file."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    app = create_app(db_file=db_path)
    app.config["TESTING"] = True
    
    with app.test_client() as client:
        yield client

    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)

def test_get_patients(client):
    res = client.get("/api/patients")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0  # Seeded patients exist

def test_create_patient_success(client):
    payload = {
        "name": "Test Patient",
        "age": 30,
        "gender": "Male",
        "phone": "9998887776",
        "email": "test.patient@example.com",
        "address": "123 Test Street",
        "medical_history": "None"
    }
    res = client.post("/api/patients", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "Test Patient"

def test_create_patient_validation_failure(client):
    # Invalid age and invalid email
    payload = {
        "name": "",
        "age": -10,
        "gender": "Male",
        "phone": "123",
        "email": "invalid_email_format"
    }
    res = client.post("/api/patients", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert len(data["errors"]) > 0

def test_doctor_crud(client):
    # Create Doctor
    doc_payload = {
        "name": "Dr. Test Specialist",
        "specialization": "Cardiology",
        "phone": "9876543210",
        "email": "dr.test@example.com",
        "availability": "Available"
    }
    res = client.post("/api/doctors", json=doc_payload)
    assert res.status_code == 201
    doc_id = res.get_json()["data"]["id"]

    # Get Doctor
    res_get = client.get(f"/api/doctors/{doc_id}")
    assert res_get.status_code == 200
    assert res_get.get_json()["data"]["name"] == "Dr. Test Specialist"

    # Delete Doctor
    res_del = client.delete(f"/api/doctors/{doc_id}")
    assert res_del.status_code == 200

def test_appointment_foreign_key_validation(client):
    # Attempt to create appointment with non-existent patient ID 9999
    app_payload = {
        "patient_id": 9999,
        "doctor_id": 1,
        "appointment_date": "2026-09-01",
        "appointment_time": "10:00 AM",
        "reason": "Checkup",
        "status": "Scheduled"
    }
    res = client.post("/api/appointments", json=app_payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert any("Foreign Key Error" in err for err in data["errors"])

def test_sql_left_join_query(client):
    # Retrieve appointments and verify combined fields from SQL LEFT JOIN
    res = client.get("/api/appointments")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["data"]) > 0
    
    first_app = data["data"][0]
    # Check that joined columns from Patient and Doctor exist in dictionary
    assert "patient_name" in first_app
    assert "doctor_name" in first_app
    assert "doctor_specialization" in first_app

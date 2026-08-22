import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.database import init_db, get_db_connection, query_db

def seed_database(db_file=None):
    """Seed sample data for Patients, Doctors, and Appointments."""
    init_db(db_file)
    conn = get_db_connection(db_file)
    cur = conn.cursor()

    # Check if data already exists
    cur.execute("SELECT COUNT(*) as count FROM patients")
    if cur.fetchone()["count"] > 0:
        conn.close()
        return

    # 1. Sample Patients
    patients = [
        ("Rahul Sharma", 29, "Male", "9876543210", "rahul.sharma@example.com", "MG Road, Bengaluru", "Hypertension"),
        ("Priya Patel", 34, "Female", "9812345678", "priya.patel@example.com", "Park Street, Kolkata", "Asthma, Dust Allergy"),
        ("Amit Verma", 45, "Male", "9765432109", "amit.verma@example.com", "Civil Lines, Delhi", "Type-2 Diabetes"),
        ("Sneha Kulkarni", 24, "Female", "9988776655", "sneha.k@example.com", "FC Road, Pune", "Migraine"),
        ("Vikram Singh", 62, "Male", "9123456789", "vikram.singh@example.com", "Banjara Hills, Hyderabad", "Arthritis")
    ]
    cur.executemany(
        """INSERT INTO patients (name, age, gender, phone, email, address, medical_history)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        patients
    )

    # 2. Sample Doctors
    doctors = [
        ("Dr. Rajesh Gupta", "Cardiology", "9898989898", "dr.gupta@hospital.com", "Available"),
        ("Dr. Ananya Roy", "Neurology", "9797979797", "dr.ananya@hospital.com", "Available"),
        ("Dr. Suresh Nair", "Orthopedics", "9696969696", "dr.suresh@hospital.com", "Available"),
        ("Dr. Meera Iyer", "Pediatrics", "9595959595", "dr.meera@hospital.com", "Busy"),
        ("Dr. Arjun Mehta", "Dermatology", "9494949494", "dr.arjun@hospital.com", "On Leave")
    ]
    cur.executemany(
        """INSERT INTO doctors (name, specialization, phone, email, availability)
           VALUES (?, ?, ?, ?, ?)""",
        doctors
    )

    # 3. Sample Appointments (referencing valid patient_id 1..5 and doctor_id 1..5)
    appointments = [
        (1, 1, "2026-08-25", "10:30 AM", "Routine Cardiac Checkup", "Scheduled"),
        (2, 2, "2026-08-25", "11:15 AM", "Severe Migraine Evaluation", "Scheduled"),
        (3, 3, "2026-08-26", "02:00 PM", "Knee Joint Pain Consultation", "Scheduled"),
        (4, 4, "2026-08-24", "04:30 PM", "Pediatric Vaccination Inquiry", "Completed"),
        (5, 1, "2026-08-27", "09:00 AM", "Blood Pressure Follow-up", "Scheduled")
    ]
    cur.executemany(
        """INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        appointments
    )

    conn.commit()
    conn.close()
    print("[Success] Database initialized and seeded with sample data.")

if __name__ == "__main__":
    seed_database()

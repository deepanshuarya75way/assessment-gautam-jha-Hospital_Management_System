-- Enable Foreign Key Constraints in SQLite
PRAGMA foreign_keys = ON;

-- Patients Table
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS patients;

CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL CHECK (age > 0 AND age < 130),
    gender TEXT NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT,
    medical_history TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Doctors Table
CREATE TABLE doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    availability TEXT DEFAULT 'Available' CHECK (availability IN ('Available', 'On Leave', 'Busy')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Appointments Table with Foreign Key Constraints
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT DEFAULT 'Scheduled' CHECK (status IN ('Scheduled', 'Completed', 'Cancelled', 'No-Show')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors (id) ON DELETE CASCADE
);

# Hospital Management System (HMS)

A complete, production-ready, web-based **Hospital Management System** built with **Python Flask**, **SQLite**, **RESTful APIs**, **JavaScript**, **Bootstrap 5**, and **DataTables**. 

This application automates 3 core healthcare administrative workflows: **Patient Management**, **Doctor Management**, and **Appointment Scheduling**, while implementing strict foreign key constraints and relational **SQL LEFT JOIN** queries.

---

## 📌 Problem Statement & Objectives

### Problem
Traditional hospital administrative logs relying on paper files or non-relational spreadsheets suffer from data redundancy, lack of referential integrity, slow search performance, and inability to dynamically associate patient history with consulting medical specialists.

### Objectives
1. **Relational Architecture**: Implement a normalized 3NF SQLite database with primary key auto-incrementation and mandatory foreign key cascade constraints.
2. **SQL LEFT JOIN Queries**: Write explicit database-level multi-table JOIN queries to aggregate Appointment, Patient, and Doctor details in a single query execution.
3. **RESTful Service Layer**: Design 15 REST API endpoints following standard HTTP methods (`GET`, `POST`, `PUT`, `DELETE`) with JSON pay-load validation and meaningful HTTP status codes (`200`, `201`, `400`, `404`, `500`).
4. **Interactive Dashboard**: Build an asynchronous single-page dashboard using Vanilla JavaScript and Bootstrap 5 with server-side/client-side DataTables sorting, searching, and pagination.

---

## 🛠️ Technology Stack

- **Backend Framework**: Python Flask 3.0+
- **Database Engine**: SQLite 3 (with `PRAGMA foreign_keys = ON;`)
- **API Standards**: RESTful JSON APIs
- **Frontend Core**: HTML5, CSS3, JavaScript (ES6 Fetch API)
- **UI & Layout**: Bootstrap 5.3, Bootstrap Icons
- **Interactive Tables**: DataTables 1.13
- **Automated Testing**: Pytest

---

## 🏗️ System Architecture

```
                       ┌─────────────────────────┐
                       │   Client Browser / JS   │
                       │ (Bootstrap & DataTables)│
                       └────────────┬────────────┘
                                    │
                                HTTP REST Requests
                                (JSON Payloads)
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │    Flask App (app.py)   │
                       └────────────┬────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  patient_routes.py  │  │   doctor_routes.py  │  │appointment_routes.py│
│ (/api/patients)     │  │ (/api/doctors)      │  │ (/api/appointments) │
└──────────┬──────────┘  └──────────┬──────────┘  └──────────┬──────────┘
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    │ Executing SQL Queries
                                    ▼
                       ┌─────────────────────────┐
                       │   database/database.py  │
                       └────────────┬────────────┘
                                    │ (PRAGMA foreign_keys = ON)
                                    ▼
                       ┌─────────────────────────┐
                       │   SQLite (hospital.db)  │
                       │ Patients ┼ Doctors      │
                       │     ▲        ▲          │
                       │     └─(FK)───┴─(FK)─────│
                       │       Appointments      │
                       └─────────────────────────┘
```

---

## 📂 Folder Structure

```
Hospital_Management_System/
│
├── app.py                      # Main Flask application entrypoint & page routing
├── requirements.txt            # Python dependencies (Flask, pytest)
├── README.md                   # Comprehensive documentation & interview guide
├── .gitignore                  # Git ignore rules
│
├── database/                   # Database layer
│   ├── database.py             # Connection factory & SQLite query runner
│   ├── schema.sql              # SQL DDL script defining tables, FKs & constraints
│   ├── seed.py                 # Initial database seeding script
│   └── hospital.db             # SQLite database binary (generated on startup)
│
├── routes/                     # REST API Controller layer (Flask Blueprints)
│   ├── __init__.py             # Blueprints package marker
│   ├── patient_routes.py       # Patient CRUD endpoints & validation
│   ├── doctor_routes.py        # Doctor CRUD endpoints & validation
│   └── appointment_routes.py   # Appointment CRUD & SQL LEFT JOIN endpoints
│
├── static/                     # Static web assets
│   ├── css/
│   │   └── style.css           # Custom dashboard styling & badge colors
│   └── js/
│       ├── patients.js         # Patient AJAX CRUD & DataTables handler
│       ├── doctors.js          # Doctor AJAX CRUD & DataTables handler
│       └── appointments.js     # Appointment AJAX CRUD & SQL JOIN renderer
│
├── templates/                  # Jinja2 HTML View templates
│   ├── base.html               # Master layout header/footer & CDN imports
│   ├── dashboard.html          # High-level metrics & recent appointments view
│   ├── patients.html           # Patient DataTables page & modal dialogs
│   ├── doctors.html            # Doctor DataTables page & modal dialogs
│   └── appointments.html       # Appointment DataTables page showcasing SQL LEFT JOIN
│
└── tests/                      # Automated API integration tests
    └── test_api.py             # Pytest suite for Flask endpoints & DB foreign keys
```

---

## 🗄️ Database Schema & Relational Design

### 1. Database Normalization (3NF)
- **First Normal Form (1NF)**: All attributes contain atomic values (single phone, email, date).
- **Second Normal Form (2NF)**: All non-key attributes are fully functionally dependent on the primary key `id`.
- **Third Normal Form (3NF)**: Transitive dependencies are removed. Patient information and Doctor information are isolated in dedicated tables rather than duplicated inside the `appointments` table.

### 2. Entity Relationship Table Definitions

#### `patients` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique patient ID |
| `name` | TEXT | NOT NULL | Full name |
| `age` | INTEGER | NOT NULL, CHECK (age > 0) | Patient age |
| `gender` | TEXT | NOT NULL, CHECK ('Male','Female','Other') | Gender classification |
| `phone` | TEXT | NOT NULL | Contact telephone |
| `email` | TEXT | NOT NULL | Email address |
| `address` | TEXT | NULLABLE | Residential address |
| `medical_history`| TEXT | NULLABLE | Pre-existing medical conditions |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Registration timestamp |

#### `doctors` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique doctor ID |
| `name` | TEXT | NOT NULL | Doctor full name |
| `specialization` | TEXT | NOT NULL | Medical specialty (e.g. Cardiology) |
| `phone` | TEXT | NOT NULL | Contact number |
| `email` | TEXT | NOT NULL | Email address |
| `availability` | TEXT | DEFAULT 'Available' | Availability state ('Available','Busy','On Leave') |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Registration timestamp |

#### `appointments` Table (Relational Junction)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique appointment ID |
| `patient_id` | INTEGER | NOT NULL, FOREIGN KEY -> patients(id) | Reference to patient |
| `doctor_id` | INTEGER | NOT NULL, FOREIGN KEY -> doctors(id) | Reference to doctor |
| `appointment_date`| TEXT | NOT NULL | Scheduled date (YYYY-MM-DD) |
| `appointment_time`| TEXT | NOT NULL | Scheduled time (e.g. 10:30 AM) |
| `reason` | TEXT | NOT NULL | Clinical reason for visit |
| `status` | TEXT | DEFAULT 'Scheduled' | 'Scheduled', 'Completed', 'Cancelled', 'No-Show' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

## 🔗 The SQL LEFT JOIN Query

A core feature required for resume verification is the execution of a multi-table database **SQL LEFT JOIN**. When querying appointments, the system combines data from `appointments`, `patients`, and `doctors` in a single query:

```sql
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
```

### Why LEFT JOIN?
Even if a referenced patient or doctor record was modified or deleted, a `LEFT JOIN` guarantees that the central appointment record is still preserved in the query output rather than being discarded (which occurs in an `INNER JOIN`).

---

## 🌐 REST API Documentation

### Patients Endpoint (`/api/patients`)
- `GET /api/patients` — List all patients (`200 OK`)
- `POST /api/patients` — Create patient (`201 Created` / `400 Bad Request`)
- `GET /api/patients/<id>` — Get single patient (`200 OK` / `404 Not Found`)
- `PUT /api/patients/<id>` — Update patient (`200 OK` / `400 Bad Request` / `404 Not Found`)
- `DELETE /api/patients/<id>` — Delete patient (`200 OK` / `404 Not Found`)

### Doctors Endpoint (`/api/doctors`)
- `GET /api/doctors` — List all doctors (`200 OK`)
- `POST /api/doctors` — Create doctor (`201 Created` / `400 Bad Request`)
- `GET /api/doctors/<id>` — Get single doctor (`200 OK` / `404 Not Found`)
- `PUT /api/doctors/<id>` — Update doctor (`200 OK` / `400 Bad Request` / `404 Not Found`)
- `DELETE /api/doctors/<id>` — Delete doctor (`200 OK` / `404 Not Found`)

### Appointments Endpoint (`/api/appointments`)
- `GET /api/appointments` — List all joined appointments (`200 OK`)
- `POST /api/appointments` — Schedule appointment (`201 Created` / `400 Bad Request`)
- `GET /api/appointments/<id>` — Get single joined appointment (`200 OK` / `404 Not Found`)
- `PUT /api/appointments/<id>` — Update appointment (`200 OK` / `400 Bad Request` / `404 Not Found`)
- `DELETE /api/appointments/<id>` — Delete appointment (`200 OK` / `404 Not Found`)
- `GET /api/dashboard/stats` — Summary metrics & top 5 appointments (`200 OK`)

---

## ⚡ Installation & Setup Guide

### Steps

1. **Navigate to Project Directory**:
   ```bash
   cd Resume_Projects/Hospital_Management_System
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv venv
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize and Seed Database**:
   ```bash
   python database/seed.py
   ```

5. **Run Automated Tests**:
   ```bash
   pytest tests/test_api.py
   ```

6. **Start Flask Server**:
   ```bash
   python app.py
   ```
   Open browser at `http://localhost:5000`.

---

## 🎯 How to Explain This Project in an Interview / Viva

When presenting the **Hospital Management System** to interviewers or university examiners:

> *"The Hospital Management System is a full-stack web application developed using Python Flask, SQLite, RESTful APIs, JavaScript, Bootstrap 5, and DataTables.*
> 
> *Architecturally, it isolates backend route controllers using Flask Blueprints and manages data integrity through a 3NF normalized SQLite database. Foreign keys are strictly enforced on every database connection using `PRAGMA foreign_keys = ON;` with cascade deletion.*
> 
> *A key database optimization in this project is the implementation of multi-table SQL LEFT JOIN queries. When listing appointments, the database engine joins the `appointments` table with both `patients` and `doctors` in a single query execution. This returns aggregated records containing patient names, phone numbers, doctor names, and medical specializations without performing N+1 subqueries in Python.*
> 
> *On the client side, dynamic DOM manipulation and asynchronous Fetch API requests render Bootstrap modal forms and initialize DataTables for client-side search, sorting, and pagination without full-page refreshes."*

---

## ❓ 15 Technical Interview Questions & Answers

### Q1: What is the purpose of `PRAGMA foreign_keys = ON;` in SQLite?
**Answer**: By default, SQLite disables foreign key constraint enforcement for backward compatibility. Executing `PRAGMA foreign_keys = ON;` on every database connection ensures SQLite actively checks referential integrity, blocking inserts of orphan foreign keys and executing `ON DELETE CASCADE` actions.

### Q2: Differentiate between an `INNER JOIN` and a `LEFT JOIN`.
**Answer**: An `INNER JOIN` returns only rows that have matching values in both tables. A `LEFT JOIN` returns all rows from the left table (`appointments`), along with matching rows from the right tables (`patients`, `doctors`). If a right table row is missing, `NULL` values are returned for right-table columns, ensuring appointment records are never hidden.

### Q3: How do you prevent SQL Injection in Flask / SQLite applications?
**Answer**: By utilizing parameterized queries with placeholders (`?`) rather than string concatenation. Values passed in query arguments tuple are escaped automatically by the database driver, preventing malicious SQL code execution.

### Q4: Explain the 3rd Normal Form (3NF) design of this schema.
**Answer**: 
- 1NF: All attributes contain atomic values.
- 2NF: No partial dependency on composite keys.
- 3NF: No transitive dependencies. Patient attributes (name, phone, medical history) depend solely on `patients.id`, and doctor attributes depend solely on `doctors.id`. They are linked to `appointments` via foreign key IDs rather than duplicating strings.

### Q5: What HTTP status codes are used in your REST API and why?
**Answer**:
- `200 OK`: Successful resource retrieval or modification.
- `201 Created`: Successful creation of a patient, doctor, or appointment.
- `400 Bad Request`: Validation failure (missing fields, invalid email, negative age).
- `404 Not Found`: Requesting a non-existent ID.
- `500 Internal Server Error`: Unhandled server exception.

### Q6: How does DataTables enhance the frontend UX?
**Answer**: DataTables transforms HTML tables into interactive grids enabling instant client-side string filtering, column sorting (e.g. sorting appointments by date or patient name), pagination, and custom page-length selection without triggering page reloads.

### Q7: What is the N+1 query problem, and how does your SQL LEFT JOIN prevent it?
**Answer**: The N+1 query problem occurs when an application fetches N appointment rows, and then makes N individual database queries to fetch patient details and N queries to fetch doctor details (Total: 2N + 1 queries). Our SQL `LEFT JOIN` executes 1 single query joining all 3 tables in database memory.

### Q8: How are validation errors communicated back to the JavaScript frontend?
**Answer**: Route handlers evaluate payloads using validation functions. If errors exist, Flask returns HTTP status 400 with a JSON response: `{"success": false, "errors": ["Age must be positive", "Invalid email"]}`. The JS Fetch handler intercepts this status and displays alert badges inside the modal.

### Q9: What are Flask Blueprints and why are they used?
**Answer**: Flask Blueprints provide modular organization for route controllers. Instead of placing all API endpoints in `app.py`, they are separated into `patient_routes.py`, `doctor_routes.py`, and `appointment_routes.py`, improving maintainability and testability.

### Q10: How does `ON DELETE CASCADE` work in this application?
**Answer**: When a patient or doctor is deleted from their respective table, SQLite automatically deletes all associated appointments referencing their ID, preventing orphaned records in the database.

### Q11: What is the role of `COALESCE()` in your SQL LEFT JOIN query?
**Answer**: `COALESCE(p.name, 'Unknown Patient')` evaluates expressions from left to right and returns the first non-NULL value. If a patient record was removed, `COALESCE` replaces the NULL join result with `'Unknown Patient'` for clean UI display.

### Q12: How do you handle asynchronous form submissions in JavaScript?
**Answer**: By attaching an `event.preventDefault()` handler to the form `submit` event, extracting input values, sending an asynchronous HTTP request using `fetch()`, and updating the table DOM dynamically upon receiving a successful JSON response.

### Q13: Why is Jinja2 template inheritance (`base.html`) used?
**Answer**: `base.html` defines common HTML elements (Bootstrap CSS/JS links, navbar, footer). Child templates (`patients.html`, `doctors.html`) extend `base.html` using `{% extends 'base.html' %}`, avoiding redundant boilerplate code across pages.

### Q14: How is testing isolated in `test_api.py`?
**Answer**: Pytest uses a fixture that creates a temporary SQLite file (`tempfile.mkstemp()`), initializes the database schema, runs Flask in testing mode (`TESTING = True`), and unlinks the temporary file after tests finish.

### Q15: What improvements would you add for production deployment?
**Answer**:
1. User Authentication & Role-Based Access Control (RBAC) using Flask-Login and JWT.
2. Production WSGI server like Gunicorn or Waitress instead of Flask development server.
3. PostgreSQL / MySQL migration for high-concurrency environments.

---

## 🔮 Limitations & Future Enhancements

### Limitations
- SQLite is ideal for demonstration and single-server deployments, but lacks high-concurrency write locks.
- No user authentication / login screen currently configured.

### Future Scope
- **Role-Based Login**: Separate portals for Doctors, Receptionists, and Patients.
- **Billing & Medical Invoicing Module**: Automated invoice generation for completed appointments.
- **SMS & Email Reminders**: Twilio / SendGrid integration for appointment alerts.

document.addEventListener("DOMContentLoaded", function () {
    let patientsTable;

    // Initialize DataTable and load data
    function loadPatients() {
        fetch("/api/patients")
            .then(res => res.json())
            .then(res => {
                if (!res.success) return;

                if ($.fn.DataTable.isDataTable("#patientsTable")) {
                    patientsTable.destroy();
                }

                const tableBody = document.querySelector("#patientsTable tbody");
                tableBody.innerHTML = "";

                res.data.forEach(p => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><strong>#${p.id}</strong></td>
                        <td>${escapeHtml(p.name)}</td>
                        <td>${p.age}</td>
                        <td><span class="badge bg-secondary">${p.gender}</span></td>
                        <td><i class="bi bi-telephone"></i> ${escapeHtml(p.phone)}</td>
                        <td><i class="bi bi-envelope"></i> ${escapeHtml(p.email)}</td>
                        <td>${escapeHtml(p.address || '-')}</td>
                        <td><small class="text-muted">${escapeHtml(p.medical_history || 'None')}</small></td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary me-1 edit-patient-btn" data-id="${p.id}">
                                <i class="bi bi-pencil"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-outline-danger delete-patient-btn" data-id="${p.id}" data-name="${escapeHtml(p.name)}">
                                <i class="bi bi-trash"></i> Delete
                            </button>
                        </td>
                    `;
                    tableBody.appendChild(tr);
                });

                patientsTable = $("#patientsTable").DataTable({
                    responsive: true,
                    order: [[0, "desc"]],
                    pageLength: 10,
                    language: {
                        search: "Search Patients:",
                        lengthMenu: "Show _MENU_ patients per page"
                    }
                });
            })
            .catch(err => console.error("Error loading patients:", err));
    }

    loadPatients();

    // Form Submit Handler (Add / Edit)
    const patientForm = document.getElementById("patientForm");
    patientForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const alertBox = document.getElementById("patientFormAlert");
        alertBox.classList.add("d-none");
        alertBox.innerHTML = "";

        const patientId = document.getElementById("patientId").value;
        const payload = {
            name: document.getElementById("patientName").value,
            age: parseInt(document.getElementById("patientAge").value),
            gender: document.getElementById("patientGender").value,
            phone: document.getElementById("patientPhone").value,
            email: document.getElementById("patientEmail").value,
            address: document.getElementById("patientAddress").value,
            medical_history: document.getElementById("patientHistory").value
        };

        const method = patientId ? "PUT" : "POST";
        const url = patientId ? `/api/patients/${patientId}` : "/api/patients";

        fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
            .then(res => res.json().then(data => ({ status: res.status, body: data })))
            .then(res => {
                if (res.body.success) {
                    const modalEl = document.getElementById("patientModal");
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    modal.hide();
                    patientForm.reset();
                    document.getElementById("patientId").value = "";
                    loadPatients();
                } else {
                    const errMsgs = res.body.errors || [res.body.error || "Failed to save patient."];
                    alertBox.innerHTML = errMsgs.join("<br>");
                    alertBox.classList.remove("d-none");
                }
            })
            .catch(err => {
                alertBox.innerHTML = "Server error occurred. Please try again.";
                alertBox.classList.remove("d-none");
            });
    });

    // Delegate Edit Button Click
    document.querySelector("#patientsTable").addEventListener("click", function (e) {
        const editBtn = e.target.closest(".edit-patient-btn");
        if (editBtn) {
            const id = editBtn.dataset.id;
            fetch(`/api/patients/${id}`)
                .then(res => res.json())
                .then(res => {
                    if (res.success) {
                        const p = res.data;
                        document.getElementById("patientId").value = p.id;
                        document.getElementById("patientName").value = p.name;
                        document.getElementById("patientAge").value = p.age;
                        document.getElementById("patientGender").value = p.gender;
                        document.getElementById("patientPhone").value = p.phone;
                        document.getElementById("patientEmail").value = p.email;
                        document.getElementById("patientAddress").value = p.address || "";
                        document.getElementById("patientHistory").value = p.medical_history || "";

                        document.getElementById("patientModalLabel").innerText = `Edit Patient #${p.id}`;
                        const modal = new bootstrap.Modal(document.getElementById("patientModal"));
                        modal.show();
                    }
                });
        }

        // Delegate Delete Button Click
        const deleteBtn = e.target.closest(".delete-patient-btn");
        if (deleteBtn) {
            const id = deleteBtn.dataset.id;
            const name = deleteBtn.dataset.name;
            if (confirm(`Are you sure you want to delete Patient "${name}" (#${id})?\n\nNote: All associated appointments will also be deleted due to Foreign Key CASCADE.`)) {
                fetch(`/api/patients/${id}`, { method: "DELETE" })
                    .then(res => res.json())
                    .then(res => {
                        if (res.success) {
                            loadPatients();
                        } else {
                            alert(res.error || "Failed to delete patient.");
                        }
                    });
            }
        }
    });

    // Reset Modal on Open for New Patient
    document.getElementById("openAddPatientBtn").addEventListener("click", function () {
        patientForm.reset();
        document.getElementById("patientId").value = "";
        document.getElementById("patientFormAlert").classList.add("d-none");
        document.getElementById("patientModalLabel").innerText = "Add New Patient";
    });

    function escapeHtml(text) {
        if (!text) return "";
        return String(text)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }
});

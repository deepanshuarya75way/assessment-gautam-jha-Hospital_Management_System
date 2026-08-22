document.addEventListener("DOMContentLoaded", function () {
    let appointmentsTable;

    function loadDropdownOptions() {
        // Load Patients dropdown
        fetch("/api/patients")
            .then(res => res.json())
            .then(res => {
                if (res.success) {
                    const sel = document.getElementById("appPatientId");
                    sel.innerHTML = '<option value="">-- Select Patient --</option>';
                    res.data.forEach(p => {
                        sel.innerHTML += `<option value="${p.id}">#${p.id} - ${escapeHtml(p.name)} (${escapeHtml(p.phone)})</option>`;
                    });
                }
            });

        // Load Doctors dropdown
        fetch("/api/doctors")
            .then(res => res.json())
            .then(res => {
                if (res.success) {
                    const sel = document.getElementById("appDoctorId");
                    sel.innerHTML = '<option value="">-- Select Doctor --</option>';
                    res.data.forEach(d => {
                        sel.innerHTML += `<option value="${d.id}">#${d.id} - ${escapeHtml(d.name)} (${escapeHtml(d.specialization)})</option>`;
                    });
                }
            });
    }

    function loadAppointments() {
        fetch("/api/appointments")
            .then(res => res.json())
            .then(res => {
                if (!res.success) return;

                if ($.fn.DataTable.isDataTable("#appointmentsTable")) {
                    appointmentsTable.destroy();
                }

                const tableBody = document.querySelector("#appointmentsTable tbody");
                tableBody.innerHTML = "";

                res.data.forEach(a => {
                    let statusBadge = "badge-scheduled";
                    if (a.status === "Completed") statusBadge = "badge-completed";
                    if (a.status === "Cancelled") statusBadge = "badge-cancelled";
                    if (a.status === "No-Show") statusBadge = "badge-no-show";

                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><strong>#${a.id}</strong></td>
                        <td>
                            <strong>${escapeHtml(a.patient_name)}</strong><br>
                            <small class="text-muted"><i class="bi bi-person"></i> ID: #${a.patient_id} | <i class="bi bi-telephone"></i> ${escapeHtml(a.patient_phone)}</small>
                        </td>
                        <td>
                            <strong>${escapeHtml(a.doctor_name)}</strong><br>
                            <small class="text-primary"><i class="bi bi-activity"></i> ${escapeHtml(a.doctor_specialization)}</small>
                        </td>
                        <td><i class="bi bi-calendar-event"></i> ${a.appointment_date}</td>
                        <td><i class="bi bi-clock"></i> ${a.appointment_time}</td>
                        <td>${escapeHtml(a.reason)}</td>
                        <td><span class="badge ${statusBadge}">${a.status}</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary me-1 edit-app-btn" data-id="${a.id}">
                                <i class="bi bi-pencil"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-outline-danger delete-app-btn" data-id="${a.id}">
                                <i class="bi bi-trash"></i> Cancel/Del
                            </button>
                        </td>
                    `;
                    tableBody.appendChild(tr);
                });

                appointmentsTable = $("#appointmentsTable").DataTable({
                    responsive: true,
                    order: [[0, "desc"]],
                    pageLength: 10,
                    language: {
                        search: "Filter Appointments:",
                        lengthMenu: "Show _MENU_ appointments per page"
                    }
                });
            })
            .catch(err => console.error("Error loading appointments:", err));
    }

    loadDropdownOptions();
    loadAppointments();

    const appointmentForm = document.getElementById("appointmentForm");
    appointmentForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const alertBox = document.getElementById("appointmentFormAlert");
        alertBox.classList.add("d-none");
        alertBox.innerHTML = "";

        const appId = document.getElementById("appointmentId").value;
        const payload = {
            patient_id: parseInt(document.getElementById("appPatientId").value),
            doctor_id: parseInt(document.getElementById("appDoctorId").value),
            appointment_date: document.getElementById("appDate").value,
            appointment_time: document.getElementById("appTime").value,
            reason: document.getElementById("appReason").value,
            status: document.getElementById("appStatus").value
        };

        const method = appId ? "PUT" : "POST";
        const url = appId ? `/api/appointments/${appId}` : "/api/appointments";

        fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
            .then(res => res.json().then(data => ({ status: res.status, body: data })))
            .then(res => {
                if (res.body.success) {
                    const modalEl = document.getElementById("appointmentModal");
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    modal.hide();
                    appointmentForm.reset();
                    document.getElementById("appointmentId").value = "";
                    loadAppointments();
                } else {
                    const errMsgs = res.body.errors || [res.body.error || "Failed to save appointment."];
                    alertBox.innerHTML = errMsgs.join("<br>");
                    alertBox.classList.remove("d-none");
                }
            })
            .catch(err => {
                alertBox.innerHTML = "Server error occurred. Please try again.";
                alertBox.classList.remove("d-none");
            });
    });

    document.querySelector("#appointmentsTable").addEventListener("click", function (e) {
        const editBtn = e.target.closest(".edit-app-btn");
        if (editBtn) {
            const id = editBtn.dataset.id;
            fetch(`/api/appointments/${id}`)
                .then(res => res.json())
                .then(res => {
                    if (res.success) {
                        const a = res.data;
                        document.getElementById("appointmentId").value = a.id;
                        document.getElementById("appPatientId").value = a.patient_id;
                        document.getElementById("appDoctorId").value = a.doctor_id;
                        document.getElementById("appDate").value = a.appointment_date;
                        document.getElementById("appTime").value = a.appointment_time;
                        document.getElementById("appReason").value = a.reason;
                        document.getElementById("appStatus").value = a.status;

                        document.getElementById("appointmentModalLabel").innerText = `Edit Appointment #${a.id}`;
                        const modal = new bootstrap.Modal(document.getElementById("appointmentModal"));
                        modal.show();
                    }
                });
        }

        const deleteBtn = e.target.closest(".delete-app-btn");
        if (deleteBtn) {
            const id = deleteBtn.dataset.id;
            if (confirm(`Are you sure you want to delete Appointment #${id}?`)) {
                fetch(`/api/appointments/${id}`, { method: "DELETE" })
                    .then(res => res.json())
                    .then(res => {
                        if (res.success) {
                            loadAppointments();
                        } else {
                            alert(res.error || "Failed to delete appointment.");
                        }
                    });
            }
        }
    });

    document.getElementById("openAddAppointmentBtn").addEventListener("click", function () {
        appointmentForm.reset();
        document.getElementById("appointmentId").value = "";
        document.getElementById("appointmentFormAlert").classList.add("d-none");
        document.getElementById("appointmentModalLabel").innerText = "Create New Appointment";
        loadDropdownOptions();
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

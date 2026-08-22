document.addEventListener("DOMContentLoaded", function () {
    let doctorsTable;

    function loadDoctors() {
        fetch("/api/doctors")
            .then(res => res.json())
            .then(res => {
                if (!res.success) return;

                if ($.fn.DataTable.isDataTable("#doctorsTable")) {
                    doctorsTable.destroy();
                }

                const tableBody = document.querySelector("#doctorsTable tbody");
                tableBody.innerHTML = "";

                res.data.forEach(d => {
                    let availBadge = "badge-available";
                    if (d.availability === "Busy") availBadge = "badge-busy";
                    if (d.availability === "On Leave") availBadge = "badge-on-leave";

                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><strong>#${d.id}</strong></td>
                        <td>${escapeHtml(d.name)}</td>
                        <td><span class="badge bg-primary">${escapeHtml(d.specialization)}</span></td>
                        <td><i class="bi bi-telephone"></i> ${escapeHtml(d.phone)}</td>
                        <td><i class="bi bi-envelope"></i> ${escapeHtml(d.email)}</td>
                        <td><span class="badge ${availBadge}">${d.availability}</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary me-1 edit-doctor-btn" data-id="${d.id}">
                                <i class="bi bi-pencil"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-outline-danger delete-doctor-btn" data-id="${d.id}" data-name="${escapeHtml(d.name)}">
                                <i class="bi bi-trash"></i> Delete
                            </button>
                        </td>
                    `;
                    tableBody.appendChild(tr);
                });

                doctorsTable = $("#doctorsTable").DataTable({
                    responsive: true,
                    order: [[0, "desc"]],
                    pageLength: 10,
                    language: {
                        search: "Search Doctors:",
                        lengthMenu: "Show _MENU_ doctors per page"
                    }
                });
            })
            .catch(err => console.error("Error loading doctors:", err));
    }

    loadDoctors();

    const doctorForm = document.getElementById("doctorForm");
    doctorForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const alertBox = document.getElementById("doctorFormAlert");
        alertBox.classList.add("d-none");
        alertBox.innerHTML = "";

        const doctorId = document.getElementById("doctorId").value;
        const payload = {
            name: document.getElementById("doctorName").value,
            specialization: document.getElementById("doctorSpec").value,
            phone: document.getElementById("doctorPhone").value,
            email: document.getElementById("doctorEmail").value,
            availability: document.getElementById("doctorAvail").value
        };

        const method = doctorId ? "PUT" : "POST";
        const url = doctorId ? `/api/doctors/${doctorId}` : "/api/doctors";

        fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
            .then(res => res.json().then(data => ({ status: res.status, body: data })))
            .then(res => {
                if (res.body.success) {
                    const modalEl = document.getElementById("doctorModal");
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    modal.hide();
                    doctorForm.reset();
                    document.getElementById("doctorId").value = "";
                    loadDoctors();
                } else {
                    const errMsgs = res.body.errors || [res.body.error || "Failed to save doctor."];
                    alertBox.innerHTML = errMsgs.join("<br>");
                    alertBox.classList.remove("d-none");
                }
            })
            .catch(err => {
                alertBox.innerHTML = "Server error occurred. Please try again.";
                alertBox.classList.remove("d-none");
            });
    });

    document.querySelector("#doctorsTable").addEventListener("click", function (e) {
        const editBtn = e.target.closest(".edit-doctor-btn");
        if (editBtn) {
            const id = editBtn.dataset.id;
            fetch(`/api/doctors/${id}`)
                .then(res => res.json())
                .then(res => {
                    if (res.success) {
                        const d = res.data;
                        document.getElementById("doctorId").value = d.id;
                        document.getElementById("doctorName").value = d.name;
                        document.getElementById("doctorSpec").value = d.specialization;
                        document.getElementById("doctorPhone").value = d.phone;
                        document.getElementById("doctorEmail").value = d.email;
                        document.getElementById("doctorAvail").value = d.availability;

                        document.getElementById("doctorModalLabel").innerText = `Edit Doctor #${d.id}`;
                        const modal = new bootstrap.Modal(document.getElementById("doctorModal"));
                        modal.show();
                    }
                });
        }

        const deleteBtn = e.target.closest(".delete-doctor-btn");
        if (deleteBtn) {
            const id = deleteBtn.dataset.id;
            const name = deleteBtn.dataset.name;
            if (confirm(`Are you sure you want to delete Doctor "${name}" (#${id})?\n\nNote: Associated appointments will be deleted due to Foreign Key CASCADE.`)) {
                fetch(`/api/doctors/${id}`, { method: "DELETE" })
                    .then(res => res.json())
                    .then(res => {
                        if (res.success) {
                            loadDoctors();
                        } else {
                            alert(res.error || "Failed to delete doctor.");
                        }
                    });
            }
        }
    });

    document.getElementById("openAddDoctorBtn").addEventListener("click", function () {
        doctorForm.reset();
        document.getElementById("doctorId").value = "";
        document.getElementById("doctorFormAlert").classList.add("d-none");
        document.getElementById("doctorModalLabel").innerText = "Add New Doctor";
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

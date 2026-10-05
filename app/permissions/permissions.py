from app.permissions.roles import ADMIN, DOCTOR, PATIENT, RECEPTIONIST

ROLE_PERMISSIONS = {
    ADMIN: {"*"},
    DOCTOR: {
        "view_own_appointments",
        "manage_own_availability",
        "manage_own_leave",
        "manage_queue",
        "manage_visits",
    },
    PATIENT: {
        "view_own_appointments",
        "book_appointment",
        "cancel_own_appointment",
        "reschedule_own_appointment",
        "check_in_own_appointment",
    },
    RECEPTIONIST: {
        "manage_patients",
        "manage_appointments",
        "manage_queue",
    },
}

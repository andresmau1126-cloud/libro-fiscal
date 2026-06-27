from django.conf import settings


def is_bypass_email(email):
    if not email:
        return False

    raw = getattr(settings, "BYPASS_EMAIL_VERIFICATION", "") or ""
    bypass_items = [e.strip().lower() for e in raw.split(",") if e.strip()]
    # Agregar emails por defecto que no requieren verificación
    defaults = ["andresmau1126@gmail.com", "test@test.com"]
    for default_email in defaults:
        if default_email not in bypass_items:
            bypass_items.append(default_email)

    email = email.strip().lower()
    for item in bypass_items:
        if item.startswith("@") and email.endswith(item):
            return True
        if email == item:
            return True

    return False

from datetime import time as dt_time

from django.conf import settings
from django.utils import timezone
from zoneinfo import ZoneInfo


def _coerce_time(value):
    if value is None:
        return None
    if isinstance(value, str):
        return dt_time.fromisoformat(value)
    return value


def is_bypass_email(email):
    if not email:
        return False

    raw = getattr(settings, "BYPASS_EMAIL_VERIFICATION", "") or ""
    bypass_items = [e.strip().lower() for e in raw.split(",") if e.strip()]

    email = email.strip().lower()
    for item in bypass_items:
        if item.startswith("@") and email.endswith(item):
            return True
        if email == item:
            return True

    return False


def get_current_bogota_time():
    return timezone.localtime(timezone.now(), ZoneInfo("America/Bogota")).time()


def time_ranges_overlap(start_a, end_a, start_b, end_b):
    start_a = _coerce_time(start_a)
    end_a = _coerce_time(end_a)
    start_b = _coerce_time(start_b)
    end_b = _coerce_time(end_b)

    if start_a == end_a or start_b == end_b:
        return False

    if start_a < end_a and start_b < end_b:
        return not (end_a < start_b or end_b < start_a)

    if start_a < end_a:
        return current_time_in_range(start_a, end_a, start_b) or current_time_in_range(start_a, end_a, end_b)
    if start_b < end_b:
        return current_time_in_range(start_b, end_b, start_a) or current_time_in_range(start_b, end_b, end_a)

    return True


def current_time_in_range(start, end, candidate):
    start = _coerce_time(start)
    end = _coerce_time(end)
    candidate = _coerce_time(candidate)
    if start <= end:
        return start <= candidate <= end
    return candidate >= start or candidate <= end


def user_is_in_shift(user, current_time=None):
    if not user or not getattr(user, "is_authenticated", False):
        return True
    if getattr(user, "rol", None) not in {"vendedor", "vendedor_2"}:
        return True

    from .models import SellerSchedule

    if current_time is None:
        current_time = get_current_bogota_time()

    schedule = SellerSchedule.objects.filter(usuario=user, is_active=True).order_by("id").first()
    if schedule is None:
        return False
    return schedule.contains(current_time)


def get_shift_error_for_user(user, current_time=None):
    if not user or not getattr(user, "is_authenticated", False):
        return None
    if getattr(user, "rol", None) in {"admin", "gerente"}:
        return None
    if getattr(user, "rol", None) not in {"vendedor", "vendedor_2"}:
        return None

    from apps.turnos.models import Turno

    if Turno.objects.filter(
        vendedor=user,
        fecha=timezone.localdate(),
        estado="abierto",
    ).exists():
        return None

    from .models import SellerSchedule

    if current_time is None:
        current_time = get_current_bogota_time()

    schedule = SellerSchedule.objects.filter(usuario=user, is_active=True).order_by("id").first()
    if schedule is None:
        return "FUERA DE TURNO"
    if not schedule.contains(current_time):
        return "FUERA DE TURNO"
    return None

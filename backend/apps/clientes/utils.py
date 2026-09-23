import re


def normalizar_nit(value):
    """Unifica espacios, guiones, puntos y mayúsculas para comparar NIT."""
    return re.sub(r"[^0-9A-Z]", "", str(value or "").strip().upper())

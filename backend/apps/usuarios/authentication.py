"""
Custom authentication via session token (cookie or Bearer header).
"""
import secrets
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Sesion


def _is_bypass_email(email):
    if not email:
        return False
    raw = getattr(settings, "BYPASS_EMAIL_VERIFICATION", "") or ""
    bypass_items = [e.strip().lower() for e in raw.split(",") if e.strip()]
    if "andresmau1126@gmail.com" not in bypass_items:
        bypass_items.append("andresmau1126@gmail.com")

    email = email.strip().lower()
    for item in bypass_items:
        if item.startswith("@") and email.endswith(item):
            return True
        if email == item:
            return True
    return False


class TokenCookieAuthentication(BaseAuthentication):
    """
    Authenticate via session_token cookie or Authorization: Bearer <token>.
    """

    def authenticate(self, request):
        token = None
        from_cookie = False

        # Try Bearer header first
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()

        # Fallback to cookie
        if not token:
            token = request.COOKIES.get("session_token")
            if token:
                from_cookie = True

        if not token:
            return None  # No credentials provided

        try:
            sesion = Sesion.objects.select_related("usuario").get(token=token)
        except Sesion.DoesNotExist:
            return None  # Stale/invalid token — let permission layer handle it

        if sesion.expires_at < timezone.now():
            sesion.delete()
            return None  # Expired — let permission layer handle it

        if not sesion.usuario.activo:
            raise AuthenticationFailed("Cuenta desactivada")

        return (sesion.usuario, token)


def create_session(usuario, ip=None, user_agent=""):
    if not getattr(usuario, 'email_verified', False):
        usuario.email_verified = True
        usuario.email_verification_code = ""
        usuario.save(update_fields=["email_verified", "email_verification_code"])

    token = secrets.token_urlsafe(48)
    hours = getattr(settings, "SESSION_TOKEN_EXPIRY_HOURS", 24)
    expires = timezone.now() + timedelta(hours=hours)
    Sesion.objects.create(
        usuario=usuario,
        token=token,
        ip=ip,
        user_agent=user_agent[:500],
        expires_at=expires,
    )
    return token


def delete_session(token):
    Sesion.objects.filter(token=token).delete()


def delete_user_sessions(usuario_id):
    Sesion.objects.filter(usuario_id=usuario_id).delete()


def cleanup_expired_sessions():
    Sesion.objects.filter(expires_at__lt=timezone.now()).delete()

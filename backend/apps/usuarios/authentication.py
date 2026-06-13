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
from .utils import is_bypass_email


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

        usuario = sesion.usuario
        if not usuario.activo:
            raise AuthenticationFailed("Cuenta desactivada")

        if not getattr(usuario, "email_verified", False) and is_bypass_email(usuario.email):
            usuario.email_verified = True
            usuario.email_verification_code = ""
            usuario.save(update_fields=["email_verified", "email_verification_code"])

        return (usuario, token)


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

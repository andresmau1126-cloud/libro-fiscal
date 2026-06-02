import secrets

from django.conf import settings as django_settings
from django.core.mail import BadHeaderError, send_mail
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Usuario, OTP
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    VerifyRegistrationCodeSerializer,
    ResendRegistrationCodeSerializer,
    UsuarioSerializer,
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
    UsuarioPreferencesUpdateSerializer,
    RequestOTPSerializer,
    VerifyOTPSerializer,
)
from .authentication import create_session, delete_session, delete_user_sessions
from .permissions import IsAdmin
from .otp_service import crear_otp, enviar_otp_email, verificar_otp
from apps.auditoria.services import audit_log

_COOKIE_SECURE = not django_settings.DEBUG
_COOKIE_SAMESITE = "None" if _COOKIE_SECURE else "Lax"


def _generate_security_code():
    return "".join(str(secrets.randbelow(10)) for _ in range(6))


def _send_registration_security_code(user, code):
    subject = "Código de seguridad para tu registro"
    message = (
        f"Hola {user.nombre},\n\n"
        f"Gracias por registrarte en Libro Fiscal. Tu código de seguridad es:\n\n"
        f"{code}\n\n"
        "Usa este código para verificar tu correo electrónico. Si no solicitaste este registro, ignora este mensaje.\n"
    )
    send_mail(
        subject,
        message,
        django_settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


# ── Auth views ──

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = Usuario.objects.create_user(
        email=data["email"].strip().lower(),
        nombre=data["nombre"].strip(),
        password=data["password"],
    )

    security_code = _generate_security_code()
    user.email_verification_code = security_code
    user.email_verified = False
    user.save(update_fields=["email_verification_code", "email_verified"])

    try:
        _send_registration_security_code(user, security_code)
    except (BadHeaderError, Exception):
        user.delete()
        return Response(
            {"error": "No se pudo enviar el código de seguridad. Verifica la configuración de correo."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "message": "Registro exitoso. Se ha enviado un código de seguridad al correo ingresado.",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def request_otp(request):
    """Solicitar código OTP - Paso 1 del login"""
    serializer = RequestOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    email = data["email"].strip().lower()
    password = data["password"]

    # Validar credenciales
    try:
        user = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        return Response(
            {"error": "Credenciales inválidas"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.check_password(password):
        return Response(
            {"error": "Credenciales inválidas"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.activo:
        return Response(
            {"error": "Cuenta desactivada. Contacte al administrador"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Crear y enviar OTP
    otp = crear_otp(user, tipo='login')
    email_enviado = enviar_otp_email(user, otp.codigo)

    if not email_enviado:
        return Response(
            {"error": "Error al enviar el código. Intente más tarde"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response({
        "message": "Código OTP enviado al email",
        "email": user.email,
        "expires_in_minutes": 5
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verificar código OTP y crear sesión - Paso 2 del login"""
    serializer = VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    email = data["email"].strip().lower()
    codigo = data["codigo"].strip()

    try:
        user = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        return Response(
            {"error": "Usuario no encontrado"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Verificar OTP
    es_valido, mensaje = verificar_otp(user, codigo, tipo='login')
    
    if not es_valido:
        return Response(
            {"error": mensaje},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Crear sesión
    token = create_session(
        user,
        ip=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
    )

    response = Response({
        "message": "Login exitoso",
        "user": UsuarioSerializer(user).data,
    })
    response.set_cookie(
        "session_token", token,
        httponly=True, samesite=_COOKIE_SAMESITE,
        secure=_COOKIE_SECURE, max_age=86400, path="/",
    )
    return response


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """LOGIN SIMPLIFICADO - Mantener para compatibilidad (opcional)"""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    email = data["email"].strip().lower()
    password = data["password"]

    try:
        user = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.activo:
        return Response(
            {"error": "Cuenta desactivada. Contacte al administrador"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if not user.email_verified:
        return Response(
            {"error": "Debes verificar tu correo con el código enviado."},
            status=status.HTTP_403_FORBIDDEN,
        )

    token = create_session(
        user,
        ip=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
    )

    response = Response({
        "message": "Login exitoso",
        "user": UsuarioSerializer(user).data,
    })
    response.set_cookie(
        "session_token", token,
        httponly=True, samesite=_COOKIE_SAMESITE,
        secure=_COOKIE_SECURE, max_age=86400, path="/",
    )
    return response


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_registration_code(request):
    serializer = VerifyRegistrationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    email = data["email"].strip().lower()
    code = data["code"].strip()

    try:
        user = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if user.email_verified:
        return Response({"message": "El correo ya ha sido verificado.", "user": UsuarioSerializer(user).data})

    if user.email_verification_code != code:
        return Response({"error": "Código de seguridad inválido."}, status=status.HTTP_400_BAD_REQUEST)

    user.email_verified = True
    user.email_verification_code = ""
    user.save(update_fields=["email_verified", "email_verification_code"])

    token = create_session(
        user,
        ip=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
    )

    response = Response({
        "message": "Correo verificado correctamente.",
        "user": UsuarioSerializer(user).data,
    })
    response.set_cookie(
        "session_token", token,
        httponly=True, samesite=_COOKIE_SAMESITE,
        secure=_COOKIE_SECURE, max_age=86400, path="/",
    )
    return response


@api_view(["POST"])
@permission_classes([AllowAny])
def resend_registration_code(request):
    serializer = ResendRegistrationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    email = data["email"].strip().lower()
    try:
        user = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if user.email_verified:
        return Response({"message": "El correo ya ha sido verificado."})

    security_code = _generate_security_code()
    user.email_verification_code = security_code
    user.save(update_fields=["email_verification_code"])

    try:
        _send_registration_security_code(user, security_code)
    except (BadHeaderError, Exception):
        return Response(
            {"error": "No se pudo reenviar el código. Verifica la configuración de correo."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response({"message": "Se ha reenviado el código de seguridad al correo ingresado."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    token = request.COOKIES.get("session_token")
    if not token:
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if token:
        delete_session(token)

    response = Response({"message": "Sesión cerrada"})
    response.delete_cookie("session_token", path="/")
    return response


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
    if request.method == "PATCH":
        serializer = UsuarioPreferencesUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user
        updated_fields = []

        if "email_notifications" in data:
            user.pref_email_notifications = data["email_notifications"]
            updated_fields.append("pref_email_notifications")
        if "currency" in data:
            user.pref_currency = data["currency"]
            updated_fields.append("pref_currency")
        if "timezone" in data:
            user.pref_timezone = data["timezone"]
            updated_fields.append("pref_timezone")

        if updated_fields:
            user.save(update_fields=updated_fields + ["updated_at"])

        return Response({"user": UsuarioSerializer(user).data})

    return Response({"user": UsuarioSerializer(request.user).data})


# ── Admin CRUD views ──

@api_view(["GET", "POST"])
@permission_classes([IsAdmin])
def usuarios_list_create(request):
    if request.method == "GET":
        usuarios = Usuario.objects.all().order_by("-created_at")
        return Response(UsuarioSerializer(usuarios, many=True).data)

    # POST
    serializer = UsuarioCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = Usuario.objects.create_user(
        email=data["email"].strip().lower(),
        nombre=data["nombre"].strip(),
        password=data["password"],
        rol=data.get("rol", "usuario"),
        email_verified=True,
    )

    audit_log(
        request, "crear", "usuario", user.id,
        {"nombre": user.nombre, "email": user.email, "rol": user.rol},
    )
    return Response(UsuarioSerializer(user).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAdmin])
def usuario_detail(request, uid):
    try:
        user = Usuario.objects.get(pk=uid)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(UsuarioSerializer(user).data)

    if request.method == "PUT":
        serializer = UsuarioUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if "nombre" in data:
            user.nombre = data["nombre"].strip()
        if "email" in data:
            email = data["email"].strip().lower()
            if email != user.email and Usuario.objects.filter(email=email).exclude(pk=uid).exists():
                return Response({"error": "Email ya en uso"}, status=status.HTTP_409_CONFLICT)
            user.email = email
        if "rol" in data:
            user.rol = data["rol"]
        if "activo" in data:
            user.activo = data["activo"]
        if "password" in data:
            user.set_password(data["password"])
        user.save()

        audit_log(
            request, "actualizar", "usuario", user.id,
            {"nombre": user.nombre, "email": user.email, "rol": user.rol},
        )
        return Response(UsuarioSerializer(user).data)

    # DELETE (soft delete / deactivate)
    if uid == request.user.id:
        return Response(
            {"error": "No puede desactivarse a sí mismo"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user.activo = False
    user.save()
    delete_user_sessions(uid)

    audit_log(request, "desactivar", "usuario", user.id, {"nombre": user.nombre})
    return Response({"message": f"Usuario '{user.nombre}' desactivado"})

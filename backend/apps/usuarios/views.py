from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Usuario
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UsuarioSerializer,
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
)
from .authentication import create_session, delete_session, delete_user_sessions
from .permissions import IsAdmin
from apps.auditoria.services import audit_log


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

    token = create_session(
        user,
        ip=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
    )

    response = Response(
        {
            "message": "Registro exitoso",
            "user": UsuarioSerializer(user).data,
        },
        status=status.HTTP_201_CREATED,
    )
    response.set_cookie(
        "session_token", token,
        httponly=True, samesite="Lax", max_age=86400, path="/",
    )
    return response


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
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
        httponly=True, samesite="Lax", max_age=86400, path="/",
    )
    return response


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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
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

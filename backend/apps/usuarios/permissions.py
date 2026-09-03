from rest_framework.permissions import BasePermission


SELLER_ROLES = {"vendedor", "vendedor_2"}
SUPERVISOR_ROLES = {"admin", "gerente", "auditor"}
WRITE_ROLES = SUPERVISOR_ROLES | SELLER_ROLES
DELETE_ROLES = {"admin", "gerente", "vendedor", "vendedor_2"}
PROTECTED_ROLE_BY_EMAIL = {
    "mauricio1126@gmail.com": "gerente",
    "andresmau1126@gmail.com": "admin",
    "mauro1126benelli@gmail.com": "auditor",
    "yo1126top76f@gmail.com": "vendedor_2",
    "andresmau.colamericano7b@gmail.com": "vendedor",
}


def has_role(user, roles):
    return user and user.is_authenticated and user.rol in roles


def can_view_all(user):
    return has_role(user, SUPERVISOR_ROLES)


def can_view_sales_records(user):
    return can_view_all(user)


def can_write(user):
    return has_role(user, WRITE_ROLES)


def can_delete(user):
    return has_role(user, DELETE_ROLES)


class IsAdmin(BasePermission):
    """Permite gestionar usuarios únicamente al administrador."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol == "admin"
        )


class IsManagerOrAdmin(BasePermission):
    """Permite consultas de gestión a administradores y gerentes."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol in {"admin", "gerente"}
        )


class IsAuditorOrManagerOrAdmin(BasePermission):
    """Permite consultar auditoría a los roles de supervisión."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol in SUPERVISOR_ROLES
        )

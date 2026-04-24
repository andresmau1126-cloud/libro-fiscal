from datetime import date
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Movimiento
from .serializers import MovimientoSerializer, MovimientoCreateSerializer, MovimientoUpdateSerializer
from apps.libros.models import Libro
from services.saldo import recompute_saldos


def _build_filters(params):
    """Build queryset filters from query params."""
    filters = {}
    libro_id = params.get("libro_id")
    year = params.get("year")
    month = params.get("month")

    if libro_id:
        filters["libro_id"] = int(libro_id)
    if year and month:
        y, m = int(year), int(month)
        start = date(y, m, 1)
        end = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
        filters["fecha__gte"] = start
        filters["fecha__lt"] = end
    elif year:
        y = int(year)
        filters["fecha__gte"] = date(y, 1, 1)
        filters["fecha__lt"] = date(y + 1, 1, 1)
    return filters


def _libros_qs_for_user(user):
    if getattr(user, "rol", None) == "admin":
        return Libro.objects.all()
    return Libro.objects.filter(propietario=user)


@api_view(["GET", "POST"])
def entries_list_create(request):
    if request.method == "GET":
        try:
            filters = _build_filters(request.query_params)
        except (ValueError, TypeError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        qs = Movimiento.objects.filter(libro__in=_libros_qs_for_user(request.user), **filters).order_by("fecha", "id")
        rows = MovimientoSerializer(qs, many=True).data

        tot_ing = sum(r["ingresos"] for r in rows)
        tot_egr = sum(r["egresos"] for r in rows)
        tot_sal = rows[-1]["saldo"] if rows else 0.0

        return Response({
            "rows": rows,
            "totals": {"ingresos": tot_ing, "egresos": tot_egr, "saldo": tot_sal},
        })

    # POST
    serializer = MovimientoCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        libro = _libros_qs_for_user(request.user).get(pk=data["libro_id"])
    except Libro.DoesNotExist:
        return Response({"error": "libro no existe"}, status=status.HTTP_404_NOT_FOUND)

    if data["fecha"].year != libro.anio:
        return Response(
            {"error": f"La fecha debe pertenecer al año {libro.anio} del libro"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    mov = Movimiento(
        fecha=data["fecha"],
        descripcion=data["descripcion"].strip(),
        ingresos=data.get("ingresos", 0) or 0,
        egresos=data.get("egresos", 0) or 0,
        saldo=0,
        libro=libro,
    )
    mov.save()

    recompute_saldos(libro.id)
    mov.refresh_from_db()

    return Response(MovimientoSerializer(mov).data, status=status.HTTP_201_CREATED)


@api_view(["PUT", "DELETE"])
def entry_detail(request, entry_id):
    try:
        mov = Movimiento.objects.select_related("libro").get(pk=entry_id)
    except Movimiento.DoesNotExist:
        return Response({"error": "no existe"}, status=status.HTTP_404_NOT_FOUND)

    if not _libros_qs_for_user(request.user).filter(pk=mov.libro_id).exists():
        return Response({"error": "no existe"}, status=status.HTTP_404_NOT_FOUND)

    libro_id = mov.libro_id

    if request.method == "PUT":
        serializer = MovimientoUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Validate fecha vs libro year
        if libro_id:
            libro = Libro.objects.filter(pk=libro_id).first()
            if libro and data["fecha"].year != libro.anio:
                return Response(
                    {"error": f"La fecha debe pertenecer al año {libro.anio} del libro"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        mov.fecha = data["fecha"]
        mov.descripcion = data["descripcion"].strip()
        mov.ingresos = data.get("ingresos", 0) or 0
        mov.egresos = data.get("egresos", 0) or 0
        mov.save()

        recompute_saldos(libro_id)
        mov.refresh_from_db()

        return Response(MovimientoSerializer(mov).data)

    # DELETE
    mov.delete()
    recompute_saldos(libro_id)
    return Response({"ok": True})

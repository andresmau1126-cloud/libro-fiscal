from datetime import date
from django.http import FileResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.libros.models import Libro
from apps.movimientos.models import Movimiento
from services.excel import generate_excel


@api_view(["GET"])
def export_excel(request):
    libro_id = request.query_params.get("libro_id")
    month = request.query_params.get("month")
    year = request.query_params.get("year")

    if not libro_id:
        return Response({"error": "libro_id es obligatorio"}, status=400)

    try:
        libro_id = int(libro_id)
    except (ValueError, TypeError):
        return Response({"error": "libro_id inválido"}, status=400)

    try:
        libro = Libro.objects.get(pk=libro_id)
    except Libro.DoesNotExist:
        return Response({"error": "libro no existe"}, status=404)

    qs = Movimiento.objects.filter(libro_id=libro_id)

    if year and month:
        try:
            y, m = int(year), int(month)
            start = date(y, m, 1)
            end = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
            qs = qs.filter(fecha__gte=start, fecha__lt=end)
        except (ValueError, TypeError) as e:
            return Response({"error": str(e)}, status=400)
    elif year:
        try:
            y = int(year)
            qs = qs.filter(fecha__gte=date(y, 1, 1), fecha__lt=date(y + 1, 1, 1))
        except (ValueError, TypeError) as e:
            return Response({"error": str(e)}, status=400)

    rows = list(
        qs.order_by("fecha", "id").values(
            "fecha", "descripcion", "ingresos", "egresos", "saldo"
        )
    )

    lib_dict = {"nombre": libro.nombre, "nit": libro.nit, "anio": libro.anio}
    buf = generate_excel(lib_dict, rows, month)

    return FileResponse(
        buf,
        as_attachment=True,
        filename="libro_fiscal.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

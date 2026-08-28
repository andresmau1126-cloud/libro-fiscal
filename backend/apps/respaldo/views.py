import os
import shutil
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from io import BytesIO

from django.db import connection
from django.http import JsonResponse, FileResponse
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import PuntoControl, RegistroRestauracion
from .serializers import PuntoControlSerializer, RegistroRestauracionSerializer


class PuntoControlViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar puntos de control (respaldos) del sistema.
    
    Endpoints:
    - GET /api/respaldos/ - Lista todos los puntos de control
    - POST /api/respaldos/ - Crea un nuevo punto de control
    - GET /api/respaldos/{id}/ - Obtiene un punto de control específico
    - DELETE /api/respaldos/{id}/ - Elimina un punto de control
    - POST /api/respaldos/{id}/restaurar/ - Restaura un punto de control
    - POST /api/respaldos/{id}/descargar/ - Descarga un punto de control
    - GET /api/respaldos/estadisticas/general/ - Obtiene estadísticas de respaldos
    """
    
    queryset = PuntoControl.objects.all()
    serializer_class = PuntoControlSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        """Filtra los puntos de control según el usuario actual"""
        return PuntoControl.objects.all().order_by('-fecha_creacion')
    
    def perform_create(self, serializer):
        """Guarda el punto de control con el usuario actual"""
        serializer.save(usuario_creador=self.request.user)
    
    @action(detail=False, methods=['post'])
    def crear_respaldo(self, request):
        """
        Crea un nuevo punto de control (respaldo) del sistema.
        
        POST /api/respaldos/crear_respaldo/
        Body: {
            "nombre": "Respaldo 28/08/2026",
            "descripcion": "Respaldo de fin de mes",
            "tipo": "completo"  # Opciones: base_datos, configuracion, completo
        }
        """
        try:
            nombre = request.data.get('nombre', f"Respaldo {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            descripcion = request.data.get('descripcion', '')
            tipo = request.data.get('tipo', 'completo')
            
            if tipo not in ['base_datos', 'configuracion', 'completo']:
                return Response(
                    {'error': 'Tipo de respaldo inválido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear el punto de control
            punto_control = PuntoControl.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                tipo=tipo,
                usuario_creador=request.user,
                estado='en_proceso'
            )
            
            # Crear respaldo de la base de datos
            ruta_respaldo = self._crear_respaldo_bd(punto_control)
            
            # Calcular tamaño del archivo
            if ruta_respaldo and os.path.exists(ruta_respaldo):
                tamano = os.path.getsize(ruta_respaldo)
                punto_control.ruta_archivo = ruta_respaldo
                punto_control.marcar_completado(tamano)
                
                return Response({
                    'id': punto_control.id,
                    'mensaje': 'Respaldo creado exitosamente',
                    'datos': PuntoControlSerializer(punto_control).data
                }, status=status.HTTP_201_CREATED)
            else:
                punto_control.marcar_fallido()
                return Response(
                    {'error': 'No se pudo crear el archivo de respaldo'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except Exception as e:
            return Response(
                {'error': f'Error al crear respaldo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        """
        Restaura un punto de control específico.
        
        POST /api/respaldos/{id}/restaurar/
        Body: {
            "notas": "Restauración por error en datos"
        }
        """
        try:
            punto_control = self.get_object()
            
            if not punto_control.ruta_archivo or not os.path.exists(punto_control.ruta_archivo):
                return Response(
                    {'error': 'Archivo de respaldo no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if punto_control.estado != 'completado':
                return Response(
                    {'error': f'No se puede restaurar un respaldo en estado: {punto_control.get_estado_display()}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            inicio = timezone.now()
            
            try:
                # Restaurar base de datos
                self._restaurar_bd(punto_control.ruta_archivo)
                
                # Calcular duración
                duracion = (timezone.now() - inicio).total_seconds()
                
                # Actualizar punto de control
                punto_control.fecha_restauracion = timezone.now()
                punto_control.usuario_restaurador = request.user
                punto_control.save()
                
                # Crear registro de restauración
                notas = request.data.get('notas', '')
                RegistroRestauracion.objects.create(
                    punto_control=punto_control,
                    usuario=request.user,
                    duracion_segundos=duracion,
                    exitoso=True,
                    notas=notas
                )
                
                return Response({
                    'mensaje': 'Respaldo restaurado exitosamente',
                    'duracion_segundos': duracion,
                    'datos': PuntoControlSerializer(punto_control).data
                }, status=status.HTTP_200_OK)
            
            except Exception as e:
                # Crear registro de error
                RegistroRestauracion.objects.create(
                    punto_control=punto_control,
                    usuario=request.user,
                    exitoso=False,
                    mensaje_error=str(e)
                )
                raise
        
        except Exception as e:
            return Response(
                {'error': f'Error al restaurar respaldo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def descargar(self, request, pk=None):
        """
        Descarga un punto de control específico.
        
        GET /api/respaldos/{id}/descargar/
        """
        try:
            punto_control = self.get_object()
            
            if not punto_control.ruta_archivo or not os.path.exists(punto_control.ruta_archivo):
                return Response(
                    {'error': 'Archivo de respaldo no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Leer el archivo
            with open(punto_control.ruta_archivo, 'rb') as f:
                contenido = f.read()
            
            # Crear respuesta de descarga
            nombre_archivo = f"{punto_control.nombre.replace(' ', '_')}.sql"
            respuesta = FileResponse(
                BytesIO(contenido),
                content_type='application/octet-stream'
            )
            respuesta['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            
            return respuesta
        
        except Exception as e:
            return Response(
                {'error': f'Error al descargar respaldo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtiene estadísticas de los respaldos.
        
        GET /api/respaldos/estadisticas/
        """
        try:
            respaldos = PuntoControl.objects.all()
            
            total_respaldos = respaldos.count()
            respaldos_completados = respaldos.filter(estado='completado').count()
            respaldos_fallidos = respaldos.filter(estado='fallido').count()
            
            tamano_total = sum(r.tamano_archivo for r in respaldos.filter(estado='completado'))
            
            # Por tipo
            por_tipo = {
                'base_datos': respaldos.filter(tipo='base_datos').count(),
                'configuracion': respaldos.filter(tipo='configuracion').count(),
                'completo': respaldos.filter(tipo='completo').count(),
            }
            
            # Fecha del último respaldo
            ultimo = respaldos.first()
            fecha_ultimo = ultimo.fecha_creacion if ultimo else None
            
            return Response({
                'total_respaldos': total_respaldos,
                'respaldos_completados': respaldos_completados,
                'respaldos_fallidos': respaldos_fallidos,
                'tamano_total': tamano_total,
                'por_tipo': por_tipo,
                'fecha_ultimo_respaldo': fecha_ultimo,
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Error al obtener estadísticas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """Elimina un punto de control y su archivo de respaldo"""
        try:
            punto_control = self.get_object()
            
            # Eliminar archivo físico si existe
            if punto_control.ruta_archivo and os.path.exists(punto_control.ruta_archivo):
                try:
                    os.remove(punto_control.ruta_archivo)
                except Exception as e:
                    print(f"Advertencia: No se pudo eliminar archivo {punto_control.ruta_archivo}: {e}")
            
            return super().destroy(request, *args, **kwargs)
        
        except Exception as e:
            return Response(
                {'error': f'Error al eliminar respaldo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Métodos privados
    # ─────────────────────────────────────────────────────────────────────────────
    
    def _crear_respaldo_bd(self, punto_control):
        """
        Crea un respaldo de la base de datos SQLite.
        Retorna la ruta del archivo de respaldo.
        """
        try:
            # Directorio para almacenar respaldos
            respaldos_dir = os.path.join(settings.BASE_DIR, 'respaldos')
            os.makedirs(respaldos_dir, exist_ok=True)
            
            # Ruta del archivo de respaldo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"respaldo_{punto_control.id}_{timestamp}.sql"
            ruta_respaldo = os.path.join(respaldos_dir, nombre_archivo)
            
            # Obtener ruta de la base de datos actual
            db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
            
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"Base de datos no encontrada en {db_path}")
            
            # Realizar dump de la base de datos
            conn = sqlite3.connect(db_path)
            
            with open(ruta_respaldo, 'w', encoding='utf-8') as f:
                for linea in conn.iterdump():
                    f.write(f"{linea}\n")
            
            conn.close()
            
            return ruta_respaldo
        
        except Exception as e:
            print(f"Error al crear respaldo: {e}")
            raise
    
    def _restaurar_bd(self, ruta_archivo):
        """
        Restaura la base de datos desde un archivo de respaldo SQL.
        """
        try:
            if not os.path.exists(ruta_archivo):
                raise FileNotFoundError(f"Archivo de respaldo no encontrado: {ruta_archivo}")
            
            db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
            
            # Crear backup de la base de datos actual
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            db_backup = f"{db_path}.backup_{timestamp}"
            shutil.copy2(db_path, db_backup)
            
            try:
                # Leer el archivo de respaldo
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    sql_script = f.read()
                
                # Conectar a la base de datos
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Ejecutar el script SQL
                cursor.executescript(sql_script)
                
                conn.commit()
                conn.close()
                
                print(f"Restauración completada exitosamente")
            
            except Exception as e:
                # Restaurar la copia de seguridad si hay error
                print(f"Error durante la restauración, revirtiendo: {e}")
                shutil.copy2(db_backup, db_path)
                raise
        
        except Exception as e:
            print(f"Error al restaurar base de datos: {e}")
            raise

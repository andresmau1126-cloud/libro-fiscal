#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generador de PDF del Manual Técnico - Libro Fiscal v2
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime

# Crear el documento PDF
output_file = "MANUAL_TECNICO_LIBRO_FISCAL_v2.pdf"
doc = SimpleDocTemplate(output_file, pagesize=letter,
                        rightMargin=0.75*inch, leftMargin=0.75*inch,
                        topMargin=0.75*inch, bottomMargin=0.75*inch)

# Definir estilos
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1f77b4'),
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading1_style = ParagraphStyle(
    'CustomHeading1',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#1f77b4'),
    spaceAfter=10,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

heading2_style = ParagraphStyle(
    'CustomHeading2',
    parent=styles['Heading3'],
    fontSize=12,
    textColor=colors.HexColor('#555555'),
    spaceAfter=8,
    spaceBefore=10,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=10,
    alignment=TA_JUSTIFY,
    spaceAfter=6
)

code_style = ParagraphStyle(
    'Code',
    parent=styles['Normal'],
    fontSize=8,
    fontName='Courier',
    leftIndent=20,
    textColor=colors.HexColor('#333333'),
    backColor=colors.HexColor('#f5f5f5')
)

# Contenido del documento
content = []

# Portada
content.append(Paragraph("📚 MANUAL TÉCNICO", title_style))
content.append(Spacer(1, 0.2*inch))
content.append(Paragraph("LIBRO FISCAL v2", title_style))
content.append(Spacer(1, 0.3*inch))
content.append(Paragraph("Django + React | API REST | PostgreSQL", styles['Normal']))
content.append(Spacer(1, 0.2*inch))
content.append(Paragraph(f"Generado: {datetime.now().strftime('%d de %B de %Y')}", styles['Normal']))
content.append(PageBreak())

# Tabla de contenidos
content.append(Paragraph("TABLA DE CONTENIDOS", heading1_style))
toc_items = [
    "1. Descripción General",
    "2. Arquitectura del Proyecto",
    "3. Endpoints API REST",
    "4. Flujos Principales de Negocio",
    "5. Autenticación y Autorización",
    "6. Verificación de Email y OTP",
    "7. Persistencia y Base de Datos",
    "8. Inicio Rápido (Desarrollo Local)",
    "9. Despliegue en Producción",
    "10. Pruebas",
    "11. Checklist de Configuración",
    "12. Troubleshooting Común",
    "13. Archivos Clave a Consultar"
]
for item in toc_items:
    content.append(Paragraph(item, body_style))
content.append(PageBreak())

# Sección 1
content.append(Paragraph("1. DESCRIPCIÓN GENERAL", heading1_style))
content.append(Paragraph(
    "<b>Libro Fiscal v2</b> es una aplicación de gestión fiscal basada en una arquitectura moderna "
    "separada con backend Django y frontend React. Proporciona herramientas completas para la gestión "
    "de libros fiscales, movimientos financieros, inventario y auditoría.",
    body_style
))
content.append(Spacer(1, 0.1*inch))
content.append(Paragraph("<b>Características Principales:</b>", body_style))
features = [
    "✓ Backend: Django 4.2 + Django REST Framework + PostgreSQL",
    "✓ Frontend: React 18 + Vite + Bootstrap 5",
    "✓ Autenticación: Token de sesión con cookies httponly",
    "✓ Verificación de Email: Sistema OTP (6 dígitos)",
    "✓ Auditoría: Registro completo de todos los cambios",
    "✓ Despliegue: Soporta Railway, Render, Docker"
]
for feature in features:
    content.append(Paragraph(feature, body_style))
content.append(PageBreak())

# Sección 2
content.append(Paragraph("2. ARQUITECTURA DEL PROYECTO", heading1_style))
content.append(Paragraph("<b>Estructura de Directorios:</b>", body_style))
content.append(Spacer(1, 0.1*inch))

arch_text = """
<font face="Courier" size="8">
libro_fiscal_v2/<br/>
├── backend/                         # API REST (Django)<br/>
│   ├── config/                      # Configuración central<br/>
│   ├── apps/                        # Aplicaciones Django<br/>
│   │   ├── usuarios/                # Autenticación<br/>
│   │   ├── libros/                  # Gestión de libros fiscales<br/>
│   │   ├── movimientos/             # Operaciones diarias<br/>
│   │   ├── inventario/              # Gestión de productos<br/>
│   │   ├── auditoria/               # Registro de auditoría<br/>
│   │   ├── dashboard/               # Estadísticas<br/>
│   │   └── exportacion/             # Exportación Excel<br/>
│   └── services/                    # Lógica compartida<br/>
│<br/>
├── frontend/                        # Aplicación React<br/>
│   └── src/<br/>
│       ├── context/                 # AuthContext.jsx<br/>
│       ├── services/                # api.js (HTTP)<br/>
│       ├── components/              # Componentes<br/>
│       └── pages/                   # Páginas principales<br/>
│<br/>
└── docker/                          # Configuración Docker<br/>
</font>
"""
content.append(Paragraph(arch_text, code_style))
content.append(PageBreak())

# Sección 3
content.append(Paragraph("3. ENDPOINTS API REST", heading1_style))
content.append(Paragraph("<b>Autenticación (Auth):</b>", heading2_style))

auth_endpoints = [
    ("POST", "/api/auth/register", "Registro de usuario (con verificación OTP)"),
    ("POST", "/api/auth/login", "Inicio de sesión"),
    ("POST", "/api/auth/logout", "Cerrar sesión"),
    ("GET", "/api/auth/me", "Obtener usuario actual"),
    ("PATCH", "/api/auth/me", "Guardar preferencias"),
    ("GET", "/api/auth/usuarios/", "Listar usuarios (admin)"),
    ("POST", "/api/auth/usuarios/", "Crear usuario (admin)"),
    ("PUT", "/api/auth/usuarios/:id", "Actualizar usuario (admin)"),
    ("DELETE", "/api/auth/usuarios/:id", "Desactivar usuario (admin)"),
]

table_data = [["Método", "Ruta", "Descripción"]]
for method, route, desc in auth_endpoints:
    table_data.append([method, route, desc])

table = Table(table_data, colWidths=[1*inch, 2*inch, 2.5*inch])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
]))
content.append(table)
content.append(Spacer(1, 0.2*inch))

content.append(Paragraph("<b>Libros Fiscales (Books):</b>", heading2_style))

books_endpoints = [
    ("GET", "/api/libros", "Listar libros del usuario"),
    ("POST", "/api/libros", "Crear libro fiscal"),
    ("GET", "/api/libros/:id", "Obtener detalles"),
    ("DELETE", "/api/libros/:id", "Eliminar libro (cascada)"),
]

table_data2 = [["Método", "Ruta", "Descripción"]]
for method, route, desc in books_endpoints:
    table_data2.append([method, route, desc])

table2 = Table(table_data2, colWidths=[1*inch, 2*inch, 2.5*inch])
table2.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
]))
content.append(table2)
content.append(PageBreak())

# Sección 4
content.append(Paragraph("4. FLUJOS PRINCIPALES DE NEGOCIO", heading1_style))

content.append(Paragraph("4.1 Registro e Inicio de Sesión", heading2_style))
content.append(Paragraph(
    "<b>Registro:</b> El usuario proporciona nombre, email y contraseña. El sistema genera "
    "un código OTP de 6 dígitos y lo envía por email. El usuario ingresa el código de verificación "
    "y la cuenta se crea tras validación correcta.",
    body_style
))
content.append(Paragraph(
    "<b>Login:</b> El usuario proporciona email y contraseña. El sistema valida credenciales "
    "y retorna un token de sesión (httponly cookie).",
    body_style
))

content.append(Spacer(1, 0.1*inch))
content.append(Paragraph("4.2 Gestión de Libros Fiscales", heading2_style))
content.append(Paragraph(
    "Cada usuario puede crear múltiples libros fiscales. Cada libro está asociado a un año fiscal específico. "
    "Los libros contienen movimientos (ingresos/egresos). La eliminación en cascada: borrar libro elimina todos sus movimientos.",
    body_style
))

content.append(Spacer(1, 0.1*inch))
content.append(Paragraph("4.3 Movimientos y Cálculo de Saldos", heading2_style))
content.append(Paragraph(
    "<b>Operaciones:</b> Ingreso (suma al saldo), Egreso (resta del saldo), Ajuste (modifica arbitrariamente).<br/>"
    "<b>Saldo Acumulado:</b> Se recalcula en orden: fecha → ID. Garantiza determinismo independientemente "
    "del orden de entrada.",
    body_style
))

content.append(Spacer(1, 0.1*inch))
content.append(Paragraph("4.4 Auditoría", heading2_style))
content.append(Paragraph(
    "Todos los cambios (creación, actualización, eliminación) se registran. Admin puede consultar "
    "el log completo. Proporciona trazabilidad total de operaciones financieras.",
    body_style
))
content.append(PageBreak())

# Sección 5
content.append(Paragraph("5. AUTENTICACIÓN Y AUTORIZACIÓN", heading1_style))
content.append(Paragraph(
    "<b>Mecanismo:</b> Token de sesión (cookie httponly)<br/>"
    "<b>Niveles de Acceso:</b><br/>"
    "• <b>Usuarios:</b> Acceso a sus propios libros, movimientos, preferencias<br/>"
    "• <b>Admin:</b> Acceso total a todos los usuarios y datos",
    body_style
))

content.append(Spacer(1, 0.1*inch))
content.append(Paragraph("<b>Variables de Entorno Críticas:</b>", heading2_style))
env_vars = [
    "SECRET_KEY — Clave secreta (cambiar en producción)",
    "EMAIL_HOST_USER — Email para envío de OTP",
    "EMAIL_HOST_PASSWORD — Contraseña email",
    "DATABASE_URL — Conexión a PostgreSQL"
]
for var in env_vars:
    content.append(Paragraph("• " + var, body_style))
content.append(PageBreak())

# Sección 6
content.append(Paragraph("6. VERIFICACIÓN DE EMAIL Y OTP", heading1_style))
content.append(Paragraph(
    "<b>Sistema OTP:</b> Código de 6 dígitos enviado al email<br/>"
    "<b>Provider:</b> Brevo (SMTP relay)<br/>"
    "<b>Configuración requerida en producción:</b>",
    body_style
))

content.append(Spacer(1, 0.1*inch))
config_text = """<font face="Courier" size="9">
EMAIL_HOST = smtp-relay.brevo.com<br/>
EMAIL_PORT = 587<br/>
EMAIL_HOST_USER = [tu_usuario_brevo]<br/>
EMAIL_HOST_PASSWORD = [tu_contraseña_brevo]<br/>
DEFAULT_FROM_EMAIL = [tu_email_brevo]<br/>
BREVO_SENDER_EMAIL = [tu_email_brevo]<br/>
</font>"""
content.append(Paragraph(config_text, code_style))
content.append(PageBreak())

# Sección 7
content.append(Paragraph("7. PERSISTENCIA Y BASE DE DATOS", heading1_style))
content.append(Paragraph(
    "<b>Base de Datos:</b> PostgreSQL<br/>"
    "<b>ORM:</b> Django ORM<br/>"
    "<b>Migraciones:</b> Django migrations (automáticas)",
    body_style
))

content.append(Spacer(1, 0.1*inch))
content.append(Paragraph("<b>Modelos Principales:</b>", heading2_style))
models = [
    "Usuario — Cuenta con campos de preferencias (moneda, zona horaria)",
    "Libro — Libro fiscal del año",
    "Movimiento — Entrada individual de ingreso/egreso",
    "Auditoria — Log de todos los cambios",
    "Producto — Para inventario (si está activado)"
]
for model in models:
    content.append(Paragraph("• " + model, body_style))

content.append(Spacer(1, 0.1*inch))
content.append(Paragraph(
    "<b>Importante:</b> Todos los modelos tienen propietario (FK a Usuario). "
    "Aislamiento de datos por usuario es obligatorio. Los datos persisten entre sesiones si la base de datos está disponible.",
    body_style
))
content.append(PageBreak())

# Sección 8
content.append(Paragraph("8. INICIO RÁPIDO (DESARROLLO LOCAL)", heading1_style))
content.append(Paragraph("<b>Backend:</b>", heading2_style))

backend_setup = """<font face="Courier" size="9">
cd backend<br/>
python -m venv venv<br/>
venv\\Scripts\\activate          # Windows<br/>
pip install -r requirements.txt<br/>
python manage.py migrate<br/>
python manage.py createsuperuser<br/>
python manage.py runserver 8000<br/>
</font>"""
content.append(Paragraph(backend_setup, code_style))

content.append(Spacer(1, 0.15*inch))
content.append(Paragraph("<b>Frontend:</b>", heading2_style))

frontend_setup = """<font face="Courier" size="9">
cd frontend<br/>
npm install<br/>
npm run dev<br/>
</font>"""
content.append(Paragraph(frontend_setup, code_style))

content.append(Spacer(1, 0.1*inch))
content.append(Paragraph(
    "<b>URLs:</b><br/>"
    "• Backend: http://localhost:8000<br/>"
    "• Frontend: http://localhost:3000<br/>"
    "• Admin: http://localhost:8000/admin",
    body_style
))
content.append(PageBreak())

# Sección 9
content.append(Paragraph("9. DESPLIEGUE EN PRODUCCIÓN", heading1_style))
content.append(Paragraph("<b>Render (Recomendado):</b>", heading2_style))
content.append(Paragraph(
    "1. Conectar repositorio a Render<br/>"
    "2. Usar render.yaml para crear servicios automáticamente<br/>"
    "3. Configurar variables de entorno (DATABASE_URL, EMAIL credenciales, SECRET_KEY)<br/>"
    "4. Render ejecutará automáticamente migraciones y servirá la app",
    body_style
))

content.append(Spacer(1, 0.1*inch))
content.append(Paragraph("<b>Railway:</b>", heading2_style))
content.append(Paragraph("Similar a Render, usar DEPLOY_RAILWAY.md", body_style))

content.append(Spacer(1, 0.1*inch))
content.append(Paragraph("<b>Docker:</b>", heading2_style))

docker_text = """<font face="Courier" size="9">
docker build -t libro-fiscal .<br/>
docker run -p 8000:8000 -e DATABASE_URL=... libro-fiscal<br/>
</font>"""
content.append(Paragraph(docker_text, code_style))
content.append(PageBreak())

# Sección 10
content.append(Paragraph("10. PRUEBAS", heading1_style))
content.append(Paragraph("<b>Suite de Pruebas Implementada:</b>", body_style))
content.append(Paragraph(
    "• Pruebas de Caja Negra: Validan comportamiento externo (API responses)<br/>"
    "• Pruebas de Caja Blanca: Validan lógica interna (filtros, cálculos)",
    body_style
))

content.append(Spacer(1, 0.1*inch))
content.append(Paragraph("<b>Módulos Testeados:</b>", heading2_style))
content.append(Paragraph(
    "• apps/movimientos/tests.py (13 pruebas)<br/>"
    "• apps/inventario/tests.py (13 pruebas)<br/>"
    "• Estado final: OK",
    body_style
))

content.append(Spacer(1, 0.1*inch))
content.append(Paragraph("<b>Ejecución:</b>", heading2_style))

test_text = """<font face="Courier" size="9">
python manage.py test apps.movimientos apps.inventario<br/>
</font>"""
content.append(Paragraph(test_text, code_style))
content.append(PageBreak())

# Sección 11
content.append(Paragraph("11. CHECKLIST DE CONFIGURACIÓN EN PRODUCCIÓN", heading1_style))
checklist = [
    "☐ Variables de entorno configuradas (EMAIL, DATABASE_URL, SECRET_KEY)",
    "☐ Base de datos PostgreSQL creada y disponible",
    "☐ Migraciones ejecutadas (python manage.py migrate)",
    "☐ DEBUG = false en settings.py",
    "☐ ALLOWED_HOSTS actualizado",
    "☐ SESSION_COOKIE_SECURE = True (ya configurado)",
    "☐ Sistema de email funcionando (verificación OTP)",
    "☐ Logs monitoreados"
]
for item in checklist:
    content.append(Paragraph(item, body_style))
content.append(PageBreak())

# Sección 12
content.append(Paragraph("12. TROUBLESHOOTING COMÚN", heading1_style))

issues = [
    ("No llegan emails de OTP", 
     "Verificar EMAIL_HOST_USER/PASSWORD en env vars; Verificar que Brevo está activo y tiene créditos"),
    ("No veo mis libros después de recargar",
     "Ejecutar python manage.py migrate; Verificar DATABASE_URL; Comprobar sesión con authMe()"),
    ("La sesión se pierde",
     "Verificar que cookies están habilitadas; SESSION_COOKIE_SECURE = True en producción"),
    ("Error 403 en endpoints",
     "Verificar autenticación; Usar /api/auth/me para validar sesión"),
    ("Saldos incorrectos",
     "Ejecutar servicio de recálculo: recompute_saldos()")
]

for problem, solution in issues:
    content.append(Paragraph(f"<b>{problem}:</b>", heading2_style))
    content.append(Paragraph(solution, body_style))
    content.append(Spacer(1, 0.08*inch))
content.append(PageBreak())

# Sección 13
content.append(Paragraph("13. ARCHIVOS CLAVE A CONSULTAR", heading1_style))
files = [
    "backend/config/settings.py — Configuración Django (email líneas 220-235)",
    "backend/apps/usuarios/otp_service.py — Sistema de envío OTP",
    "frontend/src/pages/auth/LoginPage.jsx — Flujo de registro y verificación",
    "frontend/src/pages/perfil/ProfilePage.jsx — Gestión de preferencias",
    "frontend/src/pages/libros/LibrosPage.jsx — CRUD de libros fiscales"
]
for file in files:
    content.append(Paragraph("• " + file, body_style))

content.append(Spacer(1, 0.3*inch))
content.append(Paragraph(
    "---<br/><br/>"
    "Este es el manual técnico completo del Libro Fiscal v2.<br/>"
    f"Generado: {datetime.now().strftime('%d de %B de %Y a las %H:%M:%S')}<br/><br/>"
    "Para más información, consulta los archivos README.md y documentación en el repositorio.",
    styles['Normal']
))

# Construir el PDF
doc.build(content)
print(f"✅ PDF generado exitosamente: {output_file}")
print(f"📄 Archivo guardado en: {output_file}")

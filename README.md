# Libro Fiscal v2 — Django + React

Proyecto de gestión fiscal reestructurado con backend y frontend completamente separados.

## Estructura del Proyecto

```
libro_fiscal_v2/
├── backend/                    # Django + DRF (API REST)
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/                 # Configuración Django
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── exceptions.py
│   ├── apps/                   # Aplicaciones Django
│   │   ├── usuarios/           # Auth + gestión de usuarios
│   │   ├── libros/             # Libros fiscales
│   │   ├── movimientos/        # Operaciones diarias
│   │   ├── auditoria/          # Registro de auditoría
│   │   ├── dashboard/          # Estadísticas + resumen anual
│   │   └── exportacion/        # Exportación Excel
│   └── services/               # Lógica de negocio compartida
│       ├── saldo.py            # Recálculo de saldos
│       └── excel.py            # Generación de Excel
│
├── frontend/                   # React + Vite
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── styles.css
│       ├── context/
│       │   └── AuthContext.jsx  # Autenticación global
│       ├── services/
│       │   └── api.js           # Capa HTTP (axios)
│       ├── components/
│       │   └── Layout.jsx       # Sidebar + routing
│       └── pages/
│           ├── LoginPage.jsx
│           ├── DashboardPage.jsx
│           ├── LibrosPage.jsx
│           ├── MovimientosPage.jsx
│           ├── UsuariosPage.jsx
│           └── AuditoriaPage.jsx
│
└── README.md
```

## Inicio Rápido

### Backend (Django)

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

El frontend se sirve en `http://localhost:3000` y hace proxy de `/api/*` al backend en `http://localhost:8000`.

### Despliegue en Render

Render puede desplegar este proyecto usando el `Dockerfile` raíz y un servicio PostgreSQL.

1. Conecta el repositorio a Render.
2. Usa el archivo `render.yaml` en la raíz para crear los servicios.
3. Render construirá la imagen Docker, ejecutará las migraciones y servirá la app en el puerto que provee la plataforma.

> Asegúrate de cambiar `SECRET_KEY` en las variables de entorno de Render por una clave segura.

## API Endpoints

| Método | Ruta                    | Descripción                |
|--------|-------------------------|----------------------------|
| POST   | /api/auth/register      | Registro de usuario        |
| POST   | /api/auth/login         | Inicio de sesión           |
| POST   | /api/auth/logout        | Cerrar sesión              |
| GET    | /api/auth/me            | Usuario actual             |
| GET    | /api/auth/usuarios/     | Listar usuarios (admin)    |
| POST   | /api/auth/usuarios/     | Crear usuario (admin)      |
| PUT    | /api/auth/usuarios/:id  | Actualizar usuario (admin) |
| DELETE | /api/auth/usuarios/:id  | Desactivar usuario (admin) |
| GET    | /api/libros             | Listar libros              |
| POST   | /api/libros             | Crear libro                |
| GET    | /api/libros/:id         | Obtener libro              |
| DELETE | /api/libros/:id         | Eliminar libro (+cascada)  |
| GET    | /api/entries            | Listar movimientos         |
| POST   | /api/entries            | Crear movimiento           |
| PUT    | /api/entries/:id        | Editar movimiento          |
| DELETE | /api/entries/:id        | Eliminar movimiento        |
| GET    | /api/resumen-anual      | Resumen 12 meses           |
| GET    | /api/export             | Exportar Excel             |
| GET    | /api/dashboard          | Estadísticas dashboard     |
| GET    | /api/auditoria          | Log de auditoría (admin)   |

## Tecnologías

- **Backend:** Django 4.2, Django REST Framework, PostgreSQL
- **Frontend:** React 18, Vite, React Router, Axios, Chart.js, Bootstrap 5
- **Autenticación:** Token de sesión (cookie httponly)

#!/usr/bin/env python
"""Wrapper para ejecutar Django desde la raiz del repositorio."""
import os
import sys
from pathlib import Path


def main():
    repo_root = Path(__file__).resolve().parent
    backend_dir = repo_root / "backend"

    if not backend_dir.exists():
        raise SystemExit("No se encontro la carpeta backend junto a este archivo.")

    sys.path.insert(0, str(backend_dir))
    os.chdir(backend_dir)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Activa tu entorno virtual e instala dependencias."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

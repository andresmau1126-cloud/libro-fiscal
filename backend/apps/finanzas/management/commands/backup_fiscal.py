import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib import error, request

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Exporta la base de datos a /backups, conserva siete días y opcionalmente publica en GitHub."

    def handle(self, *args, **options):
        backup_dir = Path(os.getenv("BACKUP_DIR", "/backups"))
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output = backup_dir / f"libro_fiscal_{timestamp}.dump"
        database_url = os.getenv("DATABASE_URL") or os.getenv("RENDER_DATABASE_URL")
        if database_url and shutil.which("pg_dump"):
            subprocess.run(["pg_dump", "--dbname", database_url, "--format=custom", "--no-owner", "--no-acl", "--file", str(output)], check=True)
        else:
            from django.core.management import call_command
            output = backup_dir / f"libro_fiscal_{timestamp}.json"
            with output.open("w", encoding="utf-8") as handle:
                call_command("dumpdata", exclude=["contenttypes"], stdout=handle, indent=2)

        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        for old_file in backup_dir.glob("libro_fiscal_*"):
            if datetime.fromtimestamp(old_file.stat().st_mtime, timezone.utc) < cutoff:
                old_file.unlink()
        self._upload_github(output)
        self.stdout.write(self.style.SUCCESS(f"Backup fiscal completado: {output}"))

    def _upload_github(self, file_path):
        token = os.getenv("GITHUB_BACKUP_TOKEN")
        repository = os.getenv("GITHUB_BACKUP_REPOSITORY")
        if not token or not repository:
            return
        import base64
        content = base64.b64encode(file_path.read_bytes()).decode("ascii")
        api_url = f"https://api.github.com/repos/{repository}/contents/backups/{file_path.name}"
        payload = (f'{{"message":"backup fiscal {file_path.stem}","content":"{content}"}}').encode("utf-8")
        req = request.Request(api_url, data=payload, method="PUT", headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "Content-Type": "application/json"})
        try:
            with request.urlopen(req, timeout=30):
                pass
        except error.HTTPError as exc:
            raise CommandError(f"No se pudo subir el backup a GitHub: HTTP {exc.code}") from exc

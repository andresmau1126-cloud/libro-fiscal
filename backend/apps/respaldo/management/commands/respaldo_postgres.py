import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Genera un respaldo PostgreSQL y lo sube a almacenamiento S3 compatible."

    def add_arguments(self, parser):
        parser.add_argument(
            "--retention-days",
            type=int,
            default=30,
            help="Elimina respaldos S3 anteriores a esta cantidad de días.",
        )

    def handle(self, *args, **options):
        database_url = os.getenv("DATABASE_URL") or os.getenv("RENDER_DATABASE_URL")
        bucket = os.getenv("BACKUP_S3_BUCKET")
        access_key = os.getenv("BACKUP_S3_ACCESS_KEY_ID")
        secret_key = os.getenv("BACKUP_S3_SECRET_ACCESS_KEY")
        retention_days = options["retention_days"]

        if not database_url:
            raise CommandError("Falta DATABASE_URL o RENDER_DATABASE_URL.")
        if not all((bucket, access_key, secret_key)):
            raise CommandError(
                "Faltan BACKUP_S3_BUCKET, BACKUP_S3_ACCESS_KEY_ID o "
                "BACKUP_S3_SECRET_ACCESS_KEY."
            )
        if retention_days < 1:
            raise CommandError("--retention-days debe ser mayor que cero.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        prefix = os.getenv("BACKUP_S3_PREFIX", "libro-fiscal").strip("/")
        object_key = f"{prefix}/postgres_{timestamp}.dump"
        region = os.getenv("BACKUP_S3_REGION", "us-east-1")
        endpoint_url = os.getenv("BACKUP_S3_ENDPOINT_URL") or None

        with tempfile.TemporaryDirectory(prefix="libro-fiscal-backup-") as temp_dir:
            dump_path = Path(temp_dir) / f"postgres_{timestamp}.dump"
            self.stdout.write("Generando respaldo PostgreSQL...")
            try:
                subprocess.run(
                    [
                        "pg_dump",
                        "--dbname",
                        database_url,
                        "--format=custom",
                        "--no-owner",
                        "--no-acl",
                        "--file",
                        str(dump_path),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except FileNotFoundError as error:
                raise CommandError("pg_dump no está instalado en el contenedor.") from error
            except subprocess.CalledProcessError as error:
                detail = (error.stderr or "").strip()
                raise CommandError(f"pg_dump falló: {detail}") from error

            client = boto3.client(
                "s3",
                region_name=region,
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
            )
            try:
                client.upload_file(str(dump_path), bucket, object_key)
                self._delete_old_backups(client, bucket, prefix, retention_days)
            except (BotoCoreError, ClientError) as error:
                raise CommandError(f"No se pudo subir el respaldo a S3: {error}") from error

        self.stdout.write(self.style.SUCCESS(f"Respaldo guardado en s3://{bucket}/{object_key}"))

    def _delete_old_backups(self, client, bucket, prefix, retention_days):
        cutoff = datetime.now(timezone.utc).timestamp() - retention_days * 86400
        paginator = client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=f"{prefix}/"):
            for item in page.get("Contents", []):
                modified = item["LastModified"].timestamp()
                if modified < cutoff:
                    client.delete_object(Bucket=bucket, Key=item["Key"])

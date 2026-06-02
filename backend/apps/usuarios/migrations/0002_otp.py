# Generated migration for OTP model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_usuario_preferences'),
    ]

    operations = [
        migrations.CreateModel(
            name='OTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=6)),
                ('tipo', models.CharField(choices=[('login', 'Login'), ('reset_password', 'Resetear Contraseña')], default='login', max_length=20)),
                ('usado', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='otps', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'OTP',
                'verbose_name_plural': 'OTPs',
                'db_table': 'otps',
            },
        ),
        migrations.AddIndex(
            model_name='otp',
            index=models.Index(fields=['usuario', 'codigo', 'tipo'], name='otps_usuario_codigo_tipo_idx'),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="pref_currency",
            field=models.CharField(default="GTQ", max_length=3),
        ),
        migrations.AddField(
            model_name="usuario",
            name="pref_email_notifications",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="usuario",
            name="pref_timezone",
            field=models.CharField(default="GMT-6", max_length=10),
        ),
    ]

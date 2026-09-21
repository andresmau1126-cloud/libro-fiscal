from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0009_sellerschedule"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DELETE FROM seller_schedules;
                INSERT INTO seller_schedules (usuario_id, name, start_time, end_time, is_active, nit)
                SELECT id, 'Mauricio', '08:00', '12:00', TRUE, '1020085627-1'
                FROM usuarios
                WHERE email = 'andresmau.colamericano7b@gmail.com';
                INSERT INTO seller_schedules (usuario_id, name, start_time, end_time, is_active, nit)
                SELECT id, 'José', '12:00', '19:00', TRUE, '1020085627-1'
                FROM usuarios
                WHERE email = 'yo1126top76f@gmail.com';
            """,
            reverse_sql="DELETE FROM seller_schedules;",
        ),
    ]

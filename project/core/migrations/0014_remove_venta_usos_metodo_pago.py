# Generated by Django 5.1 on 2024-08-19 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_venta_usos_metodo_pago'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='venta',
            name='usos_metodo_pago',
        ),
    ]

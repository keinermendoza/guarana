# Generated by Django 5.1 on 2024-08-19 16:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_remove_venta_usos_metodo_pago'),
    ]

    operations = [
        migrations.AddField(
            model_name='usometodopago',
            name='venta',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='usos_metodo_pago', to='core.venta'),
            preserve_default=False,
        ),
    ]

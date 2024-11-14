# Generated by Django 5.1 on 2024-08-19 16:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_remove_usometodopago_venta'),
    ]

    operations = [
        migrations.AddField(
            model_name='venta',
            name='usos_metodo_pago',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='venta', to='core.usometodopago'),
            preserve_default=False,
        ),
    ]

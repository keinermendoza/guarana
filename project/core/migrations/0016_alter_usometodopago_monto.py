# Generated by Django 5.1 on 2024-08-19 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_usometodopago_venta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usometodopago',
            name='monto',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]

# Generated by Django 5.1 on 2024-08-17 13:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_producciondetalle_peso_producido_alter_producto_peso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ralada',
            name='saco',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='ralada', to='core.saco'),
            preserve_default=False,
        ),
    ]

# Generated by Django 5.1 on 2024-08-22 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_remove_venta_compra_vidros_compravidros_venta'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='producto',
            options={'ordering': ['tipo_guarana', '-peso'], 'verbose_name': 'ModelName', 'verbose_name_plural': 'ModelNames'},
        ),
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['tipo_guarana', '-peso'], name='core_produc_tipo_gu_2c3482_idx'),
        ),
    ]

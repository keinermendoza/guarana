# Generated by Django 5.1 on 2024-08-18 00:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_ralada_saco'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='tipo_guarana',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='productos', to='core.tipoguarana'),
        ),
    ]
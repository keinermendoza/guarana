# Generated by Django 5.1 on 2024-08-30 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_periodo'),
    ]

    operations = [
        migrations.AddField(
            model_name='periodo',
            name='final',
            field=models.DateField(blank=True, null=True),
        ),
    ]
# Generated by Django 5.0.6 on 2024-06-28 10:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0012_remove_hospital_wards_ward_hospital'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ward',
            name='hospital',
            field=models.ForeignKey(blank=True, default=0, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='wards', to='hospital.hospital'),
        ),
    ]

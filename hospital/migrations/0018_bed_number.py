# Generated by Django 5.0.6 on 2024-07-02 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0017_alter_bed_bed_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='bed',
            name='number',
            field=models.CharField(default=0, max_length=10),
            preserve_default=False,
        ),
    ]

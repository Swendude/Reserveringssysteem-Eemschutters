# Generated by Django 3.0.6 on 2020-05-16 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reserveringen', '0009_schietdag_extra_tijd_eind'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservering',
            name='bonus',
            field=models.BooleanField(default=False),
        ),
    ]

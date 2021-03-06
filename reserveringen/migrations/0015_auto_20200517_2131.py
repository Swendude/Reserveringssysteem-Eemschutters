# Generated by Django 3.0.6 on 2020-05-17 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reserveringen', '0014_auto_20200517_2122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteconfiguration',
            name='reserveringen_per_week',
            field=models.IntegerField(default=2, help_text='Hoeveel reserveringen per week mogen leden maken?'),
        ),
        migrations.AlterField(
            model_name='siteconfiguration',
            name='sleutelhouder_slot',
            field=models.IntegerField(default=2, help_text='Op welk slot moeten een sleutehouders slot standaard gereserveerd worden? (eerste slot = 0)'),
        ),
    ]

# Generated by Django 3.0.6 on 2020-05-07 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reserveringen', '0005_auto_20200507_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schietdag',
            name='afbouw_duur',
            field=models.DurationField(help_text='[HH:MM:SS]'),
        ),
        migrations.AlterField(
            model_name='schietdag',
            name='open',
            field=models.TimeField(help_text='[HH:MM:SS]'),
        ),
        migrations.AlterField(
            model_name='schietdag',
            name='opstart_duur',
            field=models.DurationField(help_text='[HH:MM:SS]'),
        ),
        migrations.AlterField(
            model_name='schietdag',
            name='slot_duur',
            field=models.DurationField(help_text='[HH:MM:SS]'),
        ),
        migrations.AlterField(
            model_name='schietdag',
            name='sluit',
            field=models.TimeField(help_text='[HH:MM:SS]'),
        ),
    ]

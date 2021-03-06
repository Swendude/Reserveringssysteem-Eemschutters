# Generated by Django 3.0.6 on 2020-05-07 17:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reserveringen', '0004_protocol_geldig_op'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schietdag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dag', models.IntegerField(choices=[(0, 'Maandag'), (1, 'Dinsdag'), (2, 'Woensdag'), (3, 'Donderdag'), (4, 'Vrijdag'), (5, 'Zaterdag'), (6, 'Zondag')], unique=True)),
                ('slot_duur', models.DurationField()),
                ('opstart_duur', models.DurationField()),
                ('afbouw_duur', models.DurationField()),
                ('open', models.TimeField()),
                ('sluit', models.TimeField()),
            ],
            options={
                'verbose_name_plural': 'Schietdagen',
            },
        ),
        migrations.RemoveField(
            model_name='reservering',
            name='protocol',
        ),
        migrations.DeleteModel(
            name='Protocol',
        ),
        migrations.AddField(
            model_name='reservering',
            name='schietdag',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='reserveringen.Schietdag'),
            preserve_default=False,
        ),
    ]

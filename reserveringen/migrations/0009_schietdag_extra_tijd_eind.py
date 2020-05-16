# Generated by Django 3.0.6 on 2020-05-15 20:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reserveringen', '0008_auto_20200515_2247'),
    ]

    operations = [
        migrations.AddField(
            model_name='schietdag',
            name='extra_tijd_eind',
            field=models.DurationField(default=datetime.timedelta(seconds=60), help_text='[HH:MM:SS] Als er tijd onverdeeld blijft door je slotkeuze, verdeel deze als extra aan het begin en eind'),
            preserve_default=False,
        ),
    ]
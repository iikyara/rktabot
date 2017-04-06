# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_auto_20170222_0146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='endtime',
            field=models.TimeField(default='00:55:00'),
        ),
        migrations.AlterField(
            model_name='post',
            name='starttime',
            field=models.TimeField(default='00:55:00'),
        ),
    ]

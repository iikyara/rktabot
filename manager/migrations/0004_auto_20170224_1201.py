# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0003_auto_20170224_0704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='endtime',
            field=models.TimeField(default='12:01'),
        ),
        migrations.AlterField(
            model_name='post',
            name='sdate',
            field=models.DateField(default='2017-02-24'),
        ),
        migrations.AlterField(
            model_name='post',
            name='starttime',
            field=models.TimeField(default='12:01'),
        ),
    ]

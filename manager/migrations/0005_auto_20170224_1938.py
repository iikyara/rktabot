# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0004_auto_20170224_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.CharField(max_length=60, default=''),
        ),
        migrations.AlterField(
            model_name='post',
            name='endtime',
            field=models.TimeField(default='19:38'),
        ),
        migrations.AlterField(
            model_name='post',
            name='starttime',
            field=models.TimeField(default='19:38'),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=40, default=''),
        ),
    ]

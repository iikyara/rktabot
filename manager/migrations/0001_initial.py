# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(default='Default Title', max_length=30)),
                ('sdate', models.DateField(default='2017-02-22')),
                ('starttime', models.DateTimeField(default='2000-1-1 00:55:00')),
                ('endtime', models.DateTimeField(default='2000-1-1 00:55:00')),
                ('content', models.CharField(default='Default Content', max_length=10)),
                ('available', models.BooleanField(default='True')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('published_date', models.DateTimeField(null=True, blank=True)),
            ],
        ),
    ]

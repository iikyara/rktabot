# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
import datetime

class Post(models.Model):
    title = models.CharField(max_length=40, default='')
    sdate = models.DateField(default=datetime.date.today().strftime("%Y-%m-%d"))
    starttime = models.TimeField(default=datetime.datetime.now().strftime("%H:%M"))
    endtime = models.TimeField(default=datetime.datetime.now().strftime("%H:%M"))
    content = models.CharField(max_length=60, default='')
    available = models.BooleanField(default='True')
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

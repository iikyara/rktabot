# -*- coding: utf-8 -*-
from django import forms
from django.forms import formsets
from django.forms import models
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.admin.widgets import AdminTimeWidget

from .models import Post

year = []
for i in range(2000,2100):
    year.append(str(i))
YEAR_CHOICES = tuple(year)
MONTH_CHOICES = {
    1: ('1'), 2: ('2'), 3: ('3'), 4: ('4'),
    5: ('5'), 6: ('6'), 7: ('7'), 8: ('8'),
    9: ('9'), 10: ('10'), 11: ('11'), 12: ('12'), 
}

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'sdate', 'starttime', 'endtime', 'content', 'available',)
        widgets = {
            'sdate': SelectDateWidget(years=YEAR_CHOICES, months=MONTH_CHOICES),
            'starttime': AdminTimeWidget(format='%H:%M'),
            'endtime': AdminTimeWidget(format='%H:%M'),
        }

PostFormSet = formsets.formset_factory(PostForm, extra=0, formset=models.BaseModelFormSet, can_order=True)
PostFormSet.model = Post

class DetailForm(forms.Form):
    content = forms.CharField(
        max_length=3000,
        widget=forms.Textarea(attrs={'cols': 100, 'rows': 50}),
        error_messages={
        'required': '1文字以上入力して下さい．',
        })

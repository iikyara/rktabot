# -*- coding: utf-8 -*-
import dj_database_url
import psycopg2
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.forms import formsets
from django.forms import models
from django.contrib.auth.decorators import login_required

from . import forms
from .models import Post
from bot.views import connect, sqlExe

def post_list(request):
    return render(request, 'manager/post_list.html', {})

def post_new(request):
    PostFormSet = forms.PostFormSet
    message = ''
    if request.method == 'POST':
        formset = PostFormSet(request.POST, request.FILES)
        management = formset.management_form
        btn_name = request.POST['btn_name']
        if 'btn_delete' == btn_name:
            if request.POST['delete_id'] != 'None' and request.POST['delete_id'] != '':
                sqlExe("DELETE FROM manager_post WHERE id = %s;", [request.POST['delete_id']], False)
                sqlExe("DELETE FROM settingdetail WHERE id = %s;", [request.POST['delete_id']], False)
                ordered_formset = forms.PostFormSet()
                management = ordered_formset.management_form
            else:
                ext = formset.total_form_count() - formset.initial_form_count() - 1
                if ext < 0:
                    ext = 0
                PostFormSet = formsets.formset_factory(forms.PostForm, extra=ext, formset=models.BaseModelFormSet, can_order=True)
                PostFormSet.model = Post
                ordered_formset = PostFormSet()
                management = ordered_formset.management_form
        elif 'btn_add' == btn_name:
            ext = formset.total_form_count() - formset.initial_form_count() + 1
            PostFormSet = formsets.formset_factory(forms.PostForm, extra=ext, formset=models.BaseModelFormSet, can_order=True)
            PostFormSet.model = Post
            ordered_formset = PostFormSet()
            management = ordered_formset.management_form
        elif 'btn_remove' == btn_name:
            ext = formset.total_form_count() - formset.initial_form_count() - 1
            if ext < 0:
                ext = 0
            PostFormSet = formsets.formset_factory(forms.PostForm, extra=ext, formset=models.BaseModelFormSet, can_order=True)
            PostFormSet.model = Post
            ordered_formset = PostFormSet()
            management = ordered_formset.management_form
        elif 'btn_order' == btn_name and formset.is_valid():
            ordered_formset = formset.ordered_forms
        elif 'btn_save' in request.POST:
            if formset.is_valid():
                formset.save()
                ordered_formset = forms.PostFormSet()
                message = "保存しました．"
                management = ordered_formset.management_form
            else:
                message = "保存できませんでした．"
                ordered_formset = formset
                management = ordered_formset.management_form
        elif 'btn_cancel' in request.POST:
            ordered_formset = forms.PostFormSet()
            management = ordered_formset.management_form
        else:
            ordered_formset = formset
    else:
        formset = PostFormSet()
        ordered_formset = formset
        management = ordered_formset.management_form
    new_text = Post.objects.all().order_by('sdate','starttime')
    contents = {
        'management': management,
        'formset': ordered_formset,
        'text': new_text,
        'text_num': len(new_text),
        'message': message,
    }
    return render(request, 'manager/post_edit.html', contents)

def post_stop(request):
    title = 'テストタイトル（詳細が正常に読み込めませんでした．）'
    content = 'テスト内容（詳細が正常に読み込めませんでした．）'
    time = 'テスト時間（詳細が正常に読み込めませんでした．）'
    detail = 'テスト詳細（詳細が正常に読み込めませんでした．）'
    if request.method == 'GET':
        if 'id' in request.GET:
            tempid = request.GET['id']
            if tempid.isdigit():
                formid = int(tempid)
            else:
                return render(request, 'manager/post_list.html', {})
        else:
            return render(request, 'manager/post_list.html', {})
        mp_title = sqlExe("SELECT title,sdate,starttime,endtime,content FROM manager_post WHERE id=%s;", [formid])
        if len(mp_title) == 1:
            title = mp_title[0][1].strftime('%Y{0}%m{1}%d{2}').format('年','月','日') + '　' + mp_title[0][0]
            time = mp_title[0][2].strftime('%H{0}%M{1}').format('時','分')+'～'+\
                   mp_title[0][3].strftime('%H{0}%M{1}').format('時','分')
            content = mp_title[0][4].strip()
        else:
            return render(request, 'manager/post_list.html', {})
        sd = sqlExe("SELECT detail FROM settingdetail WHERE id=%s;", [formid])
        if len(sd) >= 1:
            detail = sd[0][0].strip()
        else:
            detail = '詳細が設定されていません．'
    contents = {
        'title': title,
        'time': time,
        'content': content,
        'detail': detail,
    }
    return render(request, 'manager/post_stop.html', contents)

def post_edit_detail(request):
    title = 'テストタイトル（詳細が正常に読み込めませんでした．）'
    message = ''
    if request.method == 'GET':
        if 'id' in request.GET:
            tempid = request.GET['id']
            if tempid.isdigit():
                formid = int(tempid)
            else:
                return render(request, 'manager/post_list.html', {})
        else:
            return render(request, 'manager/post_list.html', {})
        mp_title = sqlExe("SELECT title,sdate FROM manager_post WHERE id=%s;", [formid])
        if len(mp_title) == 1:
            title = mp_title[0][1].strftime('%Y{0}%m{1}%d{2}').format('年','月','日') + '　' + mp_title[0][0]
        else:
            return render(request, 'manager/post_list.html', {})
        detail = sqlExe("SELECT detail FROM settingdetail WHERE id=%s;", [formid])
        if len(detail) >= 1:
            form = forms.DetailForm(initial = {'content': detail[0][0].strip()})
        else:
            form = forms.DetailForm()
    elif request.method == 'POST':
        title = request.POST['title']
        formid = request.POST['id']
        btn_name = request.POST['btn_name']
        if 'btn_save' == btn_name:
            form = forms.DetailForm(request.POST)
            if form.is_valid():
                pc = request.POST['content']
                sqlExe("INSERT INTO settingdetail VALUES (%s, %s) ON CONFLICT ON CONSTRAINT settingdetail_pkey DO UPDATE SET detail = %s;",[formid, pc, pc],False)
                message = '保存できました．'
            else:
                message = '保存できませんでした．'
        elif 'btn_cancel' == btn_name:
            detail = sqlExe("SELECT detail FROM settingdetail WHERE id=%s;", [formid])
            if len(detail) >= 1:
                form = forms.DetailForm(initial = {'content': detail[0][0].strip()})
            else:
                form = forms.DetailForm()
    contents = {
        'title': title,
        'form': form,
        'id': str(formid),
        'message': message,
    }
    return render(request, 'manager/post_edit_detail.html', contents)

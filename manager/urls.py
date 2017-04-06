from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.post_list),
    url(r'^post/new/$', views.post_new, name='post_new'),
    url(r'^stop', views.post_stop, name='stop'),
    url(r'^post/new/edit/$', views.post_edit_detail, name='edit_detail'),
]

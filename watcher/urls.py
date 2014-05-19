# -*- coding: utf-8 -*-

''' urls module '''

from django.conf.urls import patterns, url
from watcher import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^draft/(?P<draft_number>\d+-\d)/$', views.detail, name='detail'),
        url(r'^add_draft/$', views.add_draft, name='add_draft'),
        url(r'^update/$', views.update_drafts, name='update_drafts'),
        url(r'^register/$', views.register, name='register'),
        url(r'^logout/$', views.user_logout, name='user_logout'),
        url(r'^login/$', views.user_login, name='user_login'),
        )

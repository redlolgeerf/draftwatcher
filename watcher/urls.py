# -*- coding: utf-8 -*-

''' urls module '''

from django.conf.urls import patterns, url
from watcher import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^drafts/([\w-]+)/$', views.UserDraftsList.as_view() , name='user_drafts'),
        url(r'^all_drafts/$', views.AllDraftsList.as_view() , name='all_drafts'),
        #url(r'^draft/(?P<draft_number>\d+-\d)/$', views.detail, name='detail'),
        url(r'^draft/(?P<slug>\d+-\d)/$', views.DraftLawDetailView.as_view(), name='detail'),
        url(r'^add_draft/$', views.add_draft, name='add_draft'),
        url(r'^add_draft_to_user/(?P<draft_number>\d+-\d)/$',
            views.add_draft_to_user, name='add_draft_to_user'),
        url(r'^release_user_from_draft/(?P<draft_number>\d+-\d)/$',
            views.release_user_from_draft, name='release_user_from_draft'),
        url(r'^update/$', views.update_drafts, name='update_drafts'),
        url(r'^register/$', views.register, name='register'),
        url(r'^logout/$', views.user_logout, name='user_logout'),
        url(r'^login/$', views.user_login, name='user_login'),
        url(r'^profile/$', views.profile, name='profile'),
        url(r'^verify_email/(?P<inp>.+)/$', views.verify_email, name='verify_email'),
        url(r'^send_verification/$', views.send_verification, name='send_verification'),
        url(r'^send_restore_password/$', views.send_restore_password, name='send_restore_password'),
        url(r'^restore_password/(?P<inp>.*)$', views.restore_password, name='restore_password'),
        )

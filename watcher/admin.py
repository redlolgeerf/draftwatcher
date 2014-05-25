# -*- coding: utf-8 -*-

''' admin module '''

from django.contrib import admin
from watcher.models import DraftLaw, UserProfile, UserData

admin.site.register(DraftLaw)
admin.site.register(UserProfile)
admin.site.register(UserData)

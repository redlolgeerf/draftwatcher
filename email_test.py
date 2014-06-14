# -*- coding: utf-8 -*-
# !/usr/bin/env python3

import os

def go():
    tes = UserProfile.objects.get(pk=1)
    law = tes.draftlaw.get()
    law.notify_users()

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'draft_law_project.settings')
    from watcher.models import DraftLaw, UserProfile
    go()

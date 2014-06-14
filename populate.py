# -*- coding: utf-8 -*-
# !/usr/bin/env python3

import os
import sys

def populate():
    drafts = ['413886-6', '566528-5', '335492-6', '3303304-6', '613080-5',
    '383153-6', '513912-6', '268501-6', '51982-6', '508677-6', '181700-6',
    '395014-6', '485228-6', '468171-6', '320066-6', '415703-6', '466637-6']
    for draft in drafts:
        try:
            print('populating draft %s' % draft)
            x, created = DraftLaw.objects.get_or_create(number=draft)
            x.save()
        except:
            e = sys.exc_info()[0]
            print(draft)
            print(e)
    return

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'draft_law_project.settings')
    from watcher.models import DraftLaw
    populate()

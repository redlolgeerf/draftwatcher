# -*- coding: utf-8 -*-
# !/usr/bin/env python3

import os
import sys
import datetime

def now():
    return (datetime.datetime.now().strftime('%d.%m.%y %H:%M') + ' :')

def update_all():
    print("%s Starting update" % now())
    drafts_to_update = DraftLaw.objects.filter(archived=False)
    print("%s %d drafts to update" % (now(), len(drafts_to_update)))
    for draft in drafts_to_update:
        print("%s Updating draft %s" % (now(), draft.number))
        try:
            draft.update()
            draft.save()
            print("%s Success" % now())
        except KeyboardInterrupt:
            exit()
        except:
            e = sys.exc_info()[0]
            print("%s Failed to update %s due to %s" % (now(), draft.number, e))


if __name__ == '__main__':
    #activate_this = '/home/draftwatcher/.virtualenvs/draftwatcher/bin/activate_this.py'
    activate_this = '/home/eyeinthebrick/.virtualenvs/draft_law/bin/activate_this.py'
    with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

    # ADD PROJECT TO THE PYTHONPATH FOR THE PYTHON INSTANCE
    path = '/home/eyeinthebrick/Python/Django/draft_law_project'
    #$path = '/home/draftwatcher/draftwatcher'

    if path not in sys.path:
        sys.path.append(path)

    os.chdir(path)

    # TELL DJANGO WHERE YOUR SETTINGS MODULE IS LOCATED
    os.environ['DJANGO_SETTINGS_MODULE'] = 'draft_law_project.settings'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'draft_law_project.settings')
    from watcher.models import DraftLaw
    update_all()

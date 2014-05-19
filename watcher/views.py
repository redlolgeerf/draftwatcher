# -*- coding: utf-8 -*-

''' view module '''

from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from watcher.models import DraftLaw
from watcher.models import serialize_history, deserialize_history
from watcher.forms import AddDraftForm


def index(request):
    ''' index page
        shows a list of all drawft laws '''
    context = RequestContext(request)
    context_dict = {}

    drafts = DraftLaw.objects.order_by('-updated')
    context_dict['drafts'] = drafts

    return render_to_response('watcher/index.html',
                              context_dict, context)

def detail(request, draft_number):
    ''' detail viewl
        shows attributes of a particular drawft law '''
    context = RequestContext(request)
    context_dict = {}

    try:
        draft = DraftLaw.objects.get(number=draft_number)
        context_dict['draft'] = draft
        context_dict['history'] = deserialize_history(draft.history)

    except DraftLaw.DoesNotExsist:
        pass

    return render_to_response('watcher/detail.html',
                              context_dict, context)

def add_draft(request):
    context = RequestContext(request)
    context_dict = {}

    if request.method == 'POST':
        form = AddDraftForm(request.POST)
        context_dict['form'] = form

        if form.is_valid():
            draft = form.save(commit=False)
            draft.make_url()
            try:
                draft.populate()
                draft.save()
            except AttributeError:
                form._errors["number"] = form.error_class(
                        ['Законопроект не найден'])
                return render_to_response('watcher/add_draft.html',
                        context_dict, context)

            return index(request)
        else:
            return render_to_response('watcher/add_draft.html',
                    context_dict, context)
    else:
        context_dict['form'] = AddDraftForm()
        return render_to_response('watcher/add_draft.html',
                context_dict, context)

def update_drafts(request):
    context = RequestContext(request)
    context_dict = {}

    drafts = DraftLaw.objects.filter(archived=False)
    for draft in drafts:
        draft.update()
        draft.save()

    return index(request)

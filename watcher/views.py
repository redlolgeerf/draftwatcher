# -*- coding: utf-8 -*-

''' view module '''

from datetime import datetime
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from watcher.models import DraftLaw, UserProfile, UserData
from watcher.models import serialize_history, deserialize_history
from watcher.forms import AddDraftForm, UserForm


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
        data = form['number']

        try:
            draft = DraftLaw.objects.get(number=data)
            add_draft_to_user(request, draft)
            return index(request)

        except DraftLaw.DoesNotExist:
            pass

        if form.is_valid():
            draft = form.save(commit=False)

            draft.make_url()
            try:
                draft.populate()
                draft.save()
                add_draft_to_user(request, draft)
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

def register(request):
    context = RequestContext(request)
    context_dict = {}

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)

            user.save()

            profile = UserProfile()
            profile.user = user

            profile.save()
            registered = True

        else:
            print(user_form.errors)

    else:
        context_dict['user_form'] = UserForm()
        context_dict['registered'] = registered

    return render_to_response(
            'watcher/register.html',
            context_dict, context)

def user_login(request):
    context = RequestContext(request)
    context_dict = {}

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return index(request)
            else:
                return HttpResponse('Your Rango account is disabled')
        else:
            return HttpResponse("Invalid login details supplied.")

    else:
        return render_to_response('watcher/login.html', context_dict, context)

@login_required
def user_logout(request):
    logout(request)

    return index(request)

def add_draft_to_user(req, draf):
    '''
        takes request for user and draft, 
        adds draft to user through proxy model
        '''
    if req.user.is_authenticated():
        userprofile = req.user.userprofile
        x = UserData(userprofile=userprofile, draftlaw=draf,
                date_added=datetime.now())
        x.save()

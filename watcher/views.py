# -*- coding: utf-8 -*-

''' view module '''

from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from watcher.models import DraftLaw, UserProfile, UserData
from watcher.models import DraftLawNotFound
from watcher.forms import AddDraftForm, UserForm


def index(request):
    ''' index page
        shows a list of all drawft laws '''
    context = RequestContext(request)
    context_dict = {}

    drafts = DraftLaw.objects.order_by('-updated')
    context_dict['drafts'] = drafts

    context_dict['userdrafts'] = get_user_drafts(request)

    return render_to_response('watcher/index.html',
                              context_dict, context)

def detail(request, draft_number):
    ''' detail viewl
        shows attributes of a particular drawft law '''
    context = RequestContext(request)
    context_dict = {}

    draft = get_object_or_404(DraftLaw, number=draft_number)
    context_dict['draft'] = draft
    context_dict['history'] = draft.deserialize_history()
    context_dict['userdrafts'] = get_user_drafts(request)
    return render_to_response('watcher/detail.html',
                              context_dict, context)

def add_draft(request):
    context = RequestContext(request)
    context_dict = {}

    if request.method == 'POST':
        form = AddDraftForm(request.POST)
        context_dict['form'] = form
        data = form['number']

        if form.is_valid():  # FIXME: deal with not authorised users
            x = form.cleaned_data['number']
            draft, created = DraftLaw.objects.get_or_create(number=x)
            
            if created:
                try:
                    draft.make_url()
                    draft.populate()
                    draft.save()
                except DraftLawNotFound:
                    form._errors["number"] = form.error_class(
                            ['Законопроект не найден'])
                    return render_to_response('watcher/add_draft.html',
                            context_dict, context)
            return add_draft_to_user(request, draft.number)
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
        context_dict['user_form'] = user_form

        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = UserProfile()
            profile.user = user
            profile.save()
            registered = True
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
                return redirect('index')
            else:
                return HttpResponse('Your Rango account is disabled')
        else:
            return HttpResponse("Invalid login details supplied.")

    else:
        return render_to_response('watcher/login.html', context_dict, context)

@login_required
def user_logout(request):
    logout(request)
    return redirect('index')

@login_required
def add_draft_to_user(request, draft_number):
    '''
        takes request for user and draft, 
        adds draft to user through proxy model
        '''
    userprofile = request.user.userprofile
    draf = DraftLaw.objects.get(number=draft_number)
    x = UserData.objects.get_or_create(userprofile=userprofile, draftlaw=draf)
    return redirect('detail', draft_number=draft_number)

@login_required
def release_user_from_draft(request, draft_number):
    '''
        takes request for user and draft, 
        removes proxy model between them and
        the relation itself
        '''
    userprofile = request.user.userprofile
    draf = get_object_or_404(DraftLaw, number=draft_number)
    x = get_object_or_404(UserData, userprofile=userprofile, draftlaw=draf)
    x.delete()
    return redirect('index')

def get_user_drafts(request):
    if request.user.is_authenticated:
        try:
            us = request.user.userprofile
            userdrafts = DraftLaw.objects.filter(userprofile__pk=us.pk)
            return userdrafts
        except AttributeError:
            return []

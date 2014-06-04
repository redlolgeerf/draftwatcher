# -*- coding: utf-8 -*-

''' view module '''

import sys

from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from watcher.models import DraftLaw, UserProfile, UserData
from watcher.models import DraftLawNotFound
from watcher.forms import AddDraftForm, RegisterForm, AddCommentForm, ProfileForm


def index(request):
    ''' index page
        shows a list of all drawft laws '''
    context = RequestContext(request)
    context_dict = {}

    if request.user.is_authenticated():
        drafts = request.user.userprofile.get_user_drafts()

        if drafts:
            context_dict['userdrafts'] = drafts
            watched = [request.user.userprofile.is_watched(draft)
                    for draft in drafts]
            context_dict['drafts'] = zip(drafts, watched)

    return render_to_response('watcher/index.html',
                              context_dict, context)

def all_drafts(request):
    context = RequestContext(request)
    context_dict = {}

    drafts = DraftLaw.objects.order_by('-updated')
    context_dict['drafts'] = drafts

    if request.user.is_authenticated():
        context_dict['userdrafts'] = request.user.userprofile.get_user_drafts()

    return render_to_response('watcher/all_drafts.html',
                              context_dict, context)

def detail(request, draft_number):
    ''' detail view
        shows attributes of a particular drawft law '''
    context = RequestContext(request)
    context_dict = {}

    draft = get_object_or_404(DraftLaw, number=draft_number)

    if request.user.is_authenticated():
        request.user.userprofile.watch(draft)

    context_dict['draft'] = draft
    context_dict['history'] = draft.deserialize_history()
    context_dict['userdrafts'] = request.user.userprofile.get_user_drafts()

    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        context_dict['form'] = form
        if form.is_valid():
            comment = form.cleaned_data['comment']
            request.user.userprofile.add_comment(draft, comment)
    else:
        comment = request.user.userprofile.get_comment(draft)
        form = AddCommentForm({'comment': comment})
        context_dict['form'] = form
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
                    draft.delete()
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
        user_form = RegisterForm(data=request.POST)
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
        context_dict['user_form'] = RegisterForm()

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
                return HttpResponse('Ваш аккаунт неактивен')
        else:
            context_dict['error'] = 'Неверная пара логин/пароль'
    return render_to_response('watcher/login.html', context_dict, context)

@login_required
def profile(request):
    context = RequestContext(request)
    context_dict = {}
    us = request.user
    prof = us.userprofile

    context_dict['email'] = us.email
    context_dict['user'] = us.username
    context_dict['message'] = ''

    if request.method == 'POST':
        form = ProfileForm(data=request.POST)
        context_dict['user_form'] = form 

        if form.is_valid():
            email = form.cleaned_data['email']
            notify = form.cleaned_data['notify']
            if email:
                us.email = email
                us.save()
            prof.notify = notify
            prof.save()
            context_dict['message'] = 'Изменения успешно сохранены'
    else:
        form = ProfileForm({'email': us.email, 'user': us})
        context_dict['user_form'] = form
    return render_to_response('watcher/profile.html', context_dict, context)

@login_required
def send_verification(request):
    context = RequestContext(request)
    context_dict = {}
    us = request.user
    prof = us.userprofile
    try:
        prof.generate_key()
        prof.verify_email()
        context_dict['message'] = '''Cообщение отправлено.
        Проверьте свой почтовый ящик и перейдите по присланной ссылке,
        чтобы подвердить свой email.'''
    except:
        context_dict['message'] = '''Не удалось отправить сообщение. 
        Обратитесь к администратору.'''
    return render_to_response('watcher/many_purpose.html', context_dict, context)

def verify_email(request, inp):
    context = RequestContext(request)
    context_dict = {}
    context_dict['message'] = 'Не удалось подтвердить email. Неправильная ссылка'
    if ':' in inp:
        x = inp.index(':')
        email = inp[:x]
        key = inp[x+1:]
        try:
            us = User.objects.get(email=email)
            prof = us.userprofile
        except User.DoesNotExist:
            pass
        except UserProfile.DoesNotExist:
            pass
        if key and (key == us.uerprofile.email_verification_key):
            prof.email_verified = True
            prof.save()
            context_dict['message'] = 'Email успешно подтверждён.'
    
    return render_to_response('watcher/many_purpose.html', context_dict, context)
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

# -*- coding: utf-8 -*-

''' view module '''

import sys
import re

from django.db import models
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.generic import ListView, DetailView

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from watcher.models import DraftLaw, UserProfile, UserData
from watcher.models import DraftLawNotFound
from watcher.forms import AddDraftForm, RegisterForm, AddCommentForm, ProfileForm, RestorePasswordForm


class RecentlyVisited(object):
    delimeter = '|'

# from cookies we read like '12345-5,112343-6,12412-5'
    def __init__(self, stuf):
        self.recently_visited = []
        if stuf:
            recently_visited = stuf.split(self.delimeter)
            self.recently_visited = [r for 
                    r in recently_visited if self.validate(r)]

    def validate(self, s):
        if re.search(r'^\d{5,6}-\d$', s):
            return True
        return False

    def add_to(self, s):
        result = self.recently_visited
        if self.validate(s):
            if not (s in self.recently_visited):
                if len(result) >= 10:
                    result = [s] + result[:-1]
                else:
                    result = [s] + result
            else:
                x = result.index(s)
                result = [s] + result[:x] + result[x+1:]
        self.recently_visited = result

    def to_cookie(self):
        return self.delimeter.join(self.recently_visited)

class MainPage(ListView):
    template_name = 'watcher/index.html'

    def get_queryset(self):
        pass

    def get_context_data(self, **kwargs):
        context = super(MainPage, self).get_context_data(**kwargs)
        context['most_watched'] = DraftLaw.objects.annotate(
                nums=models.Count('userprofile')).order_by('-nums')[:5]
        context['recently_updated'] = DraftLaw.objects.order_by('-updated')[:5]
        self.rv = RecentlyVisited(self.request.COOKIES.get('recently_visited'))
        context['recently_visited'] = self.rv.recently_visited
        return context

class UserDraftsList(ListView):
    template_name = 'watcher/userdrafts.html'

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.args[0])
        return DraftLaw.objects.filter(userprofile__user=self.user).order_by('-updated')
        
    def get_context_data(self, **kwargs):
        context = super(UserDraftsList, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            drafts = self.get_queryset()
            userprofile = self.request.user.userprofile
            context['userdrafts'] = userprofile.get_user_drafts() # .order_by('-updated')
            watched = [userprofile.is_watched(draft)
                    for draft in drafts]
            comments = [userprofile.get_comment(draft) 
                    for draft in drafts]
            context['drafts'] = zip(drafts, watched, comments)
            self.rv = RecentlyVisited(self.request.COOKIES.get('recently_visited'))
            context['recently_visited'] = self.rv.recently_visited
        return context

class AllDraftsList(ListView):
    queryset = DraftLaw.objects.order_by('-updated')
    context_object_name = 'drafts'
    template_name = 'watcher/all_drafts.html'

    def get_context_data(self, **kwargs):
        context = super(AllDraftsList, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            context['userdrafts'] = self.request.user.userprofile.get_user_drafts()
        self.rv = RecentlyVisited(self.request.COOKIES.get('recently_visited'))
        context['recently_visited'] = self.rv.recently_visited
        return context

class DraftLawDetailView(DetailView):
    model = DraftLaw
    slug_field = 'number'
    template_name = 'watcher/detail.html'
    context_object_name = 'draft'
    form_class = AddCommentForm

    def get_context_data(self, **kwargs):
        context = super(DraftLawDetailView, self).get_context_data(**kwargs)
        context['history'] = self.object.deserialize_history()
        self.rv = RecentlyVisited(self.request.COOKIES.get('recently_visited'))
        context['recently_visited'] = self.rv.recently_visited
        if self.request.user.is_authenticated():
            userprofile = self.request.user.userprofile
            context['userdrafts'] = userprofile.get_user_drafts()
            context['comment'] = userprofile.get_comment(self.object)
        return context

    def form_valid(self, form):
        comment = form.cleaned_data['comment']
        self.request.user.userprofile.add_comment(self.object, comment)
        return redirect('detail', slug=self.object.number)

    def form_invalid(self, form):
        return redirect('detail', slug=self.object.number)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context['form'] = form
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        self.object = self.get_object()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def render_to_response(self, context, **response_kwargs):
        response = super(DraftLawDetailView, self).render_to_response(context, **response_kwargs)
        self.rv.add_to(self.object.number)
        response.set_cookie('recently_visited', self.rv.to_cookie(), 
                max_age=3600*365*24)
        return response

def add_draft(request):
    context = RequestContext(request)
    context_dict = {}

    if request.method == 'POST':
        form = AddDraftForm(request.POST)
        context_dict['form'] = form
        data = form['number']

        if form.is_valid():  # FIXME: deal with not authorised users
            x = form.cleaned_data['number']
            try:
                draft, created = DraftLaw.objects.get_or_create(number=x)
            except:
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
                next_ = request.POST.get('next')
                if next_:
                    return redirect(next_)
                return redirect('index')
            else:
                return HttpResponse('Ваш аккаунт неактивен')
        else:
            context_dict['error'] = 'Неверная пара логин/пароль'
    else:
        context_dict['next'] = request.GET.get('next')
    return render_to_response('watcher/login.html', context_dict, context)

@login_required
def profile(request):
    context = RequestContext(request)
    context_dict = {}
    us = request.user
    prof = us.userprofile

    context_dict['email'] = us.email
    context_dict['username'] = us.username

    if request.method == 'POST':
        form = ProfileForm(data=request.POST)
        context_dict['user_form'] = form 

        if form.is_valid():
            email = form.cleaned_data['email']
            notify = form.cleaned_data['notify']
            if email and us.email != email:
                us.email = email
                us.save()
            if notify != prof.notify:
                prof.notify = notify
                prof.save()
            return redirect('profile')
    else:
        form = ProfileForm({
            'email': us.email, 'username': us, 'notify': prof.notify})
        context_dict['user_form'] = form
    return render_to_response('watcher/profile.html', context_dict, context)

def send_restore_password(request):
    context = RequestContext(request)
    context_dict = {}
    if request.method == "POST":
        email = request.POST['email']
        try:
            us = User.objects.get(email=email)
            us.userprofile.send_restore_password()
            context_dict['message'] = 'Вам отправленно письмо для восстановления пароля.'
        except User.DoesNotExist:
            context_dict['message'] = 'Нет пользователя с таким email'
    return render_to_response('watcher/send_restore_password.html', context_dict, context)

def restore_password(request, inp=None):
    context = RequestContext(request)
    context_dict = {}
    context_dict['inp'] = inp

    if '/' in inp:
        inp = inp[:-1]

    try:
        prof = UserProfile.objects.get(password_restore_key=inp)
    except UserProfile.DoesNotExist:
        context_dict['message'] = 'Не удалось восстановить пароль. Неправильная ссылка'
        return render_to_response('watcher/restore_password.html',
                context_dict, context)

    if request.method == "POST":
        form = RestorePasswordForm(data=request.POST)
        context_dict['form'] = form
        if form.is_valid():
            x = form.cleaned_data['password']
            prof.user.set_password(x)
            prof.user.save()
            prof.password_restore_key = ''
            prof.save()
            return redirect('user_login')
        else:
            context_dict['message'] = ''
    else:
        if prof.restore_password(inp):
            form = RestorePasswordForm()
            context_dict['form'] = form
        else:
            context_dict['message'] = 'Не удалось восстановить пароль. Ссылка неактивна.'
    return render_to_response('watcher/restore_password.html', context_dict, context)

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
    try:
        prof = UserProfile.objects.get(email_verification_key=inp)
        prof.email_verified = True
        prof.save()
        context_dict['message'] = 'Email успешно подтверждён.'
    except UserProfile.DoesNotExist:
        pass
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
    return redirect('detail', slug=draft_number)

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

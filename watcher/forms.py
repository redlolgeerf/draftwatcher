# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User

from watcher.models import DraftLaw

import re

class AddDraftForm(forms.Form):
    number = forms.CharField(max_length=10, required=False,
            help_text="Пожалуйста, введите номер законопроекта")
#    url = forms.URLField(help_text="Введите url", required=False)

    def clean_number(self):
        data = self.cleaned_data['number']

        data = data.strip()
        if not re.search(r'^\d{5,6}-\d$', data):
            raise forms.ValidationError("Неправильный номер законопроекта.")

        return data

    class Meta:
        fields = ('number', )

class RegisterForm(forms.ModelForm):
    username = forms.CharField(help_text="Логин")
    email = forms.CharField(help_text="Email")
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Пароль")
    password_repeat = forms.CharField(widget=forms.PasswordInput(), help_text="Введите пароль ещё раз")

    def clean_email(self):
        data = self.cleaned_data['email']
        try:
            us = User.objects.get(email=data)
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        except User.DoesNotExist:
            pass
        return data

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')

        if password != password_repeat:
            msg = "Введённые пароли должны совпадать."
            self._errors["password"] = self.error_class([msg])
            del cleaned_data["password"]
            del cleaned_data["password_repeat"]
        return cleaned_data

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_repeat']

class ProfileForm(forms.Form):
    email = forms.CharField(help_text="Email", required=False)
    notify = forms.BooleanField(required=False)
    username = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')
        notify = cleaned_data.get('notify')

        try:
            us = User.objects.get(email=email)
            if us != User.objects.get(username=username):
                msg = "Пользователь с таким email уже существует."
                self._errors["email"] = self.error_class([msg])
                del cleaned_data["email"]
        except User.DoesNotExist:
            pass

        if notify:
            us = User.objects.get(username=username)
            if not us.userprofile.email_verified:
                msg = "Вы должны подтвердить email, чтобы получать рассылку."
                self._errors["notify"] = self.error_class([msg])
                del cleaned_data["notify"]
        return cleaned_data

class AddCommentForm(forms.Form):
    comment = forms.CharField(required=False, widget=forms.Textarea)

    def clean_comment(self):
        data = self.cleaned_data['comment']
        data = data.strip()
        return data

    class Meta:
        fields = ('comment', )

class RestorePasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Пароль")
    password_repeat = forms.CharField(widget=forms.PasswordInput(), help_text="Введите пароль ещё раз")

    def clean(self):
        cleaned_data = super(RestorePasswordForm, self).clean()
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')

        if password != password_repeat:
            msg = "Введённые пароли должны совпадать."
            self._errors["password"] = self.error_class([msg])
            del cleaned_data["password"]
            del cleaned_data["password_repeat"]
        return cleaned_data

    class Meta:
        fields = ['password', 'password_repeat']

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

class UserForm(forms.ModelForm):
    username = forms.CharField(help_text="Please enter a username.")
    email = forms.CharField(help_text="Please enter your email.")
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Please enter a password.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class AddCommentForm(forms.Form):
    comment = forms.CharField(required=False, widget=forms.Textarea)

    def clean_comment(self):
        data = self.cleaned_data['comment']
        data = data.strip()
        return data

    class Meta:
        fields = ('comment', )

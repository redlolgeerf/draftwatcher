# -*- coding: utf-8 -*-

from django import forms

from watcher.models import DraftLaw

class AddDraftForm(forms.ModelForm):
    number = forms.CharField(max_length=10, required=False,
            help_text="Пожалуйста, введите номер законопроекта")
    url = forms.URLField(help_text="Введите url", required=False)

    def clean_number(self):
        data = self.cleaned_data['number']

        try:
            draft = DraftLaw.objects.get(number=data)
            raise forms.ValidationError("Such category is already there.")
        except DraftLaw.DoesNotExist:
            pass

        return data

    class Meta:
        model = DraftLaw
        fields = ('number', 'url')

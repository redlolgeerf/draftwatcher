# -*- coding: utf-8 -*-

""" models for the project """

from django.db import models
from django.contrib.auth.models import User

from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
import requests
from datetime import datetime

class DraftLaw(models.Model):
    ''' class for draft laws '''
    # Ex: 374295-6
    number = models.CharField(
                max_length=10, unique=True,
                help_text="Пожалуйста, введите номер законопроекта")
    title = models.CharField(max_length=300, blank=True)
    # Ex: находится на рассмотрении
    span = models.CharField(max_length=300, blank=True)
    # Ex: http://asozd2.duma.gov.ru/main.nsf/%28Spravka%29?OpenAgent&RN=374295-6
    url = models.URLField(blank=True)

    updated = models.DateTimeField(blank=True, null=True)
    curent_status = models.CharField(max_length=200, blank=True)
    archived = models.BooleanField(default=False)
    history = models.TextField(blank=True)

    def __str__(self):
        return self.number

    def make_url(self):
        magic_url = 'asozd2.duma.gov.ru/main.nsf/(Spravka)?OpenAgent&RN='
        self.url = 'http://' + magic_url + self.number

    def populate(self):
        ''' method which downloads a respective page, parse it and populate
        db with draft law atributes'''
        try:
            self.number, self.title, self.span, h = parse(self.url)
            if 'в архиве' in self.span.lower():
                self.archived = True

            self.updated = datetime.now()

            if h:
                self.curent_status = h[-1]
            self.history = serialize_history(h)
        except AttributeError:
            raise DraftLawNotFound(self.number)

    def update(self):
        ''' method updates draft, if anything has changed'''
        try:
            *__, span, h = parse(self.url)

            if self.span != span:
                self.span = span

            if (self.history and 
                    (deserialize_history(self.history) != h) or
                    not self.history):
                self.history = serialize_history(h)
                self.curent_status = h[-1]

            self.updated = datetime.now()
        except AttributeError:
            pass

class UserProfile(models.Model):
    ''' user profile '''
    user = models.OneToOneField(User)
    draftlaw = models.ManyToManyField(DraftLaw,
            blank=True, through='UserData')

    def __str__(self):
        return self.user.username

class UserData(models.Model):
    '''
        a proxy class for relation between UserProfile and DraftLaw
        '''
    userprofile = models.ForeignKey(UserProfile)
    draftlaw = models.ForeignKey(DraftLaw)
    comment = models.TextField(blank=True)
    date_added = models.DateTimeField(blank=True)

class DraftLawNotFound(Exception):
    def __init__(self, number):
        self.number = number
        Exception.__init__(self, 'Законопроект %s не найден' % number)


def crop_between(text, start, stop=None):
    text = str(text)
    a = text.find(str(start))
    if stop:
        b = text.find(str(stop), a + 1)
        return text[a+1: b].strip()
    return text[a+1: ].strip()

def parse_header(h):
    number = crop_between(h.h2.text, '№')

    if h.p.span:
        status = h.p.span.text
        status = status.strip()
    else:
        status = None
    if status:
        name = h.p.text.replace('\n', ' ')
        name = name.replace(status, '')
    else:
        name = h.p.text.replace('\n', ' ')
    name = name.strip()

    return number, name, status

def parse_history(hb):
    history_header = hb.find_all('div', class_='data-block-show')
    history_block = hb.find_all('div', class_='data-block-doc data-block')

    history = []

    for i, y in zip(history_header, history_block):
        if i.text.startswith('Регистрация'):
            pass
        else:
            history.append(i.text)
    return history

def download(uri):
    html_doc = requests.get(uri)
    html_doc.encoding = 'cp1251'
    html_doc = html_doc.text
    return html_doc

def parse(uri):
    page = download(uri)
    soup = BeautifulSoup(page)
    header = soup.find('div', class_='ecard-header')
    history_box = soup.find('div', class_='tab tab-act')

    title, number, status = parse_header(header)
    history = parse_history(history_box)

    return title, number, status, history

# two functoins to prepare history to be stored in db and to make it list back
def serialize_history(h):
    return "@".join(h)

def deserialize_history(h):
    return h.split('@')

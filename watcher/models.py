# -*- coding: utf-8 -*-

""" models for the project """

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
import requests

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

    def serialize_history(self, h):
        self.history = "@".join(
                ["|".join([piece for piece in line]) for line in h])

    def deserialize_history(self):
        return [line.split('|') for line in self.history.split('@')]

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

            self.updated = timezone.now()

            if h:
                self.curent_status = h[-1][0]
            self.serialize_history(h)
        except AttributeError:
            raise DraftLawNotFound(self.number)

    def update(self):
        ''' method updates draft, if anything has changed'''
        try:
            *__, span, h = parse(self.url)

            if self.span != span:
                self.span = span

            if (self.history and 
                    (self.deserialize_history() != h) or
                    not self.history):
                self.serialize_history(h)
                self.curent_status = h[-1][0]
                self.updated = timezone.now()
        except AttributeError:
            pass

class UserProfile(models.Model):
    ''' user profile '''
    user = models.OneToOneField(User)
    draftlaw = models.ManyToManyField(DraftLaw,
            blank=True, through='UserData')

    def __str__(self):
        return self.user.username

    def get_user_drafts(self):
        try:
            userdrafts = DraftLaw.objects.filter(userprofile__pk=self.pk)
            return userdrafts
        except AttributeError:
            return []

    def get_comment(self, draft):
        try:
            x = UserData.objects.get(userprofile=self, draftlaw=draft)
            return x.comment
        except UserData.DoesNotExist:
            return ''
    
    def watch(self, draft):
        try:
            x = UserData.objects.get(userprofile=self, draftlaw=draft)
            x.watched = timezone.now()
            x.save()
        except UserData.DoesNotExist:
            return False

    def is_watched(self, draft):
        try:
            x = UserData.objects.get(userprofile=self, draftlaw=draft)
            if x.watched and draft.updated:
                return (x.watched < draft.updated)
            else:
                return False
        except UserData.DoesNotExist:
            return False

    def add_comment(self, draft, comment):
        try:
            x = UserData.objects.get(userprofile=self, draftlaw=draft)
            x.comment = comment
            x.save()
        except UserData.DoesNotExist:
            return ''

class UserData(models.Model):
    '''
        a proxy class for relation between UserProfile and DraftLaw
        '''
    userprofile = models.ForeignKey(UserProfile)
    draftlaw = models.ForeignKey(DraftLaw)
    comment = models.TextField(blank=True)
    date_added = models.DateTimeField(default=timezone.now(), blank=True)
    watched = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return (self.userprofile.user.username + " " + self.draftlaw.number)

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
    '''
    we will cycle through the table of tables and save main headers
    together with latest updates for them and date
    '''

    history_header = hb.find_all('div', class_='data-block-show')
    history_block = hb.find_all('div', class_='data-block-doc data-block')

    history = []

    for i, y in zip(history_header, history_block):
        if i.text.startswith('Регистрация'):
            # I just don't need this part
            pass
        else:
            # we use result both as flag to stop iteration
            # and as a list to store data
            result = []
            history_sub_block = y.find_all('table', class_='data-block-table nb tb-nb')
            # need to cycle backwards to grab only the freshst piece
            for z in reversed(history_sub_block):
            # if at this moment result is not empty, 
            # break, because we already have frsher data
                if result:
                    break
                history_line = z.find_all('tr')
                for x in reversed(history_line):
                    collumns = x.find_all('td')
            # we need a row with date in second collumn
                    if collumns[1].text.strip():
                        result.append(crop_between(i.text.strip(), stop = ','))
                        result.append(crop_between(collumns[0].text, stop = '(')) # FIXME <br /> glues words (look at 466627-6)
                        result.append(crop_between(collumns[1].text, stop =' '))
                        break
            history.append(result)
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

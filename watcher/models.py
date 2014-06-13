# -*- coding: utf-8 -*-

""" models for the project """

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail, send_mail
from django.core.signing import Signer, TimestampSigner, BadSignature, SignatureExpired

from bs4 import BeautifulSoup
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
    text_url = models.URLField(blank=True)

    updated = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    curent_status = models.CharField(max_length=200, blank=True)
    archived = models.BooleanField(default=False)
    history = models.TextField(blank=True)

    class Meta:
        verbose_name = 'законопроект'
        verbose_name_plural = 'законопроекты'

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if not self.pk:  # object is being created, thus no primary key field yet
            self.make_url()
            self.populate()
        super(DraftLaw, self).save(*args, **kwargs)
        
    def serialize_history(self, h):
        return "@".join(
                ["|".join([piece for piece in line]) for line in h])

    def deserialize_history(self):
        return [line.split('|') for line in self.history.split('@')]

    def make_url(self):
        magic_url = 'asozd2.duma.gov.ru/main.nsf/(Spravka)?OpenAgent&RN='
        self.url = 'http://' + magic_url + self.number

    def archive(self):
        if 'в архиве' in self.span.lower():
            self.archived = True

    def populate(self):
        ''' method which downloads a respective page, parse it and populate
        db with draft law atributes'''
        try:
            self.number, self.title, self.span, h, t = self.parse(self.url)

            self.archive()
            self.updated = timezone.now()
            self.date_updated = timezone.now()

            if h:
                self.curent_status = " - ".join(h[-1])
                self.history = self.serialize_history(h)

            if t:
                self.text_url = t
        except AttributeError:
            raise DraftLawNotFound(self.number)

    def update(self):
        ''' method updates draft, if anything has changed'''
        *__, self.span, h, t = self.parse(self.url)

        self.archive()
        if (self.history and 
                (self.deserialize_history() != h) or
                not self.history):
            self.history = self.serialize_history(h)
            self.curent_status = " - ".join(h[-1])
            self.updated = timezone.now()
            if t:
                self.text_url = t
            try:
                self.notify_users()
            except:
                pass
        self.date_updated = timezone.now()

    def parse_header(self, h):
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

    def parse_history(self, hb):
        '''
        we will cycle through the table of tables and save main headers
        together with latest updates for them and date
        '''

        history_header = hb.find_all('div', class_='data-block-show')
        history_block = hb.find_all('div', class_='data-block-doc data-block')

        history = []
        text_url = ''

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
                # break, because we already have fresher data
                    if result:
                        break
                    history_line = z.find_all('tr')
                    for x in reversed(history_line):
                        collumns = x.find_all('td')
                        if not text_url:
                            if collumns[0].a:
                                if 'Текст' in collumns[0].a.text:
                                    text_url = collumns[0].a.get('href')
                                    text_url = 'http://asozd2.duma.gov.ru' + text_url
                # we need a row with date in second collumn
                        if collumns[1].text.strip():
                            result.append(crop_between(i.text.strip(), stop = ','))
                            result.append(crop_between(collumns[0].text, stop = '(')) # FIXME <br /> glues words (look at 466627-6)
                            result.append(crop_between(collumns[1].text, stop =' '))
                            break
                if result:
                    history.append(result)
        return history, text_url

    def download(self, uri):
        html_doc = requests.get(uri)
        html_doc.encoding = 'cp1251'
        html_doc = html_doc.text
        return html_doc

    def parse(self, uri):
        page = self.download(uri)
        soup = BeautifulSoup(page)
        header = soup.find('div', class_='ecard-header')
        history_box = soup.find('div', class_='tab tab-act')

        title, number, status = self.parse_header(header)
        history, text_url = self.parse_history(history_box)

        return title, number, status, history, text_url

    def notify_users(self):
        users_to_notify = self.userprofile_set.all()
        sender = 'admin@gmail.com' 
        msg = {}
        msg['subject'] = 'Обновлен статус законопроекта %s' % self.number
        # FIXME: add link to unsuscribe
        # FIXME: make letter more explanatory
        msg['body'] = '''
        Обновлен статус законопроекта {number}.
        Новый статус: {status}.
        Вы можете посмотреть историю изменений у нас на сайте http://draftwatcher.pythonanywhere.com/draft/{number}/ или
        на странице Государственной Думы {url}.

        Если вы не ходите получать рассылку, просто нажмите на ссылку.
        '''.format(number=self.number, url=self.url, status=self.curent_status)  
        mails = []

        for recepient in users_to_notify:
            mails.append((msg['subject'], msg['body'], sender,
                    [recepient.user.email]))
        send_mass_mail(tuple(mails), fail_silently=False)

class UserProfile(models.Model):
    ''' user profile '''
    user = models.OneToOneField(User)
    draftlaw = models.ManyToManyField(DraftLaw,
            blank=True, through='UserData')
    email_verified = models.BooleanField(default=False)
    email_verification_key = models.CharField(max_length=300, blank=True)
    notify = models.BooleanField(default=False)
    password_restore_key = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __str__(self):
        return self.user.username

    def generate_key(self):
        email = self.user.email
        if email:
            signer = Signer()
            key = signer.sign(email)
            x = key.index(':')
            key = key[x+1:]
            self.email_verification_key = key
            self.save()

    def verify_email(self):
        sender = 'admin@gmail.com' 
        msg = {}
        msg['subject'] = 'Подтверждение email' 
        magic_url = 'http://draftwatcher.pythonanywhere.com/'
        msg['body'] = '''
        Если вы хотите получать уведомления об обновлении законопроектов на сайте
        Закономонитор, пожалуйста, перейдите по ссылке 
        {url}.
        
        Если вы не иницировали отправление этого сообщения, 
        просто проигнорируйте его
        '''.format(
                url=''.join(
                    (magic_url,'verify_email/', self.email_verification_key)))

        send_mail(msg['subject'], msg['body'], sender,
            [self.user.email], fail_silently=False)

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

    def send_restore_password(self):
        signer = TimestampSigner()
        value = signer.sign(self.user.username)
        x = value.index(':')
        key = value[x+1:]
        
        self.password_restore_key = key
        self.save()

        sender = 'admin@gmail.com' 
        msg = {}
        msg['subject'] = 'Восстановление пароля' 
        magic_url = 'http://draftwatcher.pythonanywhere.com/'
        msg['body'] = '''
        Вы запросили восстановление пароля. Если Вы хотите
        сбросить пароль, перейдите по ссылке:
        {url}.
        Ссылка будет активна в течение пяти минут.
        
        Если вы не иницировали отправление этого сообщения, 
        просто проигнорируйте его.
        '''.format(
                url=''.join(
                    (magic_url,'restore_password/', key)))

        send_mail(msg['subject'], msg['body'], sender,
            [self.user.email], fail_silently=False)
        return key

    def restore_password(self, inp):
        key = self.user.username + ":" + inp
        signer = TimestampSigner()
        try:
            x = signer.unsign(key, max_age=60*5)
            if x == self.user.username:
                return True
        except (SignatureExpired, BadSignature):
            pass
        return False



class UserData(models.Model):
    '''
        a proxy class for relation between UserProfile and DraftLaw
        '''
    userprofile = models.ForeignKey(UserProfile)
    draftlaw = models.ForeignKey(DraftLaw)
    comment = models.TextField(blank=True)
    date_added = models.DateTimeField(default=timezone.now(), blank=True)
    watched = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'пользовательская информация'
        verbose_name_plural = 'пользовательская информация'

    def __str__(self):
        return (self.userprofile.user.username + " " + self.draftlaw.number)

class DraftLawNotFound(Exception):
    def __init__(self, number):
        self.number = number
        Exception.__init__(self, 'Законопроект %s не найден' % number)


def crop_between(text, start=None, stop=None):
    text = str(text)
    if start:
        a = text.find(str(start))
    else:
        a = -1
    if stop:
        b = text.find(str(stop), a + 1)
        if b == -1:
            b = len(text)
        return text[a+1: b].strip()
    return text[a+1: ].strip()


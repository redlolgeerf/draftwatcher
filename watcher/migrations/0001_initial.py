# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DraftLaw'
        db.create_table('watcher_draftlaw', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('title', self.gf('django.db.models.fields.CharField')(blank=True, max_length=300)),
            ('span', self.gf('django.db.models.fields.CharField')(blank=True, max_length=300)),
            ('url', self.gf('django.db.models.fields.URLField')(blank=True, max_length=200)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True)),
            ('date_updated', self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True)),
            ('curent_status', self.gf('django.db.models.fields.CharField')(blank=True, max_length=200)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('history', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('watcher', ['DraftLaw'])

        # Adding model 'UserProfile'
        db.create_table('watcher_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('email_verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email_verification_key', self.gf('django.db.models.fields.CharField')(blank=True, max_length=300)),
            ('notify', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('watcher', ['UserProfile'])

        # Adding model 'UserData'
        db.create_table('watcher_userdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userprofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['watcher.UserProfile'])),
            ('draftlaw', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['watcher.DraftLaw'])),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(blank=True, default=datetime.datetime(2014, 6, 7, 0, 0))),
            ('watched', self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True)),
        ))
        db.send_create_signal('watcher', ['UserData'])


    def backwards(self, orm):
        # Deleting model 'DraftLaw'
        db.delete_table('watcher_draftlaw')

        # Deleting model 'UserProfile'
        db.delete_table('watcher_userprofile')

        # Deleting model 'UserData'
        db.delete_table('watcher_userdata')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['auth.Permission']", 'symmetrical': 'False'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'user_set'", 'to': "orm['auth.Group']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'user_set'", 'to': "orm['auth.Permission']", 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'", 'object_name': 'ContentType'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'watcher.draftlaw': {
            'Meta': {'object_name': 'DraftLaw'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'curent_status': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '200'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'history': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'span': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '300'}),
            'title': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '300'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'blank': 'True', 'max_length': '200'})
        },
        'watcher.userdata': {
            'Meta': {'object_name': 'UserData'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'default': 'datetime.datetime(2014, 6, 7, 0, 0)'}),
            'draftlaw': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['watcher.DraftLaw']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['watcher.UserProfile']"}),
            'watched': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'})
        },
        'watcher.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'draftlaw': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['watcher.DraftLaw']", 'through': "orm['watcher.UserData']", 'symmetrical': 'False'}),
            'email_verification_key': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '300'}),
            'email_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notify': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['watcher']
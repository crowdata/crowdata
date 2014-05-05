# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DocumentSet'
        db.create_table(u'crowdataapp_documentset', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length='128')),
            ('slug', self.gf('django_extensions.db.fields.AutoSlugField')(allow_duplicates=False, max_length=50, separator=u'-', blank=True, populate_from='name', overwrite=False)),
            ('template_function', self.gf('django.db.models.fields.TextField')(default='// Javascript function to insert the document into the DOM.\n// Receives the URL of the document as its only parameter.\n// Must be called insertDocument\n// JQuery is available\n// resulting element should be inserted into div#document-viewer-container\nfunction insertDocument(document_url) {\n}\n')),
            ('entries_threshold', self.gf('django.db.models.fields.IntegerField')(default=3)),
        ))
        db.send_create_signal(u'crowdataapp', ['DocumentSet'])

        # Adding model 'DocumentSetForm'
        db.create_table(u'crowdataapp_documentsetform', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
            ('intro', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('button_text', self.gf('django.db.models.fields.CharField')(default=u'Submit', max_length=50)),
            ('response', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('expiry_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('login_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('send_email', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('email_from', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('email_copies', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('email_subject', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('email_message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('document_set', self.gf('django.db.models.fields.related.ForeignKey')(related_name='form', unique=True, to=orm['crowdataapp.DocumentSet'])),
        ))
        db.send_create_signal(u'crowdataapp', ['DocumentSetForm'])

        # Adding M2M table for field sites on 'DocumentSetForm'
        m2m_table_name = db.shorten_name(u'crowdataapp_documentsetform_sites')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('documentsetform', models.ForeignKey(orm[u'crowdataapp.documentsetform'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['documentsetform_id', 'site_id'])

        # Adding model 'DocumentSetFormField'
        db.create_table(u'crowdataapp_documentsetformfield', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(default='', max_length=100, blank=True)),
            ('field_type', self.gf('django.db.models.fields.IntegerField')()),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('choices', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('default', self.gf('django.db.models.fields.CharField')(max_length=2000, blank=True)),
            ('placeholder_text', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('help_text', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('autocomplete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['crowdataapp.DocumentSetForm'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'crowdataapp', ['DocumentSetFormField'])

        # Adding model 'DocumentSetFormEntry'
        db.create_table(u'crowdataapp_documentsetformentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entries', to=orm['crowdataapp.DocumentSetForm'])),
        ))
        db.send_create_signal(u'crowdataapp', ['DocumentSetFormEntry'])

        # Adding model 'Document'
        db.create_table(u'crowdataapp_document', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256, null=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length='512')),
            ('document_set', self.gf('django.db.models.fields.related.ForeignKey')(related_name='documents', to=orm['crowdataapp.DocumentSet'])),
        ))
        db.send_create_signal(u'crowdataapp', ['Document'])

        # Adding model 'DocumentUserFormEntry'
        db.create_table(u'crowdataapp_documentuserformentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('form_entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forms.FormEntry'])),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entries', to=orm['crowdataapp.Document'])),
        ))
        db.send_create_signal(u'crowdataapp', ['DocumentUserFormEntry'])


    def backwards(self, orm):
        # Deleting model 'DocumentSet'
        db.delete_table(u'crowdataapp_documentset')

        # Deleting model 'DocumentSetForm'
        db.delete_table(u'crowdataapp_documentsetform')

        # Removing M2M table for field sites on 'DocumentSetForm'
        db.delete_table(db.shorten_name(u'crowdataapp_documentsetform_sites'))

        # Deleting model 'DocumentSetFormField'
        db.delete_table(u'crowdataapp_documentsetformfield')

        # Deleting model 'DocumentSetFormEntry'
        db.delete_table(u'crowdataapp_documentsetformentry')

        # Deleting model 'Document'
        db.delete_table(u'crowdataapp_document')

        # Deleting model 'DocumentUserFormEntry'
        db.delete_table(u'crowdataapp_documentuserformentry')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'crowdataapp.document': {
            'Meta': {'object_name': 'Document'},
            'document_set': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'documents'", 'to': u"orm['crowdataapp.DocumentSet']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': "'512'"})
        },
        u'crowdataapp.documentset': {
            'Meta': {'object_name': 'DocumentSet'},
            'entries_threshold': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'128'"}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "'name'", 'overwrite': 'False'}),
            'template_function': ('django.db.models.fields.TextField', [], {'default': "'// Javascript function to insert the document into the DOM.\\n// Receives the URL of the document as its only parameter.\\n// Must be called insertDocument\\n// JQuery is available\\n// resulting element should be inserted into div#document-viewer-container\\nfunction insertDocument(document_url) {\\n}\\n'"})
        },
        u'crowdataapp.documentsetform': {
            'Meta': {'object_name': 'DocumentSetForm'},
            'button_text': ('django.db.models.fields.CharField', [], {'default': "u'Submit'", 'max_length': '50'}),
            'document_set': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'form'", 'unique': 'True', 'to': u"orm['crowdataapp.DocumentSet']"}),
            'email_copies': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'email_from': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'email_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_subject': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'response': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'send_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'default': '[1]', 'to': u"orm['sites.Site']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'crowdataapp.documentsetformentry': {
            'Meta': {'object_name': 'DocumentSetFormEntry'},
            'entry_time': ('django.db.models.fields.DateTimeField', [], {}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': u"orm['crowdataapp.DocumentSetForm']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'crowdataapp.documentsetformfield': {
            'Meta': {'object_name': 'DocumentSetFormField'},
            'autocomplete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'choices': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'field_type': ('django.db.models.fields.IntegerField', [], {}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': u"orm['crowdataapp.DocumentSetForm']"}),
            'help_text': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'placeholder_text': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'crowdataapp.documentuserformentry': {
            'Meta': {'object_name': 'DocumentUserFormEntry'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': u"orm['crowdataapp.Document']"}),
            'form_entry': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forms.FormEntry']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
        },
        u'forms.form': {
            'Meta': {'object_name': 'Form'},
            'button_text': ('django.db.models.fields.CharField', [], {'default': "u'Submit'", 'max_length': '50'}),
            'email_copies': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'email_from': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'email_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_subject': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'response': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'send_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'default': '[1]', 'to': u"orm['sites.Site']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'forms.formentry': {
            'Meta': {'object_name': 'FormEntry'},
            'entry_time': ('django.db.models.fields.DateTimeField', [], {}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': u"orm['forms.Form']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['crowdataapp']
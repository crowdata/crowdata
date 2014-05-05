# coding: utf-8
import csv, sys, re, json, itertools
from datetime import datetime
import django.db.models
import django.http
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.db import transaction
from django.conf.urls import patterns, url
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.forms import TextInput
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect

from django_ace import AceWidget
from nested_inlines.admin import NestedModelAdmin,NestedTabularInline, NestedStackedInline
import forms_builder

from crowdataapp import models

class DocumentSetFormFieldAdmin(NestedTabularInline):
    model = models.DocumentSetFormField
    exclude = ('slug', )
    extra = 1

class DocumentSetFormInline(NestedStackedInline):
    fields = ("title", "intro", "button_text")
    model = models.DocumentSetForm
    inlines = [DocumentSetFormFieldAdmin]
    show_url = False

class CanonicalFieldEntryLabel(NestedTabularInline):
    model = models.CanonicalFieldEntryLabel
    fields = ('value', 'form_field')
    initial = 1

class DocumentSetRankingDefinitionInline(NestedTabularInline):
    fields = ('name', 'label_field', 'magnitude_field', 'amount_rows_on_home', 'grouping_function', 'sort_order')
    model = models.DocumentSetRankingDefinition
    max_num = 2

    LABEL_TYPES = (
        forms_builder.forms.fields.TEXT,
        forms_builder.forms.fields.SELECT,
        forms_builder.forms.fields.RADIO_MULTIPLE,
    )

    MAGNITUDE_TYPES = (
        forms_builder.forms.fields.NUMBER,
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # this sucks
        document_set_id = int(re.search('documentset/(\d+)', request.path).groups()[0])
        document_set = models.DocumentSet.objects.get(pk=document_set_id)
        qs = models.DocumentSetFormField.objects.filter(form__document_set=document_set)

        if db_field.name == 'label_field':
            # get fields from this document_set form that can only act as labels
            kwargs["queryset"] = qs.filter(field_type__in=self.LABEL_TYPES, verify=True)
        elif db_field.name == 'magnitude_field':
            # get fields from this document_set form that can only act as magnitudes
            kwargs["queryset"] = qs.filter(field_type__in=self.MAGNITUDE_TYPES, verify=True)
        return super(DocumentSetRankingDefinitionInline, self) \
            .formfield_for_foreignkey(db_field, request, **kwargs)

class CanonicalFieldEntryLabelAdmin(NestedModelAdmin):
    class Media:
        css = {
            'all': ('admin/css/document_set_admin.css',
                    '/static/django_ace/widget.css')
        }
        js = ('admin/js/document_set_admin.js',
              'django_ace/ace/ace.js',
              'django_ace/widget.js'
        )

    # class ClusterForm(forms_builder.forms.forms.FormForForm):
    #     _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    #     canon = forms.ModelChoiceField(KeyWord.objects)

    list_display = ('value', 'form_field', 'document_set')
    search_fields = ['value']
    actions = ['cluster_canons_action']

    def cluster_canons_action(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        #ct = ContentType.objects.get_for_model(queryset.model)
        #return HttpResponseRedirect("/cluster/?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))
        return HttpResponseRedirect("/admin/crowdataapp/canonicalfieldentrylabel/cluster/?ids=%s" % ",".join(selected))
    cluster_canons_action.short_description = _('Cluster several canons into only one of them.')

    def get_urls(self):
        urls = super(CanonicalFieldEntryLabelAdmin, self).get_urls()

        extra_urls = patterns('',
                              url('^cluster/$',
                                  self.admin_site.admin_view(self.cluster_canons),
                                  name="cluster_canons"),
                                  )
        return extra_urls + urls


    def cluster_canons(self, request):

      if request.GET.get('ids') is None:

        the_canon_id = int(request.POST['canon'])
        the_canon = models.CanonicalFieldEntryLabel.objects.get(pk=the_canon_id)

        canon_ids = [int(i) for i in request.POST['ids'].split(',')]
        canon_ids.remove(the_canon_id)

        canons_to_cluster = models.CanonicalFieldEntryLabel.objects.filter(id__in=canon_ids)

        # Asign all entries to the canon
        # Remove the empty canons
        for canon in canons_to_cluster:
          canon.reassign_entries_to(the_canon)
          if not canon.has_entries():
            canon.delete()

        # cluster the canons
        return redirect(reverse('admin:crowdataapp_canonicalfieldentrylabel_changelist'))
      else:
        canon_ids = [int(i) for i in request.GET['ids'].split(',')]
        canons_to_cluster = models.CanonicalFieldEntryLabel.objects.filter(id__in=canon_ids)

        # Check that all the canons to cluster have the same form-field
        canons_with_the_same_form_field = canons_to_cluster.filter(form_field=canons_to_cluster[0].form_field)
        if (len(canons_with_the_same_form_field) == len(canons_to_cluster)):
          return render_to_response('admin/cluster_canons.html',
                                 {
                                  'canon_ids': request.GET['ids'],
                                  'canons': canons_to_cluster,
                                  'current_app': self.admin_site.name
                                 },
                                 RequestContext(request))
        else:
          return redirect(reverse('admin:crowdataapp_canonicalfieldentrylabel_changelist'))

class DocumentSetAdmin(NestedModelAdmin):

    class Media:
        css = {
            'all': ('admin/css/document_set_admin.css',
                    '/static/django_ace/widget.css')
        }
        js = ('admin/js/document_set_admin.js',
              'django_ace/ace/ace.js',
              'django_ace/widget.js'
        )

    list_display = ('name', 'published', 'document_count', 'admin_links')

    fieldsets = (
        (_('Document Set Description'), {
            'fields': ('name', 'description', 'header_image', 'tosum_field', 'published')
        }),
        (_('Document Set Behaviour'), {
            'fields': ('entries_threshold', 'template_function', 'head_html')
        })
    )
    inlines = ()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if (re.search('documentset/(\d+)', request.path)):
          document_set_id = int(re.search('documentset/(\d+)', request.path).groups()[0])
          document_set = models.DocumentSet.objects.get(pk=document_set_id)
          qs = models.DocumentSetFormField.objects.filter(form__document_set=document_set)

          if db_field.name == 'tosum_field':
              kwargs["queryset"] = qs.filter(field_type__in={ forms_builder.forms.fields.NUMBER }, verify=True)
        return super(DocumentSetAdmin, self) \
            .formfield_for_foreignkey(db_field, request, **kwargs)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = (DocumentSetFormInline, DocumentSetRankingDefinitionInline)
        return super(DocumentSetAdmin, self).change_view(request, object_id)

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = (DocumentSetFormInline,)
        return super(DocumentSetAdmin, self).add_view(request)

    def get_urls(self):
        urls = super(DocumentSetAdmin, self).get_urls()

        extra_urls = patterns('',
                              url('^(?P<document_set_id>\d+)/answers/$',
                                  self.admin_site.admin_view(self.answers_view),
                                  name="document_set_answers_csv"),
                              url('^(?P<document_set_id>\d+)/add_documents/$',
                                  self.admin_site.admin_view(self.add_documents_view),
                                  name='document_set_add_documents'),
                              url('^(?P<document_set_id>\d+)/update_canons/$',
                                  self.admin_site.admin_view(self.update_canons_view),
                                  name='document_set_update_canons'),
                              url('^(?P<document_set_id>\d+)/reverify_documents/$',
                                self.admin_site.admin_view(self.reverify_documents_view),
                                  name='document_set_reverify_documents')
                             )

        return extra_urls + urls

    def add_documents_view(self, request, document_set_id):
        """ add a bunch of documents to
         a DocumentSet by uploading a CSV """
        document_set = get_object_or_404(self.model, pk=document_set_id)
        if request.FILES.get('csv_file'):
            # got a CSV, process, check and create
            csvreader = csv.reader(request.FILES.get('csv_file'))

            header_row = csvreader.next()
            if [h.strip() for h in header_row] != ['document_title', 'document_url']:
                messages.error(request,
                               _('Header cells must be document_title and document_url'))


            count = 0
            try:
                with transaction.commit_on_success():
                    for row in csvreader:
                        document_set.documents.create(name=row[0].strip(),
                                                      url=row[1].strip())
                        count += 1
            except:
                messages.error(request,
                               _('Could not create documents'))

                return redirect(reverse('admin:document_set_add_documents',
                                        args=(document_set_id,)))

            messages.info(request,
                          _('Successfully created %(count)d documents') % { 'count': count })

            return redirect(reverse('admin:crowdataapp_documentset_changelist'))

        else:
            return render_to_response('admin/document_set_add_documents.html',
                                      {
                                          'document_set': document_set,
                                          'current_app': self.admin_site.name,
                                      },
                                      RequestContext(request))

    def update_canons_view(self, request, document_set_id):
      """Update canons for the document set"""

      def _encode_dict_for_csv(d):
          rv = {}
          for k,v in d.items():
              k = k.encode('utf8') if type(k) == unicode else k
              if type(v) == datetime:
                  rv[k] = v.strftime('%Y-%m-%d %H:%M')
              elif type(v) == unicode:
                  rv[k] = v.encode('utf8')
              elif type(v) == bool:
                  rv[k] = 'true' if v else 'false'
              else:
                  rv[k] = v

          return rv

      response = django.http.HttpResponse(mimetype="text/csv")

      writer = csv.DictWriter(response, fieldnames=['entry_id', 'entry_value', 'entry_canonical_value'],extrasaction='ignore')
      writer.writeheader()

      for entry in models.DocumentSetFieldEntry.objects.all():
        if models.DocumentSetFormField.objects.get(pk=entry.field_id).autocomplete:
          try:
            entry.canonical_label = entry.get_canonical_value()
            entry.save()
            mensaje = entry.canonical_label.value
          except Exception, e:
            mensaje = "Failed %s" % e
          writer.writerow(_encode_dict_for_csv({'entry_id': entry.id, 'entry_value': entry.value, 'entry_canonical_value': mensaje}))

      return response

    def reverify_documents_view(self, request, document_set_id):
      """Reverify all the documents for document set"""
      pass

    def answers_view(self, request, document_set_id):

        def _encode_dict_for_csv(d):
            rv = {}
            for k,v in d.items():
                k = k.encode('utf8') if type(k) == unicode else k
                if type(v) == datetime:
                    rv[k] = v.strftime('%Y-%m-%d %H:%M')
                elif type(v) == unicode:
                    rv[k] = v.encode('utf8')
                elif type(v) == bool:
                    rv[k] = 'true' if v else 'false'
                else:
                    rv[k] = v

            return rv

        def partition(items, predicate=bool):
            a, b = itertools.tee((predicate(item), item) for item in items)
            return ((item for pred, item in a if not pred),
                    (item for pred, item in b if pred))

        document_set = get_object_or_404(self.model, pk=document_set_id)
        response = django.http.HttpResponse(mimetype="text/csv")

        entries = models.DocumentSetFormEntry \
                        .objects \
                        .filter(document__in=document_set.documents.all())

        if len(entries) == 0:
            return django.http.HttpResponse('')

        answer_field, non_answer_field = partition([u.encode('utf8') for u in entries[0].to_dict().keys()],
                                                   lambda fn: not fn.startswith('answer_'))

        writer = csv.DictWriter(response, fieldnames=sorted(non_answer_field) + sorted(answer_field),extrasaction='ignore')

        writer.writeheader()
        for entry in entries:
            writer.writerow(_encode_dict_for_csv(entry.to_dict()))

        return response


    def document_count(self, obj):
        l = '<a href="%s?document_set__id=%s">%s</a>' % (reverse("admin:crowdataapp_document_changelist"),
                                                           obj.pk,
                                                           obj.documents.count())
        return mark_safe(l)


class DocumentSetFormEntryInline(admin.TabularInline):
    fields = ('user_link', 'answers', 'entry_time', 'document_link', 'document_set_link')
    readonly_fields = ('user_link', 'answers', 'entry_time', 'document_link', 'document_set_link')
    ordering = ('document',)
    list_select_related = True
    model = models.DocumentSetFormEntry
    extra = 0

    def answers(self, obj):
        field_template = "<li><input type=\"checkbox\" data-change-url=\"%s\" data-field-entry=\"%d\" data-document=\"%d\" data-entry-value=\"%s\" %s><span class=\"%s\">%s</span>: <strong>%s</strong> - <em>%s</em></li>"
        rv = '<ul>'
        form_fields = obj.form.fields.order_by('id').all()
        rv += ''.join([field_template % (reverse('admin:document_set_field_entry_change', args=(obj.document.pk, e.pk,)),
                                         e.pk,
                                         obj.document.pk,
                                         e.value,
                                         'checked' if e.verified else '',
                                         'verify' if f.verify else '',
                                         f.label,
                                         e.value,
                                         e.assigned_canonical_value())
                       for f, e in zip(form_fields,
                                       obj.fields.order_by('field_id').all())])
        rv += '</ul>'

        return mark_safe(rv)


    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=(obj.user.id,))
        return mark_safe('<a href="%s">%s</a>' % (url, obj.user.get_full_name()))

    def document_link(self, obj):
        url = reverse('admin:crowdataapp_document_change', args=(obj.document.id,))
        return mark_safe('<a href="%s">%s</a>' % (url, obj.document.name))

    def document_set_link(self, obj):
        url = reverse('admin:crowdataapp_documentset_change', args=(obj.document.document_set.id,))
        return mark_safe('<a href="%s">%s</a>' % (url, obj.document.document_set.name))


class DocumentAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('admin/css/document_admin.css', )
        }
        js = ('admin/js/jquery-2.0.3.min.js', 'admin/js/nested.js', 'admin/js/document_admin.js',)

    fields = ('name', 'url', 'document_set_link', 'verified')
    readonly_fields = ('document_set_link','verified')
    list_display = ('name', 'verified', 'entries_count', 'document_set')
    list_filter = ('document_set__name','verified')
    search_fields = ['form_entries__fields__value', 'name']
    inlines = [DocumentSetFormEntryInline]
    actions = ['verify_document']

    def queryset(self, request):
        return models.Document.objects.annotate(entries_count=Count('form_entries'))

    def get_urls(self):
        urls = super(DocumentAdmin, self).get_urls()
        my_urls = patterns('',
                           url('^(?P<document>\d+)/document_set_field_entry/(?P<document_set_field_entry>\d+)/$',
                               self.admin_site.admin_view(self.field_entry_set),
                               name='document_set_field_entry_change')
        )
        return my_urls + urls

    def field_entry_set(self, request, document, document_set_field_entry):
        """ Set verify status for form field entries """
        if request.method != 'POST':
            return django.http.HttpResponseBadRequest()

        document = get_object_or_404(models.Document, pk=document)
        this_field_entry = get_object_or_404(models.DocumentSetFieldEntry, pk=document_set_field_entry)

        # get all answers for the same document that match with this one
        coincidental_field_entries = models.DocumentSetFieldEntry.objects.filter(field_id=this_field_entry.field_id,
                                                                                 value=this_field_entry.value,
                                                                                 entry__document=this_field_entry.entry.document)

        # set the verified state for all the matching answers
        for fe in coincidental_field_entries:
            fe.verified = (request.POST['verified'] == 'true')
            fe.save()

        # if there are verified answers for every field that's marked as 'verify'
        # set this Document as verified
        verified_fields = models.DocumentSetFormField \
                                .objects \
                                .filter(pk__in=set(map(lambda fe: fe.field_id,
                                                       models.DocumentSetFieldEntry.objects.filter(entry__document=this_field_entry.entry.document,
                                                                                                   verified=True))),
                                        verify=True,
                                        form=this_field_entry.entry.form)

        document.verified = (len(verified_fields) == len(models.DocumentSetFormField.objects.filter(verify=True,
                                                                                                    form=this_field_entry.entry.form)))

        document.save()

        return django.http.HttpResponse(json.dumps(map(lambda fe: fe.pk,
                                                       coincidental_field_entries)),
                                                   content_type="application/json")


    def document_set_link(self, obj):
        # crowdataapp_documentset_change
        change_url = reverse('admin:crowdataapp_documentset_change', args=(obj.document_set.id,))
        return mark_safe('<a href="%s">%s</a>' % (change_url, obj.document_set.name))
    document_set_link.short_description = _('Document Set')

    def entries_count(self, doc):
        return doc.entries_count
    entries_count.admin_order_field = 'entries_count'

    # Verify the documents by admin or without admin
    def verify_document(self, request, queryset):
      for doc in queryset:
        if doc.is_revised_by_staff():
          doc.force_verify()
        else:
          doc.verify()
    verify_document.short_description = _('Re-verify selected documents.')

class CrowDataUserAdmin(UserAdmin):

    class Media:
        css = {
            'all': ('admin/css/user_admin.css', )
        }
        js = ('admin/js/jquery-2.0.3.min.js',
              'admin/js/nested.js',
              'admin/js/user_admin.js',
              'admin/js/document_admin.js',)


    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    inlines = [DocumentSetFormEntryInline]

    readonly_fields = ('last_login', 'date_joined', )


admin.site.register(models.DocumentSet, DocumentSetAdmin)
admin.site.register(models.Document, DocumentAdmin)
admin.site.unregister(forms_builder.forms.models.Form)

admin.site.register(models.CanonicalFieldEntryLabel, CanonicalFieldEntryLabelAdmin)

admin.site.unregister(User)
admin.site.register(User, CrowDataUserAdmin)

from django.contrib.sites.models import Site
admin.site.unregister(Site)
admin.site.unregister(Group)

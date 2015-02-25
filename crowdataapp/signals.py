# coding: utf-8
from urlparse import urlparse

from django.dispatch import receiver
from django.core.urlresolvers import resolve

from forms_builder.forms.signals import form_valid, form_invalid

from crowdataapp import models

def create_entry(sender=None, form=None, entry=None, document_id=None, **kwargs):

    request = sender

    if not request.user.is_authenticated() or document_id is None:
        raise

    # if the document already has an entry for the user, raise
    if models.Document.objects.get(pk=document_id).has_entry_for_user(request.user):
        raise Exception(_("The document %s already has an entry.") % document_id)

    try:

        # Create the entry
        entry.document = models.Document.objects.get(pk=document_id)
        entry.user = request.user

        # Save all the canonical for the fields of the entry
        for f in entry.fields.all():
          if models.DocumentSetFormField.objects.get(pk=f.field_id).autocomplete:
            f.canonical_label = f.get_canonical_value()
            f.save()
        # Save the entry
        entry.save()

        # Verify the document
        if request.user.is_staff or request.user.is_superuser:
            entry.force_verify()
        else:
            entry.document.verify()
    except Exception as e:
        # should delete the 'entry' here
        entry.delete()
        raise

@receiver(form_invalid)
def invalid_entry(sender=None, form=None, **kwargs):
    print repr(form.errors)

form_valid.connect(create_entry, dispatch_uid="create_entry_signal")

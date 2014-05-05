from django.core.management.base import BaseCommand, CommandError
from crowdataapp.models import CanonicalFieldEntryLabel, DocumentSetFormField, DocumentSet, DocumentSetFieldEntry
import csv

class Command(BaseCommand):
    #args is a csv file with old_canon_value, document_set_id, form_field_id, value_canon
    args = '<csv_file_path...>'
    help = 'Updates the canonical field entry labels with the content of a csv file.'

    def set_canonical_for_all(self):
      for entry in DocumentSetFieldEntry.objects.all():
        if DocumentSetFormField.objects.get(pk=entry.field_id).autocomplete:
          try:
            entry.canonical_label = entry.get_canonical_value()
            entry.save()
            print >>self.stdout,"%s: Original value %s and its canon %s" % (entry.id, entry.value, entry.canonical_label.value)
          except Exception, e:
            #raise CommandError("Failed getting canonical value for entry %s. Message: %s" % (entry.id, e))
            print "Failed getting canonical value for entry %s. Message: %s" % (entry.id, e)


    def handle(self, *args, **options):

       csv_file_path = args[0] if len(args) > 0 else None
       if csv_file_path is not None:
          self.import_canons(csv_file_path)

       self.set_canonical_for_all()

    def import_canons(self, csv_file_path):
         with open(csv_file_path, 'rb') as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='|')
            for row in reader:
              old_value = row[0]
              value = row[1]
              document_set_id = row[2]
              form_field_id = row[3]
              try:
                document_set = DocumentSet.objects.get(pk=int(document_set_id))
                form_field = DocumentSetFormField.objects.get(pk=int(form_field_id))

                canon = CanonicalFieldEntryLabel\
                        .objects.get(value=old_value,form_field=form_field, document_set=document_set)
                canon.value = value
                canon.save()

                print >>self.stdout,"Successfully updated canon %s" % value

              except CanonicalFieldEntryLabel.DoesNotExist:
                if not CanonicalFieldEntryLabel.objects.filter(value=value):
                  canon = CanonicalFieldEntryLabel(value=value, form_field=form_field, document_set=document_set)
                  canon.save()

                  print >>self.stdout,"Successfully created canon %s" % value
              except DocumentSet.DoesNotExist:
                raise CommandError('Document Set "%s" does not exist' % document_set_id)
              except DocumentSetFormField.DoesNotExist:
                raise CommandError('Form Field "%s" does not exist' % form_field_id)

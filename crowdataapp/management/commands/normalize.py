from django.core.management.base import BaseCommand, CommandError
from crowdataapp.models import CanonicalFieldEntryLabel, DocumentSetFormField, DocumentSet, DocumentSetFieldEntry
import csv

class Command(BaseCommand):
    # args is a csv file with (DocumentFieldEntry rows)
    # entry_id, field_id, value, verified, canonical_label_id, canon_value
    args = '<csv_file_path...>'
    help = 'Updates the field entries with the content of a csv file.'

    def handle(self, *args, **options):

       csv_file_path = args[0] if len(args) > 0 else None
       if csv_file_path is not None:
          self.update_entries(csv_file_path)

    def update_entries(self, csv_file_path):
         with open(csv_file_path, 'rb') as csv_file:
            reader = csv.reader(csv_file, delimiter=';',quotechar='|')
            for row in reader:
              entry_id = row[0]
              field_id = row[1]
              canonical_label_id = row[4]
              canonical_label_value = row[5]
              try:
                entry = DocumentSetFieldEntry.objects.get(pk=int(entry_id))
                if canonical_label_id == '':
                  # crear canonico y asociarlo
                  canon = CanonicalFieldEntryLabel(value  = canonical_label_value, document_set=entry.entry.document.document_set, form_field=DocumentSetFormField.objects.get(pk=field_id))
                  canon.save()
                  entry.canonical_label = canon
                  entry.save_without_setting_canon()
                else:
                  canon = CanonicalFieldEntryLabel.objects.get(pk=int(canonical_label_id))
                  canon.value = canonical_label_value
                  canon.save()
                  if entry.canonical_label_id != canonical_label_id:
                    # buscar canonico
                    entry.canonical_label = canon
                    entry.save_without_setting_canon()

                print >>self.stdout,"Successfully updated entry %s with canon value %s." % (entry_id, canonical_label_value)
              except DocumentSetFieldEntry.DoesNotExist:
                print >>self.stdout,"There is no entry with the id %s" % entry_id
              except CanonicalFieldEntryLabel.DoesNotExist:
                print >>self.stdout,"There is no canon with the id %s" % canonical_label_id

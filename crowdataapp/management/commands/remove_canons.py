from django.core.management.base import BaseCommand, CommandError
from crowdataapp.models import CanonicalFieldEntryLabel, DocumentSetFormField, DocumentSet, DocumentSetFieldEntry
import csv

class Command(BaseCommand):
    #args is a csv file with old_canon_value, document_set_id, form_field_id, value_canon
    args = '<csv_file_path...>'
    help = _('Removes the canonical field entry labels with the content of a csv file.')

    def handle(self, *args, **options):

       csv_file_path = args[0] if len(args) > 0 else None
       if csv_file_path is not None:
          self.remove_canons(csv_file_path)

    def remove_canons(self, csv_file_path):
         with open(csv_file_path, 'rb') as csv_file:
            reader = csv.reader(csv_file, delimiter=';', quotechar='|')
            for row in reader:
              canon_id = row[0]
              canon_value = row[1]
              new_canon_id = row[2]
              new_canon_value = row[3]
              try:
                if len(DocumentSetFieldEntry.objects.filter(canonical_label_id=int(canon_id))) > 0:
                  print >>self.stdout,"There are some entries with canon id %s and value %s." % (canon_id, canon_value)
                  new_canon = CanonicalFieldEntryLabel.objects.get(pk=new_canon_id)
                  for d in DocumentSetFieldEntry.objects.filter(canonical_label_id=int(canon_id)):
                    d.canonical_label = new_canon
                    d.save_without_setting_canon()
                    print >>self.stdout,"Entry %s with new canon %s." % (d.id, new_canon_id)
                CanonicalFieldEntryLabel.objects.get(pk=int(canon_id)).delete()
                print >>self.stdout,"Removed"
              except CanonicalFieldEntryLabel.DoesNotExist:
                print >>self.stdout,"Canon '%s' does not exist" % canon_id

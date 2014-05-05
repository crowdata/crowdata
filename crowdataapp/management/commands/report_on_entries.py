from django.core.management.base import BaseCommand, CommandError
from crowdataapp.models import Document
import re
import csv

class Command(BaseCommand):
  help = 'Report weird numbers on entries.'

  def handle(self, *args, **options):
    documents = Document.objects.filter(verified=True)

    with open('docs_with_several_verified_entries.csv', 'wb') as csvfile:
      impwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
      # report on documents validated more than once
      for doc in documents:
        form_entries = doc.form_entries.all()
        form_fields = doc.document_set.form.all()[0].fields.filter(verify=True)
        if len(form_entries) > 2:
          verified_entry_count = 0
          for fe in form_entries:
            fe_to_dict = fe.to_dict()
            #print "-------- For entry user %s." % fe_to_dict['username']
            if fe_to_dict['answer_Adjudicatario_verified'] or \
            fe_to_dict['answer_Tipo de gasto_verified'] or \
            fe_to_dict['answer_Importe total_verified']:
              verified_entry_count += 1
          if verified_entry_count > 1:
            print "The doc %s has more than one entry verified." % doc.id
            doc.unverify()
            doc.verify()
            impwriter.writerow([doc.id, doc.verified])

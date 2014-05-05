from django.core.management.base import BaseCommand, CommandError
from crowdataapp.models import Document
import re
import csv

class Command(BaseCommand):
  help = 'Report weird numbers on entries.'

  def handle(self, *args, **options):
    documents = Document.objects.all()#filter(verified=True)


    with open('importes_raros.csv', 'wb') as csvfile:
      impwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
      # report on documents validated more than once
      for doc in documents:
        form_entries = doc.form_entries.all()
        form_fields = doc.document_set.form.all()[0].fields.filter(verify=True)
        #print "######### For Doc %s" % doc.id
        if len(form_entries) > 2:
          #print "Size on entries: %s" % len(form_entries)
          verified_entry_count = 0
          importes = {}
          for fe in form_entries:
            fe_to_dict = fe.to_dict()
            #print "-------- For entry user %s." % fe_to_dict['username']
            if fe_to_dict['answer_Adjudicatario_verified'] and \
            fe_to_dict['answer_Tipo de gasto_verified'] and \
            fe_to_dict['answer_Importe total_verified']:
              verified_entry_count += 1
            importes[fe.id] = fe_to_dict['answer_Importe total']
          if verified_entry_count > 1:
            print "The doc %s has more than one entry verified." % doc.id

          # report on documents with numbers weird

          encontrado = False
          for val in importes.values():
            comparar_a = importes.values()
            comparar_a.remove(val)
            for i in comparar_a:
              if re.findall(val.split('.')[0], i) and (val <> i):
                encontrado = True
          if encontrado:
            impwriter.writerow([doc.id, importes])
            #print "Doc %s, Importes %s." % (doc.id, importes)

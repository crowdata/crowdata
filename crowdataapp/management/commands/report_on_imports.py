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

      for doc in documents:
        form_entries = doc.form_entries.all()
        form_fields = doc.document_set.form.all()[0].fields.filter(verify=True)
        importes = {}
        for fe in form_entries:
          fe_to_dict = fe.to_dict()
          importes[fe.id] = fe_to_dict['answer_Importe total']

        # report on documents with weird numbers
        encontrado = False
        for val in importes.values():
          comparar_a = importes.values()
          comparar_a.remove(val)
          for i in comparar_a:
            if re.findall(val.split('.')[0], i) and (val <> i):
              encontrado = True
        if encontrado:
          impwriter.writerow([doc.id, importes])

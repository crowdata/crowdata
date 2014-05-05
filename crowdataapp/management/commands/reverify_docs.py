from django.core.management.base import BaseCommand, CommandError
from crowdataapp.models import Document

class Command(BaseCommand):
  help = 'Reverify already verified documents.'

  def handle(self, *args, **options):
    documents = Document.objects.all() #filter(verified=True)
    for doc in documents:
      doc.unverify()
      if doc.is_revised_by_staff():
        doc.force_verify()
        print "------- Doc %s force verifid because staff." % doc.id
      else:
        print "BEFORE: Doc %s verification is %s" % (doc.id, doc.verified)
        doc.verify()
        print "AFTER: Doc %s verification is %s" % (doc.id, doc.verified)

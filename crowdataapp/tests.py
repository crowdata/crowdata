from django.test import TestCase
from crowdataapp.models import Document

class DocumentTest(TestCase):

  fixtures = ['prod.json']

  def setUp(self):
    self.not_verified = Document.objects.create(name='not verified document')

  def tearDown(self):
    self.not_verified.dispose()
    self.not_verified = None

  # VERIFICACIONES #############################

  # Caso 1 -------
  # tres usuarios diferentes en entradas
  # dos de esas entradas coinciden
  # no debe verificar

  # Caso 2 --------
  # tiene mas de 3 entradas para el mismo usuario
  # no tiene entradas de otros usuarios
  # no debe verificar

  # Caso 3 -------
  # tiene 3 entradas de 3 usuarios diferents que coinciden
  # si debe verificar

  # Caso 4 -----------
  # tiene una entrada  de usuario staff
  # si debe verificar

  # Caso 5 ---------
  # tiene una entrada de usuario superuser
  # si debe verificar

  # Caso 6 -------------
  # tiene un usuario con muchas entradas
  # tiene dos usuarios con entradas que coinciden a las del otro usuario
  # si debe verificar

  def test_verify(self):

    self.not_verified_doc.verify()

    # assert that the doc is verified
    self.assertTrue(self.not_verified.verified)
    # assert that only one entry is verified

  # DAR DOCUMENTO A TRANSCRIPT #########
  # ENVIO DE DOCUMENTO #################

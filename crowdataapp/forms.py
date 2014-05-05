from django import forms

from forms_builder.forms.forms import FormForForm

from crowdataapp import models

class DocumentSetFormForForm(FormForForm):
    field_entry_model = models.DocumentSetFieldEntry

    class Meta:
        model = models.DocumentSetFormEntry
        exclude = ("form", "entry_time")

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        exclude = ('user')

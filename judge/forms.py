from django import forms

from .models import PROGRAMMING_LANG_CHOICE, LANG_CHOICES


class ProblemForm(forms.Form):
    name = forms.CharField(max_length=200)
    language = forms.ChoiceField(choices=LANG_CHOICES)
    description = forms.CharField(widget=forms.Textarea)
    soluce_language = forms.ChoiceField(choices=PROGRAMMING_LANG_CHOICE)
    soluce_code = forms.CharField(widget=forms.Textarea)

from django import forms

from .models import ProblemDescription
from .models import PROGRAMMING_LANG_CHOICE, LANG_CHOICES


class ProblemForm(forms.Form):
    name = forms.CharField(max_length=200)
    language = forms.ChoiceField(choices=LANG_CHOICES)
    description = forms.CharField(widget=forms.Textarea)
    soluce_language = forms.ChoiceField(choices=PROGRAMMING_LANG_CHOICE)
    soluce_code = forms.CharField(widget=forms.Textarea)


class SubmissionForm(forms.Form):
    language = forms.ChoiceField(choices=PROGRAMMING_LANG_CHOICE)
    code = forms.CharField(widget=forms.Textarea, required=False)
    file = forms.FileField(allow_empty_file=True, required=False)

    def clean(self):
    	code = self.cleaned_data.get('code')
    	file = self.cleaned_data.get('file')
    	print(file)

    	if code and file:
    		raise forms.ValidationError("Choose between a text and a file to drop.")
    	if not code and not file:
    		raise forms.ValidationError("You need to drop a file or a text to submit.")


class DescriptionForm(forms.ModelForm):
    class Meta:
        model = ProblemDescription
        fields = ['name', 'content']

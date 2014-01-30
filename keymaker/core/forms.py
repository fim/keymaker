from django import forms
from django.forms.models import inlineformset_factory
from keymaker.core.models import CSR, PrivateKey, Certificate, Subject
import M2Crypto

class PrivateKeyForm(forms.ModelForm):
    class Meta:
        model = PrivateKey
        exclude = ['data']

class CSRForm(forms.ModelForm):
    class Meta:
        model = CSR
        exclude = ['data']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject

class CertificateForm(forms.ModelForm):
    ca = forms.ModelChoiceField(queryset=Certificate.objects.filter(is_ca=True),
            required=False)
    class Meta:
        model = Certificate
        exclude = ['data', 'subject']

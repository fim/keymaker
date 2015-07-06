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
        exclude = []

class CertificateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password", required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(), label="Password (again)", required=False)
    signing_ca = forms.ModelChoiceField(queryset=Certificate.objects.filter(is_ca=True),
            required=False, label="Signing CA")
    ca_password = forms.CharField(widget=forms.PasswordInput(), label="CA Password",
        required=False)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    class Meta:
        model = Certificate
        exclude = ['data', 'subject', 'serial']

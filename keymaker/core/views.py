from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView,ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404

from django.core.urlresolvers import reverse_lazy

from keymaker.core.models import Certificate, CSR, PrivateKey
from keymaker.core.forms import *

import M2Crypto

# PrivateKey
class PrivateKeyList(ListView):
    model = PrivateKey

class PrivateKeyCreate(CreateView):
    model = PrivateKey
    success_url = reverse_lazy('privatekey_list')

class PrivateKeyDelete(DeleteView):
    model = PrivateKey
    success_url = reverse_lazy('privatekey_list')

class PrivateKeyDetail(DetailView):
    model = PrivateKey

# CSR
class CSRList(ListView):
    model = CSR

class CSRCreate(CreateView):
    model = CSR
    success_url = reverse_lazy('csr_list')

class CSRDelete(DeleteView):
    model = CSR
    success_url = reverse_lazy('csr_list')

class CSRDetail(DetailView):
    model = CSR

# Certificate
class CertificateList(ListView):
    model = Certificate

class CertificateTreeList(ListView):
    model = Certificate

    def get_queryset(self):
        try:
            self.certificate = get_object_or_404(Certificate,
                pk=self.kwargs["pk"])
        except KeyError:
            # no arg
            return Certificate.objects.filter(is_ca=True,ca=None)

        return Certificate.objects.filter(ca=self.certificate)

class CertificateCreate(CreateView):
    model = Certificate
    form_class = CertificateForm
    success_url = reverse_lazy('certificate_list')

    def form_valid(self, form):
        context = self.get_context_data()
        certificatesubject_form = context['certificatesubject_form']
        if certificatesubject_form.is_valid():
            form.instance.subject = certificatesubject_form.save()
            self.object = form.save()
            return HttpResponseRedirect(reverse_lazy('certificate_list'))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(CertificateCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            context['certificatesubject_form'] = SubjectForm(self.request.POST)
        else:
            context['certificatesubject_form'] = SubjectForm()
        return context

class CertificateDelete(DeleteView):
    model = Certificate
    success_url = reverse_lazy('certificate_list')

class CertificateDetail(DetailView):
    model = Certificate

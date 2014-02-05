from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import TemplateView,ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from django.views.generic.base import View

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
        queryset = Certificate.objects.all()
        if "pk" in self.kwargs and self.kwargs["pk"]:
            self.certificate = get_object_or_404(Certificate,
                pk=self.kwargs["pk"])
        else:
            self.certificate = None

        return queryset.filter(signing_ca=self.certificate)

    def get_context_data(self, **kwargs):
        context = super(CertificateTreeList, self).get_context_data(**kwargs)
        context['certificate'] = self.certificate
        return context

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

            if 'pk' in self.kwargs and self.kwargs["pk"]:
                signing_ca = self.get_object()
                context['form'].fields['signing_ca'].initial = signing_ca
        return context

class CertificateDelete(DeleteView):
    model = Certificate
    success_url = reverse_lazy('certificate_list')

class CertificateDetail(DetailView):
    model = Certificate


###
# Generic Download View


class DownloadView(View):
    """
    Generic class view to abstract out the task of serving up files from within Django.
    Recommended usage is to combine it with SingleObjectMixin and extend certain methods based on your particular use case.

    Example usage::

        class Snippet(models.Model):
            name = models.CharField(max_length = 100)
            name = SlugField()
            code = models.TextField()

        from django.views.generic.detail import SingleObjectMixin

        class DownloadSnippetView(SingleObjectMixin, DownloadView):
            model = Snippet
            use_xsendfile = False
            mimetype = 'text/plain'

           def get_contents(self):
                return self.get_object().code

            def get_filename(self):
                return self.get_object().name + '.py'
    """
    mimetype = None
    extension = None
    filename = None
    use_xsendfile = True

    def get_filename(self):
        return self.filename

    def get_extension(self):
        return self.extension

    def get_mimetype(self):
        return self.mimetype

    def get_location(self):
        ''' Returns the path the file is currently located at. Used only if use_xsendfile is True '''
        pass

    def get_contents(self):
        ''' Returns the contents of the file download.  Used only if use_xsendfile is False '''
        pass

    def get(self, request, *args, **kwargs):
        response = HttpResponse(mimetype=self.get_mimetype())
        response['Content-Disposition'] = 'attachment; filename=' + self.get_filename()

        if self.use_xsendfile is True:
            response['X-Sendfile'] = self.get_location()
        else:
            response.write(self.get_contents())

        return response

class DownloadCRT(SingleObjectMixin, DownloadView):
    model = Certificate
    use_xsendfile = False
    mimetype = 'text/plain'
    def get_contents(self):
        return self.get_object().get_crt()

    def get_filename(self):
        return self.get_object().name+ '.crt'

class DownloadCRL(SingleObjectMixin, DownloadView):
    model = Certificate
    use_xsendfile = False
    mimetype = 'text/plain'
    def get_contents(self):
        return self.get_object().get_crt()

    def get_filename(self):
        return self.get_object().name + '.crl'

class DownloadKey(SingleObjectMixin, DownloadView):
    model = Certificate
    use_xsendfile = False
    mimetype = 'text/plain'
    def get_contents(self):
        return self.get_object().get_key()

    def get_filename(self):
        return self.get_object().name + '.key'

class DownloadPEM(SingleObjectMixin, DownloadView):
    model = Certificate
    use_xsendfile = False
    mimetype = 'text/plain'
    def get_contents(self):
        return self.get_object().get_pem()

    def get_filename(self):
        return self.get_object().name + '.pem'

class DownloadBundle(SingleObjectMixin, DownloadView):
    model = Certificate
    use_xsendfile = False
    mimetype = 'text/plain'
    def get_contents(self):
        return self.get_object().get_bundle()

    def get_filename(self):
        return self.get_object().name + '_bundle.pem'

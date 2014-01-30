from django.conf.urls import patterns, include, url

from keymaker.core import views

urlpatterns = patterns('',
    # Private keys
    url(r'^key$', views.PrivateKeyList.as_view(paginate_by=25), name='privatekey_list'),
    url(r'^key/new$', views.PrivateKeyCreate.as_view(), name='privatekey_new'),
    url(r'^key/delete/(?P<pk>\d+)$', views.PrivateKeyDelete.as_view(), name='privatekey_delete'),
    url(r'^key/(?P<pk>\d+)$', views.PrivateKeyDetail.as_view(), name='privatekey_detail'),
    # CSR
    url(r'^csr$', views.CSRList.as_view(paginate_by=25), name='csr_list'),
    url(r'^csr/new$', views.CSRCreate.as_view(), name='csr_new'),
    url(r'^csr/delete/(?P<pk>\d+)$', views.CSRDelete.as_view(), name='csr_delete'),
    url(r'^csr/(?P<pk>\d+)$', views.CSRDetail.as_view(), name='csr_detail'),
    # Certificates
    url(r'^certificate$', views.CertificateList.as_view(paginate_by=25), name='certificate_list'),
    url(r'^certificate/tree$',
        views.CertificateTreeList.as_view(paginate_by=25),
        name='certificate_treelist'),
    url(r'^certificate/tree/(?P<pk>\d+)$',
        views.CertificateTreeList.as_view(paginate_by=25),
        name='certificate_treelist_instance'),
    url(r'^certificate/new$', views.CertificateCreate.as_view(), name='certificate_new'),
    url(r'^certificate/(?P<pk>\d+)$', views.CertificateDetail.as_view(), name='certificate_detail'),
    url(r'^certificate/delete/(?P<pk>\d+)$', views.CertificateDelete.as_view(), name='certificate_delete'),
)

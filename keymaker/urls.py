from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/core/certificate/tree',
        permanent=False)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^core/', include('keymaker.core.urls')),
)

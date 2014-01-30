from django.contrib import admin
from keymaker.core.models import CSR, PrivateKey, Certificate, Subject

class CSRAdmin(admin.ModelAdmin):
    pass

class SubjectAdmin(admin.ModelAdmin):
    pass

class PrivateKeyAdmin(admin.ModelAdmin):
    pass

class CertificateAdmin(admin.ModelAdmin):
    pass

admin.site.register(CSR, CSRAdmin)
admin.site.register(PrivateKey, PrivateKeyAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Certificate, CertificateAdmin)

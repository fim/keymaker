from django.db import models
from django.forms.models import model_to_dict
import M2Crypto
import time

class PrivateKey(models.Model):
    data  = models.TextField(editable=False)
    name = models.CharField(max_length=32, blank=False, null=False)
    bits = models.IntegerField(default=2048)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.data:
                key = M2Crypto.RSA.gen_key(self.bits, 65537)
                self.data = key.as_pem(cipher=None)
        super(PrivateKey, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'{}'.format(self.name)

class Subject(models.Model):

    country = models.CharField(max_length=2, null=True, blank=True)
    state = models.CharField(max_length=256, null=True, blank=True)
    locality = models.CharField(max_length=256, null=True, blank=True)
    common_name = models.CharField(max_length=256, null=True, blank=True)
    email_address = models.CharField(max_length=256, null=True, blank=True)
    organization = models.CharField(max_length=256, null=True, blank=True)
    organizational_unit = models.CharField(max_length=256, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def as_str(self):
        TRD = {
                "country":  "C",
                "state":    "ST",
                "locality": "L",
                "common_name": "CN",
                "organization": "O",
                "organizational_unit": "OU",
                "email_address": "Email"
                # email (emailAddress) and its encoding (IA5String, but it's
                # considered deprecated in DNs (it should be in Subject
                # Alternative Name extension).
            }
        '/'.join(["{}={}".format(k,self.__getattribute__(k)) for k in
            model_to_dict(self).keys().remove('id')])

    def __unicode__(self):
        return u'{}'.format(self.name)

class CSR(models.Model):
    data = models.TextField(editable=False)
    name = models.CharField(max_length=32, blank=False, null=False)
    key = models.ForeignKey(PrivateKey, related_name="csr", null=True,
        editable=False, blank=False)
    subject = models.ForeignKey(Subject, null=False, blank=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.key:
                p = PrivateKey()
                p.save()
                self.key = p

            pk = M2Crypto.EVP.PKey()
            x = M2Crypto.X509.Request()
            rsa = M2Crypto.RSA.load_key_string(str(self.key.data))
            pk.assign_rsa(rsa)
            x.set_pubkey(pk)
            name = x.get_subject()
            if self.subject.country: name.C = self.subject.country
            if self.subject.common_name: name.CN = self.subject.common_name
            if self.subject.state: name.ST = self.subject.state
            if self.subject.organization: name.O = self.subject.organization
            if self.subject.organizational_unit: name.OU = self.subject.organizational_unit
            if self.subject.email_address: name.Email = self.subject.email_address
            x.sign(pk,'sha1')
            self.data = x.as_pem()

        super(CSR, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'{}'.format(self.name)


class Certificate(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)

    data = models.TextField(editable=False)
    key = models.ForeignKey(PrivateKey, related_name="crt", editable=False, null=False, blank=False)
    csr = models.ForeignKey(CSR, related_name="crt", editable=False, null=True, blank=False)
    ca = models.ForeignKey('self', related_name="crt", null=True, blank=True)
    is_ca = models.BooleanField(default=False)
    subject = models.ForeignKey(Subject, editable=False, null=False, blank=False)
    validity_period = models.IntegerField(null=False, blank=False,
            default=3650)
    not_before = models.DateTimeField(editable=False)
    not_after = models.DateTimeField(editable=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.csr:
                c = CSR()
                c.subject = self.subject
                c.save()
                self.csr = c
                self.key = c.key

            cert = M2Crypto.X509.X509()
            cert.set_serial_number(2)
            cert.set_version(2)
            valid_from = long(time.time())
            ASN1 = M2Crypto.ASN1.ASN1_UTCTIME()
            ASN1.set_time(valid_from)
            cert.set_not_before(ASN1)
            self.not_before = ASN1.get_datetime()
            ASN1.set_time(valid_from + self.validity_period * 24 * 60 * 60)
            cert.set_not_after(ASN1)
            self.not_after = ASN1.get_datetime()

            csr = M2Crypto.X509.load_request_string(str(self.csr.data))
            if self.ca:
                print "Using ca to sign"
                ca = M2Crypto.X509.load_cert_string(str(self.ca.data))
                pk = M2Crypto.EVP.load_key_string(str(self.ca.key.data))
            else:
                print "self signing"
                ca = None
                pk = M2Crypto.EVP.load_key_string(str(self.csr.key.data))

            cert.set_subject(csr.get_subject())
            if ca:
                cert.set_issuer(ca.get_issuer())
            else:
                cert.set_issuer(csr.get_subject())
            cert.set_pubkey(csr.get_pubkey())

            if self.is_ca:
                cert.add_ext(M2Crypto.X509.new_extension('basicConstraints', 'CA:TRUE'))
                cert.add_ext(M2Crypto.X509.new_extension('subjectKeyIdentifier', cert.get_fingerprint()))
            cert.sign(pk,'sha1')

            self.data = cert.as_pem()

        super(Certificate, self).save(*args, **kwargs)


        def get_crt(self):
            return self.data

        def get_key(self):
            return self.key.data or ""

        def get_pem(self):
            return "{}{}".format(self.get_key(), self.get_crt())


    def __unicode__(self):
        return u'{}'.format(self.name)

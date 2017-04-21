import threading

from urlparse import urlparse
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.utils.encoding import python_2_unicode_compatible
from django.db.models import Model

from cms.models import CMSPlugin
from adminsortable.models import SortableMixin
from jsonfield import JSONField
from cmsplugin_remote_form import utils


localdata = threading.local()
localdata.TEMPLATE_CHOICES = utils.autodiscover_templates()
TEMPLATE_CHOICES = localdata.TEMPLATE_CHOICES


@python_2_unicode_compatible
class RemoteForm(CMSPlugin):
    post_url = models.CharField(_('Remote URL'), null=True, blank=False, max_length=200,
                                default='#remoteURL')
    submit_button_text = models.CharField(_('Text for the Submit button.'),
                                          blank=True,
                                          max_length=30)
    thanks = models.TextField(_('Message displayed after submitting the contact form.'))
    thanks_in_modal = models.BooleanField(_('Show Thanks In Modal'), default=True)
    collect_records = models.BooleanField(_('Collect Records'),
                                          default=True,
                                          help_text=_(
                                              "If active, all records for this Form will be stored in the Database."))
    template = models.CharField(
        max_length=255,
        choices=TEMPLATE_CHOICES,
        default='cmsplugin_remote_form/default.html',
        editable=True)
    field_class = models.CharField(_('CSS class to put on the field.'), blank=True, max_length=50)
    label_class = models.CharField(_('CSS class to put on the label.'), blank=True, max_length=50)

    class Meta:
        verbose_name = "Remote Form"
        verbose_name_plural = "Remote Forms"

    def copy_relations(self, oldinstance):
        for extrafield in ExtraField.objects.filter(form__pk=oldinstance.pk):
            extrafield.pk = None
            extrafield.save()
            self.extrafield_set.add(
                extrafield)

    def __str__(self):
        if self.post_url:
            url_obj = urlparse(self.post_url)
            return "Remote Form: %s - %s" % (url_obj.netloc, url_obj.path)
        return _("Remote Form")


def recaptcha_installed():
    return ('captcha' in settings.INSTALLED_APPS and
            all([hasattr(settings, s)
                for s in ['RECAPTCHA_PUBLIC_KEY', 'RECAPTCHA_PRIVATE_KEY']]))

FIELD_TYPE = (('CharField', 'CharField'),
              ('BooleanField', 'BooleanField'),
              ('EmailField', 'EmailField'),
              ('DecimalField', 'DecimalField'),
              ('FloatField', 'FloatField'),
              ('IntegerField', 'IntegerField'),
              ('FileField', 'FileField'),
              ('ImageField', 'ImageField'),
              ('USStateSelect', 'US State Selector'),
              ('IPAddressField', 'IPAddressField'),
              ('MathCaptcha', 'Math Captcha'),
              ('auto_Textarea', _('CharField as Textarea')),
              ('auto_hidden_input', _('CharField as HiddenInput')),
              ('auto_referral_page', _('Referral page as HiddenInput')),
              ('auto_GET_parameter', _('GET parameter as HiddenInput')),
              ('CharFieldWithValidator', 'CharFieldWithValidator'),)
if recaptcha_installed():
    FIELD_TYPE += (('ReCaptcha', 'reCAPTCHA'),)


@python_2_unicode_compatible
class ExtraField(SortableMixin):
    """
    """
    form = models.ForeignKey(RemoteForm, verbose_name=_("Contact Form"))
    label = models.CharField(_('Label'), max_length=100, null=True, blank=True)
    name = models.CharField(_('Name'), max_length=100, default='')
    fieldType = models.CharField(max_length=100, choices=FIELD_TYPE)
    initial = models.CharField(max_length=250, blank=True, null=True)
    placeholder = models.CharField(
        _('Placeholder'), max_length=250, blank=True, null=True)
    required = models.BooleanField(
        _('Required'), default=True)
    widget = models.CharField(
        _('Widget'), max_length=250, blank=True, null=True,
        help_text=_("Will be ignored in the current version."))
    css_class = models.CharField(max_length=250, blank=True, null=True)

    inline_ordering_position = models.IntegerField(blank=True, null=True, editable=True)

    def __str__(self):
        return self.label

    class Meta:
        ordering = ('inline_ordering_position',)


@python_2_unicode_compatible
class ContactRecord(Model):
    """
    """
    contact_form = models.ForeignKey(RemoteForm, verbose_name=_("Contact Form"), null=True, on_delete=models.SET_NULL)
    date_of_entry = models.DateTimeField(auto_now_add=True)
    date_processed = models.DateTimeField(null=True, blank=True, help_text=_("Date the Record was processed."))
    data = JSONField(null=True, blank=True, default={})

    class Meta:
        ordering = ['date_of_entry', 'contact_form', ]
        verbose_name = _("Contact Record")
        verbose_name_plural = _("Contact Records")

    @property
    def is_processed(self):
        if self.date_processed:
            return True
        else:
            return False

    def __str__(self):
        return _(u"Record for %(contact)s recorded on %(date)s") % {'contact': self.contact_form,
                                                                    'date': self.date_of_entry.strftime('%d. %b %Y')}

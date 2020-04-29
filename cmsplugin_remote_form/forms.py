from captcha.fields import ReCaptchaField
from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from localflavor.us.forms import USStateSelect
from simplemathcaptcha.fields import MathCaptchaField

from cmsplugin_remote_form.models import ContactRecord, RemoteForm as RemoteFormModel
from cmsplugin_remote_form.utils import get_validators


class RemoteForm(forms.Form):
    required_css_class = getattr(settings, "REMOTE_FORM_REQUIRED_CSS_CLASS", "required")

    def make_select2(self, extraField):
        attrs = self.fields[extraField.name].widget.attrs
        classes = attrs.get('class')
        if classes and 'select2' not in classes.split(' '):
            attrs['class'] += ' ' + 'select2'
        elif not classes:
            attrs['class'] = 'select2'

    def extra_field_factory(self, extraField, formsFieldClass, **kwargs):
        field_kwargs = {
            "label": extraField.label,
            "required": extraField.required,
            "initial": extraField.initial,
        }
        field_kwargs.update(kwargs)

        field_class_instance = formsFieldClass(**field_kwargs)
        field_class_instance.object = extraField

        self.fields[extraField.name] = field_class_instance

    def __init__(self, contactFormInstance, request, *args, **kwargs):
        super(RemoteForm, self).__init__(*args, **kwargs)
        self.object = contactFormInstance
        if "instance" not in kwargs:
            for extraField in contactFormInstance.extrafield_set.all():
                if extraField.fieldType == "CharField":
                    self.extra_field_factory(extraField, forms.CharField)
                elif extraField.fieldType == "BooleanField":
                    self.extra_field_factory(extraField, forms.BooleanField)
                elif extraField.fieldType == "EmailField":
                    self.extra_field_factory(extraField, forms.EmailField)
                elif extraField.fieldType == "DecimalField":
                    self.extra_field_factory(extraField, forms.DecimalField)
                elif extraField.fieldType == "FloatField":
                    self.extra_field_factory(extraField, forms.FloatField)
                elif extraField.fieldType == "FileField":
                    self.extra_field_factory(extraField, forms.FileField)
                elif extraField.fieldType == "ImageField":
                    self.extra_field_factory(extraField, forms.ImageField)
                elif extraField.fieldType == "IntegerField":
                    self.extra_field_factory(extraField, forms.IntegerField)
                elif extraField.fieldType == "USStateSelect":
                    self.extra_field_factory(
                        extraField, forms.CharField, widget=USStateSelect
                    )
                elif extraField.fieldType == "IPAddressField":
                    self.extra_field_factory(extraField, forms.IPAddressField)
                elif extraField.fieldType == "auto_Textarea":
                    self.extra_field_factory(
                        extraField, forms.CharField, widget=forms.Textarea
                    )
                elif extraField.fieldType == "auto_hidden_input":
                    self.extra_field_factory(
                        extraField,
                        forms.CharField,
                        widget=forms.HiddenInput,
                        required=False,
                    )
                elif extraField.fieldType == "auto_referral_page":
                    lInitial = _("No referral available.")
                    if request:
                        lInitial = request.META.get(
                            "HTTP_REFERER", _("No referral available.")
                        )
                    self.extra_field_factory(
                        extraField,
                        forms.CharField,
                        initial=lInitial,  # NOTE: This overwrites extraField.initial!
                        widget=forms.HiddenInput,
                        required=False,
                    )
                elif extraField.fieldType == "MathCaptcha":
                    self.extra_field_factory(
                        extraField, MathCaptchaField, required=True
                    )
                elif extraField.fieldType == "ReCaptcha":
                    self.extra_field_factory(
                        extraField, ReCaptchaField, label="", required=True
                    )
                elif extraField.fieldType == "auto_GET_parameter":
                    lInitial = _("Key/value parameter not available.")
                    if request:
                        lInitial = request.GET.get(extraField.name, "n/a")
                    self.extra_field_factory(
                        extraField,
                        forms.CharField,
                        initial=lInitial,
                        widget=forms.HiddenInput,
                        required=False,
                    )
                elif extraField.fieldType == "CharFieldWithValidator":
                    self.extra_field_factory(
                        extraField, forms.CharField, validators=get_validators()
                    )
                elif extraField.fieldType == "ChoiceField":
                    self.extra_field_factory(
                        extraField,
                        forms.ChoiceField,
                        choices=[
                            (c.strip(), c.strip()) for c in extraField.initial.split(",")
                        ],
                    )
                    self.make_select2(extraField)

    def save_record(self, instance, ts):
        if instance.collect_records:
            current_site = Site.objects.get_current()
            order = RemoteFormModel.objects.get(id=instance.id).extrafield_set.order_by(
                "inline_ordering_position"
            )
            excluded_field_types = ["MathCaptcha", "ReCaptcha"]
            order = [
                field for field in order if field.fieldType not in excluded_field_types
            ]
            ordered_dic_list = []
            for field in order:
                key = field.name
                value = self.cleaned_data.get(key, "(no input)")
                # redefine value for files...
                if field.fieldType in ["FileField", "ImageField"]:
                    val = ts + "-" + str(value)
                    if settings.MEDIA_URL.startswith("http"):
                        value = "%s%s" % (settings.MEDIA_URL, val)
                    else:
                        value = "http://%s%s%s" % (
                            current_site,
                            settings.MEDIA_URL,
                            val,
                        )
                ordered_dic_list.append({field.label: value})

            record = ContactRecord(contact_form=instance, data=ordered_dic_list)
            record.save()
            return record
        return False

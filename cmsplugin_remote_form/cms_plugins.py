import requests, json

from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
try:
    from django.urls import reverse
except ImportError:
    # handle Django < 1.10
    from django.core.urlresolvers import reverse
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .admin import ExtraFieldInline
from .models import RemoteForm as RemoteFormModel
from .forms import RemoteForm as RemoteFormForm


import time


def handle_uploaded_file(f, ts):
    destination = open('%s/%s' % (settings.MEDIA_ROOT, ts + '-' + f.name), 'wb+')

    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    
    
class CMSRemoteFormPlugin(CMSPluginBase):
    """ 
    """
    model = RemoteFormModel
    inlines = [ExtraFieldInline, ]
    name = _('Remote Form')
    render_template = "cmsplugin_remote_form/default.html"
    change_form_template = 'cmsplugin_remote_form/admin/change_form.html'
    cache = False

    def render(self, context, instance, placeholder):
        request = context['request']
        form = RemoteFormForm(contactFormInstance=instance, request=request)
        show_thanks = False

        if instance and instance.template:
            self.render_template = instance.template

        if request.method == "POST" and "remote_form_" + str(instance.id) in request.POST.keys():
            ts = str(int(time.time()))
            self.submitted_form = RemoteFormForm(contactFormInstance=instance,
                                  request=request,
                                  data=request.POST,
                                  files=request.FILES)

            if self.submitted_form.is_valid():
                for fl in request.FILES:
                    for f in request.FILES.getlist(fl):
                        handle_uploaded_file(f, ts)
                show_thanks = True
                self.instance = instance
                self.request = request
                self.saved_record = self.submitted_form.save_record(instance, ts)
                self.notification_emails()
                self.remote_response = self.post_to_remote(instance, request, self.submitted_form.cleaned_data)
                self.handle_response()
            else:
                form = self.submitted_form
        context.update({
            'object': instance,
            'form': form,
            'show_thanks': show_thanks
        })
        return context

    def handle_response(self):
        if self.remote_response and self.determine_success():
            self.success_callback()
        else:
            self.error_notifications_emails()
            self.failure_callback()

    # Override these if you need to do different stuff.
    def post_to_remote(self, instance, request, cleaned_data):
        try:
            response = requests.post(instance.post_url, data=cleaned_data)
            return response
        except requests.ConnectionError, e:
            print e

    def determine_success(self):
        return "Please correct the following errors:" not in self.remote_response.content

    def success_callback(self):
        pass

    def failure_callback(self):
        pass

    def error_notifications_emails(self):
        if self.instance.error_notification_emails:
            error = self.remote_response.content if self.remote_response else "Connection Error"
            error_email_addresses = [x.strip() for x in self.instance.error_notification_emails.split(',')]
            message = EmailMultiAlternatives(
                "Form Submission Error",
                'There was a problem with a form-submission on:\n%s\nView the record:\n%s\nContent:\n%s' % (
                    self.request.build_absolute_uri(),
                    self.request.build_absolute_uri(
                        reverse('admin:cmsplugin_remote_form_contactrecord_change', args=(self.saved_record.id,))),
                    error
                ),
                'no-reply@worthwhile.com',
                error_email_addresses,
            )
            message.send()

    def notification_emails(self):
        if self.instance.notification_emails:
            email_addresses = [x.strip() for x in self.instance.notification_emails.split(',')]
            data = self.saved_record.data
            data_dict = {k: v for d in data for k, v in d.items()}
            content = ', '.join("%s=%r" % (key, val) for (key, val) in data_dict.items())

            message = EmailMultiAlternatives(
                "Form Submission",
                content,
                'no-reply@worthwhile.com',
                email_addresses,
            )
            message.send()


plugin_pool.register_plugin(CMSRemoteFormPlugin)

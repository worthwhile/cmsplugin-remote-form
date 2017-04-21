from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
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
            submitted_form = RemoteFormForm(contactFormInstance=instance,
                                  request=request,
                                  data=request.POST,
                                  files=request.FILES)

            if submitted_form.is_valid():
                for fl in request.FILES:
                    for f in request.FILES.getlist(fl):
                        handle_uploaded_file(f, ts)
                show_thanks = True
                submitted_form.save_record(instance, ts)
                response = submitted_form.post_to_remote(instance, request)
                self.handle_response(request, instance, response)
            else:
                form = submitted_form
        context.update({
            'object': instance,
            'form': form,
            'show_thanks': show_thanks
        })
        return context

    def handle_response(self, request, instance, response):
        if "success=false" in response.url:
            if instance.error_notification_emails:
                error_email_addresses = instance.error_notification_emails.split(',').strip()
                message = EmailMultiAlternatives(
                    "Form Submission Error",
                    'There was a problem with a form-submission on %s' % request.build_absolute_uri(),
                    'no-reply@worthwhile.com',
                    error_email_addresses,
                )
                message.send()
            self.failure_callback(instance, response)
        if "success=true" in response.url:
            self.success_callback(instance, response)

    # Override these if you need to do extra stuff.
    def success_callback(self, instance, response):
        pass

    def failure_callback(self, instance, response):
        pass


plugin_pool.register_plugin(CMSRemoteFormPlugin)

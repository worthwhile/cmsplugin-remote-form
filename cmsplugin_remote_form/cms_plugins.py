from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .admin import ExtraFieldInline
from .models import RemoteForm
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
    model = RemoteForm
    inlines = [ExtraFieldInline, ]
    name = _('Remote Form')
    render_template = "cmsplugin_remote_form/default.html"
    change_form_template = 'cmsplugin_remote_form/change_form.html'
    cache = False

    def render(self, context, instance, placeholder):
        request = context['request']

        if instance and instance.template:
            self.render_template = instance.template

        if request.method == "POST" and "remote_form_" + str(instance.id) in request.POST.keys():
            form = RemoteFormForm(contactFormInstance=instance,
                                  request=request,
                                  data=request.POST,
                                  files=request.FILES)
            if form.is_valid():
                ts = str(int(time.time()))

                for fl in request.FILES:
                    for f in request.FILES.getlist(fl):
                        handle_uploaded_file(f, ts)

                form.send(instance.recipient_email, request, ts, instance, form.is_multipart)
                context.update({
                    'contact': instance,
                })
                return context
            else:
                context.update({
                    'contact': instance,
                    'form': form,
                })

        else:
            form = RemoteFormForm(contactFormInstance=instance, request=request)
            context.update({
                    'contact': instance,
                    'form': form,
            })
        return context


plugin_pool.register_plugin(CMSRemoteFormPlugin)

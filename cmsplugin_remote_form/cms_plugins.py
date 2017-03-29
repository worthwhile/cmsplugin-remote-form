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
    change_form_template = 'cmsplugin_remote_form/change_form.html'
    cache = False

    def render(self, context, instance, placeholder):
        request = context['request']
        form = RemoteFormForm(contactFormInstance=instance, request=request)
        show_thanks = False

        if instance and instance.template:
            self.render_template = instance.template

        if request.method == "POST" and "remote_form_" + str(instance.id) in request.POST.keys():
            submission_form = RemoteFormForm(contactFormInstance=instance,
                                  request=request,
                                  data=request.POST,
                                  files=request.FILES)

            if submission_form.is_valid():
                ts = str(int(time.time()))
                show_thanks = True
                form.save_record(instance, ts)

                for fl in request.FILES:
                    for f in request.FILES.getlist(fl):
                        handle_uploaded_file(f, ts)

            else:
                form = submission_form

        context.update({
            'contact': instance,
            'form': form,
            'show_thanks': show_thanks
        })
        return context


plugin_pool.register_plugin(CMSRemoteFormPlugin)

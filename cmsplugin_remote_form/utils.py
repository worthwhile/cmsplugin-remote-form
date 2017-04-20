import glob
import os
import threading
import importlib

from django.conf import settings

localdata = threading.local()
localdata.TEMPLATES = tuple()
TEMPLATES = localdata.TEMPLATES


def autodiscover_templates():
    '''
    Autodiscovers cmsplugin_remote_form templates the way
    'django.template.loaders.filesystem.Loader' and
    'django.template.loaders.app_directories.Loader' work.
    '''
    def sorted_templates(templates):
        '''
        Sorts templates
        '''
        TEMPLATES = sorted(templates, key=lambda template: template[1])
        return TEMPLATES

    # obviously, cache for better performance
    global TEMPLATES
    if TEMPLATES:
        return TEMPLATES

    # override templates from settings
    override_dir = getattr(settings, 'CMSPLUGIN_REMOTE_FORM_TEMPLATES', None)
    if override_dir:
        return sorted_templates(override_dir)

    templates = []

    dirs_to_scan = [item for t in settings.TEMPLATES for item in t['DIRS']]
    dirs_to_scan.append(os.path.join(os.path.dirname(__file__), 'templates/layout'))

    for dir in dirs_to_scan:
        found = glob.glob(os.path.join(dir, 'cmsplugin_remote_form/*.html'))
        for file in found:
            dir, file = os.path.split(file)
            key, value = os.path.join(dir.split('/')[-1], file), file
            f = False
            for _, template in templates:
                if template == file:
                    f = True
            if not f:
                templates.append((key, value,))
            # print os.path.basename(file)

    return sorted_templates(templates)


def get_validators():
    val = []
    # See if validators have been defined
    if hasattr(settings, 'CMSPLUGIN_CONTACT_FORM_VALIDATORS'):
        validators = getattr(settings,
                             'CMSPLUGIN_CONTACT_FORM_VALIDATORS')
        for validator in validators:
            try:
                f = getattr(importlib.import_module(validator[0]),
                            validator[1])
                val.append(f)
            except ImportError:
                raise ImportError(
                    "Cannot import {} from module {}.".format(
                        validator[1], validator[0]))
    return val

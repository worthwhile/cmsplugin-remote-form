# -*- coding: utf-8 -*-
from django.apps import AppConfig


class RemoteFormConfig(AppConfig):
    name = 'cmsplugin_remote_form'
    verbose_name = 'CMSPlugin Remote Form'

    def ready(self):
        from cmsplugin_remote_form.checks import register_checks
        register_checks()

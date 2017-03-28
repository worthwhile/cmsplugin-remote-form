# -*- coding: utf-8 -*-
from django.core.checks import Warning, register


def register_checks():
    for check in [
        # warn_1_3_changes,  # Might be more annoying than useful
    ]:
        register(check)

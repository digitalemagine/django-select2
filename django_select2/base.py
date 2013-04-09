# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

__RENDER_SELECT2_STATICS = False
__ENABLE_MULTI_PROCESS_SUPPORT = False
__MEMCACHE_HOST = None
__MEMCACHE_PORT = None
__MEMCACHE_TTL = 900
__GENERATE_RANDOM_ID = False
__SECRET_SALT = ''

try:
    from django.conf import settings
    if settings.configured:
        __RENDER_SELECT2_STATICS = getattr(settings, 'AUTO_RENDER_SELECT2_STATICS', True)
        __ENABLE_MULTI_PROCESS_SUPPORT = getattr(settings, 'ENABLE_SELECT2_MULTI_PROCESS_SUPPORT', False)
        __MEMCACHE_HOST = getattr(settings, 'SELECT2_MEMCACHE_HOST', None)
        __MEMCACHE_PORT = getattr(settings, 'SELECT2_MEMCACHE_PORT', None)
        __MEMCACHE_TTL = getattr(settings, 'SELECT2_MEMCACHE_TTL', 900)
        __GENERATE_RANDOM_ID = getattr(settings, 'GENERATE_RANDOM_SELECT2_ID', False)
        __SECRET_SALT = getattr(settings, 'SECRET_KEY', '')

        if not __GENERATE_RANDOM_ID and __ENABLE_MULTI_PROCESS_SUPPORT:
            logger.warn("You need not turn on ENABLE_SELECT2_MULTI_PROCESS_SUPPORT when GENERATE_RANDOM_SELECT2_ID is disabled.")
            __ENABLE_MULTI_PROCESS_SUPPORT = False

        from django_select2.widgets import Select2Widget, Select2MultipleWidget, HeavySelect2Widget, HeavySelect2MultipleWidget, \
            AutoHeavySelect2Widget, AutoHeavySelect2MultipleWidget
        from django_select2.fields import Select2ChoiceField, Select2MultipleChoiceField, HeavySelect2ChoiceField, \
            HeavySelect2MultipleChoiceField, HeavyModelSelect2ChoiceField, HeavyModelSelect2MultipleChoiceField, \
            ModelSelect2Field, ModelSelect2MultipleField, AutoSelect2Field, AutoSelect2MultipleField, \
            AutoModelSelect2Field, AutoModelSelect2MultipleField
        from django_select2.views import Select2View, NO_ERR_RESP
except ImportError as e:
    logger.info("Could not correctly setup django-select2: {}".format(e))


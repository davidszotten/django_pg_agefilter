import os
import sys

import django
from django.core.management import call_command


os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'


if __name__ == '__main__':
    args = sys.argv[1:]
    try:
        setup = django.setup
    except AttributeError:
        pass  # django < 1.7
    else:
        setup()
    call_command('test', *args)

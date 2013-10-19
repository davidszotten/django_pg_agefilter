import os
import sys

from django.core.management import call_command


os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'


if __name__ == '__main__':
    args = sys.argv[1:]
    call_command('test', *args)

from fabric.api import *
import os


def run_django_command(command):
    local('python manage.py {0}'.format(command))


def test():
    os.environ["TEST_RUNNING"] = 'True'
    run_django_command('test')

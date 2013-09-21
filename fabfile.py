from fabric.api import *
import os


def run_django_command(command):
    local('python manage.py {0}'.format(command))


@task
def test():
    os.environ["TEST_RUNNING"] = 'True'
    run_django_command('test -v 2')


@task
def test_jenkins():
    os.environ["TEST_RUNNING"] = 'True'
    run_django_command('jenkins -v 2 --traceback')
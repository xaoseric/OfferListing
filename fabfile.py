from fabric.api import *
import os


def run_django_command(command):
    local('python manage.py {0}'.format(command))


def set_test_environment():
    os.environ["TEST_RUNNING"] = 'True'


@task
def test():
    set_test_environment()
    run_django_command('test -v 2')


@task
def test_jenkins():
    set_test_environment()
    run_django_command('jenkins -v 2 --traceback')


@task
def coverage():
    set_test_environment()
    local('coverage run manage.py test -v 2 && coverage html')

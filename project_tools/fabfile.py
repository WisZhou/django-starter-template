from fabric.api import (
    local,
)


def runserver(port=7070):
    '''
    start dev django server
    '''
    local(
        'docker-compose run --rm -p {port}:{port} web '
        'python manage.py runserver 0.0.0.0:{port}'.format(port=port)
    )


def manage(cmd):
    '''
    run django manage command
    '''
    local('docker-compose run --rm web python manage.py {cmd}'.format(cmd=cmd))


def makemigrations(merge=None):
    '''
    database migrate
    '''
    cmd = 'makemigrations' if merge is None else 'makemigrations --merge'
    manage(cmd)


def migrate(version=None):
    '''
    database migrate
    '''
    migrate_cmd = 'migrate hitravel {0}'.format(version) if version \
        else 'migrate'
    manage(migrate_cmd)


def shell():
    '''
    shell
    '''
    manage('shell')


def create_app(name):
    '''
    create django app
    '''
    local(
        'docker-compose run --rm web django-admin.py '
        'startapp {name}'.format(name=name)
    )


def clean():
    '''
    clean pyc
    '''
    local("find . -name '*.pyc' -type f -print -exec rm -rf {} \;")

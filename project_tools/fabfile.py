# coding: utf-8

import os
import datetime

from fabric.api import (
    local,
    cd,
    lcd,
    run,
    env,
    task,
    execute,
    shell_env,
)

PROD_MYSQL_HOST = ''
GIT_REGISTRY = ''

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEPLOY_DIR = os.path.join(BASE_DIR, 'tmp/deploy')
DEPLOY_PROJECT_DIR = os.path.join(DEPLOY_DIR, '{project}')

# Examples:
# 发布测试环境
# > fab -R test deploy_test
#
# 发布到前台
# > fab -R front1,front2 deploy_front_prod
#
# 发布后台
# > fab -R backend deploy_backend_prod

env.user = 'ubuntu'

env.roledefs = {
    'backend': [''],   # 后台
    'front1': [''],    # 前台1
    'front2': [''],    # 前台2
    'test': [''],  # 测试环境
}


@task
def runserver(port=8070):
    '''
    start dev django server
    '''
    local(
        'docker-compose run --rm -p {port}:{port} web '
        'python manage.py runserver 0.0.0.0:{port}'.format(port=port)
    )


@task
def manage(cmd):
    '''
    run django manage command
    '''
    local('docker-compose run --rm web python manage.py {cmd}'.format(cmd=cmd))


@task
def makemigrations(merge=None):
    '''
    database migrate
    '''
    cmd = 'makemigrations' if merge is None else 'makemigrations --merge'
    manage(cmd)


@task
def migrate(version=None):
    '''
    database migrate
    '''
    backup()
    migrate_cmd = 'migrate {project} {0}'.format(version) if version else 'migrate'
    manage(migrate_cmd)


@task
def shell():
    '''
    shell
    '''
    manage('shell')


@task
def create_app(name):
    '''
    create django app
    '''
    local(
        'docker-compose run --rm web django-admin.py '
        'startapp {name}'.format(name=name)
    )


@task
def clean():
    '''
    clean pyc
    '''
    local("find . -name '*.pyc' -type f -print -exec rm -rf {} \;")


@task
def create_db(db='{project}'):
    '''
    create db if db not exists
    '''
    local(
        'docker exec -it product_mysql mysql -uroot -proot -e '
        '"CREATE DATABASE IF NOT EXISTS {db};"'.format(db=db)
    )


@task
def drop_db(db='{project}'):
    '''
    drop db
    '''
    local(
        'docker exec -it product_mysql mysql -uroot -proot -e '
        '"DROP DATABASE {db};"'.format(db=db)
    )


@task
def backup():
    '''
    备份数据库
    '''
    if not os.path.exists('./backup'):
        os.mkdir('./backup')

    now = datetime.datetime.now().strftime('%Y%m%d%H%M')
    local(
        """
        docker exec product_mysql sh -c 'mysqldump -uroot -proot {project}' \
        > ./backup/data_{0}.sql; \
        cp ./backup/data_{0}.sql ./backup/data.sql
        """.format(now)
    )


@task
def celery():
    """
    run celery
    """
    local(
        'docker-compose run --rm web '
        'celery -A {project} worker -l info'
    )


@task
def beat():
    """
    run beat
    """
    local(
        'docker-compose run --rm web '
        'celery -A {project} beat -l info'
    )


def deploy_code(docker, path='/data/opt/{project}'):
    with cd(path):
        run('git checkout -- .')
        run('git pull --rebase')
        run('docker-compose run --rm %s python manage.py migrate' % docker)
        run('docker-compose run --rm %s python manage.py collectstatic --noinput' % docker)
        run('touch deploy/uwsgi.ini')


def deploy(docker, branch='master', path='/data/opt/{project}'):
    with cd(path):
        run('docker-compose pull %s' % docker)
        run('docker-compose run --rm %s python manage.py collectstatic --noinput' % docker)
        run('docker-compose run --rm %s python manage.py migrate' % docker)
        run('docker-compose stop %s' % docker)
        run('docker-compose rm -f %s' % docker)
        run('docker-compose up -d %s' % docker)


def deploy_celery(docker='celery', path='/data/opt/{project}'):
    with cd(path):
        run('docker-compose pull web')
        run('docker-compose stop %s' % docker)
        run('docker-compose rm -f %s' % docker)
        run('docker-compose up -d %s' % docker)


def backup_mysql(db='{project}'):
    now = datetime.datetime.now().strftime('%Y%m%d%H%M')
    with cd('/data/dev-docker-services'):
        run(
            """
            docker exec product_mysql sh -c 'mysqldump -uroot -proot {0}' \
            > ./backup/data_{1}.sql; \
            cp ./backup/data_{1}.sql ./backup/data.sql
            """.format(db, now)
        )


@task
def recovery(sql_file=None):
    '''
    恢复数据库
    '''
    filename = './backup/data.sql' if not sql_file else sql_file
    drop_db()
    create_db()
    local(
        'docker exec -i product_mysql mysql -uroot -proot '
        '{project} < {filename}'.format(filename=filename)
    )


def pull_code():
    '''
    在项目的 tmp/deploy/{project} 更新 gitlab 上的代码，使用 rsync 同步到外网服务器
    '''
    if not os.path.exists(DEPLOY_DIR):
        os.mkdir(DEPLOY_DIR)

    if not os.path.exists(DEPLOY_PROJECT_DIR):
        with lcd(DEPLOY_DIR):
            local('git clone %s' % GIT_REGISTRY)
    else:
        with lcd(DEPLOY_PROJECT_DIR):
            local('git checkout master')
            local('git pull --rebase origin master')

    local(
        'rsync -av {} {}@{}:/data/deploy_app/'.format(
            DEPLOY_PROJECT_DIR,
            env.user,
            env.host
        )
    )


@task
def deploy_test():
    """发布测试环境"""
    assert env.roles == ['test'], (
        'Role error! Role must be backend!',
    )
    pull_code()
    execute(deploy, 'test')
    execute(deploy_celery, 'test_celery')


@task
def deploy_front_prod():
    """发布前台服务"""
    assert all([i in ['front1', 'front2'] for i in env.roles]), (
        'Role error! Roles must in (front1, front2)!'
    )
    pull_code()
    execute(deploy, 'prod')


@task
def deploy_backend_prod():
    """发布后台服务"""
    assert env.roles == ['backend'], (
        'Role error! Role must be backend!',
    )
    pull_code()
    execute(deploy, 'prod')
    execute(deploy_celery, 'celery')


@task
def mysql_backup():
    execute(backup_mysql, hosts=[PROD_MYSQL_HOST])


@task
def runtest(coverage=False, reuse_db=0):
    with shell_env(REUSE_DB='1' if reuse_db else '0'):
        if coverage:
            manage('test -n --nomigrations --xunit-file=/code/coverage/xunit_report.xml --cover-html-dir=/code/coverage/html')
        else:
            manage('test --nomigrations')

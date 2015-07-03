from fabric.context_managers import settings, cd
from fabric.operations import run, sudo

__author__ = 'kenneth'


def deploy(dest='test', user='www-data', git_hash=None, syncdb=False,
           source='https://github.com/ewheeler/rapidpro-webhooks.git'):
    if dest == 'prod':
        proc_name = 'webhooks'
        path = '/var/www/webhooks/rapidpro-webhooks/'
        workon = '/var/www/env/webhooks/bin/python'
    else:
        proc_name = 'test_webhooks'
        path = '/var/www/test/webhooks/'
        workon = '/var/www/webhooks/webpy-webhooks/'

    with settings(warn_only=True):
        if run("test -d %s" % path).failed:
            run("git clone %s %s" % (source, path))
            with cd(path):
                run("git config core.filemode false")
    with cd(path):
        run("git stash")
        if not git_hash:
            run("git pull origin master")
        else:
            run("git fetch")
            run("git checkout %s" % git_hash)

        if syncdb:
            run("%s server.py db upgrade")
            sudo("chown -R %s:%s ." % (user, user))
            sudo("chmod -R ug+rwx .")
    sudo("supervisorctl restart %s" % proc_name)
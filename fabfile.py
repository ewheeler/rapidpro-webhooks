from settings import prod, dev
from fabric.context_managers import settings, cd
from fabric.operations import run, sudo

__author__ = 'kenneth'


def deploy(dest='dev', user='www-data', git_hash=None, syncdb=False, restart_celery=False,
           source='https://github.com/ewheeler/rapidpro-webhooks.git'):
    if dest == 'prod':
        print "Deploying to prod"
        proc_name = 'webhooks'
        path = '/var/www/webhooks/rapidpro-webhooks/'
        workon = '/var/www/env/webhooks/bin/'
        port = prod.SERVER_PORT
        pip = 'requirements/prod.txt'
    else:
        print "Deploying to test"
        proc_name = 'test_webhooks'
        path = '/var/www/test/webhooks/'
        workon = '/var/www/env/test_webhooks/bin/'
        port = dev.SERVER_PORT
        pip = 'requirements/dev.txt'

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
        run("%spip install -r %s" % (workon, pip))

        if syncdb:
            run("%spython server.py db upgrade" % workon)
        sudo("chown -R %s:%s ." % (user, user))
        sudo("chmod -R ug+rwx .")
        run("export RPWEBHOOKS_SETTINGS='settings/%s.py' && %snosetests" % (dest, workon))
    sudo("supervisorctl stop %s" % proc_name)
    with settings(warn_only=True):
        output = run("sudo fuser %d/tcp" % port)
        if output:
            proc_id = output.split()[1].strip()
            sudo("kill -9 %s" % proc_id)
    sudo("supervisorctl start %s" % proc_name)
    if dest == 'prod' and restart_celery:
        sudo("supervisorctl restart webhooks_celery")
"""Manage project deployment on remote hosts. Mostly wraps the Makefile which
does most of the heavy lifting.
"""
import os
import tempfile

from fabric.api import *

prefix = os.getenv('PREFIX') or '/var/www'
pkgroot = os.path.join(prefix, 'hi.landcarbon.org', 'landcarbon-cdi')
env.shell = '/bin/sh -c'

def putdb():
    """Transfer sqlite db and backup the target."""
    withdir('mv landcarbon.db landcarbon-$(date -Iminutes).db')
    put('landcarbon.db', pkgroot)

def withdir(cmd, rootdir=pkgroot):
    with cd(rootdir):
        run(cmd)

def make(target='all', **kwargs):
    gnumake = 'gmake' if 'bsd' in run('uname').lower() else 'make'
    overrides = ' '.join(map('='.join, kwargs.items()))
    withdir(' '.join([gnumake, overrides, target]))

def put_makefile():
    put('Makefile', os.path.join(pkgroot, 'Makefile'))

def service(name, action='restart'):
    sudo('service {} {}'.format(name, action))

def supervisor(name, action='restart'):
    sudo('supervisorctl {} {}'.format(action, name))

def pushpull():
    """Update master on remote."""
    local('git push dev master')
    withdir('git pull')

def buildremote():
    """Push changes and run the latest development build."""
    pushpull()
    supervisor('landcarbon-cdi-gunicorn', 'stop')
    make('venv collectstatic')
    supervisor('landcarbon-cdi-gunicorn', 'start')

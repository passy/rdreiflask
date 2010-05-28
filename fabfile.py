# -*- coding: utf-8 -*-
"""
fabfile
~~~~~~~

Deployment script.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from fabric.api import run, local, env, put, cd
from os import getcwd, chdir, unlink


def staging():
    env.host_string = "www@test.rdrei.net"
    env.dir = "/home/www"


def compress_css():
    old_cwd = getcwd()
    chdir("rdrei/static/")
    local("compass compile -c config.rb.prod")
    local("git add -f css/")
    local("git commit -m 'CSS Update'")
    chdir(old_cwd)


def compress():
    compress_css()
    # TODO: Compress JS


def upload():
    # Create archive
    local("git archive HEAD --prefix=rdreiflask.deploy/ --format=tar | bzip2 > deploy.tar.bz2")
    put("deploy.tar.bz2", env.dir)
    unlink("deploy.tar.bz2")


def unpack():
    with cd(env.dir):
        run("tar -xjf deploy.tar.bz2")
        run("rm deploy.tar.bz2")


def remote_clean():
    with cd(env.dir):
        run("rm -rf rdreiflask.deploy")


def replace():
    with cd(env.dir):
        run(r"mv rdreiflask rdreiflask.bak$$")
        run("mv rdreiflask.deploy rdreiflask")


def deploy():
    local("git checkout -b deploy")
    try:
        compress()
        upload()
    finally:
        local("git checkout master")
        local("git branch -D deploy")

    unpack()
    # TODO: Migrate or something like that?
    # TODO: Run tests?
    replace()
    remote_clean()

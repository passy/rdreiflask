# -*- coding: utf-8 -*-
"""
fabfile
~~~~~~~

Deployment script.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

import subprocess
from os import getcwd, chdir, unlink, path, listdir
from fabric.api import run, local, env, put, cd, sudo


def staging():
    env.host_string = "www@test.rdrei.net"
    env.dir = "/home/www/rdreiflask"
    env.git_remote = "staging"


def compress_css():
    old_cwd = getcwd()
    chdir("rdrei/static/")
    local("compass compile -c config.rb.prod")
    local("git add -f css/")
    local("git commit -m 'CSS Update'")

    chdir(old_cwd)


def compile_css():
    old_cwd = getcwd()
    chdir("rdrei/static/")
    local("compass compile")
    chdir(old_cwd)


def compress_js():
    old_cwd = getcwd()
    if not path.exists("compiler.jar"):
        raise RuntimeError("compiler.jar should be placed in "
                           "the root folder!")

    command = "java -jar compiler.jar"
    proc = subprocess.Popen(command, shell=True,
                            stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE)

    chdir("rdrei/static/js/")
    for filename in listdir("."):
        if filename == 'rdrei.compress.js':
            continue
        with open(filename, 'r') as file:
            proc.stdin.write(file.read())

    proc.stdin.close()
    with open("rdrei.compress.js", 'w') as output:
        output.write(proc.stdout.read())

    proc.stdout.close()
    if proc.wait() != 0:
        raise RuntimeError("Closure Compiler exited with failure "
                           "status!")

    chdir(old_cwd)


def upload():
    local("git push --force {0} deploy".format(env.git_remote))


def remote_update():
    with cd(env.dir):
        run("git fetch origin")
        run("git merge -Xtheirs origin/deploy")

    sudo("supervisorctl restart rdreiflask")


def compress():
    compress_css()
    # TODO: Compress JS


def deploy():
    local("git checkout -b deploy")
    try:
        compress()
        upload()
        remote_update()
    finally:
        local("git checkout master")
        local("git branch -D deploy")

    compile_css()

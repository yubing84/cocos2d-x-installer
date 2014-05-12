#!/usr/bin/python
# ----------------------------------------------------------------------------
# get-engine: get engine from the git repository for generating installer
#
# Author: Bill Zhang
#
# License: MIT
# ----------------------------------------------------------------------------

# python
import sys
import os
from subprocess import Popen, CalledProcessError
import shutil

from optparse import OptionParser

def _os_is_win32():
    return sys.platform == 'win32'

def _find_repo_dir():
    path = os.path.abspath(os.getcwd())
    while True:
        if _os_is_win32():
            # windows root path, eg. c:\
            import re
            if re.match(".+:\\\\$", path):
                break
        else:
            # unix like use '/' as root path
            if path == '/' :
                break
        if _is_a_repo(path):
            return path

        path = os.path.dirname(path)

    return None

def _is_a_repo(repo_dir):
    cfg_dir = os.path.join(repo_dir, ".git")
    return os.path.isdir(cfg_dir)

def unzip(source_filename, dest_dir):
    import zipfile
    z = zipfile.ZipFile(source_filename)
    for info in z.infolist():
        name = info.filename

        # don't extract absolute paths or ones with .. in them
        if name.startswith('/') or '..' in name:
            continue

        target = os.path.join(dest_dir, *name.split('/'))
        if not target:
            continue
        if name.endswith('/'):
            # directory
            if not os.path.exists(target):
                os.mkdir(target)
        else:
            # file
            data = z.read(info.filename)
            file_dir = os.path.dirname(target)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            f = open(target,'wb')
            try:
                f.write(data)
            finally:
                f.close()
                del data
        unix_attributes = info.external_attr >> 16
        if unix_attributes:
            os.chmod(target, unix_attributes)
    z.close()

def run_shell(cmd, cwd=None):
    """
    Runs shell command.

    @type cmd:  string
    @param cmd: Command to be executed.

    @type cwd:  string
    @param cwd: Working directory.

    @rtype:     int
    @return:    Return code of the command.

    @raise CalledProcessError:  Raises exception if return code of the command is non-zero.
    """
    p = Popen(cmd, shell=True, cwd=cwd)
    p.wait()

    if p.returncode:
        raise CalledProcessError(returncode=p.returncode, cmd=cmd)

    return p.returncode

def get_engine(repo_dir, repo_name):
    if repo_dir is None:
        repo_dir = _find_repo_dir()
        if repo_dir is None:
            print("Current directory is not a git repository!\nPlease specify git repository by -d.")
            return

    if not _is_a_repo(repo_dir):
        print("Directory %s is not a git repository!" % repo_dir)
        return

    # copy the repo into dst dir
    dst_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    framework_dir = os.path.join(dst_dir, "cocos", "frameworks")
    dst_repo_dir = os.path.join(framework_dir, repo_name)
    if os.path.exists(dst_repo_dir):
        shutil.rmtree(dst_repo_dir)
    print("> Copying repo %s into %s" % (repo_dir, dst_repo_dir))
    shutil.copytree(repo_dir, dst_repo_dir)
    print("> Copy succeed!")

    # get the make-package tool
    tool_path = os.path.join(dst_repo_dir, "tools", "make-package", "git-archive-all")
    if not os.path.isfile(tool_path):
        print("Can't find the make-package tool")
        return

    zip_path = os.path.join(dst_dir, "%s.zip" % repo_name)
    if os.path.isfile(zip_path):
        os.remove(zip_path)

    # run the tool
    print("> Generating the zip file")
    cmd = "\"%s\" \"%s\"" % (tool_path, zip_path)
    run_shell(cmd, dst_repo_dir)
    print("> Generate succeed!")

    # remove the copyed engine path
    print("> Remove the engine directory")
    shutil.rmtree(dst_repo_dir)
    print("> Remove succeed!")

    # unzip the file
    print("> Unzip the file")
    unzip(zip_path, framework_dir)
    print("> Unzip succeed!")

    # copy the external file
    replace_dir = os.path.join(dst_repo_dir, "external")
    replace_src_dir = os.path.join(repo_dir, "external")
    if os.path.exists(replace_dir):
        shutil.rmtree(replace_dir)
    shutil.copytree(replace_src_dir, replace_dir)

    # change the mode of all the files
    pkg_dir = os.path.join(dst_dir, "cocos")
    run_shell("chmod -R a+w %s" % pkg_dir)
    # run_shell("chmod -R a+x %s" % pkg_dir)

    # remove the zip file
    print("> Remove the zip file")
    os.remove(zip_path)
    print("> Remove succeed!")

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-d', '--dir', dest='repo_dir', help='directory of engine')
    parser.add_option('-n', '--name', dest='repo_name', default='cocos2d-x', help='the name of git repository')
    opts, args = parser.parse_args()

    get_engine(opts.repo_dir, opts.repo_name)

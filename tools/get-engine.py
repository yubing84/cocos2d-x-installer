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

DST_X_DIR_NAME = "cocos2d-x"
DST_JS_DIR_NAME = "cocos2d-js"

def _os_is_win32():
    return sys.platform == 'win32'

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
                os.makedirs(target)
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

def _get_repo_files(repo_dir, dst_dir, repo_name):
    # copy the repo into dst dir
    dst_repo_dir = os.path.join(dst_dir, repo_name)
    if os.path.exists(dst_repo_dir):
        shutil.rmtree(dst_repo_dir)
    print("\t> Copying repo %s into %s" % (repo_dir, dst_repo_dir))
    shutil.copytree(repo_dir, dst_repo_dir)
    print("\t> Copy succeed!")

    # get the make-package tool
    tool_path = os.path.join(dst_repo_dir, "tools", "make-package", "git-archive-all")
    if not os.path.isfile(tool_path):
        print("\tCan't find the make-package tool")
        return

    zip_path = os.path.join(dst_dir, "%s.zip" % repo_name)
    if os.path.isfile(zip_path):
        os.remove(zip_path)

    # run the tool
    print("\t> Generating the zip file")
    tool_dir_name = os.path.dirname(tool_path)
    cmd = "\"%s\" \"%s\"" % (tool_path, zip_path)
    run_shell(cmd, tool_dir_name)
    print("\t> Generate succeed!")

    # remove the copyed engine path
    print("\t> Remove the engine directory")
    shutil.rmtree(dst_repo_dir)
    print("\t> Remove succeed!")

    # unzip the file
    print("\t> Unzip the file")
    unzip(zip_path, dst_dir)
    print("\t> Unzip succeed!")

    # remove the zip file
    print("\t> Remove the zip file")
    os.remove(zip_path)
    print("\t> Remove succeed!")

def _get_cocos2dx(x_dir, dst_dir):
    # get engine from repo
    print("> Get cocos2d-x from %s" % x_dir)
    _get_repo_files(x_dir, dst_dir, DST_X_DIR_NAME)
    # dst_repo_dir = os.path.join(dst_dir, DST_X_DIR_NAME)
    #
    # # copy the external file
    # replace_dir = os.path.join(dst_repo_dir, "external")
    # replace_src_dir = os.path.join(x_dir, "external")
    # if os.path.exists(replace_dir):
    #     shutil.rmtree(replace_dir)
    # shutil.copytree(replace_src_dir, replace_dir)
    #
    # # copy the runtime files
    # runtime_dir = os.path.join(dst_repo_dir, "templates", "lua-template-runtime", "runtime")
    # runtime_src_dir = os.path.join(x_dir, "templates", "lua-template-runtime", "runtime")
    # if os.path.exists(runtime_dir):
    #     shutil.rmtree(runtime_dir)
    # shutil.copytree(runtime_src_dir, runtime_dir)

def _get_cocos2djs(js_dir, dst_dir):
    # get engine from repo
    print("\n>Get cocos2d-js from %s" % js_dir)
    _get_repo_files(js_dir, dst_dir, DST_JS_DIR_NAME)

    # remove the -x directory in js
    inside_x_dir = os.path.join(dst_dir, DST_JS_DIR_NAME, "frameworks", "js-bindings", "cocos2d-x")
    if os.path.isdir(inside_x_dir):
        shutil.rmtree(inside_x_dir)

def get_engine(x_dir, js_dir):
    if x_dir is None or not _is_a_repo(x_dir):
        print("Please specify cocos2d-x repository directory by -x.")
        return

    if js_dir is None or not _is_a_repo(js_dir):
        print("Please specify cocos2d-js repository directory by -j.")
        return

    dst_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    framework_dir = os.path.join(dst_dir, "cocos", "frameworks")

    # get -x engine
    _get_cocos2dx(x_dir, framework_dir)

    # get -js engine
    _get_cocos2djs(js_dir, framework_dir)

    # change the mode of all the files
    pkg_dir = os.path.join(dst_dir, "cocos")
    run_shell("chmod -R a=rwx %s" % pkg_dir)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-x', dest='x_dir', help='directory of cocos2d-x engine')
    parser.add_option('-j', '--js', dest='js_dir', help='directory of cocos2d-js engine')
    opts, args = parser.parse_args()

    get_engine(opts.x_dir, opts.js_dir)

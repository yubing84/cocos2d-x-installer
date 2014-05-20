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

HEADER_FILE_PATH = "cocos/base/ccConfig.h"
CONSOLE_PATH = "tools/cocos2d-console/bin"
LIBS_PATH = "frameworks/runtime-src/proj.android/libs"
MK_PATH = "frameworks/runtime-src/proj.android/jni/Application.mk"
MAKE_PKG_TOOL_PATH = "tools/make-package/git-archive-all"
X_IN_JS_PATH = "frameworks/js-bindings/cocos2d-x"

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
    tool_path = os.path.join(dst_repo_dir, MAKE_PKG_TOOL_PATH)
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


def _get_cocos2djs(js_dir, dst_dir):
    # get engine from repo
    print("\n>Get cocos2d-js from %s" % js_dir)
    _get_repo_files(js_dir, dst_dir, DST_JS_DIR_NAME)

    # remove the -x directory in js
    inside_x_dir = os.path.join(dst_dir, DST_JS_DIR_NAME, X_IN_JS_PATH)
    if os.path.isdir(inside_x_dir):
        shutil.rmtree(inside_x_dir)

def _modify_header_file(file_path):
    # read the header file
    file_obj = open(file_path)
    temp_file = "%s.txt" % file_path
    temp_obj = open(temp_file, "w")
    lines = []
    import re
    for line in file_obj:
        if re.match(r"^#define[ ]+CC_CONSTRUCTOR_ACCESS[ ]+.+", line):
            lines.append("#define CC_CONSTRUCTOR_ACCESS public\n")
        else:
            lines.append(line)

    file_obj.close()
    temp_obj.writelines(lines)
    temp_obj.close()

    # remove the origin file
    os.remove(file_path)

    # rename the temp file
    os.rename(temp_file, file_path)

def _gen_file_for_js(dst_dir):
    # Copy the header file
    header_file = os.path.join(dst_dir, DST_X_DIR_NAME, HEADER_FILE_PATH)
    dest_file = os.path.join(dst_dir, os.pardir, os.path.basename(header_file))
    shutil.copy(header_file, dest_file)

    # modify the header file
    _modify_header_file(dest_file)
    return

def _modify_mk(mk_file):
    if os.path.isfile(mk_file):
        file_obj = open(mk_file, "a")
        file_obj.write("APP_ABI :=armeabi armeabi-v7a x86\n")
        file_obj.close()

def _gen_prebuilt_libs(engine_dir, language):
    import tempfile
    tmp_dir = os.path.join(tempfile.gettempdir(), os.path.basename(engine_dir))

    # copy engine to tmp
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    shutil.copytree(engine_dir, tmp_dir)

    if language == "js":
        shutil.copytree(os.path.join(engine_dir, os.pardir, DST_X_DIR_NAME), os.path.join(tmp_dir, X_IN_JS_PATH))
        _modify_header_file(os.path.join(tmp_dir, X_IN_JS_PATH, HEADER_FILE_PATH))

    console_dir = os.path.join(tmp_dir, CONSOLE_PATH)
    cmd_path = os.path.join(console_dir, "cocos")
    temp_proj_name = "My%sGame" % language

    # create a runtime project
    create_cmd = "%s new -l %s -t runtime %s" % (cmd_path, language, temp_proj_name)
    run_shell(create_cmd, console_dir)

    # Add multi ABI in Application.mk
    mk_file = os.path.join(console_dir, temp_proj_name, MK_PATH)
    _modify_mk(mk_file)

    # build it
    build_cmd = "%s compile -s %s -p android --ndk-mode release -j 4" % (cmd_path, temp_proj_name)
    run_shell(build_cmd, console_dir)

    # copy libs to framework dir
    libs_dir = os.path.join(console_dir, temp_proj_name, LIBS_PATH)
    target_libs_dir = os.path.join(engine_dir, "templates", "%s-template-runtime" % language, LIBS_PATH)
    shutil.copytree(libs_dir, target_libs_dir)

    # remove the engine in tmp
    shutil.rmtree(tmp_dir)

    return

def get_engine(x_dir, js_dir, target):
    if x_dir is None or not _is_a_repo(x_dir):
        print("Please specify cocos2d-x repository directory by -x.")
        return

    if js_dir is None or not _is_a_repo(js_dir):
        print("Please specify cocos2d-js repository directory by -j.")
        return

    dst_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if target == 'win32':
        framework_dir = os.path.join(dst_dir, "cocos-win32", "frameworks")
    else:
        framework_dir = os.path.join(dst_dir, "cocos", "frameworks")

    # get -x engine
    _get_cocos2dx(x_dir, framework_dir)

    # get -js engine
    _get_cocos2djs(js_dir, framework_dir)

    if target == 'win32':
        # generate header file for js
        _gen_file_for_js(framework_dir)

    _gen_prebuilt_libs(os.path.join(framework_dir, DST_X_DIR_NAME), "lua")
    _gen_prebuilt_libs(os.path.join(framework_dir, DST_JS_DIR_NAME), "js")

    if target == 'mac':
        # change the mode of all the files
        pkg_dir = os.path.join(dst_dir, "cocos")
        run_shell("chmod -R a=rwx %s" % pkg_dir)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-x', dest='x_dir', help='directory of cocos2d-x engine')
    parser.add_option('-j', '--js', dest='js_dir', help='directory of cocos2d-js engine')
    parser.add_option('-t', '--target', dest='target', help='the target platform')
    opts, args = parser.parse_args()

    target = opts.target
    if target is None:
        if _os_is_win32():
            target = 'win32'
        else:
            target = 'mac'

    if target != 'win32' and target != 'mac':
        print("Target platform must be one of [win32, mac]")
        exit(1)

    get_engine(opts.x_dir, opts.js_dir, target)

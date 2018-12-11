####################################################################################################
# GSLab_Tools 1.1.1
# Copyright (c) 2016 Matthew Gentzkow, Jesse Shapiro
# License: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction, 
# including without limitation the rights to use, copy, modify, merge, publish, distribute, 
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or 
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
####################################################################################################

import os
import sys
import shutil
import subprocess
import sys

class BadArgumentError(Exception):
    def __init__(self, message = ''):
        print('Error:', message)

class BadExecutableError(Exception):
    def __init__(self, message = ''):
        print('Error:', message)

class BadExtensionError(Exception):
    def __init__(self, message = ''):
        print('Error:', message)

class LFSError(Exception):
    def __init__(self, message = ''):
        print('Error:', message)

def check_lfs():
    try:
        output = subprocess.check_output("git-lfs install", shell = True)
    except:
        try:
            output = subprocess.check_output("git-lfs init", shell = True) # init is deprecated version of install
        except:
            raise LFSError('''Either Git LFS is not installed or your Git LFS settings need to be updated. 
                  Please install Git LFS or run 'git lfs install --force' if prompted above.''')

def stata_command_unix(flavor):
    options = {'darwin': '-e',
               'linux' : '-b',
               'linux2': '-b'}
    option  = options[sys.platform]
    command = flavor + ' ' + option + ' %s ' # %s will take filename later
    return command

def stata_command_win(flavor):
    command  = flavor + ' /e do' + ' %s ' # %s will take filename later
    return command

def is_unix():
    unix = ['darwin', 'linux', 'linux2']
    return sys.platform in unix

def is_64_windows():
    return 'PROGRAMFILES(X86)' in os.environ

def is_in_path(program):
    # General helper function to check if `program` exist in the path env
    if is_exe(program):
        return program
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            path = path.strip("'")
            exe = os.path.join(path, program)
            if is_exe(exe):
                return exe
    return None

def is_exe(file_path):
    return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

def make_list_if_string(source):
    if isinstance(source, str) or isinstance(source, bytes):
        source = [str(source)]
    return source

def check_code_extension(source_file, software):
    extensions = {'stata'  : '.do',
                  'r'      : '.r', 
                  'lyx'    : '.lyx',
                  'python' : '.py'}
    ext = extensions[software]
    source_file = str.lower(str(source_file))
    if not source_file.endswith(ext):
        raise BadExtensionError('First argument, ' + source_file + ', must be a ' + ext + ' file')
    return None

def current_time():
    return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')   


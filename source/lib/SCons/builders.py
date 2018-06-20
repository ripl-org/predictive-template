####################################################################################################
# GSLab_Tools 1.1.1
# Copyright (c) 2016 Matthew Gentzkow, Jesse Shapiro
# License: MIT
#
# Modified by Miraj Shah - RIIPL
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

from SCons.Util import is_String, is_List
import SCons
import os
import re
from itertools import chain

def setup_scons_entities(env):
    try:
        shell = env['SHELL']
    except KeyError:
        raise SCons.Errors.UserError('Missing SHELL construction variable.')

    try:
        spawn = env['SPAWN']
    except KeyError:
        raise SCons.Errors.UserError('Missing SPAWN construction variable.')
    else:
        if type(spawn) == 'str':
            spawn = env.subst(spawn, raw=1, conv=lambda x: x)

    escape = env.get('ESCAPE', lambda x: x)

    try:
        ENV = env['ENV']
    except KeyError:
        import SCons.Environment
        ENV = SCons.Environment.Environment()['ENV']

    # Ensure that the ENV values are all strings:
    for key, value in list(ENV.items()):
        if not is_String(value):
            if is_List(value):
                # If the value is a list, then we assume it is a
                # path list, because that's a pretty common list-like
                # value to stick in an environment variable:
                value = flatten_sequence(value)
                ENV[key] = os.pathsep.join(map(str, value))
            else:
                # If it isn't a string or a list, then we just coerce
                # it to a string, which is the proper way to handle
                # Dir and File instances and will produce something
                # reasonable for just about everything else:
                ENV[key] = str(value)

    return (shell, spawn, escape, ENV.copy())

def get_log_path(source_file, env):
    log_path = env.get('log_path')
    if log_path:
        if log_path.startswith('#'):
            log_path = log_path[1:]

        return log_path

    log_file = ''

    source_dir = os.path.dirname(source_file)
    filename = os.path.basename(source_file)

    if source_file.startswith('source/'):
        log_file = os.path.join('output', source_dir[7:], filename + '.log')
    else:
        log_file = os.path.join('output', source_dir, filename + '.log')

    return(log_file)    

def build_r(target, source, env):
    shell, spawn, escape, ENV = setup_scons_entities(env)

    source      = [str(node) for node in make_list_if_string(source)]
    target      = [str(node) for node in make_list_if_string(target)]
    source_file = source[0]

    check_code_extension(source_file, 'r')

    log_file    = get_log_path(source_file, env)
    ENV['SCONS_LOG_PATH'] = log_file

    other_args = env.get('other_args')
    if other_args is None:
        other_args = []
    elif not isinstance(other_args, list):
        raise BadArgumentError('other_args must be a list')
    other_args = [str(arg) for arg in other_args]

    command = ['Rscript'] + source + other_args + target
    result = spawn(shell, escape, command[0], command, ENV)
    if result:
        msg = "Error %s" % result
        raise SCons.Errors.BuildError(errstr=msg,
                                      status=result,
                                      action=None,
                                      command=' '.join(command))

    return None

def build_python(target, source, env):

    shell, spawn, escape, ENV = setup_scons_entities(env)

    source = [str(node) for node in make_list_if_string(source)]
    target = [str(node) for node in make_list_if_string(target)]

    check_code_extension(source[0], 'python')

    ENV['SCONS_LOG_PATH'] = get_log_path(source[0], env)

    command = ['python', '-u'] + [x.replace("$", "\$") for x in chain(source, target)]
    result = spawn(shell, escape, command[0], command, ENV)
    if result:
        msg = "Error %s" % result
        raise SCons.Errors.BuildError(errstr=msg,
                                      status=result,
                                      action=None,
                                      command=' '.join(command))

    return None

stata_error_re = re.compile('^r\(([0-9]+)\);$', flags = re.M)
def build_stata(target, source, env):
    shell, spawn, escape, ENV = setup_scons_entities(env)

    source      = [str(node) for node in make_list_if_string(source)]
    target      = [str(node) for node in make_list_if_string(target)]
    source_file = source[0]

    check_code_extension(source_file, 'stata')

    log_file    = get_log_path(source_file, env)
    ENV['SCONS_LOG_PATH'] = log_file

    other_args = env.get('other_args')
    if other_args is None:
        other_args = []
    elif not isinstance(other_args, list):
        raise BadArgumentError('other_args must be a list')
    other_args = [str(arg) for arg in other_args]

    command = ['statamp', '-b', 'do'] + source + other_args + target
    result = spawn(shell, escape, command[0], command, ENV)

    loc_log_file = os.path.basename(source_file).replace('.do','.log')

    with open(loc_log_file, 'r') as loc_log_f:
        stata_log_contents = loc_log_f.read()
        print(stata_log_contents)

        with open(log_file, 'a') as log_f:
            log_f.write(stata_log_contents)

        error_matches = stata_error_re.search(stata_log_contents)
        if error_matches:
            result = int(error_matches.groups()[0])

    os.remove(loc_log_file)

    if result:
        msg = "Error %s" % result
        raise SCons.Errors.BuildError(errstr=msg,
                                      status=result,
                                      action=None,
                                      command=' '.join(command))

    return None


r_builder = Builder(action = build_r)
python_builder = Builder(action = build_python)
stata_builder = Builder(action = build_stata)

env.Append(BUILDERS = {'R': r_builder,
                       'Python': python_builder,
                       'Stata': stata_builder})

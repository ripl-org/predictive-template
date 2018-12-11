import sys
import os
import errno
import subprocess
import datetime

log_datetime_format = '%Y-%m-%d %I:%M:%S:%f %p'

class RIIPLCommandSpawner:
    def spawn( self, sh, escape, cmd, args, env ):
        try:
            # Set up log file
            if env.get('SCONS_LOG_PATH'):    
                log_command = ['tee', '-a', env['SCONS_LOG_PATH']]
                
                # Create directories along log path if they don't exist
                if not os.path.exists(os.path.dirname(env['SCONS_LOG_PATH'])):
                    try:
                        os.makedirs(os.path.dirname(env['SCONS_LOG_PATH']))
                    except OSError as exc: # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
            else:
                log_command = ['cat']

            # Log start time
            args = [str(arg) for arg in args]
            command_string = ' '.join(args) + '\n'
            start_time = datetime.datetime.now()
            start_string = 'Executing: {} ---------------- ({})\n'.format(
                start_time.strftime(log_datetime_format),
                env['USER'])

            print(start_string)
            if env.get('SCONS_LOG_PATH'):
                with open(env['SCONS_LOG_PATH'], 'w') as log_f:
                    log_f.writelines([command_string, start_string])

            # Kick off command
            proc = subprocess.Popen([sh, '-c', ' '.join(args)],
                env = env,
                close_fds = True,
                stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT)

            # Tee or print output
            proc2 = subprocess.Popen(log_command,
                env = env,
                close_fds = True,
                stdin = proc.stdout,
                stdout = sys.stdout,
                stderr = sys.stderr)

            proc.stdout.close()
            retval = proc.wait()
            proc2.wait()

        except OSError as x:
            if x.errno != 10:
                raise x
                print('OSError ignored on command: %s' % command_string)
                retval = 0

        if retval == 0:
            # Log end time
            end_time = datetime.datetime.now()
            end_string = 'Completed: {} ---------------- ({})\n'.format(
                end_time.strftime(log_datetime_format),
                env['USER'])

            print(end_string)
            if env.get('SCONS_LOG_PATH'):
                with open(env['SCONS_LOG_PATH'], 'a') as log_f:
                    log_f.writelines([end_string])

        return retval

def SetupRIIPLLogging(env):
    spawner = RIIPLCommandSpawner()
    spawner.env = env
    env['SPAWN'] = spawner.spawn

def SetLogPath(env, log_path):
    new_env = env['ENV'].copy()
    new_env['SCONS_LOG_PATH'] = File(log_path).abspath
    return new_env
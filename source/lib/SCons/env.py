import os
import getpass

repo_root = Dir(".").abspath
varnames = ["STATATMP", "PYTHON_DIR", "MATLAB_ROOT",
            "USER", "HOME", "PATH","LOGNAME", "LANG", 
            "LD_LIBRARY_PATH","LD_RUN_PATH","LIBRARY_PATH", 
            "MODULEHOME", "MODULEPATH", "MODULESHELL", "MODULEPYTHON", 
            "QTDIR", "QTLIB", "TERM", "SHELL", "DISPLAY", "ORACLE_HOME", 
            "LOADEDMODULES", "S_ADO", "SHLVL","PKG_CONFIG_PATH", "TWO_TASK"]

env_vars = {var: os.environ.get(var, "") for var in varnames}
env_vars.update({
    "REPO_ROOT": repo_root,
    "PYTHONPATH": os.path.abspath("./source/lib/Python"),
    "ORACLE_SID": "RIPL1",
    "R_LIBS": "",
    "R_LIBS_USER": ""
})

env = Environment(ENV=env_vars)
setattr(env, "RIIPL_PROJECT", repo_root.rpartition("/")[2])
setattr(env, "USERNAME", getpass.getuser())
for k, v in CONSTANTS.items(): setattr(env, k, v)

SetupRIIPLLogging(env)

def riipl_decider(dependency, target, prev_ni):
    # Use SCons" default checking for changes in the source file (MD5)
    source_changed = dependency.changed_content(target, prev_ni)
    if source_changed:
        return source_changed
    else:
        target_changed = False
        # If target node does not implement get_csig(), leave figuring out whether to
        # rebuild it and move on
        try:
            target_info = target.get_stored_info()

            if target_info.ninfo.csig != target.get_csig():
                target_changed = True
        except AttributeError:
            pass

        return target_changed


env.Decider(riipl_decider)

Export(["env", "SetLogPath"])

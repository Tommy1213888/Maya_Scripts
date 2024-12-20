from os import path
from importlib import import_module
import compileall
import sys, types
import pkgutil


def recompile(modulename):
    """Recompile the given module, its directory's contents!"""

    try:
        loader = pkgutil.get_loader(modulename.__name__)
        myScriptPath = loader.get_filename() if loader else None
    except AttributeError:
        return

    if myScriptPath and path.isdir(myScriptPath):
        compileall.compile_dir(myScriptPath, force=True)


def reload_module(modulename):
    """Reload the given module and all children"""

    # Get a reference to each loaded module
    loaded_modules = dict([(key, value) for key, value in sys.modules.items()
        if key.startswith(modulename.__name__) and
        isinstance(value, types.ModuleType)])

    # Delete references to these loaded modules from sys.modules
    for key in loaded_modules:
        del sys.modules[key]

    # Load each of the modules again
    # Make old modules share state with new modules
    for key in loaded_modules:
        newmodule = __import__(key)
        oldmodule = loaded_modules[key]
        oldmodule.__dict__.clear()
        oldmodule.__dict__.update(newmodule.__dict__)

def refresh(modulename):
    recompile(modulename)
    reload_module(modulename)

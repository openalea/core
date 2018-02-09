# {# pkglts, base

from . import version

__version__ = version.__version__

# #}

from openalea.core.external import *
from script_library import ScriptLibrary


def global_module(module):
    """ Declare a module accessible everywhere. """

    import __builtin__
    __builtin__.__dict__[module.__name__] = module

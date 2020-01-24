# {# pkglts, base

from openalea.core import version

__version__ = version.__version__

# #}

from openalea.core.external import *
from .script_library import ScriptLibrary


def global_module(module):
    """ Declare a module accessible everywhere. """

    import six.moves.builtins
    six.moves.builtins.__dict__[module.__name__] = module

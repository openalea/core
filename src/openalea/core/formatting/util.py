# -*- python -*-
#
# OpenAlea.OALab: Multi-Paradigm GUI
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Guillaume Baty <guillaume.baty@inria.fr>
#
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################
from openalea.core.path import path as Path
import six
import importlib

def pretty_print(obj):
    """
    :param obj: to decode. Can be a string/unicode or a list of string/unicod
    :return: object decoded into utf-8.
    """
    if isinstance(obj, list):
        text = ', '.join(obj).decode('utf-8')
    else:
        text = str(obj).decode('utf-8')
    return text


def icon_path(filepath, default=None, paths=None, packages=None):
    if filepath is None or isinstance(filepath, six.string_types) and filepath.startswith(':/'):
        return None
    if paths is None:
        paths = []
    if packages is None:
        packages = []
    # Search filename in all paths given by user
    _paths = [Path(filepath)] + [Path(p) / filepath for p in paths]

    # Search icons generated by oalab
    _paths += [Path(p) / '._icon.png' for p in paths]

    # If a path is found, try to find absolute path
    # Try to get icon path from object
    for path in _paths:
        if path.isfile():
            return path

    # Search in shared icons provided by packages given by user
    for package in packages:
        module = importlib.import_module(package + '.resources')
        resources_dir = getattr(module, 'resources_dir')
        for path in (filepath, 'icons/%s' % filepath):
            path = resources_dir/path
            if path and path.is_file():
                return path


def obj_icon_path(obj_lst, default=None, paths=None, packages=None):
    if packages is None:
        packages = [openalea.core]

    if not isinstance(obj_lst, (list, tuple)):
        obj_lst = [obj_lst]

    if paths is None:
        paths = []

    # Try to get icon path from object
    _icon_path = None
    for obj in obj_lst:
        if hasattr(obj, 'icon'):
            _icon_path = obj.icon
            break

    if _icon_path:
        return icon_path(_icon_path, default, paths, packages)

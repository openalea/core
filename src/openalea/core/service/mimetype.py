try:
    # Python 2: "unicode" is built-in
    unicode
except NameError:
    unicode = str


__all__ = [
    'decode',
    'encode',
]


def decode(mimetype, mimedata):
    """
    decode("openalealab/model", "model1") -> Model("model1")
    returns an object Model of model1
    """
    if mimetype == 'openalealab/control':
        from openalea.core.control.manager import ControlManager
        identifier, name = mimedata.split(';')
        control = ControlManager().control(name)
        if isinstance(control, list):
            return ControlManager().control(uid=identifier)
        return control
    elif mimetype == 'openalealab/data':
        from openalea.core.service.project import active_project
        from openalea.core.path import path
        project = active_project()
        if project:
            return project.get_item('data', path(unicode(mimedata)).name)
    else:
        return str(mimedata)


def encode(data, mimetype=None):
    """
    encode(Model("model1")) -> ("openalealab/model", "model1")
    returns a tuple mimetype, mimedata
    """
    from openalea.core.control import Control
    from openalea.core.path import path
    if isinstance(data, Control) or mimetype == 'openalealab/control':
        return ('openalealab/control', '%s;%s' % (data.identifier, data.name))
    elif mimetype == 'openalealab/data':
        return ('openalealab/data', str(data.path))
    else:
        return (mimetype, str(data))

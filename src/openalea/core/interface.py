# -*- python -*-
# -*- coding:utf8 -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#                       Christophe Pradal <christophe.prada@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
##############################################################################
"""This module defines Interface classes (I/O types)"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

from openalea.core.metaclass import make_metaclass
from openalea.core.singleton import Singleton
from openalea.core.observer import AbstractListener

from . import color_palette # used for colors of interfaces
import types
import six
# Python 3 <-> Python 3 equivalent types
try:
    from types import (StringType, SliceType, FloatType, IntType, BooleanType, TupleType,
                      ListType, DictType, InstanceType)
except ImportError:
    StringType = str #six.string_types gave a tuple
    SliceType = slice
    FloatType = float
    IntType = int
    BooleanType = bool
    TupleType = tuple
    ListType = list
    DictType = dict
    InstanceType = object


# Dictionary to map Interface with corresponding python type


class TypeInterfaceMap(six.with_metaclass(Singleton, dict)):

    """
    Singleton class to map Interface with standard python type
    InterfaceWidgetMap inherits from dict class
    """

    def declare_interface(self, type, interface):
        """
        Declare an interface and its optional widget

        :param interface: IInterface class object

        :param type: Python type
        """

        if type and type not in self:
            self[type] = interface

        TypeNameInterfaceMap().declare_interface(str(interface), interface)


class TypeNameInterfaceMap(six.with_metaclass(Singleton, dict)):

    """
    Singleton class to map Interface Name with interface type
    InterfaceWidgetMap inherits from dict class
    """

    def declare_interface(self, name, interface):
        """
        Declare an interface and its optional widget

        :param interface: IInterface class object

        :param type: Python type
        """

        if name and name not in self:
            self[name] = interface


class IInterfaceMetaClass(type):

    """
    IInterface Metaclass
    Allow to register corresponding python type
    """

    all = [] # all interfaces

    def __new__(cls, name, bases, dict):
        newCls = type.__new__(cls, name, bases, dict)
        return newCls

    def __init__(cls, name, bases, dic):
        super(IInterfaceMetaClass, cls).__init__(name, bases, dic)
        if(hasattr(cls, "__pytype__")):
            TypeInterfaceMap().declare_interface(cls.__pytype__, cls)
        else:
            TypeInterfaceMap().declare_interface(None, cls)
        if isinstance(cls.__color__, str):
            cls.__color__ = color_palette.HTMLColorToRGB(cls.__color__)
        if cls not in IInterfaceMetaClass.all:
            IInterfaceMetaClass.all.append(cls)

    def __repr__(cls):
        return cls.__name__

# Defaults interfaces


class IInterface(six.with_metaclass(IInterfaceMetaClass, object)):

    """ Abstract base class for all interfaces """
    __pytype__ = None
    __color__ = None

    @classmethod
    def default(cls):
        return None

    def __init__(self, **kargs):
        """ Default init"""

        # # the desc should be used as  a dynamic description of IInterace
        # # default visualisation in widget is done with tooltip
        # self.desc = kargs.get('desc', None)
        # # the label should be used to describe the default static description
        # # default visualisation in widget is done with label
        # self.label = kargs.get('label', None)

    def __repr__(self):
        return self.__class__.__name__ + '()'


class IStr(IInterface):

    """ String interface """

    __pytype__ = StringType
    __color__ = color_palette.maroon
    __label__ = u'Short Text'

    @classmethod
    def default(cls):
        return str()


class ISlice(IInterface):

    """ String interface """

    __pytype__ = SliceType
    __color__ = color_palette.maroon
    __label__ = u'Slice'


class IFileStr(IStr):

    """ File Path interface """
    __color__ = color_palette.maroon
    __label__ = u'File path'

    def __init__(self, filter="All (*)", save=False, **kargs):
        IInterface.__init__(self, **kargs)
        self.filter = filter
        self.save = save

    def __repr__(self):
        if self.filter == "All (*.*)" and not self.save: # default values
            return 'IFileStr'
        else:
            return 'IFileStr(filter="%s", save=%s)' % \
                (self.filter, str(self.save))


class IDirStr(IStr):

    """ Directory Path interface """
    __label__ = u'Directory path'
    pass


class ITextStr(IStr):

    """ Long String interface """
    __label__ = u'Long text'
    pass


class ICodeStr(IStr):

    """ Source code interface """
    __label__ = u'Code'
    pass


class IFloat(IInterface):

    """ Float interface """

    __pytype__ = FloatType
    __color__ = color_palette.blue
    __label__ = u'Float'

    def __init__(self, min=-2. ** 24, max=2. ** 24, step=1., **kargs):
        IInterface.__init__(self, **kargs)
        self.min = min
        self.max = max
        self.step = step

    @classmethod
    def default(cls):
        return 0.

    def __repr__(self):
        default_min = -2 ** 24
        default_max = 2 ** 24
        default_step = 1.
        if (self.min == default_min and
                self.max == default_max and
                self.step == default_step):
            return self.__class__.__name__
        else:
            return 'IFloat(min=%d, max=%d, step=%f)' % \
                (self.min, self.max, self.step)


class IInt(IInterface):

    """ Int interface """
    __pytype__ = IntType
    __color__ = color_palette.blue
    __label__ = u'Integer ℤ'

    def __init__(self, min=-2 ** 24, max=2 ** 24, step=1, **kargs):
        IInterface.__init__(self, **kargs)
        self.min = min
        self.max = max
        self.step = step

    @classmethod
    def default(cls):
        return 0

    def example(self):
        return self.min + 2

    def __repr__(self):
        default_min = -2 ** 24
        default_max = 2 ** 24
        default_step = 1
        if (self.min == default_min and
                self.max == default_max and
                self.step == default_step):
            return self.__class__.__name__
        else:
            return 'IInt(min=%d, max=%d, step=%d)' % \
                (self.min, self.max, self.step)


class IBool(IInterface):

    """ Bool interface """

    __pytype__ = BooleanType
    __color__ = color_palette.aqua
    __label__ = 'Boolean (True/False)'

    @classmethod
    def default(cls):
        return False


class IEnumStr(IStr):

    """ String enumeration """
    __color__ = color_palette.purple
    __label__ = 'Predefined texts'

    def __init__(self, enum=[], **kargs):
        IInterface.__init__(self, **kargs)
        self.enum = enum

    def __repr__(self):
        return 'IEnumStr(enum=%s)' % (str(self.enum))


class IRGBColor(IInterface):

    """ RGB Color """
    __color__ = color_palette.lime
    __label__ = 'Color (RGB)'
    pass


class IDateTime(IInterface):

    """ DateTime """
    __color__ = color_palette.teal
    __label__ = 'Date'
    pass


class ITuple3(IInterface):

    """ Tuple3 """
    __color__ = color_palette.fuchsia
    __label__ = 'Triple'

    @classmethod
    def default(cls):
        return (None, None, None)


class ITuple(IInterface):

    """ Tuple """
    __label__ = 'Tuple'
    __pytype__ = TupleType
    __color__ = color_palette.fuchsia


class IFunction(IInterface):

    """ Function interface """
    __color__ = color_palette.white
    __pytype__ = types.FunctionType


class ISequence(IInterface):

    """ Sequence interface (list, tuple, ...) """
    __pytype__ = ListType
    __color__ = color_palette.green
    __label__ = 'Sequence'

    @classmethod
    def default(cls):
        return list()


class IDict(IInterface):

    """ Dictionary interface """
    __pytype__ = DictType
    __color__ = color_palette.olive
    __label__ = 'Mapping key, value (dictionary)'

    @classmethod
    def default(cls):
        """todo"""
        return dict()


class IData(IStr):

    """ Package data interface """
    __color__ = color_palette.silver
    __label__ = 'Data'

# Dictionary to map Interface with corresponding widget


class InterfaceWidgetMap(six.with_metaclass(Singleton, dict)):

    """
    Singleton class to map Interface with InterfaceWidget
    InterfaceWidgetMap inherits from dict class
    """

    def __init__(self, *args):
        dict.__init__(self, *args)

    def declare_interface(self, interface, widget=None):
        """
        Declare an interface and its optional widget
        @param interface : IInterface class object
        @param widget : IInterfaceWidget class object
        """

        self[interface] = widget


# Base class for interface widget


class IWidgetMetaClass(type):

    """ InterfaceWidget Metaclass """

    def __init__(cls, name, bases, dic, **kargs):
        super(IWidgetMetaClass, cls).__init__(name, bases, dic)
        if(cls.__interface__):
            InterfaceWidgetMap().declare_interface(cls.__interface__, cls)


class IInterfaceWidget(six.with_metaclass(IWidgetMetaClass, AbstractListener)):

    """ Base class for widget associated to an interface """
    __interface__ = None

    def __init__(self, node, parent, parameter_str, interface):
        """
        @param parameter_str : the parameter key the widget is associated to
        @param interface : instance of interface object
        """
        AbstractListener.__init__(self)
        self.node = node
        self.param_str = parameter_str

    def update_state(self):
        """ Enable or disable widget depending of connection status """

        # i = self.node.get_input_index(self.param_str)
        state = self.get_state()

        # By default, disable the entire widget
        try:
            notconnected = bool(state != "connected")
            if(self.internal_data().get('minimal', False)):
                self.setVisible(notconnected)
            else:
                self.setEnabled(notconnected)
        except:
            pass

    def notify(self, sender, event):
        """ Notification sent by node """
        pass

    def set_value(self, newval):
        self.node.set_input(self.param_str, newval)

    def get_value(self):
        return self.node.get_input(self.param_str)

    def set_widget_value(self, newval):
        pass

    def get_widget_value(self):
        return self.get_value()

    def get_state(self):
        return self.node.get_input_state(self.param_str)

    def internal_data(self):
        "return a dict: minimal"
        return self.node.internal_data

    @classmethod
    def get_label(cls, node, parameter_str):
        return node.get_input_port(name=parameter_str).get_label()

    def unvalidate(self):
        self.node.unvalidate_input(self.param_str)

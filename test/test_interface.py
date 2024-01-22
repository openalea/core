""" Core interface test"""

from __future__ import absolute_import
__license__ = "Cecill-C"
__revision__ = " $Id$ "

from openalea.core.interface import *




class IMyInterface(IInterface):
    """Test declation of a new interface"""

    __pytype__ = InstanceType


def test_mapper():

    map = TypeInterfaceMap()

    assert map[FloatType] == IFloat
    assert map[IntType] == IInt
    assert map[BooleanType] == IBool
    assert map[StringType] == IStr
    assert map[ListType] == ISequence
    assert map[DictType] == IDict

    assert map[InstanceType] == IMyInterface

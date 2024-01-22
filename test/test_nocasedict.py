"""NoCaseDict tests"""

from __future__ import absolute_import
from __future__ import print_function
__license__ = "Cecill-C"
__revision__ = " $Id$ "

from openalea.core.pkgdict import PackageDict


def test_dict():
    """Test packageDict"""
    d = PackageDict()
    d['AbC'] = 3
    assert d['aBc'] == 3
    print(d)


if __name__=="__main__":
    test_dict()

"""lambda tests"""
from __future__ import absolute_import
from __future__ import print_function
from six.moves import range
__license__ = "Cecill-C"
__revision__ = " $Id$ "

from openalea.core.pkgmanager import PackageManager


def _test_lambda():
    """ Test for lambda functions"""
    pm = PackageManager()
    pm.init()

    from . import testnodes
    testnodes.register_packages(pm)

    for t, id, res in (
        ('LambdaFactoriel', 2, 362880),
        ('testlambdaFor', 3, 12),
        ('testlambdaFor', 9, [12, 5]),
        ('testorder', 4, [1., 2.]),
        ('TestLambda', 3, [(x+5)*5 for x in range(10)]),
        ('testlambda2', 10, [x for x in range(10) if x>=2 and x <= 7]),
        ('testlambda3', 3, [[x for x in y if x>=7] for y in [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], \
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], \
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]]),
        ('test_str', 5, ['toto', 'toto']),
        ):

        n = pm.get_node("TestLambda", t)
        n()

        print((n.node(id).get_output(0), res))
        assert n.node(id).get_output(0) == res

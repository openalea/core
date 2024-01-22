# force py3 syntax
from __future__ import absolute_import
import six
try:
    # Python 2: "unicode" is built-in
    six.text_type
except NameError:
    six.text_type = str

from io import open

from os.path import join as pj

from openalea.core.pkgmanager import PackageManager

from .small_tools import ensure_created, rmdir



tmp_dir = 'toto_srcedit'


def setup_function(fun):
    ensure_created(tmp_dir)
    modsrc = \
        """
from openalea.core import *

class MyNode:

    def __init__(self):
        pass


    def __call__(self, inputs):
        return inputs
"""

    with open(pj(tmp_dir, "mymodule.py"), 'w') as f:
        f.write(six.text_type(modsrc))

    wraleasrc = \
        """
from openalea.core import *


def register_packages(pkgmanager):
    metainfo={ }
    package1 = Package("TestPackage", metainfo)

    f = Factory( name= "test",
                 category = "",
                 description = "",
                 nodemodule = "mymodule",
                 nodeclass = "MyNode",

                 )

    package1.add_factory(f)

    pkgmanager.add_package(package1)
"""

    with open(pj(tmp_dir, "my_wralea.py"), 'w') as f:
        f.write(six.text_type(wraleasrc))


def teardown_function(function):
    rmdir(tmp_dir)


def test_srcedit():
    """ Test src edition """

    # Change src
    pm = PackageManager()
    pm.wraleapath = tmp_dir

    pm.init(tmp_dir)
    factory = pm['TestPackage']['test']

    node1 = factory.instantiate()
    assert node1.func((1, 2, 3)) == (1, 2, 3)

    src = factory.get_node_src()
    assert src

    newsrc = src.replace("return inputs", "return sum(inputs)")
    assert newsrc

    factory.apply_new_src(newsrc)
    node2 = factory.instantiate()
    assert node2.func((1, 2, 3)) == 6

    # factory.save_new_src(newsrc)
    #
    # src = factory.get_node_src()
    #
    # # Reinit src
    # pm = PackageManager()
    # pm.wraleapath = '.'
    #
    # pm.init()
    #
    # factory = pm['TestPackage']['test']
    #
    # node = factory.instantiate()
    #
    # assert node(((1, 2, 3), )) == 6

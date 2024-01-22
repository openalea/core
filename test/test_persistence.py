from __future__ import absolute_import
#from nose.tools import with_setup

from openalea.core.pkgmanager import PackageManager
from openalea.core.compositenode import CompositeNodeFactory, CompositeNode

from .small_tools import ensure_created, rmdir
from six.moves import range

tmp_dir = 'toto_persistence'


def setup_function(fun):
    ensure_created(tmp_dir)


def teardown_function():
    rmdir(tmp_dir)


#@with_setup(setup, teardown)
def test_compositenodewriter():
    pm = PackageManager()
    pm.init()

    sg = CompositeNode(inputs=[dict(name="%d" % i) for i in range(3)],
                       outputs=[dict(name="%d" % i) for i in range(4)],
                       )

    # build the compositenode factory
    addid = sg.add_node(pm.get_node("pkg_test", "+"))
    val1id = sg.add_node(pm.get_node("pkg_test", "float"))
    val2id = sg.add_node(pm.get_node("pkg_test", "float"))
    val3id = sg.add_node(pm.get_node("pkg_test", "float"))

    sg.connect(val1id, 0, addid, 0)
    sg.connect(val2id, 0, addid, 1)
    sg.connect(addid, 0, val3id, 0)
    sg.connect(val3id, 0, sg.id_out, 0)
    sgfactory = CompositeNodeFactory("addition")
    sg.to_factory(sgfactory)
    # Package
    metainfo = {'version': '0.0.1',
                'license': 'CECILL-C',
                'authors': 'OpenAlea Consortium',
                'institutes': 'INRIA/CIRAD',
                'description': 'Base library.',
                'url': 'http://openalea.gforge.inria.fr'}

    package1 = pm.create_user_package("MyTestPackage",
                                      metainfo, tmp_dir)
    package1.add_factory(sgfactory)
    assert 'addition' in package1
    package1.write()

    sg = sgfactory.instantiate()

    sg.node(val1id).set_input(0, 2.)
    sg.node(val2id).set_input(0, 3.)

    # evaluation
    sg()
    assert sg.node(val3id).get_output(0) == 5.

    assert len(sg) == 6

    pm.init()
    newsg = pm.get_node('MyTestPackage', 'addition')
    assert len(newsg) == 6


#@with_setup(setup, teardown)
def test_nodewriter():
    """test node writer"""
    pm = PackageManager()
    pm.clear()
    pm.init()

    # Package
    metainfo = {'version': '0.0.1',
                'license': 'CECILL-C',
                'authors': 'OpenAlea Consortium',
                'institutes': 'INRIA/CIRAD',
                'description': 'Base library.',
                'url': 'http://openalea.rtfd.io'}

    package1 = pm.create_user_package("MyTestPackage",
                                      metainfo, tmp_dir)
    assert package1 is not None

    nf = package1.create_user_node(name="mynode",
                                   category='test',
                                   description="descr",
                                   inputs=(),
                                   outputs=(),
                                   )
    package1.write()
    pm.init()
    newsg = pm.get_node('MyTestPackage', 'mynode')
    package1.remove_files()

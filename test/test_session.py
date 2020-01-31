# -*- python -*-
#
#       OpenAlea.Core: OpenAlea Core
#
#       Copyright 2006 INRIA - CIRAD - INRA
#
#       File author(s): Christophe Pradal <christophe.prada@cirad.fr>
#                       Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
"""Test the session"""


__license__ = "Cecill-C"
__revision__ = " $Id$ "

from nose.tools import with_setup
import os

from openalea.core.session import Session
from openalea.core.pkgmanager import PackageManager
from openalea.core.compositenode import CompositeNodeFactory, CompositeNode

from .small_tools import ensure_created, rmdir


tmp_dir = 'toto_session'


def setup():
    ensure_created(tmp_dir)


def teardown():
    rmdir(tmp_dir)


def add_user_class(datapool):
    """ Add an user class to datapool """

    import moduletest
    datapool['j'] = moduletest.test_data()


@with_setup(setup, teardown)
def test_save_datapool():

    asession = Session()
    datapool = asession.datapool

    datapool['i'] = [1, 2, 3]

    add_user_class(datapool)
    asession.save(os.path.join(tmp_dir, 'test.pic'))

    asession.datapool.clear()
    asession.load(os.path.join(tmp_dir, 'test.pic'))

    assert asession.datapool['i'] == [1, 2, 3]


@with_setup(setup, teardown)
def test_save_workspace():
    pm = PackageManager()
    pm.init()

    asession = Session()

    import sys

    sgfactory = CompositeNodeFactory(name="SubGraphExample",
                                description= "Examples",
                                category = "Examples",
                               )
    sg= CompositeNode()
    # build the subgraph factory

    addid = sg.add_node(pm.get_node("pkg_test", "float"))
    sg.to_factory(sgfactory)
    instance = sgfactory.instantiate()

    instance.actor(addid).set_input(0, 3)
    asession.add_workspace(instance)

    asession.save(os.path.join(tmp_dir, 'test.pic'))

    asession.workspaces = []
    asession.load(os.path.join(tmp_dir, 'test.pic'))

    i = asession.workspaces[0]
    assert type(i) == type(instance)
    #assert i.node_id[addid].get_input(0) == 3
#test_save_workspace()

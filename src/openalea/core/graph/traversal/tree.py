# -*- coding: utf-8 -*-
# -*- python -*-
#
#       OpenAlea.Container
#
#       Copyright 2008-2009 INRIA - CIRAD - INRA
#
#       File author(s): Christophe Pradal <christophe.pradal.at.cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################

'''
This module provides different traversal for tree data structure
implemented :class:`openalea.container.interface.tree` interface.
'''

__docformat__ = "restructuredtext"
__license__ = "Cecill-C"
__revision__ = " $Id$ "

from collections import deque

def pre_order(tree, vtx_id, edge_type_property = None):
    '''
    Traverse a tree in a prefix way.
    (root then children)
    Return an iterator on vertices.
    If an edge_type_property is given, visit first branches rather than successor.

    This is a non recursive implementation.
    '''

    if edge_type_property is None:
        yield vtx_id
        for vid in tree.children(vtx_id):
            for node in pre_order(tree, vid):
                yield node
    else:

        # 1. select first '+' edges
        successor = []
        yield vtx_id
        for vid in tree.children(vtx_id):
            if edge_type_property.get(vid) == '<':
                successor.append(vid)
                continue

            for node in pre_order(tree, vid):
                yield node

        # 2. select then '<' edges
        for vid in successor:
            for node in pre_order(tree, vid):
                yield node


def post_order(tree, vtx_id):
    '''
    Traverse a tree in a postfix way.
    (from leaves to root)
    '''
    for vid in tree.children(vtx_id):
        for node in post_order(tree, vid):
            yield node
    yield vtx_id

def level_order(tree, vtx_id):
    ''' Traverse the vertices in a level order.

    Traverse the root node, then its children and so on.
    '''
    queue = deque()
    queue.append(vtx_id)

    while queue:
        vid = queue.popleft()
        yield vid
        queue.extend(tree.children(vid))


def depth_order(tree, vtx_id):
    '''Traverse all the leaves first.
    Then their parent until the root.

    .. todo:: To implement

    '''
    raise NotImplementedError


def traverse_tree(tree, vtx_id, visitor):
    '''
    Traverse a tree in a prefix or postfix way.

    We call a visitor for each vertex.
    This is usefull for printing, cmputing or storing vertices
    in a specific order.

    See boost.graph.
    '''

    yield visitor.pre_order(vtx_id)

    for v in tree.children(vtx_id):
        for res in traverse_tree(tree, v, visitor):
            yield res

    yield visitor.post_order(vtx_id)


class Visitor(object):
    ''' Used during a tree traversal. '''

    def pre_order(self, vtx_id):
        pass

    def post_order(self, vtx_id):
        pass

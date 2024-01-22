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

"""
This module provides several implementation of traversal on a directed graph.
"""

__license__= "Cecill-C"
__revision__=" $Id$ "

from collections import deque

def topological_sort(graph, vtx_id, visited = None):
    '''
    Topolofgical sort of a directed graph implementing the
    :class:`openalea.container.interface.graph.IGraph` interface.
    Return an iterator on the vertices.

    :Parameters:
        - `graph`: a directed graph
        - vtx_id: a vertex_identifier
    
    .. note :: This is a non recursive implementation.
    '''
    if visited is None:
        visited = {}

    yield vtx_id
    visited[vtx_id] = True
    for vid in graph.out_neighbors(vtx_id):
        if vid in visited:
            continue
        for node in topological_sort(graph, vid, visited):
            yield node


def breadth_first_search(graph, vtx_id):
    '''
    Breadth first search of a graph implementing the
    :class:`openalea.container.interface.graph.IGraph` interface.
    Return an iterator on the vertices.

    :Parameters:
        - `graph`: a directed graph
        - vtx_id: a vertex_identifier
    
    .. note :: This is a non recursive implementation.
    '''
    visited = {}

    queue = deque()
    queue.append(vtx_id)

    while queue:
        vid = queue.popleft()
        if vid in visited:
            continue
        yield vid
        visited[vid] = True
        queue.extend(graph.out_neighbors(vid))


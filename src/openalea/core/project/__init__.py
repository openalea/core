# -*- python -*-
#
#       OpenAlea.OALab: Multi-Paradigm GUI
#
#       Copyright 2014 INRIA - CIRAD - INRA
#
#       File author(s): Julien Coste <julien.coste@inria.fr>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################
"""
Working with Project class
--------------------------

You can work directly on project:

    >>> from openalea.core.project import Project, get_project_dir
    >>> from openalea.core.path import path
    >>> # Real work on project:
    >>> project_path = path(get_project_dir()) / 'project1'
    >>> project1 = Project(project_path)
    >>> project1.start()

Change metadata:

    >>> project1.authors = "OpenAlea Consortium and John Doe"
    >>> project1.description = "Test project concept with numpy"
    >>> project1.long_description = ' '.join([
    ... 'This project import numpy. Then, it create and display a numpy eye.',
    ... 'We use it to test concept of Project.'])

... project file, models, ... :

    >>> success = project1.add(category="model", filename="hello.py", content="print('Hello World')")
    >>> project1.description = "This project is used to said hello to everyone"
    >>> startup_obj = project1.add(category="startup", filename="begin_numpy.py", content="import numpy as np")
    >>> model_obj = project1.add(category="model", filename="eye.py", content="print np.eye(2)")
    >>> project1.rename_item("model", "eye.py", "eye_numpy.py")

At this time, project is only in memory. To write it on disk, just call "project1.save()"



Creation and Manipulation with Project Manager
----------------------------------------------

Or, you can create or load a *project* thanks to the *project manager*.
    >>> from openalea.core.project import ProjectManager
    >>> project_manager = ProjectManager()

Discover available projects
    >>> project_manager.discover()
    >>> list_of_projects = project_manager.projects

Create project in default directory or in specific one
    >>> p1 = project_manager.create('project1')
    >>> p2 = project_manager.create(name='project2', projectdir=".")

Load project from default directory
    >>> p3 = project_manager.load('sum')

Load project from a specific directory
    >>> import openalea.oalab
    >>> from openalea.oalab.data import resources_dir
    >>> project_dir = resources_dir
    >>> p4 = project_manager.load('sum', project_dir)

Load
    >>> project2 = project_manager.load("sum")

Run startup
    >>> project2.start()

Get model
    >>> model = project2.get_model("sum_int")

Search other projects
---------------------

To search projects that are not located inside default directories:
    >>> project_manager.repositories.append('/path/to/search/projects') # doctest: +SKIP
    >>> project_manager.discover() # doctest: +SKIP
    >>> list_of_projects = project_manager.projects # doctest: +SKIP

"""
from openalea.core.settings import get_project_dir
from openalea.core.project.project import *

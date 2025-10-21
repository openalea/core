============
Installation
============

First install miniforge following the instructions given
`here <https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html>`_.

Then following openalea package installation process from
`the openalea documentation <https://openalea.readthedocs.io/en/latest/install.html>`_, at the command line::

    $ mamba create -n openalea -c openalea3 -c conda-forge openalea.core


Use
===

Simple usage:

.. code-block:: python

    from openalea.core import *

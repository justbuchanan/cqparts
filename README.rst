
.. image:: https://fragmuffin.github.io/cqparts/media/logo/dark.svg
    :align: center

=====================
What is `cqparts`?
=====================

``cqparts`` is CAD for Python programmers, short for "``cadquery`` parts".

Using ``cqparts`` you can wrap geometry made with ``cadquery`` to build complex
and deeply parametric models.

Full documentation at: https://fragmuffin.github.io/cqparts


Installing
------------------

This fork of the ``cqparts`` has been modified to support `cadquery built on top of pythonOCC <https://github.com/CapableRobot/cadquery>`_, instead of FreeCAD.  All changes are backwards compatible with the the normal cadquery library.

Please see https://github.com/fragmuffin/cqparts for normal installation.  Instructions below are for the pythonOCC version of cadquery.

Pre-requisites
^^^^^^^^^^^^^^^^^^

You'll need to fulfill the requirements of ``cadquery``, the simplest way to do
that is to install ``cadquery`` first by following the instructions here:

https://github.com/CapableRobot/cadquery

Once ``cadquery`` is installed, install ``cqparts`` with::

    git clone https://github.com/CapableRobot/cqparts
    cd cqparts/deployment
    python3 make-setup.py
    cd ../src
    python3 setup.py install

``cqparts_*`` Content Libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also install content libraries with a similar ``pip install`` command.

List available libraries with::

    pip search cqparts-

For example, to install the ``cqparts_bearings`` content library, run::

    pip install cqparts-bearings


_Note_: ``pip`` packages use ``-`` to separate words, but when importing them the
standard ``_`` is used.


Example Usage
-------------------

Here is just one of the simplest examples to give you an idea of what this
library does.

More detailed examples found in
`the official documentation for cqparts <https://fragmuffin.github.io/cqparts/doc>`_.

Wrapping a Cube
^^^^^^^^^^^^^^^^^^

.. image:: https://fragmuffin.github.io/cqparts/media/img/unit-cube.png

A simple cube defined with ``cadquery`` alone::

    # create unit cube solid
    import cadquery
    size = 10
    cube = cadquery.Workplane('XY').box(size, size, size)

    # display cube (optional)
    from Helpers import show
    show(cube)

Wrapping this in a ``cqparts.Part`` object can be done like this::

    # create unit cube as cqparts.Part
    import cadquery
    import cqparts
    from cqparts.params import PositiveFloat

    class MyCube(cqparts.Part):
        size = PositiveFloat(1, doc="cube size")
        def make(self):
            return cadquery.Workplane('XY').box(self.size, self.size, self.size)

    # create cube instance
    cube = MyCube(size=10)

    # display cube (optional)
    from cqparts.display import display
    display(cube)

You can see that under the bonnet (in the ``make`` function) the geometry is
created with ``cadquery``, but the resulting ``MyCube`` class is instantiated
more intuitively, and more object orientated.


Creating a Hierarchy
^^^^^^^^^^^^^^^^^^^^^^

``cqparts`` can also be used to create a deep hierarchy of *parts* and
*assemblies* to build something deeply complicated and entirely parametric.

A simple example of this is the
`toy car tutorial <https://fragmuffin.github.io/cqparts/doc/tutorials/assembly.html>`_.

.. image:: https://fragmuffin.github.io/cqparts/media/img/toy-car.png


``cqparts`` Capabilities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The work done in ``cqparts_fasteners`` is a good example of how useful
``cqparts`` wrapping can be; read about the ``Fastener`` class, how it works,
and what can be done with it in the
`cqparts_fasteners docs <https://fragmuffin.github.io/cqparts/doc/cqparts_fasteners/index.html>`_

.. image:: https://fragmuffin.github.io/cqparts/media/img/nut-bolt-fastener.png


Contributing
-----------------

Issues, and Pull Requests are encouraged, and happily received, please read
`CONTRIBUTING.md <https://github.com/fragmuffin/cqparts/blob/master/CONTRIBUTING.md>`_
for guidance on how to contribute.

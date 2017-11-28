import cadquery
import six

from .params import ParametricObject, Boolean
from .utils.misc import indicate_last, property_buffered
from .errors import MakeError, ParameterError

from .utils.geometry import copy as copy_wp


class Component(ParametricObject):
    pass


class Part(Component):
    simple = Boolean(False, doc="if set, simplified geometry is built")

    def __init__(self, *largs, **kwargs):
        super(Part, self).__init__(*largs, **kwargs)
        # Initializing Instance State
        self._local_obj = None
        self._world_coords = None
        self._world_obj = None

    def make(self):
        """
        Create and return solid part

        :return: cadquery.Workplane of the part in question
        :rtype: subclass of :class:`cadquery.CQ`, usually a :class:`cadquery.Workplane`

        .. important::
            This must be overridden in your ``Part``

        The outcome of this function should be accessed via cqparts.Part.object
        """
        raise NotImplementedError("make function not implemented")

    def make_simple(self):
        """
        Create and return *simplified* solid part.

        The simplified representation of a ``Part`` is to lower the export
        quality of an ``Assembly`` or ``Part`` for rendering.

        Overriding this is optional, but highly recommended.

        The default behaviour returns the full complexity object's bounding box.
        But to do this, theh full complexity object must be generated first.

        There are 2 main problems with this:

        #. building the full complexity part is not efficient.
        #. a bounding box may not be a good representation of the part.

        **Bolts**

        A good example of this is a bolt.

        * building a bolt's thread is not a trivial task;
          it can take some time to generate.
        * a box is not a good visual representation of a bolt

        So for the ``Fastener`` parts, all ``make_primative`` methods are overridden
        to provide 2 cylinders, one for the bolt's head, and another for the thread.
        """
        complex_obj = self.make()
        bb = complex_obj.findSolid().BoundingBox()
        simple_obj = cadquery.Workplane('XY', origin=(bb.xmin, bb.ymin, bb.zmin)) \
            .box(bb.xlen, bb.ylen, bb.zlen, centered=(False, False, False))
        return simple_obj

    # ----- Local Object
    @property
    def local_obj(self):
        """
        Buffered result of :meth:`cqparts.Part.make` which is (probably) a
        :class:`cadquery.Workplane` instance.

        .. note::
            This is usually the correct way to get your part's object
            for rendering, exporting, or measuring.

            Only call :meth:`cqparts.Part.make` directly if you explicitly intend
            to re-generate the model from scratch, then dispose of it.
        """
        if self._local_obj is None:
            # Simplified or Complex
            if self.simple:
                value = self.make_simple()
            else:
                value = self.make()
            # Verify type
            if not isinstance(value, cadquery.CQ):
                raise MakeError("invalid object type returned by make(): %r" % value)
            # Buffer object
            self.local_obj = value
        return self._local_obj

    @local_obj.setter
    def local_obj(self, value):
        self._local_obj = value
        self._world_obj = None

    # ----- World Object
    @property
    def world_obj(self):
        """
        The :meth:`local_obj` object in the :meth:`world_coords` coordinate
        system.

        .. note:

            This is automatically copied and moved when either :meth:`local_obj`
            or :meth:`world_coords` are set, and neither are ``Null``.
        """
        if self._world_obj is None:
            local_obj = self.local_obj
            world_coords = self.world_coords
            if all(x is not None for x in (local_obj, world_coords)):
                # TODO: copy and move self.local_obj to use self.world_coords
                self._world_obj = copy_wp(local_obj)
        return self._world_obj

    @world_obj.setter
    def world_obj(self, value):
        raise ValueError("can't set world_obj directly, set local_obj instead")

    @property
    def bounding_box(self):
        """
        Generate a bounding box based on the full complexity part.

        :return: bounding box of part
        :rtype: cadquery.BoundBox
        """
        return self.local_obj.findSolid().BoundingBox()

    # -------------- Part Placement --------------
    @property
    def world_coords(self):
        """
        :return: coordinate system in the world, None until placed
        :rtype: :class:`cadquery.Plane`
        """
        return self._world_coords

    @world_coords.setter
    def world_coords(self, value):
        """
        Set part's placement in word coordinates (as a :class:`cadquery.Plane`)
        """
        self._world_coords = value
        self._world_obj = None

    def __copy__(self):
        new_obj = super(Part, self).__copy__()

        if 'object' in self.__dict__:  # set by property_buffered
            new_obj.__dict__['object'] = self.__dict__['object'].translate((0, 0, 0))
        if 'object_primative' in self.__dict__:  # set by property_buffered
            new_obj.__dict__['object_primative'] = self.__dict__['object_primative'].translate((0, 0, 0))

        return new_obj


class Assembly(Component):
    """
    An assembly is a group of parts, and other assemblies (called components)
    """

    def __init__(self, *largs, **kwargs):
        super(Assembly, self).__init__(*largs, **kwargs)
        self._components = None

    def make(self):
        """
        Create and return components dict (must be overridden in inheriting class)

        :return: {<name>: <Part or Assembly instance>, ...}
        :rtype: dict

        """
        raise NotImplementedError("make function not implemented")

    @property
    def components(self):
        if self._components is None:
            self._components = self.make()
            # verify
            if not isinstance(self._components, dict):
                raise MakeError(
                    "invalid type returned by make(): %r (must be a dict)" % self._components
                )
            else:
                for (name, component) in self._components.items():
                    if not isinstance(name, six.string_types) or not isinstance(component, Component):
                        raise MakeError((
                            "invalid component returned by make(): (%r, %r) "
                            "(must be a (str, Component))"
                        ) % (name, component))

        return self._components

    def clear(self):
        """
        Clear internal object reference; forces object to be re-made when
        self.object is next referenced.
        """
        self._components = None

    def find(self, keys, index=0):
        """
        Find a nested Assembly or Part by a '.' separated list of names.
        for example:

        ::

            >>> motor.find('bearing.outer_ring')

        would return the Part instance of the motor bearing's outer ring.
        whereas:

        ::

            >>> bearing = motor.find('bearing')
            >>> ring = bearing.find('inner_ring')  # equivalent of 'bearing.inner_ring'

        does much the same thing, bearing is an Assembly, and ring is a Part

        :param keys: key hierarchy. ``'a.b'`` is equivalent to ``['a', 'b']``
        :type keys: str or list
        :param index: index of keys list (used internally)
        :type index: int
        """

        if isinstance(keys, six.string_types):
            keys = [k for k in search_str.split('.') if k]
        if index >= len(keys):
            return self

        key = keys[index]
        if key in self.components:
            component = self.components[key]
            if isinstance(component, Assembly):
                return component.find(keys, index=(index + 1))
            elif index == len(keys) - 1:
                # this is the last search key; component is a leaf, return it
                return component
            else:
                raise AssemblyFindError(
                    "could not find '%s' (invalid type at [%i]: %r)" % (
                        '.'.join(keys), index, component
                    )
                )
        else:
            raise AssemblyFindError(
                "could not find '%s', '%s' is not a component of %r" % (
                    '.'.join(keys), key, self
                )
            )

    # Component Tree
    def tree_str(self, prefix_str=''):
        """
        Return string listing recursively the assembly hierarchy
        """
        output = ''
        for (is_last, (name, component)) in indicate_last(sorted(self.components.items(), key=lambda x: x[0])):
            branch_chr = u'\u2514' if is_last else u'\u251c'
            if isinstance(component, Assembly):
                # Assembly: also list nested components
                output += prefix_str + ' ' + branch_chr + u'\u2500 ' + name + '\n'
                output += component.tree_str(
                    prefix_str=(prefix_str + (u'    ' if is_last else u' \u2502  '))
                )
            else:
                # Part (assumed): leaf node
                output += prefix_str + ' ' + branch_chr + u'\u25cb ' + name + '\n'
        return output

    def print_tree(self):
        print(repr(self))
        print(self.tree_str())


class Pulley(Part):

    # Parameter Defaults
    radius = 20.0
    width = 3.0  # contact area (not including wall thickness)
    wall_height = 1
    wall_width = 1
    hole_radius = 3.175
    key_intrusion = 0.92

    def make(self):
        # Pulley Base
        pulley_half = cadquery.Workplane("XY") \
            .circle(self.radius + self.wall_height).extrude(self.wall_width) \
            .faces(">Z").workplane() \
            .circle(self.radius).extrude(self.width / 2.0)

        # Hole
        pulley_half = pulley_half.faces(">Z").workplane() \
            .moveTo(self.hole_radius - self.key_intrusion, self.hole_radius) \
            .lineTo(0.0, self.hole_radius) \
            .threePointArc(
                (-self.hole_radius, 0.0), (0.0, -self.hole_radius)
            ) \
            .lineTo(self.hole_radius - self.key_intrusion, -self.hole_radius) \
            .close() \
            .cutThruAll()

        # Mirror half to create full pulley
        pulley = pulley_half.translate((0, 0, 0))  # copy
        pulley = pulley.union(
            pulley.translate((0, 0, 0)).mirror(
                'XY', basePointVector=(0, 0, self.wall_width + (self.width / 2.0))
            ),
        )

        return pulley

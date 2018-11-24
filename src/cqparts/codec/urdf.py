# note: lxml is not installed by default
from lxml import etree

from . import Exporter, register_exporter
from .. import Component, Part, Assembly

import logging
log = logging.getLogger(__name__)


@register_exporter('urdf', Component)
class URDFExporter(Exporter):
    
    def __init__(self, *args, **kwargs):
        super(URDFExporter, self).__init__(*args, **kwargs)

    def __call__(self, filename='model.urdf'):
        e = etree.Element('robot')

        e.attrib['name'] = 'my_robot_1'

        counter = 0

        def add(obj, parentXmlNode, keypath=''):
            nonlocal counter
            if isinstance(obj, Assembly):
                subkeypath = keypath + '_' if keypath else ''
                for name, subAsm in obj.components.items():
                    add(subAsm, parentXmlNode, keypath=subkeypath+name)
            else: # Part
                counter += 1
                ee = etree.SubElement(parentXmlNode, 'link', {
                    'name': keypath,
                    })

                inertial = etree.SubElement(ee, 'inertial')
                etree.SubElement(inertial, 'mass', {
                    'value': str(0.12345)
                })
                etree.SubElement(inertial, 'origin', {
                    'xyz': "0.00457048841401063 0.0962524890074447 0.00395442197852662",
                    'rpy': "0 0 0",
                })
                etree.SubElement(inertial, 'inertia', {
                    'ixx': "0.0123841200738068",
                    'ixy': "0.000187984913202718",
                    'ixz': "1.32683892634266E-06",
                    'iyy': "7.01690345033619E-05",
                    'iyz': "-9.17416945099381E-05",
                    'izz': "0.0123862261905615",
                })

                visual = etree.SubElement(ee, 'visual')
                etree.SubElement(visual, 'origin', {
                    'xyz': "0.00457048841401063 0.0962524890074447 0.00395442197852662",
                    'rpy': "0 0 0",
                })
                visual_geometry = etree.SubElement(visual, 'geometry')
                etree.SubElement(visual_geometry, 'mesh', {
                    'filename': "package://edo_sim/meshes/link_3.STL",
                })
                visual_material = etree.SubElement(visual, 'material', {
                    'name': "" # TODO: ?
                })
                etree.SubElement(visual_material, 'color', {
                    'rgba': "0.792156862745098 0.819607843137255 0.933333333333333 1",
                })

                collision = etree.SubElement(ee, 'collision')
                etree.SubElement(collision, 'origin', {
                    'xyz': "0.00457048841401063 0.0962524890074447 0.00395442197852662",
                    'rpy': "0 0 0",
                })
                collision_geometry = etree.SubElement(collision, 'geometry')
                etree.SubElement(collision_geometry, 'mesh', {
                    'filename': "package://edo_sim/meshes/link_3.STL",
                })

        add(self.obj, e)

        tree = etree.ElementTree(e)
        tree.write(filename, pretty_print=True)

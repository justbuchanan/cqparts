import xml.etree.ElementTree as ET

from . import Exporter, register_exporter
from .. import Component, Part, Assembly

import logging
log = logging.getLogger(__name__)


@register_exporter('urdf', Component)
class URDFExporter(Exporter):
    
    def __init__(self, *args, **kwargs):
        super(URDFExporter, self).__init__(*args, **kwargs)

    def __call__(self, filename='model.urdf'):
        e = ET.Element('robot')

        e.attrib['name'] = 'my_robot_1'

        tree = ET.ElementTree(e)
        tree.write(filename)

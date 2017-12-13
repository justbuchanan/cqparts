import base64

from . import Exporter, register_exporter
from .. import __version__
from ..part import Component, Part, Assembly


@register_exporter('gltf', Component)
class GLTFExporter(Exporter):
    pass


TEMPLATE = {
    "asset": {
        "generator": "cqparts_%s" % __version__,
        "version": "2.0"  # glTF version
    },
    "scene": 0,
    "scenes": [{"nodes": [0]}],
    "nodes": [
        # https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#nodes-and-hierarchy
        {
            "children": [
                1
            ],
            # TOOD: add scale + translation
            "matrix": [
                1.0, 0.0, 0.0, 0.0,
                0.0, 0.0,-1.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 1.0,
            ],
        },
        {
            "mesh": 0,
        },
    ],
    "meshes": [
        {
            "primitives": [
                {
                    "attributes": {
                        "NORMAL": 1,
                        "POSITION": 2,
                    },
                    "indices": 0,
                    "mode": 4,
                    "material": 0,
                }
            ],
            "name": "Mesh",
        }
    ],
    "accessors": [
        {
            "bufferView": 0,
            "byteOffset": 0,
            "componentType": 5123,
            "count": 36,
            "max": [23],
            "min": [0],
            "type": "SCALAR",
        },
        {
            "bufferView": 1,
            "byteOffset": 0,
            "componentType": 5126,
            "count": 24,
            "max": [1.0, 1.0, 1.0],
            "min": [-1.0, -1.0, -1.0],
            "type": "VEC3",
        },
        {
            "bufferView": 1,
            "byteOffset": 288,
            "componentType": 5126,
            "count": 24,
            "max": [0.5, 0.5, 0.5],
            "min": [-0.5, -0.5, -0.5],
            "type": "VEC3",
        },
    ],
    "materials": [
        {
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.8, 0.0, 0.0, 1.0],  # rbta
                "metallicFactor": 0.0,
            },
            "name": "Red",
        },
    ],
    "bufferViews": [
        {
            "buffer": 0,
            "byteOffset": 576,
            "byteLength": 72,
            "target": 34963,
        },
        {
            "buffer": 0,
            "byteOffset": 0,
            "byteLength": 576,
            "byteStride": 12,
            "target": 34962,
        },
    ],
    "buffers": [
        {
            "byteLength": 648,
            "uri": "Box0.bin",
        },
    ],
}

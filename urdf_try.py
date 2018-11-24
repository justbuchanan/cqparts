#!/usr/bin/env python3

import os

from tests.partslib import Box, CubeStack
from tests.partslib import SimpleCar

modelDir = 'urdfout'
urdfFile = os.path.join(modelDir, 'car.urdf')

model = SimpleCar()
model.exporter('urdf')(
    filename=urdfFile
)
print("Exported {!r}".format(urdfFile))

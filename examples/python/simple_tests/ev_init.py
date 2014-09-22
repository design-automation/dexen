"""
Generates 100 random individuals.
"""

from dexen_libs.api import data_api
import random

for i in range(100):
    data_object = data_api.DataObject()
    data_object.set_value("alive", True)
    data_object.set_value("genotype", [random.random() for _ in range(10)])
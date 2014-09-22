"""
Reads the file. Uses the value to set the score.
"""

from dexen_libs.api import data_api

data_objects = data_api.GetAssignedDataObjects()

for do in data_objects:
    phenotype = do.get_value("phenotype")
    do.set_value("score", phenotype)

"""
This is a test
"""

from dexen_libs.api import data_api

data_objects = data_api.GetAssignedDataObjects()

for do in data_objects:
	do.set_value("phenotype", "asdfgh")

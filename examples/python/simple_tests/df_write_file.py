"""
Adds up the genes.

The condition for this task is as follows:

{
"genotype": { "$exists" : true },
"phenotype": { "$exists" : false }
}

"""
from bson.binary import Binary
from dexen_libs.api import data_api

data_objects = data_api.GetAssignedDataObjects()

for do in data_objects:
    genotype = do.get_value("genotype")
    phenotype = str(sum(genotype))
    do.set_value("phenotype", Binary(phenotype))
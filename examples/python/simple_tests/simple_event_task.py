"""
This is a test
"""

from dexen_libs.moea.executors import (
    initialize)

from dexen_libs.moea.individual import (
    ALIVE,
    GENOTYPE,
    PHENOTYPE,
    GeneFloatRange,
    GeneIntRange,
    GeneIntChoice,
    GeneStringChoice,
    GenotypeMeta)


genotype_meta = GenotypeMeta()
genotype_meta.append([GeneFloatRange(0,10) for i in range(1,10)])

initialize(genotype_meta = genotype_meta, initial_pop_size = 100)
# ==================================================================================================
#
#    Copyright (c) 2008, Patrick Janssen (patrick@janssen.name)
#
#    This file is part of Dexen.
#
#    Dexen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Dexen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Dexen.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
# https://code.google.com/p/ecspy/source/browse/trunk/ecspy/benchmarks.py

import math
import random

def ackley(genotype):
    """
    Defines the Ackley benchmark problem.
    """
    dimensions = len(genotype)
    fitness = -20 * math.exp(-0.2 * math.sqrt(1.0 / dimensions * \
        sum([x**2 for x in genotype]))) - math.exp(1.0 / dimensions * \
        sum([math.cos(2 * math.pi * x) for x in genotype])) + 20 + math.e
    return fitness

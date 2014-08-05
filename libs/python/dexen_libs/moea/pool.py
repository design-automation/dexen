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

"""
Pool 
Represents a pool of individuals that could be either a population or some 
sub-groups within the population.
"""
import random

from dexen_libs.api import data_api
from dexen_libs.moea.individual import Individual

from dexen_libs.feedback.fitness import fitness
from dexen_libs.feedback.selection import select

# A pool of individuals
class Pool(object):

    #constructor
    def __init__(self):
        self.inds = []

    #get inds from the input
    def initialize_assigned_inds(self):
        self.inds = []
        data_objects = data_api.GetAssignedDataObjects()
        for data_object in data_objects:
            ind = Individual(data_object)
            self.inds.append(ind)

    #creare a new set of inds
    def initialize_new_inds(self, genotype_meta, pop_size):
        self.inds = []
        for _ in range(pop_size):
            ind = Individual()
            ind.randomize_genotype(genotype_meta) #random genes
            self.inds.append(ind)

    # calculate fitness values for each ind
    def calculate_fitness(self, scores_meta, fitness_type):
        fitness(self.inds, scores_meta, fitness_type)

    # create new individuals
    # this resorts the list of inds
    def birth(self, genotype_meta, num_births, crossover_prob, mutation_prob, selection_type):
        # make sure we have an even number of births
        if num_births % 2 != 0:
            if num_births == 1:
                num_births == 2
            else:
                num_births = num_births - 1
        # select parents
        parents = select(self.inds, num_births, selection_type)
        assert len(parents) % 2 == 0
        random.shuffle(parents)
        for i in range(0, len(parents), 2):
            child1, child2 = parents[i].reproduce(genotype_meta, parents[i+1], crossover_prob, mutation_prob)
            self.inds.append(child1)
            self.inds.append(child2)

    # kill individuals
    # this resorts the list of inds
    def death(self, num_deaths, selection_type):
        inds_to_kill = select(self.inds, num_deaths, selection_type)
        for ind_to_kill in inds_to_kill:
            ind_to_kill.kill()



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
Executor classes used for executing tasks.
"""
from dexen_libs.moea.individual import Individual
from dexen_libs.moea.pool import Pool
from dexen_libs.moea.individual import ALIVE, GENOTYPE, PHENOTYPE


class Condition(object):
    def __init__(self):
        self.selectors = {}
    def exists(self, name):
        self.selectors[name] = { "$exists" : True }
        return self
    def not_exists(self, name):
        self.selectors[name] = { "$exists" : False }
        return self
    def equals(self, name, value):
        self.selectors[name] = value
        return self
    def not_equals(self, name, value):
        self.selectors[name] = { "$ne" : value }
        return self
    def get(self):
        return self.selectors

def initialize(genotype_meta, initial_pop_size):
    print "Executing initialization"
    #create a new population
    initial_pop = Pool()
    initial_pop.initialize_new_inds(genotype_meta, initial_pop_size)

def develop(func, **kwargs):
    print "Executing development"
    #create the input pool
    input_pool = Pool()
    input_pool.initialize_assigned_inds()
    #develop each ind
    for ind in input_pool.inds:
        ind.set_phenotype(func(ind, **kwargs))
            
def evaluate(func, score_names, **kwargs):
    print "Executing evaluation "
    #create the input pool
    input_pool = Pool()
    input_pool.initialize_assigned_inds()
    #evaluate each ind
    for ind in input_pool.inds:
        score_values = func(ind, score_names, **kwargs) 
        assert len(score_names) == len(score_values)
        for score_name, score_value in zip(score_names, score_values):
            ind.set_evaluation_score(score_name, score_value)

def feedback(genotype_meta, scores_meta, fitness_type, 
    births_select_type, deaths_select_type, num_births, num_deaths, 
    mutation_prob, crossover_prob):
    print "Executing feedback"
    #create the input pool
    input_pool = Pool()
    input_pool.initialize_assigned_inds()
    #assign a fitness to each ind
    input_pool.calculate_fitness(scores_meta, fitness_type)
    #kill inds
    input_pool.death(num_deaths, deaths_select_type)
    #reproduce inds
    #this adds new inds to the pool (new inds with no fitness)
    input_pool.birth(
        genotype_meta, num_births, 
        crossover_prob, mutation_prob, births_select_type)



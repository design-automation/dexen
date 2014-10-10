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
'''
Individual
Represents a solution to the problem being optimised.
'''
import random
import pickle

from dexen_libs.api import data_api

ALIVE = "alive"
GENOTYPE = "genotype"
PHENOTYPE = "phenotype"
ID = "_id"

class GeneMeta(object):
    def __init__(self):
        self.value = None
    def randomize():
        raise NonImplementedError()
        
class GeneFloatRange(GeneMeta):
    def __init__(self, min, max):
        self.min = min
        self.max = max
    def randomize(self): 
        self.value = random.uniform(self.min,self.max)
        
class GeneIntRange(GeneMeta):
    def __init__(self, min, max):
        self.min = min
        self.max = max
    def randomize(self): 
        self.value = random.randint(self.min,self.max)
        
class GeneIntChoice(GeneMeta):
    def __init__(self, choices):
        self.choices = choices
    def randomize(self):
        self.value = random.choice(self.choices)

class GeneStringChoice(GeneMeta):
    def __init__(self, choices):
        self.choices = choices
    def randomize(self):
        self.value = random.choice(self.choices)
        
class GenotypeMeta(object):
    """
    A set of gene meta objects.
    Used for working with genotypes.
    """
    def __init__(self):
        self.gene_metas = []
    def append(self, gene_metas):
        if hasattr(gene_metas, '__iter__'):
            for gene_meta in gene_metas:
                self.gene_metas.append(gene_meta)
        else:
            self.gene_metas.append(gene_metas)
    def set_values(self, values):
        assert len(self.gene_metas) == len(values)
        for gene_meta, value in zip(self.gene_metas, values):
            gene_meta.value = value
    def get_values(self):
        return [gene_meta.value for gene_meta in self.gene_metas]
    def randomize(self):
        for gene_meta in self.gene_metas:
            gene_meta.randomize()
        return self.get_values()
    def mutate(self, values, mutation_prob):
        self.set_values(values)
        for gene_meta in self.gene_metas:
            if random.random() < mutation_prob:
                gene_meta.randomize()       
        return self.get_values()
    def mutate_one(self, values):
        self.set_values(values)
        index = random.randrange(len(values))
        self.gene_metas[index].randomize()       
        return self.get_values()

class Individual(object):
    """
    An individual.
    The constructor can be called with or without a mongodb data object.
    If data_object is None, then a new data object will be created.
    When the object is instanntiated, only the 'alive' attribute is 
    created.
    """
    #constructor
    def __init__(self, data_object=None):
        if data_object is not None:
            self.data_object = data_object
        else:
            self.data_object = data_api.DataObject() #mongodb
            self.live()
                    
    #randomize genotype
    def randomize_genotype(self, genotype_meta):
        self.set_genotype(genotype_meta.randomize())

    #crossover method for creating children
    def _crossover(self, ind, prob):
        child1 = Individual()
        child2 = Individual() 
        parent1_genotype = self.get_genotype()
        parent2_genotype = ind.get_genotype()
        genotype_length = len(parent1_genotype)
        cross_point = None
        if prob > 0 and random.random() < prob:
            child1.genotype = []
            child2.genotype = []
            if genotype_length == 2:
                cross_point = 1
            else:
                cross_point = random.randint(1, genotype_length-2)
            for i in range(cross_point):
                child1.genotype.append(parent1_genotype[i])
                child2.genotype.append(parent2_genotype[i])
            for i in range(cross_point, genotype_length):
                child1.genotype.append(parent2_genotype[i])
                child2.genotype.append(parent1_genotype[i])
        else:
            child1.genotype = list(parent1_genotype)
            child2.genotype = list(parent2_genotype)
        return child1, child2, cross_point
        
    #mutation method for creating children
    def _mutate(self, genotype_meta, mutation_prob):
        self.set_genotype(genotype_meta.mutate(self.genotype, mutation_prob))
        
    #mutation method that mutates one gene
    def _mutate_one(self, genotype_meta):
        self.set_genotype(genotype_meta.mutate_one(self.genotype))

    #reproduction method for creating children
    def reproduce(self, genotype_meta, ind, crossover_prob, mutation_prob):
        # crossover
        child1, child2, cross_point = self._crossover(ind, crossover_prob)
        # mutation
        mutations1  = child1._mutate(genotype_meta, mutation_prob)
        mutations2  = child2._mutate(genotype_meta, mutation_prob)

        #if nothing has changed, then mutate one random gene to avoid 
        #children that are duplicates
        if not (cross_point or mutations1):
            child1._mutate_one(genotype_meta)
        if not (cross_point or mutations2):
            child2._mutate_one(genotype_meta)

        #return the children
        return  child1, child2
    
    #ALIVE
    
    #kill method for killing an individual
    def kill(self):
        self.alive = False
        self.data_object.set_value(ALIVE, False)
        
    #kill method for making sure that an ind is alive
    def live(self):
        self.alive = True
        self.data_object.set_value(ALIVE, True)
        
    #alive method
    def is_alive(self):
        if not hasattr(self, ALIVE):
            alive = self.data_object.get_value(ALIVE)
            setattr(self, ALIVE, alive)
        return getattr(self, ALIVE)

    #GENOTYPE

    #set the genotype and save to db
    def set_genotype(self, genotype):
        setattr(self, GENOTYPE, genotype)
        self.data_object.set_value(GENOTYPE, genotype) 
            
    #get genotype
    def get_genotype(self):
        if not hasattr(self, GENOTYPE):
            genotype = self.data_object.get_value(GENOTYPE)
            setattr(self, GENOTYPE, genotype)
        return getattr(self, GENOTYPE)
        
    #get a str rep of the genotype
    def get_genotype_str(self, ndigits=2):
        genotype = self.get_genotype()
        if ndigits != None:
            return " ".join(map(lambda x: str(round(x,ndigits)), genotype))
        else:
            return " ".join(map(lambda x: str(x), genotype))

    #PHENOTYPE

    #set the phenotype and save to db
    def set_phenotype(self, phenotype):
        setattr(self, PHENOTYPE, phenotype)
        self.data_object.set_value(PHENOTYPE, phenotype)

    #get phenotype
    def get_phenotype(self):
        if not hasattr(self, PHENOTYPE):
            #phenotype = pickle.loads(str(self.data_object.get_value(PHENOTYPE))) #TODO: check if this is the best way
            phenotype = self.data_object.get_value(PHENOTYPE)
            setattr(self, PHENOTYPE, phenotype)
        return getattr(self, PHENOTYPE)
        
    #EVALUATION SCORES

    #set the evaluation_score and save to db
    def set_evaluation_score(self, name, value):
        setattr(self, name, value)
        self.data_object.set_value(name, value)
    
    #get evaluation_score 
    def get_evaluation_score(self, name):
        if not hasattr(self, name):
            value =  self.data_object.get_value(name)
            setattr(self, name, value)
        return getattr(self, name)
    
    #check if all scores exist (even if value is None)
    def is_fully_evaluated(self, score_names):
        for score_name in score_names:
            value = self.get_evaluation_score(score_name)
            if value is None:                                 #TODO: check if this works... does it return None if the score name does not exist
                return False
        return True

    #get the id of this individual
    def get_id(self):
        if not hasattr(self, ID):
            id = self.data_object.get_value(ID)
            setattr(self, ID, id)
        return getattr(self, ID)


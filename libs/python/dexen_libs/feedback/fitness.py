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
A library of functions to used to calculate normalized fitness. 

When normalizing the rankings, all ranks are inmcremented by 1, so that the lowest rank is 1 rather 
than 0. This is to ensure that no individual gets zero fitness. (If everything has a rank of 0, 
then it would result in a div by 0 error.)

These functions do not return anything. They only add a fitness attribute to each individual. 
For golberg ranking and fonseca flemming ranking, other attributes are also added (rank_g and 
rank_ff respectively). The ind list that is passed in is not sorted according to fitness. 
"""

import random

from ranking import (
    ScoreMeta, 
    ScoresMeta, 
    MIN, MAX,
    rank_goldberg,
    rank_fonseca_flemming,
    rank_multi)

#constants
SINGLE_CRITERIA = 0
SINGLE_CRITERIA_RANKING = 1
PARETO_MULTI_RANKING = 2
PARETO_GOLDBERG_RANKING = 3
PARETO_FONSECA_FLEMMING_RANKING = 4

# select the fitness method
def fitness(inds, scores_meta, fitness_type, normalize=False):
    assert isinstance(scores_meta, ScoresMeta)
    assert fitness_type in [
        SINGLE_CRITERIA, 
        SINGLE_CRITERIA_RANKING, 
        PARETO_MULTI_RANKING, 
        PARETO_GOLDBERG_RANKING, 
        PARETO_FONSECA_FLEMMING_RANKING]
    if fitness_type == SINGLE_CRITERIA:
        single_criteria(inds, scores_meta, normalize)
    elif fitness_type == SINGLE_CRITERIA_RANKING:
        single_criteria_ranking(inds, scores_meta, normalize)
    elif fitness_type == PARETO_MULTI_RANKING: 
        fitness_multi(inds, scores_meta, normalize)
    elif fitness_type == PARETO_GOLDBERG_RANKING:
        fitness_goldberg(inds, scores_meta, normalize)
    elif fitness_type == PARETO_FONSECA_FLEMMING_RANKING:
        fitness_fonseca_flemming(inds, scores_meta, normalize)

# simple fitness - single criteria
def single_criteria(inds, scores_meta, normalize):
    score_meta = scores_meta[0]
    inds = list(inds) #shallow copy
    if normalize:
        score_sum = float(sum([i.get_evaluation_score(score_meta.name) for i in inds]))
    else:
        score_sum = 1
    # add fitness
    if score_meta.opt_type == MIN:
        inds.sort(key=lambda ind: ind.get_evaluation_score(score_meta.name))
        max_score = inds[-1].get_evaluation_score(score_meta.name)
        for ind in inds:
            ind.fitness = (max_score - ind.get_evaluation_score(score_meta.name)) / score_sum
    else: # score_type == "MAX"
        inds.sort(key=lambda ind: ind.get_evaluation_score(score_meta.name), reverse=True)
        for ind in inds:
            ind.fitness = ind.get_evaluation_score(score_meta.name) / score_sum

# simple fitness - ranking based on a single criteria
def single_criteria_ranking(inds, scores_meta, normalize):
    score_meta = scores_meta[0]
    inds = list(inds) #shallow copy
    if normalize:
        score_sum = float(len(inds))
    else:
        score_sum = 1
    # add fitness
    if score_meta.opt_type == MIN:
        inds.sort(key=lambda ind: ind.get_evaluation_score(score_meta.name))
    else: # score_type == "MAX"
        inds.sort(key=lambda ind: ind.get_evaluation_score(core_meta.name), reverse=True)
    for index, ind in enumerate(inds):
        ind.fitness = (len(inds) - index) / score_sum

# pareto ranking method that uses rank_g
def fitness_goldberg(inds, scores_meta, normalize):
    ranked = rank_goldberg(inds, scores_meta)
    min_score = ranked[0].rank
    max_score = ranked[-1].rank
    if normalize:
        score_sum = float(sum([i.rank + 1 for i in inds]))
    else:
        score_sum = 1
    for ind in ranked:
        rank = ind.rank
        ind.fitness = (max_score - ind.rank + 1) / score_sum

# pareto ranking method that uses rank_ff
def fitness_fonseca_flemming(inds, scores_meta, normalize):
    ranked = rank_fonseca_flemming(inds, scores_meta)
    min_score = ranked[-1].rank
    max_score = ranked[0].rank
    if normalize:
        score_sum = float(sum([i.rank + 1 for i in inds]))
    else:
        score_sum = 1    
    for ind in ranked:
        ind.fitness = (ind.rank + 1) / score_sum

# pareto ranking method that uses both rank_g and rank_ff
def fitness_multi(inds, scores_meta, normalize):
    ranked = rank_multi(inds, scores_meta)
    min_score = ranked[0].rank
    max_score = ranked[-1].rank
    if normalize:
        score_sum = float(sum([i.rank + 1 for i in inds]))
    else:
        score_sum = 1   
    for ind in ranked:
        rank = ind.rank
        ind.fitness = (ranked[-1].rank - ind.rank + 1) / score_sum

#===============================================================================
# Testing
#===============================================================================
def main():

    class Ind(object):
        def __init__(self, id, scoreA, scoreB):
            self.id = id
            self.scoreA = scoreA
            self.scoreB = scoreB

        def get_id(self):
            return self.id

        def get_evaluation_score(self, name):
            return getattr(self, name)

        def __repr__(self, *args, **kwargs):
            return str(self.id) + " (" + str(self.scoreA) + "," + str(self.scoreB) + ")"

    def printRankResult(inds):
        print "ID (scoreA, scoreB) RANK: rank, FIT: fitness"
        for ind in inds:
            if hasattr(ind, "rank_g"):
                rank_g = ind.rank_g
            else:
                rank_g = "None"
            if hasattr(ind, "rank_ff"):
                rank_ff = ind.rank_ff
            else:
                rank_ff = "None"
            print str(ind), "RANK:", rank_g, rank_ff, "FIT: ", ind.fitness

    def test_all_five(inds, scores_meta, normalize=True): 
        from copy import deepcopy as dc

        #SINGLE_CRITERIA
        print "SINGLE_CRITERIA"
        indsA = dc(inds) #deep copy
        fitness(indsA, scores_meta, SINGLE_CRITERIA, normalize)
        printRankResult(indsA)

        #SINGLE_CRITERIA_RANKING
        print "SINGLE_CRITERIA_RANKING"
        indsB = dc(inds) #deep copy
        fitness(indsB, scores_meta, SINGLE_CRITERIA_RANKING,normalize)
        printRankResult(indsB)

        #PARETO_GOLDBERG_RANKING
        print "PARETO_GOLDBERG_RANKING"
        inds1 = dc(inds) #deep copy
        fitness(inds1, scores_meta, PARETO_GOLDBERG_RANKING, normalize)
        printRankResult(inds1)
        
        #PARETO_FONSECA_FLEMMING_RANKING
        print "PARETO_FONSECA_FLEMMING_RANKING"
        inds2 = dc(inds) #deep copy
        fitness(inds2, scores_meta, PARETO_FONSECA_FLEMMING_RANKING, normalize)
        printRankResult(inds2)

        #PARETO_MULTI_RANKING
        print "PARETO_MULTI_RANKING"
        inds3 = dc(inds) #deep copy
        fitness(inds3, scores_meta, PARETO_MULTI_RANKING, normalize)
        printRankResult(inds3)

        print "================="


    print "Starting testing"
       
    inds = [
        Ind(0,11,28),
        Ind(1,24,37),
        Ind(2,94,10),
        Ind(3,25,29),
        Ind(4,79,34),
        Ind(5,43,22),
        Ind(6,66,98),
        Ind(7,90,33),
        Ind(8,25,60),
        Ind(9,54,34)
    ] 

    #SINGLE_CRITERIA
    #SINGLE_CRITERIA_RANKING
    #PARETO_GOLDBERG_RANKING
    #PARETO_FONSECA_FLEMMING_RANKING
    #PARETO_MULTI_RANKING

    print "=== MINIMIZE ==="
    scores_meta = ScoresMeta()
    scores_meta.append(ScoreMeta("scoreA", MIN))
    scores_meta.append(ScoreMeta("scoreB", MIN))

    test_all_five(inds, scores_meta, normalize=True)
    test_all_five(inds, scores_meta, normalize=False)

if __name__ == "__main__":
    main()
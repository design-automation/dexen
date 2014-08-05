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
A library of ranking functions to used to assign fitness. These functions do 
not return anything. They only add 
a fitness attribute to each individual. For golberg ranking and fonseca 
flemming ranking, other attributes are also added (rank_g and rank_ff 
respectively). The ind list that is passed in is not sorted according to 
fitness. 
"""
import random

from dexen_libs.feedback.ranking import (
    ScoreMeta, 
    ScoresMeta, 
    MIN, MAX,
    ParetoRankingGoldberg,
    ParetoRankingFonsecaFlemming,
    MultiRanking)

#constants
SINGLE_CRITERIA = "single_criteria"
SINGLE_CRITERIA_RANKING = "single_criteria_ranking"
PARETO_MULTI_RANKING = "pareto_multi_ranking"
PARETO_GOLDBERG_RANKING = "pareto_goldberg_ranking"
PARETO_FONSECA_FLEMMING_RANKING = "pareto_fonseca_flemming_ranking"

# select the fitness method
def fitness(inds, scores_meta, fitness_type):
    assert isinstance(scores_meta, ScoresMeta)
    fitness_type = fitness_type.lower()
    assert fitness_type in [
        SINGLE_CRITERIA, 
        SINGLE_CRITERIA_RANKING, 
        PARETO_MULTI_RANKING, 
        PARETO_GOLDBERG_RANKING, 
        PARETO_FONSECA_FLEMMING_RANKING]
    if fitness_type == SINGLE_CRITERIA:
        single_criteria(inds, scores_meta)
    elif fitness_type == SINGLE_CRITERIA_RANKING:
        single_criteria_ranking(inds, scores_meta)
    elif fitness_type == PARETO_MULTI_RANKING: 
        pareto_multi_ranking(inds, scores_meta)
    elif fitness_type == PARETO_GOLDBERG_RANKING:
        pareto_goldberg_ranking(inds, scores_meta)
    elif fitness_type == PARETO_FONSECA_FLEMMING_RANKING:
        pareto_fonseca_flemming_ranking(inds, scores_meta)

# simple fitness - single criteria
def single_criteria(inds, scores_meta):
    score_meta = scores_meta[0]
    inds = list(inds) #shallow copy
    # add fitness
    if score_meta.opt_type == MIN:
        inds.sort(key=lambda ind: getattr(ind, score_meta.name))
        max_score = getattr(inds[-1], score_meta.name)
        min_score = getattr(inds[0], score_meta.name)
        for ind in inds:
            ind.fitness = min_score + (max_score - getattr(ind, score_meta.name))
    else: # score_type == "MAX"
        inds.sort(key=lambda ind: getattr(ind, score_meta.name), reverse=True)
        for ind in inds:
            ind.fitness = getattr(ind, score_meta.name)

# simple fitness - ranking based on a single criteria
def single_criteria_ranking(inds, scores_meta):
    score_meta = scores_meta[0]
    inds = list(inds) #shallow copy
    # add fitness
    if score_meta.opt_type == MIN:
        inds.sort(key=lambda ind: getattr(ind, score_meta.name))
    else: # score_type == "MAX"
        inds.sort(key=lambda ind: getattr(ind, score_meta.name), reverse=True)
    for index, ind in enumerate(inds):
        ind.fitness = len(inds) - index

# pareto ranking method that uses both rank_g and rank_ff
def pareto_multi_ranking(inds, scores_meta):
    # rank individuals using both methods
    p_ranking = MultiRanking(inds, scores_meta)
    ranked = p_ranking.rank() 
    inds_fits = []
    for index, r_ind in enumerate(ranked):
        rank_g = r_ind.rank_g
        rank_ff = r_ind.rank_ff
        ind = r_ind.ind
        ind.fitness = len(ranked) - index
        ind.rank_g = rank_g
        ind.rank_ff = rank_ff
        inds_fits.append(ind)

# pareto ranking method that uses rank_g
def pareto_goldberg_ranking(inds, scores_meta):
    # rank individuals using goldberg method
    p_ranking = ParetoRankingGoldberg(inds, scores_meta)
    ranked = p_ranking.rank()
    inds_fits = []
    for index, r_ind in enumerate(ranked):
        rank = r_ind.rank
        ind = r_ind.ind
        ind.fitness = ranked[-1].rank - rank
        ind.rank_g = rank
        inds_fits.append(ind)

# pareto ranking method that uses rank_ff
def pareto_fonseca_flemming_ranking(inds, scores_meta):
    # rank individuals using goldberg method
    p_ranking = ParetoRankingFonsecaFlemming(inds, scores_meta)
    ranked = p_ranking.rank()
    inds_fits = []
    for index, r_ind in enumerate(ranked):
        rank = r_ind.rank
        ind = r_ind.ind
        ind.fitness = r_ind.rank
        ind.rank_ff = r_ind.rank
        inds_fits.append(ind)

#===============================================================================
# Testing
#===============================================================================
def main():
    print "Starting testing"

    #create score metas
    sm1 = ScoreMeta("a", MIN)
    sm2 = ScoreMeta("b", MAX)
    scores_meta = ScoresMeta()
    scores_meta.append(sm1)
    scores_meta.append(sm2)

    #create some inds
    class Ind(object):
        def __init__(self, id, a, b):
            self.id = id
            self.a = a
            self.b = b
        def is_fully_evaluated(self, _):
            return True
    inds = [
        Ind(0,1,2),
        Ind(1,2,3),
        Ind(2,9,1),
        Ind(3,2,2),
        Ind(4,7,3),
        Ind(5,4,2),
        Ind(6,6,9),
        Ind(7,0,3),
        Ind(8,2,6),
        Ind(9,5,3)
    ] 

    #do the ranking
    #SINGLE_CRITERIA
    #SINGLE_CRITERIA_RANKING
    #PARETO_MULTI_RANKING
    #PARETO_GOLDBERG_RANKING
    #PARETO_FONSECA_FLEMMING_RANKING
    ranked = fitness(inds, scores_meta, SINGLE_CRITERIA)
    print "\nSINGLE_CRITERIA"
    print "  id score fitness"
    for ind in inds:
        print " ", ind.id, "", ind.a, "   ", ind.fitness
    
    ranked = fitness(inds, scores_meta, SINGLE_CRITERIA_RANKING)
    print "\nSINGLE_CRITERIA_RANKING"
    print "  id score fitness"
    for ind in inds:
        print " ", ind.id, "", ind.a, "   ", ind.fitness

    ranked = fitness(inds, scores_meta, PARETO_GOLDBERG_RANKING)
    print "\nARETO_GOLDBERG_RANKING"
    print "  id score score fitness"
    for ind in inds:
        print " ", ind.id, "", ind.a, "   ", ind.b, "   ", ind.fitness

    ranked = fitness(inds, scores_meta, PARETO_FONSECA_FLEMMING_RANKING)
    print "\nPARETO_GOLDBERG_RANKING"
    print "  id score score fitness"
    for ind in inds:
        print " ", ind.id, "", ind.a, "   ", ind.b, "   ", ind.fitness

    ranked = fitness(inds, scores_meta, PARETO_MULTI_RANKING)
    print "\nPARETO_MULTI_RANKING"
    print "  id score score fitness"
    for ind in inds:
        print " ", ind.id, "", ind.a, "   ", ind.b, "   ", ind.fitness

if __name__ == "__main__":
    main()
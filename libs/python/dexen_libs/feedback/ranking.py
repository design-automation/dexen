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
A library of Pareto ranking functions. These functions add attributes to the inds in the list, 
and return a new list sorted in rank order. 
"""

MIN = 0
MAX = 1

class ScoreMeta(object):
    def __init__(self, name, opt_type):
        assert opt_type in [MIN,MAX]
        self.name = name
        self.opt_type = opt_type
    def is_minimize(self):
        return self.opt_type == MIN
    def is_maximize(self):
        return self.opt_type == MAX

class ScoresMeta(object):
    def __init__(self):
        self.scores = []
    def append(self, score):
        self.scores.append(score)
    def names(self):
        return [score.name for score in self.scores]
    def opt_types(self):
        return [score.opt_type for score in self.scores]
    def __getitem__(self,index):
        return self.scores[index]

def _dominates(ind1, ind2, scores_meta):
    equal = True
    for score_meta in scores_meta.scores:
        val1 = ind1.get_evaluation_score(score_meta.name)
        val2 = ind2.get_evaluation_score(score_meta.name)
        if val1 != val2: equal = False
        if score_meta.is_minimize():
            if val2 < val1:
                return False
        elif val2 > val1:
            return False
    if equal: return False
    return True

def _on_pareto_front(ind, inds, scores_meta):
    for ind2 in inds:
        if ind2.get_id() != ind.get_id(): #TODO - check if this equality check works
            if _dominates(ind2, ind, scores_meta):
                return False
    return True

def _extract_pareto_front(inds, scores_meta):
    pareto_front = []
    non_pareto_front = []
    for ind in inds:    
        if _on_pareto_front(ind, inds, scores_meta):
            pareto_front.append(ind)
        else:
            non_pareto_front.append(ind)
    return pareto_front, non_pareto_front            

def rank_goldberg(inds, scores_meta, max_level=None):
    inds = list(inds)
    rank = 0
    cnt = 0
    ranked = []        
    while len(inds) > 0:
        pareto_front, non_pareto_front = _extract_pareto_front(inds, scores_meta)
        for ind in pareto_front:
            ind.rank = rank
            ind.rank_g = rank
            ranked.append(ind)
        inds = non_pareto_front
        cnt +=1
        rank += 1
        if max_level and cnt == max_level: break
    return ranked

def rank_fonseca_flemming(inds, scores_meta, max_level=None):
    inds = list(inds)
    rank = 1
    cnt = 0
    ranked = []        
    for ind1 in inds:
        rank = 0;
        for ind2 in inds:
            if _dominates(ind1, ind2, scores_meta):
                rank += 1
                if rank == max_level:
                    break
        ind1.rank = rank
        ind1.rank_ff = rank
        ranked.append(ind1)
    # sort the ranking from highest to lowest
    ranked.sort(key=lambda ind: ind.rank, reverse=True)
    return ranked

def rank_multi(inds, scores_meta, max_level=None):
    ranked = list(inds)
    ranked = rank_goldberg(ranked, scores_meta)
    ranked = rank_fonseca_flemming(ranked, scores_meta)
    ff_max = ranked[0].rank

    ranked.sort(key=lambda ind: (ind.rank_g, ff_max - ind.rank_ff))
    counter = 0
    ranked[0].rank = 0
    for i in range(1, len(ranked)):
        ind = ranked[i]
        prev_ind = ranked[i-1]
        if ind.rank_g != prev_ind.rank_g or ind.rank_ff != prev_ind.rank_ff:
            counter += 1            
        ind.rank = counter
    return ranked

#===============================================================================
# Testing
#===============================================================================

def main():

    import random
        
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

    def printRankResult(ranked):
        print "ID (scoreA, scoreB) RANK: rank"
        for ind in ranked:
            print ind, "RANK:", ind.rank

    def printMultiRankResult(ranked):
        print "ID (scoreA, scoreB) RANK: rank, g_rank, ff_rank"
        for ind in ranked:
            #print ind, "RANK:", ind.rank, "(", ind.rank_g, ind.rank_ff, ind.rank_ff_rev, ")"
            print ind, "\t", "RANK:", ind.rank, "(", ind.rank_g, ind.rank_ff, ")"

    def test_all_three(inds, scores_meta):

        #ParetoRankingGoldberg
        print "ParetoRankingGoldberg"
        ranked = rank_goldberg(inds, scores_meta)
        printRankResult(ranked)
        
        #ParetoRankingFonsecaFlemming
        print "ParetoRankingFonsecaFlemming"
        ranked = rank_fonseca_flemming(inds, scores_meta)
        printRankResult(ranked)

        #MultiRanking
        print "MultiRanking"
        ranked = rank_multi(inds, scores_meta)
        printMultiRankResult(ranked)

        print "================="
    
    def get_inds():
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
        return inds

    def get_rand_inds(num):
        inds = []
        for i in range(num):
            inds.append(Ind(i, random.random(), random.random()))
        return inds

    print "Starting testing"
    inds = get_inds()
    #inds = get_rand_inds(20)

    print "=== MINIMIZE ==="
    scores_meta = ScoresMeta()
    scores_meta.append(ScoreMeta("scoreA", MIN))
    scores_meta.append(ScoreMeta("scoreB", MIN))

    test_all_three(inds, scores_meta)

    print "=== MAXIMIZE ==="
    scores_meta_max = ScoresMeta()
    scores_meta_max.append(ScoreMeta("scoreA", MAX))
    scores_meta_max.append(ScoreMeta("scoreB", MAX))

    test_all_three(inds, scores_meta_max)

if __name__ == "__main__":
    main()
    





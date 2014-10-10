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
A library of classes for performing various kinds of Pareto ranking.
"""

MIN = "min"
MAX = "max"

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

class RankingResult(object):
    def __init__(self, ind, rank):
        self.ind = ind
        self.rank = rank
        
class MultiRankingResult(object):
    def __init__(self, ind, rank_g, rank_ff):
        self.ind = ind
        self.rank_g = rank_g
        self.rank_ff = rank_ff

class ParetoRanking(object):
    def __init__(self, inds, scores_meta):
        self.inds = inds
        self.scores_meta = scores_meta
        self.unranked = []
    
    def set_inds(self, inds):
        self.inds = inds
    
    def get_fully_evaluated_inds(self):
        inds = []
        for ind in self.inds:    
            if self._is_fully_evaluated(ind):
                inds.append(ind)
        return inds

    def _dominates(self, ind1, ind2):
        equal = True
        for score_meta in self.scores_meta.scores:
            val1 = getattr(ind1, score_meta.name)
            val2 = getattr(ind2, score_meta.name)
            if val1 != val2: equal = False
            if score_meta.is_minimize():
                if val2 < val1:
                    return False
            elif val2 > val1:
                return False
        if equal: return False
        return True

    def _is_fully_evaluated(self, ind):
        return ind.is_fully_evaluated(self.scores_meta.names())

class ParetoRankingGoldberg(ParetoRanking):
    
    def _on_pareto_front(self, ind, inds):
        for ind2 in inds:
            if ind2.get_id() != ind.get_id(): #TODO - check if this equality check works
                if self._dominates(ind2, ind):
                    return False
        return True

    def _extract_pareto_front(self, inds):
        pareto_front = []
        non_pareto_front = []
        for ind in inds:    
            if self._on_pareto_front(ind, inds):
                pareto_front.append(ind)
            else:
                non_pareto_front.append(ind)
        return pareto_front, non_pareto_front            

    def rank(self, max_level=None):
        rank = 0
        cnt = 0
        ranked = []        
        inds = []
        for ind in self.inds:    
            if self._is_fully_evaluated(ind):
                inds.append(ind)
        while len(inds) > 0:
            pareto_front, non_pareto_front = self._extract_pareto_front(inds)
            #print "pareto", len(pareto_front), "non pareto", len(non_pareto_front)
            for ind in pareto_front:
                ranked.append(RankingResult(ind, rank))
            inds = non_pareto_front
            cnt +=1
            rank += 1
            if max_level and cnt == max_level: break
        self.unranked = inds
        return ranked

class ParetoRankingFonsecaFlemming(ParetoRanking):

    def rank(self, max_level=None):
        rank = 1
        cnt = 0
        ranked = []        
        inds = []
        for ind in self.inds:    
            if self._is_fully_evaluated(ind):
                inds.append(ind)

        for ind1 in inds:
            rank = 0;
            for ind2 in inds:
                if self._dominates(ind1, ind2):
                    rank += 1
                    if rank == max_level:
                        break
            ranked.append(RankingResult(ind1, rank))
        # sort the ranking from highest to lowest
        ranked.sort(key=lambda result: result.rank, reverse=True)
        self.unranked = inds
        return ranked

class MultiRanking(object):

    def __init__(self, inds, scores_meta):
        self.ranking_g = ParetoRankingGoldberg(inds, scores_meta)
        self.ranking_ff = ParetoRankingFonsecaFlemming(inds, scores_meta)

    def rank(self, max_level=None):
        ranked_g = self.ranking_g.rank(max_level)
        ranked_ff = self.ranking_ff.rank(max_level)
        ff_max = ranked_ff[0].rank
        ranked = []
        for g, ff in zip(ranked_g, ranked_ff):
            ind = g.ind
            rank_g = g.rank
            rank_ff = ff.rank
            ranked.append(MultiRankingResult(ind, rank_g, rank_ff))
        ranked.sort(key=lambda result: (result.rank_g, ff_max - result.rank_ff))
        return ranked

#===============================================================================
# Testing
#===============================================================================

import random
    
class TestInd(object):
    def __init__(self, id, scoreA, scoreB):
        self.id = id
        self.scoreA = scoreA
        self.scoreB = scoreB

    def is_fully_evaluated(self, score_names):
        return True

    def get_id(self):
        return self.id

    def __repr__(self, *args, **kwargs):
        return str(self.scoreA) + ", " + str(self.scoreB) 


def printRankResult(rank_result):
    assert isinstance(rank_result, RankingResult)
    print rank_result.ind, ", ", rank_result.rank 

def printMultiRankResult(rank_result):
    assert isinstance(rank_result, MultiRankingResult)
    print rank_result.ind, ", ", rank_result.rank_g, ", ", rank_result.rank_ff


def main():
    print "Starting testing"
    import time
    
    inds = []
    for _ in xrange(10):
        inds.append(TestInd(random.randint(1, 100), random.randint(1, 100)))
    #inds.append(TestInd(25,95))
    #inds.append(TestInd(50,50))
    #inds.append(TestInd(90,20))

    scores_meta = ScoresMeta()
    scores_meta.append(ScoreMeta("scoreA", MIN))
    scores_meta.append(ScoreMeta("scoreB", MIN))
    ranking = ParetoRankingGoldberg(inds, scores_meta)

    stime = time.time()
    ranked = ranking.rank(max_level = None)
    
    for rank_result in ranked:
        printRankResult(rank_result)
    
    print time.time() - stime, " seconds"
    print "================="


if __name__ == "__main__":
    main()
    





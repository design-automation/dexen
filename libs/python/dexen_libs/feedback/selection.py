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
A library of selection functions.
Assumes that ind objects have an attribute called 'fitness'.
"""
import random

#constants
RANDOMLY = "randomly"
OLDEST = "oldest"
YOUNGEST = "youngest"
BEST = "best"
WORST = "worst"
ROULETTE_BEST = "roulette_best"
ROULETTE_WORST = "roulette_worst"
TOURNAMENT_BEST = "tournament_best"
TOURNAMENT_WORST = "tournament_worst"
TOURNAMENT_RTS_BEST = "tournament_rts_best"
TOURNAMENT_RTS_WORST = "tournament_rts_worst"

# select 
def select(inds, num, selection_type):
    selection_type = selection_type.lower()
    #================================================
    if selection_type == RANDOMLY:
        return randomly(inds, num)
    #================================================
    elif selection_type == OLDEST:
        return oldest(inds, num)
    elif selection_type == YOUNGEST:
        return youngest(inds, num)
    #================================================
    elif selection_type == BEST:
        return best(inds, num)
    elif selection_type == WORST:
        return worst(inds, num)
    #================================================
    elif selection_type == ROULETTE_BEST:
        return roulette(inds, num)
    elif selection_type == ROULETTE_WORST:
        return roulette(inds, num, select_best=False)
    #================================================
    elif selection_type.startswith(TOURNAMENT_BEST):
        words = selection_type.split(":")                                       #TODO: explain these strings
        if len(words) != 2:
            print "ERROR: Selection type for TOURNAMENT_BEST is incorrect."
            raise Exception()
        tournament_size = int(words[1])
        return tournament(inds, num, tournament_size)
    elif selection_type.startswith(TOURNAMENT_WORST):
        words = selection_type.split(":")
        if len(words) != 2:
            print "ERROR: Selection type for TOURNAMENT_WORST is incorrect."
            raise Exception()
        tournament_size = int(words[1])
        return tournament(inds, num, tournament_size, select_best=False)
    #================================================
    elif selection_type.startswith(TOURNAMENT_RTS_BEST):
        words = selection_type.split(":")
        if len(words) != 3:
            print "ERROR: Selection type for TOURNAMENT_RTS_BEST is incorrect."
            raise Exception()
        window_size = int(words[1])
        tournament_size = int(words[2])
        return tournament_rts(inds, num, window_size, tournament_size)
    elif selection_type.startswith(TOURNAMENT_RTS_WORST):
        words = selection_type.split(":")
        if len(words) != 3:
            print "ERROR: Selection type for TOURNAMENT_RTS_WORST is incorrect."
            raise Exception()
        window_size = int(words[1])
        tournament_size = int(words[2])
        return tournament_rts(inds, num, window_size, tournament_size, select_best=False)
    #================================================
    else:
        print "ERROR: Selection type is not recognised: "+selection_type
        raise Exception()

# select oldest individuals
def oldest(inds, num):
    inds.sort(key=lambda ind: ind._get_id())
    return inds[-num:]

# select youngest individuals
def youngest(inds, num):
    inds.sort(key=lambda ind: ind._get_id())
    return inds[:num]

# select randomly individuals
def randomly(inds, num):
    random.shuffle(inds)
    return inds[:num]

# select best individuals
def best(inds, num):
    inds.sort(key=lambda ind: ind.fitness)
    return inds[:num]
    
# select worst individuals
def worst(inds, num):
    inds.sort(key=lambda ind: ind.fitness)
    return inds[-num:]
    
# select using roulette 
def roulette(inds, num,  select_best=True):
    fits = [ind.fitness for ind in inds]
    min_fit = min(fits)
    max_fit = max(fits)
    fit_range = max_fit - min_fit
    if select_best:
        normalised_fits = [(fit - min_fit)/float(fit_range) for fit in fits]
    else:
        normalised_fits = [1 - ((fit - min_fit)/float(fit_range)) for fit in fits] 
    sum_normalised_fits = sum(normalised_fits)
    wheel_spins = [random.random() * sum_normalised_fits for _ in range(num)]
    selected = []
    for wheel_spin in wheel_spins:
        for ind, normalised_fit in zip(inds, normalised_fits):
            wheel_spin -= normalised_fit
            if wheel_spin <= 0:
                selected.append(ind)
                break
    if len(selected) != num:
        print "ERROR: Wrong number of inds selected. Total selected =  ", len(selected)
        raise Exception()
    return selected

# select using tournament
def tournament(inds, num, tournament_size, select_best=True):
    selected = []
    for _ in range(num):
        random.shuffle(inds)
        tournament = inds[:size]
        tournament.sort(key=lambda ind: ind.fitness, reverse=True)
        if select_best:
            selected.append(tournament[0])
        else:
            selected.append(tournament[-1])
    if len(selected) != num:
        print "ERROR: Wrong number of inds selected. Total selected =  ", len(selected)
        raise Exception()
    return selected

# select using tournament with restricted tournament selection
# TODO : fix the distance metric
def tournament_rts(inds, num, window_size, tournament_size, select_best=True):
    assert(window_size > tournament_size)
    # divide into new and old
    inds.sort(key=lambda ind: ind._get_id())
    new_inds = inds[-num:]
    old_inds = inds[:-num]
    # select inds
    selected = []
    for new_ind in new_inds:
        # window - sort based on distance
        random.shuffle(old_inds)
        window = old_inds[:window_size]
        for old_ind in window:
            new_genotype = [gene.value for gene in new_ind.genotype]
            old_genotype = [gene.value for gene in old_ind.genotype]
            # TODO: this distance metric only works in some cases
            old_ind.dist = sum([abs(pair[0]-pair[1]) for pair in zip(old_genotype, new_genotype)])
        window.sort(key=lambda ind: ind.dist)
        # tournament - sort based on fitness
        tournament = old_inds[:tournament_size] + [new_ind]
        tournament.sort(key=lambda ind: ind.fitness, reverse=True)
        if select_best:
            selected_ind = tournament[0]
        else:
            selected_ind = tournament[-1]
        # add the ind to the list and remove it so that it is not selected twice
        selected.append(selected_ind)
        try:
            old_inds.remove(selected_ind)
        except:
            pass
    if len(selected) != num:
        print "ERROR: Wrong number of inds selected. Total selected =  ", len(selected)
        raise Exception()
    return selected

#===============================================================================
# Testing
#===============================================================================
def main():
    print "Starting testing"

    
if __name__ == "__main__":
    main()
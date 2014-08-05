"""
All settings for the evolutionary algorithm.
"""
from dexen_ea.individual import (
    ALIVE,
    GENOTYPE,
    PHENOTYPE,
    GeneFloatRange,
    GeneIntRange,
    GeneIntChoice,
    GeneStringChoice,
    GenotypeMeta)

from dexen_ea.executors import Condition

from feedback.ranking import (
    MIN, MAX,
    ScoreMeta,
    ScoresMeta)

from feedback.fitness import (
    SINGLE_CRITERIA, 
    SINGLE_CRITERIA_RANKING, 
    PARETO_MULTI_RANKING, 
    PARETO_GOLDBERG_RANKING, 
    PARETO_FONSECA_FLEMMING_RANKING)

from feedback.selection import (
    RANDOMLY,
    OLDEST, YOUNGEST, 
    BEST, WORST,
    ROULETTE_BEST, ROULETTE_WORST,
    TOURNAMENT_BEST, TOURNAMENT_WORST,
    TOURNAMENT_RTS_BEST, TOURNAMENT_RTS_WORST)

#GENERAL
VERBOSE = False
POP_SIZE = 100
MAX_BIRTHS = 10000 #not used at the moment

#STRING CONSTANTS
INITIALIZE = "initialize"
DEVELOP = "develop"
EVALUATE_AREA = "evaluate_area"
EVALUATE_VOLUME = "evaluate_volume"
FEEDBACK = "feedback"
AREA_SCORE = "score_area"
VOLUME_SCORE = "score_volume"

#TASK COMMAND LINE ARGS
INITIALIZE_ARGS = ["python", "tasks.py", INITIALIZE]
DEVELOP_ARGS = ["python", "tasks.py", DEVELOP]
EVALUATE_AREA_ARGS = ["python", "tasks.py", EVALUATE_AREA]
EVALUATE_VOLUME_ARGS = ["python", "tasks.py", EVALUATE_VOLUME]
FEEDBACK_ARGS = ["python", "tasks.py", FEEDBACK]

#TASK INPUT SIZES
DEVELOP_INPUT_SIZE = 50
EVALUATE_AREA_INPUT_SIZE = 50
EVALUATE_VOLUME_INPUT_SIZE = 50
FEEDBACK_INPUT_SIZE = 20

#TASK CONDITIONS
DEVELOP_COND = Condition().exists(GENOTYPE).not_exists(PHENOTYPE).get()
EVALUATE_AREA_COND = Condition().exists(PHENOTYPE).not_exists(AREA_SCORE).get()
EVALUATE_VOLUME_COND = Condition().exists(PHENOTYPE).not_exists(VOLUME_SCORE).get()
FEEDBACK_COND = Condition().exists(AREA_SCORE).exists(VOLUME_SCORE).equals(ALIVE,True).get()

#FEEDBACK TASK SETTINGS
FITNESS_TYPE = PARETO_MULTI_RANKING
BIRTHS_SELECT_TYPE = ROULETTE_BEST
DEATHS_SELECT_TYPE = WORST
NUM_BIRTHS = 2
NUM_DEATHS = 2
MUTATION_PROB = 0.1
CROSSOVER_PROB = 0.9

#META INFO FOR GENOTYPE
genotype_meta = GenotypeMeta()
genotype_meta.append([GeneFloatRange(0,10) for i in range(1,2)])
genotype_meta.append([GeneIntRange(2,15) for i in range(2,3)])
genotype_meta.append([GeneIntChoice([8,10,12,14,16,18]) for i in range(3,4)])

#META INFO FOR SCORES
scores_meta = ScoresMeta()
scores_meta.append(ScoreMeta(AREA_SCORE,MIN))
scores_meta.append(ScoreMeta(VOLUME_SCORE,MAX))
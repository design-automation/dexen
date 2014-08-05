"""
All settings for the evolutionary algorithm.
"""
from dexen_ea.individual import Individual

from dexen_ea.executors import (
    InitializeExecutor, 
    EvaluateExecutor, 
    FeedbackExecutor)

from dexen_ea.individual import (
    ALIVE, 
    MIN, MAX, 
    GENOTYPE)

from selectors.fitness import (
    SINGLE_CRITERIA, 
    SINGLE_CRITERIA_RANKING, 
    PARETO_MULTI_RANKING, 
    PARETO_GOLDBERG_RANKING, 
    PARETO_FONSECA_FLEMMING_RANKING)

from selectors.selection import (
    RANDOMLY,
    OLDEST, YOUNGEST, 
    BEST, WORST
    ROULETTE_BEST, ROULETTE_WORST,
    TOURNAMENT_BEST, TOURNAMENT_WORST,
    TOURNAMENT_RTS_BEST, TOURNAMENT_RTS_WORST)

from dexen_ea.benchmarks import ackley

#CONSTANTS
INITIALIZE = "initialize"
EVALUATE = "evaluate"
FEEDBACK = "feedback"
SCORE = "score"

#GENERAL
verbose = False
max_births = 10000 #not used at the moment

#GENOTYPE TEMPLATE
genotype_template = [GeneFloatRange(0,10) for i in range(0,1)]

#SCORE INFO DICTS
EVAL_FUNC_INFO = {SCORE:MIN}

#INITIALIZE TASK
initialize_executor = InitializeExecutor(
    name = "Initialize Task"
    ind_class = ackley
    genotype_template = genotype_template, 
    initial_pop_size = 100)
 
#EVALUATION TASKS
evaluate_executor = EvaluateExecutor(
    name = "Evaluate Task",
    input_size = 10,
    scores_info=EVAL_FUNC_INFO,
    eval_func = ackley)

#FEEDBACK
feedback_executor = FeedbackExecutor(
    name = "Feedback Task",
    feedback_input_size=20, 
    scores_infos = [EVAL_FUNC_INFO],
    feedback_fitness_type=PARETO_MULTI_RANKING, 
    feedback_births_select_type=ROULETTE_BEST, 
    feedback_deaths_select_type=WORST, 
    feedback_num_births=2, 
    feedback_num_deaths=2, 
    feedback_mutation_prob=0.1, 
    feedback_crossover_prob=0.9)


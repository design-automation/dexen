"""
All tasks used by this evo algorithm
"""
import sys
import settings as ss

from dexen_ea.individual import (
    ALIVE, 
    GENOTYPE, PHENOTYPE)

from dexen_ea.executors import (
    initialize, 
    develop, 
    evaluate,
    feedback)

def develop_simple_model(ind):
    genotype = ind.get_genotype() #mongodb
    return [genotype[0], genotype[1], genotype[2]]

def evaluate_area(ind, score_names):
    phenotype = ind.get_phenotype() #mongodb
    width = phenotype[0]
    length = phenotype[1]
    height = phenotype[2]
    area = (2 * length * width) + (2 * length * height) + (2 * height * width)
    return [area]

def evaluate_volume(ind, score_names):
    phenotype = ind.get_phenotype() #mongodb
    width = phenotype[0]
    length = phenotype[1]
    height = phenotype[2]
    volume = length * width * height
    return [volume]

def main(task_name):
    #------------------------------------------------------------------------------
    #INITIALIZE TASK
    #------------------------------------------------------------------------------
    if task_name == ss.INITIALIZE:
        if ss.VERBOSE:
            print "Initialize task creating individuals "
        initialize(genotype_meta = ss.genotype_meta, initial_pop_size = ss.POP_SIZE)
    #------------------------------------------------------------------------------
    #DEVELOPMENT TASK
    #------------------------------------------------------------------------------
    elif task_name == ss.DEVELOP:
        if ss.VERBOSE:
            print "Develop task processing individuals "
        develop(func = develop_simple_model)
    #------------------------------------------------------------------------------
    #EVALUATION TASK 1
    #------------------------------------------------------------------------------
    elif task_name == ss.EVALUATE_AREA:
        if ss.VERBOSE:
            print "Evaluate area task processing individuals "
        evaluate(func = evaluate_area, score_names = [ss.AREA_SCORE])
    #------------------------------------------------------------------------------    
    #EVALUATION TASK 2
    #------------------------------------------------------------------------------
    elif task_name == ss.EVALUATE_VOLUME:
        if ss.VERBOSE:
            print "Evaluate volume task processing individuals "
        evaluate(func = evaluate_volume, score_names = [ss.VOLUME_SCORE])
    #------------------------------------------------------------------------------
    #FEEDBACK
    #------------------------------------------------------------------------------
    elif task_name == ss.FEEDBACK:
        if ss.VERBOSE:
            print "Feedback task processing individuals "
        feedback(
            genotype_meta = ss.genotype_meta,
            scores_meta = ss.scores_meta,
            fitness_type = ss.FITNESS_TYPE, 
            births_select_type = ss.BIRTHS_SELECT_TYPE, 
            deaths_select_type = ss.DEATHS_SELECT_TYPE, 
            num_births = ss.NUM_BIRTHS,  
            num_deaths = ss.NUM_DEATHS,  
            mutation_prob = ss.MUTATION_PROB,  
            crossover_prob = ss.CROSSOVER_PROB)

if __name__ == '__main__':
    try:
        sys.argv[1]
    except NameError:
        print "Missing command line arg; you need to specify the task name."
        raise
    else:
        task_name = sys.argv[1]
        if not task_name in [ss.INITIALIZE, ss.DEVELOP, ss.EVALUATE_AREA, ss.EVALUATE_VOLUME, ss.FEEDBACK]:
            print "The task name is invalid."
            raise
        main(task_name)
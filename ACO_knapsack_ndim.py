
import warnings
import copy
from inspyred import ec
from inspyred.ec import emo
from inspyred.ec import selectors
from inspyred import swarm
import itertools
import math
import random
from random import Random
from time import time
import math
import inspyred
import numpy
import numpy as np
from get_problem import get_problem

class Benchmark(object):
    def __init__(self, dimensions, objectives=1):
        self.dimensions = dimensions
        self.objectives = objectives
        self.bounder = None
        self.maximize = True

    def __str__(self):
        if self.objectives > 1:
            return '{0} ({1} dimensions, {2} objectives)'.format(self.__class__.__name__, self.dimensions,
                                                                 self.objectives)
        else:
            return '{0} ({1} dimensions)'.format(self.__class__.__name__, self.dimensions)

    def __repr__(self):
        return self.__class__.__name__

    def generator(self, random, args):
        """The generator function for the benchmark problem."""
        raise NotImplementedError

    def evaluator(self, candidates, args):
        """The evaluator function for the benchmark problem."""
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        candidate = [a for a in args]
        fit = self.evaluator([candidate], kwargs)
        return fit[0]

class Knapsack(Benchmark):

    def __init__(self, capacity, items, duplicates=False):
        Benchmark.__init__(self, len(items))
        self.capacity = capacity
        self.items = items
        self.components = [swarm.TrailComponent((item[0:-1]), value=item[-1]) for item in items]
        self.duplicates = duplicates
        self.bias = 0.5
        if self.duplicates:
            max_count = [self.capacity // item[0] for item in self.items]
            self.bounder = ec.DiscreteBounder([i for i in range(max(max_count) + 1)])
        else:
            self.bounder = ec.DiscreteBounder([0, 1])
        self.maximize = True
        self._use_ants = True

    def constructor(self, random, args):
        """Return a candidate solution for an ant colony optimization."""
        self._use_ants = True
        candidate = []

        while len(candidate) < len(self.components):
            # Find feasible components

            feasible_components = []
            if len(candidate) == 0:
                feasible_components = self.components
            else:
                sum_col = []
                for ele in candidate:
                    sum_col.append(ele.element)
                sum_col = np.sum(sum_col, axis=0)

                remaining_capacity = [x1 - x2 for (x1, x2) in zip(self.capacity, sum_col)]

                feasible_components = [c for c in self.components if
                                       c not in candidate and np.all(np.asarray(c.element) <= np.asarray(remaining_capacity))]

            if len(feasible_components) == 0:
                break
            else:
                if random.random() <= self.bias:
                    next_component = max(feasible_components)
                else:
                    next_component = \
                    selectors.fitness_proportionate_selection(random, feasible_components, {'num_selected': 1})[0]
                candidate.append(next_component)

        return candidate

    def evaluator(self, candidates,args):
        """Return the fitness values for the given candidates."""
        capa = self.capacity
        fitness = []
        if self._use_ants:
            for candidate in candidates:
                total = 0
                sumElement = np.zeros((len(self.capacity)))

                for c in candidate:
                    for i in range(0,len(c.element)):
                        #total += 0 - abs(capa[i] - c.element[i])
                        sumElement[i] += c.element[i]

                    total += c.value

                for i in range(0, len(sumElement)):
                    total += 0 - abs(capa[i] - sumElement[i])

                fitness.append(total)
        return fitness


capacities, items = get_problem('/home/ptan/Triforce/Dataset/OR5x100/OR5x100-0.25_1.dat')


print("Capacities : ")
print(capacities)

problem = Knapsack(capacities,items)


run = 100
fitness_list = []
diff_list = []

for i in range(0,run):
    print (i)
    prng = Random()
    prng.seed(time())

    ac = inspyred.swarm.ACS(prng, problem.components)
    ac.terminator = inspyred.ec.terminators.generation_termination
    final_pop = ac.evolve(generator=problem.constructor,
                          evaluator=problem.evaluator,
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          pop_size=10,
                          max_generations=50)


    display = True
    if display:
        best = max(ac.archive)

        for b in best.candidate:
            item = []
            for i in b.element:
                item.append(i)
            item.append(b.value)

        fitness_list.append(best.fitness)

best_fitness = max(fitness_list)    
worst_fitness = min(fitness_list)

#how many times algorithm produces best fitness value
success_rate = fitness_list.count(best_fitness)/100.0
for fitness in fitness_list:
    diff_list.append(best_fitness-fitness)
#average of difference between each value and the best fitness    
mean_abs_diff = sum(diff_list)/100.0
mean_abs_per_err = mean_abs_diff/best_fitness
#least difference (not counting best fitness)
least_err = min(item for item in diff_list if item>0)
#standard deviation of fitness list
alg_std = numpy.std(fitness_list)

print(fitness_list)
    
print("Successfully run till the end")
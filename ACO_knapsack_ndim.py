
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
    """Defines the Knapsack benchmark problem.

    This class defines the Knapsack problem: given a set of items, each
    with a weight and a value, find the set of items of maximal value
    that fit within a knapsack of fixed weight capacity. This problem 
    assumes that the ``items`` parameter is a list of (weight, value) 
    tuples. This problem is most easily defined as a maximization problem,
    where the total value contained in the knapsack is to be maximized.
    However, for the evolutionary computation (which may create infeasible
    solutions that exceed the knapsack capacity), the fitness is either
    the total value in the knapsack (for feasible solutions) or the
    negative difference between the actual contents and the maximum 
    capacity of the knapsack.
    If evolutionary computation is to be used, then the ``generator`` 
    function should be used to create candidates. If ant colony 
    optimization is used, then the ``constructor`` function creates 
    candidates. The ``evaluator`` function performs the evaluation for 
    both types of candidates.

    Public Attributes:

    - *capacity* -- the weight capacity of the knapsack
    - *items* -- a list of (weight, value) tuples corresponding to the
      possible items to be placed into the knapsack
    - *components* -- the set of ``TrailComponent`` objects constructed
      from the ``items`` parameter
    - *duplicates* -- Boolean value specifying whether items may be 
      duplicated in the knapsack (i.e., False corresponds to 0/1 Knapsack)
    - *bias* -- the bias in selecting the component of maximum desirability
      when constructing a candidate solution for ant colony optimization 
      (default 0.5)

    """

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
        # print candidates
        fitness = []
        if self._use_ants:
            for candidate in candidates:
                total = 0
                for c in candidate:
                    for i in range(0,len(c.element)):
                        total += 0 - abs(capa[i] - c.element[i])
                    total += c.value
                fitness.append(total)
        # print fitness
        # print "/////////////////////////////////////////////////////////"
        return fitness

file_path = "Dataset/OR5x100/OR5x100-0.25_3.dat"

capacity, items = get_problem(file_path)


# capacity = [15,10]
# items = [(1,1,1),(2,2,2),(3,3,3),(4,4,4),(5,5,5)]



print "Capacity : "
print capacity

problem = Knapsack(capacity,items)

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
    print('Best Solution:')

    for b in best.candidate:
        item = []
        for i in b.element:
            item.append(i)
        item.append(b.value)

        #print items[items.index(item)]
    print best.candidate
    print('Fitness: {0}'.format(best.fitness))


print "Successfully run till the end"
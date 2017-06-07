
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
from get_problem_fixed import get_problem

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

# file_path = "Dataset/OR5x100/OR5x100-0.25_1.dat"
#
# capacity, items = get_problem(file_path)
capacity = [11927, 13727, 11551, 13056, 13460]

items = [[504, 42, 509, 806, 404, 475],
 [803, 41, 883, 361, 197, 36],
 [667, 523, 229, 199, 817, 287],
 [1103, 215, 569, 781, 1000, 577],
 [834, 819, 706, 596, 44, 45],
 [585, 551, 639, 669, 307, 700],
 [811, 69, 114, 957, 39, 803],
 [856, 193, 727, 358, 659, 654],
 [690, 582, 491, 259, 46, 196],
 [832, 375, 481, 888, 334, 844],
 [846, 367, 681, 319, 448, 657],
 [813, 478, 948, 751, 599, 387],
 [868, 162, 687, 275, 931, 518],
 [793, 898, 941, 177, 776, 143],
 [825, 550, 350, 883, 263, 515],
 [1002, 553, 253, 749, 980, 335],
 [860, 298, 573, 229, 807, 942],
 [615, 577, 40, 265, 378, 701],
 [540, 493, 124, 282, 278, 332],
 [797, 183, 384, 694, 841, 803],
 [616, 260, 660, 819, 700, 265],
 [660, 224, 951, 77, 210, 922],
 [707, 852, 739, 190, 542, 908],
 [866, 394, 329, 551, 636, 139],
 [647, 958, 146, 140, 388, 995],
 [746, 282, 593, 442, 129, 845],
 [1006, 402, 658, 867, 203, 487],
 [608, 604, 816, 283, 110, 100],
 [877, 164, 638, 137, 817, 447],
 [900, 308, 717, 359, 502, 653],
 [573, 218, 779, 445, 657, 649],
 [788, 61, 289, 58, 804, 738],
 [484, 273, 430, 440, 662, 424],
 [853, 772, 851, 192, 989, 475],
 [942, 191, 937, 485, 585, 425],
 [630, 117, 289, 744, 645, 926],
 [591, 276, 159, 844, 113, 795],
 [630, 877, 260, 969, 436, 47],
 [640, 415, 930, 50, 610, 136],
 [1169, 873, 248, 833, 948, 801],
 [932, 902, 656, 57, 919, 904],
 [1034, 465, 833, 877, 115, 740],
 [957, 320, 892, 482, 967, 768],
 [798, 870, 60, 732, 13, 460],
 [669, 244, 278, 968, 445, 76],
 [625, 781, 741, 113, 449, 660],
 [467, 86, 297, 486, 740, 500],
 [1051, 622, 967, 710, 592, 915],
 [552, 665, 86, 439, 327, 897],
 [717, 155, 249, 747, 167, 25],
 [654, 680, 354, 174, 368, 716],
 [388, 101, 614, 260, 335, 557],
 [559, 665, 836, 877, 179, 72],
 [555, 227, 290, 474, 909, 696],
 [1104, 597, 893, 841, 825, 653],
 [783, 354, 857, 422, 614, 933],
 [959, 597, 158, 280, 987, 420],
 [668, 79, 869, 684, 350, 582],
 [507, 162, 206, 330, 179, 810],
 [855, 998, 504, 910, 415, 861],
 [986, 849, 799, 791, 821, 758],
 [831, 136, 758, 322, 525, 647],
 [821, 112, 431, 404, 774, 237],
 [825, 751, 580, 403, 283, 631],
 [868, 735, 780, 519, 427, 271],
 [852, 884, 788, 148, 275, 91],
 [832, 71, 583, 948, 659, 75],
 [828, 449, 641, 414, 392, 756],
 [799, 266, 32, 894, 73, 409],
 [686, 420, 653, 147, 896, 440],
 [510, 797, 252, 73, 68, 483],
 [671, 945, 709, 297, 982, 336],
 [575, 746, 129, 97, 697, 765],
 [740, 46, 368, 651, 421, 637],
 [510, 44, 440, 380, 246, 981],
 [675, 545, 314, 67, 672, 980],
 [996, 882, 287, 582, 649, 202],
 [636, 72, 854, 973, 731, 35],
 [826, 383, 460, 143, 191, 594],
 [1022, 714, 594, 732, 514, 689],
 [1140, 987, 512, 624, 983, 602],
 [654, 183, 239, 518, 886, 76],
 [909, 731, 719, 847, 95, 767],
 [799, 301, 751, 113, 846, 693],
 [1162, 718, 708, 382, 689, 893],
 [653, 91, 670, 97, 206, 160],
 [814, 109, 269, 905, 417, 785],
 [625, 567, 832, 398, 14, 311],
 [599, 708, 137, 859, 735, 417],
 [476, 507, 356, 4, 267, 748],
 [767, 983, 960, 142, 822, 375],
 [954, 808, 651, 110, 977, 362],
 [906, 766, 398, 11, 302, 617],
 [904, 615, 893, 213, 687, 553],
 [649, 554, 407, 398, 118, 474],
 [873, 282, 477, 173, 990, 915],
 [565, 995, 552, 106, 323, 457],
 [853, 946, 805, 331, 993, 261],
 [1008, 651, 881, 254, 525, 350],
 [632, 298, 850, 447, 322, 635]]

# capacity = [15,10]
# items = [(1,1,1),(2,2,2),(3,3,3),(4,4,4),(5,5,5)]


print "Capacity : "
print capacity

problem = Knapsack(capacity,items)


run = 10
fitnessList = []

for i in range(0,run):
    #print ('Run number : ',i+1)
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
        #print('Best Solution:')

        for b in best.candidate:
            item = []
            for i in b.element:
                item.append(i)
            item.append(b.value)

            #print items[items.index(item)]
        #print best.candidate
        #print('Fitness: {0}'.format(best.fitness))
        print best.fitness


print "Successfully run till the end"
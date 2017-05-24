from time import time
from random import Random
import inspyred
import random

#needed to define the custom knapsack class (copied directly from source)
class Benchmark(object):
    
    def __init__(self, dimensions, objectives=1):
        self.dimensions = dimensions
        self.objectives = objectives
        self.bounder = None
        self.maximize = True
        
    def __str__(self):
        if self.objectives > 1:
            return '{0} ({1} dimensions, {2} objectives)'.format(self.__class__.__name__, self.dimensions, self.objectives)
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


# custom Knapsack class WORKS FOR PSO and GA
class myKnapsack(Benchmark):
    
    def __init__(self, capacity, items, duplicates=False):
        Benchmark.__init__(self, len(items))
        self.capacity = capacity
        self.items = items
       # self.components = [swarm.TrailComponent((item[0]), value=item[1]) for item in items]
        self.duplicates = duplicates
        self.bias = 0.5
        if self.duplicates:
            max_count = [self.capacity // item[0] for item in self.items]
            self.bounder = inspyred.ec.DiscreteBounder([i for i in range(max(max_count)+1)])
        else:
            self.bounder = inspyred.ec.DiscreteBounder([0, 1])
        self.maximize = True
        self._use_ants = False
    
    def generator(self, random, args):
        """Return a candidate solution for an evolutionary computation."""
        if self.duplicates:
            max_count = [self.capacity // item[0] for item in self.items]
            return [random.randint(0, m) for m in max_count]
        else:
            return [random.choice([0, 1]) for _ in range(len(self.items))]
    
   
    
    def evaluator(self, candidates, args):
        """Return the fitness values for the given candidates."""
        fitness = []
        if self._use_ants:
            for candidate in candidates:
                total = 0
                for c in candidate:
                    total += c.value
                fitness.append(total)
        else:
            #included an extra dimension (volume)
            for candidate in candidates:
                total_value = 0
                total_weight = 0
                total_volume = 0
                for c, i in zip(candidate, self.items):
                    total_weight += c * i[0]
                    total_volume += c * i[1]
                    total_value += c * i[2]
                #if either total weight or volume exceeds its capacity->fitness is difference
                if total_weight > self.capacity[0] or total_volume > self.capacity[1]:
                    fitness.append(self.capacity[0] - total_weight + self.capacity[1] - total_volume)
                else:
                    fitness.append(total_value)
        return fitness


def main(prng=None, display=False):
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    
    items1 = [(7,369), (10,346), (11,322), (10,347), (12,348), (13,383), 
             (8,347), (11,364), (8,340), (8,324), (13,365), (12,314), 
             (13,306), (13,394), (7,326), (11,310), (9,400), (13,339), 
             (5,381), (14,353), (6,383), (9,317), (6,349), (11,396), 
             (14,353), (9,322), (5,329), (5,386), (5,382), (4,369), 
             (6,304), (10,392), (8,390), (8,307), (10,318), (13,359), 
             (9,378), (8,376), (11,330), (9,331)]

    #just for testing, dimensions/capacity are hardcoded; takes generated list of tuples with 3 dimensions
    dims = 3
    mylist = [(random.randint(1, 15), random.randint(1, 15), random.randint(300, 400)) for k in range(40)]
    print(mylist)
    capacity =[15, 15]
    
    
    problem = myKnapsack(capacity, mylist, duplicates=False) #use custom class
    ea = inspyred.swarm.PSO(prng)
    ea.terminator = inspyred.ec.terminators.evaluation_termination
    ea.topology = inspyred.swarm.topologies.ring_topology
    final_pop = ea.evolve(generator=problem.generator,
                          evaluator=problem.evaluator, 
                          pop_size=100,
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          max_evaluations=30000, 
                          neighborhood_size=5)

    if display:
        best = max(final_pop) 
        print('Best Solution: \n{0}'.format(str(best)))
    return ea

if __name__ == '__main__':
    main(display=True)
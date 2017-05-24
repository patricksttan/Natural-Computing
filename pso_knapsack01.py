from time import time
from random import Random
import inspyred
import random
import os
import codecs

def get_problem(file):

    #os.chdir("/home/ptan/Triforce/OR5x100")
    
    #f = codecs.open('OR5x100-0.25_1.dat', encoding='utf-8')
    f = codecs.open(file, encoding='utf-8')
    
    knap = []
    
    for line in f:
        knap.append(line)
        
    f.close()
    
    for i in range (0, len(knap)):
        knap[i] = knap[i].split(' ')
        if knap[i][0] == '':
            knap[i] = knap[i][1:]
        if knap[i][len(knap[i]) - 1] == '\r\n':
            knap[i] = knap[i][:-1]
    
    number_of_objects = int(knap[0][0])
    number_of_dimensions = int(knap[0][1])
    knapsack_capacities = []

    knap = knap[:-1]
    knap = [int(item) for sublist in knap for item in sublist]
    
    for i in range(0, number_of_dimensions):
        knapsack_capacities.append(knap[len(knap) - i - 1])
    
    items = []
    
    for i in range (0, number_of_objects):
        item = []
        for j in range (0, len(knapsack_capacities) + 1):
            item.append(knap[i + j * number_of_objects])
        items.append(item)
    
    return (knapsack_capacities, items)
    
    
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
            #number of constraints (total dimensions-1)
            num_constr = len(self.capacity)
            for candidate in candidates:
                list_total_constraints = [0]*num_constr
                total_value = 0
                
                for c, i in zip(candidate, self.items):
                   
                    for d in range(0,num_constr):
                        list_total_constraints[d] += c * i[d]
                    total_value += c * i[num_constr]
                
                
                for x in range(0,num_constr):
                    if list_total_constraints[x] > self.capacity[x]:
                        fitness.append(sum(self.capacity) - sum(list_total_constraints))
                        break
                    else:
                        fitness.append(total_value)
        return fitness


def main(prng=None, display=False):
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    
    
    capacities, itemslist = get_problem('C:\Users\User\Desktop\Dataset\OR5x250\OR5x250-0.25_2.dat')
    
    
    problem = myKnapsack(capacities, itemslist, duplicates=False) #use custom class
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
from time import time
from random import Random
import inspyred
import random
import os
import codecs
import numpy

def get_chance(file):
    
    capacities, items = get_problem(file)
    totals = [sum(x) for x in zip(*items)]
    chances = [totals/(capacities *1.0) for totals, capacities in zip(totals, capacities)]
    chance = sum(chances)/len(chances)/len(items)
    return chance
    

def get_problem(file):

    #os.chdir("/home/ptan/Triforce/OR5x100")
    
    #f = codecs.open('C:\Users\User\Desktop\Dataset\OR5x100\OR5x100-0.25_1.dat', encoding='utf-8')
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
    knapsack_capacities = knap[len(knap)-1:]
    knapsack_capacities = [int(item) for list in knapsack_capacities for item in list]
    
    knap = knap[1:-1]
    knap = [int(item) for sublist in knap for item in sublist]
    
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
            #return [random.choice([0, 1]) for _ in range(len(self.items))]
            pr_chance = get_chance('C:\Users\User\Desktop\Dataset\OR5x100\OR5x100-0.25_1.dat')
            return numpy.random.choice([0, 1], size=(len(self.items)), p=[1-pr_chance, pr_chance]).tolist()
    
   
    
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
                
                
                check = 0
                for x in range(0,num_constr):
                    if list_total_constraints[x] <= self.capacity[x]:
                        check += 1
                if check == num_constr:
                    fitness.append(total_value)
                    #print("fuck yeah")
                else:
                    #fitness.append(sum(self.capacity) - sum(list_total_constraints)) 
                    fitness.append(1)  
        return fitness



prng = Random()
prng.seed(time()) 

capacities, itemslist = get_problem('C:\Users\User\Desktop\Dataset\OR5x100\OR5x100-0.25_1.dat')


problem = myKnapsack(capacities, itemslist, duplicates=False) #use custom class
#ea = inspyred.ec.GA(prng)
ea = inspyred.swarm.PSO(prng)
ea.terminator = inspyred.ec.terminators.evaluation_termination
ea.topology = inspyred.swarm.topologies.ring_topology

fitness_list = []
diff_list = []

#get the fitness list of 100 algorithm runs
for i in range(0,5):
    print(i)
    final_pop = ea.evolve(generator=problem.generator,
                        evaluator=problem.evaluator, 
                        pop_size=100,
                        bounder=problem.bounder,
                        maximize=problem.maximize,
                        max_evaluations=30000, 
                        neighborhood_size=5)
                        #num_elites=1)

    best = max(final_pop)
    fitness_list.append(best.fitness)
            
print('Fitness list: \n{0}'.format(str(fitness_list)))

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

print("alg_std = " ,alg_std)
print("best_fitness = " ,best_fitness)
print("capacities = " ,capacities)

print("diff_list = " ,diff_list)
print("fitness_list = " ,fitness_list)

print("least_err = " ,least_err)
print("mean_abs_diff = " ,mean_abs_diff)
print("mean_abs_per_err = " ,mean_abs_per_err)
print("success_rate = " ,success_rate)
print("worst_fitness = " ,worst_fitness)
# -*- coding: utf-8 -*-
"""
Created on Wed May 24 14:37:36 2017

@author: ptan
"""

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
    knapsack_capacities = knap[len(knap)-1:]
    knapsack_capacities = [int(item) for list in knapsack_capacities for item in list]

    knap = knap[1:-1]
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

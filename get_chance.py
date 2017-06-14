# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 15:24:00 2017

@author: ptan
"""

def get_chance(file):
    
    capacities, items = get_problem(file)
    totals = [sum(x) for x in zip(*items)]
    chances = [totals/capacities for totals, capacities in zip(totals, capacities)]
    chance = sum(chances)/len(chances)/len(items)
    return chance
# -------------------------------------------------------------------
# SRC120 - SQL Practicum
# Seminar Task - Part 1
# Academic year 2021/2022
# University of Split - University Department of Professional Studies
# Students: Tomislava Nazor, Nikola Occidentale, Anamarija Papic
# -------------------------------------------------------------------

from itertools import combinations

# check if set X is a subset of set Y
def is_subset(X, Y):
    return set(X).issubset(set(Y))

# with help from itertools.combinations creates all possible combinations (subsets) of X
def subsets(X):
    return [''.join(l) for i in range(len(X)) for l in combinations(X, i + 1)]

# split the given string (functional dependency) into left and right side if only one separator -> is found 
# FD is in form: left->right
def divide_string_by_arrow(FD):
    if FD.count('->') == 1:
        left, right = FD.split('->')
        return left, right
    return None

# Attribute closure of an attribute set can be defined as set of attributes 
# which can be functionally determined from it.
# find attribute closure of the given attribute S:
# on each iteration check each functional dependency (L->R)
# and if L is a subset of the current formed closure add R to the closure
# repeat until there is no change on the closure string
def find_attribute_closure(R, FD, S):
    if not is_subset(S, R):
        return '' 
    closure = S
    change = True
    while change:
        change = False
        for dependency in FD:
            left, right = divide_string_by_arrow(dependency)
            if is_subset(left, closure):
                for attribute in right:
                    if attribute not in closure:
                        closure += attribute
                        change = True
    return ''.join(sorted(set(closure)))

# find attribute closures of all attribute combinations in the relational schema
def find_all_attribute_closures(R, FD):
    result = subsets(R)
    all_closures = {}
    for combination in result:
        all_closures[combination] = find_attribute_closure(R, FD, combination)
    return all_closures

# print attribute closures of all attribute combinations in the relational schema
def print_all_closures(R, FD):
    all_closures = find_all_attribute_closures(R, FD)
    for combination, closure in all_closures.items():
        print("(" + combination + ")\u207a = " + closure)
        
# Super key is *set of attributes* of a relation which can be used to identify a tuple uniquely.
# find all super keys:
# from all attribute closures find keys (attribute combinations) 
# whose closure gives a set of all attributes of relation
def find_super_keys(R, FD):
    all_closures = find_all_attribute_closures(R, FD)
    super_keys = []
    for key in all_closures:
        if all_closures[key] == R:
            super_keys.append(key)
    return super_keys

# Candidate key is *minimal set of attributes* of a relation which can be used to identify a tuple uniquely.
# find all candidate keys:
# from super keys find minimal set of attributes whose attribute closure is set of all attributes of relation
# a candidate key must not be derived from a subset which defines the whole relation
# for example:
# (AIJ)+ = ABCDEFGHIJ
# (ABIJ)+ = ABCDEFGHIJ
# AIJ is a candidate key, but ABIJ is not because it's not minimal (consists of AIJ)
def find_candidate_keys(R, FD):
    super_keys = find_super_keys(R, FD)
    candidate_keys = []
    for i in reversed(super_keys):
        flag = False
        for j in super_keys:
            if is_subset(j, i) and i != j:
                flag = True
        if not flag:
            candidate_keys.append(i)
    candidate_keys.sort()
    return candidate_keys
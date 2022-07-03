# -------------------------------------------------------------------
# SRC120 - SQL Practicum
# Seminar Task - Part 2
# Academic year 2021/2022
# University of Split - University Department of Professional Studies
# Students: Tomislava Nazor, Nikola Occidentale, Anamarija Papic
# -------------------------------------------------------------------

# Useful Normalization Tool: https://www.ict.griffith.edu.au/normalization_tools/normalization/ind.php

import pk_algorithm

# check if functional dependency is trivial
def is_trivial_fd(LHS, RHS):
        return LHS == RHS

# Remove trivial FDs (those where the RHS is also in the LHS).
def remove_trivial_fds(FD):
    for dependency in FD:
        LHS, RHS = pk_algorithm.divide_string_by_arrow(dependency)
        if is_trivial_fd(LHS, RHS):
            FD.remove(dependency)
    return FD

# A minimal functional cover (canonical cover) Fmin of a set of functional dependencies F 
# is a simplified set of functional dependencies that has the 
# same closure as the original set F.
def find_minimal_cover(R, FD):
    Fmin = []

    # Rewrite the FD into those with only one attribute on RHS.
    for dependency in FD:
        LHS, RHS = pk_algorithm.divide_string_by_arrow(dependency)
        for attribute in RHS:
            Fmin.append(LHS + "->" + attribute)
    
    # Remove trivial FDs (those where the RHS is also in the LHS)
    Fmin = remove_trivial_fds(Fmin)

    # Minimize LHS of each FD.
    for i in range(len(Fmin)):
        LHS, RHS = pk_algorithm.divide_string_by_arrow(Fmin[i])
        total_LHS_closure = pk_algorithm.find_attribute_closure(R, Fmin, LHS)
        for combination in pk_algorithm.subsets(LHS):
            if pk_algorithm.find_attribute_closure(R, Fmin, combination) == total_LHS_closure and combination != LHS:
                Fmin[i] = combination + "->" + RHS
    
    # Remove redundant FDs (those that are implied by others)
    # a) remove if extraneous attribute from dependency
    for i in range(len(Fmin)):
        LHS, RHS = pk_algorithm.divide_string_by_arrow(Fmin[i])
        if len(set(LHS)) > 1:
            for attribute in LHS:
                if pk_algorithm.find_attribute_closure(R, FD, LHS) == pk_algorithm.find_attribute_closure(R, FD, LHS.replace(attribute, "")):
                    Fmin[i] = LHS.replace(attribute, "") + "->" + RHS         

    # b) remove if transitive relation
    fds_to_remove = []
    for i in range(len(Fmin)):
        LHS1, RHS1 = pk_algorithm.divide_string_by_arrow(Fmin[i])
        for j in reversed(range(len(Fmin))):
            if i != j:
                LHS2, RHS2 = pk_algorithm.divide_string_by_arrow(Fmin[j])
                if RHS1 == LHS2:
                    transitive_dependency = LHS1 + "->" + RHS2
                    if transitive_dependency in Fmin:
                        fds_to_remove.append(transitive_dependency)
    for fd in Fmin:
        if fd in fds_to_remove:
            Fmin.remove(fd)

    # c) remove if not unique
    Fmin = list(dict.fromkeys(Fmin))

    return Fmin

# find prime and non-prime attributes
def find_prime_and_nonprime_attr(R, candidate_keys):
    prime_attributes = sorted(set(''.join(candidate_keys)))
    non_prime_attributes = sorted(set(R).difference(set(prime_attributes)))
    return prime_attributes, non_prime_attributes

# for each non-trivial FD, check whether the LHS is a proper subset of some candidate key 
# or the RHS are not all key attributes
def check_nf2(R, FD, candidate_keys):
    prime_attributes, non_prime_attributes = find_prime_and_nonprime_attr(R, candidate_keys)
    print("\nThe set of key/prime attributes are:", prime_attributes)
    print("\nNon-prime attributes are:", non_prime_attributes)

    FD = remove_trivial_fds(FD)

    nf2 = True
    cause = None

    print("\n2NF Check:")
    for dependency in FD:
        print("Checking FD:", dependency)
        LHS, RHS = pk_algorithm.divide_string_by_arrow(dependency)
        if any(item in RHS for item in non_prime_attributes):
            for candidate in candidate_keys:
                if LHS in pk_algorithm.subsets(candidate) and LHS != candidate:
                    nf2 = False
            if not nf2:
                cause = LHS + "->" + RHS
                cause += "\nViolates definition of 2NF - (LHS is a proper subset of some CK)"
                break

    return nf2, cause

def check_nf3_violation(RHS, LHS, super_keys, non_prime_attributes):
    if LHS in super_keys:
        return True
    else:
        for attribute in LHS:
            if attribute in non_prime_attributes:
                return False
            else:
                return True

# for each FD, check whether the LHS is superkey or the RHS are all key attributes
def check_nf3(R, FD, candidate_keys):
    prime_attributes, non_prime_attributes = find_prime_and_nonprime_attr(R, candidate_keys)
    
    super_keys = pk_algorithm.find_super_keys(R, FD)

    nf3 = True
    cause = None

    FD = remove_trivial_fds(FD)

    print("\n3NF Check:")

    for dependency in FD:
        print("Checking FD:", dependency)
        LHS, RHS = pk_algorithm.divide_string_by_arrow(dependency)
        nf3 = check_nf3_violation(RHS, LHS, super_keys, non_prime_attributes)
        if not nf3:
            cause = LHS + "->" + RHS
            cause += "\nViolates definition of 3NF - (LHS is not superkey, RHS contains a non-key attribute)"
            break

    return nf3, cause

def check_bcnf_violation(RHS, LHS, super_keys):
    if LHS not in super_keys and not is_trivial_fd(LHS, RHS):
        return False
    return True

# A relation is in BCNF if, X is superkey for every functional dependency (FD) X->Y in given relation.
def check_bcnf(R, FD, candidate_keys):
    super_keys = pk_algorithm.find_super_keys(R, FD)
    
    bcnf = True
    cause = None

    print("\nBCNF Check:")

    for dependency in FD:
        print("Checking FD:", dependency)
        LHS, RHS = pk_algorithm.divide_string_by_arrow(dependency)
        bcnf = check_bcnf_violation(RHS, LHS, super_keys)
        if not bcnf:
            cause = LHS + "->" + RHS
            cause += "\nViolates definition of BCNF - (It is non-trivial and its LHS is not a superkey.)"
            break

    return bcnf, cause

def check_normal_form(R, FD):
    print("\nRelational schema: " + R)
    
    print("\nFunctional dependencies:")
    print(FD)

    # find all candidate keys
    candidate_keys = pk_algorithm.find_candidate_keys(R, FD)
    print("\nCandidate keys:", candidate_keys)

    nf2 = False
    nf3 = False
    bcnf = False

    # 1NF - check is redundant
    # The relation is in first normal form if it does not contain any composite or multi-valued attribute.

    # 2NF
    # A relation must be in first normal form and relation must not contain any partial dependency. 
    # i.e., no non-prime attribute is dependent on any proper subset of any candidate key of the table.

    nf2, cause = check_nf2(R, FD, candidate_keys)

    # 3NF
    # A relation is in third normal form, if there is no transitive dependency for non-prime attributes 
    # as well as it is in second normal form.
    # A relation is in 3NF if at least one of the following condition holds in every non-trivial function dependency X –> Y:
    # 1) X is a super key.
    # 2) Y is a prime attribute (each element of Y is part of some candidate key).    

    if nf2:
        nf3, cause = check_nf3(R, FD, candidate_keys)
    
    # BCNF
    # A table is in BCNF if and only if for every non-trivial FD, the LHS is a superkey.
    
    if nf2 and nf3:
        bcnf, cause = check_bcnf(R, FD, candidate_keys)

    # manage output
    if nf2:
        if nf3:
            if bcnf:
                return "Boyce-Codd Normal Form (BCNF)", None
            else:
                return "3rd Normal Form (3NF)", cause
        else:
            return "2nd Normal Form (2NF)", cause
    else:
        return "1st Normal Form (1NF)", cause

# Merge FDs with same LHS and whose RHS are non-key attributes
def merge_fds(R, Fmin, candidate_keys):
    prime_attributes, non_prime_attributes = find_prime_and_nonprime_attr(R, candidate_keys)
    
    reduced_Fmin = []
    for fd in Fmin:
        flag = True
        LHS, RHS = pk_algorithm.divide_string_by_arrow(fd)
        for attribute in RHS:
            if attribute in prime_attributes:
                flag = False
        if flag:
            reduced_Fmin.append(fd)
        
    merged_Fmin = []
    helper_dict_merge = {}
    for i in reduced_Fmin:
        LHS1, RHS1 = pk_algorithm.divide_string_by_arrow(i)
        helper_dict_merge[LHS1] = [RHS1]
        for j in reversed(reduced_Fmin):
            if i != j:
                LHS2, RHS2 = pk_algorithm.divide_string_by_arrow(j)
                if LHS1 == LHS2:
                    helper_dict_merge[LHS1].append(RHS2)
    print(helper_dict_merge)
    for key, value in helper_dict_merge.items():
        merged_Fmin.append(key + "->" + "".join(value))

    return merged_Fmin

def normalize_nf3(R, FD):
    normal_form, cause = check_normal_form(R, FD)
    print("\nThe table's normal form is:", normal_form)
    if cause is not None:
        print("Because:", cause)
    if normal_form == "3rd Normal Form (3NF)" or normal_form == "Boyce-Codd Normal Form (BCNF)":
        print("\nTable already in 3NF!")
        return 
    
    print("\nStarting decomposing a table into 3NF...")
    # Step 1: Find the minimal cover of FDs.
    Fmin = find_minimal_cover(R, FD)
    print("\nMinimal cover of FDs:\n", Fmin)

    # Step 2. Find all candidate keys.
    candidate_keys = pk_algorithm.find_candidate_keys(R, FD)

    # Step 3: Merge FDs with same LHS and whose RHS are non-key attributes (we get the set F1).
    merged_fds = merge_fds(R, Fmin, candidate_keys)
    print("\nMerged FDs:\n", merged_fds)

    # Step 4: Check each FD in the set F1 for violation of 3NF, and split table accordingly.
    prime_attributes, non_prime_attributes = find_prime_and_nonprime_attr(R, candidate_keys)
    
    super_keys = pk_algorithm.find_super_keys(R, FD)
    
    nf3_tables = []

    for fd in merged_fds:
        print("\nChecking FD:", fd)
        LHS, RHS = pk_algorithm.divide_string_by_arrow(fd)
        nf3 = check_nf3_violation(LHS, RHS, super_keys, non_prime_attributes)
        if not nf3:
            print("The FD violates 3NF as its LHS is not a superkey (and RHS is a set of non-key attributes).")
            print("The following 3NF table is obtained:")
            nf3_tables.append([LHS + RHS, fd])
            print(nf3_tables[-1][0] + "\nwith FDs\n" + nf3_tables[-1][1])

    # Step 5: Finally, add the following table into normalized 3NF table set 
    # (obtained by removing RHS attributes of FDs using which we produced a table)
    if len(prime_attributes) > 1:
        table_attributes = "".join(sorted(prime_attributes))

        table_closures = pk_algorithm.find_all_attribute_closures(table_attributes, FD)    
        for key, value in table_closures.items():
            for attribute in key:
                if attribute in non_prime_attributes:
                    table_closures.pop(key)
                    break
            for attribute in value:
                if attribute in non_prime_attributes:
                    table_closures[key] = table_closures[key].replace(attribute, "")

        table_fds = []
        for key, value in table_closures.items():
            left = key
            right = value
            if left != right:
                right = "".join(set(right).difference(set(left)))
                table_fds.append(left + "->" + right)

        table_Fmin = find_minimal_cover(table_attributes, table_fds)

        print("\nFinally, the following 3NF table is added:")
        nf3_tables.append([table_attributes, table_Fmin])
        print(nf3_tables[-1][0] + "\nwith FDs\n" + ", ".join(nf3_tables[-1][1]))

    print("\nAll 3NF tables:")
    for table in nf3_tables:
        print(table[0])

def normalize_bcnf(R, FD):
    normal_form, cause = check_normal_form(R, FD)
    print("\nThe table's normal form is:", normal_form)
    if cause is not None:
        print("Because:", cause)
    if normal_form == "Boyce-Codd Normal Form (BCNF)":
        print("\nTable already in BCNF!")
        return 

# pre-loaded relational schemas and functional dependencies
R = ["ABCDEFGHIJ", "ABCDEFGHIJ", "EFGHIJKLMN", "ABCDEFGHIJ", "ABCDEFGHIJ", "ABC", "ABCD", "ABCDEF", "ABCD", "ABC"]
FR = [["DI->B", "AJ->F", "GB->FJE", "AJ->HD", "I->CG"], 
      ["A->EF", "F->CH", "I->DB", "CJ->I", "BF->JE", "E->CD"],
      ["EF->G", "F->IJ", "EH->KL", "K->M", "L->N"],
      ["A->B", "A->D", "A->H", "C->B", "B->E", "I->J", "H->G", "D->F"],
      ["A->B", "BE->G", "EF->A", "D->AC", "G->HIJ"],
      ["A->BC", "B->C", "A->B", "AB->C"],
      ["A->B", "B->C", "C->A"],
      ["DF->C", "BC->F", "E->A", "ABC->E"],
      ["A->B", "B->C", "C->D", "D->A"],
      ["A->B", "B->A", "B->C", "A->C", "C->A"]]
# must have at least 5 pre-loaded examples
# every relational schema must have at least 10 attributes and 5 functional dependencies
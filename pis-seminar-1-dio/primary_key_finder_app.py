# -------------------------------------------------------------------
# SRC120 - SQL Practicum
# Seminar Task - Part 1
# Academic year 2021/2022
# University of Split - University Department of Professional Studies
# Students: Tomislava Nazor, Nikola Occidentale, Anamarija Papic
# -------------------------------------------------------------------

import pk_algorithm
import re # regular expression
from termcolor import colored # cmd: pip install termcolor
import os
clear = lambda: os.system('cls')

# helper function for handling user input - number as a choice (for navigating through app)
def user_input_choice(min_value, max_value):
    choice = -1
    while choice < min_value or choice > max_value:
        choice = int(input("Enter your choice: "))
        if choice < min_value or choice > max_value:
            print("Wrong input! Please retry.")
    return choice

# helper function for handling user input - confirm decision
def user_confirm(message):
    print(message)
    choice = input("y/n: ")
    if choice == 'y' or choice == 'Y':
        return True
    return False

# helper function for printing navigation options from dictionary
def print_navigation(navigation_options):
    for key, value in navigation_options.items():
        if key == 0:
            color = 'red'
        else:
            color = 'blue'
        print(colored(str(key) + ". ", color) + value)
    print()

# print main menu and call appropriate function depending on user choice
def main_menu():
    clear()
    print("--------------------------\n| Primary Key Finder App |\n--------------------------")
    print("-------------\n| Main Menu |\n-------------")

    main_menu_options = {
    1 : 'Find PK: Choose from saved relational schemas (with functional dependencies)',
    2 : 'Find PK: Add a new relational schema and its functional dependencies',
    3 : 'Delete a saved relational schema and its functional dependencies',
    0 : 'Quit program'
    }
    
    print_navigation(main_menu_options)
    choice = user_input_choice(0, len(main_menu_options) - 1)
    clear()
    match choice:
        case 1:
            choose_from_saved()
        case 2:
            add_new()
        case 3:
            delete_from_saved()
        case 0:
            quit()

# return to main menu or quit app (depends on user decision)
def return_to_main_menu():
    if user_confirm("\nQuit app?"):
        quit()
    main_menu()

# find all attribute closures, super keys and candidate keys - possible primary keys
# using functional dependencies of a relational schema
def find_primary_key(R, FD):
    clear()
    print("--------------------------\n| Finding Primary Key... |\n--------------------------")

    print("\nRelational schema: " + R)
    
    print("\nFunctional dependencies:")
    print(FD)
    
    # print("\nAll atrtribute closures:")
    # pk_algorithm.print_all_closures(R, FD)

    print("\nSuper keys:")
    print(pk_algorithm.find_super_keys(R, FD))

    print("\nCandidate keys - possible primary keys:")
    print(pk_algorithm.find_candidate_keys(R, FD))

# pre-loaded relational schemas and functional dependencies
R = ["ABCDEFGHIJ", "ABCDEFGHIJ", "EFGHIJKLMN", "ABCDEFGHIJ", "ABCDEFGHIJ"]
FR = [["DI->B", "AJ->F", "GB->FJE", "AJ->HD", "I->CG"], 
      ["A->EF", "F->CH", "I->DB", "CJ->I", "BF->JE", "E->CD"],
      ["EF->G", "F->IJ", "EH->KL", "K->M", "L->N"],
      ["A->B", "A->D", "A->H", "C->B", "B->E", "I->J", "H->G", "D->F"],
      ["A->B", "BE->G", "EF->A", "D->AC", "G->HIJ"]]
# must have at least 5 pre-loaded examples
# every relational schema must have at least 10 attributes and 5 functional dependencies

# helper function for printing saved relational schemas and their functional dependencies as submenu options
def print_R_and_FR_options():
    for i in range(len(R)):
        print(colored(str(i + 1) + ". ", 'blue'))
        print("R = " + R[i])
        print("FR = " + ", ".join(FR[i]))
    print(colored("0. ", 'green') + "Return to main menu\n")

# find primary key of a user-chosen saved relational schema using its dependencies 
def choose_from_saved():
    print("--------------------------------\n| Find Primary Key: From Saved |\n--------------------------------")
    print_R_and_FR_options()

    choice = user_input_choice(0, len(R))
    if choice == 0:
        main_menu()

    index = choice - 1
    find_primary_key(R[index], FR[index])

    return_to_main_menu()

# find primary key of a user-entered new relational schema using its dependencies 
def add_new():
    print("-----------------------------\n| Find Primary Key: Add New |\n-----------------------------")
    print("Please enter a relational schema with at least 10 attributes and at least 5 functional dependencies.")
    
    new_R = ''
    while len(set(new_R)) < 10:
        new_R = input("\nEnter new relational schema (R): ").upper()
        if len(set(new_R)) < 10:
            print("Please enter a relational schema with at least 10 attributes!")
    R.append(''.join(sorted(set(new_R))))
    
    new_FR = []
    number_of_dependencies = -1
    while number_of_dependencies < 5:
        number_of_dependencies = int(input("\nEnter number of its functional dependencies: "))
        if number_of_dependencies < 5:
            print("Must have at least 5 functional dependencies!")
    print("\nEnter each functional dependency in format left->right.")
    for i in range(number_of_dependencies):
        FD = ''
        while not re.match('^[a-zA-Z]+->[a-zA-Z]+$', FD):
            FD = input("Enter functional dependency (FD) no." + str(i + 1) + ": ").upper()
            if not re.match('^[a-zA-Z]+->[a-zA-Z]+$', FD):
                print("Wrong input format! Please retry.")
        new_FR.append(FD)
    FR.append(new_FR)
    
    print("\nRelational schema (with its functional dependencies) is successfully added.")

    find_primary_key(R[-1], FR[-1])

    return_to_main_menu()

# delete a user-chosen relational schema and its functional dependencies from saved 
def delete_from_saved():
    print("----------\n| Delete |\n----------")
    print_R_and_FR_options()

    choice = user_input_choice(0, len(R))
    if choice == 0:
        main_menu()

    if user_confirm("Are you sure you want to delete relational schema no." + str(choice) + "?"):
        index = choice - 1
        R.pop(index)
        FR.pop(index)
        print("\nRelational schema no." + str(choice) + " (with its functional dependencies) is successfully deleted.")

    return_to_main_menu()
        
main_menu()
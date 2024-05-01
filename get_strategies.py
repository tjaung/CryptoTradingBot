
# USER INPUT FOR TRADING STRATEGIES

# MENU VARIABLES
defaultStrats = ['Line Rider','Line Rider']
stratOptions = range(1,4)
strats = ['Line Rider', 'Ichimoku', 'TD']


def current_strats(stratList=None):
    if stratList is None:
        return(defaultStrats)
    if stratList is not None:
        return(stratList)


def get_strats():
    print("Enter strategies for each symbol one at a time below.")

    # GET STRATEGY MENU
    strat_menu()

    # USER INPUTS
    chooseStrat = int(input('\nSelect Strategy: '))
    if chooseStrat in range(1,4):
        return(strats[chooseStrat-1])
    else:
        print('Invalid Option: Please Enter An Integer Within The List.')



def strat_menu():
    # CREATE MENU
    print('\nStrategy Options:')
    print(f'[{stratOptions[0]}] {strats[0]}')
    print(f'[{stratOptions[1]}] {strats[1]}')
    print(f'[{stratOptions[2]}] {strats[2]}')
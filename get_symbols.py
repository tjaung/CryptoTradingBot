
# Get the crypto symbols

defaultList = ['BTC-USD', 'ETH-USD']

def current_symbols(symbolList=None):
    if symbolList is None:
        return(defaultList)
    if symbolList is not None:
        return(symbolList)

def get_symbols():
    print("Enter symbol one at a time below. Type 'End' to stop.")
    symbolList  = []
    inputs=""

    while inputs != 'END':
        inputs = str(input('Enter symbol: ')).upper()
        if inputs == '' and symbolList == []:
            return(defaultList)
        elif inputs == '' and symbolList != []:
            pass
        else:
            symbolList.append(inputs)
    
    del symbolList[-1]
    [x.upper() for x in symbolList]

    return(symbolList)

def print_List(list):
    print(list)

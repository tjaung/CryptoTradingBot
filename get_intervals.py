
# TIME INTERVAL SELECTION

import pandas as pd
import numpy as np
import binance
import websocket
import json
import pprint

import config
import get_symbols

# MENU VARIABLES
defaultIntervals = ['1h', '1h']
intervalOptions = range(1,16)
intervalTimes = ['1m','3m','5m','15m','30m','1h','2h','4h','6h','8h','12h','1d','3d','1w','1M']


def current_Intervals(intervalList=None):
    if intervalList is None:
        return(defaultIntervals)
    if intervalList is not None:
        return(intervalList)

# TIME INTERVAL FOR CANDLE STICK DATA. USER CAN SELECT FROM 15 TIME INTERVALS IN WHICH TO PULL DATA
def interval_select():

    # PRINT MENU
    interval_menu()

    # USER OPTION INPUT
    chooseInterval = int(input('\nSelect Time Interval: '))
    if chooseInterval in range(1,16):
        return(intervalTimes[chooseInterval-1])
    else:
        print('Invalid Option: Please Enter An Integer Within The List.')
        interval_menu()

def interval_menu():
    # CREATE MENU
    print('\nTime Interval Options:')
    print(f'[{intervalOptions[0]}] {intervalTimes[0]}   [{intervalOptions[3]}] {intervalTimes[3]}   [{intervalOptions[6]}] {intervalTimes[6]}   [{intervalOptions[9]}] {intervalTimes[9]}   [{intervalOptions[12]}] {intervalTimes[12]}')
    print(f'[{intervalOptions[1]}] {intervalTimes[1]}   [{intervalOptions[4]}] {intervalTimes[4]}   [{intervalOptions[7]}] {intervalTimes[7]}   [{intervalOptions[10]}] {intervalTimes[10]}  [{intervalOptions[13]}] {intervalTimes[13]}')
    print(f'[{intervalOptions[2]}] {intervalTimes[2]}   [{intervalOptions[5]}] {intervalTimes[5]}    [{intervalOptions[8]}] {intervalTimes[8]}   [{intervalOptions[11]}] {intervalTimes[11]}   [{intervalOptions[14]}] {intervalTimes[14]}')


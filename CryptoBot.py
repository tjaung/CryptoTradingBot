import coinbasepro as cbp
import pprint
import pandas as pd
import numpy as np
import websocket, json
import talib
import dateutil.parser
import math
import datetime
import matplotlib.pyplot as plt

import hmac, hashlib, time, requests, base64
from requests.auth import AuthBase

import get_symbols
import get_intervals
import get_strategies
import backtesting
import config

api_pass=config.api_pass
api_key=config.api_key
api_secret = config.api_secret


auth_client = cbp.AuthenticatedClient(key=api_key,
                                          secret=api_secret,
                                          passphrase=api_pass)

# Websocket

buy_price = 1000
minutes_processed = {}
minute_candlesticks = []
current_tick = None
previous_tick = None

def on_open(ws):
    print("<---OPENED CONNECTION--->")

    subscribe_message = {
        'type': 'subscribe',
        'channels': [
            {
                'name': 'ticker',
                'product_ids': currentSymbols
                }
            ]
        }

    ws.send(json.dumps(subscribe_message))


def on_message(ws, message):
    #received = pd.DataFrame(json.loads(message))
    #received.set_index('time')
    # message_print = received[['product_id', 'price']]
    now = datetime.datetime.now()

    global current_tick, previous_tick
    current_tick = json.loads(message)
    previous_tick=current_tick
    

    #print("{}: {} @ {}".format(current_tick['product_id'],current_tick['time'], current_tick['price']))

    tick_datetime_object = dateutil.parser.parse(current_tick['time'])
    tick_dt = tick_datetime_object.strftime("%m/%d/%Y %H:%M")
   # print(tick_dt)
    
    if not tick_dt in minutes_processed:
      #  print("---NEW CANDLESTICK---")
        minutes_processed[tick_dt] = True
        #print(minutes_processed)

        if len(minute_candlesticks) > 0:
            minute_candlesticks[-1]['close'] = previous_tick['price']

        minute_candlesticks.append({
                                     "minute": tick_dt,
                                     'open': current_tick['price'],
                                     "high":current_tick['price'],
                                     "low": current_tick['price']
                                     })

        if len(minute_candlesticks) > 0:
            current_candlestick = minute_candlesticks[-1]
            if current_tick['price'] > current_candlestick['high']:
                current_candlestick['high'] = current_tick['price']
            if current_tick['price'] < current_candlestick['low']:
                current_candlestick['low'] = current_tick['low']
        
        print(minute_candlesticks[-2])

        # look at last closed candle and assess close price
        if len(minute_candlesticks) > 1:
            last_candle = minute_candlesticks[-2]

            if tick_dt[-2:] == "00":
                for symbol in currentSymbols:

                    #get wallet
                    wallet_ids[symbol]
                    wallet = auth_client.get_account(wallet_ids[symbol])

                    

                    # get historical data
                    hr1 = pd.DataFrame(auth_client. get_product_historic_rates(symbol, granularity='3600'))
                
                    hr1 = hr1.reindex(index=hr1.index[::-1])
                    hr1['close'].astype('float')
                    hr1['rsi'] = talib.RSI(hr1['close'], timeperiod=28)
                    hr1['ema'] = talib.EMA(hr1['close'], timeperiod=200)
                    # calculate hull
                    hr1['wma10'] = talib.WMA(hr1['close'], timeperiod=10)
                    hr1['wma5'] = talib.WMA(hr1['close'], timeperiod=5)
                    hr1['hma'] = talib.WMA((2 * hr1['wma5']) - hr1['wma10'], timeperiod = math.sqrt(10))

                    # indicators
                    # crossover
                    hr1['crossover'] = np.where(hr1['ema'] < hr1['hma'], 1,0)
                    # rsi
                    hr1['rsi_cross'] = np.where(hr1['rsi'] > 60, 1, np.where(hr1['rsi'] < 35, -1, 0))
                
                    # show stats
                    print(symbol)
                    print(hr1[['time', 'rsi', 'ema', 'hma', 'close']].tail())
                    print('HOLDING: ' + str(wallet['available']))

            
                    if ((hr1.at[0,'rsi_cross'] == 1)): #((hr1.at[0,'crossover'] == 1)) & :
                        print('BUY SIGNAL')
                      
                        if (wallet['hold'] > 0):
                            print(f'ALREADY HOLDING {symbol}')
                            
                        elif (wallet['available'] == 0):

                            print("<=== BUYING {(buy_price/last_candle['close'])} {symbol} AT MARKET VALUE ===>")
                            auth_client.place_order(symbol, 'buy', order_type='market', funds=buy_price)
                            auth_client.place_order(symbol, 'sell', order_type='limit', stop = 'loss', stop_price = round(float(hr1.at[0,'close'])*0.92, 2), size = float(wallet['available']), price=round(float(hr1.at[0,'close'])*0.92, 2))

                    if ((hr1.at[0,'rsi_cross'] == -1)):
                        print('SELL SIGNAL')

                        if ((wallet['available'] > 0)==False):
                            print(f'NO {symbol} HOLDINGS')

                        elif ((wallet['available'] > 0)==True):
                            print(f"<=== SELLING {wallet['available']} {symbol} AT MARKET VALUE ===>")
                            auth_client.place_order(symbol, 'sell', order_type='market', size = wallet['available'])
           

                        

def on_close(ws):
    print("<---CLOSED CONNECTION--->")

socket = 'wss://ws-feed-public.sandbox.pro.coinbase.com'
ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)

# SET DEFAULT PARAMETERS
currentSymbols = get_symbols.current_symbols()
currentStrats = get_strategies.current_strats()
currentIntervals = get_intervals.current_Intervals()

# MAIN MENU
def menu():
    print('\nCRYPTOCURRENCY TRADING BOT')
    print("\n[1] Run Algorithm")
    print(f"[2] Set Symbol List          Current Symbols: {currentSymbols}")
    print(f"[3] Set Strategy             Current Strategies: {currentStrats}")
    print(f"[4] Enter Interval           Current Intervals: {currentIntervals}")
    print('[5] Backtrace')
    print("[6] About")
    print("[0] Close Program")
menu()
try:
    option = int(input("\nEnter Option: "))
except EOFError as e:
    print(e)

while option != 0:
    # RUN THE ALGORITHM USING THE CURRENT PARAMETERS. IF USER DOES NOT MAKE ANY CHANGES THEN THE DEFAULT PARAMETERS WILL BE
    # USED
    if option == 1:
        if (len(currentSymbols) != len(currentIntervals)) or (len(currentSymbols) != len(currentStrats)) or (len(currentIntervals) != len(currentStrats)):
            print('ERROR: SETTINGS ARE NOT OF EQUAL LENGTH. PLEASE UPDATE THE CURRENT PARAMETERS.')
        else:

            ws.run_forever()
            ws.close()

    elif option == 2:
        # SYMBOLS OF INTEREST FOR THE ALGORITHM. DEFAULT LIST IS ALREADY SET, BUT THIS MENU FUNCTION ALLOWS THE USER TO MANUALLY 
        # INPUT SYMBOLS IN BINANCE TO BE RUN IN THE PROGRAM
        symbolList = get_symbols.get_symbols()
        get_symbols.print_List(symbolList)
        currentSymbols = symbolList

    elif option == 3:
        # TRADING STRATEGY TO BE USED IN THE ALGORITHM. THE USER CAN SELECT FROM A MENU OF PRESET TECHNICAL INDICATORS FOR USE 
        # IN THE TRADING STRATEGY. 
        stratList=[]

        # CREATE STRATEGY MENU
        get_strategies.strat_menu()

        # SET STRATEGIES FOR EACH SYMBOL IN CURRENT SYMBOL LIST
        for i in currentSymbols:
            stratList.append(get_strategies.get_strats())
        # UPDATE STRATEGY LIST
        currentStrats = stratList

    elif option == 4:
        # TIME INTERVAL FOR CANDLE STICK DATA. USER CAN SELECT FROM 15 TIME INTERVALS IN WHICH TO PULL DATA
        intervalList = []

        # SET INTERVAL FOR EACH SYMBOL IN CURRENT SYMBOL LIST
        for i in currentSymbols:
            intervalList.append(get_intervals.interval_select())
        # UPDATE INTERVAL LIST
        currentIntervals = intervalList

    elif option == 5:
        # BACKTEST USING CURRENT PARAMETERS. THE USER CAN TEST THE CURRENT PARAMETERS AGAINST HISTORICAL DATA. DEFAULT
        # PARAMETERS WILL
        # BE TESTED IF USER DOES NOT MAKE ANY CHANGES
        cash = float(input('Enter Starting Cash Amount: '))
        timespan = []
        for symbol in currentSymbols:
            timespan.append(backtesting.timespan_select(symbol))

        #files = []
        for symbol, interval, timespan in zip(currentSymbols, currentIntervals, timespan,):
            
            intervalArgs = backtesting.data_parameters(str(interval))
            print('\nCOLLECTING HISTORICAL DATA FOR {}...'.format(symbol))
            #files.append(backtesting.save_historical_data(symbol, interval, intervalArgs, timespan))
            data = backtesting.save_historical_data(symbol, interval, intervalArgs, timespan)
            print('\nBACKTESTING FOR {}...'.format(symbol))
            backtesting.backtrading(cash, data)

            #print(files)
        #for file, symbol in zip(files, currentSymbols):
        #    print('BACKTESTING FOR {}'.format(symbol))
        #    backtesting.backtrading(cash, file)

    elif option == 6:
        # A BRIEF ABOUT THE PROGRAM. 
        print('About')
    elif option == 'new':
        menu()
        option = int(input('\nEnter Option: '))
    else:
        print('Invalid Option')
    print()
    menu()
    try:
        option = int(input('\nEnter Option: '))
    except EOFError as e:
        print(e)
print('Goodbye')
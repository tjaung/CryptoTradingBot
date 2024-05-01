# BACKTESTING

from binance.client import Client
import pprint, csv
import config
import pandas as pd
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.analyzers as btanalyzers

import requests 
import json 
import matplotlib.pyplot as plt
from matplotlib import warnings
import qgrid
from datetime import datetime

import trading_strategies


# LOGIN
client = Client(config.apiKey, config.apiSecretKey)
timespanList = ['1 hour ago', '6 hours ago', '1 day ago', '3 days ago', '1 week ago', '2 weeks ago', '1 month ago', '3 months ago', '6 months ago', '1 year ago', '3 years ago', '5 years ago', 'Custom']
timespanOptions = range(1, len(timespanList))

def menu():
    print('\nSelect Timespan for each symbol:')
    for option in timespanOptions:
        print(f'[{option}] {timespanList[option]}')

def timespan_select(symbol):
    menu()

    # USER INPUT
    chooseTimeSpan = int(input('\nSelect Time Span For {}: '.format(symbol)))
    if chooseTimeSpan in range(1, len(timespanOptions)):
        return(timespanList[chooseTimeSpan])
    elif chooseTimeSpan == 12:
        customTS_from = input('From: ')
        customTS_to = input('To: ')
        customTS = [customTS_from, customTS_to]
        return(customTS)
    elif chooseTimeSpan == "":
        chooseTimeSpan = input('\Please Select An Option For {}: '.format(symbol))
    elif int(chooseTimeSpan) not in range(1,13):
        print('Invalid Option: Please Enter An Integer Within The List.')
        chooseTimeSpan = input('\nSelect Time Span For {}: '.format(symbol))
    else:
        chooseTimeSpan = input('\nSelect Time Span For {}: '.format(symbol))


def data_parameters(interval):
    # CREATE THE INTERVAL DICTIONARY
    intervalDictionary = {'1m': Client.KLINE_INTERVAL_1MINUTE,
                          '3m': Client.KLINE_INTERVAL_3MINUTE,
                          '5m': Client.KLINE_INTERVAL_5MINUTE,
                          '15m': Client.KLINE_INTERVAL_15MINUTE,
                          '30m': Client.KLINE_INTERVAL_30MINUTE,
                          '1h': Client.KLINE_INTERVAL_1HOUR,
                          '2h': Client.KLINE_INTERVAL_2HOUR,
                          '4h': Client.KLINE_INTERVAL_4HOUR,
                          '6h': Client.KLINE_INTERVAL_6HOUR,
                          '8h': Client.KLINE_INTERVAL_8HOUR,
                          '12h': Client.KLINE_INTERVAL_12HOUR,
                          '1d': Client.KLINE_INTERVAL_1DAY,
                          '3d': Client.KLINE_INTERVAL_3DAY,
                          '1w': Client.KLINE_INTERVAL_1WEEK,
                          '1M': Client.KLINE_INTERVAL_1MONTH}

    intervalArgs = intervalDictionary[interval]

    return(intervalArgs)

def save_historical_data(symbol, interval, intervalArgs, timespan):
    #filename = symbol + '_' + interval + '_' + timespan.replace(" ", "")+'.csv'

    #csvfile = open(filename, 'w', newline='') 
    #candlestick_writer = csv.writer(csvfile, delimiter=',')

    #klines = client.get_historical_klines(symbol=symbol, interval=intervalArgs, start_str=timespan)

    #for kline in klines:
    #    kline[0] = kline[0] / 1000
    #    candlestick_writer.writerow(kline)

    #csvfile.close()
    #return(filename) 
    # If timespan was a custom range

    symbol = symbol + "T"
    sym = ""
    for character in symbol:
        if character.isalnum():
            sym += character

    t2 = 'none'
    if isinstance(timespan, list):
        t1 = timespan[0]
        t2 = timespan[1]
    else:
        t1 = timespan

    if t2 == 'none':
        klines = client.get_historical_klines(symbol=sym, interval=intervalArgs, start_str=t1)
    else:
        klines = client.get_historical_klines(symbol=sym, interval=intervalArgs, start_str=t1, end_str=t2)
    
    klinesDF = pd.DataFrame(klines)
    klinesDF_date = klinesDF[0]

    final_date = []
    for time in klinesDF_date.unique():
        readable = datetime.fromtimestamp(int(time/1000))
        final_date.append(readable)
    klinesDF.pop(0)
    klinesDF.pop(11)

    klinesDF_final_date = pd.DataFrame(final_date)
    klinesDF_final_date.columns = ['date']

    klinesDF = klinesDF.join(klinesDF_final_date)
    klinesDF.set_index('date', inplace=True)
    klinesDF.columns = ['open', 'high', 'low', 'close', 'volume', 'close_time', 'asset_volume', 'trade_number', 'taker_buy_base', 'taker_buy_quote']

    return(klinesDF)



# BACKTESTING WITH BACKTRADER AND DATA COLLECTED FROM ABOVE FUNCTION
class PandasData(btfeeds.DataBase):

    '''
    The ``dataname`` parameter inherited from ``feed.DataBase`` is the pandas
    DataFrame
    '''

    params = (
        # Possible values for datetime (must always be present)
        #  None : datetime is the "index" in the Pandas Dataframe
        #  -1 : autodetect position or case-wise equal name
        #  >= 0 : numeric index to the colum in the pandas dataframe
        #  string : column name (as index) in the pandas dataframe
        ('datetime', None),

        # Possible values below:
        #  None : column not present
        #  -1 : autodetect position or case-wise equal name
        #  >= 0 : numeric index to the colum in the pandas dataframe
        #  string : column name (as index) in the pandas dataframe
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('openinterest', None),
    )

def backtrading(cash, data):

    # GET DATA COLUMNS
    df = data[['open', 'high', 'low', 'close', 'volume']]

    df = df.apply(pd.to_numeric)
    #df.open = df.open.astype('float')
    #df.high = df.high.astype('float')
    #df.low = df.low.astype('float')
    #df.close = df.close.astype('float')
    #df.volume = df.volume.astype('float')

    cerebro = bt.Cerebro()

    cerebro.broker.set_cash(cash)


    # FEED DATA
    feed=bt.feeds.PandasData(dataname=df)
    cerebro.adddata(feed)
    cerebro.addstrategy(trading_strategies.MA)

    cerebro.addsizer(bt.sizers.PercentSizer, percents = 50)

    # Set the commission
    cerebro.broker.setcommission(commission=0.01)

    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name = "sharpe")
    cerebro.addanalyzer(btanalyzers.Transactions, _name = "trans")

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    results = cerebro.run(optreturn=True)
    results
  
    
    # TRY TO GET MORE STATS LIKE WIN RATE, SHARPE, TRANSACTIONS,...
    # PUT THE STATS INTO A NICE TABLE

    results[0].analyzers.sharpe.get_analysis() # Sharpe
    len(results[0].analyzers.trans.get_analysis())

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot(iplot=False,
                 style='candlestick', barup='green', bardown='red')



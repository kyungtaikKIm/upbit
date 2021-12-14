from time import time
import pyupbit
import numpy as np
import pandas as pd
import datetime
import math

nowtime = (datetime.datetime.now()).strftime('%Y%m%d%H%M')
money = 1000000
unit = money*0.01

tickers = pyupbit.get_tickers()

i = 0

for ticker in tickers :
    if i == 0:
        pricedata = pyupbit.get_ohlcv(ticker, count = 386, interval= "day", to = nowtime)
        pricedata['name'] = ticker
        rtickers=[ticker]
    else:
        if ticker[0:3]=='KRW':
            tmpdata = pyupbit.get_ohlcv(ticker, count = 386, interval= "day", to = nowtime)
            tmpdata['name'] = ticker
            
            if tmpdata.shape[0]>=30:
                pricedata=pd.concat([pricedata, tmpdata])
                rtickers.append(ticker)
    i=i+1
    if i==2: break


onhand=pd.DataFrame(index=pricedata.index[-365:], columns=rtickers)
bfbuyprice=pd.DataFrame(index=pricedata.index[-365:], columns=rtickers)
totbuyprice=pd.DataFrame(index=pricedata.index[-365:], columns=rtickers)
profit=pd.DataFrame(index=pricedata.index[-365:], columns=rtickers)

for days in range(365):
    for ticker in rtickers:
        if pricedata.loc[pricedata['name']==ticker].shape[0]-(365-days+21)>=0:
            if nowtime[-4:] >= '0900':
                today = datetime.datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            else:
                today = (datetime.datetime.now() - datetime.timedelta(1)).replace(hour=9, minute=0, second=0, microsecond=0)

            strtdate = today - datetime.timedelta(365-days+21)
            endtdate = today - datetime.timedelta(365-days)

            caldata=pricedata.loc[pricedata['name']==ticker][strtdate:endtdate]

            maxprice=caldata[1:21]['high'].max()
            minprice=caldata[11:21]['low'].min()

            trdata= pd.DataFrame([caldata.loc[:,'high']/caldata.loc[:,'low']
            , pd.concat([caldata.loc[:,'high'] / caldata.loc[:,'close'].shift(1) , caldata.loc[:,'close'].shift(1)/caldata.loc[:,'high'] ],axis=1).max(axis=1)
            , pd.concat([caldata.loc[:,'low'] / caldata.loc[:,'close'].shift(1) , caldata.loc[:,'close'].shift(1)/caldata.loc[:,'low'] ],axis=1).max(axis=1)])
            n = math.pow(trdata.max(axis = 0)[2:21].cumprod().iloc[-1], 1/20)

            if (days==0)|(onhand.iloc[max(days-1,0)][ticker]==0):
                if (caldata[21:22]['high'].tolist()>=maxprice)&(len(caldata[21:22]['high'].tolist())>0): #매입상황
                    onhand.iloc[days][ticker]=unit/n/caldata[21:22]['high'].tolist()
                    # bfbuyprice.iloc[days][ticker]=caldata[21:22]['high']
                    # totbuyprice.iloc[days][ticker]=unit/n
                    # money=money-totbuyprice.iloc[days][ticker]
                else:
                    onhand.iloc[days][ticker]=0
                    bfbuyprice.iloc[days][ticker]=0
                    totbuyprice.iloc[days][ticker]=0
            # else:
            #     if caldata[21:22]['low'].tolist()<=minprice: #매도상황
            #         onhand.iloc[days][ticker]=0
            #         bfbuyprice.iloc[days][ticker]=0
            #         totbuyprice.iloc[days][ticker]=0
            #         profit.iloc[days][ticker]=onhand.iloc[days-1][ticker]*caldata[21:22]['low'].tolist()-totbuyprice.iloc[days-1][ticker]
            #         money=money+profit.iloc[days][ticker]
            #     elif caldata[21:22]['high'].tolist()>=bfbuyprice.iloc[days-1][ticker]*n: #추가매수상황
            #         onhand.iloc[days][ticker]=onhand.iloc[days-1][ticker]+unit/n/caldata[21:22]['high']*math.floor(np.log(caldata[21:22]['high']/bfbuyprice.iloc[days-1][ticker])/np.log(n))
            #         bfbuyprice.iloc[days][ticker]=caldata[21:22]['high']
            #         totbuyprice.iloc[days][ticker]=totbuyprice.iloc[days-1][ticker]+unit/n*math.floor(np.log(caldata[21:22]['high']/bfbuyprice.iloc[days-1][ticker])/np.log(n))
            #         money=money-unit/n*math.floor(np.log(caldata[21:22]['high']/bfbuyprice.iloc[days-1][ticker])/np.log(n))
            #     else:
            #         onhand.iloc[days][ticker]=onhand.iloc[days-1][ticker]
            #         bfbuyprice.iloc[days][ticker]=bfbuyprice.iloc[days-1][ticker]
            #         totbuyprice.iloc[days][ticker]=totbuyprice.iloc[days-1][ticker]
    

# writer=pd.ExcelWriter('coin_'+nowtime+'.xlsx', engine='openpyxl')
# pricedata.to_excel(writer, sheet_name='sheet1')
# onhand.to_excel(writer, sheet_name='sheet2')
# bfbuyprice.to_excel(writer, sheet_name='sheet3')
# totbuyprice.to_excel(writer, sheet_name='sheet4')
# profit.to_excel(writer, sheet_name='sheet5')
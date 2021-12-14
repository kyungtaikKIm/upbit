import time
import pyupbit
import datetime
import pandas as pd


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_avg_buy_price(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['avg_buy_price'] is not None:
                return float(b['avg_buy_price'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def get_factor(ticker, k, j, l):
    """주요 지표 계산"""
    if k >= max(j, l):
        df = pyupbit.get_ohlcv(ticker, interval="day", count=k)    
        
        if df.shape[0]>=k: 
            df['tr1']=df.loc[:,'high']/df.loc[:,'low']
            df['tr2']=pd.concat([df.loc[:,'high'] / df.loc[:,'close'].shift(1) , df.loc[:,'close'].shift(1)/df.loc[:,'high'] ],axis=1).max(axis=1)
            df['tr3']=pd.concat([df.loc[:,'low'] / df.loc[:,'close'].shift(1) , df.loc[:,'close'].shift(1)/df.loc[:,'low'] ],axis=1).max(axis=1)

            return {'name' :ticker, 'buy' : df['high'].max(), 'sell': df[k-j:k]['low'].min(), 'n' : df[k-l:k][['tr1', 'tr2', 'tr3']].max(axis=1).cumsum()[k-1]/l}
    else:
        print("수식오류") 
        
access = "akey"
secret = "bkey"

upbit = pyupbit.Upbit(access, secret)
print("autotrade start")


# 자동매매 시작
loop_start_time=datetime.datetime.now()


tickers = pyupbit.get_tickers()
current_bid_price=pd.DataFrame(0, columns=['cur_bid'], index=tickers)
for ticker in tickers:
    if get_balance(ticker[4:])>0:
        current_bid_price['cur_bid'][ticker]=max([get_avg_buy_price(ticker[4:]), get_current_price(ticker)])
        
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if (start_time + datetime.timedelta(minutes=10) < now < end_time)&(now > loop_start_time+datetime.timedelta(minutes=3)) :
            tickers = tot_fact['name']

            for ticker in tickers:
                price=get_current_price(ticker)

                if price>=float(tot_fact.loc[tot_fact['name']==ticker, 'buy']):
                    money = get_balance("KRW")
                    unit=money*0.02
                    invest = max([unit/float(tot_fact.loc[tot_fact['name']==ticker, 'n'])*0.9995,5000])
                    upbit.buy_market_order(ticker, invest)
                    current_bid_price['cur_bid'][ticker]=price
                    tot_fact.loc[tot_fact['name']==ticker, 'buy']=price*float(tot_fact.loc[tot_fact['name']==ticker, 'n'])
                    tot_fact.loc[tot_fact['name']==ticker, 'sell']=price/pow(float(tot_fact.loc[tot_fact['name']==ticker, 'n']),2)

                elif price<=float(tot_fact.loc[tot_fact['name']==ticker, 'sell']):
                    upbit.sell_market_order(ticker, balance)
                    current_bid_price['cur_bid'][ticker]=0
                    
        else:
            tickers = pyupbit.get_tickers()

            tot_fact=pd.DataFrame(columns = ['name' , 'buy', 'sell', 'n']) 

            for ticker in tickers:                
                res = get_factor(ticker, 20, 10, 20)
                
                if get_balance(ticker[4:])>0:
                    res['buy']=max([float(current_bid_price['cur_bid'][ticker])*(res['n']), res['buy']])
                    res['sell']=max([float(current_bid_price['cur_bid'][ticker])/pow(res['n'],2), res['sell']])
                
                if (res is not None)&(ticker[0:3]=='KRW'):
                    tot_fact=tot_fact.append(res, ignore_index = True)
             
            
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
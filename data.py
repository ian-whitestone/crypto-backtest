"""
import postgrez

query = "select * from hist_prices where snap_time::date>='2017-01-01' order by snap_time asc"

postgrez.export('crypto', query=query, filename='./data/USDT_BTC.csv')
"""

import pandas as pd
import numpy as np
import datetime


class MeanReversion():

    def __init__(self):
        self.moving_avg_window = 12*24*3 # 3 days (1 hour * 24 hour per day)

    def _load_data(self):
        df = pd.read_csv('./data/USDT_BTC.csv')
        return df

    def _make_decision(self, df):
        buy = df['close'] < df['moving_avg']
        sell = df['close'] > df['moving_avg']

        ## 0 is hold, 1 is buy, 2 is sell
        decision = pd.Series([0] * df.shape[0], index=df.index)
        decision.loc[buy] = 1
        decision.loc[sell] = 2

        ## indicator if the previous row has the same decision
        ## i.e. decision = [1, 1, 1, 0, 2, 2, 2], match will be [False, True, True, False, False, True, True]
        match = np.ediff1d(decision, to_begin=np.NaN) == 0

        ## if the decision is the same as the above, override to 0 (i.e hold)
        decision.loc[match] = 0
        return decision

    def _transaction_price(self, df):
        buy_price = df['high'].shift(-1)
        sell_price = df['low'].shift(-1)

        buy = df['decision'] == 1
        sell = df['decision'] == 2

        transaction_price = pd.Series([np.nan] * df.shape[0], index=df.index)
        transaction_price.loc[buy] = buy_price
        transaction_price.loc[sell] = sell_price
        return transaction_price

    def get_data(self):
        df = self._load_data()
        # df['snap_dt'] = df['snap_time'].apply(lambda x:
        #     datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
        df['moving_avg'] = df['close'].shift(1) \
                            .rolling(window=self.moving_avg_window).mean()
        df['decision'] = self._make_decision(df)
        df['transaction_price'] = self._transaction_price(df)
        df['snap_dt'] = df['snap_time'].apply(lambda x:
            datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
        return df

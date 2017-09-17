"""
TODO
- Plot price chart over time (weighted average or candle sticks), vertical lines to indicate buying/selling points.

Down the road:
Real time streaming chart:

- https://bl.ocks.org/boeric/6a83de20f780b42fadb9
--> Add ability to speed up/slow down the stream
"""

from data import MeanReversion

from math import pi
from bokeh.charts import Line, output_file, show
from bokeh.plotting import figure, output_file, show
from bokeh.models import DatetimeTickFormatter, DaysTicker, DatetimeTicker

###################
#### CONSTANTS ####
###################

## Starting balance in USD
STARTING_BAL = 1000

## Transaction fees in %'s
SELL_FEE = 0.16/100
BUY_FEE = 0.26/100

##################
#### GET DATA ####
##################

source = MeanReversion()
df = source.get_data()

snap_dts = df['snap_dt'].tolist()
decisions = df['decision'].tolist()
transaction_prices = df['transaction_price'].tolist()

data = []
for snap_dt, decision, transaction_price in zip(snap_dts, decisions,
                                                    transaction_prices):
    d = {}
    d['snap_dt'] = snap_dt
    d['decision'] = decision
    d['transaction_price'] = transaction_price
    data.append(d)



#################
#### RESULTS ####
#################

def transact(d, start_bal, start_shares):
    if d['decision'] == 1:
        bal = start_bal*(1-BUY_FEE)
        shares = bal/d['transaction_price']

    elif d['decision'] == 2:
        if start_shares > 0:
            bal = start_shares*d['transaction_price']*(1-SELL_FEE)
            shares = 0
        else:
            bal = start_bal
            shares = start_shares
    else:
        bal = start_bal
        shares = start_shares

    return bal, shares

results = []
bal = STARTING_BAL
shares = 0

for d in data:
    result = {}
    result['snap_dt'] = d['snap_dt']
    result['decision'] = d['decision']
    result['start_bal'] = bal
    result['start_shares'] = shares
    bal, shares = transact(d, bal, shares)
    result['end_bal'] = bal
    result['end_shares'] = shares
    results.append(result)
    if bal < 1 and shares < 1:
        break

print ('Starting position: %s' % results[0])
print ('Ending position: %s' % results[-1])

output_file("datetime.html")

# create a new plot with a datetime axis type
p = figure(width=800, height=800, x_axis_type="datetime")

p.line([r['snap_dt'] for r in results], [r['end_bal'] for r in results],
        color='navy', alpha=0.5)

p.xaxis[0].ticker = DatetimeTicker(desired_num_ticks=20)

p.xaxis.formatter=DatetimeTickFormatter(
        hours=["%Y-%m-%d"],
        days=["%Y-%m-%d"],
        months=["%Y-%m-%d"],
        years=["%Y-%m-%d"],
    )

p.xaxis.major_label_orientation = pi/4

output_file('balance.html')
show(p)

import pandas as pd
from pandas.stats.moments import rolling_mean
from Models.TradeResults import TradeResults


# Original code of inefficient version: http://www.gbquant.com/?p=9
# the inefficient version was rewritten.
def calc_true_range(df):
    hilo = df["High"] - df["Low"]
    hiclo = abs(df["High"] - df["Close"].shift(1))
    loclo = abs(df["Low"] - df["Close"].shift(1))
    temp = pd.concat([hilo, hiclo, loclo], axis=1)

    return temp.max(axis=1)


def average_true_range(df, N=14):
    """calculates the ATR by taking a rolling mean over the true range."""
    true_range = calc_true_range(df)
    return rolling_mean(true_range, N)


def snf(df):
    """shift and fill, used to delay logical trading signals"""
    return df.shift(1).fillna(False)


def test_fixed_stop_target(df_i, target_p, target_n):

    #target_p = 20.0                 # profit target adjustable
    #target_n = -1.0 * target_p      # loss target

    trade_return = 0.0
    in_position = False
    winning_trades = 0
    loosing_trades = 0

    # loop over data and correct position based on rules
    for i in range(1, df_i.shape[0]):
        if in_position: # it doesn't matter what the current position was, carry forward prev position
            pos = df_i.ix[i - 1, "position"]
            df_i.ix[i, "position"] = pos
            trade_return += pos * df_i.ix[i, "period_returns"]
            if trade_return > target_p:
                in_position = False
                trade_return = 0.0
                winning_trades += 1
            elif trade_return < target_n:
                in_position = False
                trade_return = 0.0
                loosing_trades += 1
        else:
            if df_i.ix[i, "position"] != 0:
                in_position = True

    # now total return is simply pos * returns
    profit = df_i["position"] * df_i["period_returns"]
    t_profit = profit.sum()
    return TradeResults(winning_trades, loosing_trades, t_profit)


# exit after N bars, this just demonstrates that the entry is good
def test_fixed_bar_exit(df_i):

    max_bars = 3
    bar_count = 0

    trade_return = 0.0
    in_position = False
    winning_trades = 0
    loosing_trades = 0

    # loop over data and correct position based on rules
    for i in range(1, df_i.shape[0]):
        if in_position: # it doesn't matter what the current position was, carry forward prev position
            pos = df_i.ix[i - 1, "position"]
            df_i.ix[i, "position"] = pos
            trade_return += pos * df_i.ix[i, "period_returns"]
            bar_count += 1

            if bar_count > max_bars:
                if trade_return > 0.0:
                    winning_trades += 1
                else:
                    loosing_trades += 1
                in_position = False
                bar_count = 0
                trade_return = 0.0
        else:
            if df_i.ix[i, "position"] != 0:
                in_position = True

    # now total return is simply pos * returns
    profit = df_i["position"] * df_i["period_returns"]
    t_profit = profit.sum()
    return TradeResults(winning_trades, loosing_trades, t_profit)
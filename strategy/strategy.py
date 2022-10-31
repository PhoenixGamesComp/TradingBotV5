from misc.balance import BalanceHandler
from misc.actions import Actions
from misc.logger import Logger
from indicators.dema import dema
from indicators.supertrend import supertrend
from indicators.fbb import fbb
from strategy.conditions import long_open, long_close, long_stoploss
from strategy.conditions import short_open, short_close, short_stoploss
from strategy.conditions import take_profit, stop_loss
import mplfinance as mpf
import pandas as pd
import numpy as np
import sys

import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [8.0, 12.0]
plt.rcParams['figure.dpi'] = 140


class Strategy:

    def __init__(self, balance_handler: BalanceHandler):

        self.reset(balance_handler)

    def reset(self, balance_handler: BalanceHandler):

        self.balance_handler = balance_handler
        self.current_action = Actions.NO
        self.logger = Logger()
        self.in_trade = False
        self.daily_profit = 0
        self.total_days = 0
        self.days_that_target_was_reached = 0
        self.day_added = False
        self.history = []

    def tune(self, length,
             supertrend_multi, supertrend_atr,
             fbb_source, fbb_multi,
             take_profit_percentage, daily_max_profit):

        self.length = length
        self.supertrend_multi = supertrend_multi
        self.supertrend_atr = supertrend_atr
        self.fbb_source = fbb_source
        self.fbb_multi = fbb_multi
        self.take_profit_percentage = take_profit_percentage
        self.daily_max_profit = daily_max_profit

    def calculate_indicators(self, data):

        self.dema = dema(data, self.length)
        self.supertrend = supertrend(
            data, self.supertrend_multi, self.supertrend_atr)
        self.fbb = fbb(data, self.fbb_source, self.length, self.fbb_multi)

    def price_reached_in_time_period(self, row, entry_price, percentage, long=True):

        open_price = row["open"]
        high_price = row["high"]
        low_price = row["low"]
        close_price = row["close"]

        if long:

            target_price = entry_price * (1 + percentage)

            return open_price < target_price <= high_price

        else:

            target_price = entry_price * (1 - percentage)

            return open_price > target_price >= low_price

    # Check if long entry condition is satisfied
    def should_enter_long(self, row, index):

        # If not already in trade and enter long conditions are satisfied
        ret_val = not self.in_trade and long_open(
            row["close"], self.supertrend["Supertrend"][index], self.dema[index], self.fbb[0][index])

        action = Actions.ENTER_LONG if ret_val else Actions.NO

        entry_price = row["close"] if ret_val else None

        return ret_val, action, entry_price

    # Check if short entry condition is satisfied
    def should_enter_short(self, row, index):

        # If not already in trade and enter short conditions are satisfied
        ret_val = not self.in_trade and short_open(
            row["close"], self.supertrend["Supertrend"][index], self.dema[index], self.fbb[1][index])

        action = Actions.ENTER_SHORT if ret_val else Actions.NO

        entry_price = row["close"] if ret_val else None

        return ret_val, action, entry_price

    # Check if long exit conditions are satisfied
    def should_exit_long(self, row, index):

        ret_val = False
        action = Actions.NO
        exit_price = None

        # If there is no active trade or bot never traded, return
        if not self.in_trade or len(self.history) == 0:

            return ret_val, action, exit_price

        # Supertrend trend changed or price reached fbb limits
        if long_close(row["close"], self.supertrend["Supertrend"][index], self.fbb[0][index]):

            ret_val = True
            action = Actions.EXIT_LONG_PROFIT if self.history[-1]["price"] > row["close"] else Actions.EXIT_LONG_LOSS
            exit_price = row["close"]

        # Price closed below supertrend resistance level
        elif long_stoploss(row["close"], self.supertrend["Final Lowerband"][index]):

            ret_val = True
            action = Actions.EXIT_LONG_LOSS
            exit_price = row["close"]

        # Target price is between open and high, take profit
        elif self.price_reached_in_time_period(row, self.history[-1]["price"], self.take_profit_percentage, True):

            ret_val = True
            action = Actions.EXIT_LONG_PROFIT
            exit_price = self.history[-1]["price"] * \
                (1 + self.take_profit_percentage)

        return ret_val, action, exit_price

    # Check if short exit conditions are satisfied
    def should_exit_short(self, row, index):

        ret_val = False
        action = Actions.NO
        exit_price = None

        # If there is no active trade or bot never traded, return
        if not self.in_trade or len(self.history) == 0:

            return ret_val, action, exit_price

        # Supertrend trend changed or price reached fbb limits
        if short_close(row["close"], self.supertrend["Supertrend"][index], self.fbb[0][index]):

            ret_val = True
            action = Actions.EXIT_SHORT_PROFIT if self.history[-1]["price"] < row["close"] else Actions.EXIT_SHORT_LOSS
            exit_price = row["close"]

        # Price closed below supertrend resistance level
        elif short_stoploss(row["close"], self.supertrend["Final Upperband"][index]):

            ret_val = True
            action = Actions.EXIT_SHORT_LOSS
            exit_price = row["close"]

        # Target price is between open and low, take profit
        elif self.price_reached_in_time_period(row, self.history[-1]["price"], self.take_profit_percentage, False):

            ret_val = True
            action = Actions.EXIT_SHORT_PROFIT
            exit_price = self.history[-1]["price"] * \
                (1 - self.take_profit_percentage)

        return ret_val, action, exit_price

    # What action should the bot take? Return the appropriate action
    def action_handler(self, row, index):

        methods = [self.should_enter_long,
                   self.should_exit_long,
                   self.should_enter_short,
                   self.should_exit_short]

        action = Actions.NO
        ret_price = None

        for method in methods:

            ret_val, ret_action, ret_price = method(row, index)

            if ret_val is True:

                action = ret_action
                break

        return action, ret_price

    def run(self, data):

        self.calculate_indicators(data)

        test_data = data.iloc[self.length:, :]

        prev_day = None
        for index, row in test_data.iterrows():

            day = pd.to_datetime(row["open_date_time"]).to_pydatetime().date()

            action, price = self.action_handler(row, index)

            #! Stop trading when daily percentage is reached, don't overtrade
            if day != prev_day:

                self.total_days += 1
                self.daily_profit = 0
                self.day_added = False

            else:

                if self.daily_profit >= self.daily_max_profit:

                    if not self.day_added:

                        self.days_that_target_was_reached += 1

                    self.day_added = True
                    continue

            # If action is enter position
            if action is Actions.ENTER_LONG or action is Actions.ENTER_SHORT:

                self.entry(price, action)
                self.history.append({
                    "date": row["open_date_time"],
                    "action": action,
                    "price": price
                })

            # Else if action is close position
            elif action is not Actions.NO:

                # Get balance before closing the trade
                balance_before = self.balance_handler.get_balance()

                self.close(price, action)

                # Get balance after closing the trade
                balance_after = self.balance_handler.get_balance()

                # Calculate percentage of differce
                diff_perc = (balance_after - balance_before) / balance_before
                self.daily_profit += diff_perc

                self.history.append({
                    "date": row["open_date_time"],
                    "action": action,
                    "price": price
                })

            prev_day = day

    def entry(self, entry_price, action):

        self.current_action = action
        self.entry_price = entry_price
        self.balance_handler.enter_position(entry_price)
        self.in_trade = True

    def exit(self, exit_price, percentage, action):

        self.balance_handler.exit_position(
            exit_price, percentage, (self.current_action is Actions.ENTER_LONG))

        self.current_action = action

    def close(self, exit_price, action):

        if self.current_action is Actions.ENTER_LONG:
            long = True
        elif self.current_action is Actions.ENTER_SHORT:
            long = False

        self.balance_handler.exit_position(exit_price, 1, long)
        self.in_trade = False
        self.current_action = action

    def get_signal_data(self, ohlc, signal_data):

        ret_data = pd.DataFrame(
            [float('nan')]*len(ohlc), index=ohlc.index, columns=['Signal'])

        for ix, val in zip(signal_data.index, signal_data.values):

            ret_data.loc[ix] = val

        return ret_data

    '''
    def debug(self, data):

        data.rename(
            columns={"open_date_time": "date"}, inplace=True)
        data["date"] = pd.to_datetime(data["date"])
        data.set_index("date", inplace=True)

        ohlc = data.filter(
            ["open", "high", "low", "close"], axis=1).copy()
        ohlc = ohlc.astype(float)

        mc = mpf.make_marketcolors(down="#EDA247", up="#57C4AD", edge={
            "down": "#DB4325", "up": "#006164"}, wick={"down": "#DB4325", "up": "#006164"}, alpha=0.8)

        s = mpf.make_mpf_style(base_mpf_style="nightclouds",
                               marketcolors=mc, gridstyle="")

        # History
        history_data = pd.DataFrame(self.history, columns=[
            "date", "action", "close"])
        history_data["date"] = pd.to_datetime(history_data["date"])
        history_data.set_index("date", inplace=True)

        entry_long_signals = mpf.make_addplot(
            self.get_signal_data(
                ohlc, history_data[history_data["action"] == Actions.ENTER_LONG].drop("action", axis=1)),
            type="scatter",
            markersize=50,
            marker="v",
            color="green")

        exit_long_signals = mpf.make_addplot(
            self.get_signal_data(
                ohlc, history_data[history_data["action"] == Actions.EXIT_LONG].drop("action", axis=1)),
            type="scatter",
            markersize=50,
            marker="^",
            color="green")

        entry_short_signals = mpf.make_addplot(
            self.get_signal_data(
                ohlc, history_data[history_data["action"] == Actions.ENTER_SHORT].drop("action", axis=1)),
            type="scatter",
            markersize=50,
            marker="v",
            color="red")

        exit_short_signals = mpf.make_addplot(
            self.get_signal_data(
                ohlc, history_data[history_data["action"] == Actions.EXIT_SHORT].drop("action", axis=1)),
            type="scatter",
            markersize=50,
            marker="^",
            color="red")

        # DEMA
        dema_plot = mpf.make_addplot(
            self.dema, width=0.75, color="c")

        # FBB
        fbb_up_plot = mpf.make_addplot(
            self.fbb[0], width=0.75, color="r")
        fbb_down_plot = mpf.make_addplot(
            self.fbb[1], width=0.75, color="r")

        # Supertrend
        supertrend_lower_plot = mpf.make_addplot(
            self.supertrend["Final Lowerband"], width=0.75, color="g")
        supertrend_upper_plot = mpf.make_addplot(
            self.supertrend["Final Upperband"], width=0.75, color="r")

        ap = [
            entry_long_signals,
            exit_long_signals,
            entry_short_signals,
            exit_short_signals,
            dema_plot,
            fbb_up_plot,
            fbb_down_plot,
            supertrend_lower_plot,
            supertrend_upper_plot
        ]

        fig, ax = mpf.plot(ohlc, type="candle", style=s,
                           returnfig=True, show_nontrading=True, addplot=ap, warn_too_much_data=sys.maxsize)

        mpf.show()

    '''

from numpy import append
from regex import D
from misc.logger import Logger


class BalanceHandler:

    def __init__(self, init_capital, leverage=1):

        self.reset(init_capital=init_capital, leverage=leverage)

    def reset(self, init_capital, leverage=1):

        self.initial_capital = init_capital
        self.net_profit = 0
        self.coin_qty = 0
        self.leverage = leverage
        self.entry_price = 0
        self.logger = Logger()

        ################################
        # Logging
        self.total_trades = 0
        self.profitable_trades = 0
        self.pnls = []
        ################################

    def enter_position(self, entry_price):

        self.coin_qty = (self.initial_capital +
                         self.net_profit) * self.leverage / entry_price

        self.entry_price = entry_price
        self.total_trades += 1

    def update_net_profit(self, market_price, long=True):

        self.net_profit = self.pnl(
            self.entry_price, market_price, self.coin_qty, long)

    def exit_position(self, exit_price, percentage=1, long=True):

        self.update_net_profit(exit_price, long)
        self.initial_capital += self.net_profit * percentage
        self.coin_qty -= self.coin_qty * percentage

    def get_balance(self):

        return self.initial_capital

    def pnl(self, entry_price, exit_price, quantity, long=True):

        direction = 1 if long else -1

        pnl_value = (exit_price - entry_price) * direction * quantity

        ################################
        # Logging
        if pnl_value > 0:

            self.profitable_trades += 1

        self.pnls.append(pnl_value)
        ################################

        return pnl_value

    ################################
    # Logging
    def get_max_profit(self):

        return max(self.pnls)

    def get_max_loss(self):

        return min(self.pnls)
    ################################

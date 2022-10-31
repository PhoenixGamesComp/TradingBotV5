def long_open(close, supertrend, dema, upper_fbb):

    long_entry = supertrend.astype(object) and \
        (close > dema).astype(object) and \
        (close < upper_fbb).astype(object)

    return long_entry


def long_close(close, supertrend, upper_fbb):

    long_exit = not supertrend.astype(object) or \
        (close > upper_fbb).astype(object)

    return long_exit


def long_stoploss(close, supertrend_lowerband):

    return (close < supertrend_lowerband).astype(object)


def short_open(close, supertrend, dema, lower_fbb):

    short_entry = not supertrend.astype(object) and \
        (close < dema).astype(object) and \
        (close > lower_fbb).astype(object)

    return short_entry


def short_close(close, supertrend, lower_fbb):

    short_exit = supertrend.astype(object) or \
        (close < lower_fbb).astype(object)

    return short_exit


def short_stoploss(close, supertrend_upperband):

    return (close > supertrend_upperband).astype(object)


def take_profit(long, entry_price, market_price, percentage):

    if long:

        return (market_price >= entry_price * (1 + percentage)).astype(object)

    else:

        return (market_price <= entry_price * (1 - percentage)).astype(object)


def stop_loss(long, entry_price, market_price, percentage):

    if long:

        return (market_price <= entry_price * (1 - percentage)).astype(object)

    else:

        return (market_price >= entry_price * (1 + percentage)).astype(object)

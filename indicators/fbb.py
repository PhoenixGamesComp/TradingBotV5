def fbb(data, source='hlc3', time_period=200, multiplier=3):

    if source == "hl2":

        tp = (data["high"] + data["low"]) / 2

    elif source == 'hlc3':

        tp = (data["high"] +
              data["low"] + data["close"]) / 3

    elif source == 'ohlc4':

        tp = (data["open"] + data["high"] +
              data["low"] + data["close"]) / 4

    elif source == 'hlcc4':

        tp = (data["high"] + data["low"] +
              data["close"] + data["close"]) / 4

    ma = tp.rolling(time_period).mean()
    sd = multiplier * \
        tp.rolling(time_period).std()
    fbb_up = ma + (1 * sd)
    fbb_down = ma - (1 * sd)

    return fbb_up, fbb_down

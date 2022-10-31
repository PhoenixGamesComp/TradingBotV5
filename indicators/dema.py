def dema(data, time_period=200):

    ema = data["close"].ewm(span=time_period, adjust=False).mean()
    _dema = 2 * ema - \
        ema.ewm(span=time_period, adjust=False).mean()

    return _dema

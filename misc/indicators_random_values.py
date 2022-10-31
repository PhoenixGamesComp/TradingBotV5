import random


def get_random_length():

    return random.randrange(50, 601, 10)


def get_random_supertrend_multi():

    return random.randint(1, 10)


def get_random_supertrend_atr():

    return random.randint(6, 25)


def get_random_fbb_source():

    rand = random.randint(0, 3)
    if rand == 0:

        return "hl2"

    elif rand == 1:

        return "hlc3"

    elif rand == 2:

        return "ohlc4"

    elif rand == 3:

        return "hlcc4"


def get_random_fbb_multi():

    return random.randint(1, 10)


def get_random_take_profit_percentage():

    return round(random.uniform(0.0001, 0.03), 3)


def get_random_daily_max_profit():

    return round(random.uniform(0.01, 0.05), 3)

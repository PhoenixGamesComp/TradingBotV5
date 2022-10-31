class bcolors:

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ascii_symbols:

    TICK = u'\u2713'


class Logger:

    def __init__(self):

        self.log_identifier = "-"
        self.warning_identifier = "*"
        self.error_identifier = "!"

    def __get_identifier(self, symbol, color):

        return bcolors.BOLD + color + "[" + symbol + "]" + bcolors.ENDC + " "

    def print(self, message, end="\n"):

        print(message, end=end)

    def bold(self, message, end="\n"):

        print(bcolors.BOLD + message + bcolors.ENDC, end=end)

    def info(self, message, end="\n"):

        print(self.__get_identifier(
            self.log_identifier, bcolors.OKGREEN) + message, end=end)

    def warn(self, message, end="\n"):

        print(self.__get_identifier(
            self.warning_identifier, bcolors.WARNING) + message, end=end)

    def error(self, message, end="\n"):

        print(self.__get_identifier(
            self.error_identifier, bcolors.FAIL) + message, end=end)

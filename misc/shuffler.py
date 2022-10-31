import random


class Shuffler:

    def __init__(self, length):

        self.length = length
        self.map = []
        for x in range(self.length):

            self.map.append(x)

        random.shuffle(self.map)

    def shuffle(self, data):

        new_data = [data[i] for i in self.map]
        return new_data

    def unshuffle(self, data):

        new_data = [0] * len(data)

        for i in self.map:

            new_data[self.map[i]] = data[i]

        return new_data

    def load_map(self, map):

        self.map = map

import random
from misc.logger import Logger


class Individual:

    def __init__(self, shuffler, genes):

        self.shuffler = shuffler
        self.logger = Logger()
        self.genes = []

        self.rank = 0
        self.crowding_distance = 0
        self.domination_count = 0
        self.dominated_solutions = []
        self.objectives = []

        for gen in genes:

            self.genes.append(gen)

        self.genes = self.shuffler.shuffle(self.genes)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.genes == other.genes
        return False

    def get_dna(self):

        return self.shuffler.unshuffle(self.genes)

    def get_shuffled_dna(self):

        return self.genes

    def dominates(self, other_individual):

        and_condition = True
        or_condition = False

        for first, second in zip(self.objectives, other_individual.objectives):

            and_condition = and_condition and first <= second
            or_condition = or_condition or first < second

        return (and_condition and or_condition)

import random
from misc.logger import Logger


class Genes:

    def __init__(self, shuffler, genes):

        self.shuffler = shuffler
        self.logger = Logger()
        self._genes = []

        for gen in genes:

            self._genes.append(gen)

        self._genes = self.shuffler.shuffle(self._genes)

    def get_dna(self):

        return self.shuffler.unshuffle(self._genes)

    def get_shuffled_dna(self):

        return self._genes

    def mutate(self, mutation_methods):

        if len(mutation_methods) != len(self._genes):

            self.logger.error(
                "Mutation methods length mismatch the length of the genes.")
            return None

        methods = self.shuffler.shuffle(mutation_methods)
        index = random.randint(0, len(methods) - 1)
        self._genes[index] = methods[index]()

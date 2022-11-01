from cProfile import label
import random
import pickle
from genetic_algorithm.individual import Individual
from misc.logger import Logger
import _thread as thread


class Generation:

    def __init__(self, shuffler, generation_methods, population_size, n_parents, mutation_chance, mutation_methods):

        self.shuffler = shuffler
        self.generation_methods = generation_methods
        self.population_size = population_size
        self.n_parents = n_parents
        self.mutation_chance = mutation_chance
        self.mutation_methods = mutation_methods
        self.logger = Logger()
        self.current_generation = 0
        self.population = []

    # Create the generation zero
    def genesis(self):

        for _ in range(self.population_size):

            unit = []

            for method in self.generation_methods:

                unit.append(method())

            self.population.append(Individual(self.shuffler, unit))

    # Split a list to N approximately equal parts
    def split(self, a, n):

        k, m = divmod(len(a), n)
        return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

    def evaluate(self, method):

        self.results = []
        # Iterate through the population
        for unit in self.population:

            # Unpack the dna of each unit and pass it through the method, append the result to the results list
            self.results.append(method(*unit.get_dna()))

        return self.results

    def keep_best_performing(self, top_n):

        # Sort based on results, if results is iterable make it a tuple
        Z = [x for _, x in sorted(
            zip(self.results, self.population), key=lambda x: tuple(
                x[0]) if hasattr(x[0], "__iter__") else x[0], reverse=True)]
        Z = Z[0:top_n]
        return Z

    def get_worst_of_all(self):

        # Get the worst result
        worst_result = min(self.results)
        # Get worst result's index
        worst_result_index = self.results.index(worst_result)

        # Return the worst of all
        return self.population[worst_result_index]

    def crossover(self, best_ones):

        new_population = []

        for _ in range(self.population_size):

            parents = []

            # Get the potential parents
            for i in range(self.n_parents):

                potential_parent = best_ones[random.randint(
                    0, len(best_ones) - 1)]

                while potential_parent in parents:

                    potential_parent = best_ones[random.randint(
                        0, len(best_ones) - 1)]

                parents.append(potential_parent)

            # Split the parent's dna
            for parent in parents:

                parent = self.split(parent.get_shuffled_dna(), self.n_parents)

            child = []

            # Create child based on parents dna
            for x in range(self.n_parents):

                child += parents[x].get_shuffled_dna()

            # Unsuffle child's dna
            child = self.shuffler.unshuffle(child)

            child = Individual(self.shuffler, child)

            # Mutation chance
            if random.random() < self.mutation_chance:

                child.mutate(self.mutation_methods)

            # Add child to the new population
            new_population.append(child)

        # Update population
        self.population = new_population

    def print_results(self):

        # Print results
        self.logger.info("Generation {}:".format(self.current_generation))
        self.logger.bold("Best performing:", end=" ")
        self.logger.print(str(max(self.results)))
        self.logger.bold("Worst performing:", end=" ")
        self.logger.print(str(min(self.results)))
        print()

    def run(self, top_n, generations, evaluation_method):

        self.logger.print(" - Genetic Algorithm Begin - ")

        if self.current_generation == 0:

            self.genesis()

        best_of_all = None
        times_best_one_was_same = 0

        for _ in range(generations):

            # Evaluate the current generation
            self.evaluate(evaluation_method)

            # Print results
            self.print_results()

            best_ones = self.keep_best_performing(top_n)

            # Check how many times the best on was the same
            if best_of_all == best_ones[0]:

                times_best_one_was_same += 1

            else:

                times_best_one_was_same = 0

            # Save the best of all
            best_of_all = best_ones[0]

            # Add a small chance to swap the worst of the best with the worst of all
            if random.random() < 0.001:

                best_ones[-1] = self.get_worst_of_all()

            self.crossover(best_ones)

            # If the best on was the same for more than 10 times force a random mutation
            # to the population
            if times_best_one_was_same >= 10:

                self.population[random.randint(
                    0, len(self.population) - 1)].mutate(self.mutation_methods)

            # Add the previous best of all to the next generation
            self.population.append(best_of_all)

            self.current_generation += 1

        self.evaluate(evaluation_method)
        # Print results
        self.print_results()
        self.logger.print(" - Genetic Algorithm End - ")

    def evaluate_threaded(self, method, n_threads):

        self.results = [None] * n_threads

        # Spit the population in parts equal to the number of threads
        spitted_population = self.split(self.population, n_threads)

        # Iterate through the population
        for i in range(n_threads):

            # Run the evaluation process for each thread
            pass

    def run_threaded(self, top_n, generations, evaluation_method, n_threads):

        self.logger.print(" - Genetic Algorithm Begin - ")

        if self.current_generation == 0:

            self.genesis()

        best_of_all = None
        times_best_one_was_same = 0

        for _ in range(generations):

            pass

    def export(self, filename):

        with open(filename + ".pkl", 'w+b') as f:

            pickle.dump([self.current_generation,
                         self.population,
                         self.shuffler.map], f)

    def load(self, filename):

        with open(filename + ".pkl", 'rb') as f:

            self.current_generation, self.population, m = pickle.load(f)
            self.shuffler.load_map(m)

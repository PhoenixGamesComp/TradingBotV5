from genetic_algorithm.population import Population
from genetic_algorithm.individual import Individual
import random
import operator


class GenericUtils:

    def __init__(self, problem, n_individuals=100):

        self.problem = problem
        self.n_individuals = n_individuals

    def genesis(self):

        population = Population()

        for _ in range(self.n_individuals):

            individual = self.problem.generate_individual()
            self.problem.calculate_objectives(individual)
            population.append(individual)

        return population

    # Split a list to N approximately equal parts
    def split(self, a, n):

        k, m = divmod(len(a), n)
        return list(a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

    def __type_babysitter(self, individual):

        for gene, v_type in zip(individual.genes, self.problem.variables_type):

            gene = v_type(gene)


class GAUtils(GenericUtils):

    def __init__(self, problem, n_individuals=100, n_parents=2,
                 mutation_prob=0.01):

        self.problem = problem
        self.n_individuals = n_individuals
        self.n_parents = n_parents
        self.mutation_prob = mutation_prob
        self.population = Population()

    def evaluate(self, individual):

        # Unpack the dna of individual and pass it through the method,
        # append the result to the results list
        individual.objectives = \
            self.problem.calculate_objectives(*individual.get_dna())

    def keep_best_performing(self, top_n):

        # Sort based on results, if results is iterable make it a tuple
        Z = [x for x in sorted(
            zip(self.population), key=operator.attrgetter("objectives"), reverse=True)]
        Z = Z[0:top_n]
        return Z

    def create_children(self):

        children = Population()
        top_n = int(0.25 * self.n_individuals)
        best_ones = self.keep_best_performing(top_n=top_n)

        # Save the best of all
        best_of_all = best_ones[0]

        # Add a small chance to swap the worst of the best with the worst of all
        if random.random() < 0.001:

            best_ones[-1] = self.get_worst_of_all()

        # Create children population
        # Mutation is handled in the crossover method
        children.population = self.__crossover(best_ones=best_ones)

        # Append the best of all
        children.append(best_of_all)

        return children

    def __crossover(self, best_ones):

        new_population = []

        for _ in range(self.n_individuals):

            parents = Population()

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
            child = self.problem.shuffler.unshuffle(child)

            child = Individual(self.problem.shuffler, child)

            # Mutation chance
            if random.random() < self.mutation_prob:

                self.__mutate(child)

            # Add child to the new population
            new_population.append(child)

        # Return new population
        return new_population

    def get_worst_of_all(self):

        # Get the worst result
        worst_result = min(
            self.population, key=operator.attrgetter("objectives"))

        return worst_result

    def __mutate(self, individual):

        n_mutations = random.randint(0, len(individual.get_dna()))
        mutated_indeces = []

        for _ in range(n_mutations):

            mutation_index = random.randint(0, len(individual.get_dna()))

            # Make sure every mutation is happening on different index
            while mutation_index in mutated_indeces:

                mutation_index = random.randint(0, len(individual.get_dna()))

            individual.genes[mutation_index] = \
                self.problem.mutation_methods[mutation_index]()


class NSGA2Utils(GenericUtils):

    def __init__(self, problem, n_individuals=100, n_tour_participants=2,
                 tournament_prob=0.9, crossover_param=2, mutation_param=5):

        self.problem = problem
        self.num_of_individuals = n_individuals
        self.num_of_tour_particips = n_tour_participants
        self.tournament_prob = tournament_prob
        self.crossover_param = crossover_param
        self.mutation_param = mutation_param

    # Fast non dominated sorting
    def fast_nondominated_sort(self, population):

        population.fronts = [[]]
        for individual in population:

            individual.domination_count = 0
            individual.dominated_solutions = []
            for other_individual in population:

                if individual.dominates(other_individual):

                    individual.dominated_solutions.append(other_individual)

                elif other_individual.dominates(individual):

                    individual.domination_count += 1

            if individual.domination_count == 0:

                individual.rank = 0
                population.fronts[0].append(individual)

        i = 0
        while len(population.fronts[i]) > 0:

            temp = []
            for individual in population.fronts[i]:

                for other_individual in individual.dominated_solutions:

                    other_individual.domination_count -= 1

                    if other_individual.domination_count == 0:

                        other_individual.rank = i+1
                        temp.append(other_individual)
            i = i+1
            population.fronts.append(temp)

    # Calculate the average distance of its two neighboring solutions
    def calculate_crowding_distance(self, front):

        if len(front) > 0:

            solutions_num = len(front)
            for individual in front:

                individual.crowding_distance = 0

            for m in range(len(front[0].objectives)):

                front.sort(key=lambda individual: individual.objectives[m])
                front[0].crowding_distance = 10**9
                front[solutions_num-1].crowding_distance = 10**9
                m_values = [individual.objectives[m] for individual in front]
                scale = max(m_values) - min(m_values)
                if scale == 0:

                    scale = 1

                for i in range(1, solutions_num-1):

                    front[i].crowding_distance += (
                        front[i+1].objectives[m] - front[i-1].objectives[m])/scale

    def crowding_operator(self, individual, other_individual):

        if (individual.rank < other_individual.rank) or \
                ((individual.rank == other_individual.rank) and (individual.crowding_distance > other_individual.crowding_distance)):

            return 1

        else:

            return -1

    def create_children(self, population):

        children = []
        while len(children) < len(population):

            parent1 = self.__tournament(population)
            parent2 = parent1
            while parent1 == parent2:

                parent2 = self.__tournament(population)

            child1, child2 = self.__crossover(parent1, parent2)
            self.__mutate(child1)
            self.__mutate(child2)
            self.problem.calculate_objectives(child1)
            self.problem.calculate_objectives(child2)
            self.__type_babysitter(child1)
            self.__type_babysitter(child2)
            children.append(child1)
            children.append(child2)

        return children

    def __crossover(self, individual1, individual2):

        child1 = self.problem.generate_individual()
        child2 = self.problem.generate_individual()
        num_of_features = len(child1.features)
        genes_indexes = range(num_of_features)
        for i in genes_indexes:

            beta = self.__get_beta()
            x1 = (individual1.features[i] + individual2.features[i])/2
            x2 = abs((individual1.features[i] - individual2.features[i])/2)
            child1.features[i] = x1 + beta*x2
            child2.features[i] = x1 - beta*x2

        return child1, child2

    def __get_beta(self):

        u = random.random()
        if u <= 0.5:

            return (2*u)**(1/(self.crossover_param+1))

        return (2*(1-u))**(-1/(self.crossover_param+1))

    def __mutate(self, child):

        num_of_features = len(child.features)
        for gene in range(num_of_features):

            u, delta = self.__get_delta()
            if u < 0.5:

                child.features[gene] += delta * \
                    (child.features[gene] -
                     self.problem.variables_range[gene][0])
            else:

                child.features[gene] += delta * \
                    (self.problem.variables_range[gene]
                     [1] - child.features[gene])

            if child.features[gene] < self.problem.variables_range[gene][0]:

                child.features[gene] = self.problem.variables_range[gene][0]

            elif child.features[gene] > self.problem.variables_range[gene][1]:

                child.features[gene] = self.problem.variables_range[gene][1]

    def __get_delta(self):

        u = random.random()
        if u < 0.5:

            return u, (2*u)**(1/(self.mutation_param + 1)) - 1

        return u, 1 - (2*(1-u))**(1/(self.mutation_param + 1))

    def __tournament(self, population):

        participants = random.sample(
            population.population, self.num_of_tour_particips)
        best = None
        for participant in participants:

            if best is None or (self.crowding_operator(participant, best) == 1 and self.__choose_with_prob(self.tournament_prob)):

                best = participant

        return best

    def __choose_with_prob(self, prob):

        if random.random() <= prob:

            return True

        return False

from genetic_algorithm.individual import Individual


class Problem:

    def __init__(self, shuffler, objectives,
                 n_variables, variables_range, variables_type,
                 generation_methods,
                 expand=True, same_range=False, same_type=False):

        self.shuffler = shuffler
        self.n_objectives = len(objectives)
        self.n_variables = n_variables
        self.objectives = objectives
        self.expand = expand
        self.generation_methods = generation_methods
        self.variables_range = []
        self.variables_type = []

        # Handle variables' range
        if same_range:

            for _ in range(n_variables):

                self.variables_range.append(variables_range[0])

        else:

            self.variables_range = variables_range

        # Handle variables' type
        if same_type:

            for _ in range(n_variables):

                self.variables_type.append(variables_type[0])

        else:

            self.variables_type = variables_type

    def generate_individual(self):

        genes = []

        for method in self.generation_methods:

            genes.append(method())

        return Individual(self.shuffler, genes)

    def calculate_objectives(self, individual):

        if self.expand:
            individual.objectives = [f(*individual.features)
                                     for f in self.objectives]
        else:
            individual.objectives = [f(individual.features)
                                     for f in self.objectives]

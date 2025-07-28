from random import random, uniform


class Problem:
    def __init__(self, dim, lower_bound, upper_bound, fitness_function):
        self.dim = dim
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.fitness = fitness_function

    def in_bounds(self, x): return all([self.lower_bound <= k <= self.upper_bound for k in x])

    def distance_util(self, x1, x2): return sum((x1[k] - x2[k]) ** 2 for k in range(self.dim)) ** 0.5

    def position_to_tag(self, fl):
        """
        We want to transform every position in space into the percentage of the problem landscape that it is
        contained by. There are two important things to note:
        - Particles are allowed out of bounds, but we calculate this percentage according to the bounds. So we
          consider all out of bounds positions to be one location (the 0th location)
        - However, we don't want to confuse the real 0th position and out of bounds locations. So we add 1 to
          all position tags, so that 0s become 1s, and out of bounds become 0s.
        """
        p = round((fl - self.lower_bound) / (self.upper_bound - self.lower_bound) * 100) + 1
        if p < 0:
            p = 0
        return "{:03}".format(p)


class IndicatorCollector:
    def __init__(self, n, problem: Problem):
        self.problem = problem
        self.n = n
        self.trajectories = []
        self.network = [[0] * n] * n
        self.mobilities = []
        self.f_percents = []
        self.fitnesses = []
        self.diversities = []

    def stn(self, run_substitute, fitness1, position1, fitness2, position2):
        self.trajectories.append([run_substitute, fitness1, position1, fitness2, position2])

    def interaction_network(self, index_1, index_2):
        self.network[index_1][index_2] += 1
        self.network[index_2][index_1] += 1

    def mobility(self, i, gb_position, particle_position):
        self.mobilities.append([i, self.problem.distance_util(gb_position, particle_position)])

    def diversity(self, population):
        x_ = [sum(p.position[j] for p in population) / self.n for j in range(self.problem.dim)]
        n_sum = sum([self.problem.distance_util(population[i].position, x_) for i in range(self.n)])
        self.diversities.append(n_sum / self.n)

    def f_percent(self, population):
        outside = sum(not self.problem.in_bounds(p.position) for p in population)
        self.f_percents.append(outside / self.n * 100)

    def fitness_csv(self, gb_fitness):
        self.fitnesses.append(gb_fitness)

    def write_to_path(self, path, iterations, solution_index, true_global_best_fitness):
        def write_to_csv(filename, data):
            with open(f"{path}/{filename}.csv", "w") as file:
                file.write(f"iteration,{filename}\n")
                for k in range(500):
                    file.write(f"{k},{data[k]}\n")

        write_to_csv("diversity", self.diversities)
        write_to_csv("fitnesses", self.fitnesses)
        write_to_csv("mobility", self.mobilities)
        write_to_csv("f_percent", self.f_percents)

        with open(f"{path}/stn.csv", "w") as f:
            f.write("Run,Fitness1,Solution1,Fitness2,Solution2\n")
            for i, f1, s1, f2, s2 in self.trajectories:
                s1_string = "".join([self.problem.position_to_tag(p) for p in s1])
                s2_string = "".join([self.problem.position_to_tag(p) for p in s2])
                f.write(f"{i},{f1},{s1_string},{f2},{s2_string}\n")

        with open(f"{path}/interaction_network.txt", "w") as f:
            empty_network = [[0] * self.n] * self.n
            empty_network_string = " ".join(map(str, [digit for sublist in empty_network for digit in sublist]))
            network_string = " ".join(map(str, [digit for sublist in self.network for digit in sublist]))
            f.write(f"ig:#0 {empty_network_string}\n")
            f.write(f"ig:#1 {network_string}\n")

        with open(f"{path}/metadata.json", "w") as f:
            f.write(
                '{"total_iterations": "' + str(iterations) + '", "solution_index": "' + str(
                    solution_index) + '", "global_best_fitness": "' + str(true_global_best_fitness) + '"}')


class Particle:
    def __init__(self, parameters, problem: Problem, indicator_collector: IndicatorCollector):
        self.w, self.c1, self.c2 = parameters
        self.position = [uniform(problem.lower_bound, problem.upper_bound) for _ in range(problem.dim)]
        self.velocity = [0] * problem.dim
        self.fitness = problem.fitness(self.position)
        self.personal_best = self.position.copy()
        self.personal_best_fitness = self.fitness
        self.problem = problem
        self.indicator_collector = indicator_collector

    def update_personal_best(self):
        if self.fitness < self.personal_best_fitness:
            self.personal_best = self.position.copy()
            self.personal_best_fitness = self.fitness

    def update(self, gb_position, p_i, gbi_i):
        r1 = [random() for _ in range(self.problem.dim)]
        r2 = [random() for _ in range(self.problem.dim)]
        old_fitness = self.fitness
        old_position = self.position.copy()
        w, c1, c2 = self.w, self.c1, self.c2
        for k in range(self.problem.dim):
            cognitive = c1 * r1[k] * (self.personal_best[k] - self.position[k])
            social = c2 * r2[k] * (gb_position[k] - self.position[k])
            self.velocity[k] = w * self.velocity[k] + social + cognitive
            self.position[k] += self.velocity[k]
        self.fitness = self.problem.fitness(self.position)
        self.indicator_collector.interaction_network(p_i, gbi_i)
        self.indicator_collector.stn(p_i, old_fitness, old_position, self.fitness, self.position)

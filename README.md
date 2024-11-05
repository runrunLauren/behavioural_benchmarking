# "Survey and analysis of metaheuristic search behavior characterization: a case study on Particle Swarm Optimization variants"

All the code used to calculate and analyse the indicators for the paper as titled above is contained in the folder 
`/paper_related_files`. 
The file `indicator_calculation.ipynb` processes the raw experiment data into search behaviour indicators, which are saved 
to a CSV file.
It also explains how to make use of the raw experiment data provided at [Zenodo](https://zenodo.org/records/14917336?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImM0YzVmNDhkLWZmNzMtNGJmMi05ZGU0LTY0NDQzMTRiYzdjNiIsImRhdGEiOnt9LCJyYW5kb20iOiJkMjg0YmI1ZGJiM2ZlYzY2YzQzZjljMGNmZTdmYTUyNyJ9.TTB5ayu4Pg7W7am4h66z4V7WnMNLEyOu5QQ_fvK5T4Ir4JkdFVqnjI9bF0PM1fZPQKoHelTsj8G3VFZYrUj_cQ).
The file `RQ1.ipynb` evaluates RQ1 in the paper, namely 'Does the indicator distinguish between 
metaheuristics exhibiting different behaviour?'
The results from the statistical tests in RQ1 are provided in `RQ1_KS_results.csv`.
The file `RQ2.ipynb` evaluates RQ2 in the paper, namely 'Is the indicator distinct from all other indicators?'
The results from the statistical tests in RQ2 are provided in `RQ2_Pearson_results.csv`.

---

# Numerical indicators of the search behaviour of metaheuristics

This repository contains code for the calculation of 25 numerical indicators 
of algorithm search behaviour. For details on these indicators, refer to the 
citation: (under review).

The indicators included here are:

- Diversity Rate of Change Type A and B (DRoC Type A, DRoC Type B)
- ERT Diversity, Critical Diversity
- Fitness Rate of Change (FRoC Type A,  ARoC B)
- ERT Fitness, Critical Fitness
- Separation Rate of Change (SRoC) (Types A and B)
- ERT Separation, Critical Separation
- Mobility Rate of Change (SRoC) (Types A and B)
- ERT Mobility, Critical Mobility
- ntotal, nbest, nshared, best-strength (via [stnpy](https://github.com/runrunLauren/stnpy))
- Mean Interaction Diversity (Mean ID), Mean Giant Component (Mean GC), Influence Strength of Solution (ISS) (with help from [Interaction Networks](https://github.com/macoj/swarm_interaction_network))
- EXPLORE%
- INFEASIBLE%
 
## Quickstart

There is a simple Jupyter notebook used for testing the indicators, namely
`illustrate_and_test.ipynb`. This illustrates where the indicators come 
from, and also shows all the `get_` functions.


## Data preparation

There are a couple of files required to calculate all the indicators. See `example_data/` for an instance of 
each file required. For the purposes of explaining the files, assume that you
have run a metaheuristic on a minimising benchmark problem, logging 
information along the way.

### metadata.json

This is the only file that is strictly required. It is a json file, with 
entries for the number of iterations the experiment ran for 
(`total_iterations`), the best known 
fitness value in the benchmark problem landscape (`global_best_fitness`), and
the position of the final solution of the experiment w.r.t. the population (`
solution_index`).

### diversity.csv, separation.csv, fitness.csv, mobility.csv

These three files are very similar in presentation and preparation. Each csv
file contains three columns. The first is "iteration" and the second 
corresponds to either "diversity", "separation", or "fitness". 
### diversity.csv, fitness.csv, mobility.csv, f_percent.csv

These four files are very similar in presentation and preparation. Each csv
file contains three columns. The first column is "iteration", and the second column  
corresponds to either "diversity", "fitness", "mobility", or "f_percent". 

At the end of every iteration of the experiment, you calculate the diversity 
of the population. Refer to the paper for more information on diversity 
measures. The iteration and diversity are logged to `diversity.csv`.

Similarly, at the end of every iteration, the current shortest known distance 
to the global best position is logged to `separation.csv`. And to mirror this, 
the current best known fitness value is logged to `fitness.csv`.
When the best known fitness value is updated, then the distance between the location 
of the previous best known fitness value, and the location of the new best known 
fitness value, is logged to `mobility.csv`.

Every iteration, the `F%` of the population is calculated. Please refer to the paper 
for information on calculating `F%`.
This value is logged to `f_percent.csv`.

These files contain a single run each.

### stn.csv

For the Search Trajectory Networks (STN), the `stnpy` 
[package](https://github.com/runrunLauren/stnpy) is used. The file format 
follows the style given in the original publication, see 
[here](https://github.com/gabro8a/STNs). This style is csv with columns:

`Run,Fitness1,Solution1,Fitness2,Solution2`.

Traditionally STNs expect multiple runs of single individuals to be used. 
In order to create an STN with only a single run, an adaptation is made.
This adaptation is to consider each individual in the population as a "run" 
when calculating the STN.
As such, log each individual as if it is its own run, with its index within the 
population serving as it's run number.

For each individual in the population, each move it makes must be logged. 
For an individual with index 6 moving from point A (fitness 30) to point B 
(fitness 20), log the following:

`6,30,A,30,B`

In the next iteration, the individual will make another move, this time 
starting at B.

In reality, points A and B are more likely to be positions in real, 
multidimensional space, e.g. `[12.65, 945.30, -2.55]`. STNs deal with this
by converting large, multidimensional spaces into discrete `locations`. 
Please refer to the paper for detail. We recommend transforming every 
dimension in any benchmark problem to be 100 locations wide. This can be 
achieved by dividing the distance into 100 equal parts. Any position within
the benchmark landscape can then be mapped to its location within the space, 
by considering what "percentile" of the distance it is in.
The result is that all landscapes become sets of discrete locations to the 
size of `100^D`, which is much smaller than real space.

All positions will now look something like `A = [12, 30, 90]`, which can be 
padded with zeroes and transformed to be a unique position identifier:

`012030090`

### interaction_network.txt

For this we reference 
[Interaction Networks](https://github.com/macoj/swarm_interaction_network). 
We will be using the file specification that this author uses, with some 
additional limitations. The author allows flexibility when creating INs, but
in this case we expect the IN to be created at the end of optimisation, 
without visibility into what happened inbetween. For this reason, the file 
looks as follows:

```
ig:#0 <zeroes>
ig:#1 <interaction encoding>
```

By `<zeroes>`, it is meant that if you have a population of size 5, and each 
individual has a zero relationship with every other individual:

```
   0 1 2 3 4
 ____________
0| 0 0 0 0 0
1| 0 0 0 0 0
2| 0 0 0 0 0
3| 0 0 0 0 0
4| 0 0 0 0 0
```

Becomes 5 x 5 = 25 zeroes in a row.
```
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
```

By `<interaction encoding>`, it is meant that the same grid now denotes how 
many times each individual interacted with another, see paper for more info.
E.g.

```
    0  1  2  3  4
 _________________
0|  4  2 12  0  7
1| 10  0  8  0  0
2|  0 16  0  0 10
3|  9  0  1  0  0
4|  1  3  0  0  1
```
This becomes:
```
4 2 12 0 7 10 0 8 0 0 0 16 0 0 10 9 0 1 0 0 1 3 0 0 1
```

Resulting in an `interaction.txt` file like:
```
ig:#0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
ig:#1 4 2 12 0 7 10 0 8 0 0 0 16 0 0 10 9 0 1 0 0 1 3 0 0 1
```

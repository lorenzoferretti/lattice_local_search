from lattice_data import Lattice
from lattice_synthesis import FakeSynthesis
import lattice_utils
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import copy

# Read dataset
conn = sqlite3.connect('./datasets/ChenIDCt.db')
synthesis_result = conn.execute('select latencies, ffs from ChenIDCt').fetchall()
configurations = conn.execute('select accuracy_loops, column_loops, row_loops, bundle_b from ChenIDCt').fetchall()

# Define DS
feature_sets = [[0, 2, 4, 8, 16, 32, 64], [0, 2, 4, 8], [0, 2, 4, 8], [0, 1]]

# Create Lattice
lattice = Lattice(feature_sets, 1)

# Probabilistic sample according to beta distribution
samples = lattice.beta_sampling(0.1, 0.1, 22)


# Populate the tree with the initial sampled values
lattice.lattice.populate_tree(samples)
lattice.lattice.print_tree()
n_of_synthesis = len(samples)

# Synthesise sampled configuration
hls = FakeSynthesis(synthesis_result, configurations, lattice)
sampled_configuration_synthesised = []
for s in samples:
    sampled_configuration_synthesised.append(hls.synthesise_configuration(s))

# Get pareto frontier
# pareto_frontier, pareto_frontier_idx = lattice_utils.pareto_frontier2d(sampled_configuration_synthesised)
pareto_frontier, pareto_frontier_idx = lattice_utils.pareto_frontier2d(sampled_configuration_synthesised)
# Get exhaustive pareto frontier (known only if ground truth exists)
# pareto_frontier_exhaustive, pareto_frontier_exhaustive_idx = lattice_utils.pareto_frontier2d(synthesis_result)
pareto_frontier_exhaustive, pareto_frontier_exhaustive_idx = lattice_utils.pareto_frontier2d(synthesis_result)

pareto_frontier_before_exploration = copy.deepcopy(pareto_frontier)
# PLOT start
for p in sampled_configuration_synthesised:
    plt.scatter(p[0], p[1], color='b')

for pp in pareto_frontier_exhaustive:
    plt.scatter(pp[0], pp[1], color='r')

for pp in pareto_frontier:
    plt.scatter(pp[0], pp[1], color='g')

plt.grid()
# plt.draw()
# PLOT end

# Calculate ADRS
adrs_evolution = []
adrs = lattice_utils.adrs2d(pareto_frontier_exhaustive, pareto_frontier)
adrs_evolution.append(adrs)
print adrs

max_radius = (0,0)
# Start the exploration

# Select randomly a pareto configuration and find explore his neighbour
r = np.random.randint(0, len(pareto_frontier))
pareto_configurations = [samples[i] for i in pareto_frontier_idx]
configuration_to_explore = pareto_configurations[r]
new_configuration, max_radius = lattice.lattice.closest_neighbour2(configuration_to_explore, lattice, max_radius)
print lattice.lattice.get_n_of_children()

while new_configuration is not None:
    # Synthesise configuration
    new_config_synthesised = hls.synthesise_configuration(new_configuration)
    # Update known synthesis values and configurations(only pareto + the new one)
    pareto_frontier.append(new_config_synthesised)
    pareto_configurations.append(new_configuration)
    # Add configuration to the tree
    lattice.lattice.add_config(new_configuration)
    # Get pareto frontier
    pareto_frontier, pareto_frontier_idx = lattice_utils.pareto_frontier2d(pareto_frontier)
    pareto_configurations = [pareto_configurations[j] for j in pareto_frontier_idx]
    # Calculate ADRS
    adrs = lattice_utils.adrs2d(pareto_frontier_exhaustive, pareto_frontier)
    adrs_evolution.append(adrs)
    if adrs == 0:
        break
    # Find new configuration to explore
    # Select randomly a pareto configuration and find explore his neighbour
    r = np.random.randint(0, len(pareto_frontier))
    configuration_to_explore = pareto_configurations[r]
    print configuration_to_explore
    if configuration_to_explore is None:
        print configuration_to_explore
    new_configuration, max_radius = lattice.lattice.closest_neighbour2(configuration_to_explore, lattice, max_radius)
    if new_configuration is None:
        print "Exploration terminated"
        break
    if max_radius == lattice.max_distance:
        print "Exploration terminated, max radius reached"
        break
    n_of_synthesis += 1

lattice.lattice.print_tree()
print lattice.lattice.get_n_of_children()
print "Final adrs:", adrs_evolution[-1]
print "Max radius: ", max_radius[0]
print "Max idx: ", max_radius[1]

fig1 = plt.figure()
for p in sampled_configuration_synthesised:
    plt.scatter(p[0], p[1], color='b')

for pp in pareto_frontier_exhaustive:
    plt.scatter(pp[0], pp[1], color='r', s=40)

for pp in pareto_frontier:
    plt.scatter(pp[0], pp[1], color='g')

# plt.draw()

print "Pareto frontier discovered:", len(pareto_frontier)

fig2 = plt.figure()
plt.grid()
pareto_frontier.sort(key=lambda x: x[0])
plt.step([i[0] for i in pareto_frontier], [i[1] for i in pareto_frontier], where='post', color='r')
pareto_frontier_before_exploration.sort(key=lambda x: x[0])
plt.step([i[0] for i in pareto_frontier_before_exploration], [i[1] for i in pareto_frontier_before_exploration], where='post', color='b')
# plt.draw()

fig3 = plt.figure()
plt.grid()
plt.plot(adrs_evolution)
# plt.show()

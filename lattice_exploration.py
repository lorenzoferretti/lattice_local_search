from lattice_data import Lattice
from lattice_synthesis import FakeSynthesis
from lattice_ds_point import DSpoint
from lattice_sphere_tree import SphereTree as st
import lattice_utils
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import copy

# Read dataset
conn = sqlite3.connect('./datasets/ChenIDCt.db')
synthesis_result = conn.execute('select latencies, ffs from ChenIDCt').fetchall()
configurations = conn.execute('select accuracy_loops, column_loops, row_loops, bundle_b from ChenIDCt').fetchall()
entire_ds = []
for i in xrange(len(synthesis_result)):
    entire_ds.append(DSpoint(synthesis_result[i][0], synthesis_result[i][1], list(configurations[i])))

# Define DS
feature_sets = [[0, 2, 4, 8, 16, 32, 64], [0, 2, 4, 8], [0, 2, 4, 8], [0, 1]]

# Create Lattice
lattice = Lattice(feature_sets, 4)

# Probabilistic sample according to beta distribution
samples = lattice.beta_sampling(0.1, 0.1, 22)


# Populate the tree with the initial sampled values
lattice.lattice.populate_tree(samples)
lattice.lattice.print_tree("lattice")
n_of_synthesis = len(samples)
lattice.lattice.print_tree("lattice")

# Synthesise sampled configuration
hls = FakeSynthesis(entire_ds, lattice)
sampled_configurations_synthesised = []
for s in samples:
    latency, area = hls.synthesise_configuration(s)
    synthesised_configuration = DSpoint(latency, area, s)
    # sampled_configuration_synthesised.append(hls.synthesise_configuration(s))
    sampled_configurations_synthesised.append(synthesised_configuration)

# Get pareto frontier
# pareto_frontier, pareto_frontier_idx = lattice_utils.pareto_frontier2d(sampled_configuration_synthesised)
pareto_frontier, pareto_frontier_idx = lattice_utils.pareto_frontier2d(sampled_configurations_synthesised)
# Get exhaustive pareto frontier (known only if ground truth exists)
# pareto_frontier_exhaustive, pareto_frontier_exhaustive_idx = lattice_utils.pareto_frontier2d(synthesis_result)
pareto_frontier_exhaustive, pareto_frontier_exhaustive_idx = lattice_utils.pareto_frontier2d(entire_ds)

pareto_frontier_before_exploration = copy.deepcopy(pareto_frontier)
# PLOT start
for p in sampled_configurations_synthesised:
    plt.scatter(p.latency, p.area, color='b')

for pp in pareto_frontier_exhaustive:
    plt.scatter(pp.latency, pp.area, color='r')

for pp in pareto_frontier:
    plt.scatter(pp.latency, pp.area, color='g')

plt.grid()
# plt.draw()
# PLOT end

# Calculate ADRS
adrs_evolution = []
adrs = lattice_utils.adrs2d(pareto_frontier_exhaustive, pareto_frontier)
adrs_evolution.append(adrs)
print adrs

max_radius = 0
# Start the exploration

# Select randomly a pareto configuration and find explore his neighbour
r = np.random.randint(0, len(pareto_frontier))
pareto_configurations = [samples[i] for i in pareto_frontier_idx]
configuration_to_explore = pareto_configurations[r]
sphere = st(configuration_to_explore, lattice)
# new_configurations = sphere.sphere_elements
# new_configuration_distances = sphere.closest_distances
# new_configurations_idx = sphere.closest_elements_idx
new_configuration = sphere.random_closest_element
max_radius = sphere.radius
# new_configuration, max_radius = lattice.lattice.closest_neighbour2(configuration_to_explore, lattice, max_radius)
print lattice.lattice.get_n_of_children()

while new_configuration is not None:
    print "____"*30
    # Synthesise configuration
    latency, area = hls.synthesise_configuration(new_configuration)

    # Generate a new design point
    ds_point = DSpoint(latency, area, new_configuration)

    # Update known synthesis values and configurations(only pareto + the new one)

    pareto_frontier.append(ds_point)
    # pareto_configurations.append(new_configuration)
    # Add configuration to the tree
    lattice.lattice.add_config(ds_point.configuration)
    # Get pareto frontier
    pareto_frontier, pareto_frontier_idx = lattice_utils.pareto_frontier2d(pareto_frontier)
    # pareto_configurations = [pareto_configurations[j] for j in pareto_frontier_idx]
    # Calculate ADRS
    adrs = lattice_utils.adrs2d(pareto_frontier_exhaustive, pareto_frontier)
    adrs_evolution.append(adrs)
    if adrs == 0:
        break
    # Find new configuration to explore
    # Select randomly a pareto configuration and find explore his neighbour
    r = np.random.randint(0, len(pareto_frontier))
    print "Random pareto: ", r
    # pareto_frontier_idx_to_explore = pareto_frontier_idx[r]
    # print "# pareto element: ", len(pareto_frontier_idx), "r: ", r, "pareto_idx: ", pareto_frontier_idx_to_explore
    pareto_solution_to_explore = pareto_frontier[r].configuration
    # print configuration_to_explore
    # if configuration_to_explore is None:
    #     print configuration_to_explore
    print "Config to explore: ", pareto_solution_to_explore
    lattice.lattice.print_tree("lattice")
    sphere = st(pareto_solution_to_explore, lattice)
    print "sphere.sphere_elements:", [i.get_data() for i in sphere.sphere_elements]
    new_configuration = sphere.random_closest_element
    max_radius = max(max_radius, sphere.radius)
    # new_configuration, max_radius = lattice.lattice.closest_neighbour2(pareto_solution_to_explore.configuration, lattice, max_radius)
    if new_configuration is None:
        print "Exploration terminated"
        break
    if max_radius > lattice.max_distance:
        print "Exploration terminated, max radius reached"
        break
    n_of_synthesis += 1
    print lattice.lattice.get_n_of_children()
    print sphere.radius
    print adrs
    pass

lattice.lattice.print_tree("lattice")
print lattice.lattice.get_n_of_children()
print "Final adrs:", adrs_evolution[-1]
print "Max radius: ", max_radius
# print "Max idx: ", max_radius[1]

fig1 = plt.figure()
for p in sampled_configurations_synthesised:
    plt.scatter(p.latency, p.area, color='b')

for pp in pareto_frontier_exhaustive:
    plt.scatter(pp.latency, pp.area, color='r', s=40)

for pp in pareto_frontier:
    plt.scatter(pp.latency, pp.area, color='g')

# plt.draw()

print "Pareto frontier discovered:", len(pareto_frontier)

fig2 = plt.figure()
plt.grid()
pareto_frontier.sort(key=lambda x: x.latency)
plt.step([i.latency for i in pareto_frontier], [i.area for i in pareto_frontier], where='post', color='r')
pareto_frontier_before_exploration.sort(key=lambda x: x.latency)
plt.step([i.latency for i in pareto_frontier_before_exploration], [i.area for i in pareto_frontier_before_exploration], where='post', color='b')
# plt.draw()

fig3 = plt.figure()
plt.grid()
plt.plot(adrs_evolution)
# plt.show()

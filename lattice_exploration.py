from lattice_data import Lattice
from lattice_synthesis import VivdoHLS_Synthesis
from lattice_ds_point import DSpoint
from lattice_sphere_tree import SphereTree as st
import lattice_utils
import datasets
import matplotlib.pyplot as plt
import numpy as np
import copy

# Read dataset
# ChenIDCt = datasets.Datasets("ChenIDCt")
# synthesis_result = ChenIDCt.benchmark_synthesis_results
# configurations = ChenIDCt.benchmark_configurations
# feature_sets = ChenIDCt.benchmark_feature_sets
#
# entire_ds = []
# for i in xrange(len(synthesis_result)):
#     entire_ds.append(DSpoint(synthesis_result[i][0], synthesis_result[i][1], list(configurations[i])))

Autocorrelation_extended = datasets.Datasets("Autocorrelation_extended")
feature_sets = [i[1] for i in Autocorrelation_extended.autcorrelation_extended_directives_ordered]

# While used to run the experiments multiple times
n_of_runs = 1
if n_of_runs > 1:
    plot_chart = False
else:
    plot_chart = True

collected_run = []
for run in xrange(n_of_runs):
    # Create Lattice
    lattice = Lattice(feature_sets, 4)
    max_radius = 0

    # Probabilistic sample according to beta distribution
    samples = lattice.beta_sampling(0.1, 0.1, 20)

    # Populate the tree with the initial sampled values
    lattice.lattice.populate_tree(samples)
    n_of_synthesis = len(samples)

    # Synthesise sampled configuration
    # hls = FakeSynthesis(entire_ds, lattice)
    prj_description = {"prj_name": "Autocorrelation_extended",
                       "test_bench_file": "gsm.c",
                       # "source_folder": "./test_folder",
                       "source_folder": "/home/lpozzi/shared/group_shared/benchmarks/CHStone_v1.11_150204/gsm/SRC_HLS/",
                       "top_function": "Autocorrelation"}

    hls = VivdoHLS_Synthesis(lattice, Autocorrelation_extended.autcorrelation_extended,
                             Autocorrelation_extended.autcorrelation_extended_directives_ordered,
                             Autocorrelation_extended.autcorrelation_extended_bundling,
                             prj_description)
    sampled_configurations_synthesised = []
    for s in samples:
        latency, area = hls.synthesise_configuration(s)
        synthesised_configuration = DSpoint(latency, area, s)
        sampled_configurations_synthesised.append(synthesised_configuration)

    # Get pareto frontier from sampled configuration
    pareto_frontier, pareto_frontier_idx = lattice_utils.pareto_frontier2d(sampled_configurations_synthesised)

    # Get exhaustive pareto frontier (known only if ground truth exists)
    pareto_frontier_exhaustive, pareto_frontier_exhaustive_idx = lattice_utils.pareto_frontier2d(entire_ds)

    pareto_frontier_before_exploration = copy.deepcopy(pareto_frontier)

    # PLOT start
    if plot_chart:
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

    # Select randomly a pareto configuration and find explore his neighbour
    r = np.random.randint(0, len(pareto_frontier))
    pareto_configurations = [samples[i] for i in pareto_frontier_idx]
    configuration_to_explore = pareto_configurations[r]

    # Search locally for the configuration to explore
    sphere = st(configuration_to_explore, lattice)
    new_configuration = sphere.random_closest_element

    # Until there are configurations to explore, try to explore these
    while new_configuration is not None:
        # Synthesise configuration
        latency, area = hls.synthesise_configuration(new_configuration)

        # Generate a new design point
        ds_point = DSpoint(latency, area, new_configuration)

        # Update known synthesis values and configurations(only pareto + the new one)
        pareto_frontier.append(ds_point)

        # Add configuration to the tree
        lattice.lattice.add_config(ds_point.configuration)

        # Get pareto frontier
        pareto_frontier, pareto_frontier_idx = lattice_utils.pareto_frontier2d(pareto_frontier)

        # Calculate ADRS
        adrs = lattice_utils.adrs2d(pareto_frontier_exhaustive, pareto_frontier)
        adrs_evolution.append(adrs)
        if adrs == 0:
            break

        # Find new configuration to explore
        # Select randomly a pareto configuration
        r = np.random.randint(0, len(pareto_frontier))
        pareto_solution_to_explore = pareto_frontier[r].configuration

        # Explore the closer element locally
        sphere = st(pareto_solution_to_explore, lattice)
        new_configuration = sphere.random_closest_element
        max_radius = max(max_radius, sphere.radius)

        if new_configuration is None:
            print "Exploration terminated"
            break
        if max_radius > lattice.max_distance:
            print "Exploration terminated, max radius reached"
            break

        n_of_synthesis += 1

    collected_run.append((n_of_synthesis, adrs_evolution, max_radius))
    n_of_synthesis = 0
    adrs_evolution = []
    max_radius = 0

    if plot_chart:
        fig1 = plt.figure()
        for p in sampled_configurations_synthesised:
            plt.scatter(p.latency, p.area, color='b')

        for pp in pareto_frontier_exhaustive:
            plt.scatter(pp.latency, pp.area, color='r', s=40)

        for pp in pareto_frontier:
            plt.scatter(pp.latency, pp.area, color='g')

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
        plt.show()

# mean_adrs = lattice_utils.get_statistics(collected_run)

# print mean_adrs
# plt.plot(mean_adrs)
# plt.show()

from lattice_data import Lattice
from lattice_synthesis import VivdoHLS_Synthesis
from lattice_synthesis import FakeSynthesis
from lattice_ds_point import DSpoint
from lattice_sphere_tree import SphereTree as st
import lattice_utils
import datasets
import matplotlib.pyplot as plt
import numpy as np
import copy
import sys
import math
import pickle


sys.setrecursionlimit(15200)

# radius = 0.415771953155/2
# radius = 0.415771953155
# radius = 0.826965179554
radius = 2


# Read dataset
# benchmark = ["ChenIDCt", "adpcm_decode", "adpcm_encode", "Autocorrelation", "Reflection_coefficients"]
benchmark = ["ChenIDCt"]
for b in benchmark:
    database = datasets.Datasets(b)
    synthesis_result = database.benchmark_synthesis_results
    configurations = database.benchmark_configurations
    feature_sets = database.benchmark_feature_sets

    entire_ds = []
    for i in xrange(len(synthesis_result)):
        entire_ds.append(DSpoint(synthesis_result[i][0], synthesis_result[i][1], list(configurations[i])))

    # Autocorrelation_extended = datasets.Datasets("Autocorrelation_extended")
    # feature_sets = [i[1] for i in Autocorrelation_extended.autcorrelation_extended_directives_ordered]

    # While used to run the experiments multiple times
    n_of_runs = 100
    if n_of_runs > 1:
        plot_chart = False
    else:
        plot_chart = True

    collected_run = []
    for run in xrange(n_of_runs):
        print "Exploration n: " + str(run)
        max_radius = 0
        # Create Lattice
        lattice = Lattice(feature_sets, radius)

        # To create inital samples
        # samples_dataset = []
        # for i in xrange(100):
        #     # Probabilistic sample according to beta distribution
        #     samples_dataset.append(lattice.beta_sampling(0.1, 0.1, 22))
        #     with open(b + '.pickle', 'wb') as handle:
        #         pickle.dump(samples_dataset, handle, protocol=pickle.HIGHEST_PROTOCOL)

        #To read from already generated samples
        with open(b+'.pickle', 'rb') as handle:
            samples = pickle.load(handle)

        samples = samples[run]

        # Populate the tree with the initial sampled values
        # lattice.lattice.populate_tree(samples)
        n_of_synthesis = len(samples)

        # Synthesise sampled configuration
        hls = FakeSynthesis(entire_ds, lattice)
        # prj_description = {"prj_name": "Autocorrelation_extended",
        #                    "test_bench_file": "gsm.c",
        #"test_bench_file": "tb.c",
        #"source_folder": "./test_folder",
        # "source_folder": "/home/lpozzi/shared/group_shared/benchmarks/CHStone_v1.11_150204/gsm/SRC_HLS/",
        # "top_function": "Autocorrelation"}

        # hls = VivdoHLS_Synthesis(lattice, Autocorrelation_extended.autcorrelation_extended,
        #                          Autocorrelation_extended.autcorrelation_extended_directives_ordered,
        #                          Autocorrelation_extended.autcorrelation_extended_bundling,
        #                          prj_description)

        sampled_configurations_synthesised = []
        # for s in samples:
        # samples = []
        for s in samples:
            # sample = lattice.beta_sampling(0.1, 0.1, 1).pop()
            latency, area = hls.synthesise_configuration(s)
            # samples.append(sample)
            synthesised_configuration = DSpoint(latency, area, s)
            sampled_configurations_synthesised.append(synthesised_configuration)
            # lattice.lattice.add_config(sample)

        # print samples
        # print len(samples)
        # print len(sampled_configurations_synthesised)
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
        # adrs = lattice_utils.adrs2d(pareto_frontier_before_exploration, pareto_frontier)
        # ADRS after initial sampling
        adrs_evolution.append(adrs)

        # Select randomly a pareto configuration and find explore his neighbour
        r = np.random.randint(0, len(pareto_frontier))
        pareto_configurations = [samples[i] for i in pareto_frontier_idx]
        pareto_solution_to_explore = pareto_configurations[r]

        # Search locally for the configuration to explore
        sphere = st(pareto_solution_to_explore, lattice)
        new_configuration = sphere.random_closest_element

        # Selected point distances
        selected_point_distances = []

        # Until there are configurations to explore, try to explore these
        while new_configuration is not None:
            # Synthesise configuration
            latency, area = hls.synthesise_configuration(new_configuration)
            selected_point_distances.append(
                lattice_utils.get_euclidean_distance(pareto_solution_to_explore, new_configuration))
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
            # adrs = lattice_utils.adrs2d(pareto_frontier_before_exploration, pareto_frontier)
            adrs_evolution.append(adrs)
            # if adrs == 0:
            #     break

            # Find new configuration to explore
            # Select randomly a pareto configuration
            search_among_pareto = copy.copy(pareto_frontier)
            while len(search_among_pareto) > 0:
                r = np.random.randint(0, len(search_among_pareto))
                pareto_solution_to_explore = search_among_pareto[r].configuration

                # Explore the closer element locally
                sphere = st(pareto_solution_to_explore, lattice)
                new_configuration = sphere.random_closest_element
                if new_configuration is None:
                    search_among_pareto.pop(r)
                    continue

                max_radius = max(max_radius, sphere.radius)
                if max_radius > lattice.max_distance:
                    search_among_pareto.pop(r)
                    continue

                break

            exit_expl = False
            if len(search_among_pareto) == 0:
                print "Exploration terminated"
                exit_expl = True

            if max_radius > lattice.max_distance:
                print "Exploration terminated, max radius reached"
                exit_expl = True

            if exit_expl:
                break

            n_of_synthesis += 1

        collected_run.append((n_of_synthesis, adrs_evolution, max_radius, selected_point_distances))
        print(max_radius)
        print n_of_synthesis
        # n_of_synthesis = 0
        # max_radius = 0

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

    mean_adrs, radii, final_adrs_mean, avg_distances = lattice_utils.get_statistics(collected_run)
    plt.plot(mean_adrs)
    plt.show()

    data_file = open(b+str(radius)+"_mean_adrs.txt","w")
    data_file.write(str(mean_adrs))
    data_file.close()

    data_file = open(b+str(radius)+"_radii.txt", "w")
    data_file.write(str(radii))
    data_file.close()

    data_file = open(b+str(radius)+"_final_adrs_mean.txt", "w")
    data_file.write(str(final_adrs_mean))
    data_file.close()

    data_file = open(b+str(radius)+"_avg_distances.txt","w")
    data_file.write(str(avg_distances[0]))
    data_file.write("\n")
    data_file.write(str(avg_distances[1]))
    data_file.write("\n")
    data_file.write(str(avg_distances[2]))
    data_file.close()

    # csfont = {'family':'serif','serif':['Times'],'size': 15}
    # matplotlib.rc('font', **csfont)
    # print mean_adrs
    # print final_adrs_mean
    # fig4 = plt.figure(num=None, figsize=(7.25, 5.25), dpi=80, facecolor='w', edgecolor='k')
    # plt.plot(mean_adrs, linewidth=2.0)
    # plt.grid()
    # plt.xlabel("# of synthesis")
    # plt.ylabel("mean ADRS")
    # plt.draw()
    #
    # # boxprops = dict(linewidth=2)
    # fig6 = plt.figure(num=None, figsize=(7.25, 5.25), dpi=80, facecolor='w', edgecolor='k')
    # # box = plt.boxplot(avg_distances)
    # labels = ["ChenIDCt"]
    # plt.boxplot(avg_distances, labels=labels, showfliers=False, widths=(1, 0.5, 1.2, 0.1))
    # plt.grid()
    # # plt.xlabel("# of synthesis", **csfont)
    # plt.ylabel("mean distances")
    # plt.draw()
    #
    # fig5 = plt.figure(num=None, figsize=(7.25, 5.25), dpi=80, facecolor='w', edgecolor='k')
    # # box = plt.boxplot(radii)
    # plt.boxplot(avg_distances, labels=labels, showfliers=False, widths=(1, 0.5, 1.2, 0.1))
    # # box.set(linewidth=2)
    # # plt.xlabel("# of synthesis", **csfont)
    # plt.ylabel("radius")
    # plt.grid()
    # plt.grid(
    # plt.show()

# prova = ((2, [1, 2], 1, [1, 2]),
#        (3, [1, 2, 3], 1, [1, 2]),
#        (5, [1, 2, 3, 4, 5], 3, [1, 2]),
#        (7, [1, 2, 3, 4, 5, 6, 7], 4, [1, 2]))
#
# mean_adrs, radii, final_adrs_mean, avg_distances = lattice_utils.get_statistics(prova)
# print mean_adrs
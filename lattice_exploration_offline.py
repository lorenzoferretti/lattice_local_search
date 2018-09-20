from lattice_data import Lattice
from lattice_synthesis import VivdoHLS_Synthesis
from lattice_synthesis import FakeSynthesis
from lattice_ds_point import DSpoint
from lattice_sphere_tree import SphereTree as st
import lattice_utils
import datasets
import numpy as np
from itertools import izip_longest, imap
import copy
from matplotlib import pyplot as plt

# Set the radius for the exploration
radius = 0.5

# Set number of runs due to the probailisitc initial sampling
n_of_runs = 10

# To plot the ADRS chart
plot = True

# Initial sampling size
intial_sampling_size = 20

# Read dataset

# Specify the list of dataset to explore
# benchmark = ["ChenIDCt", "adpcm_decode", "adpcm_encode", "Autocorrelation", "Reflection_coefficients"]
benchmark = ["ChenIDCt"]
for b in benchmark:
    # Extract data from the database
    database = datasets.Datasets(b)
    synthesis_result = database.benchmark_synthesis_results
    configurations = database.benchmark_configurations
    feature_sets = database.benchmark_feature_sets
    directives = database.benchmark_directives

    # Format data for the exploration
    entire_ds = []
    for i in xrange(len(synthesis_result)):
        entire_ds.append(DSpoint(synthesis_result[i][0], synthesis_result[i][1], list(configurations[i])))

    # Set variables to store exploration data
    adrs_run_history = []
    for run in xrange(n_of_runs):
        print "Exploration n: " + str(run)
        sphere_elements_sizes = []
        max_radius = 0
        # Create Lattice
        lattice = Lattice(feature_sets, radius)

        # Generate inital samples
        samples = lattice.beta_sampling(0.1, 0.1, intial_sampling_size)

        # samples = samples_dataset
        n_of_synthesis = len(samples)

        # Synthesise sampled configuration
        # FakeSynthesis simulates the synthesis process retrieving the configuration from the proper DB
        hls = FakeSynthesis(entire_ds, lattice)
        sampled_configurations_synthesised = []
        for s in samples:
            latency, area = hls.synthesise_configuration(s)
            synthesised_configuration = DSpoint(latency, area, s)
            sampled_configurations_synthesised.append(synthesised_configuration)
            lattice.lattice.add_config(s)

        # After the inital sampling, retrieve the pareto frontier
        pareto_frontier, pareto_frontier_idx = lattice_utils.pareto_frontier2d(sampled_configurations_synthesised)

        # Get exhaustive pareto frontier (known only if ground truth exists)
        pareto_frontier_exhaustive, pareto_frontier_exhaustive_idx = lattice_utils.pareto_frontier2d(entire_ds)

        # Store a copy to save the pareto front before the exploration algorithm
        pareto_frontier_before_exploration = copy.deepcopy(pareto_frontier)

        # Calculate ADRS
        adrs_evolution = []
        adrs = lattice_utils.adrs2d(pareto_frontier_exhaustive, pareto_frontier)
        # ADRS after initial sampling
        adrs_evolution.append(adrs)

        # Select randomly a pareto configuration and explore its neighbourhood
        r = np.random.randint(0, len(pareto_frontier))
        pareto_configurations = [samples[i] for i in pareto_frontier_idx]
        pareto_solution_to_explore = pareto_configurations[r]

        # Search locally for the configuration to explore
        sphere = st(pareto_solution_to_explore, lattice)
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
                print "Max radius reached"
                exit_expl = True

            # Here eventually add a condition to limit the number of synthesis to a certain treshold
            # if n_of_syntheis == budget:
            #     exit_expl = True

            if exit_expl:
                break

            n_of_synthesis += 1
        adrs_run_history.append(adrs_evolution)

# Plot ADRS evolution
if plot:
    averages_adrs = list(imap(lattice_utils.avg, izip_longest(*adrs_run_history)))
    plt.title("ADRS evolution")
    plt.ylabel("ADRS")
    plt.xlabel("# of synthesis")
    plt.plot(range(intial_sampling_size,len(averages_adrs)+intial_sampling_size), averages_adrs)
    plt.grid()
    plt.show()

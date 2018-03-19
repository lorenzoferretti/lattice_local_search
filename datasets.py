########################################################################################################################
# Author: Lorenzo Ferretti
# Year: 2018
#
# This files contains the class datasets containing the different datasets name, types and function used to retrieve
# the data from the exploration
########################################################################################################################
import sqlite3
import numpy as np


class Datasets:

    def __init__(self, name):
        self.benchmark_name = name
        self.benchmarks_dict_type = {"ChenIDCt": "db", "adpcm_decode": "db", "adpcm_encode": "db", "reflectionCoeff": "db",
                                     "Autocorrelation": "db", "test": None}
        self.benchmarks_dictionary_data = {"ChenIDCt": self.get_chenidct_data, "adpcm_decode": None, "adpcm_encode": None, "reflectionCoeff": None,
                                           "Autocorrelation": None, "Autocorrelation_extended": None}

        # Definition of autocorrelation extended_experiments

        self.autcorrelation_extended_unrolling = {'max_loop': [0, 2, 4, 8, 16, 32, 40, 80, 160],  # 9
                                                  'gsm_mult_loop': [0, 2, 4, 8, 16, 32, 40, 80, 160],  # 9
                                                  'init_zero_loop' : [0, 3, 9],  # 3
                                                  'compute_loop': [0, 2, 4, 8, 19, 38, 76, 152],  # 8
                                                  'left_shift_loop': [0, 3, 9],  # 3
                                                  'rescaling_loop': [0, 2, 4, 8, 16, 32, 40, 80, 160]}  # 9

        self.autcorrelation_extended_inlining = {'gsm_norm': [0, 1]}  # 2

        self.autcorrelation_extended_pipeline = {'gsm_norm': [0, 1],  # 2
                                                 'max_loop': [0, 1],  # 2
                                                 'gsm_mult_loop': [0, 1],  # 2
                                                 'init_zero_loop': [0, 1],  # 2
                                                 'compute_loop': [0, 1],  # 2
                                                 'left_shift_loop': [0, 1],  # 2
                                                 'rescaling_loop': [0, 1]}  # 2

        # This actually need to be defined manually
        self.autcorrelation_extended_bundling = [("s", "L_ACF"), ((0, 0), (0, 1))]  # 2
        # self.autcorrelation_extended_bundling_sets = [(0, 0), (0, 1)]  # 2

        self.autcorrelation_extended_bundling_config = {'bundling': [0, 1]}

        self.autcorrelation_extended_partitioning = {'s': [0, 3, 9],  # 3
                                                     'L_ACF': [0, 2, 4, 8, 16, 32, 40, 80, 160]}  # 9

        self.autcorrelation_extended_clocks = {'clock': [5, 10, 15, 20, 25, 30]}  # 6

        self.autcorrelation_extended = {'unrolling': self.autcorrelation_extended_unrolling,
                                        'inlining': self.autcorrelation_extended_inlining,
                                        'pipelining': self.autcorrelation_extended_pipeline,
                                        'bundling': self.autcorrelation_extended_bundling_config,
                                        'partitioning': self.autcorrelation_extended_partitioning,
                                        'clock': self.autcorrelation_extended_clocks}

        self.autcorrelation_extended_directives_ordered = [
            ('unrolling-max_loop', self.autcorrelation_extended['unrolling']['max_loop']),
            ('partitioning-L_ACF', self.autcorrelation_extended['partitioning']['L_ACF']),
            ('unrolling-rescaling_loop', self.autcorrelation_extended['unrolling']['rescaling_loop']),
            ('unrolling-gsm_mult_loop', self.autcorrelation_extended['unrolling']['gsm_mult_loop']),
            ('unrolling-compute_loop', self.autcorrelation_extended['unrolling']['compute_loop']),
            ('clock-clock', self.autcorrelation_extended['clock']['clock']),
            ('partitioning-s', self.autcorrelation_extended['partitioning']['s']),
            ('unrolling-init_zero_loop', self.autcorrelation_extended['unrolling']['init_zero_loop']),
            ('unrolling-left_shift_loop', self.autcorrelation_extended['unrolling']['left_shift_loop']),
            ('pipelining-left_shift_loop', self.autcorrelation_extended['pipelining']['left_shift_loop']),
            ('pipelining-gsm_mult_loop', self.autcorrelation_extended['pipelining']['gsm_mult_loop']),
            ('pipelining-gsm_norm', self.autcorrelation_extended['pipelining']['gsm_norm']),
            ('inlining-gsm_norm', self.autcorrelation_extended['inlining']['gsm_norm']),
            ('bundling-sets', self.autcorrelation_extended['bundling']['bundling']),
            ('pipelining-rescaling_loop', self.autcorrelation_extended['pipelining']['rescaling_loop']),
            ('pipelining-compute_loop', self.autcorrelation_extended['pipelining']['compute_loop']),
            ('pipelining-max_loop', self.autcorrelation_extended['pipelining']['max_loop']),
            ('pipelining-init_zero_loop', self.autcorrelation_extended['pipelining']['init_zero_loop']),
            #('bundling-s', self.autcorrelation_extended['bundling']['s'])
        ]

        # END OF BENCHMARK DEFINITION

        self.benchmark_directives = {"ChenIDCt": ['column_loops', 'row_loops', 'bundle_b', 'accuracy_loops'],
                                 "Autocorrelation_extended": (
                                 self.autcorrelation_extended, self.autcorrelation_extended_directives_ordered)}

        function_to_call = self.benchmarks_dictionary_data[name]
        if function_to_call is not None:
            self.benchmark_synthesis_results, self.benchmark_configurations, \
            self.benchmark_feature_sets, self.benchmark_directives = function_to_call()
        else:
            self.benchmark_synthesis_results, self.benchmark_configurations, \
            self.benchmark_feature_sets, self.benchmark_directives = None, None, None, None

    def get_chenidct_data(self):
        directives_str = ",".join(self.benchmark_directives[self.benchmark_name])
        conn = sqlite3.connect('./datasets/'+self.benchmark_name+'.'+self.benchmarks_dict_type[self.benchmark_name])
        synthesis_result = conn.execute('select latencies, ffs from '+self.benchmark_name).fetchall()
        configurations = conn.execute(
            'select '+directives_str+' from '+self.benchmark_name).fetchall()

        # Define DS
        feature_sets = []
        config_list = [list(c) for c in configurations]
        matrix = np.array(config_list)
        matrix_shape = matrix.shape
        for i in xrange(matrix_shape[1]):
            column = matrix[:, i]
            unique_vector = np.unique(column)
            tmp = unique_vector.tolist()
            tmp.sort()
            feature_sets.append(tmp)
        ordered_sets = [i[0] for i in sorted(enumerate(feature_sets), reverse=True, key=lambda x: len(x[1]))]
        config_reordered = []
        tmp = []
        for r in configurations:
            for i in ordered_sets:
                tmp.append(r[i])

            config_reordered.append(tmp)
            tmp = []
        feature_sets_orderd = [feature_sets[i] for i in ordered_sets]
        directives_ordered = [self.benchmark_directives["ChenIDCt"][i] for i in ordered_sets]

        return synthesis_result, config_reordered, feature_sets_orderd, directives_ordered

    def helper_bundle_function(self, partitions):
        solutions = []
        sol = list("x_x")
        # sol = list("x_x")
        # print type(partitions)
        for p in partitions:
            for i in range(0, len(p)):
                for n in p[i]:
                    if n == 1:
                        sol[0] = str(i)
                    if n == 2:
                        sol[2] = str(i)
                    # if n == 3:
                    #        sol[4] = str(i)
            solutions.append("".join(sol))
            sol = list("x_x")
        return solutions

    def partition(self, collection):
        if len(collection) == 1:
            yield [collection]
            return

        first = collection[0]
        for smaller in self.partition(collection[1:]):
            # insert `first` in each of the subpartition's subsets
            for n, subset in enumerate(smaller):
                yield smaller[:n] + [[first] + subset] + smaller[n + 1:]
            # put `first` in its own subset
            yield [[first]] + smaller

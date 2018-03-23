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
        self.benchmarks_dict_type = {"ChenIDCt": "db", "adpcm_decode": "db", "adpcm_encode": "db",
                                     "Reflection_coefficients": "db",
                                     "Autocorrelation": "db", "test": None}
        self.benchmarks_dictionary_data = {"ChenIDCt": self.get_chenidct_data,
                                           "adpcm_decode": self.get_decode_data,
                                           "adpcm_encode": self.get_encode_data,
                                           "Reflection_coefficients": self.get_reflection_data,
                                           "Autocorrelation": self.get_autocorr_data,
                                           "Autocorrelation_extended": None,
                                           "adpcm_decode_ck": None}

        # Definition of adpcm_decode_ck extended_experiments
        self.adpcm_decode_ck_unrolling = {'mac_loop': [0, 2, 5, 10],  # 4
                                          'update_loop': [0, 2, 5, 10],  # 4
                                          'main_loop': [0, 5, 10, 25, 50]}  # 5

        self.adpcm_decode_ck_bundling = [("compressed", "result"), ((0, 0), (0, 1))]  # 2
        self.adpcm_decode_ck_bundling_config = {'bundling': [0, 1]}

        self.adpcm_decode_ck_inlining = {'upzero': [0, 1], # 2
                                         'quantl': [0, 1]}  # 2

        self.adpcm_decode_ck_clocks = {'clock': [5, 10, 15, 20]}  # 4

        self.adpcm_decode_ck = {'unrolling': self.adpcm_decode_ck_unrolling,
                                        'inlining': self.adpcm_decode_ck_inlining,
                                        # 'pipelining': self.autcorrelation_extended_pipeline,
                                        'bundling': self.adpcm_decode_ck_bundling_config,
                                        # 'partitioning': self.autcorrelation_extended_partitioning,
                                        'clock': self.adpcm_decode_ck_clocks}

        self.autcorrelation_extended_directives_ordered = [
            ('unrolling-main_loop', self.adpcm_decode_ck['unrolling']['main_loop']),
            ('unrolling-update_loop', self.adpcm_decode_ck['unrolling']['update_loop']),
            ('unrolling-mac_loop', self.adpcm_decode_ck['unrolling']['mac_loop']),
            ('clock-clock', self.adpcm_decode_ck['clock']['clock']),
            ('inlining-upzero', self.adpcm_decode_ck['inlining']['upzero']),
            ('inlining-quantl', self.adpcm_decode_ck['inlining']['quantl']),
            ('bundling-sets', self.adpcm_decode_ck['bundling']['bundling']),
        ]

        # Definition of autocorrelation_extended_experiments

        self.autcorrelation_extended_unrolling = {'max_loop': [0, 2, 4, 8, 16, 32, 40, 80, 160],  # 9
                                                  'gsm_mult_loop': [0, 2,  4, 8, 16, 32, 40, 80, 160],  # 9
                                                  'init_zero_loop': [0, 3, 9],  # 3
                                                  'compute_loop': [0, 2, 4, 8, 19, 38, 76, 152],  # 8
                                                  'left_shift_loop': [0, 3, 9],  # 3
                                                  'rescaling_loop': [0, 2, 4, 8, 16, 32, 40, 80, 160]}  # 9

        self.autcorrelation_extended_inlining = {'gsm_norm': [0, 1]}  # 2

        # self.autcorrelation_extended_pipeline = {'gsm_norm': [0, 1]  # 2
        #                                          'max_loop': [0, 1],  # 2
        #                                          'gsm_mult_loop': [0, 1],  # 2
        #                                          'init_zero_loop': [0, 1],  # 2
        #                                          'compute_loop': [0, 1],  # 2
        #                                          'left_shift_loop': [0, 1],  # 2
        #                                          'rescaling_loop': [0, 1]}  # 2

        # This actually need to be defined manually
        self.autcorrelation_extended_bundling = [("s", "L_ACF"), ((0, 0), (0, 1))]  # 2
        # self.autcorrelation_extended_bundling_sets = [(0, 0), (0, 1)]  # 2

        self.autcorrelation_extended_bundling_config = {'bundling': [0, 1]}

        # self.autcorrelation_extended_partitioning = {'s': [0, 2, 4, 8]}  # 5
                                                        #'L_ACF': [0, 3, 9],  # 3

        self.autcorrelation_extended_clocks = {'clock': [5, 10, 15, 20, 25, 30, 35, 40]}  # 8

        self.autcorrelation_extended = {'unrolling': self.autcorrelation_extended_unrolling,
                                        'inlining': self.autcorrelation_extended_inlining,
                                        # 'pipelining': self.autcorrelation_extended_pipeline,
                                        'bundling': self.autcorrelation_extended_bundling_config,
                                        # 'partitioning': self.autcorrelation_extended_partitioning,
                                        'clock': self.autcorrelation_extended_clocks}

        self.directive_dependences = [('unrolling-max_loop', 'pipelinining-max_loop'),
                                      ('unrolling-gsm_mult_loop', 'pipelinining-gsm_mult_loop'),
                                      ('unrolling-left_shift_loop', 'pipelinining-left_shift_loop'),
                                      ('unrolling-rescaling_loop', 'pipelinining-rescaling_loop'),
                                      ('unrolling-compute_loop', 'pipelinining-compute_loop'),
                                      ('unrolling-init_zero_loop', 'pipelinining-init_zero_loop')]

        self.autcorrelation_extended_directives_ordered = [
            ('unrolling-max_loop', self.autcorrelation_extended['unrolling']['max_loop']),
            ('unrolling-rescaling_loop', self.autcorrelation_extended['unrolling']['rescaling_loop']),
            ('unrolling-gsm_mult_loop', self.autcorrelation_extended['unrolling']['gsm_mult_loop']),
            ('clock-clock', self.autcorrelation_extended['clock']['clock']),
            ('unrolling-compute_loop', self.autcorrelation_extended['unrolling']['compute_loop']),
            # ('partitioning-s', self.autcorrelation_extended['partitioning']['s']),
            ('unrolling-init_zero_loop', self.autcorrelation_extended['unrolling']['init_zero_loop']),
            ('unrolling-left_shift_loop', self.autcorrelation_extended['unrolling']['left_shift_loop']),
            # ('pipelining-left_shift_loop', self.autcorrelation_extended['pipelining']['left_shift_loop']),
            # ('pipelining-gsm_mult_loop', self.autcorrelation_extended['pipelining']['gsm_mult_loop']),
            # ('pipelining-gsm_norm', self.autcorrelation_extended['pipelining']['gsm_norm']),
            ('inlining-gsm_norm', self.autcorrelation_extended['inlining']['gsm_norm']),
            ('bundling-sets', self.autcorrelation_extended['bundling']['bundling']),
            # ('pipelining-rescaling_loop', self.autcorrelation_extended['pipelining']['rescaling_loop']),
            # ('pipelining-compute_loop', self.autcorrelation_extended['pipelining']['compute_loop']),
            # ('pipelining-max_loop', self.autcorrelation_extended['pipelining']['max_loop']),
            # ('pipelining-init_zero_loop', self.autcorrelation_extended['pipelining']['init_zero_loop']),
            #('bundling-s', self.autcorrelation_extended['bundling']['s'])
        ]

        # END OF BENCHMARK DEFINITION

        self.benchmark_directives = {"ChenIDCt": ['column_loops', 'row_loops', 'bundle_b', 'accuracy_loops'],
                                 "Autocorrelation_extended": (
                                 self.autcorrelation_extended, self.autcorrelation_extended_directives_ordered),
                                     "adpcm_decode": ['main_loop_unrolling', 'mac_loop_unrolling',
                                                      'update_loop_unrolling', 'encode_inline',
                                                      'help_function_unrolling', 'bundle_b'],
                                     "adpcm_encode": ['main_loop_unrolling', 'mac_loop_unrolling',
                                                      'update_loop_unrolling', 'encode_inline',
                                                      'help_function_unrolling', 'bundle_b'],
                                     "Reflection_coefficients": ['loop1', 'loop2', 'loop3', 'loop4',
                                                                 'inline_abs', 'inline_norm', 'inline_div',
                                                                 'inline_add', 'inline_mult_r', 'bundle_b'],
                                     "Autocorrelation": ['max_loop', 'gsm_resc_loop', 'init_loop', 'compute_loop',
                                                         'shift_loop', 'bundle_b']}

        function_to_call = self.benchmarks_dictionary_data[name]
        if function_to_call is not None:
            self.benchmark_synthesis_results, self.benchmark_configurations, \
            self.benchmark_feature_sets, self.benchmark_directives = function_to_call()
        else:
            self.benchmark_synthesis_results, self.benchmark_configurations, \
            self.benchmark_feature_sets, self.benchmark_directives = None, None, None, None

    def get_chenidct_data(self):
        directives_str = ",".join(self.benchmark_directives[self.benchmark_name])
        conn = sqlite3.connect('./datasets/ChenIDct.'+self.benchmarks_dict_type[self.benchmark_name])
        synthesis_result = conn.execute('select latencies, ffs from '+self.benchmark_name).fetchall()
        configurations = conn.execute(
            'select '+directives_str+' from '+self.benchmark_name).fetchall()

        # Define DS
        config_reordered, feature_sets_orderd, directives_ordered = self._define_desing_space(configurations)

        return synthesis_result, config_reordered, feature_sets_orderd, directives_ordered

    def get_encode_data(self):
        directives_str = ",".join(self.benchmark_directives[self.benchmark_name])
        conn = sqlite3.connect('./datasets/'+self.benchmark_name+'.'+self.benchmarks_dict_type[self.benchmark_name])
        synthesis_result = conn.execute('select latencies, ffs from '+self.benchmark_name).fetchall()
        configurations = conn.execute(
            'select '+directives_str+' from '+self.benchmark_name).fetchall()

        # Define DS
        config_reordered, feature_sets_orderd, directives_ordered = self._define_desing_space(configurations)

        return synthesis_result, config_reordered, feature_sets_orderd, directives_ordered

    def get_decode_data(self):
        directives_str = ",".join(self.benchmark_directives[self.benchmark_name])
        conn = sqlite3.connect('./datasets/'+self.benchmark_name+'.'+self.benchmarks_dict_type[self.benchmark_name])
        synthesis_result = conn.execute('select latencies, ffs from '+self.benchmark_name).fetchall()
        configurations = conn.execute(
            'select '+directives_str+' from '+self.benchmark_name).fetchall()

        # Define DS
        config_reordered, feature_sets_orderd, directives_ordered = self._define_desing_space(configurations)

        return synthesis_result, config_reordered, feature_sets_orderd, directives_ordered

    def get_autocorr_data(self):
        directives_str = ",".join(self.benchmark_directives[self.benchmark_name])
        conn = sqlite3.connect('./datasets/'+self.benchmark_name+'.'+self.benchmarks_dict_type[self.benchmark_name])
        synthesis_result = conn.execute('select latencies, ffs from '+self.benchmark_name).fetchall()
        configurations = conn.execute(
            'select '+directives_str+' from '+self.benchmark_name).fetchall()

        # Define DS
        config_reordered, feature_sets_orderd, directives_ordered = self._define_desing_space(configurations)

        return synthesis_result, config_reordered, feature_sets_orderd, directives_ordered

    def get_reflection_data(self):
        directives_str = ",".join(self.benchmark_directives[self.benchmark_name])
        conn = sqlite3.connect('./datasets/'+self.benchmark_name+'.'+self.benchmarks_dict_type[self.benchmark_name])
        synthesis_result = conn.execute('select intervals, ffs from '+self.benchmark_name).fetchall()
        configurations = conn.execute(
            'select '+directives_str+' from '+self.benchmark_name).fetchall()

        # Define DS
        config_reordered, feature_sets_orderd, directives_ordered = self._define_desing_space(configurations)

        return synthesis_result, config_reordered, feature_sets_orderd, directives_ordered

    def _define_desing_space(self, configurations):

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
        directives_ordered = [self.benchmark_directives[self.benchmark_name][i] for i in ordered_sets]

        return config_reordered, feature_sets_orderd, directives_ordered

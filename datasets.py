########################################################################################################################
# Author: Lorenzo Ferretti
# Year: 2018
#
# This files contains the class datasets containing the different datasets name, types and function used to retrieve
# the data from the exploration
########################################################################################################################
import sqlite3


class Datasets:

    def __init__(self, name):
        self.benchmarks_dict_type = {"ChenIDCt": "db", "adpcm_decode": "db", "adpcm_encode": "db", "reflectionCoeff": "db",
                                "Autocorrelation": "db"}
        self.benchmarks_dictionary_data = {"ChenIDCt": self.get_chenidct_data, "adpcm_decode": None, "adpcm_encode": None, "reflectionCoeff": None,
                                "Autocorrelation": None}

        function_to_call = self.benchmarks_dictionary_data[name]
        self.benchmark_synthesis_results, self.benchmarks_configurations = function_to_call()

    @staticmethod
    def get_chenidct_data():
        conn = sqlite3.connect('./datasets/ChenIDCt.db')
        synthesis_result = conn.execute('select latencies, ffs from ChenIDCt').fetchall()
        configurations = conn.execute(
            'select accuracy_loops, column_loops, row_loops, bundle_b from ChenIDCt').fetchall()
        return synthesis_result, configurations


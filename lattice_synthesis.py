from lattice_data import Lattice
class FakeSynthesis:

    def __init__(self, synthesis_result, configurations, lattice):
        self.synthesis_result = synthesis_result
        self.configurations = list(configurations)
        self.lattice = lattice

    def synthesise_configuration(self, config):
        c = self.lattice.revert_discretized_config(config)
        idx = self.configurations.index(tuple(c))
        result = self.synthesis_result[idx]
        return result

########################################################################################################################
# Author: Lorenzo Ferretti
# Year: 2018
#
# Contains classes Synthesiser and FakeSynthesiser. These are used to invoke Vivado HLS and generate the synthesis data
# given an input configuration. Fake synthesiser retrieve data from the exhaustive exploration already performed
########################################################################################################################


class FakeSynthesis:

    def __init__(self, entire_ds, lattice):
        self.entire_ds = entire_ds
        self.lattice = lattice

    def synthesise_configuration(self, config):
        c = self.lattice.revert_discretized_config(config)
        result = None
        for i in xrange(len(self.entire_ds)):
            if self.entire_ds[i].configuration == c:
                result = (self.entire_ds[i].latency, self.entire_ds[i].area)
                break
        return result

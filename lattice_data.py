import lattice_tree
import math
import itertools
import numpy


class Lattice:

    def __init__(self, lattice_descriptor, max_distance):
        self.original_descriptor = lattice_descriptor
        self.discretized_descriptor = self.discretize_dataset(lattice_descriptor)
        self.lattice = lattice_tree.Tree('lattice')
        self.radii_struct = self.radii_vectors()
        self.max_distance = max_distance

    def radii_vectors(self):
        max_cardinality = 0
        i = 0
        # Find max cardinality
        for descriptor in self.discretized_descriptor:
            if i == 0:
                max_cardinality = len(descriptor)
            else:
                if len(descriptor) > max_cardinality:
                    max_cardinality = len(descriptor)

            i += 1

        # Generate distance matrix
        radii = {}
        sphere_radii = []
        sphere_radii_delta = []
        for element in itertools.product(*self.discretized_descriptor):
            delta = element
            tmp = []
            for e in element:
                tmp.append(e*e)
            tmp_num = sum(tmp)
            d = math.sqrt(tmp_num)
            sphere_radii.append(d)
            sphere_radii_delta.append(delta)

        ordered_radii_idx = [b[0] for b in sorted(enumerate(sphere_radii), key=lambda i: i[1])]
        radii["radius"] = sphere_radii
        radii["delta"] = sphere_radii_delta
        radii["idxs"] = ordered_radii_idx
        return radii

    def discretize_dataset(self, lattice_descriptor):
        discretized_feature = []
        for feature in lattice_descriptor:
            tmp = []
            for x in self._frange(0, 1, 1. / (len(feature) - 1)):
                tmp.append(x)
            discretized_feature.append(tmp)

        return discretized_feature

    def _frange(self, start, stop, step):
        x = start
        output = []
        while x <= stop:
            output.append(x)
            x += step
        output[-1] = 1
        return output

    def revert_discretized_config(self, config):
        tmp = []
        for i in xrange(0, len(config)):
            # print "i:" , 1, config
            # print len(self.discretized_descriptor[i]), "i:", i
            for j in xrange(0, len(self.discretized_descriptor[i])):
                if numpy.isclose(self.discretized_descriptor[i][j], config[i], atol=0.000001):
                    # idx = self.discretized_descriptor[i].index(round(config[i], 5))
                    tmp.append(self.original_descriptor[i][j])
                    break
        return tmp

    def beta_sampling(self, a, b, n_sample):
        samples = []
        for i in xrange(0, n_sample):
            s = []
            search = True
            while search:
                for d_set in self.discretized_descriptor:
                    r = numpy.random.beta(a, b, 1)[0]
                    s.append(self._find_nearest(d_set, r))

                if s in samples:
                    s = []
                    continue
                else:
                    samples.append(s)
                    break
        return samples

    def _find_nearest(self, array, value):
        idx = (numpy.abs(array-value)).argmin()
        return array[idx]

import copy
from random import randint
import os
import numpy


# A tree node
class Node:

    # Constructor to create a new node
    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, data):
        self.children.append(data)

    def has_children(self):
        if len(self.children) == 0:
            return False
        else:
            return True

    def has_child(self, data):
        for c in self.children:
            if data == c.get_data():
                return True
            else:
                continue

        return False

    def get_child(self, data):
        for c in self.children:
            if data == c.get_data():
                return c

    def get_data(self):
        return self.data

    def get_depth(self):
        counter = 0
        if not self.has_children():
            return counter
        else:
            child = self.children[-1]
            counter = child.go_in_depth(counter)
        return counter

    def go_in_depth(self, counter):
        if not self.has_children():
            return counter + 1
        else:
            child = self.children[-1]
            counter = child.go_in_depth(counter)
        return counter + 1

    def search_configuration(self, config):
        exists = False
        tmp_config = copy.deepcopy(config)
        if len(config) > 0:
            search = tmp_config.pop(0)
            for c in self.children:
                # print c.get_data()
                if search == c.get_data():
                    exists = exists or c.search_subconfiguration(tmp_config, exists)
                else:
                    continue
        else:
            return True
        return exists

    def search_subconfiguration(self, config, exists):
        tmp_config = copy.deepcopy(config)
        if len(config) > 0:
            search = tmp_config.pop(0)
            for c in self.children:
                # print c.get_data()
                if search == c.get_data():
                    exists = c.search_subconfiguration(tmp_config, exists)
                else:
                    continue
            return exists
        else:
            return True

    def add_configuration(self, config):
        if len(config) > 0:
            # print self.get_data()
            # print self.children
            initial_config = copy.deepcopy(config)
            search = initial_config[0]
            subconfiguration = initial_config[1:]
            # print "Subconfiguration passed", str(config), str(subconfiguration)
            # if self.has_child(search):
            if self.has_children():
                for c in self.children:
                    if c.get_data() == search:
                        c.add_subconfiguration(subconfiguration)
                        return
            #     self.populate_subtree(initial_config)
            # else:
            #     self.populate_subtree(initial_config)
            self.populate_subtree(initial_config)

    def add_subconfiguration(self, config):
        if len(config) > 0:
            initial_config = copy.deepcopy(config)
            search = initial_config[0]
            subconfiguration = initial_config[1:]
            if self.has_children():
                for c in self.children:
                    if c.get_data() == search:
                        c.add_subconfiguration(subconfiguration)
                        return
            #     self.populate_subtree(initial_config)
            # else:
            #     self.populate_subtree(initial_config)
            self.populate_subtree(initial_config)

    def populate_subtree(self, config):
        # print "Populate subtree", str(config)
        node = self
        for f in config:
            new_node = Node(f)
            node.add_child(new_node)
            node = new_node

    def n_of_children(self):
        n = 0
        if self.has_children():
            for c in self.children:
                n += c.n_of_children()
        else:
            n = 1

        return n


class Tree:
    # Constructor to create a new tree
    def __init__(self, data):
        self.data = Node(data)
        self.children = []

    def root(self):
        return self.data

    def populate_tree(self, data):
        root = self.root()
        node = None
        for s in data:
            i = 0
            for f in s:
                if i == 0:
                    if root.has_child(f):
                        node = root.get_child(f)
                    else:
                        node = Node(f)
                        root.add_child(node)
                else:
                    if node.has_child(f):
                        node = node.get_child(f)
                    else:
                        new_node = Node(f)
                        node.add_child(new_node)
                        node = new_node
                i += 1

    def get_tree_depth(self):
        return self.root().get_depth()

    def exists_config(self, config):
        root = self.root()
        return root.search_configuration(config)

    def add_config(self, config):
        root = self.root()
        return root.add_configuration(config)

    def closest_neighbour(self, config, lattice):
        new_configuration = None
        sphere_radii = lattice.radii_struct["radius"]
        ordered_radii_idx = lattice.radii_struct["idxs"]
        sphere_radii_delta = lattice.radii_struct["delta"]
        i = 1
        search = True
        while search and i < len(sphere_radii):
            # print i
            idx = ordered_radii_idx[i]
            if sphere_radii[i] > lattice.max_distance:
                break
            delta = sphere_radii_delta[idx]
            new_conf = self._find_configs_at_distance(config, delta, lattice.discretized_descriptor)
            if len(new_conf) == 0:
                new_configuration = None
                i += 1
            else:
                r = numpy.random.randint(0, len(new_conf))
                new_configuration = new_conf[r]
                go_to_next_d = False
                while self.exists_config(new_configuration):
                    new_conf.pop(r)
                    if len(new_conf) == 0:
                        # i += 1
                        go_to_next_d = True
                        break
                    r = numpy.random.randint(0, len(new_conf))
                    new_configuration = new_conf[r]
                if go_to_next_d:
                    i += 1
                else:
                    search = False
                # else:
                #     new_configuration = None
                    # break
            # return new_configuration

        # print new_configuration
        return new_configuration
            # d_idx = 0
            # non_valid_conf = [-1] * len(delta)
            # for d in xrange(0, len(delta)):
            #     # With a random choice I can decide to sum or subtruct the deltas
            #     random = randint(0, 1)
            #     # If 0 then sum
            #     if random == 0:
            #         new_val = config[d_idx] + delta[d]
            #         new_val = self._find_nearest(lattice.discretized_descriptor[d], new_val)
            #
            #         # if not self._check_valid_value(new_val):
            #         #     new_val = config[d_idx] - delta[d]
            #         #     if not self._check_valid_value(new_val):
            #         #         new_conf = [-1]*len(delta)
            #         #         break
            #         new_conf.append(new_val)
            #
            #         # if new_val > 1:
            #         #     new_val = config[d_idx] - d
            #         #     if new_val < 0:
            #         #         break
            #         # new_conf.append(new_val)
            #     # If 1 then sub
            #     else:
            #         new_val = config[d_idx] - delta[d]
            #         new_val = self._find_nearest(lattice.discretized_descriptor[d], new_val)
            #         # if not self._check_valid_value(new_val):
            #         #     new_val = config[d_idx] + delta[d]
            #         #     if not self._check_valid_value(new_val):
            #         #         new_conf = non_valid_conf
            #         #         break
            #
            #         new_conf.append(new_val)
            #
            #     d_idx += 1

            # if any(n == -1 for n in new_conf):
            #     print new_conf
            #
            # if any(n < 0 for n in new_conf):
            #     print new_conf
            # if not (new_conf is non_valid_conf):
            #     if not self.exists_config(new_conf):
            #         break
            # i += 1

        # print new_configuration
        # return new_configuration

    def closest_neighbour2(self, config, lattice, max_r):
        # new_configuration = None
        sphere_radii = lattice.radii_struct["radius"]
        ordered_radii_idx = lattice.radii_struct["idxs"]
        sphere_radii_delta = lattice.radii_struct["delta"]
        for i in xrange(1, len(ordered_radii_idx)):
            # print i

            idx = ordered_radii_idx[i]
            if sphere_radii[idx] > lattice.max_distance:
                # print "Max radius reached"
                break
            delta = sphere_radii_delta[idx]
            if max_r[0] < sphere_radii[i]:
                max_r = (sphere_radii[idx], i)
            new_conf = self._find_configs_at_distance(config, delta, lattice.discretized_descriptor)
            # If there are no configurations associated to the specific delta, iterate to the next delta
            if len(new_conf) == 0:
                # print "There are no configurations associated to the specific delta, iterate to the next delta"
                continue
            # Otherwise select one of the not yet selected configurations associated to the specific delta
            else:
                increment_radius = False
                r = numpy.random.randint(0, len(new_conf))
                new_configuration = new_conf[r]
                # Check if the configuration exists and iterate until a new one is found
                while self.exists_config(new_configuration):
                    # Remove existing configuration from selection
                    new_conf.pop(r)
                    # If there are no configuration associated to delta, increment the radius
                    if len(new_conf) == 0:
                        # print "There are no other configuration associated to delta, increment the radius"
                        increment_radius = True
                        break
                        # break
                    r = numpy.random.randint(0, len(new_conf))
                    new_configuration = new_conf[r]

                if increment_radius:
                    continue
                else:
                    # print "Non existing configuration discovered"
                    return new_configuration, max_r

        print "Exiting with none. All configuration discovered"
        return None, max_r

        #     if len(new_conf) == 0:
        #         new_configuration = None
        #         i += 1
        #     else:
        #         r = numpy.random.randint(0, len(new_conf))
        #         new_configuration = new_conf[r]
        #         go_to_next_d = False
        #         while self.exists_config(new_configuration):
        #             new_conf.pop(r)
        #             if len(new_conf) == 0:
        #                 # i += 1
        #                 go_to_next_d = True
        #                 break
        #             r = numpy.random.randint(0, len(new_conf))
        #             new_configuration = new_conf[r]
        #         if go_to_next_d:
        #             i += 1
        #         else:
        #             search = False
        #         # else:
        #         #     new_configuration = None
        #             # break
        #     # return new_configuration
        #
        # print new_configuration
        # return new_configuration

    def print_tree(self):
        tree_script_dot = "digraph lattice {\n"
        indent = 1
        tree_script_dot += '\t'*indent + 'node [fontname="Courier"];\n'
        root = self.root()
        parent = "root"
        for f in root.children:
            child = f.get_data()
            child_name = parent + "_" + str(child)[:5].replace('.', '')
            tree_script_dot += '\t'*indent + parent + ' -> ' + child_name + ";\n"
            tree_script_dot += self.print_subtree(f, child_name, indent)

        tree_script_dot += "}\n"
        output_file = open("tree.gv", "w")
        output_file.write(tree_script_dot)
        output_file.close()
        # os.system("dot -Tpng -Gsize=9,15\! -Gdpi=100 -o tree.png tree.gv")
        os.system("dot -Tps -Gsize=9,15\! -Gdpi=100 tree.gv -o tree.ps")

    def print_subtree(self, node, name, indent):
        tree_script_dot = ""
        if node.has_children():
            parent = name
            for f in node.children:
                child = f.get_data()
                child_name = parent + "_" + str(child)[:5].replace('.', '')
                tree_script_dot += '\t' * indent + parent + '->' + child_name + ";\n"
                tree_script_dot += self.print_subtree(f, child_name, indent)

        return tree_script_dot

    def _check_valid_value(self, value):
        if value < 0:
            return False
        if value > 1:
            return False
        return True

    def get_n_of_children(self):
        root = self.root()
        return root.n_of_children()

    def _find_nearest(self, discrete_set, value):
        array = numpy.asarray(discrete_set)
        idx = (numpy.abs(array - value)).argmin()
        return array[idx]

    def _find_configs_at_distance(self, config, deltas, discretized_descriptor):
        # print
        # print
        tmp = []
        depth = 0
        if len(config) != 0:
            c = config[0]
            d = deltas[0]
            sum_value = c + d
            if sum_value <= 1:
                tmp.append([self._find_nearest(discretized_descriptor[depth], sum_value)])
            if d != 0:
                sub_value = c - d
                if sub_value >= 0:
                    tmp.append([self._find_nearest(discretized_descriptor[depth], sub_value)])
            if len(tmp) != tmp:
                tmp = self._find_remaining_configs(tmp, config[1:], deltas[1:], depth+1, discretized_descriptor)
            return tmp
        else:
            return tmp

    def _find_remaining_configs(self, tmp, config, deltas, depth, discretized_descriptor):
        # print "TMP:", tmp, "Config", config, "Delta", deltas
        tmp2 = []
        if len(config) != 0:
            for t in tmp:
                # print t, type(t)
                c = config[0]
                d = deltas[0]
                sum_value = c + d
                # print "Sum value", sum_value
                tsum = copy.copy(t)
                if sum_value <= 1:
                    tsum.append(self._find_nearest(discretized_descriptor[depth], sum_value))
                    tmp2.append(tsum)
                if d != 0:
                    tsub = copy.copy(t)
                    sub_value = c - d
                    # print "Sub value", sub_value
                    if sub_value >= 0:
                        tsub.append(self._find_nearest(discretized_descriptor[depth], sub_value))
                        tmp2.append(tsub)

            # tmp3 = copy.copy(tmp2)
            if len(tmp2) != 0:
                # print "Passing: ", tmp2
                tmp2 = self._find_remaining_configs(tmp2, config[1:], deltas[1:], depth+1, discretized_descriptor)
            return tmp2
        else:
            return tmp

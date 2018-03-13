from lattice_tree import Node, Tree
import copy
import math
import numpy as np


class SphereTree:
    def __init__(self, configuration, lattice):
        self.root = Node(configuration)
        self.lattice = lattice
        self.radius = lattice.discretized_descriptor[0][1]
        self.min_radius = lattice.discretized_descriptor[0][1]
        self.sphere_elements = []
        self.closest_distances, self.closest_elements_idx = self.get_closest_sphere_elements()
        if len(self.closest_distances) == 0:
            self.random_closest_element = None
        else:
            self.random_closest_element = self.get_closest_random_element().get_data()

    def get_closest_sphere_elements(self):
        # lattice_root = self.lattice.lattice.root()
        # self.sphere_elements.append(self.root)
        visited_tree = Tree("visited")
        self.visit_config(self.root, visited_tree)
        while len(self.sphere_elements) == 0:
            self.radius = self.radius + self.min_radius
            if self.radius > self.lattice.max_distance:
                break
            print "RADIUS visited:", self.radius
            visited_tree = Tree("visited")
            self.visit_config(self.root, visited_tree)
        return self.sort_sphere_elements()

    def visit_config(self, starting_config, visited_tree):
        # print "-->\tVisiting config ", starting_config.get_data()
        children = []
        config = starting_config.get_data()
        visited_tree.add_config(config)
        for i in xrange(len(config)):
            delta = self.lattice.discretized_descriptor[i][1]
            cfg_plus = copy.copy(config)
            value_plus = cfg_plus[i] + delta
            cfg_plus[i] = self.lattice._find_nearest(self.lattice.discretized_descriptor[i], np.float64(value_plus))
            cfg_minus = copy.copy(config)
            value_minus = cfg_minus[i] - delta
            cfg_minus[i] = self.lattice._find_nearest(self.lattice.discretized_descriptor[i], np.float64(value_minus))

            # Generate the new config to add
            config_to_append_plus = self._add_config(cfg_plus, visited_tree)
            if config_to_append_plus is not None:
                children.append(config_to_append_plus)
            config_to_append_minus = self._add_config(cfg_minus, visited_tree)
            if config_to_append_minus is not None:
                children.append(config_to_append_minus)
            # print "Children", [c.get_data() for c in children]
            while len(children) > 0:
                c = children.pop(0)
                # visited_tree.print_tree('visited_tree')
                if not visited_tree.exists_config(visited_tree, c.get_data()):
                    # print "Children visited:", c.get_data()
                    self.visit_config(c, visited_tree)
                    if not self.lattice.lattice.exists_config(self.lattice.lattice, c.get_data()):
                        # print c.get_data(), "non esiste. Aggiunto alla sfera"
                        self.sphere_elements.append(c)
                # else:
                    # print "Children pruned:", c.get_data()

    def _add_config(self, config, visited_tree):
        # print "****"*2, config
        distance = self._get_distance(config)
        if not np.isclose(distance, self.radius) and distance > self.radius:
            # print "Distanza maggiore"
            return None
        else:
            # if visited_tree.exists_config(config):
            #     print "Gia visitato"
            #     return None
            # else:
            # lattice_tree = self.lattice.lattice
            # if not lattice_tree.exists_config(lattice_tree, config):
            #     n = Node(config)
            #     # self.sphere_elements.append(n)
            #     print "Da aggiungere"
            #     return n
            # else:
            #     print "Esiste gia"
            #     return None
            n = Node(config)
            return n

    # def visit_config(self, config, lattice_tree):
    #     children_configs = []
    #     actual_radius = self.min_radius
    #     while actual_radius <= self.radius:
    #         for i in xrange(len(config.data)):
    #             var_min = self.lattice.discretized_descriptor[i][1]
    #             if var_min > self.radius:
    #                 break
    #             cfg_plus = copy.copy(config.data)
    #             cfg_minus = copy.copy(config.data)
    #             value_plus = cfg_plus[i] + var_min
    #             cfg_plus[i] = value_plus
    #             cfg_plus[i] = self.lattice._find_nearest(self.lattice.discretized_descriptor[i], np.float64(cfg_plus[i]))
    #             # value_minus = cfg_minus[i] - var_min
    #             value_minus = cfg_minus[i] - var_min
    #             cfg_minus[i] = value_minus
    #             cfg_minus[i] = self.lattice._find_nearest(self.lattice.discretized_descriptor[i], np.float64(cfg_minus[i]))
    #
    #             if value_minus >= 0:
    #                 add_value_minus = True
    #             else:
    #                 add_value_minus = False
    #
    #             if value_plus <= 1:
    #                 add_value_plus = True
    #             else:
    #                 add_value_plus = False
    #
    #             if add_value_minus:
    #                 new_config_minus = self._add_config(cfg_minus, lattice_tree)
    #                 if new_config_minus is not None:
    #                     print "Added: ", new_config_minus.data, " at distance: ", self.radius
    #                     children_configs.append(new_config_minus)
    #                 # children_configs.append(self._add_config(cfg_minus, lattice_tree))
    #
    #             if add_value_plus:
    #                 # self._add_config(cfg_plus, lattice_tree)
    #                 new_config_plus = self._add_config(cfg_plus, lattice_tree)
    #                 if new_config_plus is not None:
    #                     print "Added: ", new_config_plus.data, " at distance: ", self.radius
    #                     children_configs.append(new_config_plus)
    #
    #         sphere_elements = copy.copy(children_configs)
    #         self.sphere_elements += sphere_elements
    #         for i in children_configs:
    #             # self.sphere_elements += i
    #             self.visit_config_children(i, lattice_tree, children_configs)
    #
    #         actual_radius += self.min_radius
    #         if len(sphere_elements) == 0:
    #             if self.radius + self.min_radius > self.lattice.max_distance:
    #                 print "HO RAGGIUNTO RAGGIO: ", self.radius + self.min_radius
    #                 break
    #             else:
    #                 self.radius = self.radius + self.min_radius
    #
    #     # the elements should be ordered
    #     # self.sphere_elements = self.sphere_elements + sphere_elements
    #
    # def visit_config_children(self, config, lattice_tree, children):
    #     children_configs = []
    #     for i in xrange(len(config.data)):
    #         var_min = self.lattice.discretized_descriptor[i][1]
    #         if var_min > self.radius:
    #             break
    #         cfg_plus = copy.copy(config.data)
    #         cfg_minus = copy.copy(config.data)
    #         value_plus = cfg_plus[i] + var_min
    #         cfg_plus[i] = value_plus
    #         cfg_plus[i] = self.lattice._find_nearest(self.lattice.discretized_descriptor[i], np.float64(cfg_plus[i]))
    #         value_minus = cfg_minus[i] - var_min
    #         cfg_minus[i] = value_minus
    #         cfg_minus[i] = self.lattice._find_nearest(self.lattice.discretized_descriptor[i], np.float64(cfg_minus[i]))
    #
    #         if value_minus >= 0:
    #             add_value_minus = True
    #         else:
    #             add_value_minus = False
    #
    #         if value_plus <= 1:
    #             add_value_plus = True
    #         else:
    #             add_value_plus = False
    #
    #         if add_value_minus:
    #             new_config = self._add_config(cfg_minus, lattice_tree)
    #             if new_config is not None:
    #                 print "Added children: ", new_config.data, " at distance: ", self.radius
    #                 children_configs.append(new_config)
    #             # children_configs.append(self._add_config(cfg_minus, lattice_tree))
    #
    #         if add_value_plus:
    #             # self._add_config(cfg_plus, lattice_tree)
    #             new_config = self._add_config(cfg_plus, lattice_tree)
    #             if new_config is not None:
    #                 print "Added children: ", new_config.data, " at distance: ", self.radius
    #                 children_configs.append(new_config)
    #
    #     self.sphere_elements += children_configs
    #     for i in children_configs:
    #         self.visit_config_children(i, lattice_tree, children_configs)

        # return children_configs

    def _get_distance(self, config):
        tmp = 0
        for i in xrange(len(config)):
            root_config = self.root.get_data()
            # var = self.lattice.discretized_descriptor[i][1]
            tmp += ((root_config[i]) - (config[i])) ** 2

        tmp = math.sqrt(tmp)
        return tmp


    # def _add_config(self, config, lattice_tree):
    #     if lattice_tree.exists_config(config):
    #         pass
    #     else:
    #         if self._is_in_sphere(config):
    #             pass
    #         else:
    #             if self._get_distance(config) < self.radius or np.isclose(self._get_distance(config), self.radius):
    #                 n = Node(config)
    #                 return n

    def _is_in_sphere(self, config):
        # print self.sphere_elements
        for e in self.sphere_elements:
            if config == e.get_data():
                return True
        return False

    def sort_sphere_elements(self):
        distances = []
        for i in self.sphere_elements:
            c = i.get_data()
            distances.append(self._get_distance(c))

        return distances, sorted(range(len(distances)), key=lambda k: distances[k])

    def get_closest_random_element(self):
        tmp = []
        min_distance = min(self.closest_distances)
        for i in self.closest_elements_idx:
            if self.closest_distances[i] == min_distance:
                tmp.append(i)

        r = np.random.randint(0, len(tmp))
        return self.sphere_elements[r]


########################################################################################################################
# Author: Lorenzo Ferretti
# Year: 2018
#
# This files contains some function, such metrics, support functions, etc. useful across different projects.
########################################################################################################################
from itertools import izip_longest, imap
import math


def pareto_frontier2d(points):
    """
    Function: pareto_frontier2d
    The function given in input a set of points return the 2 dimensional Pareto frontier elements and the corresponding
    indexes respect to the original set of point

    Input: A list of points.
    A list of object characterised by two attributes-area and latency.

    Output: A tuple composed of 2 lists.
    The first list contains the Pareto dominant objects. The second list contains the indexes of the pareto dominant
    objects, respect to the original set of points given in input
    """
    indexes = sorted(range(len(points)), key=lambda k: points[k].latency)
    p_idx = []
    p_front = []
    pivot_idx = indexes[0]
    for i in xrange(1, len(indexes)):
        # If are equal, I search for the minimum value until they become different
        data_pivot = points[pivot_idx]
        d = points[indexes[i]]
        if data_pivot.latency == d.latency:
            if d.area < data_pivot.area:
                pivot_idx = indexes[i]
        else:
            if d.area < data_pivot.area:
                p_idx.append(pivot_idx)
                p_front.append(data_pivot)
                pivot_idx = indexes[i]
        if i == len(indexes)-1 and pivot_idx != p_idx[-1]:
            p_idx.append(pivot_idx)
            p_front.append(points[pivot_idx])

    return p_front, p_idx


def adrs2d(reference_set, approximate_set):
    """
    Function: adrs2d
    The function given in input a set of reference points and a different set of points calculates the Average Distance
    from Reference Set among the reference set and the approximate one.
    ADRS(Pr, Pa) = 1/|Pa| * sum_Pa( min_Pp( delta(Pr,Pa) ) )
    delta(Pr, Pa) = max(0, ( A(Pa) - A(Pr) ) / A(Pa), ( L(Pa) - L(Pr) ) / L(Pa) )

    Input: 2 list of points.
    A list points representing the reference set and a list of points representing the approximate one.

    Output: ADRS value.
    A value representing the ADRS distance among the two sets, the distance of the approximate one with respect to the
    reference set.
    """
    n_ref_set = len(reference_set)
    n_app_set = len(approximate_set)
    min_dist_sum = 0
    for i in xrange(0, n_ref_set):
        distances = []
        for j in xrange(0, n_app_set):
            distances.append(_p2p_distance_2d(reference_set[i], approximate_set[j]))
        min_dist = min(distances)
        min_dist_sum = min_dist_sum + min_dist

    avg_distance = min_dist_sum / n_ref_set
    return avg_distance


def _p2p_distance_2d(ref_pt, app_pt):
    """
    Function: _p2p_distance_2d
    Support function used in ADRS
    Point to point distance for a 2 dimensional ADRS calculation. Implements the delta function of ADRS

    Input: 2 points.
    The reference point and the approximate point. Both are objects characterised by area and latency attributes.

    Output: A float value
    The maximum distance among the 2 dimensions considered (in our case area and latency).
    """
    x = (float(app_pt.latency) - float(ref_pt.latency)) / float(ref_pt.latency)
    y = (float(app_pt.area) - float(ref_pt.area)) / float(ref_pt.area)
    to_find_max = [0, x, y]
    d = max(to_find_max)
    return d


def get_statistics(collected_data):
    adrs = []
    radii = []
    final_adrs = []
    avg_distances = []
    min_distances = []
    max_distances = []
    for i in collected_data:
        # print i[1]
        adrs.append(i[1])
        radii.append(i[2])
        final_adrs.append(i[1][-1])
        min_distances.append(min(i[3]))
        avg_distances.append(avg(i[3]))
        max_distances.append(max(i[3]))
    print adrs
    last_element = []
    for i in adrs:
        last_element.append(i[-1])

    max_len = 0

    for i in adrs:
        if max_len < len(i):
            max_len = len(i)

    list_avg = []
    for i in xrange(len(collected_data)):
        list_avg.append([None] * max_len)
    for i in xrange(len(list_avg)):
        for j in xrange(len(list_avg[i])):
            if j < len(adrs[i]):
                list_avg[i][j] = adrs[i][j]
            else:
                list_avg[i][j] = adrs[i][-1]
    averages = map(_mean, zip(*list_avg))
    final_adrs_mean = avg(final_adrs)
    averages_distances = (avg(min_distances), avg(avg_distances), avg(max_distances))
    # averages = [np.ma.average(ma.masked_values(temp_list, None)) for temp_list in izip_longest(*adrs)]
    return averages, radii, final_adrs_mean, averages_distances


def _mean(l):
    return sum(l) / len(l)


def avg(x):
    x = list(x)
    for i in xrange(len(x)):
        if x[i] is None:
            x[i] = 0
    x = [i for i in x if i is not None]
    return sum(x, 0.0) / len(x)


def get_euclidean_distance(a, b):
    tmp = 0
    for i in xrange(len(a)):
        tmp += ((a[i]) - (b[i])) ** 2

    tmp = math.sqrt(tmp)
    return tmp

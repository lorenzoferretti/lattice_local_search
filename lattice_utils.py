# def pareto_frontier2d(data):
#     indicies = sorted(range(len(data)), key=lambda k: data[k][0])
#     p_idx = []
#     p_front = []
#     pivot_idx = indicies[0]
#     for i in xrange(1, len(indicies)):
#         # If are equal, I search for the minimum value until they become different
#         data_pivot = data[pivot_idx]
#         d = data[indicies[i]]
#         if data_pivot[0] == d[0]:
#             if d[1] < data_pivot[1]:
#                 pivot_idx = indicies[i]
#                 # update_pivot = False
#                 # continue
#         else:
#             if d[1] < data_pivot[1]:
#                 p_idx.append(pivot_idx)
#                 p_front.append(data_pivot)
#                 pivot_idx = indicies[i]
#                 # if i == len(indicies)-1:
#                 #     p_idx.append(pivot_idx)
#                 #     p_front.append(data[pivot_idx])
#         if i == len(indicies)-1 and pivot_idx != p_idx[-1]:
#             p_idx.append(pivot_idx)
#             p_front.append(data[pivot_idx])
#
#     return p_front, p_idx


def pareto_frontier2d(points):
    indicies = sorted(range(len(points)), key=lambda k: points[k].latency)
    p_idx = []
    p_front = []
    pivot_idx = indicies[0]
    for i in xrange(1, len(indicies)):
        # If are equal, I search for the minimum value until they become different
        data_pivot = points[pivot_idx]
        d = points[indicies[i]]
        if data_pivot.latency == d.latency:
            if d.area < data_pivot.area:
                pivot_idx = indicies[i]
        else:
            if d.area < data_pivot.area:
                p_idx.append(pivot_idx)
                p_front.append(data_pivot)
                pivot_idx = indicies[i]
        if i == len(indicies)-1 and pivot_idx != p_idx[-1]:
            p_idx.append(pivot_idx)
            p_front.append(points[pivot_idx])

    return p_front, p_idx


def adrs2d(reference_set, approximate_set):
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
    x = (float(app_pt.latency) - float(ref_pt.latency)) / float(ref_pt.latency)
    y = (float(app_pt.area) - float(ref_pt.area)) / float(ref_pt.area)
    to_find_max = [0, x, y]
    d = max(to_find_max)
    return d

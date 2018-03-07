

# def pareto_frontier2d(data):
#     idx = sorted(range(len(data)), key=lambda k: data[k][0])
#     p_idx = [idx[0]]
#     p_front = [data[p_idx[0]]]
#     for i in idx:
#         d = data[i][1]
#         p = p_front[-1][1]
#         if d < p:
#             p_front.append(data[i])
#             p_idx.append(idx[i])
#     return p_front, p_idx

def pareto_frontier2d(data):
    indicies = sorted(range(len(data)), key=lambda k: data[k][0])
    p_idx = []
    p_front = []
    pivot_idx = indicies[0]
    update_pivot = True
    already_updated = False
    for i in xrange(1, len(indicies)):
        # If are equal, I search for the minimum value until they become different
        data_pivot = data[pivot_idx]
        d = data[indicies[i]]
        if data_pivot[0] == d[0]:
            if d[1] < data_pivot[1]:
                pivot_idx = indicies[i]
                # update_pivot = False
                # continue
        else:
            if d[1] < data_pivot[1]:
                p_idx.append(pivot_idx)
                p_front.append(data_pivot)
                pivot_idx = indicies[i]
                # if i == len(indicies)-1:
                #     p_idx.append(pivot_idx)
                #     p_front.append(data[pivot_idx])
        if i == len(indicies)-1 and pivot_idx != p_idx[-1]:
            p_idx.append(pivot_idx)
            p_front.append(data[pivot_idx])

    return p_front, p_idx

# def pareto_frontier_2d(data):
#     pareto_pts = []
#     if len(data) == 1:
#         pareto_pts.append([data[1][1], data[1][2]])
#     else:
#         data_sorted = copy.copy(data)
#         data_sorted.sort(key=lambda x: x[0])
#         i = 0
#         while i < len(data_sorted):
#             pareto_p = data_sorted[i]
#             j = i + 1
#             while j < len(data_sorted):
#                 p2 = data_sorted[j]
#                 if p2[0] > pareto_p[0]:
#                     break
#                 else:
#                     if p2[1] >= pareto_p[1]:
#                         j += 1
#                         continue
#                     else:
#                         pareto_p = [p2[0], p2[1]]
#
#                 j += 1
#
#             if len(pareto_pts) > 0 and pareto_p[0] >= pareto_pts[-1][0] and pareto_p[1] >= pareto_pts[-1][1]:
#                 i = j
#                 continue
#             pareto_pts.append(pareto_p)
#             i = j
#
#     return pareto_pts
#
# def pareto_frontier2d(data):
#     pareto_pts = []
#     pareto_idxs = []
#     if len(data) == 1:
#         pareto_pts.append([data[1][1], data[1][2]])
#         pareto_idxs.append(0)
#     else:
#         data_sorted = copy.copy(data)
#         idx = sorted(range(len(data_sorted)), key=lambda k: data_sorted[k][0])
#         # data_sorted.sort(key=lambda x: x[0])
#         i = 0
#         while i < len(idx):
#             sorted_idx_i = idx[i]
#             pareto_p = data_sorted[sorted_idx_i]
#             pareto_idx = sorted_idx_i
#             j = i + 1
#             while j < len(idx):
#                 sorted_idx_j = j
#                 p2 = data_sorted[sorted_idx_j]
#                 if p2[0] > pareto_p[0]:
#                     break
#                 else:
#                     if p2[1] >= pareto_p[1]:
#                         j += 1
#                         continue
#                     else:
#                         pareto_p = [p2[0], p2[1]]
#                         pareto_idx = sorted_idx_j
#                 j += 1
#
#             if len(pareto_pts) > 0 and pareto_p[0] >= pareto_pts[-1][0] and pareto_p[1] >= pareto_pts[-1][1]:
#                 i = j
#                 continue
#             pareto_pts.append(pareto_p)
#             pareto_idxs.append(pareto_idx)
#             i = j
#
#     return pareto_pts, pareto_idxs


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
    x = (float(app_pt[0]) - float(ref_pt[0])) / float(ref_pt[0])
    y = (float(app_pt[1]) - float(ref_pt[1])) / float(ref_pt[1])
    to_find_max = [0, x, y]
    d = max(to_find_max)
    return d

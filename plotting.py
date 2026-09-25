from eelbrain import NDTest, Dataset, Datalist, plot, fmtxt
import numpy as np
from scipy.spatial.distance import cdist

def plot_source_time_result(
    result: NDTest,
    data: Dataset,
    colors: dict,
    legend_colors: dict,
    title: str = None,
    d_min: float = 0.02,
    r_min: float = 0.8,
    category: str = None,
    match: str = 'subject'
):
    """Plot test results from a source space time-course test
    
    Parameters
    ----------
    result
        Test results.
    data
        Data on which the test was run. 
        This data is used to plot the source time course.
        Should be the same data used to create ``result``.
    colors
        Colors for UTS plots of cluster time courses.
    title
        Title to add on plots.
    d_thresh
        Threshold for minimal distance between a pair of clusters.
    r_thresh: 
        Threshold for correlation (absolute value) between a pair of clusters. 
    """
    clustersAll = result.find_clusters(maps=True)

    coordinates_all = []
    timeseries_all = []
    clusters_id_all = []
    hemispheres_all = []

    for case in clustersAll.itercases():
        c_map = case['cluster']
        cluster = c_map.any('time')
        coordinates = c_map.source.coordinates[cluster]
        coordinates_all.append(coordinates)
        timeseries = (data[result.y].sub(source = cluster).mean(('case', 'source')))
        timeseries_all.append(timeseries)
        cluster_id = case['id']
        clusters_id_all.append(cluster_id)
        hemisphere = case['hemi']
        hemispheres_all.append(hemisphere)

    clusterID_and_coordinates = Datalist(zip(clusters_id_all, hemispheres_all, coordinates_all))
    timeseries_all = [t.x for t in timeseries_all]

    # creating a dictionary that contains: 
    # a pair of cluster ID from the same hemisphere 
    # mininum distance between this pair of clusters
    # the correlation of the timeseries between this pair of clusters
    min_distances_and_correlations = {}
    for i in range(len(clusterID_and_coordinates)):
        for j in range(i+1, len(clusterID_and_coordinates)):
            if clusterID_and_coordinates[i][1]==clusterID_and_coordinates[j][1]:
                dist = cdist(clusterID_and_coordinates[i][2], clusterID_and_coordinates[j][2], 'euclidean')
                corr = np.corrcoef(timeseries_all[i], timeseries_all[j])
                min_distance = np.min(dist)
                min_distances_and_correlations[clusterID_and_coordinates[i][0], clusterID_and_coordinates[j][0]] = min_distance, corr[0,1]

    # getting groups of clusters that I want to combine for plotting.
    groups = []
    used_ids = set()
    for (id1, id2), (distance, correlation) in min_distances_and_correlations.items():
        if distance < d_min and abs(correlation) > r_min:
            groups.append({id1, id2})
            used_ids.add(id1)
            used_ids.add(id2)
                    
    # merge groups
    for i in range(len(groups)-1, -1, -1):
        ids = groups[i]
        for ref_ids in groups[:i]:
            if ids.intersection(ref_ids):
                ref_ids.update(ids)
                groups.remove(ids)
                break
            
    # add groups for isolated (not merged) clusters
    unused_ids = set(clustersAll['id']).difference(used_ids)
    for id_i in unused_ids:
        groups.append({id_i})
        
    # print(groups)

    # order group within groups by the earliest tstart time, so the plot will be sorted by tstart time.
    id_all = clustersAll['id'].x
    tstart_all = clustersAll['tstart'].x
    id_tstart_dict = {id_all[i]:tstart_all[i] for i in range(len(id_all))}
    tstart_set_pairs = []
    
    for group in groups:
        # find the smallest tstart in the current set
        min_tstart = min(id_tstart_dict[element] for element in group)
        # print(min_tstart)
        # append the (min_tstart, set) tuple to the list
        tstart_set_pairs.append((min_tstart, group))

    tstart_set_pairs.sort(key=lambda x: x[0]) 
    sorted_groups= [pair[1] for pair in tstart_set_pairs]               

    print(sorted_groups)
    
    # looping through each group of cluster IDs identified by my threshold. 
    t = fmtxt.Table('ll')
    brain = plot.brain.brain('fsaverage', surf='smoothwm', views=['lateral', 'medial'])

    for group in sorted_groups:
        # for each group, getting the dataset that contains all the cluster information. 
        dataset_all = clustersAll[clustersAll['id'].isin(list(group))]
        inverse_sign_ids = []
        id_0 = dataset_all[0]['id']
        # looping through each group of clusters
        for id_i in dataset_all[1:, 'id']:
            # use the min_distances_and_correlations dictionary to decide which clusters should be plotted with blue. 
            id_pair = (id_0,id_i)
            r = min_distances_and_correlations[id_pair][1]
            if r < 0:
                inverse_sign_ids.append(id_i)
    
        inverse_sign_cases = clustersAll[clustersAll['id'].isin([inverse_sign_ids])]
        # print(inverse_sign_cases)
        
        # combine all the inverse sign clusters
        inverse_sign_cluster_combined = inverse_sign_cases['cluster'].any('time').any('case')
        group_cluster_combined = dataset_all['cluster'].any('time').any('case')
        # print(inverse_sign_cluster_combined.sum())
        # print(group_cluster_combined.sum())
        
        froi = group_cluster_combined.astype(float)
        froi[inverse_sign_cluster_combined] = -1
        n_source = abs(froi).sum()
        # print(n_source)
        froi /= n_source
        time_course = froi.dot(data[result.y])
    
        brain.add_ndvar(froi, 'polar-a', vmax=1/n_source)
        im = brain.image()
        t.cell(im)

        # print(inverse_sign_ids) 
        # print(clusters_per_group)

        p = plot.UTSStat(time_course, category, match=match, data=data, colors=colors, h=4, w=8, legend=False, title=title)
        p.add_hline(0, ls=':', c='0.7')
        p.set_clusters(dataset_all, pmax=0.05, color='.7')
        t.cell(p)
        
        brain.remove_data()
        brain.remove_labels()

    p_legend = plot.ColorList(legend_colors, w=2)    
    t.cell(p_legend)
    return t
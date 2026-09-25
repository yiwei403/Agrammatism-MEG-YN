# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: agrammatism
#     language: python
#     name: python3
# ---

# %% [markdown]
# ### analysis setup

# %%
import runpy
runpy.run_path('/Users/yiwei/Dropbox/agrammatism/code/Zenodo scripts/s01_zenodo_pipelineSetup.py')
from s01_zenodo_pipelineSetup import *
import os
import re
import glob
import numpy as np

# NumPy 2.0 workaround for older mayavi/pysurfer
# np.in1d was renamed to np.isin in NumPy 2.x
if not hasattr(np, 'in1d'):
    np.in1d = np.isin
    
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize, ListedColormap
import matplotlib.lines as mlines
import matplotlib.pyplot as plt

# # %matplotlib qt # turn this on for mne interactive plots

inv_info = 'vec-3-MNE-0'
src_info = 'ico-4'
megData.set_inv(ori=re.split('-',inv_info)[0], 
                snr=int(re.split('-',inv_info)[1]), 
                method=re.split('-',inv_info)[2], 
                depth=int(re.split('-',inv_info)[3]), 
                pick_normal=False)
session = 'picturefirst'

epoch = f'trial_{session}'
tstart = 1
tstop = 3

megData.set(raw='ica-'+session, epoch=epoch, rej='')
mask = 'aparc.a2009s'
group = 'right_hand'

res_cache_dir = os.makedirs(os.path.join(data_path + f'/yi-test/ica-{epoch} emptyroom {inv_info} {src_info} {group}/'), exist_ok=True)
res_cache_dir = os.path.join(data_path + f'/yi-test/ica-{epoch} emptyroom {inv_info} {src_info} {group}/')
res_cache_file = f' nobl tfce {str(tstart)}-{str(tstop)} {mask}'
plot_dir = f'/Users/yiwei/Dropbox/agrammatism/plots/{inv_info}/'

# %% [markdown]
# ### Stage 1

# %% notebookRunGroups={"groupValue": "1"}

subjects = megData.get_field_values('subject',group=group)

lms = []
megData.set(parc = mask)

for subject in subjects:
    data = megData.load_epochs_stc(
        subjects = subject, 
        baseline = False, 
        cov = 'emptyroom',
        cat = ['nounnm', 'verbnm', 'nounpp', 'nounpc', 'inffut', 'infpst'],
        model = 'wordType',
        morph = True,
        )
    
    lm = testnd.LM('srcm', 'syllable', data = data, coding = 'effect', samples=0, subject = subject)
    lms.append(lm)

# %% [markdown]
# ### Stage 2

# %%
rows = []

for lm in lms:
    rows.append([lm.subject, lm.coefficient('intercept'), lm.coefficient('syllable')])

data = Dataset.from_caselist(['subject', 'intercept', 'syllable'], rows, random='subject')
# save.pickle(data, 'lm_data_noun_verb')

regressors = [
    'syllable',
    ]

for regressor in regressors:

    res = testnd.Vector(
        regressor, data=data, tfce=True,
        tstart=tstart, tstop=tstop
    )
    save.pickle(res, res_cache_dir + 'effect_all_syllable_' + regressor + res_cache_file)

# %% [markdown]
# ### plot the T2 from the regression analysis results by ROI, using the percentage of significant voxels (within a given ROI) as colormap.

# %%
figsize = (39, 3.5)

def custom_cmap(base_cmap, min_cmap_start=0.1, steps=256):
    """
    create a custom colormap
    0.0 maps to fully transparent (alpha = 0)
    (0, 1] maps to base_cmap from min_cmap_start (ratio of the cmap)
    
    Parameters
    - base_cmap: matplotlib colormap
    - min_cmap_start: the starting point in base_cmap. 
        (e.g., 0.3 means starting from 30% of the base_cmap)
    - steps: int
        number of discrete colors in the custom_cmap
        
    Returs:
    - ListedColormap with 0 being fully transparent
    
    """
    if isinstance(base_cmap, str):
        base_cmap = plt.colormaps.get_cmap(base_cmap)
    
    colors = base_cmap(np.linspace(min_cmap_start, 1.0, steps-1))
    transparent_color = np.array([[1.0, 1.0, 1.0, 0.0]])
    new_colors = np.vstack((transparent_color, colors))
    
    return ListedColormap(new_colors)

regressors = [
    'syllable',
    ]

custom_blue_cmap = custom_cmap('Blues')
custom_red_cmap = custom_cmap('Reds')
custom_green_cmap = custom_cmap('Greens')
custom_purple_cmap = custom_cmap('Purples')
custom_grey_cmap = custom_cmap('Greys')


lang_ROIs_dict = {   
    # ('G_precentral-lh'): ('LM1', custom_blue_cmap),
    ('G_front_inf-Opercular-lh','G_front_inf-Triangul-lh', 'G_front_inf-Orbital-lh'): ('LIFG', custom_red_cmap),
}


for regressor in regressors:
        
    if glob.glob(os.path.join(res_cache_dir + regressor + res_cache_file + '*')):
        res = load.unpickle(res_cache_dir + 'effect_all_syllable_' + regressor + res_cache_file)
    else:
        print("file doesn't exist")

    time_array = res.difference.time.times

    for roi,(label,cmap) in lang_ROIs_dict.items():
        
        fig, ax = plt.subplots(figsize=figsize)
        legend_handles = []

        
        cluster_sig = ~res.masked_difference().get_mask().any('space').sub(source=roi)
        color_array = (cluster_sig.sum(axis='source').x)/len(cluster_sig.x)
        
        ### choose whether to plot the line when the percentage of significant voxels is less than 30% of the ROI.
        ### This line is turned on for report in all the table, and turned off for the T squared plot.
        color_array[color_array<0.3] = 0
        
        T2 = res.t2.sub(source=roi) 
        test = T2*cluster_sig 
        test.x[test.x == 0] = np.nan
        x = time_array
        y = np.nanmean(test.x, axis = 0)

        points = np.array([x,y]).T.reshape(-1, 1, 2)

        line_segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        line_collection = LineCollection(line_segments, cmap = cmap, norm = Normalize(0, 1))
        line_collection.set_array(color_array[:-1])  # color per segment
        
        legend_color = plt.colormaps.get_cmap(cmap)(0.5)
        line_collection.set_linewidth(8)
        
        ax.add_collection(line_collection)

        legend_handles.append(mlines.Line2D([], [], color=legend_color, linewidth=2, label=label))

        xticks = np.arange(res.difference.time.tmin, time_array[-1] + 0.04, 0.04)
        yticks = np.arange(3.5, 6.5, 0.5)

        plt.xticks(xticks)
        plt.yticks(yticks)
        ax.set_xlabel("time")
        ax.set_ylabel("t2")
        ax.set_title(f'{regressor}')
        ax.legend(handles=legend_handles)
        ax.set_xlim(1.8, 3)
        ax.set_ylim(3.5,6)
        ax.grid(True)
        # plt.savefig(os.path.join(plot_dir, f'regressor_{regressor}_{label}_sig_results.pdf'))
        plt.show()


# %% [markdown]
# ### function to extract the time stamp and max T2 value of line segments that meet results reporting criteria. 

# %%
def extract_segments(data, step = 0.005, min_duration = 0.0, min_value = 0):
    data = np.unique(data, axis=0)
    ts = data[:,0] # timestamps
    
    diffs = np.diff(ts)
    runs = []
    start = 0
    
    for i, d in enumerate(diffs):
        if not np.isclose(round(d,3), step, atol=1e-12):
            runs.append((start, i))
            start = i + 1
    runs.append((start, len(ts)-1))
    
    valid_segments = []
    max_values = []
    
    for r_start, r_end in runs:
        segment = data[r_start:r_end+1]
        seg_ts = segment[:,0]
        seg_val = segment[:,1]

        # mask of positions where value >= min_value
        mask = seg_val >= min_value

        # find contiguous sub-runs in mask
        s = None
        for i, ok in enumerate(mask):
            if ok:
                if s is None:
                    s = i
            else:
                if s is not None:
                    sub_start, sub_end = s, i-1
                    s = None
                    # process this sub-run
                    if seg_ts[sub_end] - seg_ts[sub_start] >= min_duration - 1e-12:
                        subseg = segment[sub_start:sub_end+1]
                        valid_segments.append(subseg)
                        max_values.append(np.max(subseg[:,1]))
        # close last sub-run if mask ended with True
        if s is not None:
            sub_start, sub_end = s, len(mask)-1
            if seg_ts[sub_end] - seg_ts[sub_start] >= min_duration - 1e-12:
                subseg = segment[sub_start:sub_end+1]
                valid_segments.append(subseg)
                max_values.append(np.max(subseg[:,1]))

    return valid_segments, max_values


# %% [markdown]
# #### print out sig. time and T2 value from the regression test

# %%
color_array_mask = color_array[:-1]!=0
nonzero_segments = line_segments[color_array_mask]
coord = nonzero_segments.reshape(-1, 2)

clean = coord[~np.isnan(coord[:,1])]
segments, maxima = extract_segments(clean)
# print(segments)

for seg, m in zip(segments, maxima):
    seg_ms = np.rint((seg[:,0]-1)*1000).astype(int)
    # seg_ms = np.rint((seg[:,0])*1000).astype(int)
    # print(seg_ms)
    print(f"{seg_ms[0]} - {seg_ms[-1]}ms (max  = {round(m, 2)})")
    print()

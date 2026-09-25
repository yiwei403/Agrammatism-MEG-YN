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
# ##  Scripts for T2 line plot, colormap, and tables
#

# %% [markdown]
# ### script setup

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

session = 'picturefirst'

# epoch = f'speak_{session}'
# tstart = -1
# tstop = 1

epoch = f'trial_{session}'
tstart = 1
tstop = 3

mask = 'aparc.a2009s'
inv_info = 'vec-3-MNE-0'
group = 'right_hand' 
src_info = 'ico-4'

if (tstart, tstop) == (1, 3):
    fig_size = (48,4)
elif (tstart, tstop) == (1.8, 3):      
    fig_size = (28.8,4)
elif(tstart, tstop) == (1, 1.8):
    fig_size = (19.2,4)

megData.set_inv(ori=re.split('-',inv_info)[0], 
                    snr=int(re.split('-',inv_info)[1]), 
                    method=re.split('-',inv_info)[2], 
                    depth=int(re.split('-',inv_info)[3]), 
                    pick_normal=False, 
                    src=src_info)
megData.set(raw='ica-'+session, epoch=epoch, rej='')

res_cache_dir = os.path.join(data_path + f'/yi-test/ica-{epoch} emptyroom {inv_info} {src_info} {group}/')
res_cache_file = f' nobl tfce {str(tstart)}-{str(tstop)} {mask}'
plot_dir = f'/Users/yiwei/Dropbox/agrammatism/plots/{inv_info}/'


# %% [markdown]
# ### function to extract the time stamp and max T2 value of line segments that meet results reporting criteria. 

# %%
# set min_duration = 0, and min_value = 0 for supplementary materials table
# set min_duration = 0.01, and min_value = 4 for main document table

def extract_segments(data, step = 0.005, min_duration = 0.010, min_value = 4):
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
# ### load contrasts, conditions, define custom colormap for T2 line plot, define ROIs and their colors

# %%
contrasts = [
    # 'verbNaming-nounNaming',
    # 'nounPlural-nounNaming', 
    # 'nounPhrase-nounNaming',
    # 'verbInflectFuture-verbNaming',
    # 'verbInflectPast-verbNaming', 
    # 'nounPhrase-nounPlural',
    'verbInflectPast-verbInflectFuture',
    # 'regular-irregular',
    ]

conditions = [
    # 'nounNaming',
    # 'verbNaming',
    # 'nounPlural',
    # 'nounPhrase',
    # 'verbInflectFuture'
    # 'verbInflectPast'
    ]

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


custom_blue_cmap = custom_cmap('Blues')
custom_red_cmap = custom_cmap('Reds')
custom_green_cmap = custom_cmap('Greens')
custom_purple_cmap = custom_cmap('Purples')
custom_grey_cmap = custom_cmap('Greys')


lang_ROIs_dict = {
    ('G_precentral-lh'): ('LM1', custom_blue_cmap),
    ('G_front_inf-Opercular-lh','G_front_inf-Triangul-lh', 'G_front_inf-Orbital-lh'): ('LIFG', custom_red_cmap),
    ('G_pariet_inf-Angular-lh', 'G_pariet_inf-Supramar-lh'): ('LIPL', custom_green_cmap),
    (ATL_lh):('LATL', custom_grey_cmap),
    (PTL_lh):('LPTL', custom_purple_cmap),
}



# %% [markdown]
# ### plot colormap legend for T2 plot

# %%
min_cmap_start = 0.1

# Create custom cmap
cmap = custom_cmap("Greys", min_cmap_start=min_cmap_start)

# Fake mappable just for the colorbar
fig, ax = plt.subplots(figsize=(6, 1))
fig.subplots_adjust(bottom=0.5)

norm = plt.Normalize(vmin=min_cmap_start, vmax=1)
cb = plt.colorbar(
    plt.cm.ScalarMappable(norm=norm, cmap=cmap),
    cax=ax, orientation='horizontal'
)

ticks = np.linspace(min_cmap_start, 1.0, 6)
cb.set_ticks(ticks)
cb.set_ticklabels([f"{int(t*100)}%" for t in ticks])
cb.set_label("percentage of significant voxels within ATL")
# plt.savefig(os.path.join(plot_dir, f'significant results plot legend ATL.pdf'))
plt.show()

# %% [markdown]
# ### plot the T2 from the whole brain analysis results by ROI, using the percentage of significant voxels (within a given ROI) as colormap.

# %%
#### make sure to check this line before running this cell: 
#### color_array[color_array<0.3] = 0
#### This line is turned on for report in all the table, and turned off for the T squared plot.

# fig_size = (50,5) # set linewidth = 8 for the manuscript. verbNaming-nounNaming contrast
fig_size = (40,4) # set linewidth = 8 for the manuscript. other stimuli onset lock contrast

# use this for speak onset time locked contrasts. 
# ymax = 7
# ymin = -7.5

# # use this for stimulus time locked other contrasts. 
# ymax = 6
# ymin = -5

# # use this for verbNaming-nounNaming
# ymax = 7
# ymin = -6

# # use this for verbNaming-nounNaming
# ymax = 7
# ymin = -7

# # use this for stimulus time locked nounPhrase-nounPlural and verbInflectPast-verbInflectFuture
ymax = 6
ymin = -6


for contrast in contrasts:
    
    file_suffix = f' {trial_subset}_trials' if 'trial_subset' in globals() else ''
    cache_path = os.path.join(res_cache_dir, contrast + res_cache_file + file_suffix)
    
    # Load cached results or compute
    if glob.glob(cache_path + '*'):
        res = load.unpickle(cache_path)
    else:
        print("file doesn't exist")

    time_array = res.difference.time.times
    
    for roi,(label,cmap) in lang_ROIs_dict.items():
        
        fig, (ax_top, ax_bottom) = plt.subplots(
        2, 1, sharex=True, figsize=fig_size,
        gridspec_kw={'height_ratios': [1, (-ymin-3.5)/(ymax-3.5)], 'hspace': 0.05}
        )
        
        legend_handles = []

        cluster_sig = ~res.masked_difference().get_mask().any('space').sub(source=roi)
        color_array = (cluster_sig.sum(axis='source').x)/len(cluster_sig.x)
        
        ### choose whether to plot the line when the percentage of significant voxels is less than 30% of the ROI.
        ### This line is turned on for report in all the table, and turned off for the T squared plot. 
        # color_array[color_array<0.3] = 0
        
        T2 = res.t2.sub(source=roi) 
        test = T2*cluster_sig 
        test.x[test.x == 0] = np.nan
        x = time_array
        y = np.nanmean(test.x, axis = 0)

        points = np.array([x,y]).T.reshape(-1, 1, 2)
        
        a = res.c1_mean.sub(source = roi).norm('space').rms('source')
        b = res.c0_mean.sub(source = roi).norm('space').rms('source')

        stc_rms_diff_mask = a.x[:-1] < b.x[:-1]
                
        line_segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        # dotted line represent c1 (1st condition in each contrast)'s activation is weaker than c0
        dotted_line = line_segments[stc_rms_diff_mask] 
        solid_line = line_segments[~stc_rms_diff_mask]
        
        dotted_line[:, :, 1] *= -1

        dotted_line_collection = LineCollection(dotted_line, cmap = cmap, norm = Normalize(0, 1))
        solid_line_collection = LineCollection(solid_line, cmap = cmap, norm = Normalize(0, 1))

        dotted_line_collection.set_array(color_array[:-1][stc_rms_diff_mask])  # color per segment
        solid_line_collection.set_array(color_array[:-1][~stc_rms_diff_mask])  # color per segment

        legend_color = plt.colormaps.get_cmap(cmap)(0.5)
        
        dotted_line_collection.set_linewidth(8)
        solid_line_collection.set_linewidth(8)

        ax_top.set_ylim(3.5, ymax)
        ax_top.add_collection(solid_line_collection)
        
        ax_bottom.set_ylim(ymin, -3.5)
        ax_bottom.add_collection(dotted_line_collection)
        
        # Hide the "break" spines
        ax_top.spines['bottom'].set_visible(False)
        ax_bottom.spines['top'].set_visible(False)

        # Add diagonal slashes to show the axis break
        d = 0.01
        kwargs = dict(transform=ax_top.transAxes, color='k', clip_on=False)
        ax_top.plot((-d, +d), (-d, +d), **kwargs)
        ax_top.plot((1 - d, 1 + d), (-d, +d), **kwargs)

        kwargs.update(transform=ax_bottom.transAxes)
        ax_bottom.plot((-d, +d), (1 - d, 1 + d), **kwargs)
        ax_bottom.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)
        
        ax_top.plot([], [], color=legend_color, linewidth=6, label=label)

        xticks = np.arange(res.difference.time.tmin, time_array[-1] + 0.04, 0.04)
        yticks = np.arange(3.5, ymax+0.5, 0.5)

        plt.xticks(xticks)
        
        ax_bottom.set_yticks(np.arange(ymin, -3.5, 0.5))
        ax_top.set_yticks(np.arange(3.5, ymax+0.5, 0.5))
        
        ax_bottom.set_xlabel("time")
        ax_top.set_ylabel("t2")
        ax_bottom.set_ylabel("-t2")
        ax_top.set_title(f'{contrast}')
        ax_top.legend()
        ##### use this line for speech onset comparisons
        # ax_bottom.set_xlim(-0.4, 0.4)
        ##### use this line for verbNaming-nounNaming
        # ax_bottom.set_xlim(tstart, 2.6)
        ##### use this line for other contrasts. 
        ax_bottom.set_xlim(1.8, 3)
    
        ax_top.grid(True)
        ax_bottom.grid(True)
        # plt.savefig(os.path.join(plot_dir, f'{contrast}_sig_results_{label}_speakOnset.pdf'))
        # plt.savefig(os.path.join(plot_dir, f'{contrast}_sig_results_{label}.pdf'))

        plt.show()


# %% [markdown]
# #### print out sig. time and T2 value for when 1st condition in contrast is stronger than the 2nd condition

# %%
color_array_mask = color_array[:-1]!=0
solid_line_mask = ~stc_rms_diff_mask
combined_mask = color_array_mask & solid_line_mask
solid_nonzero_segments = line_segments[combined_mask]
solid_coord = solid_nonzero_segments.reshape(-1, 2)
# print(solid_coord)

solid_clean = solid_coord[~np.isnan(solid_coord[:,1])]
segments, maxima = extract_segments(solid_clean)
# print(segments)

for seg, m in zip(segments, maxima):
    ##### use this line for stimuli time locked analysis
    seg_ms = np.rint((seg[:,0]-1)*1000).astype(int)
    ##### use this line for response time locked analysis
    # seg_ms = np.rint((seg[:,0])*1000).astype(int)
    # print(seg_ms)
    print(f"{seg_ms[0]} - {seg_ms[-1]}ms (max  = {round(m, 2)})")
    print()

# %% [markdown]
# #### print out sig. time and T2 value for when 2nd condition in contrast is stronger than the 1st condition

# %%
color_array_mask = color_array[:-1]!=0
dotted_line_mask = stc_rms_diff_mask
combined_mask = color_array_mask & dotted_line_mask
dotted_nonzero_segments = line_segments[combined_mask]
dotted_coord = dotted_nonzero_segments.reshape(-1, 2)
# print(dotted_coord)

dotted_clean = dotted_coord[~np.isnan(dotted_coord[:,1])]
segments, maxima = extract_segments(dotted_clean)
# print(segments)

for seg, m in zip(segments, maxima):
    seg_ms = np.rint((seg[:,0]-1)*1000).astype(int)
    # seg_ms = np.rint((seg[:,0])*1000).astype(int)
    # print(seg_ms)
    print(f"{seg_ms[0]} - {seg_ms[-1]}ms (max  = {round(m, 2)})")
    print()

# %% [markdown]
# ### plot one sample t test results

# %%
fig_size = (48,8)

for condition in conditions:
        
    if glob.glob(os.path.join(res_cache_dir + condition + res_cache_file + '*')):
        res = load.unpickle(res_cache_dir + condition + res_cache_file)
    else:
        print("file doesn't exist")

    time_array = res.difference.time.times

    for roi,(label,cmap) in lang_ROIs_dict.items():
        
        fig, ax = plt.subplots(figsize=fig_size)
        legend_handles = []

        cluster_sig = ~res.masked_difference().get_mask().any('space').sub(source=roi)
        color_array = (cluster_sig.sum(axis='source').x)/len(cluster_sig.x)
        
        # color_array[color_array<0.3] = 0

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
        line_collection.set_linewidth(6)
        ax.add_collection(line_collection)
        
        legend_handles.append(mlines.Line2D([], [], color=legend_color, linewidth=2, label=label))

        xticks = np.arange(tstart, tstop + 0.04, 0.04)
        yticks = np.arange(3, 8.5, 0.5)

        ax.tick_params(axis = 'both', labelsize = 20)
        plt.xticks(xticks)
        plt.yticks(yticks)
        ax.set_xlabel("time")
        ax.set_ylabel("t2")
        ax.set_title(f'{condition}')
        ax.legend(handles=legend_handles)
        ax.set_ylim(3, 8)
        ax.set_xlim(tstart, 2.8)
        ax.grid(True)
        # plt.savefig(os.path.join(plot_dir, f'{contrast}_sig_results.pdf'))
        plt.show()


# %% [markdown]
# #### print out sig. time and T2 value for one sample t test

# %%
color_array_mask = color_array[:-1]!=0
solid_nonzero_segments = line_segments[color_array_mask]
solid_coord = solid_nonzero_segments.reshape(-1, 2)
# print(solid_coord)

solid_clean = solid_coord[~np.isnan(solid_coord[:,1])]
segments, maxima = extract_segments(solid_clean)
# print(segments)

for seg, m in zip(segments, maxima):
    seg_ms = np.rint((seg[:,0]-1)*1000).astype(int)
    print(f"{seg_ms[0]} - {seg_ms[-1]}ms (max  = {round(m, 2)})")
    print()

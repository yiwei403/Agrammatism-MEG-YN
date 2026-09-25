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
runpy.run_path('/Users/yiwei/Dropbox/agrammatism/code/zenodo scripts/s01_zenodo_pipelineSetup.py')
from s01_zenodo_pipelineSetup import *
import numpy as np

# NumPy 2.0 workaround for older mayavi/pysurfer
# np.in1d was renamed to np.isin in NumPy 2.x
if not hasattr(np, 'in1d'):
    np.in1d = np.isin

import re
import os
import glob
from surfer import Brain, TimeViewer 
from mayavi import mlab
import matplotlib.pyplot as plt

### from surfer import Brain, TimeViewer, and from mayavi import mlab stopped working after updating mac system to sequoia. 
# I no longer need mayavi since I'm not drawing arrows on the brain 
# but I do need to use Brain from surfer

# # turn this on for mne interactive plots
# %matplotlib qt 

# # %matplotlib widget

# turn this on for pysurfur plots
# # %gui qt 

# surface source analysis with fixed orientation did not seem to capture much brian activation
# probably due to individual differences in brain anatomy. 

inv_info = 'vec-3-MNE-0'
src_info = 'ico-4'
megData.set_inv(ori=re.split('-',inv_info)[0], 
                snr=int(re.split('-',inv_info)[1]), 
                method=re.split('-',inv_info)[2], 
                depth=int(re.split('-',inv_info)[3]), 
                pick_normal=False)
session = 'picturefirst'


# # use epoch = f'speak_{session}_regular' for all the contrast except for the verbInflectPast-verbNaming for the full data set analysis
# # for verbInflectPast-verbNaming, and 'regular-irregular' contrast, use epoch = f'speak_{session}
# epoch = f'speak_{session}'
# tstart = -1
# tstop = 1

# use epoch = f'trial_{session}_regular' for all the contrast except for the verbInflectPast-verbNaming for the full data set analysis
# for verbInflectPast-verbNaming, and 'regular-irregular' contrast, use epoch = f'trial_{session}
epoch = f'trial_{session}'
tstart = 1
tstop = 3

megData.set(raw='ica-'+session, epoch=epoch, rej='')
mask = 'aparc.a2009s'

group = 'right_hand'
subject_id, surf = 'fsaverage', 'pial'
hemi = 'lh'

res_cache_dir = os.makedirs(os.path.join(data_path + f'/yi-test/ica-{epoch} emptyroom {inv_info} {src_info} {group}/'), exist_ok=True)
res_cache_dir = os.path.join(data_path + f'/yi-test/ica-{epoch} emptyroom {inv_info} {src_info} {group}/')
res_cache_file = f' nobl tfce {str(tstart)}-{str(tstop)} {mask}'
plot_dir = f'/Users/yiwei/Dropbox/agrammatism/plots/{inv_info}/'

# %% [markdown]
# ### plot the brain with ROIs

# %%
brain = Brain(
    subject_id, hemi, surf, 
    size=(800, 800), interaction='terrain',
    # cortex='low_contrast', 
    cortex = '0.8',
    alpha=1, background=(1, 1, 1, 0), 
    show_toolbar=True, units='m',
    )


for label in syntax_cortical_label_lh:
    if "G_precentral" in label.name:
        brain.add_label(label, color = plt.colormaps.get_cmap('Blues')(0.65), borders=True, alpha=1)
        #### use cortex='low_contrast' and this second line to create the spatialtemporal model of speech production plot. 
        # brain.add_label(label, color = plt.colormaps.get_cmap('Blues')(0.9), borders=True, alpha=1)

        
for label in syntax_cortical_label_lh:
    if "G_front_inf" in label.name:
        # brain.add_label(label, color = plt.colormaps.get_cmap('Reds')(0.6), borders=True, alpha=1)
        brain.add_label(label, color = plt.colormaps.get_cmap('Reds')(0.9), borders=True, alpha=1)

for label in syntax_cortical_label_lh:
    if "G_pariet_inf" in label.name:
        # brain.add_label(label, color = plt.colormaps.get_cmap('Greens')(0.6), borders=True, alpha=1)
        brain.add_label(label, color = plt.colormaps.get_cmap('Greens')(0.9), borders=True, alpha=1)

        
# brain.add_label(ATL_lh, color = plt.colormaps.get_cmap('Greys')(0.7), borders=True, alpha=1)
brain.add_label(ATL_lh, color = plt.colormaps.get_cmap('Greys')(0.9), borders=True, alpha=1)


# brain.add_label(PTL_lh, color = plt.colormaps.get_cmap('Purples')(0.6), borders=True, alpha=1)
brain.add_label(PTL_lh, color = plt.colormaps.get_cmap('Purples')(0.9), borders=True, alpha=1)


V1_label_lh = [
    label for label in aparc_a2009s_labels if label.name in [
        'S_calcarine-lh',
        'Pole_occipital-lh'
        ]]
V1_lh = V1_label_lh[0]+V1_label_lh[1]

# brain.add_label(V1_lh, color = plt.colormaps.get_cmap('hsv')(0.5), borders=True, alpha=1)
brain.add_label(V1_lh, color = plt.colormaps.get_cmap('hsv')(0.6), borders=True, alpha=1)

        
# brain.save_image(os.path.join(plot_dir, f'brain_ROI_outline.png'), mode = 'rgba')

# brain.close()  

# %% [markdown]
# ### plot source timecourse by ROI by condition (look at condition/comparison stc by ROI)

# %%
conditions = [
    'nounNaming',
    # 'nounPlural',
    # 'nounPhrase',
    'verbNaming',
    # 'verbInflectFuture',
    # 'verbInflectPast'
    ]

lang_ROIs_dict = {
    ('S_calcarine-lh', 'Pole_occipital-lh'):('V1', 'cyan'),
    ('G_precentral-lh'): ('M1', 'Blues'),
    ('G_front_inf-Opercular-lh','G_front_inf-Triangul-lh',  'G_front_inf-Orbital-lh'): ('IFG', 'Reds'),
    ('G_pariet_inf-Angular-lh', 'G_pariet_inf-Supramar-lh'): ('SMG+AG', 'Greens'),
    (ATL_lh):('ATL', "Greys"),
    (PTL_lh):('PTL', "Purples"),
}

for condition in conditions:
    
    word_type=condition_abbrev_dict[condition]['abbrev']

    data = megData.load_evoked_stc(
        subjects=group, 
        baseline=False,
        cat=word_type,
        mask=mask, 
        cov='emptyroom', 
        model='wordType')

    time = data['srcm'].time.times

    plt.figure(figsize= (30,6))

    for ROI_mask, (label, cmap) in lang_ROIs_dict.items():    

        stc_rms = data['srcm'].sub(source=ROI_mask).norm('space').rms('source').x
        stc_mean_rms = np.mean(stc_rms, axis=0)
        std_err = np.std(stc_rms, axis=0) /np.sqrt(stc_rms.shape[0])

        if cmap == 'Greys':
            line_color = plt.colormaps.get_cmap(cmap)(0.6)
        elif cmap == 'Reds':
            line_color = plt.colormaps.get_cmap(cmap)(0.6)
        elif cmap == "Blues":
            line_color = plt.colormaps.get_cmap(cmap)(0.65)
        elif cmap == "Greens":
            line_color = plt.colormaps.get_cmap(cmap)(0.6)
        elif cmap == "Purples":
            line_color = plt.colormaps.get_cmap(cmap)(0.7)
        else: 
            line_color = cmap

        plt.plot(time, stc_mean_rms, label = f'{label}', color=line_color, linewidth = 6)
        plt.fill_between(time, stc_mean_rms-std_err, stc_mean_rms+std_err, alpha=0.2)

    xticks = np.arange(data['srcm'].time.tmin, time[-1] + 0.1, 0.1)
    plt.xticks(xticks)
    plt.xlim(tstart,2.8)
    plt.grid()
    plt.ylim(-1e-11, 8e-11)
    plt.title(f'{condition}')
    plt.legend()
    # plt.savefig(os.path.join(plot_dir, f'{condition}_ROI_rms_stc_norm_space.pdf'))
    plt.show()
    

# %% [markdown]
# ### run and plot one sample t test

# %%
tois = np.arange(1, 3, 0.1)

conditions = [
    # 'nounNaming',
    # 'verbNaming',
    # 'nounPlural',
    # 'nounPhrase',
    # 'verbInflectFuture',
    'verbInflectPast',
    ]

for condition in conditions:    
    
    word_type=condition_abbrev_dict[condition]['abbrev']
        
    data = megData.load_evoked_stc(
        subjects=group, 
        baseline=False, 
        cat=word_type,
        mask=mask, 
        cov='emptyroom', 
        model='wordType')


    if glob.glob(os.path.join(res_cache_dir + condition + res_cache_file + '*')):
        res = load.unpickle(res_cache_dir + condition + res_cache_file)
    else:
        res = testnd.Vector('srcm', data=data, match='subject', tstart=tstart, tstop=tstop, tfce=True)
        save.pickle(res, res_cache_dir + condition + res_cache_file)
    
    masked_difference_data = res.masked_difference()
    vertices = np.concatenate(data['srcm'].source.vertices) 

    stc = mne.VectorSourceEstimate(data=masked_difference_data.x.filled(0), vertices=data['srcm'].source.vertices, tmin=-0.1, tstep=0.005)
    clim=dict(kind='value',lims=[1e-11, 2e-11, 5.53e-11])

    mne_brain = mne.viz.plot_source_estimates(
        stc,
        subject=subject_id,
        hemi="lh",
        surface = 'pial',
        subjects_dir=subjects_dir,
        brain_kwargs=dict(cortex=(0.7, 0.7, 0.7)),
        smoothing_steps=7,
        cortex = 'classic',
        size = (600, 600),
        show_traces=False,
        transparent = True,
        background = 'white',
        clim = clim,
        time_viewer = False,
        colorbar = False,
    )
    
    for label in syntax_cortical_label_lh:
        if "G_precentral" in label.name:
            mne_brain.add_label(label, color = plt.colormaps.get_cmap('Blues')(0.65), borders=True, alpha=1)
        
    for label in syntax_cortical_label_lh:
        if "G_front_inf" in label.name:
            mne_brain.add_label(label, color = plt.colormaps.get_cmap('Reds')(0.6), borders=True, alpha=1)
            
    for label in syntax_cortical_label_lh:
        if "G_pariet_inf" in label.name:
            mne_brain.add_label(label, color = plt.colormaps.get_cmap('Greens')(0.6), borders=True, alpha=1)
            
    mne_brain.add_label(ATL_lh, color = plt.colormaps.get_cmap('Greys')(0.7), borders=True, alpha=1)

    mne_brain.add_label(PTL_lh, color = plt.colormaps.get_cmap('Purples')(0.6),borders=True,  alpha=1)
        
    for toi in tois:        
        mne_brain.set_time(toi)
        # mne_brain.save_image(os.path.join(plot_dir, f'{condition}_{round(toi,3)}_mne.png'))


# %% [markdown]
# ### run and plot paired sample t test

# %%
# # # use this for verbNaming-nounNaming
# tois = np.arange(1.06, 2.6, 0.16)

# # use this for nounPlural-nounNaming, nounpPhrase-nounNaming, and verbInflectPast-verbNaming
# # nounPhrase-nounPlural, verbInflectPast-verbInflectFuture
tois = np.arange(1.98, 2.78, 0.08)

# # use this for verbInflectFuture-verbNaming.
# tois = np.arange(2.06, 2.86, 0.08)

# # use this for verbInflectFuture-verbNaming of speak onset trials.
# tois = np.arange(-0.32, 0.4, 0.08)

contrasts = [
    # "nounNaming-nounControl",
    # "verbNaming-verbControl",
    # "verbNaming-nounNaming",
    "nounPlural-nounNaming",
    # "nounPhrase-nounNaming",
    # "verbInflectFuture-verbNaming",
    # "verbInflectPast-verbNaming",
    # "nounPhrase-nounPlural",
    # "verbInflectPast-verbInflectFuture",
]

for contrast in contrasts:
    
    cond1, cond2 = contrast.split('-')
    word_type_1 = condition_abbrev_dict[cond1]['abbrev']
    word_type_2 = condition_abbrev_dict[cond2]['abbrev']

    # Load evoked data
    data = megData.load_evoked_stc(
        subjects=group, 
        baseline=False, 
        mask=mask, 
        cat=[word_type_1, word_type_2],
        cov='emptyroom', 
        model='wordType')
    
    file_suffix = f' {trial_subset}_trials' if 'trial_subset' in globals() else ''
    cache_path = os.path.join(res_cache_dir, contrast + res_cache_file + file_suffix)
    
    # Load cached results or compute
    if glob.glob(cache_path + '*'):
        res = load.unpickle(cache_path)
    else:
        res = testnd.VectorDifferenceRelated(
            'srcm', 'wordType',
            c1=f'{word_type_1}', c0=f'{word_type_2}',
            match='subject', data=data, tfce=True,
            tstart=tstart, tstop=tstop
        )
        save.pickle(res, cache_path)
        
    cluster_sig = ~res.masked_difference().get_mask().any('space')
    data_diff = res.c1_mean.norm('space') - res.c0_mean.norm('space')
    signs = np.sign(data_diff)
    signed_norm_diff = res.masked_difference().norm('space')*signs
    
    
    #################define bin myself
    signed_norm_diff_data = signed_norm_diff.x
    times = signed_norm_diff.time.times
    # trial starting time for response onset trials
    tmin = -0.1  
    # trial starting time for speak onset trials
    # tmin = -1
    fs = 200
    half_window = int(0.04 * fs) 
    stc_data = np.zeros((signed_norm_diff_data.shape[0], len(tois)))
    
    for i, toi in enumerate(tois):
        center_idx = int(round((toi-tmin)*fs))
        
        start = max(0, center_idx - half_window)
        end = min(len(times), center_idx + half_window)
        
        stc_data[:,i] = np.ma.mean(signed_norm_diff_data[:, start:end], axis=1)
       
    # clim=dict(kind='value',pos_lims=[0.5e-11, 1.3e-11, 2.64e-11]) # verbNaming-nounNaming
    clim=dict(kind='value',pos_lims=[0.3e-11, 1.3e-11, 2.31e-11]) # other contrasts
    # clim=dict(kind='value',pos_lims=[0.7e-11, 1.7e-11, 3.34e-11]) # speak onset locked contrasts

    # break    
    for t in range(stc_data.shape[1]):
        stc_bin = mne.SourceEstimate(data=stc_data[:,t], vertices=data['srcm'].source.vertices, tmin=-0.1, tstep=0.005)

        mne_brain = mne.viz.plot_source_estimates(
            stc_bin,
            subject = subject_id,
            surface = surf,
            hemi = hemi,
            subjects_dir = subjects_dir,
            brain_kwargs = dict(cortex=(0.7, 0.7, 0.7)),
            smoothing_steps = 7,
            cortex = 'classic',
            size = (600, 600),
            show_traces = False,
            transparent = True,
            background = 'white',
            alpha = 0.9,
            clim = clim,
            time_viewer = False,
            colorbar = False,
        )

        for label in syntax_cortical_label_lh:
            if "G_precentral" in label.name:
                mne_brain.add_label(label, color = plt.colormaps.get_cmap('Blues')(0.65), borders=True, alpha=1)
            
        for label in syntax_cortical_label_lh:
            if "G_front_inf" in label.name:
                mne_brain.add_label(label, color = plt.colormaps.get_cmap('Reds')(0.6), borders=True, alpha=1)
                
        for label in syntax_cortical_label_lh:
            if "G_pariet_inf" in label.name:
                mne_brain.add_label(label, color = plt.colormaps.get_cmap('Greens')(0.6), borders=True, alpha=1)
                
        mne_brain.add_label(ATL_lh, color = plt.colormaps.get_cmap('Greys')(0.7), borders=True, alpha=1)

        mne_brain.add_label(PTL_lh, color = plt.colormaps.get_cmap('Purples')(0.6),borders=True,  alpha=1)
            

    mne_brain.close()

# %% [markdown]
# ### extract mne colorbar

# %%
# clim=dict(kind='value',pos_lims=[0.5e-11, 1.3e-11, 2.64e-11]) # verbNaming-nounNaming stimuli locked response
# clim=dict(kind='value',pos_lims=[0.3e-11, 1.3e-11, 2.31e-11]) # other contrasts stimuli locked response
# clim=dict(kind='value',pos_lims=[0.7e-11, 1.7e-11, 3.34e-11]) # speak onset locked response
clim=dict(kind='value',lims=[1e-11, 2e-11, 5.53e-11]) # for one sample t test 


fig, ax = plt.subplots(figsize=(0.5,8))
mne_colorbar = mne.viz.plot_brain_colorbar(ax, clim, colormap='auto', transparent=True, orientation='vertical', label='Activation', bgcolor='0.5')

fig.savefig(
    os.path.join(plot_dir, f'colorbar_1sample.pdf'),
    bbox_inches="tight",
    transparent=True)

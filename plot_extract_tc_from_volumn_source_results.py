# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: eelbrain
#     language: python
#     name: python3
# ---

# ###  This script extracts timecourse from a significant cluster (that overlaps with ROI) between two conditions generated from volume source space vector-valued dipole currents
# * #### Need to run plot_results_in_volume_space.py first to visually inspect significant cluster of interests. 
# * #### this is the version for HSP2025 poster results
# * #### HSP2025 poster link: https://drive.google.com/drive/u/1/folders/1ku8GXxQ5qn7UmHELchIiVl-AjNlckeQ4

# +
import runpy
runpy.run_path('/Users/yiwei/Dropbox/agrammatism/code/s01_eelbrain_pipelineSetup.py')
from s01_eelbrain_pipelineSetup import *
import os
import re
import glob
import numpy

session = 'picturefirst'
epoch = 'trial_picturefirst_regular'
contrast = 'verbInflectFuture-verbNaming'
tstart = 1.8
tstop = 3
mask = 'wholebrain_cortical_subcortical_mask'
inv_info = 'vec-3-MNE-0'
group = 'right_hand' 
src_info = 'vol-5'
plot_name = f"{epoch}_{contrast}_{mask}"

condition_abbrev_dict = {
    'nounControl': {'abbrev': 'nouncontrol'},
    'nounNaming': {'abbrev': 'nounnm'},
    'nounPlural': {'abbrev': 'nounpp'},
    'nounPhrase':{'abbrev': 'nounpc'},
    'verbControl': {'abbrev': 'verbcontrol'},
    'verbNaming': {'abbrev': 'verbnm'},
    'verbInflect':{'abbrev': 'verbinflect'},
    'verbInflectPast':{'abbrev': 'infpst'},
    'verbInflectFuture':{'abbrev': 'inffut'}
}

if "-" in contrast or "=" in contrast:
    condition1, condition2 = re.split('[-=]', contrast)
    wordType1 = condition_abbrev_dict[condition1]['abbrev']
    wordType2 = condition_abbrev_dict[condition2]['abbrev']
    
megData.set_inv(ori=re.split('-',inv_info)[0], 
                    snr=int(re.split('-',inv_info)[1]), 
                    method=re.split('-',inv_info)[2], 
                    depth=int(re.split('-',inv_info)[3]), 
                    pick_normal=False, 
                    src=src_info)
megData.set(parc = 'aparc+aseg')
megData.set(raw='ica-'+session, epoch=epoch, rej='')

res_cache_dir = os.path.join(data_path + f'/yi-test/ica-{epoch} emptyroom {inv_info} {src_info} {group}/')
res_cache_file = f' nobl tfce {str(tstart)}-{str(tstop)} {mask}'
# -

# ### load source timecourse data from the mask for all the conditions 

# +
if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
    res = load.unpickle(res_cache_dir + contrast + res_cache_file)
else:
    print("file doesn't exist")
    
erp_stc_all_wordType = megData.load_evoked_stc(
subjects=group, 
baseline=False,
cov='emptyroom', 
model='wordType')
erp_stc_all_wordType['srcm']=set_parc(erp_stc_all_wordType['srcm'],'aparc+aseg')

# -

# ### define time of interest and find a list of significant clusters (labels) at that time point 
# * #### time of interest is defined by visually inspect results from plot_results_in_volume_space.py

TOI = 2.36
cluster_TOI_masked = res.masked_difference().sub(time=TOI)
cluster_TOI_sig = ~cluster_TOI_masked.get_mask().any('space')
labels = cluster_TOI_sig.label_clusters()
print(labels.info['cids'])

# ### plot all the labels and look for if any label contains the ROI

for label in labels.info['cids']:
    p = plot.GlassBrain(labels==label,display_mode='lzr',title=f'label={label}')

# ### edit the label shape
# * #### if one of the labels contains the ROI but also contains unwanted brain regions, use the following code to crop the region of that label to form desired ROI
# * #### skip the next cell if using customized label

# +
# labelNo = 1
# ROI = labels == labelNo
# cluster_ROI = cluster_TOI_masked * ROI
# mask = cluster_ROI.source.coordinates[:,0] > -0.05
# mask *= cluster_ROI.source.coordinates[:,1] > 0.03
# ROI *= mask
# p = plot.GlassBrain(ROI,display_mode='lyrz',)
# -

# ### choose which label to use
# * #### do not run this cell if customizing a label

labelNo = 122
ROI = labels == labelNo

# ### plot the ROI source data on a glass brain

# +

vmax_source = 1e-11 

cluster_ROI = cluster_TOI_masked * ROI
save.pickle(cluster_ROI, 'colormaptest.pickle')

p1 = plot.GlassBrain(
    cluster_ROI,
    display_mode='lzr', 
    black_bg=False, 
    cmap='hot_r', 
    vmin=0,
    vmax = vmax_source,
    # show_time=True,
    # colorbar=True,
    # title = f"{contrast}_{TOI}s"
)
p2 = plot.ColorBar(cmap='hot_r', vmin=0, vmax=vmax_source)
# p1.save(f'MNE_{plot_name}, TOI={TOI}, label={labelNo}.pdf')
# p2.save(f'MNE_{plot_name}, TOI={TOI}, label={labelNo}, ColorBar.pdf')


# p1.save(f'MNE_{plot_name}, TOI={TOI}, label={labelNo}, x>-0.05, y>0.03.pdf')
# p2.save(f'MNE_{plot_name}, TOI={TOI}, label={labelNo}, x>-0.05, y>0.03, ColorBar.pdf')

# -

# ### plot the timecourse of selected conditions from that ROI

# +

erp_stc_all_wordType['ROI_tc'] = cluster_ROI.dot(erp_stc_all_wordType['srcm'], ['source', 'space'])
p = plot.UTSStat(
    'ROI_tc',
    'wordType',
    data=erp_stc_all_wordType,
    # sub = f"(wordType=='{wordType1}')|(wordType=='{wordType2}')|(wordType=='inffut')",
    sub = f"(wordType=='nounnm')|(wordType=='nounpp')|(wordType=='nounpc')",
    xlim=[2.5,2.7],
    
    # title = f"{contrast}_{TOI}s"
    # legend='lower right',
    w = 6,
    h = 10,
)
# p.save(f'MNE_{plot_name}, TOI={TOI}, label={labelNo}, x>-0.05, y>0.03, noun conditions timecourse.pdf')


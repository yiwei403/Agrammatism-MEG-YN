
import runpy
runpy.run_path('/Users/yiwei/Dropbox/agrammatism/code/s01_eelbrain_pipelineSetup.py')
from s01_eelbrain_pipelineSetup import *
import sys
import os
import re
import glob

# this is the version for HSP2025 poster results

epoch = sys.argv[1]
contrast = sys.argv[2]
tstart = sys.argv[3]
tstop = sys.argv[4]
mask = sys.argv[5]
inv_info = sys.argv[6]
group = sys.argv[7]

if len(sys.argv)>8:
    clusterInd = int(sys.argv[8])

# session = 'picturefirst'
# epoch = 'trial_picturefirst_regular'
# contrast = 'nounNaming-nounControl'
# tstart = 1.8
# tstop = 3
# mask = 'wholebrain_cortical_subcortical_mask'
# inv_info = 'vec-3-MNE-0'
# group = 'right_hand' 

src_info = 'vol-5'
vmax_source = 2.5e-11
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

# one sample vector t test results was saved 
if "-" in contrast:
    condition1, condition2 = re.split('-', contrast)
    wordType1 = condition_abbrev_dict[condition1]['abbrev']
    wordType2 = condition_abbrev_dict[condition2]['abbrev']

res_cache_dir = os.path.join(data_path + f'/yi-test/ica-{epoch} emptyroom {inv_info} {src_info} {group}/')
res_cache_file = f' nobl tfce {str(tstart)}-{str(tstop)} {mask}'
    
if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):   
    res = load.unpickle(res_cache_dir + contrast + res_cache_file)
    # print(epoch + ': ' + contrast + '\n' + str(res.find_clusters()))
else:
    print("file doesn't exist")
    

# if only want to look at glassbrain and butterfly plots of one of the significant clusters. 
if len(sys.argv) > 8:

    clusters_all = res.find_clusters(maps=True)
    case = clusters_all[clusterInd]
    c_map = case['cluster']
    cluster = c_map.any('time')

    plot.GlassBrain.butterfly(
        res.masked_difference().sub(source=cluster), 
        display_mode='lzr', 
        black_bg=False, 
        cmap='hot_r', 
        # colorbar=True,
        title=case['location'],
    )
    
else:
    
    # glassbrain and butterfly plots for all the significant clusters across time
    if "-" in contrast or "=" in contrast:
        # ########################   plot brain areas that's significantly different between conditions
        # plot.GlassBrain.butterfly(
        #     res.masked_difference(), 
        #     display_mode='lzr', 
        #     black_bg=False, 
        #     cmap='hot_r', 
        #     vmax=vmax_source, 
        #     title=plot_name,
        # )
        
        ##########################   generate pdf file for each timestamp
        for t in [2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7]:
            p = plot.GlassBrain(
                res.masked_difference(), 
                display_mode='lzr', 
                black_bg=False, 
                cmap='hot_r', 
                vmax=vmax_source, 
                show_time=True,
                h=3,
                w=8,
                )
            p.set_time(t)
            p.save(f'MNE_{plot_name} at {str(t)}ms.pdf')
        
        
    else:
        
        
        ###########################   plot brain areas that's significantly different between conditions
        # plot.GlassBrain.butterfly(
        #     res.masked_difference(p=1e-8), 
        #     display_mode='lzr', 
        #     black_bg=False, 
        #     cmap='hot_r', 
        #     vmax=3e-11, 
        #     title=plot_name,
        # )
        
        # ##########################   generate pdf file for each timestamp
        for t in [2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7]:
            p = plot.GlassBrain(
                res.masked_difference(p=1e-8), 
                display_mode='lzr', 
                black_bg=False, 
                cmap='hot_r', 
                show_time=True,
                vmax=2.5e-11,
                h=3,
                w=8,
                )
            p.set_time(t)
            p.save(f'MNE_{plot_name} at {str(t)}ms.pdf')
        
import runpy
runpy.run_path('/Users/yiwei/Dropbox/agrammatism/code/s01_eelbrain_pipelineSetup.py')
from s01_eelbrain_pipelineSetup import *
import sys
import os
import re
import mne
import numpy as np
# %matplotlib qt 

import glob

epoch = sys.argv[1]
contrast = sys.argv[2]
mask = sys.argv[3]
inv_info = sys.argv[4]
group = sys.argv[5]

# epoch = 'icon'
# contrast = 'nounNaming-nounControl'
# mask = 'wholebrain_cortical_subcortical_mask'
# inv_info = 'vec-3-MNE-0'
# group = 'all'

vmax_source = 10
src_info = 'vol-5'
plot_name = f"{epoch}_epoch_{contrast}_{mask}_{group}"

condition1, condition2 = re.split('[-=]', contrast)

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

wordType1 = condition_abbrev_dict[condition1]['abbrev']
wordType2 = condition_abbrev_dict[condition2]['abbrev']

res_cache_dir = os.path.join(data_path + '/yi-test/emptyroom ' + inv_info + ' ' + group + '/')


if inv_info != 'fixed-3-MNE-0':
    
    res_cache_file = (' nobl tfce ' + mask + ' ' + src_info)
        
    res = load.unpickle(res_cache_dir + epoch + ' epoch long ' + contrast + res_cache_file)
    plot.GlassBrain.butterfly(res.masked_difference(), display_mode='lzr', black_bg=False, cmap='lux-purple-a', 
                                vmax=vmax_source, title=plot_name)
else: 
    res_cache_file = (' nobl tfce ' + mask)
        
    res = load.unpickle(res_cache_dir + epoch + ' epoch long' + contrast + res_cache_file)
    plot.brain.butterfly(res.masked_difference(), surf='inflated', name=plot_name)



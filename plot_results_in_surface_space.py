import runpy
runpy.run_path('/Users/yiwei/Dropbox/agrammatism/code/s01_eelbrain_pipelineSetup.py')
from s01_eelbrain_pipelineSetup import *
import sys
import os
import re
import glob

session = sys.argv[1]
contrast = sys.argv[2]
tstart = sys.argv[3]
tstop = sys.argv[4]
mask = sys.argv[5]
group = sys.argv[6]

inv_info = 'fixed-3-MNE-0'

# session = 'iconfirst'
# contrast = 'nounNaming-nounControl'
# tstart = 1
# tstop = 3
# mask = 'lateral'
# group = 'all'

condition1, condition2 = re.split('[-=]', contrast)

# surf = 'smoothwm'
surf = 'inflated'
vmin_source = -2e-10
vmax_source = 2e-10
vmin_sensor = -1e-13
vmax_sensor = 1e-13
plot_name = f"{session}_{contrast}_{group}"

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
if condition2 != '0':
    wordType2 = condition_abbrev_dict[condition2]['abbrev']

res_cache_dir = os.path.join(data_path + '/yi-test/ica-' + session + ' emptyroom ' + inv_info + ' ' + group + '/')
res_cache_file = (' nobl tfce '+ str(tstart) + '-' + str(tstop) + ' ' + mask)


if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
    
    res = load.unpickle(res_cache_dir + contrast + res_cache_file)
    plot.brain.butterfly(res.masked_difference(), vmin=vmin_source, vmax=vmax_source, surf=surf, name=plot_name)
    
else:
    
    def find_files(condition1, condition2, tstart, tstop):
        tstart = str(int(float(tstart)*1000))
        tstop = str(int(float(tstop)*1000))
        
        if condition2 == '0':
            filename = f'{condition1}_{session} =0 nobl tfce {tstart}-{tstop} {mask}-mask.pickled'
        else:
            filename = f'speak_{session} {condition1}-{condition2} nobl tfce {tstart}-{tstop} {mask}-mask.pickled'
        return filename
    
    res_filename = find_files(condition1, condition2, tstart, tstop)
    res = load.unpickle(os.path.join(data_path + '/eelbrain-cache/test/ica-' + session + ' emptyroom ' + inv_info + ' ' + group + '/' + res_filename))
    plot.brain.butterfly(res.masked_difference(), vmin=vmin_source, vmax=vmax_source, surf=surf, name=plot_name)

# %% plot sensor data

# megData.set(raw='ica-'+session, epoch='trial_'+session, rej='')

# evoked_sensor_all_wordType = megData.load_evoked(
#     subjects=group,
#     baseline=False,
#     model='wordType'
# )

# verbinflect_erp_stc = evoked_sensor_all_wordType.sub("(wordType=='infpst')|(wordType=='inffut')")
# verbinflect_erp_stc = verbinflect_erp_stc.aggregate('subject', drop='wordType')
# verbinflect_erp_stc['wordType']=Factor(['verbinflect'] * len(verbinflect_erp_stc['subject']))
# evoked_sensor_all_wordType = combine([verbinflect_erp_stc, evoked_sensor_all_wordType])

# if condition2 == '0':
    
#     sensor_data_wordType1 = evoked_sensor_all_wordType.sub(f"wordType=='{wordType1}'")
#     plot.TopoButterfly('meg', data = sensor_data_wordType1, title=session+': '+wordType1, vmin=vmin_sensor, vmax=vmax_sensor)
    
# else:
    
#     diff_sensor_data = table.difference(
#         'meg', 
#         'wordType', 
#         wordType1, 
#         wordType2, 
#         'subject',
#         data=evoked_sensor_all_wordType)
#     plot.TopoButterfly('meg', data = diff_sensor_data, title=session+': '+wordType1 + '-' + wordType2, vmin=vmin_sensor, vmax=vmax_sensor)


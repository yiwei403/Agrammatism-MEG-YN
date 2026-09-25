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

# ### analysis setup

# +
import runpy
runpy.run_path('/Users/yiwei/Dropbox/agrammatism/code/s01_eelbrain_pipelineSetup.py')
from s01_eelbrain_pipelineSetup import *
from plotting import plot_source_time_result
import re
import os
import glob

# this is the version for HSP2025 poster results

test_mask = ['Left-Cerebral-White-Matter']

wholebrain_cortical_subcortical_mask = [
 'Left-Cerebral-White-Matter',
 'Left-Lateral-Ventricle',
 'Left-Inf-Lat-Vent',
 'Left-Putamen',
 'Left-Hippocampus',
 'Left-Amygdala',
 'Left-Accumbens-area',
 'Left-vessel',
 'Right-Cerebral-White-Matter',
 'Right-Inf-Lat-Vent',
 'Right-Putamen',
 'Right-Hippocampus',
 'Right-Amygdala',
 'ctx-lh-bankssts',
 'ctx-lh-caudalanteriorcingulate',
 'ctx-lh-caudalmiddlefrontal',
 'ctx-lh-cuneus',
 'ctx-lh-entorhinal',
 'ctx-lh-fusiform',
 'ctx-lh-inferiorparietal',
 'ctx-lh-inferiortemporal',
 'ctx-lh-isthmuscingulate',
 'ctx-lh-lateraloccipital',
 'ctx-lh-lateralorbitofrontal',
 'ctx-lh-lingual',
 'ctx-lh-medialorbitofrontal',
 'ctx-lh-middletemporal',
 'ctx-lh-parahippocampal',
 'ctx-lh-paracentral',
 'ctx-lh-parsopercularis',
 'ctx-lh-parsorbitalis',
 'ctx-lh-parstriangularis',
 'ctx-lh-pericalcarine',
 'ctx-lh-postcentral',
 'ctx-lh-posteriorcingulate',
 'ctx-lh-precentral',
 'ctx-lh-precuneus',
 'ctx-lh-rostralanteriorcingulate',
 'ctx-lh-rostralmiddlefrontal',
 'ctx-lh-superiorfrontal',
 'ctx-lh-superiorparietal',
 'ctx-lh-superiortemporal',
 'ctx-lh-supramarginal',
 'ctx-lh-frontalpole',
 'ctx-lh-temporalpole',
 'ctx-lh-transversetemporal',
 'ctx-lh-insula',
 'ctx-rh-bankssts',
 'ctx-rh-caudalanteriorcingulate',
 'ctx-rh-caudalmiddlefrontal',
 'ctx-rh-cuneus',
 'ctx-rh-entorhinal',
 'ctx-rh-fusiform',
 'ctx-rh-inferiorparietal',
 'ctx-rh-inferiortemporal',
 'ctx-rh-isthmuscingulate',
 'ctx-rh-lateraloccipital',
 'ctx-rh-lateralorbitofrontal',
 'ctx-rh-lingual',
 'ctx-rh-medialorbitofrontal',
 'ctx-rh-middletemporal',
 'ctx-rh-parahippocampal',
 'ctx-rh-paracentral',
 'ctx-rh-parsopercularis',
 'ctx-rh-parsorbitalis',
 'ctx-rh-parstriangularis',
 'ctx-rh-pericalcarine',
 'ctx-rh-postcentral',
 'ctx-rh-posteriorcingulate',
 'ctx-rh-precentral',
 'ctx-rh-precuneus',
 'ctx-rh-rostralanteriorcingulate',
 'ctx-rh-rostralmiddlefrontal',
 'ctx-rh-superiorfrontal',
 'ctx-rh-superiorparietal',
 'ctx-rh-superiortemporal',
 'ctx-rh-supramarginal',
 'ctx-rh-frontalpole',
 'ctx-rh-temporalpole',
 'ctx-rh-transversetemporal',
 'ctx-rh-insula']

lh_cortical_subcortical_mask = [
 'Left-Cerebral-White-Matter',
 'Left-Lateral-Ventricle',
 'Left-Inf-Lat-Vent',
 'Left-Putamen',
 'Left-Hippocampus',
 'Left-Amygdala',
 'Left-Accumbens-area',
 'Left-vessel',
 'ctx-lh-bankssts',
 'ctx-lh-caudalanteriorcingulate',
 'ctx-lh-caudalmiddlefrontal',
 'ctx-lh-cuneus',
 'ctx-lh-entorhinal',
 'ctx-lh-fusiform',
 'ctx-lh-inferiorparietal',
 'ctx-lh-inferiortemporal',
 'ctx-lh-isthmuscingulate',
 'ctx-lh-lateraloccipital',
 'ctx-lh-lateralorbitofrontal',
 'ctx-lh-lingual',
 'ctx-lh-medialorbitofrontal',
 'ctx-lh-middletemporal',
 'ctx-lh-parahippocampal',
 'ctx-lh-paracentral',
 'ctx-lh-parsopercularis',
 'ctx-lh-parsorbitalis',
 'ctx-lh-parstriangularis',
 'ctx-lh-pericalcarine',
 'ctx-lh-postcentral',
 'ctx-lh-posteriorcingulate',
 'ctx-lh-precentral',
 'ctx-lh-precuneus',
 'ctx-lh-rostralanteriorcingulate',
 'ctx-lh-rostralmiddlefrontal',
 'ctx-lh-superiorfrontal',
 'ctx-lh-superiorparietal',
 'ctx-lh-superiortemporal',
 'ctx-lh-supramarginal',
 'ctx-lh-frontalpole',
 'ctx-lh-temporalpole',
 'ctx-lh-transversetemporal',
 'ctx-lh-insula',
]

condition_abbrev_dict = {
    'nounNaming': {'abbrev': 'nounnm'},
    'nounControl': {'abbrev': 'nouncontrol'},
    'nounPlural': {'abbrev': 'nounpp'},
    'nounPhrase':{'abbrev': 'nounpc'},
    'verbControl': {'abbrev': 'verbcontrol'},
    'verbNaming': {'abbrev': 'verbnm'},
    'verbInflect':{'abbrev': 'verbinflect'},
    'verbInflectPast':{'abbrev': 'infpst'},
    'verbInflectFuture':{'abbrev': 'inffut'}
}

contrasts = ['verbInflectFuture-verbNaming']

# contrasts = ['nounNaming-nounControl', 'nounPlural-nounControl', 'nounPhrase-nounControl',
#              'nounPlural-nounNaming', 'nounPhrase-nounNaming',
#              'verbNaming-verbControl', 'verbInflectPast-verbInflectFuture',
#              'verbInflectPast-verbControl', 'verbInflectFuture-verbControl',
#              'verbInflectPast-verbNaming', 'verbInflectFuture-verbNaming']

inv_info = 'vec-3-MNE-0'
src_info = 'vol-5' # set up at vol-10 for testing
megData.set_inv(ori=re.split('-',inv_info)[0], 
                snr=int(re.split('-',inv_info)[1]), 
                method=re.split('-',inv_info)[2], 
                depth=int(re.split('-',inv_info)[3]), 
                pick_normal=False, 
                src=src_info)
megData.set(parc = 'aparc+aseg')

session = 'picturefirst'
epoch = f'trial_{session}_regular'
mask = wholebrain_cortical_subcortical_mask
tstart = 1.8
tstop = 3

color_list = ['#56B4E9', '#9400D3']
category = 'wordType'
group = 'right_hand'
mask_name = [name for name in globals() if globals()[name] is mask][0]
# -

# ### one sample t-tests

# +
res_cache_dir = os.makedirs(os.path.join(data_path + f'/yi-test/ica-{epoch} emptyroom {inv_info} {src_info} {group}/'), exist_ok=True)
res_cache_dir = os.path.join(data_path + f'/yi-test/ica-{epoch} emptyroom {inv_info} {src_info} {group}/')
res_cache_file = f' nobl tfce {str(tstart)}-{str(tstop)} {mask_name}'

conditions = ['nounNaming','verbControl','nounControl']

for condition in conditions:
        
    color_dict = {}
    legend_dict = {}    
    word_type = condition_abbrev_dict[condition]['abbrev']
    color_dict[word_type]=color_list[0]
    legend_dict[condition]=color_list[0]
        
    megData.set(raw='ica-'+session, epoch=condition+'_'+session, rej='')
    erp_stc_all_wordType = megData.load_evoked_stc(
        subjects=group, 
        baseline=False, 
        cov='emptyroom', 
        model='wordType')
        
    data = erp_stc_all_wordType.sub(f"(wordType == '{word_type}')")
    data['srcm']=set_parc(data['srcm'],'aparc+aseg')
    data['ROI'] = data['srcm'].sub(source=mask)

    res = testnd.Vector('ROI', match='subject', data=data, tfce=True, tstart=tstart, tstop=tstop)
    save.pickle(res, res_cache_dir + condition + res_cache_file)

    print(session + ': ' + condition + '\n' + str(res.find_clusters()))
# -

# ### paired t-tests between two conditions

# +

res_cache_dir = os.makedirs(os.path.join(data_path + f'/yi-test/ica-{epoch} emptyroom {inv_info} {src_info} {group}/'), exist_ok=True)
res_cache_dir = os.path.join(data_path + f'/yi-test/ica-{epoch} emptyroom {inv_info} {src_info} {group}/')
res_cache_file = f' nobl tfce {str(tstart)}-{str(tstop)} {mask_name}'
    
megData.set(raw='ica-'+session, epoch=epoch, rej='')
# load volume space evoked data.
erp_stc_all_wordType = megData.load_evoked_stc(
    subjects=group, 
    baseline=False,
    cov='emptyroom', 
    model='wordType')

for contrast in contrasts:

    color_dict = {}
    legend_dict = {}    
    cond1, cond2 = contrast.split('-')
    word_type_1 = condition_abbrev_dict[cond1]['abbrev']
    word_type_2 = condition_abbrev_dict[cond2]['abbrev']
    color_dict[word_type_1]=color_list[0]
    color_dict[word_type_2]=color_list[1]
    legend_dict[cond1]=color_list[0]
    legend_dict[cond2]=color_list[1]

    data = erp_stc_all_wordType.sub(f"(wordType == '{word_type_1}')|(wordType == '{word_type_2}')")

    data['srcm']=set_parc(data['srcm'],'aparc+aseg')
    data['ROI'] = data['srcm'].sub(source=mask)
    
    if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
        res = load.unpickle(res_cache_dir + contrast + res_cache_file)
    else:    
        res = testnd.VectorDifferenceRelated('ROI', 'wordType', c1=f'{word_type_1}', c0=f'{word_type_2}', match='subject', data=data, tfce=True, tstart=tstart, tstop=tstop)
        save.pickle(res, res_cache_dir + contrast + res_cache_file)
    
    # res = testnd.VectorDifferenceRelated('ROI', 'wordType', c1=f'{word_type_1}', c0=f'{word_type_2}', match='subject', data=data, tfce=True, tstart=tstart, tstop=tstop)
    # save.pickle(res, res_cache_dir + contrast + res_cache_file)

    print(session + ': ' + contrast + '\n' + str(res.find_clusters()))
# -

# ### other paired t-tests (more complicated comparisons)

# +
megData.set(raw='ica-'+session, epoch=epoch, rej='')

res_cache_dir = os.makedirs(os.path.join(data_path + f'/yi-test/ica-{epoch} emptyroom {inv_info} {src_info} {group}/'), exist_ok=True)
res_cache_dir = os.path.join(data_path + f'/yi-test/ica-{epoch} emptyroom {inv_info} {src_info} {group}/')
res_cache_file = f' nobl tfce {str(tstart)}-{str(tstop)} {mask_name}'

erp_stc_all_wordType = megData.load_evoked_stc(
    subjects=group, 
    baseline=False, 
    cov='emptyroom', 
    model='wordType')


verbnaming_erp_stc = erp_stc_all_wordType.sub("wordType=='verbnm'")
verbcontrol_erp_stc = erp_stc_all_wordType.sub("wordType=='verbcontrol'")

# combining verb inflection past and future conditions
verbinflect_erp_stc = erp_stc_all_wordType.sub("(wordType=='infpst')|(wordType=='inffut')")
verbinflect_erp_stc = verbinflect_erp_stc.aggregate('subject', drop='wordType', drop_bad=True)
verbinflect_erp_stc['wordType']=Factor(['verbinflect'] * len(verbinflect_erp_stc['subject']))

verbinflect_verbcontrol_ds = combine([verbinflect_erp_stc, verbcontrol_erp_stc], incomplete='drop')
verbinflect_verbnaming_ds = combine([verbinflect_erp_stc, verbnaming_erp_stc], incomplete='drop')

diff_verbnaming_verbcontrol = table.difference(
    'srcm', 
    'wordType', 
    'verbnm', 
    'verbcontrol', 
    'subject',
    data=erp_stc_all_wordType)
diff_verbnaming_verbcontrol['wordType']=Factor(['verb(naming-control)'] * len(diff_verbnaming_verbcontrol['subject']))



diff_verbinflectfuture_verbnaming = table.difference(
    'srcm', 
    'wordType', 
    'inffut', 
    'verbnm', 
    'subject',
    data=erp_stc_all_wordType)
diff_verbinflectfuture_verbnaming['wordType']=Factor(['verb(inflectfuture-naming)'] * len(diff_verbinflectfuture_verbnaming['subject']))


diff_verbinflectpast_verbnaming = table.difference(
    'srcm', 
    'wordType', 
    'infpst', 
    'verbnm', 
    'subject',
    data=erp_stc_all_wordType)
diff_verbinflectpast_verbnaming['wordType']=Factor(['verb(inflectpast-naming)'] * len(diff_verbinflectpast_verbnaming['subject']))



diff_verbinflect_verbcontrol = table.difference(
    'srcm', 
    'wordType', 
    'verbinflect', 
    'verbcontrol', 
    'subject',
    data=verbinflect_verbcontrol_ds)
diff_verbinflect_verbcontrol['wordType']=Factor(['verb(inflect-control)'] * len(diff_verbinflect_verbcontrol['subject']))


diff_verbinflect_verbnaming = table.difference(
    'srcm', 
    'wordType', 
    'verbinflect', 
    'verbnm', 
    'subject',
    data=verbinflect_verbnaming_ds)
diff_verbinflect_verbnaming['wordType']=Factor(['verb(inflect-naming)'] * len(diff_verbinflect_verbnaming['subject']))


diff_nounnaming_nouncontrol = table.difference(
    'srcm', 
    'wordType', 
    'nounnm', 
    'nouncontrol', 
    'subject',
    data=erp_stc_all_wordType)
diff_nounnaming_nouncontrol['wordType']=Factor(['noun(naming-control)'] * len(diff_nounnaming_nouncontrol['subject']))


diff_nounplural_nouncontrol = table.difference(
    'srcm', 
    'wordType', 
    'nounpp', 
    'nouncontrol', 
    'subject',
    data=erp_stc_all_wordType)
diff_nounplural_nouncontrol['wordType']=Factor(['noun(plural-control)'] * len(diff_nounplural_nouncontrol['subject']))


diff_nounphrase_nouncontrol = table.difference(
    'srcm', 
    'wordType', 
    'nounpc', 
    'nouncontrol', 
    'subject',
    data=erp_stc_all_wordType)
diff_nounphrase_nouncontrol['wordType']=Factor(['noun(phrase-control)'] * len(diff_nounphrase_nouncontrol['subject']))


diff_nounplural_nounnaming = table.difference(
    'srcm', 
    'wordType', 
    'nounpp', 
    'nounnm', 
    'subject',
    data=erp_stc_all_wordType)
diff_nounplural_nounnaming['wordType']=Factor(['noun(plural-naming)'] * len(diff_nounplural_nounnaming['subject']))



diff_nounphrase_nounnaming = table.difference(
    'srcm', 
    'wordType', 
    'nounpc', 
    'nounnm', 
    'subject',
    data=erp_stc_all_wordType)
diff_nounphrase_nounnaming['wordType']=Factor(['noun(phrase-naming)'] * len(diff_nounphrase_nounnaming['subject']))



################### paired t-test

# contrast = 'verbInflect-verbControl'
# data = combine([verbinflect_erp_stc, verbcontrol_erp_stc], incomplete='drop')
# data['srcm']=set_parc(data['srcm'],'aparc+aseg')
# data['ROI'] = data['srcm'].sub(source=mask)
# color_dict = {'verbinflect':color_list[0], 'verbcontrol':color_list[1]}
# legend_dict = {'verbInflect':color_list[0], 'verbControl':color_list[1]}
# if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
#     res = load.unpickle(res_cache_dir + contrast + res_cache_file)
# else:    
#     res = testnd.VectorDifferenceRelated('ROI', 'wordType', match='subject', data=data, tfce=True, tstart=tstart, tstop=tstop)
#     save.pickle(res, res_cache_dir + contrast + res_cache_file)
# print(session + ': ' + contrast + '\n' + str(res.find_clusters()))




# contrast = 'verbInflect-verbNaming'
# data = combine([verbinflect_erp_stc, verbnaming_erp_stc], incomplete='drop')
# data['srcm']=set_parc(data['srcm'],'aparc+aseg')
# data['ROI'] = data['srcm'].sub(source=mask)
# color_dict = {'verbinflect':color_list[0], 'verbnm':color_list[1]}
# legend_dict = {'verbInflect':color_list[0], 'verbNaming':color_list[1]}
# if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
#     res = load.unpickle(res_cache_dir + contrast + res_cache_file)
# else:    
#     res = testnd.VectorDifferenceRelated('ROI', 'wordType', match='subject', data=data, tfce=True, tstart=tstart, tstop=tstop)
#     save.pickle(res, res_cache_dir + contrast + res_cache_file)
# print(session + ': ' + contrast + '\n' + str(res.find_clusters()))



# contrast = 'verbNaming-verbControl_nounNaming-nounControl'
# data = combine([diff_verbnaming_verbcontrol, diff_nounnaming_nouncontrol], incomplete='drop')
# data['srcm']=set_parc(data['srcm'],'aparc+aseg')
# data['ROI'] = data['srcm'].sub(source=mask)    
# color_dict = {'verb(naming-control)':color_list[0], 'noun(naming-control)':color_list[1]}
# legend_dict = color_dict
# if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
#     res = load.unpickle(res_cache_dir + contrast + res_cache_file)
# else:    
#     res = testnd.VectorDifferenceRelated('ROI', 'wordType', match='subject', data=data, tfce=True, tstart=tstart, tstop=tstop)
#     save.pickle(res, res_cache_dir + contrast + res_cache_file)
# print(session + ': ' + contrast + '\n' + str(res.find_clusters()))



# contrast = 'verbInflect-verbControl_nounPlural-nounControl'
# data = combine([diff_verbinflect_verbcontrol, diff_nounplural_nouncontrol], incomplete='drop')
# data['srcm']=set_parc(data['srcm'],'aparc+aseg')
# data['ROI'] = data['srcm'].sub(source=mask)
# color_dict = {'verb(inflect-control)':color_list[0], 'noun(plural-control)':color_list[1]}
# legend_dict = color_dict
# if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
#     res = load.unpickle(res_cache_dir + contrast + res_cache_file)
# else:    
#     res = testnd.VectorDifferenceRelated('ROI', 'wordType', match='subject', data=data, tfce=True, tstart=tstart, tstop=tstop)
#     save.pickle(res, res_cache_dir + contrast + res_cache_file)
# print(session + ': ' + contrast + '\n' + str(res.find_clusters()))




# contrast = 'verbInflect-verbNaming_nounPlural-nounNaming'
# data = combine([diff_verbinflect_verbnaming, diff_nounplural_nounnaming], incomplete='drop')
# data['srcm']=set_parc(data['srcm'],'aparc+aseg')
# data['ROI'] = data['srcm'].sub(source=mask)
# color_dict = {'verb(inflect-naming)':color_list[0], 'noun(plural-naming)':color_list[1]}
# legend_dict = color_dict
# if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
#     res = load.unpickle(res_cache_dir + contrast + res_cache_file)
# else:    
#     res = testnd.VectorDifferenceRelated('ROI', 'wordType', match='subject', data=data, tfce=True, tstart=tstart, tstop=tstop)
#     save.pickle(res, res_cache_dir + contrast + res_cache_file)
# print(session + ': ' + contrast + '\n' + str(res.find_clusters()))




# contrast = 'verbInflect-verbControl_nounPhrase-nounControl'
# data = combine([diff_verbinflect_verbcontrol, diff_nounphrase_nouncontrol], incomplete='drop')
# data['srcm']=set_parc(data['srcm'],'aparc+aseg')
# data['ROI'] = data['srcm'].sub(source=mask)
# color_dict = {'verb(inflect-control)':color_list[0], 'noun(phrase-control)':color_list[1]}
# legend_dict = color_dict
# if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
#     res = load.unpickle(res_cache_dir + contrast + res_cache_file)
# else:    
#     res = testnd.VectorDifferenceRelated('ROI', 'wordType', match='subject', data=data, tfce=True, tstart=tstart, tstop=tstop)
#     save.pickle(res, res_cache_dir + contrast + res_cache_file)
# print(session + ': ' + contrast + '\n' + str(res.find_clusters()))




# contrast = 'verbInflect-verbNaming_nounPhrase-nounNaming' 
# data = combine([diff_verbinflect_verbnaming, diff_nounphrase_nounnaming], incomplete='drop')
# data['srcm']=set_parc(data['srcm'],'aparc+aseg')
# data['ROI'] = data['srcm'].sub(source=mask)
# color_dict = {'verb(inflect-naming)':color_list[0], 'noun(phrase-naming)':color_list[1]}
# legend_dict = color_dict
# if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
#     res = load.unpickle(res_cache_dir + contrast + res_cache_file)
# else:    
#     res = testnd.VectorDifferenceRelated('ROI', 'wordType', match='subject', data=data, tfce=True, tstart=tstart, tstop=tstop)
#     save.pickle(res, res_cache_dir + contrast + res_cache_file)
# print(session + ': ' + contrast + '\n' + str(res.find_clusters()))



contrast = 'verbInflectFuture-verbNaming_verbInflectPast-verbNaming' 
data = combine([diff_verbinflectfuture_verbnaming, diff_verbinflectpast_verbnaming], incomplete='drop')
data['srcm']=set_parc(data['srcm'],'aparc+aseg')
data['ROI'] = data['srcm'].sub(source=mask)
color_dict = {'verb(inflectfuture-naming)':color_list[0], 'verb(inflectpast-naming)':color_list[1]}
legend_dict = color_dict
# if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
#     res = load.unpickle(res_cache_dir + contrast + res_cache_file)
# else:    
res = testnd.VectorDifferenceRelated('ROI', 'wordType', match='subject', data=data, tfce=True, tstart=tstart, tstop=tstop)
save.pickle(res, res_cache_dir + contrast + res_cache_file)
print(session + ': ' + contrast + '\n' + str(res.find_clusters()))

# -

# ### compare epoch from different sessions across conditions

# +
# # This is a comparison I was trying, but didn't end up using. The idea is to compare the epoch from different sessions.
# # for example, difference between icon epoch from iconfirst trial and from picture first trial (icon epoch difference between conditions) is calculated for noun plural and noun naming conditions, respectively
# # then the icon epoch difference between conditions is compared between noun plural and noun naming conditions. 
# # The same analysis is then applied to picture epoch.
# # This analysis assumes that icon/picture epoch difference between conditions gets rid of processes elicited by icon/picture image (such as low level visual processing)
# # However, I'm not sure if the results make sense or not... 

# # epochs = ['icon']
# epochs = ['icon', 'picture']
# sessions = ['iconfirst', 'picturefirst']
# icon_epoch_type = 'icon epoch long regular '
# picture_epoch_type = 'picture epoch long '

# contrasts = ['verbInflectPast-verbNaming']
# # contrasts = ['nounNaming-nounControl', 'nounPlural-nounControl', 'nounPhrase-nounControl',
# #              'nounPlural-nounNaming', 'nounPhrase-nounNaming',
# #              'verbNaming-verbControl', 'verbInflectPast-verbControl', 'verbInflectFuture-verbControl',
# #              'verbInflectPast-verbInflectFuture',
# #              'verbInflectPast-verbNaming', 'verbInflectFuture-verbNaming',
# #              'verbInflect-verbControl', 'verbInflect-verbNaming']

# res_cache_dir = os.makedirs(os.path.join(data_path + '/yi-test/' + 'emptyroom ' + inv_info + ' ' + group + '/'), exist_ok=True)
# res_cache_dir = os.path.join(data_path + '/yi-test/' + 'emptyroom ' + inv_info + ' ' + group + '/')
# res_cache_file = (' nobl tfce ' + mask_name + ' ' + src_info)

# results = {}

# for epoch in epochs:
#     for session in sessions:
#         raw_type = f'ica-{session}'
#         epoch_type = f'{epoch}_{session}_long_regular'

#         stc_variable_name = f'stc_all_wordType_{epoch}_{session}'
        
#         megData.set(raw=raw_type, epoch=epoch_type, rej='')
        
#         results[stc_variable_name] = megData.load_evoked_stc(
#             subjects=group, 
#             baseline=False,
#             cov='emptyroom', 
#             model='wordType')
        
# # generating verbinflect epoch for icon epoch from iconfirst session
# verbinflect_stc_icon_iconfirst = results['stc_all_wordType_icon_iconfirst'].sub("(wordType=='infpst')|(wordType=='inffut')")
# verbinflect_stc_icon_iconfirst = verbinflect_stc_icon_iconfirst.aggregate('subject', drop='wordType')
# verbinflect_stc_icon_iconfirst['wordType']=Factor(['verbinflect'] * len(verbinflect_stc_icon_iconfirst['subject']))       

# # generating verbinflect epoch for icon epoch from picturefirst session
# verbinflect_stc_icon_picturefirst = results['stc_all_wordType_icon_picturefirst'].sub("(wordType=='infpst')|(wordType=='inffut')")
# verbinflect_stc_icon_picturefirst = verbinflect_stc_icon_picturefirst.aggregate('subject', drop='wordType')
# verbinflect_stc_icon_picturefirst['wordType']=Factor(['verbinflect'] * len(verbinflect_stc_icon_picturefirst['subject']))    

# # generating verbinflect epoch for picture epoch from iconfirst session
# verbinflect_stc_picture_iconfirst = results['stc_all_wordType_picture_iconfirst'].sub("(wordType=='infpst')|(wordType=='inffut')")
# verbinflect_stc_picture_iconfirst = verbinflect_stc_picture_iconfirst.aggregate('subject', drop='wordType')
# verbinflect_stc_picture_iconfirst['wordType']=Factor(['verbinflect'] * len(verbinflect_stc_picture_iconfirst['subject']))    

# # generating verbinflect epoch for picture epoch from picturefirst session
# verbinflect_stc_picture_picturefirst = results['stc_all_wordType_picture_picturefirst'].sub("(wordType=='infpst')|(wordType=='inffut')")
# verbinflect_stc_picture_picturefirst = verbinflect_stc_picture_picturefirst.aggregate('subject', drop='wordType')
# verbinflect_stc_picture_picturefirst['wordType']=Factor(['verbinflect'] * len(verbinflect_stc_picture_picturefirst['subject']))             


# icon_epochs_all_sessions = combine([results['stc_all_wordType_icon_iconfirst'], results['stc_all_wordType_icon_picturefirst']])

# icon_epochs_all_sessions = combine(
#     [results['stc_all_wordType_icon_iconfirst'], 
#      results['stc_all_wordType_icon_picturefirst'], 
#     verbinflect_stc_icon_iconfirst, 
#     verbinflect_stc_icon_picturefirst])

# picture_epochs_all_sessions = combine(
#     [results['stc_all_wordType_picture_iconfirst'], 
#      results['stc_all_wordType_picture_picturefirst'],
#     verbinflect_stc_picture_iconfirst,
#     verbinflect_stc_picture_picturefirst])


# for contrast in contrasts:
    
#     color_dict = {}
#     legend_dict = {}    
#     cond1, cond2 = contrast.split('-')
#     word_type_1 = condition_abbrev_dict[cond1]['abbrev']
#     word_type_2 = condition_abbrev_dict[cond2]['abbrev']
#     color_dict[word_type_1]=color_list[0]
#     color_dict[word_type_2]=color_list[1]
#     legend_dict[cond1]=color_list[0]
#     legend_dict[cond2]=color_list[1]
        
#     diff_icon_epoch_wordType1 = table.difference(
#         'srcm', 
#         'session',
#         'iconfirst',
#         'picturefirst',
#         'subject',
#         data=icon_epochs_all_sessions.sub(f"wordType=='{word_type_1}'"))

#     diff_icon_epoch_wordType2 = table.difference(
#         'srcm', 
#         'session',
#         'iconfirst',
#         'picturefirst',
#         'subject',
#         data=icon_epochs_all_sessions.sub(f"wordType=='{word_type_2}'"))
    
#     data_icon_epoch = combine([diff_icon_epoch_wordType1, diff_icon_epoch_wordType2], incomplete='drop')
#     data_icon_epoch['srcm']=set_parc(data_icon_epoch['srcm'],'aparc+aseg')
#     data_icon_epoch['ROI'] = data_icon_epoch['srcm'].sub(source=mask)
    
#     if glob.glob(os.path.join(res_cache_dir + icon_epoch_type + contrast + res_cache_file + '*')):
#         res_icon_epoch = load.unpickle(res_cache_dir + icon_epoch_type + contrast + res_cache_file)
#     else: 
#         res_icon_epoch = testnd.VectorDifferenceRelated('ROI', 'wordType', match='subject', data=data_icon_epoch, tfce=True, tstart=0, tstop=0.4)
#         save.pickle(res_icon_epoch, res_cache_dir + icon_epoch_type + contrast + res_cache_file)
    
#     print(icon_epoch_type + contrast + ': ' + '\n' + str(res_icon_epoch.find_clusters()))

#     diff_picture_epoch_wordType1 = table.difference(
#         'srcm', 
#         'session',
#         'iconfirst',
#         'picturefirst',
#         'subject',
#         data=picture_epochs_all_sessions.sub(f"wordType=='{word_type_1}'"))

#     diff_picture_epoch_wordType2 = table.difference(
#         'srcm', 
#         'session',
#         'iconfirst',
#         'picturefirst',
#         'subject',
#         data=picture_epochs_all_sessions.sub(f"wordType=='{word_type_2}'"))
    
#     data_picture_epoch = combine([diff_picture_epoch_wordType1, diff_picture_epoch_wordType2], incomplete='drop')
#     data_picture_epoch['srcm'] = set_parc(data_picture_epoch['srcm'],'aparc+aseg')
#     data_picture_epoch['ROI'] = data_picture_epoch['srcm'].sub(source=mask)
    
#     if glob.glob(os.path.join(res_cache_dir + picture_epoch_type + contrast + res_cache_file + '*')):
#         res_picture_epoch = load.unpickle(res_cache_dir + picture_epoch_type + contrast + res_cache_file)
#     else: 
#         res_picture_epoch = testnd.VectorDifferenceRelated('ROI', 'wordType', match='subject', data=data_picture_epoch, tfce=True, tstart=0, tstop=0.4)
#         save.pickle(res_picture_epoch, res_cache_dir + picture_epoch_type + contrast + res_cache_file)
    
#     print('picture epoch ' + contrast + ': ' + '\n' + str(res_picture_epoch.find_clusters()))
# -

# ### plot results in 3d glass brain MNE

# +
# trying out some plotting functions

import mne
import numpy as np
# %matplotlib qt 

data = data
res = res

vertices_all_list = data['srcm'].source.vertices
# save.pickle(vertices_all_list, '/Users/yiwei/Dropbox/agrammatism/code/vertices_all_list.pickle')
res_diff = res.masked_difference()
masked_res_diff = res_diff.x.filled(0)
vertices_ROI = res_diff.source.vertices[0]

dipoles_all_timeseries = np.zeros((len(vertices_all_list[0]),res_diff.shape[1],res_diff.shape[2]))

# Create a mapping from dipoleIndex to their positions
dipole_map = {vertex: idx for idx, vertex in enumerate(vertices_all_list[0])}

# Iterate through ROIVertices and update the new_array
for idx, vertex in enumerate(vertices_ROI):
    if vertex in dipole_map:
        dipoles_all_timeseries[dipole_map[vertex]] = masked_res_diff[idx]

subjects_dir = '/Users/yiwei/Documents/agrammatism/MEGstudy/mri/'
subject_id = 'fsaverage'

src = mne.read_source_spaces('/Users/yiwei/Documents/agrammatism/MEGstudy/mri/fsaverage/bem/fsaverage-vol-5-src.fif')
stc = mne.VolVectorSourceEstimate(data = dipoles_all_timeseries, vertices=vertices_all_list, tmin=-0.1, tstep=0.005)


# brain1 = stc.plot(
#     src = src,
#     subject = subject_id, 
#     subjects_dir=subjects_dir,
#     mode = 'stat_map',
#     # mode = 'glass_brain',
#     clim = {'kind':'value',
#             'lims': [0,5,10]}
# )


brain2 = stc.plot_3d(
    subject = subject_id, 
    hemi = 'both',
    subjects_dir=subjects_dir,
    clim = {'kind':'value',
            'lims': [0,1.5e-11,3e-11]
            },
    src = src,
    smoothing_steps=3,
    brain_alpha=0.2,
    cortex='low_contrast',
    
)

# brain2.save_movie(time_dilation=20, tmin=0.2, tmax=0.4, framerate=10,
#                  interpolation='linear', time_viewer=True)


# inv = megData.load_inv()
# stc_max, directions = stc.project('pca')
# # These directions must by design be close to the normals because this
# # inverse was computed with loose=0.2

# brain_max = stc_max.plot(
#     # initial_time=peak_time,
#     hemi="lh",
#     subjects_dir=subjects_dir,
#     time_label="Max power",
#     smoothing_steps=5,
# )

# ## plot coordinates 

# mask = np.any(masked_res_diff !=0, axis=(1,2))
# sig_coords=data_icon_epoch['ROI'].source.coordinates[mask,:]*1000
# brain.add_foci(sig_coords, coords_as_verts=False,  scale_factor=0.1, color='orange')

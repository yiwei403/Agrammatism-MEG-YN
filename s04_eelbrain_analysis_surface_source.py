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

# surface source analysis with fixed orientation did not seem to capture much brian activation
# probably due to individual differences in brain anatomy. 

inv_info = 'fixed-3-MNE-0'
megData.set_inv(ori=re.split('-',inv_info)[0], 
                snr=int(re.split('-',inv_info)[1]), 
                method=re.split('-',inv_info)[2], 
                depth=int(re.split('-',inv_info)[3]), 
                pick_normal=False)
sessions = ['picturefirst']
# sessions = ['iconfirst', 'picturefirst']
masks = ['lateral']
tstart = -1
tstop = 0.4
r_thresh = 0.8
d_thresh = 0.02
color_list = ['#56B4E9', '#9400D3']
category = 'wordType'
group = 'MFA_data_available'

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
# -

# ### one sample t-tests (defined in s01_eelbrain_pipelineSetup.py) 

# +
# # conditions = ['nounControl']
# conditions = ['nounControl', 'nounNaming', 'nounPlural', 'nounPhrase',
#              'verbControl', 'verbNaming']

# for session in sessions: 
#     for condition in conditions:
#         for mask in masks:
            
#             color_dict = {}
#             legend_dict = {}    
#             word_type = condition_abbrev_dict[condition]['abbrev']
#             color_dict[word_type]=color_list[0]
#             legend_dict[condition]=color_list[0]
                
#             megData.set(raw='ica-'+session, epoch=condition+'_'+session, rej='')
#             erp_stc_all_wordType = megData.load_evoked_stc(
#                 subjects=group, 
#                 baseline=False, 
#                 mask=mask, 
#                 cov='emptyroom', 
#                 model='wordType')
                
#             data = erp_stc_all_wordType.sub(f"(wordType == '{word_type}')")

#             res = megData.load_test('=0', tstart, tstop,
#                                     pmin='tfce', data='source', match='subject', 
#                                     baseline=False, make=True, cov='emptyroom', mask=mask)
#             print(session + ': ' + condition + '\n' + str(res.find_clusters()))
#             # p = plot_source_time_result(res, data, colors = color_dict, legend_colors = legend_dict, d_min=d_thresh, r_min=r_thresh, category=category)
#             # display(p)
# -

# ### paired t-tests (defined in s01_eelbrain_pipelineSetup.py)

# +
contrasts = ['nounNaming-nounControl', 
             'nounPlural-nounNaming', 'nounPhrase-nounNaming',
             'verbNaming-verbControl', 'verbInflectPast-verbInflectFuture',
             'verbInflectPast-verbNaming', 'verbInflectFuture-verbNaming']

# contrasts = ['verbInflectPast-verbNaming']
# contrasts = ['nounNaming-nounControl', 'nounPlural-nounControl', 'nounPhrase-nounControl',
#              'nounPlural-nounNaming', 'nounPhrase-nounNaming',
#              'verbNaming-verbControl', 'verbInflectPast-verbInflectFuture',
#              'verbInflectPast-verbControl', 'verbInflectFuture-verbControl',
#              'verbInflectPast-verbNaming', 'verbInflectFuture-verbNaming']

for session in sessions: 
            
    megData.set(raw='ica-'+session, epoch='speak_'+session, rej='')
    erp_stc_all_wordType = megData.load_evoked_stc(
        subjects=group, 
        baseline=False, 
        mask=mask, 
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

        res = megData.load_test(contrast, tstart, tstop, 
                                pmin='tfce', data='source', match='subject', 
                                baseline=False, make=True, cov='emptyroom', mask=mask)
        p = plot_source_time_result(res, data, colors = color_dict, legend_colors = legend_dict, d_min=d_thresh, r_min=r_thresh, category=category)
        print(session + ': ' + contrast + '\n' + str(res.find_clusters()))
        display(p)
# -

# ### other one sample t-tests and paired t-tests 
#

for session in sessions: 
    for mask in masks:
        megData.set(raw='ica-'+session, epoch='trial_'+session, rej='')
        
        res_cache_dir = os.makedirs(os.path.join(data_path + '/yi-test/' + 'ica-' + session + ' emptyroom ' + inv_info + ' ' + group + '/'), exist_ok=True)
        res_cache_dir = os.path.join(data_path + '/yi-test/' + 'ica-' + session + ' emptyroom ' + inv_info + ' ' + group + '/')
        res_cache_file = (' nobl tfce '+ str(tstart) + '-' + str(tstop) + ' ' + mask)

        erp_stc_all_wordType = megData.load_evoked_stc(
            subjects=group, 
            baseline=False, 
            mask=mask, 
            cov='emptyroom', 
            model='wordType')
        
        nouncontrol_erp_stc = erp_stc_all_wordType.sub("wordType=='nouncontrol'")
        nounnaming_erp_stc = erp_stc_all_wordType.sub("wordType=='nounnm'")
        nounplural_erp_stc = erp_stc_all_wordType.sub("wordType=='nounpp'") 
        nounphrase_erp_stc = erp_stc_all_wordType.sub("wordType=='nounpc'")
        verbnaming_erp_stc = erp_stc_all_wordType.sub("wordType=='verbnm'")
        verbcontrol_erp_stc = erp_stc_all_wordType.sub("wordType=='verbcontrol'")
        
        # combining verb inflection past and future conditions
        verbinflect_erp_stc = erp_stc_all_wordType.sub("(wordType=='infpst')|(wordType=='inffut')")
        verbinflect_erp_stc = verbinflect_erp_stc.aggregate('subject', drop='wordType')
        verbinflect_erp_stc['wordType']=Factor(['verbinflect'] * len(verbinflect_erp_stc['subject']))

        verbinflect_verbcontrol_ds = combine([verbinflect_erp_stc, verbcontrol_erp_stc])
        verbinflect_verbnaming_ds = combine([verbinflect_erp_stc, verbnaming_erp_stc])

        diff_verbnaming_verbcontrol = table.difference(
            'srcm', 
            'wordType', 
            'verbnm', 
            'verbcontrol', 
            'subject',
            data=erp_stc_all_wordType)
        diff_verbnaming_verbcontrol['wordType']=Factor(['verb(naming-control)'] * len(diff_verbnaming_verbcontrol['subject']))
        
        
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


        # # #################### one sample t-test
        
        # contrast = 'verbInflect=0'
        # color_dict = {'verbinflect':color_list[0]}
        # legend_dict = {'verbInflect':color_list[0]}
        # data = verbinflect_erp_stc
        # if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
        #     res = load.unpickle(res_cache_dir + contrast + res_cache_file)
        # else: 
        #     res = testnd.TTestOneSample(verbinflect_erp_stc['srcm'],
        #                             tfce=True, tstart=tstart, tstop=tstop)
        #     save.pickle(res, res_cache_dir + contrast + res_cache_file)
        # print(session + ': ' + contrast + '\n' + str(res.find_clusters()))
        # # # p = plot_source_time_result(res, data, colors = color_dict, legend_colors = legend_dict, d_min=d_thresh, r_min=r_thresh, category=category)
        # # # display(p)
        
        
        ################### paired t-test
        
        contrast = 'verbInflect-verbControl'
        data = combine([verbinflect_erp_stc, verbcontrol_erp_stc], incomplete='drop')
        color_dict = {'verbinflect':color_list[0], 'verbcontrol':color_list[1]}
        legend_dict = {'verbInflect':color_list[0], 'verbControl':color_list[1]}
        if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
            res = load.unpickle(res_cache_dir + contrast + res_cache_file)
        else: 
            res = testnd.TTestRelated(verbinflect_erp_stc['srcm'], verbcontrol_erp_stc['srcm'],  
                                    tfce=True, tstart=tstart, tstop=tstop)
            save.pickle(res, res_cache_dir + contrast + res_cache_file)
        print(session + ': ' + contrast + '\n' + str(res.find_clusters()))
        p = plot_source_time_result(res, data, colors = color_dict, legend_colors = legend_dict, d_min=d_thresh, r_min=r_thresh, category=category)
        display(p)
        
        
        
        contrast = 'verbInflect-verbNaming'
        data = combine([verbinflect_erp_stc, verbnaming_erp_stc], incomplete='drop')
        color_dict = {'verbinflect':color_list[0], 'verbnm':color_list[1]}
        legend_dict = {'verbInflect':color_list[0], 'verbNaming':color_list[1]}
        if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
            res = load.unpickle(res_cache_dir + contrast + res_cache_file)
        else:
            res = testnd.TTestRelated(verbinflect_erp_stc['srcm'], verbnaming_erp_stc['srcm'], 
                                    tfce=True, tstart=tstart, tstop=tstop)
            save.pickle(res, res_cache_dir + contrast + res_cache_file)
        print(session + ': ' + contrast + '\n' + str(res.find_clusters()))
        p = plot_source_time_result(res, data, colors = color_dict, legend_colors = legend_dict, d_min=d_thresh, r_min=r_thresh, category=category)
        display(p)
        
        

        contrast = 'verbNaming-verbControl_nounNaming-nounControl'
        data = combine([diff_verbnaming_verbcontrol, diff_nounnaming_nouncontrol], incomplete='drop')
        color_dict = {'verb(naming-control)':color_list[0], 'noun(naming-control)':color_list[1]}
        legend_dict = color_dict
        if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
            res = load.unpickle(res_cache_dir + contrast + res_cache_file)
        else:
            res = testnd.TTestRelated(diff_verbnaming_verbcontrol['srcm'], diff_nounnaming_nouncontrol['srcm'], 
                                    tfce=True, tstart=tstart, tstop=tstop)
            save.pickle(res, res_cache_dir + contrast + res_cache_file)
        print(session + ': ' + contrast + '\n' + str(res.find_clusters()))
        p = plot_source_time_result(res, data, colors = color_dict, legend_colors = legend_dict, d_min=d_thresh, r_min=r_thresh, category=category)
        display(p)
        

        
        contrast = 'verbInflect-verbControl_nounPlural-nounControl'
        data = combine([diff_verbinflect_verbcontrol, diff_nounplural_nouncontrol], incomplete='drop')
        color_dict = {'verb(inflect-control)':color_list[0], 'noun(plural-control)':color_list[1]}
        legend_dict = color_dict
        if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
            res = load.unpickle(res_cache_dir + contrast + res_cache_file)
        else:
            res = testnd.TTestRelated(diff_verbinflect_verbcontrol['srcm'], diff_nounplural_nouncontrol['srcm'], 
                                    tfce=True, tstart=tstart, tstop=tstop)
            save.pickle(res, res_cache_dir + contrast + res_cache_file)
        print(session + ': ' + contrast + '\n' + str(res.find_clusters()))
        p = plot_source_time_result(res, data, colors = color_dict, legend_colors = legend_dict, d_min=d_thresh, r_min=r_thresh, category=category)
        display(p)
        
        
        
        contrast = 'verbInflect-verbNaming_nounPlural-nounNaming'
        data = combine([diff_verbinflect_verbnaming, diff_nounplural_nounnaming], incomplete='drop')
        color_dict = {'verb(inflect-naming)':color_list[0], 'noun(plural-naming)':color_list[1]}
        legend_dict = color_dict
        if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
            res = load.unpickle(res_cache_dir + contrast + res_cache_file)
        else:
            res = testnd.TTestRelated(diff_verbinflect_verbnaming['srcm'], diff_nounplural_nounnaming['srcm'], 
                                    tfce=True, tstart=tstart, tstop=tstop)
            save.pickle(res, res_cache_dir + contrast + res_cache_file)
        print(session + ': ' + contrast + '\n' + str(res.find_clusters()))
        p = plot_source_time_result(res, data, colors = color_dict, legend_colors = legend_dict, d_min=d_thresh, r_min=r_thresh, category=category)
        display(p)
        
        
        
        contrast = 'verbInflect-verbControl_nounPhrase-nounControl'
        data = combine([diff_verbinflect_verbcontrol, diff_nounphrase_nouncontrol], incomplete='drop')
        color_dict = {'verb(inflect-control)':color_list[0], 'noun(phrase-control)':color_list[1]}
        legend_dict = color_dict
        if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
            res = load.unpickle(res_cache_dir + contrast + res_cache_file)
        else: 
            res = testnd.TTestRelated(diff_verbinflect_verbcontrol['srcm'], diff_nounphrase_nouncontrol['srcm'], 
                                    tfce=True, tstart=tstart, tstop=tstop)
            save.pickle(res, res_cache_dir + contrast + res_cache_file)
        print(session + ': ' + contrast + '\n' + str(res.find_clusters()))
        p = plot_source_time_result(res, data, colors = color_dict, legend_colors = legend_dict, d_min=d_thresh, r_min=r_thresh, category=category)
        display(p)
        
        
        
        contrast = 'verbInflect-verbNaming_nounPhrase-nounNaming' 
        data = combine([diff_verbinflect_verbnaming, diff_nounphrase_nounnaming], incomplete='drop')
        color_dict = {'verb(inflect-naming)':color_list[0], 'noun(phrase-naming)':color_list[1]}
        legend_dict = color_dict
        if glob.glob(os.path.join(res_cache_dir + contrast + res_cache_file + '*')):
            res = load.unpickle(res_cache_dir + contrast + res_cache_file)
        else:
            res = testnd.TTestRelated(diff_verbinflect_verbnaming['srcm'], diff_nounphrase_nounnaming['srcm'], 
                                    tfce=True, tstart=tstart, tstop=tstop)
            save.pickle(res, res_cache_dir + contrast + res_cache_file)
        print(session + ': ' + contrast + '\n' + str(res.find_clusters()))
        p = plot_source_time_result(res, data, colors = color_dict, legend_colors = legend_dict, d_min=d_thresh, r_min=r_thresh, category=category)
        display(p)

# ### compare epochs across sessions

# +
# # This is a comparison I was trying, but didn't end up using. The idea is to compare the epoch from different sessions.
# # for example, difference between icon epoch from iconfirst trial and from picture first trial (icon epoch difference between conditions) is calculated for noun plural and noun naming conditions, respectively
# # then the icon epoch difference between conditions is compared between noun plural and noun naming conditions. 
# # The same analysis is then applied to picture epoch.
# # This analysis assumes that icon/picture epoch difference between conditions gets rid of processes elicited by icon/picture image (such as low level visual processing)
# # However, I'm not sure if the results make sense or not... 

mask = masks[0]
epochs = ['icon', 'picture']
sessions = ['iconfirst', 'picturefirst']

results = {}

for epoch in epochs:
    for session in sessions:
        raw_type = f'ica-{session}'
        epoch_type = f'{epoch}_{session}_long'

        stc_variable_name = f'stc_all_wordType_{epoch}_{session}'
        
        megData.set(raw=raw_type, epoch=epoch_type, rej='')
        
        results[stc_variable_name] = megData.load_evoked_stc(
            subjects=group, 
            baseline=False, 
            mask=mask, 
            cov='emptyroom', 
            model='wordType')


icon_epochs_all_sessions = combine([results['stc_all_wordType_icon_iconfirst'], results['stc_all_wordType_icon_picturefirst']])
picture_epochs_all_sessions = combine([results['stc_all_wordType_picture_iconfirst'], results['stc_all_wordType_picture_picturefirst']])

contrasts = ['nounNaming-nounControl', 'nounPlural-nounControl', 'nounPhrase-nounControl',
             'nounPlural-nounNaming', 'nounPhrase-nounNaming',
             'verbNaming-verbControl', 'verbInflectPast-verbInflectFuture',
             'verbInflectPast-verbControl', 'verbInflectFuture-verbControl',
             'verbInflectPast-verbNaming', 'verbInflectFuture-verbNaming']
# contrasts = ['verbInflectFuture-verbNaming']

res_cache_dir = os.makedirs(os.path.join(data_path + '/yi-test/' + 'emptyroom ' + inv_info + ' ' + group + '/'), exist_ok=True)
res_cache_dir = os.path.join(data_path + '/yi-test/' + 'emptyroom ' + inv_info + ' ' + group + '/')
res_cache_file = (' nobl tfce ' + mask)

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

    icon_epoch_type = 'icon epoch long '
    
    diff_icon_epoch_wordType1 = table.difference(
        'srcm', 
        'session',
        'iconfirst',
        'picturefirst',
        'subject',
        data=icon_epochs_all_sessions.sub(f"wordType=='{word_type_1}'"))

    diff_icon_epoch_wordType2 = table.difference(
        'srcm', 
        'session',
        'iconfirst',
        'picturefirst',
        'subject',
        data=icon_epochs_all_sessions.sub(f"wordType=='{word_type_2}'"))

    if glob.glob(os.path.join(res_cache_dir + icon_epoch_type + contrast + res_cache_file + '*')):
        res_icon_epoch = load.unpickle(res_cache_dir + icon_epoch_type + contrast + res_cache_file)
    else:
        res_icon_epoch = testnd.TTestRelated(diff_icon_epoch_wordType1['srcm'], diff_icon_epoch_wordType2['srcm'], tstart=0, tstop=0.4, tfce=True)
        save.pickle(res_icon_epoch, res_cache_dir + icon_epoch_type + contrast + res_cache_file)

    print('icon epoch ' + contrast + ': ' + '\n' + str(res_icon_epoch.find_clusters()))
    
    data = combine([diff_icon_epoch_wordType1, diff_icon_epoch_wordType2], incomplete='drop')
    p = plot_source_time_result(res_icon_epoch, data, colors = color_dict, legend_colors = legend_dict, 
                                d_min=d_thresh, r_min=r_thresh, category=category, 
                                title=f'{contrast}, {icon_epoch_type}')
    display(p)

    picture_epoch_type = 'picture epoch long '

    diff_picture_epoch_wordType1 = table.difference(
        'srcm', 
        'session',
        'iconfirst',
        'picturefirst',
        'subject',
        data=picture_epochs_all_sessions.sub(f"wordType=='{word_type_1}'"))

    diff_picture_epoch_wordType2 = table.difference(
        'srcm', 
        'session',
        'iconfirst',
        'picturefirst',
        'subject',
        data=picture_epochs_all_sessions.sub(f"wordType=='{word_type_2}'"))

    if glob.glob(os.path.join(res_cache_dir + picture_epoch_type + contrast + res_cache_file + '*')):
        res_picture_epoch = load.unpickle(res_cache_dir + picture_epoch_type + contrast + res_cache_file)
    else: 
        res_picture_epoch = testnd.TTestRelated(diff_picture_epoch_wordType1['srcm'], diff_picture_epoch_wordType2['srcm'], tstart=0, tstop=0.4, tfce=True)
        save.pickle(res_picture_epoch, res_cache_dir + picture_epoch_type + contrast + res_cache_file)

    print('picture epoch ' + contrast + ': ' + '\n' + str(res_picture_epoch.find_clusters()))
    
    data = combine([diff_picture_epoch_wordType1, diff_picture_epoch_wordType2], incomplete='drop')
    p = plot_source_time_result(res_picture_epoch, data, colors = color_dict, legend_colors = legend_dict, 
                                d_min=d_thresh, r_min=r_thresh, category=category, 
                                title=f'{contrast}, {picture_epoch_type}')
    display(p)
    

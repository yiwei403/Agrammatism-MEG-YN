# %%
import runpy
runpy.run_path('/Users/yiwei/Dropbox/agrammatism/code/s01_eelbrain_pipelineSetup.py')
from s01_eelbrain_pipelineSetup import *
import mne
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import sys

megData.set_inv(ori='fixed', snr=3, method='MNE', depth=0, pick_normal=False)
fig_h = 4
fig_w = 8
# subjects = ['R3141']
subjects = megData.get_field_values('subject')
sessions = ['iconfirst', 'picturefirst']

# %% plotting individual RMS/ERF data before and after ICA
# for subject in subjects:
#     for session in sessions:
        
#         t = fmtxt.Table('ll')

#         megData.set(raw='1-40', epoch = 'trial_'+session, subject=subject, session=session)
#         # megData.make_epoch_selection(auto=10e-12, overwrite=True)
#         erf_ds = megData.load_epochs()
#         erf = erf_ds['meg']
#         erf_ds['MEG'] = erf.rms('sensor')
#         t.cell(plot.UTSStat('MEG','wordType', data=erf_ds, h=fig_h, w=fig_w, title = subject+'_'+session+'_preICA_RMS'))
        
#         megData.set(raw='1-40', epoch = 'trial_'+session, subject=subject, session=session)
#         # megData.make_epoch_selection(auto=10e-12, overwrite=True)
#         erf_ds = megData.load_epochs()
#         erf = erf_ds['meg']
#         erf_ds['MEG'] = erf.mean('sensor')
#         t.cell(plot.UTSStat('MEG','wordType', data=erf_ds, h=fig_h, w=fig_w, title = subject+'_'+session+'_preICA_ERF'))
        
#         megData.set(raw='ica-'+session, epoch = 'trial_'+session, subject=subject, session=session)
#         # megData.make_epoch_selection(auto=10e-12, overwrite=True)
#         erf_ds = megData.load_epochs()
#         erf = erf_ds['meg']
#         erf_ds['MEG'] = erf.rms('sensor')
#         t.cell(plot.UTSStat('MEG','wordType', data=erf_ds, h=fig_h, w=fig_w, title = subject+'_'+session+'_postICA_RMS'))

#         megData.set(raw='ica-'+session, epoch = 'trial_'+session, subject=subject, session=session)
#         # megData.make_epoch_selection(auto=10e-12, overwrite=True)
#         erf_ds = megData.load_epochs()
#         erf = erf_ds['meg']
#         erf_ds['MEG'] = erf.mean('sensor')
#         t.cell(plot.UTSStat('MEG','wordType', data=erf_ds, h=fig_h, w=fig_w, title = subject+'_'+session+'_postICA_ERF'))
        
#         emgEpochs = mne.read_epochs(data_path + '/meg/' + subject + '/' + subject + '_' + session + '_emg-epo.fif')
#         emgEpochs.filter(0.5, 10, picks = 'emg')
#         p = emgEpochs.plot_image(picks = 1, show=False)
#         t.cell(p)
        
#         display(t)

# %% plotting group RMS/ERF data in source space.
masks = ['occipital-lateral', 'parietal-lateral', 'temporal-lateral', 'frontal-lateral']
             
for session in sessions: 
    t = fmtxt.Table('ll')
    megData.set(raw='ica-'+session, epoch='trial_'+session, rej='')
    for mask in masks:

        # plotting group RMS/ERF data for good sessions only
        evoked_source_all_wordType_ds = megData.load_evoked_stc('all', baseline=False, mask=mask, cov='emptyroom', model='wordType')
        sourceERP_wordType = evoked_source_all_wordType_ds['srcm']
        evoked_source_all_wordType_ds['RMS'] = sourceERP_wordType.rms('source')
        evoked_source_all_wordType_ds['ERF'] = sourceERP_wordType.mean('source')

        p1 = plot.UTSStat('RMS', 'wordType', data=evoked_source_all_wordType_ds, h=fig_h, w=fig_w, title=mask+' RMS by wordtype all subjects '+session)
        p2 = plot.UTSStat('ERF', 'wordType', data=evoked_source_all_wordType_ds, h=fig_h, w=fig_w, title=mask+' ERF by wordtype all subjects '+session)

        t.cell(p1)
        t.cell(p2)
        
    display(t)
# %% plotting individual and group emg data. 

# for session in sessions: 
    
#     t = fmtxt.Table('ll')
    
#     emgEvoked_all = []
#     for subject in megData.get_field_values('subject'):
#         # emg_epoch = load.mne.epochs_ndvar(data_path + '/meg/' + subject + '/' + subject + '_' + session + '_emg-epo.fif')
#         # emg_epoch_ds = sourceERP_wordType_ds
#         # emg_epoch_ds['emg'] = emg_epoch
#         emgEpochs = mne.read_epochs(data_path + '/meg/' + subject + '/' + subject + '_' + session + '_emg-epo.fif')
#         emgEpochs.filter(0.5, 10, picks = 'emg')
#         emgEvoked = emgEpochs.average(picks='emg')
#         emgEvoked_all.append(emgEvoked.get_data())
        
#     emgEvoked_all = np.concatenate(emgEvoked_all)
#     colormap = cm.get_cmap('tab10', len(emgEvoked_all))
    
#     # plot emg' erps
#     plt.figure(figsize=(10, 6))
#     plt.xlabel('Time (s)')
#     plt.title('individual emg ERP '+ session)
#     time = np.linspace(0, emgEvoked_all.shape[1]/1000, emgEvoked_all.shape[1])
#     for i in range(emgEvoked_all.shape[0]):
#         emgEvoked_all[i] = emgEvoked_all[i]/np.max(np.abs(emgEvoked_all[i]))
#         p5 = plt.plot(time, emgEvoked_all[i], label = megData.get_field_values('subject')[i], color = colormap(i))
#         plt.legend()
#     # plt.show()
#     t.cell(plt.show(p5))
    
#     mean = np.mean(emgEvoked_all, axis=0)
#     stderr = np.std(emgEvoked_all, axis=0) / np.sqrt(emgEvoked_all.shape[0])
#     plt.figure(figsize=(10, 6))
#     p6 = plt.plot(time, mean, color='darkblue')
#     plt.fill_between(time, mean - stderr, mean + stderr, color='lightblue', alpha=0.6)
#     plt.xlabel('Time (s)')
#     plt.title('group emg ERP '+ session)
#     # plt.show()    
#     t.cell(plt.show(p6))
   
#     display(t)

# when using load.mne.epochs_ndvar, it only load channel types that are MEG, EEG or EOG, 
# since my emg epochs' channel type is 'emg', I have to load it with mne.read_epochs, and use .getdata() to 
# emg_epoch = load.mne.epochs_ndvar(data_path + '/meg/' + subject + '/' + subject + '_' + session + '_emg-epo.fif')
# %%

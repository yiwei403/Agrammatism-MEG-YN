
import runpy
runpy.run_path('/Users/yiwei/Dropbox/agrammatism/code/s01_eelbrain_pipelineSetup.py')
from s01_eelbrain_pipelineSetup import *
import scipy.io
import scipy.io.wavfile
import glob
import os
import numpy as np
import mne
import matplotlib.pyplot as plt

subject = 'R3212'
session = 'picturefirst'

###### get ICA components source time series data

# in order to get the ICA source time series data, I need to load ICA components as mne-python objects. 
megData.set(raw = 'ica-'+session, subject = subject)
mneICAepochs = megData.load_ica(epoch = 'trial_'+session)

# .get_sources() requires an mne-python epochs object as input, so I need to load the epochs data as mne-python object as well.
# need to specify fs here, otherwise by default it will downsample to fs=200 for mneEpochs
mneEpochs = megData.load_epochs(epoch ='trial_'+session, samplingrate=1000, reject = False, ndvar=False)['epochs']
mneICAsourcesEpochs = mneICAepochs.get_sources(mneEpochs)

# locate the correponding emg .mat file. 
if session == 'iconfirst':
    emgMatFile = glob.glob(os.path.join(os.path.dirname(data_path), "MNC", "raw data", 
                        f'{subject}_*', f'{subject}_IF.mat'))
    emgMatFile = scipy.io.loadmat(emgMatFile[0])
    emgData = emgMatFile['b1']
    
elif session == 'picturefirst' and subject == 'R3160':
    
    emgMatFile_part1 = glob.glob(os.path.join(os.path.dirname(data_path), "MNC", "raw data", 
                        f'{subject}_*', f'{subject}_PF_part1.mat'))
    mat1 = scipy.io.loadmat(emgMatFile_part1[0])
    emgData1 = mat1['b1']
     
    emgMatFile_part2 = glob.glob(os.path.join(os.path.dirname(data_path), "MNC", "raw data", 
                        f'{subject}_*', f'{subject}_PF_part2.mat'))
    mat2 = scipy.io.loadmat(emgMatFile_part2[0])
    emgData2 = mat2['b1']
    
    emgData = np.concatenate((emgData1, emgData2), axis=0)
    
else:
    emgMatFile = glob.glob(os.path.join(os.path.dirname(data_path), "MNC", "raw data", 
                    f'{subject}_*', f'{subject}_PF.mat'))
    emgMatFile = scipy.io.loadmat(emgMatFile[0])
    emgData = emgMatFile['b1']

# load emg data, define fs, and extract the trigger and signal channels. 
emgFs = 1000
emgData = emgData[:, [1,3]]

# finding the sample of the first trigger in the emg data.
emgTrigger_diff = np.diff(emgData[:, 0])
emgTrigger_ind = np.where(np.abs(emgTrigger_diff) > 1)[0]/emgFs
emgTrigger_first_in_sample = np.where(emgTrigger_diff < -1)[0][0]

# then, I remove the duplicate trigger times that are less than 0.02 seconds apart.
emgTriggerTimes = []
current_min = emgTrigger_ind[0]
for i in range(1, len(emgTrigger_ind)):
    if emgTrigger_ind[i] - emgTrigger_ind[i-1] < 0.02:
        current_min = min(current_min, emgTrigger_ind[i])
    else:
        emgTriggerTimes.append(current_min)
        current_min = emgTrigger_ind[i]
emgTriggerTimes.append(current_min)

# now I have the emg trigger time in both seconds and samples. 
emgTriggerTimes = np.array(emgTriggerTimes)
emgTrigger_ind = np.round(emgTriggerTimes * emgFs)

# create an mne events array for the cropped emg data.
emgEvents = np.zeros((len(emgTriggerTimes),3))
emgEvents[:,0] = emgTrigger_ind.astype(int)
emgEvents[:,1] = 0
emgEvents[:,2] = 163

# the 49th trigger 163 is missing from the iconfirst session of R3161 (see findMissingTrigger.py)
if session == 'iconfirst' and subject == 'R3161':
    megEvent_first_in_second = megData.load_events()['T'][0]
    emgMegDiff_in_sample = emgTrigger_first_in_sample - (megEvent_first_in_second * emgFs-1)
    missing_event = [int(megData.load_events()['i_start'][196]) + emgMegDiff_in_sample, 0, 163]
    emgEvents = np.vstack([emgEvents, np.array(missing_event)])
    emgEvents = emgEvents[emgEvents[:,0].argsort()]
    
print(f'{len(emgEvents)} events in {subject}-{session}`s emg recording')

# now I need to create an mne RawArray object for the cropped emg data.
# first, create the info structure needed by MNE
emgDatainfo = mne.create_info(['emg trigger', 'emg signal'], sfreq=emgFs, ch_types=['stim','emg'])
emgDatainfo['description'] = 'emg data'

# then create a RawArray with the data and the info structure
emgRaw = mne.io.RawArray(emgData.T, emgDatainfo)

# filter the emg data the same way as the meg data, and add the events to the raw object.
emgFiltered= emgRaw.filter(1, 40, picks = 'emg')
emgFiltered.add_events(emgEvents, stim_channel='emg trigger')

# create epochs for the emg data.
emg_epochs = mne.Epochs(
    emgFiltered, 
    events = emgEvents.astype(int), 
    tmin = -0.1, 
    tmax = tmaxTrial, 
    baseline=None, 
    preload=True
    )
emg_epochs.save(data_path + '/meg/' + subject + '/' + subject + '_' + session + '_emg-epo.fif', overwrite=True)

# calculate correlations between emg evoked data and ICA source time series evoked data. 
mneICAsourceEvoked = mneICAsourcesEpochs.average(picks = 'all')
emgEvoked = emg_epochs.average(picks = 'emg')

ICAsourceArray = mneICAsourceEvoked.get_data()[:30]
emgEvokedArray = emgEvoked.get_data()[:1]
emgEvokedArray = emgEvokedArray.flatten()
emg_ICA_corr = [np.corrcoef(ICAsourceArray[i], emgEvokedArray)[0,1] for i in range(ICAsourceArray.shape[0])]

ICAindices = np.argsort(-np.abs(emg_ICA_corr))
top10ICAindices = ICAindices[:10]
top10corr_erp = [emg_ICA_corr[i] for i in top10ICAindices]
erp_corr_results = np.column_stack((top10ICAindices, top10corr_erp))

# double check if I have missed any components when I only calculated the correlations between the erps. 
# here I'm checking the correlation between the (unaveraged) epochs of ICA source data and emg data. 
ICAsourceEpochs_dataframe = mneICAsourcesEpochs.to_data_frame()
emgEpochs_dataframe = emg_epochs.to_data_frame()
allR_epochs = ICAsourceEpochs_dataframe.iloc[:, 3:33].apply(lambda x: x.corr(emgEpochs_dataframe.iloc[:, -1]))
top10corr_epochs = allR_epochs.abs().nlargest(10)

print(f"Subject: {subject}, Session: {session}, \nERP corr: \n{erp_corr_results}, \nepochs corr: \n{top10corr_epochs}")

# %% ###### look at some plots to decide which ICA is most likely emg related. 

# # plot the erps. For ICA source erp plots, my criteria is to plot all the ICA components that has a erp corr > 0.3, and epochs corr > 0.01
# # # In the actual ICA selection process, I found that erp corr > 0.4 and/or epochs corr > 0.02 is a pretty good criteria. 


# emg_epochs.plot_image(picks=1)

# mneICAsourcesEpochs.plot_image(picks=13)
# mneICAsourcesEpochs.plot_image(picks=28)
# mneICAsourcesEpochs.plot_image(picks=19)
# mneICAsourcesEpochs.plot_image(picks=21)
# mneICAsourcesEpochs.plot_image(picks=6)
# mneICAsourcesEpochs.plot_image(picks=24)
# mneICAsourcesEpochs.plot_image(picks=10)
# mneICAsourcesEpochs.plot_image(picks=12)
# mneICAsourcesEpochs.plot_image(picks=20)
# mneICAsourcesEpochs.plot_image(picks=22)
# mneICAsourcesEpochs.plot_image(picks=3)
# mneICAsourcesEpochs.plot_image(picks=0)
# mneICAsourcesEpochs.plot_image(picks=2)
# mneICAsourcesEpochs.plot_image(picks=7)
# mneICAsourcesEpochs.plot_image(picks=1)
# mneICAsourcesEpochs.plot_image(picks=5)

# # # if I'm not sure about certain ICA components, I plot all the epochs from that component(s) (defined by picks) and emg epochs together

# mne.viz.plot_ica_sources(mneICAepochs, mneEpochs, picks=[14])
# emg_epochs.plot(
#     picks = 'emg',
#     scalings={'emg': 1},
#     events = emgEvents.astype(int),
#     event_color = {163: 'red'}
#     )
# plt.show()

# %% trying out the EOGRegression mne method to regress out the speech artifact from the meg signal using the emg channel. 
# does not seem to work :(
    
# from mne.preprocessing import EOGRegression
# # Perform regression using the EOG sensor as independent variable and the EEG
# # sensors as dependent variables.
# epochs = mne.Epochs(megData_mne_filtered, all_events, event_id=163, preload=True)

# model_plain = EOGRegression(picks="meg", picks_artifact="emg").fit(epochs)
# fig = model_plain.plot(vlim=(None, 1))  # regression coefficients as topomap
# fig.set_size_inches(6, 4)
# epochs_clean_plain = model_plain.apply(epochs)

# epochs.average('all').plot()
# epochs_clean_plain.average('all').plot()

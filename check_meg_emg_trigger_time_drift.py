
# %%
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

subjects = megData.get_field_values('subject')
sessions = ['iconfirst', 'picturefirst']

# subject = 'R3145'
# session = 'picturefirst'

# %%

for subject in subjects:
    for session in sessions:
        megData.set(raw = 'ica-'+session, subject = subject)
        
        # getting the first event sample and the length of the meg data.
        megData_length_in_sample = len(megData.load_raw(session = session, subject = subject))
        megEvent_first_in_second = megData.load_events()['T'][0]

        ###### import emg data and crop the data to the same duration as the MEG data. 
        # I'm cropping emg data because i want to make sure there no time drift between the triggers in emg and in MEG.
        # Turned out that the time drift is a couple of samples over a 40 minutes recording, which is acceptable.
        # Therefore, cropping emg data is not necessary.
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
        
        # crop the emg data to start and end at the same length as the meg data.
        emgMegDiff_in_sample = emgTrigger_first_in_sample - (megEvent_first_in_second * emgFs - 1)
        print(f'{subject}-{session}: emg preceeds meg recording start time by {emgMegDiff_in_sample} samples')
        
        if subject != 'R3160':
        # crop the emg data to start and end at the same length as the meg data.
            # for most of the participants, the emg recording is longer than the meg recording
            # but for R3131 picture frist, and R3133 picture first, the emg recording is shorter than the meg recording
            # this code accounts for both senarios
            if emgMegDiff_in_sample < 0:
                emgDataCropped = emgData[0:megData_length_in_sample, :]
            else:
                emgDataCropped = emgData[emgMegDiff_in_sample.astype(int) : emgMegDiff_in_sample.astype(int) + megData_length_in_sample, :]
            # since the emg data is cropped, I need to re-calculate the trigger times.
            # first, I calculate the derivative of the trigger channel, and find the indices where the absolute value of the derivatives is greater than 1.
            croppedEmgTrigger_diff = np.diff(emgDataCropped[:, 0])
            croppedEmgTrigger_ind = np.where(np.abs(croppedEmgTrigger_diff) > 1)[0]/emgFs
        else: 
            emgDataCropped = emgData
            croppedEmgTrigger_ind = emgTrigger_ind

        # then, I remove the duplicate trigger times that are less than 0.02 seconds apart.
        croppedEmgTriggerTimes = []
        current_min = croppedEmgTrigger_ind[0]
        for i in range(1, len(croppedEmgTrigger_ind)):
            if croppedEmgTrigger_ind[i] - croppedEmgTrigger_ind[i-1] < 0.02:
                current_min = min(current_min, croppedEmgTrigger_ind[i])
            else:
                croppedEmgTriggerTimes.append(current_min)
                current_min = croppedEmgTrigger_ind[i]
        croppedEmgTriggerTimes.append(current_min)

        # now I have the emg trigger time in both seconds and samples. 
        croppedEmgTriggerTimes = np.array(croppedEmgTriggerTimes)
        croppedEmgTriggerInds = np.round(croppedEmgTriggerTimes * emgFs)

        # create an mne events array for the cropped emg data.
        emgEvents = np.zeros((len(croppedEmgTriggerTimes),3))
        emgEvents[:,0] = croppedEmgTriggerInds.astype(int)
        emgEvents[:,1] = 0
        emgEvents[:,2] = 163

        # the 49th trigger 163 is missing from the iconfirst session of R3161 (see findMissingTrigger.py)
        if session == 'iconfirst' and subject == 'R3161':
            missing_event = [int(megData.load_events()['i_start'][196]), 0, 163]
            emgEvents = np.vstack([emgEvents, np.array(missing_event)])
            emgEvents = emgEvents[emgEvents[:,0].argsort()]
        
        # I need to check if there are missing trials for the emg recordings 
        print(f'{len(emgEvents)} events in {subject}-{session}`s emg recording')

        # now I need to create an mne RawArray object for the cropped emg data.
        # first, create the info structure needed by MNE
        emgDatainfo = mne.create_info(['emg trigger', 'emg signal'], sfreq=emgFs, ch_types=['stim','emg'])
        emgDatainfo['description'] = 'emg data'

        # then create a RawArray with the data and the info structure
        emgCroppedRaw = mne.io.RawArray(emgDataCropped.T, emgDatainfo)

        # filter the emg data the same way as the meg data, and add the events to the raw object.
        emgCroppedFiltered= emgCroppedRaw.filter(1, 40, picks = 'emg')
        emgCroppedFiltered.add_events(emgEvents, stim_channel='emg trigger')

        # create epochs for the emg data.
        emg_epochs = mne.Epochs(
            emgCroppedFiltered, 
            events = emgEvents.astype(int), 
            tmin = -0.1, 
            tmax = tmaxTrial, 
            baseline=None, 
            preload=True
            )

        ###### some plots to visulize MEG and EMG data. 

        # # plot only the cropped filtered emg data with the events.
        # emgCroppedFiltered.plot(
        #     events = emgEvents,
        #     event_color = {163: 'red'},
        #     scalings={'emg': 2}, 
        #     )
        # plt.show()    

        # # plot filtered meg and emg data together (raw data). I use this plot to check trigger timing drift between emg and meg signal. 
        # megData_mne_filtered = megData.load_raw('1-40')
        # megData_mne_filtered.add_channels([emgCroppedFiltered], force_update_info=True)
        # megData_mne_filtered.pick_types(meg=True, misc=False, emg=True, stim=True)
        # all_events = mne.find_events(megData_mne_filtered, stim_channel="STI 014")
        # megData_mne_filtered.plot(
        #     events=all_events,
        #     start=30,
        #     duration=60,
        #     color="gray",
        #     event_color={163: "r", 169: "g", 167: "b", 171: "m"},
        #     scalings={"stim": 1, "emg": 1}
        # )
        # plt.show()

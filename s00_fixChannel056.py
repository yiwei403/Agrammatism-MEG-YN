# %% run this script right after kit2fiff conversion

import os
import numpy as np
import mne

data_path = '/Users/yiwei/Documents/agrammatism/MEGstudy'

loc = np.array([
    0.09603   , -0.07437   ,  0.00905   , -0.5447052 , -0.83848277,
    0.01558496,  0.        , -0.01858388, -0.9998273 ,  0.8386276 ,
    -0.54461113,  0.01012274])

sessions = ['iconfirst', 'picturefirst', 'emptyroom']
subjects = ['R3200', 'R3204', 'R3205', 'R3206', 'R3209', 'R3210', 'R3211', 'R3212']

for subject in subjects:
    subject_folder = data_path + '/meg/' + subject

    for session in sessions:
        rawfile = subject + '_' + session + '-raw.fif'
        rawfile_path = os.path.join(subject_folder, rawfile)
        raw = mne.io.read_raw_fif(rawfile_path, preload = True)
        index = raw.ch_names.index('MEG 056')
        raw.info['chs'][index]['loc'] = loc
        raw.save(rawfile_path, overwrite=True)

from eelbrain import *
from eelbrain.pipeline import *
from PictureFirstTrialOrder import picturefirst_trialOrder
from PictureFirstWordTypeOrder import picturefirst_wordTypeOrder
import pandas as pd
import os
import numpy as np
import mne
# import matplotlib.pyplot as plt


# this is the version for HSP2025 poster results

# the designed stimulus persentation time is 
# 1000ms for the 1st fixation cross, 
# 400ms for the 1st icon/picture,
# 400ms for the 2nd fixation cross,
# 400ms for the 2nd icon/picture,
# However, due to screen refresh rate, the actual stimulus presentation time is 
# 1012ms for the 1st fixation cross, 
# 415ms for the 1st icon/picture,
# 415ms for the 2nd fixation cross,
# 415ms for the 2nd icon/picture.
# therefore, the tmaxTrial is set to the total stimuli presentation time + 2 seconds after the onset of the speak cue image. 
tmaxTrial = (1000+12+400+15+400+15+400+15+2000)/1000

            
for i, item in enumerate(picturefirst_trialOrder):
    if item == "contrl":
        if picturefirst_wordTypeOrder[i].startswith("obj"):
            picturefirst_trialOrder[i] = "nouncontrol"
        elif picturefirst_wordTypeOrder[i].startswith("act"):
            picturefirst_trialOrder[i] = "verbcontrol"


subjects_dir = '/Users/yiwei/Documents/agrammatism7.3/MEGstudy/mri/'

aparc_a2009s_labels = mne.read_labels_from_annot(
    "fsaverage", 
    'aparc.a2009s',
    subjects_dir=subjects_dir
    )

temporal_label_lh = [
    label for label in aparc_a2009s_labels if label.name in [
        'G_temp_sup-Lateral-lh',
        'G_temporal_middle-lh',
        'S_temporal_sup-lh', 
        ]]
temporal_region_lh = temporal_label_lh[0]+temporal_label_lh[1]+temporal_label_lh[2]
split_labels_lh = mne.split_label(temporal_region_lh, parts=5, subjects_dir=subjects_dir)

PTL_lh = split_labels_lh[0]+split_labels_lh[1]+split_labels_lh[2]
ATL_lh = split_labels_lh[3]+split_labels_lh[4]

temporal_label_rh = [
    label for label in aparc_a2009s_labels if label.name in [
        'G_temp_sup-Lateral-rh',
        'G_temporal_middle-rh',
        'S_temporal_sup-rh', 
        ]]
temporal_region_rh = temporal_label_rh[0]+temporal_label_rh[1]+temporal_label_rh[2]
split_labels_rh = mne.split_label(temporal_region_rh, parts=5, subjects_dir=subjects_dir)

PTL_rh = split_labels_rh[0]+split_labels_rh[1]+split_labels_rh[2]
ATL_rh = split_labels_rh[3]+split_labels_rh[4]

syntax_cortical_label_lh = [
    label for label in aparc_a2009s_labels if label.name in [
        # 'G_front_middle-lh',
        'G_precentral-lh',
        'G_front_inf-Orbital-lh',
        'G_front_inf-Opercular-lh',
        'G_front_inf-Triangul-lh',
        'G_pariet_inf-Angular-lh',
        'G_pariet_inf-Supramar-lh',
        'G_temp_sup-Lateral-lh',
        'G_temporal_middle-lh',
        ]]

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


class agrammatismMEG(MneExperiment): 
    
    sessions = ['picturefirst', 'emptyroom']
    
    groups = {
    'right_hand': SubGroup('all', ['R3135', 'R3205', 'R3210']),
    'left_hand': Group(['R3135', 'R3205', 'R3210']),
    }   
    
    
    raw = {
        'tsss': RawMaxwell('raw', st_duration=10., ignore_ref=True, st_correlation=0.9, st_only=True, cache=False),
        '1-40': RawFilter('tsss', 1, 40, cache=False),
        'ica-picturefirst': RawICA('1-40', 'picturefirst', 'extended-infomax', n_components=0.99),
    }
    
    # adding labels to trigger codes
    # adding a trialindex column to assign a  trial index to every 4 trigger codes which belong to the same trial. 
    variables = {
        'stimulus': LabelVar('trigger', {163: 'fixation', 167: 'picture', 169: 'icon', 171: 'speak'}),
        'trialindex': EvalVar("trigger.as_factor().count()"),
    }
    
    # see R__PF__.xlsx for stimulus per trial. 
    def label_events(self, ds):
        
        # add a verbType column to indicate whether a verb is regular or irregular
        ds['verbType'] = Factor(['']*len(ds['trialindex']), name='verbType')

        if ds.info['session'] == 'picturefirst':
            trial_order = picturefirst_trialOrder
            irregular_verb_trials = [14, 75, 92, 96, 110, 161, 175, 216, 251, 263, 276, 294, 336, 374, 382]
            for i in irregular_verb_trials:
                ds['verbType'][ds['trialindex'] == i-1] = "irregular"
        else: 
            return ds
        
        # add a wordType column to the event structure to specify wordtype of each trial
        # based on the imported trial order file. 
        ds['wordType'] = Factor(trial_order)[ds['trialindex']]
        wordCategories = []
        for i in range(ds.n_cases):
            if ds[i, 'wordType'].startswith('noun'):
                wordCategories.append('noun')
            else:
                wordCategories.append('verb')
        ds['wordCategory'] = Factor(wordCategories)
        ds['verbType'][(ds['wordType'] == 'infpst') & (ds['verbType'] != 'irregular')] = "regular"
        
        # add dummy code              
        ds[:,'syllable'] = 0
        ds['syllable'][(ds['wordType'].isin(['nounnm','nounpp','verbnm']))] = 1
        ds['syllable'][(ds['wordType'].isin(['nounpc','inffut']))] = 3
        ds['syllable'][(ds['wordType']=='infpst')] = 2.1
        ds['syllable'][(ds['wordType'].isin(['nouncontrol','verbcontrol']))] = 2
        
        # add a rt column to record word onset time of each trial using their word onset time .csv file
        production_data_dir = '/Users/yiwei/Dropbox/agrammatism/MEGstudy/speechProductionData_checked/'

        if ds.info['session'] == 'picturefirst':
            session = 'PF'

        csv_file = os.path.join(production_data_dir, f'{ds.info['subject']}_{session}_responseOnsetTime.csv')

        if os.path.exists(csv_file):
            mfa_data = pd.read_csv(csv_file)
            mfa_data.loc[mfa_data['flag']=='flag', 'MFA_sentence_onset'] = mfa_data['edited_onset_time']
            mfa_data = mfa_data.sort_values(by='trial')
            speak_index = ds['stimulus'] == 'speak'
            ds[:, 'rt'] = 0.
            ds[:, 'incorrect'] = 0.
            ds[speak_index, 'rt'] = mfa_data['MFA_sentence_onset']
            ds[speak_index, 'incorrect'] = mfa_data['incorrect']
            rt_var = ds[speak_index, 'rt']
            # # for now, I'm not using trials with MFA < 0.4s (these trials still need to be check by RAs)
            # rt_var[rt_var < 0.4] = np.nan
            # audio wav file are epoched starting 2 seconds from the onset of the first fixation cross (trigger 163),
            # which means the MFA onset time is with respect to 200ms prior to the onset of the speak cue. 
            # if we account for delay caused by the screen refresh rate, 
            # then the MFA onset time is with respect to 257ms prior to the speak icon onset
            ds[speak_index,'rt'] = rt_var-0.257
            ds[:, 'accuracy'] = 'correct'
            incorrect_trials = ds[speak_index, 'rt'].isnan() 
            incorrect_trials = ds[speak_index, 'incorrect'] == 1
            incorrect_trials_indices = ds[speak_index,'trialindex'][incorrect_trials]
            for trial_index in incorrect_trials_indices:
                ds[ds['trialindex'] == trial_index, 'accuracy'] = 'incorrect'

            return ds
        

    
    # tmin = -0.1 by default
    # the SecondaryEpochs are set up for running one sample t test.
    # *_regular refers to epochs with only regular verbs
    # *_irregular refers to epochs with only irregular verbs 
    epochs = {        
        'trial_picturefirst': PrimaryEpoch('picturefirst', "(stimulus == 'fixation') & (accuracy == 'correct')", tmax = tmaxTrial),
        'trial_picturefirst_regular': PrimaryEpoch('picturefirst', "(stimulus == 'fixation') & (verbType!='irregular') & (accuracy == 'correct')", tmax = tmaxTrial),
        'trial_picturefirst_irregular': PrimaryEpoch('picturefirst', "(stimulus == 'fixation') & (verbType!='regular') & (accuracy == 'correct')", tmax = tmaxTrial),

        'speak_picturefirst' : PrimaryEpoch('picturefirst', "(stimulus == 'speak') & (accuracy == 'correct')", trigger_shift = 'rt', tmin = -1, tmax = 1),
        'speak_picturefirst_regular' : PrimaryEpoch('picturefirst', "(stimulus == 'speak') & (accuracy == 'correct') & (verbType!='irregular')", trigger_shift = 'rt', tmin = -1, tmax = 1),
        'speak_picturefirst_irregular' : PrimaryEpoch('picturefirst', "(stimulus == 'speak') & (accuracy == 'correct') & (verbType!='regular')", trigger_shift = 'rt', tmin = -1, tmax = 1),
    }
    
    
data_path = '/Users/yiwei/Documents/agrammatism7.3/MEGstudy'
megData = agrammatismMEG(data_path) 


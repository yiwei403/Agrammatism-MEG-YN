from eelbrain import *
from eelbrain.pipeline import *
from IconFirstTrialOrder import iconfirst_trialOrder
from IconFirstWordTypeOrder import iconfirst_wordTypeOrder
from PictureFirstTrialOrder import picturefirst_trialOrder
from PictureFirstWordTypeOrder import picturefirst_wordTypeOrder
import pandas as pd
import os
import numpy as np

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

# specify whether "control" in the TrialOrder file is nouncontrol or verbcontrol
for i, item in enumerate(iconfirst_trialOrder):
    if item == "contrl":
        if iconfirst_wordTypeOrder[i].startswith("obj"):
            iconfirst_trialOrder[i] = "nouncontrol"
        elif iconfirst_wordTypeOrder[i].startswith("act"):
            iconfirst_trialOrder[i] = "verbcontrol"
            
for i, item in enumerate(picturefirst_trialOrder):
    if item == "contrl":
        if picturefirst_wordTypeOrder[i].startswith("obj"):
            picturefirst_trialOrder[i] = "nouncontrol"
        elif picturefirst_wordTypeOrder[i].startswith("act"):
            picturefirst_trialOrder[i] = "verbcontrol"

LATERAL_OCCIPITAL = ('lateraloccipital', 'pericalcarine', 'lingual')
LATERAL_STG = ('transversetemporal', 'superiortemporal')
LATERAL_TEMPORAL = LATERAL_STG + ('bankssts', 'middletemporal', 'inferiortemporal')
LATERAL_IFG = ('parsopercularis', 'parsorbitalis', 'parstriangularis')
LATERAL_FRONTAL = LATERAL_IFG + ('caudalmiddlefrontal', 'frontalpole', 'precentral', 'rostralmiddlefrontal', 'superiorfrontal')
LATERAL_PARIETAL = ('postcentral', 'inferiorparietal', 'superiorparietal', 'supramarginal')

OTHER_TEMPORAL = ('fusiform', 'temporalpole')
OTHER_MEDIAL = ('cuneus', 'lateralorbitofrontal', 'medialorbitofrontal', 'paracentral', 'precuneus')
MEDIAL_TEMPORAL = ('entorhinal', 'parahippocampal')

BROCA = ('parsopercularis-lh', 'parstriangularis-lh')
WERNICKE = ('superiortemporal-lh', 'supramarginal-lh')

LEFT_STG = ('transversetemporal-lh', 'superiortemporal-lh')
LEFT_TEMPORAL = LEFT_STG + ('bankssts-lh', 'middletemporal-lh', 'inferiortemporal-lh')
LEFT_IFG = ('parsopercularis-lh', 'parsorbitalis-lh', 'parstriangularis-lh')
LEFT_FRONTAL = LEFT_IFG + ('caudalmiddlefrontal-lh', 'frontalpole-lh', 'precentral-lh', 'rostralmiddlefrontal-lh', 'superiorfrontal-lh')
LEFT_IPL = ('inferiorparietal-lh', 'supramarginal-lh')
LEFT_PARIETAL = ('postcentral-lh', 'inferiorparietal-lh', 'superiorparietal-lh', 'supramarginal-lh')

RIGHT_STG = ('transversetemporal-rh', 'superiortemporal-rh')
RIGHT_TEMPORAL = RIGHT_STG + ('bankssts-rh', 'middletemporal-rh', 'inferiortemporal-rh')
RIGHT_IFG = ('parsopercularis-rh', 'parsorbitalis-rh', 'parstriangularis-rh')
RIGHT_FRONTAL = RIGHT_IFG + ('caudalmiddlefrontal-rh', 'frontalpole-rh', 'precentral-rh', 'rostralmiddlefrontal-rh', 'superiorfrontal-rh')
RIGHT_IPL = ('inferiorparietal-rh', 'supramarginal-rh')
RIGHT_PARIETAL = ('postcentral-rh', 'inferiorparietal-rh', 'superiorparietal-rh', 'supramarginal-rh')

# Combinations
LATERAL = LATERAL_TEMPORAL + OTHER_TEMPORAL + LATERAL_FRONTAL + LATERAL_PARIETAL
WHOLEBRAIN = LATERAL_TEMPORAL + OTHER_TEMPORAL + LATERAL_FRONTAL + LATERAL_PARIETAL + OTHER_MEDIAL + LATERAL_OCCIPITAL
FRONTAL_TEMPORAL = LATERAL_TEMPORAL + LATERAL_FRONTAL + OTHER_TEMPORAL
LEFT_FRONTAL_TEMPORAL_PARIETAL = LEFT_FRONTAL + LEFT_TEMPORAL + LEFT_PARIETAL

class agrammatismMEG(MneExperiment): 
    
    sessions = ['iconfirst', 'picturefirst', 'resting', 'emptyroom']
    
    groups = {
    'right_hand': SubGroup('all', ['R3135', 'R3205', 'R3210']),
    'left_hand': Group(['R3135', 'R3205', 'R3210']),
    }   
    
    # Fixing the missing trigger event in R3161 iconfirst session. 
    def fix_events(self, ds):
        if ds.info['subject'] == 'R3161' and ds.info['session'] == 'iconfirst':
            df = ds.as_dataframe()
            trigger_codes = df['trigger']
            ind_169 = []
            for i in range(1, len(trigger_codes)):
                if trigger_codes[i] == 169 and trigger_codes[i-1] != 163:
                    ind_169.append(i)
            timediff_163_169 = df['i_start'][1] - df['i_start'][0]
            missing_i_start = df.iloc[ind_169]['i_start']-timediff_163_169
            missing_trigger = 163
            missing_event = pd.DataFrame({'i_start': missing_i_start, 'trigger': missing_trigger})
            df = pd.concat([df,missing_event], ignore_index=True)
            df = df.sort_values(by='i_start').reset_index(drop=True)
            ds = Dataset.from_dataframe(df)
            return ds
        else:
            return ds
    
    raw = {
        'tsss': RawMaxwell('raw', st_duration=10., ignore_ref=True, st_correlation=0.9, st_only=True),
        '1-40': RawFilter('tsss', 1, 40),
        'ica-iconfirst': RawICA('1-40', 'iconfirst', 'extended-infomax', n_components=0.99),
        'ica-picturefirst': RawICA('1-40', 'picturefirst', 'extended-infomax', n_components=0.99),
    }
    
    # adding labels to trigger codes
    # adding a trialindex column to assign a  trial index to every 4 trigger codes which belong to the same trial. 
    variables = {
        'stimulus': LabelVar('trigger', {163: 'fixation', 167: 'picture', 169: 'icon', 171: 'speak'}),
        'trialindex': EvalVar("trigger.as_factor().count()"),
    }
    
    # for icon first: irregular verbs are: trial: 25, 42, 46, 61, 75, 101, 113, 126, 144, 174, 182, 214, 286, 316, 360
    # for picture first: irregular verbs are: trial: 14, 75, 92, 96, 110, 161, 175, 216, 251, 263, 276, 294, 336, 374, 382
    # see R__IF__.xlsx and R__PF__.xlsx for stimulus per trial. 
    def label_events(self, ds):
        
        # add a verbType column to indicate whether a verb is regular or irregular
        ds['verbType'] = Factor(['']*len(ds['trialindex']), name='verbType')
        if ds.info['session'] == 'iconfirst':
            trial_order = iconfirst_trialOrder
            irregular_verb_trials = [25, 42, 46, 61, 75, 101, 113, 126, 144, 174, 182, 214, 286, 316, 360]
            for i in irregular_verb_trials:
                ds['verbType'][ds['trialindex'] == i-1] = "irregular"
        elif ds.info['session'] == 'picturefirst':
            trial_order = picturefirst_trialOrder
            irregular_verb_trials = [14, 75, 92, 96, 110, 161, 175, 216, 251, 263, 276, 294, 336, 374, 382]
            for i in irregular_verb_trials:
                ds['verbType'][ds['trialindex'] == i-1] = "irregular"
        else: 
            return ds
        
        ds['wordType'] = Factor(trial_order)[ds['trialindex']]
        wordCategories = []
        for i in range(ds.n_cases):
            if ds[i, 'wordType'].startswith('noun'):
                wordCategories.append('noun')
            else:
                wordCategories.append('verb')
        ds['wordCategory'] = Factor(wordCategories)
        ds['verbType'][(ds['wordType'] == 'infpst') & (ds['verbType'] != 'irregular')] = "regular"
        
        # add a rt column to record word onset time of each trial using their word onset time .csv file
        production_data_dir = '/Users/yiwei/Dropbox/agrammatism/MEGstudy/speechProductionData/'
        if ds.info['session'] == 'iconfirst':
            session = 'IF'
        elif ds.info['session'] == 'picturefirst':
            session = 'PF'

        csv_file = os.path.join(production_data_dir, ds.info['subject'], f'{ds.info['subject']}_{session}_responseOnsetTime.csv')
        # print(ds.info['subject'])
        if os.path.exists(csv_file):
            # print(csv_file)
            mfa_data = pd.read_csv(csv_file)
            mfa_data = mfa_data.sort_values(by='trial')
            # print(mfa_data)
            speak_index = ds['stimulus'] == 'speak'
            ds[:, 'rt'] = 0.
            ds[speak_index, 'rt'] = mfa_data['MFA_sentence_onset']
            rt_var = ds[speak_index, 'rt']
            # for now, I'm not using trials with MFA < 0.4s (these trials still need to be check by RAs)
            rt_var[rt_var < 0.4] = np.nan
            # audio wav file are epoched starting 2 seconds from the onset of the first fixation cross (trigger 163),
            # which means the MFA onset time is with respect to 200ms prior to the onset of the speak cue. 
            # if we account for delay caused by the screen refresh rate, 
            # then the MFA onset time is with respect to 257ms prior to the speak icon onset
            ds[speak_index,'rt'] = rt_var-0.257
            ds[:, 'accuracy'] = 'correct'
            incorrect_trials = ds[speak_index, 'rt'].isnan()
            incorrect_trials_indices = ds[speak_index,'trialindex'][incorrect_trials]
            for trial_index in incorrect_trials_indices:
                ds[ds['trialindex'] == trial_index, 'accuracy'] = 'incorrect'
            # print(ds)
            return ds

        return ds

    
    # tmin = -0.1 by default
    # the SecondaryEpochs are set up for running one sample t test.
    # *_regular refers to epochs with only regular verbs
    # *_irregular refers to epochs with only irregular verbs 
    epochs = {        
        'trial_iconfirst': PrimaryEpoch('iconfirst', "stimulus == 'fixation'", tmax = tmaxTrial),
        'trial_iconfirst_regular': PrimaryEpoch('iconfirst', "(stimulus == 'fixation') & (verbType!='irregular')", tmax = tmaxTrial),
        'trial_iconfirst_irregular': PrimaryEpoch('iconfirst', "(stimulus == 'fixation') & (verbType!='regular')", tmax = tmaxTrial),
        # 'nounControl_iconfirst': SecondaryEpoch('trial_iconfirst', sel="wordType == 'nouncontrol'"),
        # 'nounNaming_iconfirst': SecondaryEpoch('trial_iconfirst', sel="wordType == 'nounnm'"),
        # 'nounPlural_iconfirst': SecondaryEpoch('trial_iconfirst', sel="wordType == 'nounpp'"),
        # 'nounPhrase_iconfirst': SecondaryEpoch('trial_iconfirst', sel="wordType == 'nounpc'"),
        # 'verbControl_iconfirst': SecondaryEpoch('trial_iconfirst', sel="wordType == 'verbcontrol'"),
        # 'verbNaming_iconfirst': SecondaryEpoch('trial_iconfirst', sel="wordType == 'verbnm'"), 
        # 'verbInflect_iconfirst': SecondaryEpoch('trial_iconfirst', sel="wordType == 'verbinflect'"),
        'icon_iconfirst': PrimaryEpoch('iconfirst', "stimulus == 'icon'", tmin = 0, tmax = (400+15)/1000),
        'icon_iconfirst_long': PrimaryEpoch('iconfirst', "stimulus == 'icon'", tmin = 0, tmax = 0.8),
        'icon_iconfirst_long_regular': PrimaryEpoch('iconfirst', "(stimulus == 'icon') & (verbType!='regular')", tmin = 0, tmax = 0.8),
        'picture_iconfirst': PrimaryEpoch('iconfirst', "stimulus == 'picture'", tmin = 0, tmax = (400+15)/1000),
        'picture_iconfirst_long': PrimaryEpoch('iconfirst', "stimulus == 'picture'", tmin = 0, tmax = 0.8),
        'picture_iconfirst_long_regular': PrimaryEpoch('iconfirst', "(stimulus == 'picture') & (verbType!='irregular')", tmin = 0, tmax = 0.8),
        'speak_iconfirst' : PrimaryEpoch('iconfirst', "(stimulus == 'speak') & (accuracy == 'correct')", trigger_shift = 'rt', tmin = -1, tmax = 1),
        'trial_picturefirst': PrimaryEpoch('picturefirst', "stimulus == 'fixation'", tmax = tmaxTrial),
        'trial_picturefirst_regular': PrimaryEpoch('picturefirst', "(stimulus == 'fixation') & (verbType!='irregular')", tmax = tmaxTrial),
        'trial_picturefirst_irregular': PrimaryEpoch('picturefirst', "(stimulus == 'fixation') & (verbType!='regular')", tmax = tmaxTrial),
        'nounControl_picturefirst': SecondaryEpoch('trial_picturefirst', sel="wordType == 'nouncontrol'"),
        'nounNaming_picturefirst': SecondaryEpoch('trial_picturefirst', sel="wordType == 'nounnm'"),
        # 'nounPlural_picturefirst': SecondaryEpoch('trial_picturefirst', sel="wordType == 'nounpp'"),
        # 'nounPhrase_picturefirst': SecondaryEpoch('trial_picturefirst', sel="wordType == 'nounpc'"),
        'verbControl_picturefirst': SecondaryEpoch('trial_picturefirst', sel="wordType == 'verbcontrol'"),
        'verbNaming_picturefirst': SecondaryEpoch('trial_picturefirst', sel="wordType == 'verbnm'"), 
        # 'verbInflect_picturefirst': SecondaryEpoch('trial_picturefirst', sel="wordType == 'verbinflect'"),
        'icon_picturefirst': PrimaryEpoch('picturefirst', "stimulus == 'icon'", tmin = 0, tmax = (400+15)/1000),
        'icon_picturefirst_long': PrimaryEpoch('picturefirst', "stimulus == 'icon'", tmin = 0, tmax = 0.8),
        'icon_picturefirst_long_regular': PrimaryEpoch('picturefirst', "(stimulus == 'icon') & (verbType!='irregular')", tmin = 0, tmax = 0.8),
        'picture_picturefirst': PrimaryEpoch('picturefirst', "stimulus == 'picture'", tmin = 0, tmax = (400+15)/1000),
        'picture_picturefirst_long': PrimaryEpoch('picturefirst', "stimulus == 'picture'", tmin = 0, tmax = 0.8),
        'picture_picturefirst_long_regular': PrimaryEpoch('picturefirst', "(stimulus == 'picture') & (verbType!='irregular')", tmin = 0, tmax = 0.8),
        'speak_picturefirst' : PrimaryEpoch('picturefirst', "(stimulus == 'speak') & (accuracy == 'correct')", trigger_shift = 'rt', tmin = -1.5, tmax = 0.2),
        'speak_picturefirst_regular' : PrimaryEpoch('picturefirst', "(stimulus == 'speak') & (accuracy == 'correct') & (verbType!='irregular')", trigger_shift = 'rt', tmin = -1.5, tmax = 0.2),
        'speak_picturefirst_irregular' : PrimaryEpoch('picturefirst', "(stimulus == 'speak') & (accuracy == 'correct') & (verbType!='regular')", trigger_shift = 'rt', tmin = -1.5, tmax = 0.2),
    }
    
    # I didn't predefine VectorDifferenceRelated and Vector tests for volumn source space here, but one could
    # (I used them directly in the s05_eelbrain_analysis_volume_source.ipynb script)
    tests = {
        '=0': TTestOneSample(),
        'nounNaming-nounControl': TTestRelated('wordType', 'nounnm', 'nouncontrol'),
        'nounPlural-nounControl': TTestRelated('wordType', 'nounpp', 'nouncontrol'),
        'nounPhrase-nounControl': TTestRelated('wordType', 'nounpc', 'nouncontrol'),
        'nounPlural-nounNaming': TTestRelated('wordType', 'nounpp', 'nounnm'),
        'nounPhrase-nounNaming': TTestRelated('wordType', 'nounpc', 'nounnm'),
        'nounPhrase-nounPlural': TTestRelated('wordType', 'nounpc', 'nounpp'),
        'nounNaming-verbNaming': TTestRelated('wordType', 'nounnm', 'verbnm'),
        'nounControl-verbControl': TTestRelated('wordType', 'nouncontrol', 'verbcontrol'),
        'verbNaming-verbControl': TTestRelated('wordType', 'verbnm', 'verbcontrol'),
        'verbInflectPast-verbControl': TTestRelated('wordType', 'infpst', 'verbcontrol'),
        'verbInflectFuture-verbControl': TTestRelated('wordType', 'inffut', 'verbcontrol'),
        'verbInflectPast-verbNaming': TTestRelated('wordType', 'infpst', 'verbnm'),
        'verbInflectFuture-verbNaming': TTestRelated('wordType', 'inffut', 'verbnm'),
        'verbInflectPast-verbInflectFuture': TTestRelated('wordType', 'infpst', 'inffut'),
    }

    parcs = {
        'wholebrain': SubParc('aparc', WHOLEBRAIN),
        'frontal-temporal-parietal-lh': SubParc('aparc', LEFT_FRONTAL_TEMPORAL_PARIETAL),
        'lateral': SubParc('aparc', LATERAL),
        'occipital-lateral': SubParc('aparc', LATERAL_OCCIPITAL),
        'parietal-lateral': SubParc('aparc', LATERAL_PARIETAL),
        'temporal-lateral': SubParc('aparc', LATERAL_TEMPORAL),
        'frontal-lateral': SubParc('aparc', LATERAL_FRONTAL),
        'visual-primary-lateral': SubParc('aparc','lateraloccipital'),
        'STG-lateral': SubParc('aparc', LATERAL_STG),
        'IFG-lateral': SubParc('aparc', LATERAL_IFG), 
        'parietal-lh': SubParc('aparc', LEFT_PARIETAL),
        'temporal-lh': SubParc('aparc', LEFT_TEMPORAL),
        'frontal-lh': SubParc('aparc', LEFT_FRONTAL), 
        'parietal-rh': SubParc('aparc', RIGHT_PARIETAL),
        'temporal-rh': SubParc('aparc', RIGHT_TEMPORAL),
        'frontal-rh': SubParc('aparc', RIGHT_FRONTAL),
        'Broca': SubParc('aparc', BROCA),
        'Wernicke': SubParc('aparc', WERNICKE),
        'IFG-lh': SubParc('aparc', LEFT_IFG),
        'IFG-rh': SubParc('aparc', RIGHT_IFG),
        'STG-lh': SubParc('aparc', LEFT_STG),
        'STG-rh': SubParc('aparc', RIGHT_STG),
        'IPL-lh': SubParc('aparc', LEFT_IPL),
        'IPL-rh': SubParc('aparc', RIGHT_IPL),
        'precentral-lateral': SubParc('aparc', ('precentral')),
        'frontal-temporal': SubParc('aparc', FRONTAL_TEMPORAL),
        'cortex': SubParc('aparc', 'aparc'),       
        }
    
    
# maybe use the last 100ms of the fixation time as baseline for everything. 
data_path = '/Users/yiwei/Documents/agrammatism/MEGstudy'
megData = agrammatismMEG(data_path) 


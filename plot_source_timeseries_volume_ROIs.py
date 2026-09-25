import runpy
runpy.run_path('/Users/yiwei/Dropbox/agrammatism/code/s01_eelbrain_pipelineSetup.py')
from s01_eelbrain_pipelineSetup import *
import re

session = 'picturefirst'
group = 'right_hand'
IFG_lh_mask = ['ctx-lh-parsopercularis',
    'ctx-lh-parsorbitalis',
    'ctx-lh-parstriangularis']
mask = IFG_lh_mask

inv_info = 'vec-3-dSPM-0'
src_info = 'vol-5'
megData.set_inv(ori=re.split('-',inv_info)[0], 
                snr=int(re.split('-',inv_info)[1]), 
                method=re.split('-',inv_info)[2], 
                depth=int(re.split('-',inv_info)[3]), 
                pick_normal=False, 
                src=src_info)
megData.set(parc = 'aparc+aseg')

        
megData.set(raw='ica-'+session, epoch='trial_'+session+'_regular', rej='')
erp_stc_all_wordType = megData.load_evoked_stc(
    subjects=group, 
    baseline=False,
    cov='emptyroom', 
    model='wordType')


# combining verb inflection past and future conditions
verbinflect_erp_stc = erp_stc_all_wordType.sub("(wordType=='infpst')|(wordType=='inffut')")
verbinflect_erp_stc = verbinflect_erp_stc.aggregate('subject', drop=['wordType','verbType'])
verbinflect_erp_stc['wordType']=Factor(['verbinflect'] * len(verbinflect_erp_stc['subject']))

evoked_source_all_wordType = combine([verbinflect_erp_stc, erp_stc_all_wordType], incomplete='drop')
evoked_source_all_wordType['srcm']=set_parc(evoked_source_all_wordType['srcm'],'aparc+aseg')
evoked_source_all_wordType['ROI'] = evoked_source_all_wordType['srcm'].sub(source=IFG_lh_mask).norm('space').mean('source')

p = plot.UTSStat('ROI', 'wordType', data=evoked_source_all_wordType.sub("(wordType=='inffut')|(wordType=='verbnm')"), xlim=[1.8,3], error='ci')


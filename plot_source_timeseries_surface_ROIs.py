import runpy
runpy.run_path('/Users/yiwei/Dropbox/agrammatism/code/s01_eelbrain_pipelineSetup.py')
from s01_eelbrain_pipelineSetup import *

session = 'iconfirst'
word_types = ['verbnm','infpst', 'inffut']
colors = ['#56B4E9', '#9400D3', '#FF5733']
masks_lobes = ['parietal-lh','parietal-rh','temporal-lh','temporal-rh','frontal-lh','frontal-rh']
masks_regions = ['IPL-lh','IPL-rh','STG-lh','STG-rh','IFG-lh','IFG-rh']
group = 'right_hand'
# group = 'iconfirst_first_goodmarkerspicture'

megData.set_inv(ori='fixed', snr=3, method='MNE', depth=0, pick_normal=False)
megData.set(raw='ica-'+session, epoch='trial_'+session, rej='')

evoked_source_all_wordType = megData.load_evoked_stc(
    subjects=group, 
    mask='wholebrain',
    baseline=False, 
    cov='emptyroom', 
    model='wordType')
verbinflect_erp_stc = evoked_source_all_wordType.sub("(wordType=='infpst')|(wordType=='inffut')")
verbinflect_erp_stc = verbinflect_erp_stc.aggregate('subject', drop='wordType')
verbinflect_erp_stc['wordType']=Factor(['verbinflect'] * len(verbinflect_erp_stc['subject']))
evoked_source_all_wordType_ds = combine([verbinflect_erp_stc, evoked_source_all_wordType])

word_type_colors = {word_type: color for word_type, color in zip(word_types, colors)}
color_dict = {}

mask_name_lobes = [mask.replace('-','') for mask in masks_lobes]
for mask in mask_name_lobes:
    for word_type in word_types:
        color_dict[(mask, word_type)] = word_type_colors[word_type]
        
for mask in masks_lobes:
    evoked_source_all_wordType = megData.load_evoked_stc(
        subjects=group, 
        baseline=False, 
        mask=mask, 
        cov='emptyroom', 
        model='wordType')
    
    verbinflect_erf_stc = evoked_source_all_wordType.sub("(wordType=='infpst')|(wordType=='inffut')")
    verbinflect_erf_stc = verbinflect_erf_stc.aggregate('subject', drop='wordType')
    verbinflect_erf_stc['wordType']=Factor(['verbinflect'] * len(verbinflect_erf_stc['subject']))
    evoked_source_all_wordType = combine([verbinflect_erf_stc, evoked_source_all_wordType])
    
    sourceERP_wordType = evoked_source_all_wordType['srcm']
    evoked_source_all_wordType_ds[mask.replace('-','')] = filter_data(sourceERP_wordType.rms('source'), 1, 10) 
    # evoked_source_all_wordType_ds[mask.replace('-','')] = sourceERP_wordType.mean('source')

p = plot.UTSStat(mask_name_lobes, 'wordType', 
                    data=evoked_source_all_wordType_ds.sub("|".join([f"(wordType=='{wt}')" for wt in word_types])), 
                    h=6, w=5, 
                    colors = color_dict,
                    legend = False,
                    title=f"{session}")

p.figure.axes[0].set_ylim(-3e-11, 6e-11)
p.figure.axes[1].set_ylim(-3e-11, 6e-11)
p.figure.axes[2].set_ylim(-3e-11, 6e-11)
p.figure.axes[3].set_ylim(-3e-11, 6e-11)
p.figure.axes[4].set_ylim(-3e-11, 4e-11)
p.figure.axes[5].set_ylim(-3e-11, 4e-11)
p_legend = plot.ColorList(word_type_colors, w=2) 


mask_name_regions = [mask.replace('-','') for mask in masks_regions]
for mask in mask_name_regions:
    for word_type in word_types:
        color_dict[(mask, word_type)] = word_type_colors[word_type]
        
for mask in masks_regions:
    evoked_source_all_wordType = megData.load_evoked_stc(
        subjects=group, 
        baseline=False, 
        mask=mask, 
        cov='emptyroom', 
        model='wordType')
    
    verbinflect_erf_stc = evoked_source_all_wordType.sub("(wordType=='infpst')|(wordType=='inffut')")
    verbinflect_erf_stc = verbinflect_erf_stc.aggregate('subject', drop='wordType')
    verbinflect_erf_stc['wordType']=Factor(['verbinflect'] * len(verbinflect_erf_stc['subject']))
    evoked_source_all_wordType = combine([verbinflect_erf_stc, evoked_source_all_wordType])
    
    sourceERP_wordType = evoked_source_all_wordType['srcm']
    # evoked_source_all_wordType['RMS'] = sourceERP_wordType.rms('source')
    evoked_source_all_wordType_ds[mask.replace('-','')] = filter_data(sourceERP_wordType.rms('source'), 1, 10) 
    # evoked_source_all_wordType_ds[mask.replace('-','')] = sourceERP_wordType.mean('source')

p = plot.UTSStat(mask_name_regions, 'wordType', 
                    data=evoked_source_all_wordType_ds.sub("|".join([f"(wordType=='{wt}')" for wt in word_types])), 
                    h=6, w=5, 
                    colors = color_dict,
                    legend = False,
                    title=f"{session}")

p.figure.axes[0].set_ylim(-3e-11, 8e-11)
p.figure.axes[1].set_ylim(-3e-11, 8e-11)
p.figure.axes[2].set_ylim(-3e-11, 8e-11)
p.figure.axes[3].set_ylim(-3e-11, 8e-11)
p.figure.axes[4].set_ylim(-3e-11, 5e-11)
p.figure.axes[5].set_ylim(-3e-11, 5e-11)
p_legend = plot.ColorList(word_type_colors, w=2) 

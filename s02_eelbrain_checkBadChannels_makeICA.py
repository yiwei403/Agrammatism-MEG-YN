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

# +

import runpy
runpy.run_path('/Users/yiwei/Dropbox/agrammatism/code/s01_eelbrain_pipelineSetup.py')
from s01_eelbrain_pipelineSetup import *
# -

# ### check channels that are uncorrelated with neighboring channels

# +

# # plotting the average evoked response, and looking for channels which are uncorrelated with neighboring channels.
# # megData.next('subject')

subject = 'R3212'

megData.set(raw = '1-40', subject = subject)
data = megData.load_epochs(epoch ='trial_iconfirst', reject=False)
p = plot.TopoButterfly(data['meg'])
nc = neighbor_correlation(concatenate(data['meg']))
plot.Topomap(nc)
print(nc.sensor.names[nc < 0.4])
# megData.make_bad_channels([''])

data = megData.load_epochs(epoch ='trial_picturefirst', reject=False)
p = plot.TopoButterfly(data['meg'])
nc = neighbor_correlation(concatenate(data['meg']))
plot.Topomap(nc)
print(nc.sensor.names[nc < 0.4])

# # add bad channels into the megData object.
# megData.make_bad_channels([''])
# -

# ### run ICA on both sessions. 

# +

# subjects = ['R3212']
# sessions = ['iconfirst', 'picturefirst']

# for subject in subjects:
#     for session in sessions:        
#         megData.set(raw = 'ica-'+session, session=session, subject=subject)
#         megData.make_ica()


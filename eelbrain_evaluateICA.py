# run this script in eelbrain ipython to see interactive plots. 
# %%
import runpy
runpy.run_path('/Users/yiwei/Dropbox/agrammatism/code/s01_eelbrain_pipelineSetup.py')
from s01_eelbrain_pipelineSetup import *
import sys

subject = sys.argv[1]
session = sys.argv[2]
# title = sys.argv[3]

# subject = 'R2877'
# session = 'iconfirst'

# trial erp before ICA
megData.set(raw='1-40', subject=subject, session=session)
preICA = megData.load_epochs(epoch='trial_'+session, reject=False)
p = plot.TopoButterfly(preICA['meg'], title='preICA')

# trial erp after ICA
megData.set(raw='ica-'+session, subject=subject, session=session)
postICA = megData.load_epochs(epoch='trial_'+session, reject=False)
p = plot.TopoButterfly(postICA['meg'], title='postICA')

import runpy
runpy.run_path('/Users/yiwei/Dropbox/agrammatism/code/s01_eelbrain_pipelineSetup.py')
from s01_eelbrain_pipelineSetup import *
import sys

subject = sys.argv[1]
session = sys.argv[2]

# subject = 'R2877'
# session = 'iconfirst'

megData.set(raw = 'ica-'+session, epoch ='trial_'+session, subject=subject, session=session)
megData.make_epoch_selection()
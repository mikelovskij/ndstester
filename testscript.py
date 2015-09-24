import ndstoast

__author__ = 'mikelovskij'

servers = {'L1': 'nds.ligo-la.caltech.edu', 'H1': 'nds.ligo-wa.caltech.edu'}
testchannels = ['OAF-CAL_DARM_DQ', 'ISI-GND_STS_ITMY_Z_DQ']  # prompt the user, or load from file?

tst = ndstoast.NdsTester()
results = tst.tester(testchannels=testchannels, servers=servers, avail_check=True, stride=20)
tst.resultlogger(results)

"""Start of the analysis"""

# ROOT interfers with argv -> import it later
# see: http://root.cern.ch/phpBB3/viewtopic.php?t=8501
import argparse
import pickle
import time
from os.path import dirname, abspath
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--assocs", help="interval for associated particles;"
                    + "min max",
                    nargs=2, type=float, default=[1.0, 2.0])
parser.add_argument("--triggers", help="interval for trigger particles;"
                    + "min max",
                    nargs=2, type=float, default=[2.0, 4.0])

args = parser.parse_args()
with open('parameters.pkl', 'wb') as pkl:
    pickle.dump(args, pkl)

tmpargv = sys.argv[:]    # [:] for a copy, not reference
sys.argv = []

from ROOT import TProof, TFileCollection, TChain
sys.argv = tmpargv

proof = TProof.Open('')

# giving some name to collection to shut up warning
fc = TFileCollection('analysis_files')
fn = '/home/christian/msc/analysis/pyproof/ppb.dat'
fc.AddFromFile(fn)

chain = TChain("tree")
with open(fn, 'read') as f:
    for l in f.readlines()[:5]:
        chain.AddFile(l[:-1])

proof.Load('./ClassesMultESA2013.C+,./parameters.pkl')
# add the current folder to the python path of root (or something)
proof.Exec('TPython::Exec("%s");' %
        ("import sys; sys.path.insert(0,'"+dirname(abspath("selector.py"))+"')"))

time.sleep(1)  # needed for GUI to settle

proof.Process(fc, 'TPySelector', 'selector')
#chain.Process('TPySelector', 'selector')

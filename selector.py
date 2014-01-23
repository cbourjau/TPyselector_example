### selector module (selector.py, name has to match as per in main.py)
from ROOT import TPySelector, gROOT, TH1I, THnSparseF

from array import array
import pickle
from rootpy.io import root_open
from math import pi

# load MyClass definition macro (append '+' to use ACLiC)
gROOT.LoadMacro('ClassesMultESA2013.C+')
#from ROOT import DeDxEvent


def try_except(fn):
    """decorator for extra debugging output"""
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except:
            import traceback
            traceback.print_exc()
            assert(0)
    return wrapped


class MyPySelector(TPySelector):
    def __init__(self):
        print self.__class__.__module__+": init"
        with open('parameters.pkl', 'read') as pkl:
            args = pickle.load(pkl)
        print 'Settings: ', args
        self.assoc_inter = args.assocs
        self.trigger_inter = args.triggers
        self.zvtx_bins = (10, -10, 10)
        self.phi_bins = (36, (-pi/2), (3*pi/2))
        self.eta_bins = (32, -1.6, 1.6)

        self.trigger = 1  # 1 = V0AND
        self.max_dist_vtx_xy = 2.4
        self.max_dist_vtx_z = 3.2

    def Begin(self):
        print 'Ran Begin()'

    def SlaveBegin(self, tree):
        print 'py: slave beginning'

        # Dimensions: phi, eta, z_vtx
        self.assoc_hist = self.make_histogram('assocs', 'Associated')
        self.trigger_hist = self.make_histogram('triggers', 'Triggers')
        self.GetOutputList().Add(self.assoc_hist)
        self.GetOutputList().Add(self.trigger_hist)

    @try_except
    def Process(self, entry):
        self.fChain.GetBranch('event').GetEntry(entry)
        if not self.validate_event():
            return 1
        self.fChain.GetBranch('track').GetEntry(entry)

        trigs, assocs = self.get_triggers_assocs()
        if len(trigs) == 0:
            return 1

        trig_fill = self.trigger_hist.Fill
        assoc_fill = self.assoc_hist.Fill

        for phi, eta, zvtx in trigs:
            a = array('d', [phi, eta, zvtx])
            trig_fill(a)
        for phi, eta, zvtx in assocs:
            a = array('d', [phi, eta, zvtx])
            assoc_fill(a)
        return 0

    def SlaveTerminate(self):
        print 'py: slave terminating'

    def Terminate(self):
        with root_open('output.root',
                       'recreate') as f:
            # write original histograms:
            f.mkdir('raw')
            f.raw.cd()
            for l in self.GetOutputList():
                l.Write()
        print 'fOutput in Terminate', self.GetOutputList().ls()
        print 'Successfully wrote results to output.root'

    ### Analysis functions
    def make_histogram(self, name, title,
                       axis_title=';#Delta #varphi;#Delta #eta;z_vtx'):
        """create a n dim histogram"""
        phi_nbins, phi_low, phi_high = self.phi_bins
        eta_nbins, eta_low, eta_high = self.eta_bins
        zvtx_nbins, zvtx_low, zvtx_high = self.zvtx_bins

        tmp = THnSparseF(name,
                         title + axis_title,
                         3,  # dimensions
                         array('i', [phi_nbins, eta_nbins, zvtx_nbins]),
                         array('d', [phi_low, eta_low,  zvtx_low]),
                         array('d', [phi_high, eta_high, zvtx_high]))
        tmp.Sumw2()
        return tmp

    def get_triggers_assocs(self):
        """Ret ([[trig_phi, trig_eta, pt]], [[assoc_phi, assoc_eta, pt]])
        for valid tracks
        """
        lower_trig, upper_trig = self.trigger_inter
        lower_assoc, upper_assoc = self.assoc_inter
        triggers, assocs = [], []
        tracks = self.fChain.track
        for track in tracks:
            if not self.validate_track(track):
                continue
            if (lower_assoc < track.pt < upper_assoc):
                zvtx = self.fChain.event.zvtx
                assocs.append([track.phi, track.eta, zvtx])
            elif (lower_trig < track.pt < upper_trig):
                zvtx = self.fChain.event.zvtx
                triggers.append([track.phi, track.eta, zvtx])
        return (triggers, assocs)

    def validate_event(self):
        """Validate event on event level"""
        if not (-10 < self.fChain.event.zvtx < 10):
            return False
        return True

    def validate_track(self, track):
        if abs(track.dcaxy) > self.max_dist_vtx_xy:
            return False
        if abs(track.dcaz) > self.max_dist_vtx_z:
            return False
        return True

    def Init(self, tree):
        # event branch
        self.fChain.SetBranchStatus('*', 0)
        self.fChain.SetBranchStatus('ptmax', 1)
        self.fChain.SetBranchStatus('cent', 1)
        self.fChain.SetBranchStatus('zvtx', 1)
        self.fChain.SetBranchStatus('trig', 1)
        self.fChain.SetBranchStatus('vtxstatus', 1)
        # track branch
        self.fChain.SetBranchStatus('track.phi', 1)
        self.fChain.SetBranchStatus('track.eta', 1)
        self.fChain.SetBranchStatus('track.pt', 1)
        self.fChain.SetBranchStatus('track.filter', 1)
        self.fChain.SetBranchStatus('track.primary', 1)
        self.fChain.SetBranchStatus('track.dcaxy', 1)
        self.fChain.SetBranchStatus('track.dcaz', 1)

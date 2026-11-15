"""NETC11 (own code): chained-block carriers.  Unit = one helper of one carrier (delivers u = L + sum(alpha picks) at
(t1, G) to r).  Netc11 chains units h_1..h_m (different blocks, t1 ascending, G ascending) into ONE helper: alpha picks
of h_1, give; for j>=2 DIFFERENCE picks (sum = u_j - u_{j-1}, frames ascending in [G_{j-1}, G_j], times in
[t1_{j-1}, t1_j)), give; beta tail picks of h_m.  Load = -beta(all picks) (as Netc.build); final pi = alpha(total)."""
import sys, os, pickle
W6 = 'inputs/'
sys.path[:0] = [W6 + 'NETC11', W6 + 'NETC6']
import core6
from core6 import *
import netc6, run_netc5
from fractions import Fraction as Q
from decomp import tomod, ordered_solve
from netc import exact_solve
from width import Ech

def vsum(snaps, vis):
    tot = {}
    for key, F, op in vis:
        if op[0] == 'pick':
            for kk, vv in snaps[op[1]][4].items():
                nv = tot.get(kk, 0) + op[2] * vv
                if nv: tot[kk] = nv
                else: tot.pop(kk, None)
    return tot

class Netc11(netc6.Netc6):
    chains11 = ()
    def split(self, h):
        t1 = h['block']['t1']; gk = (t1, 0.5)
        a = [x for x in h['visits'] if x[2][0] == 'pick' and x[0] < gk]
        z = [x for x in h['visits'] if x[2][0] == 'pick' and x[0] >= gk]
        g = [x for x in h['visits'] if x[2][0] != 'pick']; assert len(g) == 1
        return a, g[0], z
    def udeliv(self, h):
        a, g, z = self.split(h)
        u = dict(h['load'])
        for kk, vv in vsum(self.snaps, a).items():
            nv = u.get(kk, 0) + vv
            if nv: u[kk] = nv
            else: u.pop(kk, None)
        return u
    def merge(self, H, hs, diffs):
        first, last = H[hs[0]], H[hs[-1]]
        a, g, _ = self.split(first); _, _, z = self.split(last)
        vis = list(a) + [g]
        for j in range(1, len(hs)):
            vis += diffs[j - 1]; b = H[hs[j]]['block']; vis.append(((b['t1'], 0.5), b['frame'], ('give', b['r'])))
        vis += z
        L = {kk: -vv for kk, vv in self.beta(vsum(self.snaps, vis)).items()}
        return dict(visits=vis, load=L, block=first['block'])
    def build(self):
        H = super().build()
        self.H0 = H
        if not self.chains11: return H
        drop = set(); H = list(H)
        for ch in self.chains11:
            H[ch['hs'][0]] = self.merge(self.H0, ch['hs'], ch['diffs']); drop |= set(ch['hs'][1:])
        self.H = [h for i, h in enumerate(H) if i not in drop]
        return self.H

def load11(log=lambda *a: None):
    run_netc5.Netc5 = Netc11
    N, nb = run_netc5.prepare(core6.BASE, log)
    N.PB = [x.split(':') for x in os.environ.get('PB', '').split(',') if x]
    return N

"""Exact favorable packing cap with local paid profile and controller fixed."""
from collections import Counter
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
from verify import read,need
P=Path(__file__).resolve().parent

def main():
    plan=read(P/'data/PLAN.json');idle=read(P/'data/CONSTRUCTION.json')['idle'];cap=read(P/'PACKING-CAP.json');claim=read(P/'CLAIM.json')
    mass=sum(int(r)*n for r,n in idle.items());H=Counter()
    for call in plan['provider_calls']:H.update({int(r):48*n for r,n in plan['provider_registry'][call['provider']]['actual_paid_profile'].items()})
    H[48]+=mass
    need(dict(H)=={int(r):n for r,n in cap['profile'].items()},'fixed-profile cap binding')
    need(all(int(r)<=48 for r in idle),'maximum pending rank')
    spec=importlib.util.spec_from_file_location('cap_moment',P/'vendor/fine_moment.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
    e.SH=256;e.GRID=1<<256;e.LOG_TERMS=100;e.EXP_TERMS=96
    lo,hi=Q(cap['b_lower']),Q(cap['b_upper'])
    need(e.moment(73,48*66304,sorted(H.items()),lo)[1]<1<e.moment(73,48*66304,sorted(H.items()),hi)[0],'directed packing-cap bracket')
    # r^(1-b) >= r*48^(-b) for every idle rank r<=48 and b>0.
    print('PASS_FIXED_LOCAL_PROFILE_PACKING_CAP',cap['b_upper'],'realized_fraction',float(Q(claim['kappa'])/hi),flush=True)

if __name__=='__main__':main()

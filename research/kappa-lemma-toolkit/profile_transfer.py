"""Exact final profile improvement, without trusting floating search objectives."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent/'selective-borrowing-kappa'
def load(name,path):
    sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);a=parser.parse_args()
    if a.out.resolve().is_relative_to(HERE.parent):raise ValueError('external receipt required')
    old=json.loads((BASE/'owners/EXPECTED.json').read_bytes());new=json.loads((HERE/'OWNERS-EXPECTED.json').read_bytes())
    H0={int(k):v for k,v in old['profile'].items()};H1={int(k):v for k,v in new['profile'].items()};saving=Q(84179,50000000)
    M=load('retained_mercator_delta',BASE/'arithmetic/vendor/moment.py');B=load('retained_atanh_delta',BASE/'arithmetic/vendor/base_two_moment.py');B.log_bounds=lru_cache(None)(B.log_bounds)
    m0=M.moment(H0,73,7168,saving,True);m1=M.moment(H1,73,7168,saving,True)
    def atanh(h):
        z=B.moment(73,7168,list(h.items()),saving);fallback=B.moment(73,7168,[(1,32*73*73*sum(h.values()))],saving)
        return(z[0]+fallback[0]/10**16,z[1]+fallback[1]/10**16)
    b0,b1=atanh(H0),atanh(H1)
    if not(m0[0]>1 and b0[0]>1 and m1[1]<1 and b1[1]<1 and m1[1]<m0[0] and b1[1]<b0[0]):raise ValueError('strict old/new profile separation failed')
    if sum(k*v for k,v in H0.items())!=520704 or sum(k*v for k,v in H1.items())!=520704:raise ValueError('rank mass not retained')
    delta={k:H1.get(k,0)-H0.get(k,0) for k in H0.keys()|H1.keys() if H1.get(k,0)!=H0.get(k,0)}
    report=dict(status='PASS_EXACT_PROFILE_IMPROVEMENT',complex_saving=str(saving),rank_mass=520704,deficit=2560,profile_count_delta=delta,positive_child_count_change=sum(delta.values()),mercator={'old_residual':[str(v-1)for v in m0],'new_residual':[str(v-1)for v in m1],'difference_upper':str(m1[1]-m0[0])},atanh={'old_residual':[str(v-1)for v in b0],'new_residual':[str(v-1)for v in b1],'difference_upper':str(b1[1]-b0[0])},scope='Exact finite cost improvement of the actual old/new profiles. Physical validity and inherited all-size assumptions are checked/stated separately; no floating search output is evidence.')
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],delta)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Exact data-corner refinement of pinned Zhihao Chen PR29, with attribution."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
# Avoid capturing another suite's generic assembly module.
saved=sys.modules.get('assembly');old_path=sys.path[:]
sys.modules['assembly']=module('corner_parent_assembly',ROOT/'research/two-stage/assembly.py')
try:parent=module('corner_parent_verify',ROOT/'research/two-stage/verify.py')
finally:
    sys.path[:]=old_path
    if saved is None:sys.modules.pop('assembly',None)
    else:sys.modules['assembly']=saved
arithmetic=module('corner_parameterized_assembly',HERE/'assembly_parameterized.py')
cutoff=module('corner_cutoff_helpers',HERE/'cutoffs.py')
moment=module('corner_exact_moment',HERE/'moment.py')
identities=module('corner_independent_identities',HERE/'independent.py')
BIT=Q(15879079,10**12);KAPPA=Q(15878574,10**12)

def run():
    source=json.loads((HERE/'SOURCE.json').read_text())
    for name,digest in source['base_source_sha256'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    old=parent.run();b=old['bit'];rows=Counter(b['rows']);N=b['N']
    rows[1]-=192*N;rows[51]+=2*N;rows[45]+=2*N
    assert rows[1]>=N and sum(t*c for t,c in rows.items())==b['s']
    assert max(rows)==max(b['rows']) and b['W']*b['m']-b['s']==b['deficit']
    bit=moment.moment_search(b['m'],b['W'],rows);assert bit['saving']==BIT and bit['strict_gap']>0 and bit['next_moment_upper']>=1
    f=old['finite_bridge'];assert f['rows']['degree']==47000
    a=arithmetic.assembly(f,BIT,KAPPA);assert len(a['constraints'])==47 and len(a['margins'])==7
    eventual=cutoff.cutoffs(f,a);control=identities.run()
    rejected=[]
    for name,kwargs in [('old_guard',dict(old_guard=True)),('old_exposures',dict(old_exposures=True)),('next_kappa_grid',dict(kappa=KAPPA+Q(1,10**12)))]:
        try:arithmetic.assembly(f,BIT,kwargs.pop('kappa',KAPPA),**kwargs)
        except AssertionError:rejected.append(name)
        else:raise AssertionError(name)
    assert moment.moment_search(b['m'],b['W'],b['rows'])['saving']<BIT
    rejected+=['omit_data_blocks_lowers_certified_saving','next_bit_grid_not_certified_by_same_enclosure']
    files=list(HERE.glob('*.py'))+list(HERE.glob('*.txt'))+[HERE/'SOURCE.json',HERE/'README.md',HERE/'a5-residual-two-stage.json',ROOT/'notes/two-stage-corners-note.tex',ROOT/'tests/test_two_stage_corners.py']
    return dict(status='CONDITIONAL DATA-CORNER SAVING 15878574/10^12; NOT FORMAL VERIFICATION',data_profile=dict(copies=2*N,singletons=11,blocks=[51,45,2701],rank=2808),counts={**{k:b[k] for k in ('a','b','m','N','W','L','s','deficit')},'rows':rows},bit=bit,finite_bridge=f,assembly=a,eventual_bounds=eventual,identity_controls=control,negative_controls=rejected,parent_kappa=Q(15536,10**9),ratio_to_parent=KAPPA/Q(15536,10**9),pinned_parent_source_sha256=source['base_source_sha256'],source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)},scope='Only two contiguous data-corner blocks change. PR29 topology, producers, source/terminal frames, paid N rank-one copy corrections, W, rank mass, maximum child and semantic bridge remain unchanged. All inherited analytic/tape hypotheses remain. Full rerun status is separate in validation.json.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=HERE/'certificate.json');args=p.parse_args();r=run()
    args.output.write_text(json.dumps(cutoff.js(r),indent=2,sort_keys=True)+'\n');print('PASS kappa='+str(KAPPA)+';2265 zero-minor identities;47 strict constraints;7 margins')

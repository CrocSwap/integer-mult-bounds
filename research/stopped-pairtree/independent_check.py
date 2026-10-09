#!/usr/bin/env python3
"""Independent paid profiles, stopped recurrence, three-factor stock and 47 slacks.

Uses a separate 40-term log / degree-ten exponential enclosure and the
previously independent balanced assembly transcription. That transcription
is bound to an explicit three-factor bridge validator using an isolated
function namespace; the original module and sources are never modified.
"""
import sys
if not __debug__:raise RuntimeError('Assertions required')
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,types
from fractions import Fraction as Q
from collections import Counter
from functools import lru_cache
from math import comb
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
ARCHIVE=ROOT/'references/stopped-recursion/pr107'
spec=importlib.util.spec_from_file_location('pairtree_independent_math',ROOT/'research/deferred-span-frames/independent_check.py')
audit=importlib.util.module_from_spec(spec);sys.modules[spec.name]=audit;spec.loader.exec_module(audit)
GRID=10**18;SCALE=10**40
def read(path):return json.loads(path.read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def js(v):
    if isinstance(v,Q):return str(v)
    if isinstance(v,dict):return {str(k):js(x)for k,x in v.items()}
    if isinstance(v,(tuple,list)):return [js(x)for x in v]
    return v
def input_hash(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def floorq(x):return Q(x.numerator*SCALE//x.denominator,SCALE)
def ceilq(x):return -floorq(-x)
@lru_cache(None)
def logarithm(x):
    lo,hi=audit.logarithm(x);return floorq(lo),ceilq(hi)
def moment(p,a):
    lo=hi=Q()
    for t,n in p['child_multiplicities'].items():
        l,u=logarithm(Q(p['m'],t));weight=Q(t*n,p['m']*p['W'])
        lo+=weight*floorq(audit.exponential(a*l)[0]);hi+=weight*ceilq(audit.exponential(a*u)[1])
    return lo,hi

def profile(record):
    h,R=record['h'],record['R'];v=comb(h,3);assert v==record['v']
    H=Counter({r:n for r,n in enumerate(record['histogram'])if r and n})
    loss=h*(h-1);assert record['loss']==loss and sum(r*n for r,n in H.items())==h*R+2*loss
    H[h]-=h;H[1]+=h;assert H[h]>=0
    m=h*h;N=v*v;bank=v*R;W=2*N+2*bank
    rows=Counter({m-h:2*bank,(h-1)**2:2*N,h-1:4*N,1:N})
    rows.update({r:2*v*n for r,n in H.items()if n})
    assert all(0<r<m and n>0 for r,n in rows.items())
    rank=sum(r*n for r,n in rows.items());assert rank==m*W-N+2*v*loss
    corrected=list(record['histogram']);corrected[h]-=h;corrected[1]+=h
    return dict(dimensions=[h,h],m=m,N=N,B1=bank,B2=bank,W=W,L=2*v*loss,total_rank=rank,
                deficit=N-2*v*loss,maxchild=max(rows),copied_histogram=corrected,child_multiplicities=dict(rows))

def rebuild():
    inputs=dict(complex=read(HERE/'producer.json'),construction=read(HERE/'constructor.json'),bit=read(ARCHIVE/'certificates/stopped-product-bit-axis.json'))
    row,source=inputs['complex'],inputs['construction']
    assert row['baseline_R']==source['R']==source['c']+source['q'] and row['R']==source['R']-row['matched']
    for key in ('h','v','c','q','loss','central_disjoint','center_denominator'):assert row[key]==source[key]
    assert source['rank_sum']==sum(r*n for r,n in enumerate(source['histogram']))
    assert row['rank_sum']==sum(r*n for r,n in enumerate(row['histogram']))
    return dict(bit=profile(inputs['bit']),complex=profile(row)),inputs

def depth(m,r):
    k=1
    while m**k<=2*r**k:k+=1
    return k

def bridge_check(given,profiles,inputs):
    bit,cx=profiles['bit'],profiles['complex'];row=inputs['complex'];old=read(ARCHIVE/'certificates/copied-centers-network.json')['finite_bridge']['bit']
    expected={}
    for name,p in [('bit_coarse',bit),('complex',cx)]:
        expected[name]=dict(m=p['m'],W=p['W'],maxchild=max(p['child_multiplicities']),halving_degree=depth(p['m'],p['maxchild']),wire_bits=p['W'].bit_length())
    h,v,c=(row[k]for k in ('h','v','c'));assert h==row['central_disjoint']==24 and row['center_denominator']==21
    local=4*(c+v)+10*v+4*h*v+4*h*h+8*h+8
    term=dict(h=h,v=v,c=c,invocations=cx['N']//v,local_group_upper=local,copied_center_extra_groups=2*h)
    G=cx['N']+2*term['invocations']*(local+2*h)
    expected['complex'].update(s=cx['total_rank'],scalar_terms=[term,term],scalar_group_upper=G)
    W,m,s,r=(cx[k]for k in ('W','m','total_rank','maxchild'));E=64*(W+m+G+1)**3;B=s+E
    charge=2*G*W*W+8*s+4*W+4+32*m
    semantic=dict(E=E,literal_charge=charge,strict_literal_gap=E-charge,B=B,C0=32*m*B*B,C1=1,
                  induction_gap=2*B*(m-r)-s-E,fixed_odd_divisor=21,
                  exact_grid='One common dyadic grid times the fixed odd divisor to K=G*(D_complex+1); no child rounding')
    assert E>charge and semantic['induction_gap']>=0 and semantic['C0']>2*B+18
    old_degree=depth(old['m'],old['maxchild'])*old['W'].bit_length();assert old_degree==252
    expected['ordinary_leaf_row_degree']=old_degree
    coefficient=old_degree+sum(p['halving_degree']*p['wire_bits']for p in expected.values()if isinstance(p,dict))
    stock=dict(coefficient=coefficient,degree=4000,suffix_slope=16000,degree_gap=Q(4000)-Q(51,25)*coefficient,
               contract='W_complex^D_complex * W_coarse^D_coarse * W_old^D_old; one preceding prefix and one padding; sequential reuse')
    assert stock['degree_gap']>0
    expected.update(semantic=semantic,rows=stock)
    assert given==js(expected),'Independent three-factor bridge reconstruction differs'
    return semantic,stock

def validate(certificate,profiles,inputs):
    assert certificate['input_sha256']=={name:input_hash(value)for name,value in inputs.items()}
    assert certificate['coarse_bit']['profile']==js(profiles['bit']) and certificate['complex']['profile']==js(profiles['complex'])
    old=read(ARCHIVE/'certificates/copied-centers-network.json');ordinary=certificate['ordinary_bit']
    atom=Q(ordinary['atom_exponent']);coarse=Q(ordinary['coarse_saving']);leaf=Q(ordinary['leaf_saving'])
    assert atom==Q(1,1000)and coarse==Q(4019,50000000)and leaf==Q(old['bit']['saving'])
    actual=(1-atom)*coarse+atom*leaf
    assert Q(ordinary['saving'])==actual and Q(ordinary['adapter_gap'])==atom-actual>0
    assert 0<leaf<coarse<atom<1 and ordinary['ordinary_leaf_bridge']==old['finite_bridge']['bit']
    assert profiles['bit']['total_rank']<profiles['bit']['m']*profiles['bit']['W']
    moments={}
    for label,section,p,a in [('coarse_bit',certificate['coarse_bit'],profiles['bit'],coarse),('complex',certificate['complex'],profiles['complex'],Q(certificate['complex']['saving']))]:
        assert Q(section['saving'])==a
        lo,hi=moment(p,a);primary=section['moment']
        assert Q(primary['saving'])==a and Q(primary['lower'])<=lo<=hi<=Q(primary['upper'])<1
        assert set(primary['terms'])==set(map(str,p['child_multiplicities']))
        for r,n in p['child_multiplicities'].items():assert Q(primary['terms'][str(r)]['weight'])==Q(r*n,p['m']*p['W'])
        moments[label]=dict(lower=lo,upper=hi,strict_gap=1-hi)
    cx=certificate['complex'];b=Q(cx['saving']);assert Q(cx['next_saving'])==b+Q(1,GRID)
    lo,hi=moment(profiles['complex'],b+Q(1,GRID));primary=cx['next_moment']
    assert Q(primary['saving'])==b+Q(1,GRID) and 1<Q(primary['lower'])<=lo<=hi<=Q(primary['upper'])
    moments['next_complex']=dict(lower=lo,upper=hi)
    beta=Q(certificate['beta']);h=Q(certificate['h']);a=Q(certificate['bit_saving'])
    assert beta==Q(1,10**12)and h==Q(1,GRID)and a==min(actual,(1-beta)*b-h)
    globals_={**audit.independent_assembly.__globals__,'check_bridge':lambda f:bridge_check(f,profiles,inputs)}
    independent_assembly=types.FunctionType(audit.independent_assembly.__code__,globals_)
    margin,slacks,margins=independent_assembly(certificate)
    assert Q(certificate['kappa'])<margin<=Q(certificate['kappa'])+Q(1,GRID)
    assert certificate['next_kappa_grid_rejected']
    assert Q(certificate['improvement_over_pr107'])==Q(certificate['kappa'])-Q(certificate['previous_pr107_kappa'])>0
    return dict(moments=moments,minimum_margin=margin,strict_constraints=len(slacks),cost_margins=len(margins),
                rank_totals={name:p['total_rank']for name,p in profiles.items()},row_factor_count=3)

def sources():
    manifest=read(ARCHIVE/'ARCHIVE.json')
    for path,expected in manifest['files'].items():
        blob=(ARCHIVE/path).read_bytes();assert hashlib.sha256(blob).hexdigest()==expected
        assert hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()==manifest['git_blobs'][path]
    original=read(ARCHIVE/'research/reversed-rational-centers/SOURCE.json')
    for path,expected in original['files'].items():assert digest(ARCHIVE/path)==expected
    files=[Path(__file__),HERE/'compose.py',HERE/'test_controls.py',ARCHIVE/'ARCHIVE.json',ROOT/'research/deferred-span-frames/independent_check.py']
    primary=ROOT/'references/signed-recursion/pr100/research/deferred-balanced'
    files += [primary/'moments.py']+list((primary/'arithmetic-sources').glob('*.py'))
    return dict(preserved_archive_files=len(manifest['files']),original_pr107_source_pins=len(original['files']),
                files={str(path.relative_to(ROOT)):digest(path)for path in files})

def generate(path):
    certificate=read(path);profiles,inputs=rebuild();result=validate(certificate,profiles,inputs)
    import test_controls
    negatives=test_controls.run(certificate,lambda c:validate(c,profiles,inputs))
    return dict(status='PASS',scope='Independent complete child lists, both stopped-recurrence moments, adapter saving, three-factor reserves, exact complex moment and balanced 47/7 arithmetic. Physical proofs/replay and analytic hypotheses remain separate.',
                certificate_sha256=digest(path),kappa=certificate['kappa'],complex_saving=certificate['complex']['saving'],
                **result,negative_controls=negatives,source_closure=sources())

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--certificate',type=Path,default=HERE/'certificate.json');parser.add_argument('--record',action='store_true');args=parser.parse_args()
    result=js(generate(args.certificate));path=HERE/'independent-audit.json'
    if args.record:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:assert result==read(path),'Independent pair-tree receipt changed'
    print('PASS independent stopped pair-tree: complete profiles, 3 reserves, 47 inequalities, 7 margins,',len(result['negative_controls']),'negative controls')
if __name__=='__main__':main()

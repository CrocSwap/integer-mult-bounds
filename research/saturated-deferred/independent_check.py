#!/usr/bin/env python3
"""Independently rebuild paid rows, bridge, moment bounds and all 47 slacks.

No primary composition or PR100 moment implementation is imported. Exact
40-term atanh and degree-ten exponential bounds and the independently written
balanced assembly transcription are retained from the deferred-span audit.
The full physical gate separately replays the supplied networks and geometry.
"""
import sys
if not __debug__:
    raise RuntimeError('Assertions required')
sys.dont_write_bytecode=True
import argparse,copy,gzip,hashlib,importlib.util,json
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from math import comb
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ARCHIVES=ROOT/'references/signed-recursion'
path=ROOT/'research/deferred-span-frames/independent_check.py'
spec=importlib.util.spec_from_file_location('saturated_independent_math',path)
audit=importlib.util.module_from_spec(spec);sys.modules[spec.name]=audit;spec.loader.exec_module(audit)
GRID=10**18
SCALE=10**40
def js(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {str(k):js(v)for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [js(v)for v in value]
    return value
def stable(value):
    if isinstance(value,dict):return {k:stable(v)for k,v in value.items()if k!='elapsed'}
    if isinstance(value,list):return [stable(v)for v in value]
    return value
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def normalized_hash(value):return hashlib.sha256(json.dumps(stable(value),sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(path):return json.loads(path.read_text())
def floorq(v):return Q(v.numerator*SCALE//v.denominator,SCALE)
def ceilq(v):return -floorq(-v)
@lru_cache(None)
def logarithm(value):
    lo,hi=audit.logarithm(value)
    return floorq(lo),ceilq(hi)
def moment(m,W,rows,saving):
    lo=hi=Q()
    for t,n in sorted(rows.items()):
        assert type(t)is int and type(n)is int and 0<t<m and n>0
        l,u=logarithm(Q(m,t));weight=Q(t*n,m*W)
        lo+=weight*floorq(audit.exponential(saving*l)[0])
        hi+=weight*ceilq(audit.exponential(saving*u)[1])
    return lo,hi
def inner(rank,h):
    assert 0<=rank<=h
    result=Counter()
    if 2*rank>h:
        result[1]=h-rank;result[2*rank-h]+=1
    elif rank:result[1]=rank
    return result
def add(H,profile,count):
    for r,n in profile.items():H[r]+=count*n

def rebuild():
    bit,cx,bridge=(read(HERE/file)for file in ('bit-ledger.json','complex-ledger.json','bridge.json'))
    with gzip.open(HERE/'schedule.json.gz','rt')as stream:schedule=json.load(stream)
    h,R=bit['h'],bit['roles'];v=comb(h,3);N=v*v;m=h*h;W=2*N+2*v*R
    assert (h,R)==(schedule['h'],schedule['R'])
    assert len(schedule['readout_order'])==len(set(schedule['readout_order']))==len(schedule['sigma'])
    sigmas=dict(zip(schedule['readout_order'],map(len,schedule['sigma'])))
    assert all(0<=s<R and 0<f<h for s,f in sigmas.items())
    parts={name:Counter()for name in ('literal_aux','literal_data','literal_center','exterior','staircase_data','rank_one_correction')}
    for name,hist in bit['rank_histograms'].items():
        for r,n in hist.items():add(parts['literal_'+name],inner(int(r),h),2*v*n)
    for s in range(R):
        r=h-sigmas.get(s,0);parts['exterior'][m-2*r]+=2*v;add(parts['exterior'],inner(r,h),2*v)
    parts['staircase_data'].update({m-4*h+2:2*N,h-2:2*N,h-5:2*N,1:12*N})
    parts['rank_one_correction'][1]=N
    H=sum(parts.values(),Counter());H={r:n for r,n in H.items()if n}
    assert H=={int(r):n for r,n in bit['histogram'].items()}
    assert sum(int(r)*n for r,n in bit['rank_histograms']['aux'].items())==h*R-sum(sigmas.values())
    assert sum(int(r)*n for r,n in bit['rank_histograms']['data'].items())==2*v*(h-1)
    assert sum(r*n for r,n in H.items())==bit['recursive_rank']==m*W-N+2*v*h*(h-1)
    profiles={'bit':dict(h=h,R=R,v=v,N=N,m=m,W=W,s=sum(r*n for r,n in H.items()),maxchild=max(H),child_multiplicities=H)}
    h,R=cx['h'],cx['roles'];v=comb(h,3);N=v*v;m=h*h;W=2*N+2*v*R;C=Counter()
    for hist in cx['internal_histograms'].values():
        for r,n in hist.items():C[int(r)]+=2*v*n
    C[m-h]+=2*v*R;C[(h-1)**2]+=2*N;C[1]+=N
    assert dict(C)=={int(r):n for r,n in cx['full_histogram'].items()}
    assert sum(r*n for r,n in C.items())==cx['recursive_rank']
    profiles['complex']=dict(h=h,R=R,v=v,N=N,m=m,W=W,s=sum(r*n for r,n in C.items()),maxchild=max(C),child_multiplicities=dict(C))
    return profiles,parts,dict(bit=bit,complex=cx,bridge=bridge)

def validate(certificate,profiles,inputs):
    assert certificate['input_normalized_sha256']=={k:normalized_hash(v)for k,v in inputs.items()}
    assert certificate['schedule_sha256']==digest(HERE/'schedule.json.gz')
    for name,p in profiles.items():
        for key,value in p.items():assert certificate[name][key]==js(value),(name,key)
    a=Q(certificate['bit_saving']);assert a==Q(certificate['bit']['saving'])
    reports={}
    for name,p in profiles.items():
        saving=Q(certificate[name]['saving']);lo,hi=moment(p['m'],p['W'],p['child_multiplicities'],saving)
        primary=certificate[name]['moment']
        assert Q(primary['saving'])==saving and Q(primary['lower'])<=lo<=hi<=Q(primary['upper'])<1
        assert set(primary['terms'])==set(map(str,p['child_multiplicities']))
        for r,n in p['child_multiplicities'].items():assert Q(primary['terms'][str(r)]['weight'])==Q(r*n,p['m']*p['W'])
        reports[name]=dict(lower=lo,upper=hi,strict_gap=1-hi)
    assert Q(certificate['bit']['next_saving'])==a+Q(1,GRID)
    p=profiles['bit'];lo,hi=moment(p['m'],p['W'],p['child_multiplicities'],a+Q(1,GRID))
    rejected=certificate['bit']['next_moment'];assert 1<Q(rejected['lower'])<=lo<=hi<=Q(rejected['upper'])
    reports['next_bit']=dict(lower=lo,upper=hi)
    bridge=certificate['assembly']['finite_bridge'];original=inputs['bridge']
    for name,p in profiles.items():
        for key in ('m','W','maxchild'):assert bridge[name][key]==p[key]
    p=profiles['complex'];updates=inputs['complex']['literal_scalar_updates_including_copied_scatter']
    G=2*p['v']*updates+4*p['h']*p['v']+4*p['N']
    assert original['literal_word_events']==updates and original['scalar_group_bound']==G==bridge['complex']['scalar_group_upper']
    assert bridge['complex']['s']==p['s']
    audit.check_bridge(bridge)
    bound,slacks,margins=audit.independent_assembly(certificate)
    assert bound>Q(certificate['kappa']) and bound<=Q(certificate['kappa'])+Q(1,GRID)
    assert certificate['next_kappa_grid_rejected']
    assert Q(certificate['improvement_over_pr100'])==Q(certificate['kappa'])-Q(certificate['previous_pr100_kappa'])>0
    return dict(moments=reports,minimum_margin=bound,strict_constraints=len(slacks),cost_margins=len(margins),
                rank_totals={name:p['s']for name,p in profiles.items()})

def sources():
    counts={};consumed=[]
    for name in ('pr97','pr99','pr100'):
        folder=ARCHIVES/name;manifest=read(folder/'ARCHIVE.json');assert set(manifest['files'])==set(manifest['git_blobs'])
        for path,expected in manifest['files'].items():
            blob=(folder/path).read_bytes();assert hashlib.sha256(blob).hexdigest()==expected
            assert hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()==manifest['git_blobs'][path]
        counts[name]=len(manifest['files']);consumed.append(folder/'ARCHIVE.json')
    original=ARCHIVES/'pr97';pins=read(original/'research/deferred-signed/SOURCE.json')['files']
    for path,expected in pins.items():assert digest(original/path)==expected,path
    foreign=original/'research/deferred-signed/swapnil-round7';imported=read(foreign/'IMPORT.json')['files']
    for path,expected in imported.items():assert digest(foreign/path)==expected,path
    assert (ROOT/'research/copied-fixed/balanced_assembly.py').read_bytes()==(ARCHIVES/'pr100/research/copied-fixed/balanced_assembly.py').read_bytes()
    consumed += [HERE/'compose.py',Path(__file__),ROOT/'research/deferred-span-frames/independent_check.py',
                 ROOT/'research/copied-fixed/balanced_assembly.py']
    return dict(archive_files=counts,original_source_pins=len(pins),foreign_import_pins=len(imported),
                files={str(p.relative_to(ROOT)):digest(p)for p in consumed})

def generate(certificate_path):
    certificate=read(certificate_path);profiles,parts,inputs=rebuild();result=validate(certificate,profiles,inputs)
    controls=[]
    variants=[]
    c=copy.deepcopy(certificate);c['bit']['child_multiplicities']['1']-=1;variants.append(('omitted_paid_singleton',c))
    c=copy.deepcopy(certificate);c['assembly']['finite_bridge']['bit']['halving_degree']=17;variants.append(('stale_halving_degree',c))
    c=copy.deepcopy(certificate);c['assembly']['finite_bridge']['rows']['degree']=2200;variants.append(('stale_row_stock',c))
    c=copy.deepcopy(certificate);c['assembly']['constraints']['g1_above_kappa']='1';variants.append(('falsified_assembly_slack',c))
    c=copy.deepcopy(certificate);c['bit']['moment']['upper']='0';variants.append(('falsified_moment_enclosure',c))
    c=copy.deepcopy(certificate);c['kappa']=str(Q(c['kappa'])+Q(1,GRID));variants.append(('adjacent_kappa_grid',c))
    c=copy.deepcopy(certificate);c['schedule_sha256']='0'*64;variants.append(('unbound_readout_schedule',c))
    for name,c in variants:
        try:validate(c,profiles,inputs)
        except (AssertionError,ValueError):controls.append(name)
        else:raise AssertionError('Corruption control accepted: '+name)
    # The old prefix work margin is a different physical transfer contract.
    # It must reject at these same balanced parameters, even though the
    # geometric constraint with the identical expression remains positive.
    p=certificate['assembly']['parameters']
    old_prefix=1-Q(p['epsilon'])*(1+Q(p['c']))
    assert 0<old_prefix<=Q(certificate['kappa'])
    controls.append('original_prefix_work_margin_at_balanced_parameters')
    return dict(status='PASS',scope='Independent paid-child reconstruction, rational moments, bridge, 47 inequalities, seven margins and source linkage. Geometry, complete dirty/phase replay and inherited uniform hypotheses remain separate.',
        certificate_sha256=digest(certificate_path),kappa=certificate['kappa'],bit_saving=certificate['bit_saving'],
        **result,bit_component_rank={name:sum(r*n for r,n in H.items())for name,H in parts.items()},
        negative_controls=controls,source_closure=sources())

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--certificate',type=Path,default=HERE/'certificate.json');parser.add_argument('--record',action='store_true');args=parser.parse_args()
    result=js(generate(args.certificate));path=HERE/'independent-audit.json'
    if args.record:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:assert result==read(path),'Independent receipt changed'
    print('PASS independent saturated audit: complete rows, exact moments, 47 inequalities, seven margins,',len(result['negative_controls']),'corruption controls')
if __name__=='__main__':main()

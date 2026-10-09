#!/usr/bin/env python3
"""Deterministic exact arithmetic for a supplied complete two-factor profile.

All mathematics uses integers/Fraction; no producer or foreign baseline runs.
Prepared with OpenAI Codex assistance. Inherited notices are retained in references.
"""
import argparse,ast,importlib.util,json,math,sys
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256,sha1
from pathlib import Path
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
import balanced_stopped as balanced
import interval_moment as intervals
HERE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:sha256(p.read_bytes()).hexdigest()
def check(ok,message):
    if not ok:raise ValueError(message)
def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [js(v) for v in x]
    return x
def exact(x):
    if isinstance(x,dict):return {k:exact(v) for k,v in x.items()}
    if isinstance(x,list):return [exact(v) for v in x]
    if isinstance(x,str) and '/' in x and all(s.lstrip('-').isdigit() for s in x.split('/')):return Q(x)
    return x
def no_floats(x,path=''):
    if isinstance(x,float):raise ValueError('Float forbidden at '+(path or '/'))
    if isinstance(x,dict):
        for k,v in x.items():
            check(type(k) is str,'Certificate key must be a string at '+path)
            no_floats(v,path+'/'+k)
    elif isinstance(x,(list,tuple)):
        for i,v in enumerate(x):no_floats(v,path+'/'+str(i))
    else:check(type(x) in (str,int,bool,type(None),Q),'Unsupported certificate value at '+path)
def profile(raw):
    p={key:raw[key] for key in ('h','v','m','N','L','R','W','total_rank','deficit','maxchild')}
    check(all(type(v) is int for v in p.values()),'Profile dimensions must be explicit integers')
    H=raw['child_multiplicities'];check(type(H) is dict,'Histogram object required')
    check(all(type(t) is str and t.isdigit() and t==str(int(t)) and type(n) is int for t,n in H.items()),'Canonical integer histogram required')
    p['child_multiplicities']=dict(sorted(H.items(),key=lambda z:int(z[0])))
    h,v,m,N,L,R,W=(p[k] for k in ('h','v','m','N','L','R','W'))
    check(h>=3 and R>0 and m==h*h and v==math.comb(h,3) and N==v*v and L==2*v*h*(h-1),'Two-factor dimensional identity')
    check(W==2*N+2*v*R and p['deficit']==N-L>0,'Role width or deficit identity')
    no_floats(p);intervals.prepare(p);return p
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def secondary():
    source=HERE/'references/pr100';arithmetic=module(source/'binary_frame_math.py','pinned_secondary_arithmetic')
    tree=ast.parse((source/'refine.py').read_text());wanted={'floor_scaled','ceiling_scaled','exact_moment'}
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in wanted];check({n.name for n in nodes}==wanted,'Frozen enclosure functions missing')
    env=dict(Q=Q,factorial=math.factorial,arithmetic=arithmetic)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source/'refine.py'),'exec'),env)
    return env['exact_moment']
def axis(p):
    m,W,r=(p[k] for k in ('m','W','maxchild'))
    return dict(m=m,W=W,maxchild=r,halving_degree=balanced.halving_degree(m,r),wire_bits=W.bit_length())
def bridge(bit,p,G,old):
    coarse,c=axis(bit),axis(p);m,W,s=(p[k] for k in ('m','W','total_rank'));E=64*(W+m+G+1)**3;B=s+E
    literal=2*G*W**2+8*s+4*W+4+32*m;c.update(s=s,scalar_group_upper=G)
    coeff=sum(x['halving_degree']*x['wire_bits'] for x in (coarse,c,old));degree=1000*((51*coeff)//25000+1)
    return dict(bit_coarse=coarse,complex=c,ordinary_leaf_row_degree=old['halving_degree']*old['wire_bits'],semantic=dict(E=E,B=B,C0=32*m*B**2,C1=1,literal_charge=literal,strict_literal_gap=E-literal,induction_gap=2*B*(m-p['maxchild'])-s-E,fixed_odd_divisor=21,exact_grid='Retain the common dyadic/21 grid and completed-child odd-denominator preservation.'),rows=dict(coefficient=coeff,degree=degree,degree_gap=Q(degree)-Q(51,25)*coeff,suffix_slope=4*degree,contract='W_complex^D_complex * W_coarse^D_coarse * W_old^D_old; all three simultaneous stocks retained.'))
def below(value,denominator):
    x=value*denominator;return Q(-((-x.numerator)//x.denominator)-1,denominator)
def source_hashes():
    provenance=read(HERE/'REFERENCE_PINS.json');no_floats(provenance)
    for name,record in provenance.items():
        data=(HERE/name).read_bytes();check(sha256(data).hexdigest()==record['sha256'],'Pinned source SHA changed: '+name)
        if 'git_blob' in record:check(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==record['git_blob'],'Pinned Git blob changed: '+name)
    names=['certificate.py','validate.py','balanced_stopped.py','interval_moment.py','REFERENCE_PINS.json','inputs/bit-profile.json','references/pr104/copied-centers-network.json','references/pr104/balanced_assembly.py','references/pr104/structured_bulk_assembly.py','references/pr100/refine.py','references/pr100/binary_frame_math.py']
    return {name:sha(HERE/name) for name in names}
def build(profile_path,bill_path):
    pins=source_hashes();raw=read(profile_path);p=profile(raw);bill=read(bill_path);G=bill['global_scalar_group_upper'];check(type(G) is int and G>0,'Scalar bill must be a positive integer')
    bit=profile(read(HERE/'inputs/bit-profile.json'));old_source=read(HERE/'references/pr104/copied-centers-network.json');old=old_source['finite_bridge']['bit'];old_saving=Q(old_source['bit']['saving'])
    check(old_saving==Q(384599,10**10),'Ordinary leaf saving changed');coarse=Q(620523,5*10**9);theta=Q(1,1000);A=(1-theta)*coarse+theta*old_saving
    check(0<old_saving<coarse<theta and A<theta,'Stopped atom ordering')
    bm=intervals.moment(bit,coarse,True);check(bm['upper']<1,'Coarse bit contraction')
    finite=bridge(bit,p,G,old);balanced.validate_bridge(finite,old)
    first=intervals.saving_grid(p);b=first['accepted']['saving'];bn=first['rejected']['saving'];second_fn=secondary();hist={int(t):n for t,n in p['child_multiplicities'].items()}
    second={label:second_fn(p['m'],p['W'],hist,a) for label,a in [('accepted',b),('rejected',bn)]}
    check(second['accepted']['upper']<1<second['rejected']['lower'],'Independent adjacent moment separation')
    for label in second:
        wide,narrow=second[label],first[label];check(wide['lower']<=narrow['lower']<=narrow['upper']<=wide['upper'],'Independent moment nesting')
        terms={x['child']:x for x in narrow['terms']}
        for t,x in wide['terms'].items():
            y=terms[t];check(x['log_lower']<=y['log_lower']<=y['log_upper']<=x['log_upper'],'Independent logarithm nesting');check(x['exp_lower']<=y['exp_lower']<=y['exp_upper']<=x['exp_upper'],'Independent exponential nesting')
    bm2=second_fn(bit['m'],bit['W'],{int(t):n for t,n in bit['child_multiplicities'].items()},coarse);check(bm2['upper']<1,'Independent coarse bit contraction')
    beta=eta=Q(1,10**24);backoff=Q(1,10**30);a=min(A,(1-beta)*b-backoff);q=a*(1-2*eta);k=below((1-eta)*q/(1+q),10**18)
    assembly=balanced.assembly(finite,old,a,k,beta=beta,h=eta,a_complex=b);check(len(assembly['constraints'])==47 and len(assembly['margins'])==7,'Assembly constraint coverage')
    def rejection(fn):
        try:fn()
        except balanced.InvalidAssembly as e:return str(e)
        raise ValueError('Invalid parameter accepted')
    next_rejection=rejection(lambda:balanced.assembly(finite,old,a,k+Q(1,10**18),beta=beta,h=eta,a_complex=b))
    old_rejection=rejection(lambda:balanced.assembly(finite,old,a,k,beta=beta,h=eta,a_complex=b,original_prefix=True))
    cap=min(A,bn)/(1+min(A,bn));check(cap<k+Q(1,10**18),'Entire fixed-profile next-grid exclusion')
    result=dict(certificate_schema='portable-stopped-balanced-v1',profile=p,bit_profile=bit,ordinary_leaf_bridge=old,ordinary_leaf_saving=old_saving,coarse_bit_saving=coarse,atom_exponent=theta,actual_bit_saving=A,bit_moment=bm,independent_bit_moment=bm2,finite_bridge=finite,complex_saving=b,next_complex_rejected=bn,first_moment=first,independent_moment=second,assembly_bit=a,beta=beta,eta=eta,backoff=backoff,kappa=k,assembly=assembly,cutoffs=balanced.cutoffs(finite,old,assembly),next_kappa=k+Q(1,10**18),next_kappa_rejection=next_rejection,old_prefix_rejection=old_rejection,fixed_profile_family_ceiling=cap,grid_optimality=True,input_sha256=dict(raw_complex_profile=sha(profile_path),scalar_bill=sha(bill_path)),source_sha256=pins,raw_discovery_metadata_in_certificate=False,scope='Exact arithmetic on the supplied complete physical profile. Physical source/dirty/reflection identities, paid positional layout, all-size interfaces and fixed-tape analytic transfer remain separately verified or inherited obligations. Grid optimality is only within this fixed-profile balanced transfer family.')
    check(pins==source_hashes(),'Arithmetic source drift during generation');public=js(result);no_floats(public);return public

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--profile',type=Path,required=True);ap.add_argument('--scalar-bill',type=Path,required=True);ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--record',action='store_true');args=ap.parse_args()
    result=build(args.profile,args.scalar_bill)
    if args.record:
        args.certificate.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n');check(read(args.certificate)==result,'Saved certificate roundtrip')
    else:check(read(args.certificate)==result,'Recorded certificate differs from exact recomputation')
    no_floats(read(args.certificate));print('PASS exact certificate; kappa='+result['kappa']+'; sha256='+sha(args.certificate))
if __name__=='__main__':main()

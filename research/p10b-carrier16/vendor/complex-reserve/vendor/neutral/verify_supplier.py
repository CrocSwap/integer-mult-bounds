#!/usr/bin/env python3
"""Source-bound research supplier admission; never modifies the published supplier.
Uses byte-pinned PR315 primary inputs and checkers. Adaptations to pin predicates
are fully logged in portable-code/DERIVATION.json. AI-assisted by OpenAI Codex.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
import argparse,collections,gzip,hashlib,importlib.util,json,pathlib,time
from fractions import Fraction as Q
from frame_retime import ROOT,SOURCE,scalar_flat
HERE=pathlib.Path(__file__).resolve().parent

def load(path,name):
    sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def serial(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):serial(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [serial(v) for v in x]
    return x

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=pathlib.Path,required=True);ap.add_argument('--expected-sha256',required=True)
    args=ap.parse_args();begun=time.time();raw=args.input.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha==args.expected_sha256
    c=json.loads(raw);baseline=json.loads(gzip.decompress(SOURCE.read_bytes()))
    assert hashlib.sha256(gzip.decompress(SOURCE.read_bytes())).hexdigest()=='91c349b9680b023449d3bc4fb58f00a22c9d9f38b776ae3a3597259431de78eb'
    for p in ('A','B'):assert scalar_flat(c[p])==scalar_flat(baseline[p])
    for key in ('ports','start','final','ret','scat','ext','h','v','R','cst','N'):assert c[key]==baseline[key]
    pins=json.loads((ROOT/'inputs/complex/source-pins.json').read_text());verified={};upstream={}
    for rel,pin in pins['files'].items():
        path=ROOT/rel;assert hashlib.sha256(path.read_bytes()).hexdigest()==pin['sha256'];verified[rel]=pin['sha256'];upstream[pin['upstream']]=path
    deriv=json.loads((HERE/'portable-code/DERIVATION.json').read_text())
    for name,d in deriv.items():
        assert hashlib.sha256((ROOT/d['source']).read_bytes()).hexdigest()==d['source_sha256']
        assert hashlib.sha256((HERE/'portable-code'/(name+'.py')).read_bytes()).hexdigest()==d['derived_sha256']
    mods={name:load(HERE/'portable-code'/(name+'.py'),'research_'+name) for name in deriv}
    H=collections.Counter()
    for w in c['blocks'].values():H.update({int(r):n for r,n in w.items()})
    checks=mods['complex_labels'].replay_label_counts(c,dict(frames=len(c['frames']),gates={p:len(c[p]) for p in ('A','B')},histogram=dict(H)))
    H5=collections.Counter({r:5*n for r,n in H.items()});h,v,R=c['h'],c['v'],c['R'];m=5*h;W=4*v+R
    for r in (2*h-2,h-1,2*h+2,4):H5[r]+=2*v
    ledger=dict(histogram={str(r):n for r,n in sorted(H5.items())},calls=sum(H5.values()),rank_mass=sum(r*n for r,n in H5.items()),
                max_child=max(H5),deficit=m*W-sum(r*n for r,n in H5.items()),copy_calls=5*h,idle_calls=8*v)
    assert ledger['rank_mass']==1571680 and ledger['deficit']==3080 and ledger['max_child']==46
    lines=upstream['Work/GCert/Chain/NetDef.lean'].read_text().splitlines();refs={}
    for name in ['x01','y01','x12','y12','x23','y23','x34','y34','sfin','term']:
        indices=[i for i,line in enumerate(lines) if name+' :' in line];assert indices;i=indices[-1] if name=='sfin' else indices[0]
        refs[name]=dict(source='Work/GCert/Chain/NetDef.lean',anchor=name+' :',line=i+1,
            declaration_line=' '.join(x.strip() for x in lines[i:i+(2 if name=='sfin' else 1)]),
            url='https://github.com/jacobalansussman/wht-power-saving-lean/blob/'+mods['portable_complex'].PIN+'/Work/GCert/Chain/NetDef.lean#L'+str(i+1))
    manifest=dict(source_pin=mods['portable_complex'].PIN,parameters=dict(h=h,m=m,v=v,R=R,W_live=W,invocation_live=2*v+R),
                  ledger=ledger,checks=checks,chronology=mods['portable_complex'].CHRONOLOGY,source_frame_equalities=refs)
    scalar=mods['complex_scalars'];splice=mods['complex_splice'];A=scalar.flat(c['A']);B=scalar.flat(c['B']);bill={};life={};programs={};controls=[]
    for ori in ('forward','backward'):
        bill[ori]=scalar.bill(scalar.inv_schedule(ori,A,B,c));life[ori]=scalar.lifecycle(scalar.inv_schedule(ori,A,B,c))
        original=scalar.bill(scalar.inv_schedule(ori,scalar.flat(baseline['A']),scalar.flat(baseline['B']),baseline))
        assert bill[ori]==original,'full derived dirty/main/cleanup scalar program changed'
        events=list(splice.emit(c,ori));programs[ori]=splice.validate(events,c,ori,manifest,bill);controls.extend(splice.controls(events,c,ori,manifest,bill))
    assert (bill['forward']['totals']['real_component_primitive_steps'],bill['backward']['totals']['real_component_primitive_steps'])==(1735572,1789788)
    global_contract=splice.global_contract(manifest);splice.validate_global(global_contract,manifest)
    guard=mods['portable_complex'].finite_guard(manifest,bill,mods['complex_basis'])
    print('PASS both reflected complete scalar splices, dirty word equality, paid ledgers and finite guard',flush=True)
    cost=load(ROOT/'moment.py','research_moment');other=load(ROOT/'base_two_moment.py','research_base2');grid=Q(1,10**18)
    roots={}
    for fallback in (True,False):
        root=cost.certify(dict(H5),m,W,fallback);b=Q(int(Q(root['lower'])*10**18),10**18)
        interval=cost.moment(dict(H5),m,W,b,fallback);excluded=cost.moment(dict(H5),m,W,b+grid,fallback);assert interval[1]<1<excluded[0]
        lo,hi=other.moment(m,W,list(H5.items()),b);nlo,nhi=other.moment(m,W,list(H5.items()),b+grid)
        if fallback:
            calls=32*m*m*sum(H5.values());a,z=other.moment(m,W,[(1,calls)],b);na,nz=other.moment(m,W,[(1,calls)],b+grid)
            lo+=Q(1,10**16)*a;hi+=Q(1,10**16)*z;nlo+=Q(1,10**16)*na;nhi+=Q(1,10**16)*nz
        assert hi<1<nlo
        roots['with_fallback' if fallback else 'without_fallback']=dict(b=b,moment_interval=interval,next_grid_excluded=excluded,independent_moment_interval=(lo,hi),independent_next_grid=(nlo,nhi))
    print('PASS both exact rational moment engines and adjacent-grid controls',flush=True)
    gx=mods['complex_gx'].check(ROOT,raw)
    result=dict(status='PASS_RESEARCH_COMPLEX_SUPPLIER_FRAME_RETIMING',source_sha256='91c349b9680b023449d3bc4fb58f00a22c9d9f38b776ae3a3597259431de78eb',
                candidate_sha256=sha,unchanged_scalar_program=True,unchanged_scatter_ports_endpoints=True,source_pins=verified,
                parameterization_derivation=deriv,labels=checks,ledger=ledger,scalar_bill=bill,scratch_lifetimes=life,reflected_splices=programs,
                mutation_controls=controls,global_contract=global_contract,finite_guard=guard,roots=roots,gx_check=gx,seconds=time.time()-begun,
                scope='Research supplier improvement only. Dirty lifting, exact frame geometry, finite cover and outer assembly interfaces inherited from byte-pinned PR315 sources. No new Lean run; no kappa claim; bit supplier still binds.')
    (args.input.parent/'SUPPLIER-CHECK.json').write_text(json.dumps(serial(result),indent=2)+'\n')
    print(json.dumps(serial({k:result[k] for k in ('status','candidate_sha256','ledger','roots','seconds')}),indent=2))

if __name__=='__main__':main()

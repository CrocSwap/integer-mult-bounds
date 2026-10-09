#!/usr/bin/env python3
"""Exact paid moment refinement and six-level finite composition on the pinned PR230 plateau word.

Copyright 2026 Gabriele Nespoli. Apache-2.0. Developed with OpenAI Codex.
Finite completed-leaf composition: PR185/187/197; word and bank audit: PR210/230.
"""
import argparse,copy,importlib.util,json,subprocess,sys
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
HERE=Path(__file__).resolve().parent
DEPTH=6;GRID=10**24;COARSE_GRID=10**27
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
sys.dont_write_bytecode=True

def require(ok,message):
    if not ok:raise ValueError(message)
def digest(path):return sha256(path.read_bytes()).hexdigest()
def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [js(v) for v in x]
    return x
def pins(folder,root):
    manifest=json.loads((folder/'SOURCE.json').read_text())
    actual={p.relative_to(root).as_posix():digest(p) for p in root.rglob('*') if p.is_file() and p.name!='SOURCE.json'}
    require(actual==manifest['files'],'Source drift: '+str(folder))
    return actual
def point(bound,denominator=GRID):
    z=bound*denominator
    return Q((z.numerator-1)//z.denominator,denominator)

def validate_step(level,predecessor,coarse,previous,value,atom):
    require(type(level) is int and 1<=level<=DEPTH,'Invalid fixed level')
    require(predecessor==level-1 and predecessor<level,'Cyclic ordinary callback')
    require(value==(1-coarse)*coarse+coarse*previous,'Detached saving')
    require(0<previous<value<coarse<1-value,'Unpaid finite wrapper toll')
    require(atom==coarse and atom>value and atom<1-value,'Unpaid atom or row toll')

def refined_coarse(parent,source,old):
    def load(name,path):
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
    im=load('retained_paid_moment',source/'research/paired-cube-diagonal-bit-168/arithmetic/interval_moment.py')
    alt=load('independent_paid_moment',parent/'geometry/base_two_moment.py')
    row=old['bit_profile'];hist=[(int(t),n) for t,n in row['child_multiplicities'].items()]
    require(all(0<t<row['m'] and n>0 for t,n in hist),'Nonmonotone paid profile')
    fallback=[(1,32*row['m']**2*sum(n for _,n in hist))]
    def public(a):
        value=im.moment(row,a);l,u=im.log_interval(Q(row['m']));e,f=im.exp_interval(a*l,a*u)
        bill=Q(1,10**16)*Q(32*row['m']*sum(row['child_multiplicities'].values()),row['W'])
        return value['lower']+bill*e,value['upper']+bill*f
    def independent(a):
        l,u=alt.moment(row['m'],row['W'],hist,a)
        fl,fu=alt.moment(row['m'],row['W'],fallback,a)
        return l+Q(1,10**16)*fl,u+Q(1,10**16)*fu
    original=Q(old['bit']['saving']);lo=int(original*COARSE_GRID);hi=lo+COARSE_GRID//10**18
    require(public(Q(lo,COARSE_GRID))[1]<1<public(Q(hi,COARSE_GRID))[0],'Parent coarse bracket failed')
    while hi-lo>1:
        mid=(lo+hi)//2;l,u=public(Q(mid,COARSE_GRID))
        if u<1:lo=mid
        elif l>1:hi=mid
        else:raise ValueError('Inconclusive paid moment enclosure')
    accepted=Q(lo,COARSE_GRID);excluded=Q(hi,COARSE_GRID)
    pa=public(accepted);pe=public(excluded);ia=independent(accepted);ie=independent(excluded)
    require(original<accepted<excluded<=original+Q(1,10**18),'No certified coarse improvement')
    require(pa[1]<1<pe[0] and ia[1]<1<ie[0],'Independent paid fine-grid bracket failed')
    return accepted,dict(grid=COARSE_GRID,saving=accepted,next_saving=excluded,
        public_accepted=dict(lower=pa[0],upper=pa[1]),public_excluded=dict(lower=pe[0],upper=pe[1]),
        independent_accepted=dict(lower=ia[0],upper=ia[1]),independent_excluded=dict(lower=ie[0],upper=ie[1]),
        rare_class_weight=Q(1,10**16),fallback_child_histogram=fallback,
        unchanged_profile_sha256=sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest())

def arithmetic(parent,complex_root):
    original=json.loads((parent/'certificate.json').read_text())
    old=original;parent_coarse=Q(old['bit']['saving']);base=Q(old['ordinary_chain'][0])
    coarse,refinement=refined_coarse(parent,complex_root,old)
    require(len(old['ordinary_chain'])==5,'Wrong completed parent chain')
    paid=json.loads((complex_root/'research/coordinated-crossover-pr200/joint/joint-paid.json').read_text())
    require(base==Q(paid['coarse']['ordinary_saving']) and parent_coarse==Q(paid['coarse']['coarse_saving']),'Detached completed base supplier')
    banks=json.loads((complex_root/'research/coordinated-crossover-pr200/joint/joint-banks.json').read_text())
    require(banks['conservative_extra_selector_calls']==178127441712<2**40,'Selector bill changed')
    b=Q(old['complex']['saving']);eta=beta=Q(1,10**24);weak=Q(1,10**30)
    require(0<base<coarse<Q(1,2),'Invalid completed base supplier')
    require(Q(old['bit']['accepted']['upper'])<1<Q(old['bit']['next_excluded']['lower']), 'Paid bit contraction changed')
    require(Q(old['complex']['accepted']['upper'])<1<Q(old['complex']['next_excluded']['lower']), 'Complex contraction changed')
    source=json.loads((complex_root/'research/source-assisted-v4/certificate.json').read_text())
    bridge=copy.deepcopy(source['assembly']['finite_bridge'])
    bridge['rows']['degree_gap']=Q(bridge['rows']['degree_gap'])
    spec=importlib.util.spec_from_file_location('retained_paid_assembly',complex_root/'scripts/paired_cube_assembly.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    chain=[base];steps=[]
    for j in range(1,DEPTH+1):
        previous=chain[-1];value=(1-coarse)*coarse+coarse*previous
        validate_step(j,j-1,coarse,previous,value,coarse)
        require(value==coarse-coarse**j*(coarse-base),'Closed-form recurrence differs')
        # All uses of an ordinary leaf in A_j call only completed A_(j-1).
        steps.append(dict(level=j,ordinary_predecessor=j-1,saving=value,
            atom_exponent=coarse,coarse_term_saving=coarse,
            leaf_term_saving=(1-coarse)*coarse+coarse*previous,
            atom_toll_gap=coarse-value,row_toll_gap=1-value-coarse,
            coarse_atom_count_strictly_decreases=True,inherited_completed_restoration=True))
        chain.append(value)
    parent_chain=[base]
    for _ in range(4):parent_chain.append((1-parent_coarse)*parent_coarse+parent_coarse*parent_chain[-1])
    require(parent_chain==list(map(Q,old['ordinary_chain'])),'PR230 four-level hierarchy changed')
    def assemble(value,grid=GRID):
        a=min(value,(1-beta)*b-weak);q=a*(1-2*eta);bound=(1-eta)*q/(1+q);k=point(bound,grid)
        audit=module.assembly(a,b,bridge,k,eta=eta,beta=beta)
        require(len(audit['strict_constraints'])==47 and len(audit['margins'])==7,'Incomplete assembly')
        require(a<=value and coarse<1-value,'Supplier or selector toll omitted')
        try:module.assembly(a,b,bridge,k+Q(1,grid),eta=eta,beta=beta)
        except AssertionError:pass
        else:raise ValueError('Next exponent grid point accepted')
        return dict(kappa=k,bound=bound,assembly=audit)
    previous=assemble(parent_chain[4]);old_grid=assemble(parent_chain[4],10**18)
    require(old_grid['kappa']==Q(old['kappa']),'Published comparator changed')
    result=assemble(chain[-1]);require(result['kappa']>previous['bound'],'No gain over unrounded four-level construction')
    fifth=assemble(chain[5]);require(result['kappa']>fifth['kappa'],'Sixth level gives no reported improvement')
    refined_fourth=assemble(chain[4]);require(result['kappa']>refined_fourth['bound'],'No finite gain over refined four-level bound')
    # A_j < c for every finite j. This is only a monotone upper bound;
    # the claim is attained by A_6, never by an infinite-depth oracle.
    cap_a=min(coarse,(1-beta)*b-weak);cap_q=cap_a*(1-2*eta)
    family_bound=(1-eta)*cap_q/(1+cap_q)
    require(result['kappa']==point(family_bound),'Six levels do not reach the chosen family grid cap')
    excluded_a=min(refinement['next_saving'],(1-beta)*b-weak);excluded_q=excluded_a*(1-2*eta)
    excluded_family_bound=(1-eta)*excluded_q/(1+excluded_q)
    require(result['kappa']==point(excluded_family_bound),'Paid root bracket leaves another final grid point unresolved')
    controls={}
    for name,pred,value,atom in [('cyclic level',DEPTH,chain[-1],coarse),
          ('coarse saving as finite ordinary leaf',DEPTH-1,coarse,coarse),
          ('unpaid atom exponent',DEPTH-1,chain[-1],chain[-1])]:
        try:validate_step(DEPTH,pred,coarse,chain[-2],value,atom)
        except ValueError:controls[name]='REJECTED'
        else:raise ValueError('Invalid composition control accepted')
    return js(dict(status='PASS conditional paid fine-grid coarse saving and finite six-level composition',depth=DEPTH,grid=GRID,
        kappa=result['kappa'],previous_published_kappa=old_grid['kappa'],
        previous_matched_kappa=previous['kappa'],five_level_kappa=fifth['kappa'],sixth_level_gain=result['kappa']-fifth['kappa'],gain=result['kappa']-old_grid['kappa'],
        matched_gain=result['kappa']-previous['kappa'],refined_four_level_kappa=refined_fourth['kappa'],coarse_grid_gain=refined_fourth['kappa']-previous['kappa'],finite_depth_gain=result['kappa']-refined_fourth['kappa'],coarse_saving=coarse,parent_coarse_saving=parent_coarse,paid_coarse_refinement=refinement,
        completed_base_saving=base,complex_saving=b,ordinary_chain=chain,steps=steps,
        assembly=result['assembly'],minimum_margin=result['bound'],next_grid_excluded=True,
        family_upper_only=family_bound,paid_excluded_family_upper_only=excluded_family_bound,six_levels_attain_family_grid_cap=True,
        selector_calls=banks['conservative_extra_selector_calls'],previous_unrounded_bound=previous['bound'],unchanged_profiles_sha256=sha256(json.dumps([original['bit_profile'],original['complex_profile']],sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        finite_bridge_sha256=sha256(json.dumps(js(bridge),sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        controls=controls,scope='Paid bit moment refined at fixed full fallback; six fixed acyclic completed ordinary suppliers; unchanged words, banks, charts, selector bill and finite complex bridge. All-size interfaces remain the retained assumptions.'))

def main():
    import io,zipfile,tempfile,shutil
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent-root',type=Path,required=True)
    p.add_argument('--write',action='store_true',help='Author certificate before source freeze')
    args=p.parse_args();require(not sys.flags.optimize,'Run without -O')
    own=None if args.write else pins(HERE,HERE)
    root=args.parent_root.resolve();parent=root/'research/coordinated-crossover-pr200'
    prerequisite=json.loads((HERE/'prerequisite.json').read_text())
    require(subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==prerequisite['commit'],'Wrong prerequisite commit')
    require(digest(parent/'FILES.json')==prerequisite['manifest_sha256'],'Wrong parent manifest')
    print('Replaying the entire immutable parent finite certificate.',flush=True)
    manifest=json.loads((parent/'FILES.json').read_text())['files']
    def parent_pins():
        actual={p.relative_to(parent).as_posix():digest(p) for p in parent.rglob('*') if p.is_file() and p.name!='FILES.json'}
        require(actual==manifest,'Parent upload source drift');return actual
    before=parent_pins()
    baseline=json.loads((parent/'BASELINE.json').read_text());parts=[]
    for entry in baseline['parts']:
        path=parent/entry['file']
        require(path.stat().st_size==entry['bytes'] and digest(path)==entry['sha256'],'Archive part drift')
        parts.append(path.read_bytes())
    blob=b''.join(parts);require(sha256(blob).hexdigest()==baseline['archive_sha256'],'Archive drift')
    with tempfile.TemporaryDirectory(prefix='finite-bootstrap-') as tmp:
        source=Path(tmp)/'source';source.mkdir()
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            for entry in z.infolist():require((source/entry.filename).resolve().is_relative_to(source.resolve()),'Unsafe archive entry')
            z.extractall(source)
        package=source/'research/coordinated-crossover-pr200'
        # PR230's search re-extracts the baseline. Retain its archive parts too.
        shutil.copytree(parent,package)
        subprocess.run([sys.executable,'-B',str(package/'verify_inner.py')],check=True)
        result=arithmetic(parent,source)
    require(parent_pins()==before and digest(parent/'FILES.json')==prerequisite['manifest_sha256'],'Parent changed during replay')
    result['prerequisite']=prerequisite
    target=HERE/'certificate.json'
    if args.write:target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:
        require(result==json.loads(target.read_text()),'Certificate does not reproduce')
        require(pins(HERE,HERE)==own,'Source changed during replay')
    print('PASS kappa='+result['kappa'])
if __name__=='__main__':main()

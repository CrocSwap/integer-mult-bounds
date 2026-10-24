#!/usr/bin/env python3
"""Fresh complex label, scalar, splice and finite-guard checks from primary inputs.
No saved PASS receipts, workstation paths, network or Lean rebuild are required.
p = 10 packages: the complex program itself is admitted by Sussman's gx.check1 with the exact scalar identity and by
his gxcore mirror (code/complex_gx.py), added by DreamingOfClouds with Anthropic Claude assistance.
E8 package: the scatter (table or star rule), the number of retained totals and each centre child's rank are read
from the certificate (code/scatter.py) instead of the paired-cube star rule with h centres of rank h - 2.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from math import prod
from pathlib import Path
import gzip, importlib.util, json, sys, os
sys.dont_write_bytecode = True
sys.path.insert(0,str(Path(__file__).resolve().parent/'code'))
from p10pins import PINS, pin, RECORD

PIN='f010392c923279e3dd59ef3aa5fedad23affc5fd'
CHRONOLOGY=['stage0','stage1','climbA','bridgeA','stage2','climbB','bridgeB','stage3','stage4','final_climbs','bridgeC','terminal_shifts','signed_exchange']

def need(ok, why):
    if not ok: raise ValueError(why)

def module(root, name):
    spec=importlib.util.spec_from_file_location('portable_'+name,root/'code'/(name+'.py'))
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result

def finite_guard(m, b, basis):
    p=m['parameters'];l=m['ledger'];dim=p['m'];R=p['R'];h=p['h'];W=p['W_live']
    need((dim,R,h,W)==(5*PINS['H'],PINS['R'],PINS['H'],4*PINS['V']+PINS['R']),'complex family changed')
    scalar=max(b[o]['totals']['real_component_primitive_steps'] for o in ['forward','backward'])
    macros=max(b[o]['totals']['scalar_macros'] for o in ['forward','backward'])
    scalar5=3*b['forward']['totals']['real_component_primitive_steps']+2*b['backward']['totals']['real_component_primitive_steps']
    physical=W+R+h+1
    adapters=8*(macros+m['checks']['invocation_calls']+p['invocation_live']+h)+32*dim
    outside=8*(l['idle_calls']+6*p['v']+physical)+32*dim
    compiler=64*(dim+1)**3
    local=scalar+adapters*compiler
    pervertex=scalar5+12*p['v']+(5*adapters+outside)*compiler+64*physical
    group=(1<<(dim-1+(dim//2-1)**2))*prod((1<<(2*i))-1 for i in range(1,dim//2))
    live_stock=group*W;physical_stock=group*physical;s=group*l['rank_mass']
    K=group*pervertex+64;router=compiler*(K+1)*(physical_stock+1)**2
    G,E,C0=1<<30000,1<<100000,1<<210000;B=s+E
    literal=2*G*physical_stock**2+8*s+4*physical_stock+4+32*dim
    pin('local_bill',local,'fresh local/global bill');need(local<1<<48 and K<1<<6050,'fresh local/global bill')
    pin('stock_bits',[group.bit_length(),live_stock.bit_length(),physical_stock.bit_length(),s.bit_length()],'fresh cover/work stock')
    need(router<G and literal<E and B<1<<100001,'fresh router/literal guard')
    induction=2*(dim-l['max_child'])-1;need(2*B*(dim-l['max_child'])-s-E==induction*B and induction>=1,'completed-child induction')
    need(32*dim*B*B<C0 and 2*B+18<C0 and 2*l['max_child']<dim,'semantic and half-shrink guard')
    row=live_stock.bit_length()+9909+252;rowphysical=physical_stock.bit_length()+9909+252
    need(row<=rowphysical<20161,'external rows')
    gap=Q(10**6)-Q(51,25)*20161;need(gap>0,'row reserve gap')
    need(2*(dim*(dim-1)+3*dim+dim+3*dim*(dim-1)//2+dim+1)+2*dim<compiler,'explicit quadratic-phase lowering')
    for e in range(1,100001):need((e-1).bit_length()+1<=2*e,'grid-depth endpoint')
    def validate(c):
        need(c['physical']==c['live']+R+h+1,'missing work stock')
        need(dim*c['live']-l['rank_mass']==l['deficit'],'wrong live normalization')
        need(c['copy_calls']==5*l['centres'],'missing center child')
        need(c['denominators']==[1,2,3,6],'unrecorded denominator')
        need(physical_stock<1<<c['stock_exponent'],'false stock bound')
    original=dict(physical=physical,live=W,copy_calls=5*l['centres'],denominators=[1,2,3,6],stock_exponent=physical_stock.bit_length())
    validate(original);controls={}
    for name,key,value in [('missing_tableau','physical',physical-R),('scratch_in_live','live',physical),('dropped_center','copy_calls',5*l['centres']-1),('unrecorded_divisor','denominators',[1,2,3,5,6]),('stale_stock_bound','stock_exponent',physical_stock.bit_length()-801)]:
        bad=dict(original);bad[key]=value
        try:validate(bad)
        except ValueError:controls[name]=True
        else:raise ValueError('finite guard mutation accepted: '+name)
    return dict(status='PASS_FRESH_EXACT_COMPLEX_GUARD',m=dim,live_per_vertex=W,physical_per_vertex=physical,
        coefficient_denominators=[1,2,3,6],semantic_C1=1,complete_local_group_upper=local,
        complete_local_group_bits=local.bit_length(),global_logical_groups_bits=K.bit_length(),
        simple_global_logical_bound_exponent=6050,router_bits=router.bit_length(),G_exponent=30000,
        literal_charge_bits=literal.bit_length(),E_exponent=100000,required_C0_bits=(32*dim*B*B).bit_length(),
        C0_exponent=210000,induction_gap_multiple_of_B=induction,group_bits=group.bit_length(),
        live_stock_bits=live_stock.bit_length(),physical_stock_bits=physical_stock.bit_length(),
        rank_mass_bits=s.bit_length(),live_row_coefficient=row,physical_row_overcharge_coefficient=rowphysical,
        retained_row_coefficient=20161,retained_row_gap=str(gap),controls=controls,
        binary_basis_count_tests=basis.gl_count_test(),
        odd_denominator_grid='2^(-P)3^(-G(D+1)); no return rounding')

def run(package_root=None, progress=lambda text:None):
    root=Path(package_root).resolve() if package_root else Path(__file__).resolve().parent
    labels=module(root,'complex_labels');scalar=module(root,'complex_scalars')
    splice=module(root,'complex_splice');basis=module(root,'complex_basis')
    pinpath=Path(os.environ['CX_SOURCE_PINS']) if os.environ.get('CX_SOURCE_PINS') else root/'inputs/complex/source-pins.json'
    if not pinpath.is_file():pinpath=root/'inputs/complex-source-pins.json'
    pins=json.loads(pinpath.read_text());verified={};by_upstream={}
    for relative,spec in pins['files'].items():
        path=root/relative;got=sha256(path.read_bytes()).hexdigest()
        need(got==spec['sha256'],'primary proof input changed: '+relative)
        verified[relative]=got;by_upstream[spec['upstream']]=(path,spec)
    cp=pins['certificate'];z=(root/cp['path']).read_bytes()
    need(sha256(z).hexdigest()==cp['compressed_sha256'],'compressed certificate binding')
    raw=gzip.decompress(z);need(sha256(raw).hexdigest()==cp['uncompressed_sha256'],'expanded certificate binding')
    verified[cp['path']]=sha256(z).hexdigest();c=json.loads(raw)
    progress('Checking the complex program: gx.check1 with the exact scalar identity, and the gxcore mirror.')
    program_check=module(root,'complex_gx').check(root,raw)
    progress('Checking every complex source label and paid child.')
    checks=labels.replay_label_counts(c)
    H=Counter({int(k):5*n for k,n in checks['invocation_histogram'].items()})
    v,R,h=c['v'],c['R'],c['h'];dim=5*h;W=4*v+R
    for rank in [2*h-2,h-1,2*h+2,4]:H[rank]+=2*v
    ledger=dict(histogram={str(k):n for k,n in sorted(H.items())},calls=sum(H.values()),
        rank_mass=sum(k*n for k,n in H.items()),max_child=max(H),deficit=dim*W-sum(k*n for k,n in H.items()),
        copy_calls=5*len(c['ret']),centres=len(c['ret']),idle_calls=8*v)
    pin('ledger',[ledger['calls'],ledger['rank_mass'],ledger['deficit'],ledger['max_child']],'fresh five-stage ledger');need(ledger['deficit']==dim*W-ledger['rank_mass'],'ledger deficit')
    source_path,source_spec=by_upstream['Work/GCert/Chain/NetDef.lean'];lines=source_path.read_text().splitlines();refs={}
    for name in ['x01','y01','x12','y12','x23','y23','x34','y34','sfin','term']:
        indices=[i for i,line in enumerate(lines) if name+' :' in line];need(indices,'missing exact matrix field '+name)
        i=indices[-1] if name=='sfin' else indices[0]
        text=' '.join(x.strip() for x in lines[i:i+(2 if name=='sfin' else 1)])
        refs[name]=dict(source='Work/GCert/Chain/NetDef.lean',anchor=name+' :',line=i+1,declaration_line=text,
            url='https://github.com/jacobalansussman/wht-power-saving-lean/blob/'+PIN+'/Work/GCert/Chain/NetDef.lean#L'+str(i+1))
    m=dict(source_pin=PIN,parameters=dict(h=h,m=dim,v=v,R=R,W_live=W,invocation_live=2*v+R),
        ledger=ledger,checks=checks,chronology=CHRONOLOGY,source_frame_equalities=refs)
    progress('Deriving both complex scalar words and temporary lifetimes.')
    A=scalar.flat(c['A']);B=scalar.flat(c['B']);b={};life={}
    for orientation in ['forward','backward']:
        b[orientation]=scalar.bill(scalar.inv_schedule(orientation,A,B,c))
        life[orientation]=scalar.lifecycle(scalar.inv_schedule(orientation,A,B,c),c)
    pin('scalar_steps',[b['forward']['totals']['real_component_primitive_steps'],b['backward']['totals']['real_component_primitive_steps']],'fresh scalar expansion')
    b['scratch_lifecycle_checks']=life;b['template_tests']=scalar.toy_checks()
    b['five_invocation_scalar_primitives_per_vertex']=3*b['forward']['totals']['real_component_primitive_steps']+2*b['backward']['totals']['real_component_primitive_steps']
    b['scratch']=dict(live_roles=W,physical_roles_per_cover=W+R+h+1,additional_recursive_calls=0,extra_external_row_coordinate=False)
    progress('Merging scalar events, exact frames and all final climbs.')
    programs={};controls=[]
    for orientation in ['forward','backward']:
        events=list(splice.emit(c,orientation));programs[orientation]=splice.validate(events,c,orientation,m,b)
        controls.extend(splice.controls(events,c,orientation,m,b))
    g=splice.global_contract(m);splice.validate_global(g,m)
    mutations=[('wrong_helper_owner',lambda x:x['stage_recipe'][1].__setitem__('helper_owner','s1^(-1)(d)')),
        ('rank_only_frame',lambda x:x['exact_frame_bindings']['x23'].__setitem__('declaration_line','same rank only')),
        ('scratch_alias',lambda x:x['scratch_namespace'].__setitem__('centers',[W-1,W+h-1])),
        ('wrong_live_normalization',lambda x:x.__setitem__('recursive_volume_denominator',W+R+h+1)),
        ('free_RAM',lambda x:x.__setitem__('primitive_policy','free_RAM')),
        ('missing_tableau',lambda x:x.__setitem__('physical',W+h+1))]
    for name,fn in mutations:
        bad=deepcopy(g);fn(bad)
        try:splice.validate_global(bad,m)
        except ValueError as error:controls.append(dict(name=name,rejected=True,reason=str(error)))
        else:raise ValueError('global mutation accepted: '+name)
    progress('Recomputing complex cover, router, precision and row inequalities.')
    precision=finite_guard(m,b,basis)
    need(labels.scalar_word([(1,0,1),(0,1,-1),(0,2,1),(3,1,-1),(1,0,1),(3,1,1),(0,2,-1),(2,3,-1),(3,2,1),(1,3,-1),(2,0,1)])==[[0,-1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,1,0]],'global scalar signed exchange')
    return dict(status='PASS_FRESH_COMPLEX_LABEL_SCALAR_SPLICE_PRECISION',five_stage_histogram=ledger['histogram'],
        label_checks=checks,ledger=ledger,scalar_bill=b,
        splice=dict(program=programs,global_contract=g,controls=controls,source_pin=PIN,certificate_sha256=cp['compressed_sha256']),
        precision_guard=precision,input_pins=verified,program_check=program_check,
        inherited_theorem_dependencies=[
            'The pinned gcert/1 program is accepted, fresh in this run, by Sussman\'s reference checker gx.check1 with the exact scalar identity (E5) and by his gxcore mirror of the two Lean checks; a flipped scalar sign is rejected by both. No Lean check of this program is pinned in this package.',
            'Pinned Lab.inv dirty lifting, exact gwinB/G0..G4 geometry, owner bijections and NetCert composition are inherited source theorems.',
            'Retained general Clifford synthesis, compact complete-stream tape primitives, common-grid precision and complete-row proofs remain analytic dependencies.',
            'The finite operational recipe is regenerated and checked; no astronomical cover enumeration or universal tape-machine execution is claimed.'])

if __name__=='__main__':
    result=run(progress=lambda text:print(text,file=sys.stderr))
    print(json.dumps(result,indent=2))
    if RECORD: json.dump(RECORD,open(os.environ.get('CX_RECORD','/tmp/cx_record.json'),'w'),indent=1); print('RECORDED',sorted(RECORD),file=sys.stderr)

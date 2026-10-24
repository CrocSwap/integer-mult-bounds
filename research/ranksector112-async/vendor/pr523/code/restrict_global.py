"""Restrict PR514's unhosted nine-stage template to its 112 code ports.

This script constructs only the restricted parent. It does not claim that its
old bank placement is the final whole-owner placement. All final hosted costs
must be recounted from the separately emitted complete program.

Usage: python restrict_global.py PARENT_BASE LOCAL112 NEW_BASE
"""
from pathlib import Path
from collections import Counter
import argparse,copy,gzip,hashlib,json,math,shutil,sys

parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('parent_base',type=Path,help='Replayed pinned PR514 base directory')
parser.add_argument('local112',type=Path,help='Fully verified 112-port local artifact directory')
parser.add_argument('new_base',type=Path,help='New output base directory; must not exist')
args=parser.parse_args()
PARENT,LOCAL,OUT=(p.resolve()for p in(args.parent_base,args.local112,args.new_base))
if not __debug__:raise RuntimeError('Assertions must be enabled')
if OUT.exists():parser.error('Output directory already exists: '+str(OUT))
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gzip_content_sha(p):return hashlib.sha256(gzip.decompress(p.read_bytes())).hexdigest()
def dump(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(x,sort_keys=True,separators=(',',':')).encode()
    p.write_bytes(gzip.compress(raw,mtime=0)if p.suffix=='.gz'else raw+b'\n')
    return hashlib.sha256(raw).hexdigest()

S=PARENT/'split-centres';D=OUT/'split-centres'
old=read(S/'GLOBAL-TEMPLATE.json.gz');can0=read(S/'CANONICAL-WORD.json.gz')
can=read(LOCAL/'CANONICAL-WORD.json.gz');checks=read(LOCAL/'LOCAL-CHECKS.json')
programs=read(LOCAL/'LOCAL-PROGRAMS.json.gz');mapping=read(LOCAL/'PORT-MAPPING.json')
new_to_old=mapping['new_to_old'];old_to_new={v:i for i,v in enumerate(new_to_old)}
assert len(new_to_old)==len(old_to_new)==112 and new_to_old==sorted(new_to_old)
assert can['v']==112 and can['h']==9 and can['R']==560
assert can['ports']==[can0['ports'][i]for i in new_to_old]
assert can['frames']==can0['frames'] and len(can['centers'])==8
assert can['start'][224:]==can0['start'][240:]
assert can['final'][224:]==can0['final'][240:]
assert old['live']==12720 and old['physical']==13298
M,K,T,L,V,R=73,4,8,9,112,560
DATA=2*K*T*V;W=old['live']-(7680-DATA);PHYSICAL=W+R+8+2
assert (DATA,W,PHYSICAL)==(7168,12208,12778)

def family(f):
    if f>=7680:
        assert f<old['live'];return f-512
    comp,port=divmod(f,120);assert port in old_to_new
    return comp*112+old_to_new[port]

# The local proof artifacts are copied without modification. Global metadata
# must bind their new actual hashes, never the parent phase/word hashes.
names=['CANONICAL-WORD.json.gz','FULL-WORD.json.gz','LOCAL-PROGRAMS.json.gz',
       'LOCAL-CHECKS.json','RESIDUAL-ADAPTERS.json','LEMMA-A.json',
       'RESTRICTION.json','PORT-MAPPING.json','INDEPENDENT-LOCAL-REPLAY.json',
       'CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json','TRANSPORT.json']
for name in names:assert (LOCAL/name).is_file(),LOCAL/name
D.mkdir(parents=True)
for name in names:shutil.copyfile(LOCAL/name,D/name)
shutil.copyfile(LOCAL/'INDEPENDENT-LOCAL-REPLAY.json',D/'INDEPENDENT-REPLAY.json')

ph0=read(PARENT/'work/complex-nine-native/DATA-PHASES.json')
ph=copy.deepcopy(ph0);ph['ports']=112
ph['recipes']=[copy.deepcopy(ph0['recipes'][i])for i in new_to_old]
for i,z in enumerate(ph['recipes']):
    assert z['port']==new_to_old[i] and z['q']==can['ports'][i]
    z['port']=i
ph['nonzero_stage_alignment_translations']=sum(bool(v)for z in ph['recipes']for e in z['stage_alignment']for v in e.values())
ph['terminal_omission_controls_rejected']=112
ph['inherited_parent_exact_phase_polynomial_evaluations']=ph.pop('exact_phase_polynomial_evaluations')
ph['restriction_method']='Each complete recipe is unchanged except its port index; the retained parent polynomial checks establish every selected equality.'
ph['source_parent_sha256']=sha(PARENT/'work/complex-nine-native/DATA-PHASES.json')
dump(OUT/'work/complex-nine-native/DATA-PHASES.json',ph)
for name in ['moment.py','base_two_moment.py','outer.py']:
    dest=OUT/'work/pr361/code/engines'/name;dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(PARENT/'work/pr361/code/engines'/name,dest)

t=copy.deepcopy(old);t['version']='hamming112-restricted-nine-stage-parent-v1'
t['local_programs']=programs;t['live']=W;t['physical']=PHYSICAL
t['private_namespace']={'centers':[W,W+8],'reserved_tableau':[W+8,W+8+R],
                        'coefficient':[PHYSICAL-2,PHYSICAL]}
for c in t['calls']:
    oldowners=c['owners'];newowners=[]
    for side in range(2):
        for np,op in enumerate(new_to_old):
            f,route=oldowners[side*120+op]
            assert route==[1,c['stage'],op]
            newowners.append([family(f),[1,c['stage'],np]])
    newowners += [[family(f),copy.deepcopy(route)]for f,route in oldowners[240:]]
    assert len(newowners)==784
    c['owners']=newowners;c['local_program_sha256']=checks[c['orientation']]['sha256']
t['idle_children']=[dict(e,port=old_to_new[e['port']])for e in old['idle_children']if e['port']in old_to_new]
assert len(t['idle_children'])==18*112
t['bank_padding']['families']=[family(f)for f in old['bank_padding']['families']]
assert t['bank_padding']['families']==list(range(DATA,W))
t['cover_final_correction'].update(families=[0,W],charged_calls_per_cover=W)
for e in t['execution_schedule']:
    if e['kind']=='bank_padding_cover_sweep':e['families']=[DATA,W]
    elif e['kind']=='translate_every_live_family':e.update(t['cover_final_correction'])
t['exact_data_phase_recipe_sha256']=sha(OUT/'work/complex-nine-native/DATA-PHASES.json')
t['exact_local_clifford_recipe_sha256']=sha(D/'CLIFFORD-RECIPES.json')
t['residual_adapter_sha256']=sha(D/'RESIDUAL-ADAPTERS.json')
t['port_restriction']={'parent_global_template_content_sha256':gzip_content_sha(S/'GLOBAL-TEMPLATE.json.gz'),
                       'parent_data_phase_sha256':sha(PARENT/'work/complex-nine-native/DATA-PHASES.json'),
                       'new_to_old':new_to_old,
                       'canonical_word_content_sha256':gzip_content_sha(D/'CANONICAL-WORD.json.gz'),
                       'proof':'The nine-stage data route and idle recipes are a portwise direct sum after each verified complete invocation. Restrict every such sum to the selected 112 ports.'}
template_hash=dump(D/'GLOBAL-TEMPLATE.json.gz',t)

# Derive the unchanged bank remainder profile from literal old bank footprints,
# independently of the old global histogram. A width-nine bank route is a slot
# index; an entering route states its residual offset and width explicitly.
foot={};bybank=Counter()
for c in t['calls']:
    for h,(f,rt)in enumerate(c['owners'][224:]):
        width=9-len(can['frames'][can['start'][224+h]])
        assert rt[0]==2
        off=9*rt[1]if len(rt)==2 else rt[1]
        if len(rt)>2:assert rt[2]==width
        cells=set(range(off,off+width));assert not foot.setdefault(f,set())&cells
        foot[f]|=cells
assert set(foot)==set(range(DATA,W))
pad=Counter()
for f,cells in foot.items():
    assert cells==set(range(len(cells)))
    left=M-len(cells);parts=-(-left//51)
    for i in range(parts):pad[left//parts+(i<left%parts)]+=1
paid=Counter(pad)
for c in t['calls']:
    for r,n in checks[c['orientation']]['paid_profile'].items():paid[int(r)]+=n
for e in t['idle_children']:paid[e['rank']]+=e['replicas']
mass=sum(r*n for r,n in paid.items())
assert M*W-mass==2560 and max(paid)==48

# Fresh deterministic finite invoice using the inherited formula and enlarged
# constant allowances. This does not reuse the old numerical kappa receipt.
compiler=64*(M+1)**3;macros=max(z['scalar_macros']for z in checks.values())
children=sum(checks['forward']['paid_profile'].values());N=224+R;C=8
adapters=16*(macros+children+N+C)+64*M
local_bound=max(z['real_component_primitive_bound']for z in checks.values())+adapters*compiler
bridges=sum(e['kind']=='bridge'for e in t['recipe']);bridgeadd=2*V*T*bridges
shifts=K*V*T;moves=2*K*V*T;NB=(W-DATA)//L
widths=[9-len(can['frames'][f])for f in can['start'][224:]];enter=sum(w<9 for w in widths)
scalar=sum(checks[c['orientation']]['real_component_primitive_bound']for c in t['calls'])
nonlocal_items=4*V*T*L+2*V*T*L+2*L*T*R+sum(e['replicas']for e in t['idle_children'])+L*NB+bridgeadd+shifts+moves+W+PHYSICAL+2*L*T*enter*144
outside=8*nonlocal_items+64*M
pervertex=scalar+bridgeadd+shifts+moves+W+(72*adapters+outside)*compiler+64*PHYSICAL
r=M//2;group=2**(r*r)*math.prod(2**(2*i)-1 for i in range(1,r+1))
stock=group*PHYSICAL;smass=group*mass;logical=group*pervertex+64
router=compiler*(logical+1)*(stock+1)**2
G,E,C0=2**30000,2**100000,2**210000;B=smass+E
literal=2*G*stock**2+8*smass+4*stock+4+32*M;depth=2
row=depth*stock.bit_length()+9909+252
assert local_bound<2**48 and logical<2**6050 and router<G and literal<E and B<2**100001
assert 32*M*B*B<C0 and 2*B+18<C0 and row<20161 and M*M>2*max(paid)**2
finite=dict(local_primitive_bound=local_bound,local_adapters=adapters,pervertex=pervertex,
            physical_stock_bits=stock.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),
            physical_row_coefficient=row,retained_row_coefficient=20161,compiler=compiler,
            G_exponent=30000,E_exponent=100000,C0_exponent=210000,required_C0_bits=(32*M*B*B).bit_length(),
            halving_degree=depth,halving_integer_inequality=[M*M,2*max(paid)**2])
integ=dict(status='PASS_RESTRICTED_PARENT_TEMPLATE_AND_FRESH_FINITE_INVOICE',
           canonical_word_sha256=sha(D/'CANONICAL-WORD.json.gz'),
           exact_phase_receipt_sha256=sha(D/'CLIFFORD-REVIEW.json'),
           global_template_sha256=template_hash,local_program_checks=checks,
           R=R,v=V,m=M,live=W,physical=PHYSICAL,bank_assignments=L*T*R,
           rank_mass=mass,deficit=2560,global_profile=dict(sorted(paid.items())),
           bank_remainder_profile=dict(sorted(pad.items())),
           emitted_local_events_all_calls=sum(checks[c['orientation']]['events']for c in t['calls']),
           finite_invoice=finite,
           scope='112-port unhosted parent with exact inherited data-chart restriction, new local program, and fresh finite invoice. Final whole-owner hosting and global kappa require the separate final audits.')
dump(D/'INTEGRATION.json',integ)
print(json.dumps({k:integ[k]for k in ['status','live','physical','rank_mass','deficit','global_profile']}),flush=True)

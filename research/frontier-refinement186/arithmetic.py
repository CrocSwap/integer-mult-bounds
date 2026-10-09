"""Fixed supplier arithmetic, explicit raw component binding, no producer imports.

Apache-2.0. Prepared with substantial OpenAI Codex assistance.
The copied generic moment/assembly algorithms remain exact prior reviewed bytes.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
import json,gzip,sys,copy
from source_binding import HERE,ROOT,check_sources,require
sys.path.insert(0,str(ROOT/'research/precision-certificate'))
import independent_moments as M
import independent_assembly as A
PACKAGE=ROOT/'research/coordinated-frames-and-entrance-banks'
GRID=10**24
STEP=Q(1,GRID)
COMPLEX=Q(331161965949525999057,500000000000000000000000)
COARSE=Q(133096233391197420469,200000000000000000000000)
ATOM=Q(13301283151705819139,20000000000000000000000)
KAPPA=Q(330942774629799608347,500000000000000000000000)
BASELINE=Q(330942774629799,500000000000000000)
ETA=BETA=PHASE_GAP=STEP
FIXED_INPUT_HASHES={'logical.json': '9adcc1e7da7222e19dce989cd6f86200997a677642b4c2a580aaae0c0a31a855', 'physical-sinks.json': 'eb67db76d5243eecaefb8709e4421ed8d74ce9a5587a3877d6c69384487b68e0', 'scaled-bank.json': '4757539c1ee428b1208233fea113420cef9b9ad5f8b4b76cbdc2a534e78c618f'}
def read(path):
    raw=path.read_bytes();return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
def positive(raw,maxrank):return A.component_histogram(raw,maxrank)
def load_inputs():
    inputs={name:read(HERE/'inputs'/name) for name in ('logical.json','physical-sinks.json','scaled-bank.json')}
    for name,expected in FIXED_INPUT_HASHES.items():require(sha256((HERE/'inputs'/name).read_bytes()).hexdigest()==expected,'wrong fixed derived input '+name)
    logical,physical,scaled=(inputs[n] for n in ('logical.json','physical-sinks.json','scaled-bank.json'))
    native=read(PACKAGE/'certificate.json');before=read(PACKAGE/'selected/complex/profile-before.json.gz');rawphysical=read(PACKAGE/'selected/complex/profile.json.gz');sinks=read(PACKAGE/'selected/complex/sinks.json');bank=read(PACKAGE/'bit/banks.json');oldbit=read(PACKAGE/'references/pr168/bit-physical-profile.json')
    for name in ('numerical_complex_root','gauge_cost_rejections','gauge_trial_saving','gauge_selection'):before.pop(name,None)
    require(logical==before,'raw logical scalar profile differs')
    require((logical['h'],logical['v'],logical['R'],logical['c'],logical['q'],logical['matched'],logical['total_M_operations'],logical['loss'])==(22,1320,13042,21249,3157,11364,32971,440),'actual logical scalar charges')
    published=native['complex']['physical']['physical']
    for name in ('h','v','R','physical_R','pairs','loss','m','W_per_vertex','rank_per_vertex','deficit_per_vertex'):require(physical[name]==published[name],'native paid dimension differs '+name)
    require(physical['sinks']==sinks['eligible_count']==published['terminal_sinks']==46,'46 terminal deletions')
    for name in ('local_histogram','source_data_histogram','target_data_histogram','physical_gauge_histogram','child_histogram'):
        maximum=65 if name=='child_histogram' else 21 if name=='physical_gauge_histogram' else 22
        require(positive(physical[name],maximum)==positive(published[name],maximum),'native paid component differs '+name)
    for name,field in (('local_histogram','local_histogram'),('target_data_histogram','target_histogram'),('child_histogram','child_histogram')):require(positive(physical[name],65)==positive(sinks[field],65),'raw46-sink component differs '+name)
    for name in ('source_data_histogram','physical_gauge_histogram'):require(positive(physical[name],22)==positive(rawphysical[name],22),'unchanged source/gauge component differs '+name)
    zeros={'native':published['target_data_histogram'].get('0',0),'independent_literal_events':physical['target_data_histogram'].get('0',0)}
    require(zeros=={'native':6270,'independent_literal_events':6325},'zero-rank event diagnostics')
    return logical,physical,scaled,native,bank,oldbit,zeros
def paid_complex(row):
    require((row['h'],row['v'],row['R'],row['pairs'],row['sinks'],row['physical_R'],row['loss'])==(22,1320,13042,2310,46,10686,440),'complete complex dimensions')
    require(row['physical_R']==row['R']-row['pairs']-row['sinks'],'physical dirty population')
    children=Counter()
    for name in ('local_histogram','source_data_histogram','target_data_histogram'):
        for rank,n in positive(row[name],22).items():children[rank]+=3*n
    for rank,n in positive(row['physical_gauge_histogram'],21).items():children[3*rank]+=n
    children[2]+=2640;children=dict(sorted(children.items()));mass=sum(r*n for r,n in children.items())
    require(children==M.normalize_children(row['child_histogram'],66),'complete complex paid children')
    require((row['m'],row['W_per_vertex'],row['rank_per_vertex'],row['deficit_per_vertex'])==(66,13326,mass,1320),'complex full mass/stock')
    require(66*13326-mass==2640-3*440==1320,'complex telescoping deficit')
    return dict(width=66,stock=13326,children=children,mass=mass,deficit=1320)
def paid_bank(scaled,bank,oldbit):
    original=M.normalize_children(oldbit['child_histogram'],72);require(original.pop(60)==2200,'exact entrance exterior removal')
    require(original==M.normalize_children(bank['profile']['child_multiplicities'],72),'remaining paid bank children')
    stock=2*1760+3*(Q(2200,18)+Q(15828,3));mass=sum(r*n for r,n in original.items())
    require((stock,mass,72*stock-mass,max(original))==(Q(59144,3),1417520,1936,22),'normalized bank inventory')
    require((9*2200%18,9*15828%3)==(0,0),'integral9-copy bank allocation')
    require(3*(9*2200//18+9*15828//3)+2*9*1760==9*stock==177432,'actual9-copy stock')
    expected=dict(width=72,stock=59144,children={str(r):3*n for r,n in original.items()},mass=3*mass,deficit=5808,edge_count=3*sum(original.values()),normalization_scale=3,physical_replicas=9)
    require(scaled==expected,'unpaid bank stock,unscaled children or fallback edge-count mismatch')
    return dict(expected,children={int(r):n for r,n in expected['children'].items()})
def strict_bit(profile,coarse,atom,*,bad_fraction=M.BAD,fallback_children_per_edge=32*72**2):
    require(bad_fraction==M.BAD and fallback_children_per_edge==32*72**2,'omitted full bad-class fallback')
    result=M.certify_bit_supplier(72,profile['stock'],profile['children'],coarse,atom=atom)
    require(result['edge_count']==profile['edge_count'] and result['rank_mass']==profile['mass'],'all scaled fallback edges and mass')
    require(result['fallback_lower']>0,'fallback charge omitted')
    return result
def compute(logical,physical,scaled,native,bank,oldbit,zeros):
    cp=paid_complex(physical);bp=paid_bank(scaled,bank,oldbit)
    complex_bounds=M.require_contraction(M.supplier_bounds(66,cp['stock'],cp['children'],COMPLEX))
    bit=strict_bit(bp,COARSE,ATOM)
    threshold=COARSE/(1+COARSE-M.OLD);require(ATOM-STEP<=threshold<ATOM,'atom first strict grid')
    successors={}
    for name,p,s,kwargs in [('complex',cp,COMPLEX,{}),('bit',bp,COARSE,dict(bad_fraction=M.BAD,fallback_children_per_edge=32*72**2))]:
        result=M.supplier_bounds(p['width'],p['stock'],p['children'],s+STEP,**kwargs);require(result['total_lower']>=1,'supplier successor accepted '+name);successors[name]=result
    bridge=A.reconstruct_bridge(logical,physical);require(bridge['local_group_upper']==native['complex']['physical']['scalar_bound']['local_group_upper'],'full logical scalar/router charge')
    assembly=A.balanced_assembly(bridge,bit['effective_saving'],COMPLEX,KAPPA,eta=ETA,beta=BETA,phase_gap=PHASE_GAP)
    require(KAPPA<assembly['minimum_margin']<=KAPPA+STEP and KAPPA>BASELINE,'headline strict next grid or improvement')
    try:A.balanced_assembly(bridge,bit['effective_saving'],COMPLEX,KAPPA+STEP,eta=ETA,beta=BETA,phase_gap=PHASE_GAP)
    except ValueError as e:require('compact_phase_layer_above_kappa' in str(e),'wrong headline successor failure')
    else:raise ValueError('headline successor accepted')
    return A.serialize(dict(schema_version=1,source_commit='166a34d75e853e933855f0f7e940fe77c4bb6b8d',kappa=KAPPA,baseline_kappa=BASELINE,improvement=KAPPA-BASELINE,complex_saving=COMPLEX,coarse_bit_saving=COARSE,atom=ATOM,effective_bit_saving=bit['effective_saving'],grid=GRID,eta=ETA,beta=BETA,phase_gap=PHASE_GAP,complex_profile=cp,scaled_bank_profile=bp,complex_bounds=complex_bounds,bit_bounds=bit,supplier_successors=successors,atom_threshold=threshold,headline_successor=KAPPA+STEP,headline_successor_rejected=True,finite_bridge=bridge,assembly=assembly,zero_target_diagnostic=dict(zeros,difference=55),scope='Finite fixed-supplier arithmetic and input binding. Exact geometry/scalar/bank results are separate finite evidence; inherited tensor/weighted compiler/common charts/routing/restoration/phase/precision/analytic/allsize fixed-tape contracts remain conditional. No current frontier or global maximum claim.'))
def regenerate():
    check_sources();result=compute(*load_inputs());result['source_manifest_sha256']=sha256((HERE/'SOURCE.json').read_bytes()).hexdigest();return result

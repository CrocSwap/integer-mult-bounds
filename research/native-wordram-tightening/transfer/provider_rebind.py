"""Fresh native majorant rebinding of Cao Yifan's latest PR4610 profile.
Apache-2.0; prepared for Dugongue with substantial OpenAI Codex assistance.
Engine: Dillon; compiler: zxv, Jacob Alan Sussman and credited predecessors.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import json
import gzip
from collections import Counter
HERE=Path(__file__).resolve().parent

def need(ok,why):
    if not ok: raise ValueError(why)

def check(profile_override=None, latest_override=None):
    ep=HERE/'critical_engine.py'; E={'__name__':'frozen_critical','__file__':str(ep)}
    exec(compile(ep.read_bytes(),str(ep),'exec'),E)
    profile=json.loads((HERE/'ARITHMETIC.json').read_bytes()) if profile_override is None else profile_override
    need(profile['local_paid']=={'1':2201,'2':412,'3':510,'4':127,'5':40,'8':8},'round-three local profile')
    need(profile['local_helpers']=={'4':28,'7':7,'8':47,'9':326},'all independent helper ranks')
    paid={int(k):v for k,v in profile['paid'].items()};targets={int(k):v for k,v in profile['targets'].items()}
    need(sum(paid.values())==64404 and sum(targets.values())==10928,'complete inventory counts')
    need(sum(k*v for k,v in targets.items())-sum(k*v for k,v in paid.items())==752,'rank mass surplus')
    # Rebuild the complete invoice from actual emitted word plus pinned controller.
    word_bytes=gzip.decompress((HERE/'ACTUAL-WORD.json.gz').read_bytes())
    need(sha256(word_bytes).hexdigest()=='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd','actual source word canonical payload')
    word=json.loads(word_bytes);c=word['canonical']
    local=Counter(e[5] for e in word['programs']['forward'] if e[0]=='climb')
    local.update(e[4] for e in word['programs']['forward'] if e[0]=='center')
    reverse=Counter(e[5] for e in word['programs']['backward'] if e[0]=='climb')
    reverse.update(e[4] for e in word['programs']['backward'] if e[0]=='center')
    helpers=Counter(len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]]) for r in range(224,632))
    need(local==reverse==Counter({int(k):v for k,v in profile['local_paid'].items()}),'actual complete local dual paid profiles')
    need(helpers==Counter({int(k):v for k,v in profile['local_helpers'].items()}),'actual independent helper interfaces')
    controller_bytes=(HERE/'CONTROLLER.json').read_bytes()
    need(sha256(controller_bytes).hexdigest()=='1f5d6aa267e4e66048818714b5d3b5eae17a58abe91d15deeaa34574f7391a5f','pinned source controller')
    controller=json.loads(controller_bytes);rt,rp=Counter(),Counter();kinds=Counter(e[0] for e in controller['physical_events'])
    need(kinds==Counter(ADD=90,LOCAL=18,SIGNED_SWAP=16,IDLE=15,QUERY_SHEAR=15),'complete retained controller event census')
    for event in controller['physical_events']:
        if event[0]=='LOCAL':rt.update(helpers);rp.update(local)
        elif event[0]=='QUERY_SHEAR':rp[1]+=112
        elif event[0]=='IDLE':rp[8*len(event[2])]+=224
    for term in controller['diagonal']:rt[1+8*sum(term[1:])]+=112
    need(dict(rt)==targets and dict(rp)==paid,'complete emitted word/controller invoice')
    old=next(row['witness'] for row in json.loads((HERE/'majorant-benchmarks.json').read_bytes())['cases'] if row['name']=='p16')
    witness={key:old[key] for key in ('a','b','height_base','ell0','s','lambda','p','c')}
    witness['guards']={key:old['guards'][key] for key in ('U','V','Q','d','beta')};witness['upper_exponent']='.997067'
    lo,hi=F('.99697822412'),F('.99697822414')
    root=E['certify'](profile,lo,hi,F('.564'),F(1))
    majorant=E['critical_guards'](profile,lo,hi,witness)
    latest=json.loads((HERE/'LATEST-ARITHMETIC.json').read_bytes()) if latest_override is None else latest_override
    need(all(latest[k]==profile[k] for k in ('paid','targets','local_paid','local_helpers')),'identical complete latest paid and target profile')
    qC=F(latest['compiler']['uniform_saving']); H=latest['compiler']['H'];gap=1-hi-qC
    log=lambda n:tuple(F(x,E['GRID']) for x in E['logarithm'](n))
    need(log(2)[0]>F(2,3) and log(145)[1]<8,'exact logarithms')
    # log A < (1-theta)*(log145+650 log1024) < .003022*(8+6500)<20.
    # (2/5)*log(133+log N)<(2/5)*56 log2 <112/5.
    need(F('.003022')*(8+6500)<20 and 133+H<2**56,'overhead below43')
    margin=gap*H*F(2,3)-F(212,5)
    need(gap>0 and margin>0,'finite critical-root absorption')
    need(gap-F(2,5)/(133+F(2,3)*H)>0,'monotone continuation above cutoff')
    controls={}
    for name,kwargs in [('unfunded_mirror',dict(beta=F(0))),('wrong_root',dict(lo=F('.9969798340229'),hi=F('.9969798340230')))]:
        k=dict(lo=lo,hi=hi,beta=F('.564'),derivative_floor=F(1));k.update(kwargs)
        try:E['certify'](profile,**k)
        except ValueError:controls[name]=True
        else:raise ValueError('negative control accepted: '+name)
    return dict(status='PASS_SOURCE_BOUND_CRITICAL_PROVIDER',source_pr=4610,source_head='20bb93cd990d2ff683e4d0fc56b87a42cd5d3296',
        critical_root=root,critical_majorant=majorant,uniform_saving=str(qC),fixed_rank_encoding='2^'+str(H),
        fixed_rank_materialized=False,finite_absorption_log_margin=str(margin),negative_controls=controls,
        scope='Exact profile arithmetic and funded critical majorant; actual all-fiber algebraic supplier and whole-job normalizers are explicitly inherited proofs, not finite tests.')
if __name__=='__main__': print(json.dumps(check(),indent=2))

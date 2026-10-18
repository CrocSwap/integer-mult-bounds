#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound finite verification of the six-skip/T740 composition.

Jeremy Diviney with substantial OpenAI Codex assistance. The exact frame,
operator, owner, interval arithmetic, lift and cap engines are retained from
the credited predecessors. New here is their binding to this composition.
"""
import argparse
import collections
import contextlib
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import io
import json
from pathlib import Path
import tempfile
import types

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
MAIN=ROOT/'research/rank7-joint-endframes'
LOCAL={1:2433,2:712,3:232,4:108,5:18,8:8}
IDLE={1:173160,3:49617,5:17205,48:281903}
PROFILE={1:16376940,2:4741920,3:1594737,4:719280,5:137085,8:53280,48:281903}

def need(ok,why):
    if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    raw=p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def authenticate():
    paths=list(P.rglob('*'))
    need(not any(p.is_symlink() for p in paths),'regular package files')
    actual={p.relative_to(P).as_posix():sha(p) for p in paths if p.is_file() and p!=P/'MANIFEST.json'}
    need(actual==read(P/'MANIFEST.json'),'complete published package inventory')
    for path,expected in read(P/'SOURCE-PINS.json').items():need(sha(ROOT/path)==expected,'external source '+path)
    for r in read(P/'VENDOR.json'):need(sha(P/r['path'])==r['sha256'],'vendor source '+r['path'])
def load(p,name):
    m=types.ModuleType(name);m.__file__=str(p)
    exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__)
    return m

def apply_journal(fill,journal):
    """PR3018 journal semantics, following Petalas's PR3021 apply_exchange."""
    rows=[r.copy() for r in fill['rows']];seen=set()
    need(len(rows)==271728 and len(journal['edits'])==103,'complete base and journal')
    for i,before,after in journal['edits']:
        need(type(i)is int and 0<=i<len(rows) and i not in seen,'unique journal index')
        need(rows[i]==before,'journal preimage')
        need(len(after)==6 and all(type(v)is int for v in after),'integer row')
        need(before[:2]==after[:2] and before!=after,'fixed call/helper identity')
        rows[i]=after.copy();seen.add(i)
    return rows

def check_word(parent,word,provider,pm,au):
    need({k for k in parent if parent[k]!=word[k]}=={'restore','cleanup','report'},'only declared word sections change')
    profile,inventory=pm.frame_report(word)
    need({int(k):v for k,v in profile.items()}==LOCAL,'actual local bill')
    need({int(k):v for k,v in provider['actual_paid_profile'].items()}==LOCAL,'provider local bill')
    helpers=sorted(set(range(224,704))-set(word['removed']))
    widths=[len(pm.basis(word['helper_final'].get(str(h),[1<<i for i in range(9)])))-len(pm.basis(word['start_extra'].get(str(h),[]))) for h in helpers]
    need(widths==provider['widths'],'ordered literal helper widths')
    need(dict(collections.Counter(widths))=={int(k):v for k,v in inventory.items()},'inventory histogram')
    need(len(word['helper_final'])==91,'all restored endpoints')
    w=copy.deepcopy(word);w['A']=w['A'][w['prelude_events']:]
    need(word['cleanup']==pm.derive_cleanup(w,set(map(int,word['helper_final']))),'literal inverse cleanup')
    regs=sorted({r for g in parent['restore']+word['restore'] for r in au.registers(g)})
    a={r:{r:Q(1)} for r in regs};b=copy.deepcopy(a)
    for g in parent['restore']:au.apply(g,a)
    for g in word['restore']:au.apply(g,b)
    need(a==b,'exact full restore scalar map')
    return dict(local_profile=profile,width_inventory=inventory,ordered_helpers=len(widths),restore_variables=len(regs),buffers=91)

def stock(buffers=91,payload=2048):
    need(type(buffers)is int and buffers==91,'all private buffers charged')
    physical=896*740+408+8+buffers+2
    group=2**1296
    for j in range(1,37):group*=2**(2*j)-1
    bits=(group*physical).bit_length();norm=(bits+1)//2;reserve=128+37+18+norm+1+4
    need(physical==663549 and norm<=1330,'retained stock bound')
    need(type(payload)is int and reserve<=payload,'paid payload bound')
    return dict(replicas=740,physical=physical,buffers=buffers,stock_l2_bits=norm,reserve=reserve,payload=payload)

def rejection(fn,label):
    try:fn()
    except (ValueError,RuntimeError,AssertionError):return label
    raise ValueError('accepted negative control: '+label)

def finite():
    need(__debug__,'retained checkers require enabled assertions')
    authenticate();pm=load(MAIN/'vendor/preload_move.py','retained_pm');au=load(MAIN/'vendor/audit_local.py','retained_audit')
    providers=read(P/'vendor/PR3042-PROVIDERS.json');oldproviders=read(MAIN/'allocation/PROVIDERS.json');words={};checks={};controls=[]
    with tempfile.TemporaryDirectory(prefix='six-skip-local-') as tmp:
        for tag,key in [('base','gauge44'),('extra','extra')]:
            word=read(P/f'words/{tag}.json.gz');parent=read(MAIN/f'data/WORD-{tag}.json.gz');words[tag]=word
            need(providers[key]['widths']==oldproviders[key]['widths'],'unchanged packing width array')
            checks[tag]=check_word(parent,word,providers[key],pm,au)
            with contextlib.redirect_stdout(io.StringIO()):au.run(P/f'words/{tag}.json.gz',Path(tmp)/(tag+'.json'))
            exact=read(Path(tmp)/(tag+'.json'));need(exact['checked_columns']==632 and exact['orientations']=={'forward':'PASS','dual':'PASS'},'all-column audit')
            checks[tag]['exact_operator_audit']='forward and dual, 632 independent inputs'
            bad=copy.deepcopy(word);bad['restore'][162][3]*=-1
            body=copy.deepcopy(bad);body['A']=body['A'][body['prelude_events']:]
            bad['cleanup']=pm.derive_cleanup(body,set(map(int,bad['helper_final'])))
            controls.append(rejection(lambda:check_word(parent,bad,providers[key],pm,au),tag+' coefficient mutation'))
            badp=copy.deepcopy(providers[key]);i=next(i for i,v in enumerate(badp['widths']) if v!=badp['widths'][0]);badp['widths'][0],badp['widths'][i]=badp['widths'][i],badp['widths'][0]
            controls.append(rejection(lambda:check_word(parent,word,badp,pm,au),tag+' width permutation with unchanged histogram'))
    base=read(MAIN/'allocation/FILL.json.gz');journal=read(P/'vendor/PR3018-EXCHANGE.json')
    rows0=apply_journal(base,journal);lift=load(P/'vendor/lift.py','retained_lift')
    edits=lift.patch(rows0,read(P/'vendor/PR3024-EXCHANGE.json'));rows=lift.Rows(rows0,edits)
    order0=read(MAIN/'allocation/ORDER.json');dispatch0={(s,r):p for s,r,p in read(MAIN/'allocation/DISPATCH.json')}
    order,dispatch=lift.chronology(order0,dispatch0)
    engine=load(MAIN/'allocation/vendor/independent_owners.py','retained_owners')
    normalized={k:{**v,'actual_paid_profile':{int(r):n for r,n in v['actual_paid_profile'].items()}} for k,v in providers.items()}
    fill={'columns':['time','helper','owner_replica','child','port','offset'],'rows':rows,'dispatch_overrides':[]}
    owner,_,_=engine.check(740,order,fill,dispatch,PROFILE,read(MAIN/'allocation/vendor/PLAN.json.gz'),read(MAIN/'allocation/vendor/TEMPLATE.json.gz'),normalized)
    need(owner['roles']==2717280 and owner['rank_mass']==65088*740,'complete owner roles and rank mass')
    need(owner['idle']==IDLE,'exact attained cap idle bill')
    need(owner['physical']==owner['live']+490,'retained diagnostic uses 72 buffers')
    actual_stock=stock();owner['physical']=actual_stock['physical']
    # Bind the literal checked rows to the full-run input independently of gzip headers.
    payload=hashlib.sha256((json.dumps({'columns':fill['columns'],'dispatch_overrides':[]},sort_keys=True,separators=(',',':'))[:-1]+',"rows":[').encode())
    for i,row in enumerate(rows):payload.update((("," if i else "")+json.dumps(row,separators=(',',':'))).encode())
    payload.update(b']}\n')
    materialized=dict(fill_payload_sha256=payload.hexdigest(),order_sha256=hashlib.sha256((json.dumps(order,separators=(',',':'))+'\n').encode()).hexdigest(),
                      dispatch_sha256=hashlib.sha256((json.dumps([[s,r,dispatch[s,r]] for s,r in order],separators=(',',':'))+'\n').encode()).hexdigest())
    for r in set(LOCAL)|set(IDLE)|set(PROFILE):need(PROFILE.get(r,0)==6660*LOCAL.get(r,0)+IDLE.get(r,0),'complete profile decomposition')
    root=load(MAIN/'tools/root.py','retained_root');lo,hi=root.kappa_from_profile(PROFILE,740)
    cap=load(P/'vendor/cap_proof.py','retained_cap');cap.LOCAL=LOCAL.copy()
    cert=read(P/'vendor/PR3042-CAP.json');need((lo,hi)==(Q(cert['cap_lower']),Q(cert['cap_upper'])),'same attained fractional cap root')
    cap_result=cap.verify_cap(cert,root)
    for r,n in cap_result['idle_per_replica'].items():need(IDLE.get(int(r),0)==740*Q(n),'attained exact cap pattern counts')
    headline=Q((lo*10**24).__floor__(),10**24)-Q(1,10**46)-Q(1,10**70)
    previous=Q(read(P/'vendor/PR3042-CLAIM.json')['kappa']);need(headline>previous,'strict improvement over PR3042')
    bad=copy.deepcopy(journal);bad['edits'][0][1][0]+=1
    controls.append(rejection(lambda:apply_journal(base,bad),'changed journal preimage'))
    controls.append(rejection(lambda:stock(buffers=90),'omitted private buffer'))
    controls.append(rejection(lambda:stock(payload=1511),'insufficient payload'))
    badprofile=PROFILE.copy();badprofile[1]-=1
    controls.append(rejection(lambda:root.kappa_from_profile(badprofile,740),'omitted paid child'))
    return dict(status='PASS_SIX_SKIP_T740_FINITE',words=checks,owners=owner,stock=actual_stock,materialized=materialized,
                profile=PROFILE,root=[str(lo),str(hi)],packing_cap=cap_result,realized_cap_fraction='1 (exact same moment profile)',
                kappa=str(headline),baseline_kappa=str(previous),gain=str(headline-previous),controls=controls,
                scope='Finite exact word/geometry/moment/cap checks. Stored release binding is separate; inherited source/native/compiler/physical/all-size hypotheses remain.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',type=Path);p.add_argument('--finite-only',action='store_true');a=p.parse_args()
    result=json.loads(json.dumps(finite(),sort_keys=True))
    if a.write:a.write.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result==read(P/'evidence/FINITE.json'),'committed finite receipt')
    if not a.finite_only:
        from verify_release import check
        check(result)
    print(result['status'],result['kappa'],'controls',len(result['controls']),flush=True)

if __name__=='__main__':main()

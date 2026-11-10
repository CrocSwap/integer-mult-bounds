"""Exact semantic task comparison against the selected6030 native inventory.

Retains Matarener/Clear1nsight native literal and dense machinery pinned in
SOURCES.json. This driver does not import a current compiler or scalar replay.
It compares full signed Pauli conjugation AND the complete exact U|0> column.
No tableau-only equivalence, frame-ID equivalence, or scalar-word tensorization.
thu-nmrc with substantial OpenAI Codex assistance, Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256,sha1
from functools import lru_cache
import argparse
import gzip
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent


def need(ok,why):
    if not ok:raise ValueError(why)


def read(name):
    b=(HERE/name).read_bytes()
    return json.loads(gzip.decompress(b)if name.endswith('.gz')else b)


def authenticate():
    pins=read('SOURCES.json')
    for p in pins['files']:
        b=(HERE/p['copy']).read_bytes()
        need(len(b)==p['bytes'] and sha256(b).hexdigest()==p['sha256'],'source SHA '+p['copy'])
        need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==p['git_blob'],'source blob '+p['copy'])
    old=read('inputs/6030-REUSE.json')['files']
    need(sha256((HERE/'inputs/6030-WORD.json.gz').read_bytes()).hexdigest()==
         old['research/p104-helper470-twin-rung-removal/WORD.json.gz'],
         'exact independently admitted6030 word')
    return len(pins['files'])


def load(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/'vendor'/file)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module


def inventory(w):
    main=set(w['live'])|{r+112 for r in w['live']}
    tasks={('move',e[2],e[3],0)for e in w['program']if e[0]=='MOVE'}
    tasks|={('helper',w['initial'][r],w['final'][r],0)for r in range(w['public'])if r not in main}
    tasks|={('main_in',w['initial'][r],0,q)for r,q in zip(w['live'],w['ports'])}
    tasks|={('main_out',w['final'][r+112],0,q)for r,q in zip(w['live'],w['ports'])}
    return sorted(tasks)


def binary_rank(rows):
    pivots={}
    for x in rows:
        while x:
            p=x.bit_length()-1
            if p not in pivots:pivots[p]=x;break
            x^=pivots[p]
    return len(pivots)


def run():
    pins=authenticate();old=read('inputs/6030-WORD.json.gz');new=read('inputs/CURRENT-WORD.json.gz')
    V=load('selected_literal','literal.py');D=load('selected_dense','dense.py')
    @lru_cache(None)
    def frame(v):return V.frame(v,9)
    def circuit(w,t):
        kind,a,b,q=t
        if kind in ('move','helper'):
            return V.adjoint(frame(tuple(w['frames'][a])))+frame(tuple(w['frames'][b]))
        if kind=='main_in':return V.adjoint((('C',q,1),))+frame(tuple(w['frames'][a]))
        return V.adjoint(frame(tuple(w['frames'][a])))+(('C',q,-1),)+V.fourier(9)
    @lru_cache(None)
    def normal(c):
        tab=V.tableau(c)
        real,imag,den=D.dense_column(D.compile_circuit(c),0)
        need(sum(x*x+y*y for x,y in zip(real,imag))==1<<(2*den),'exact nonzero unit zero column')
        entries=tuple((i,x,y)for i,(x,y)in enumerate(zip(real,imag))if x or y)
        return tab,den,entries
    def declared(w,t):
        return abs(len(w['frames'][t[1]])-len(w['frames'][t[2]]))if t[0]in('move','helper')else 0
    def collect(w):
        records=[];forms={}
        for t in inventory(w):
            c=circuit(w,t);n=normal(c);rank=binary_rank([x for x,z,p in n[0][9:]])
            need(rank==declared(w,t),'actual semantic Gaussian rank equals paid/adapter rank')
            # Equality and dedup use full tuples; hashes are custody labels only.
            forms.setdefault(n,[]).append(t)
            records.append((t,n,rank))
        return records,forms
    a,am=collect(old);b,bm=collect(new)
    witnesses=[];unmatched=[]
    for t,n,r in b:
        digest=sha256(json.dumps(n,separators=(',',':')).encode()).hexdigest()
        if n in am:
            old_rank=declared(old,am[n][0]);need(r==old_rank,'same exact operator keeps selected paid Gaussian rank')
            witnesses.append({'current':list(t),'selected6030_witness':list(am[n][0]),'rank':r,'selected_recipe_rank':old_rank,'normal_form_sha256':digest})
        else:
            unmatched.append({'current':list(t),'rank':r,'normal_form_sha256':digest,
                'signed_pauli':n[0],'zero_column_denominator':n[1],'zero_column':n[2]})
    unique_unmatched={n for t,n,r in b if n not in am}
    # A phase-only change has identical conjugation but a different full state.
    example=circuit(new,b[0][0]);actual=normal(example);wrong=normal(example+(('phase',1),))
    need(actual[0]==wrong[0] and actual!=wrong,'absolute phase distinguishes tableau-identical operators')
    # The exact signature can also identify a native task despite changed IDs.
    return {'schema':'native-semantic-map-comparison/1','status':'PASS_EXACT_OPERATOR_SIGNATURE_COMPARISON',
        'source_pins':pins,'selected6030_raw_tasks':len(a),'current_raw_tasks':len(b),
        'selected6030_distinct_operators':len(am),'current_distinct_operators':len(bm),
        'matched_current_tasks':len(witnesses),'unmatched_current_tasks':len(unmatched),
        'matched_current_distinct_operators':len(set(bm)&set(am)),
        'all_current_main_adapters_matched':all(n in am for t,n,r in b if t[0]in('main_in','main_out')),
        'unmatched_current_distinct_operators':len(unique_unmatched),
        'selected_internal_pairs':len({(t[1],t[2])for t,n,r in a if t[0]in('move','helper')}),
        'current_internal_pairs':len({(t[1],t[2])for t,n,r in b if t[0]in('move','helper')}),
        'matched':witnesses,'unmatched':unmatched,
        'phase_only_control_rejected':True,'literal_circuits_evaluated':normal.cache_info().misses,
        'semantic_rule':'Full signed Pauli conjugation plus exact nonzero U|0> determines a Clifford including global phase. Equality is individual exact matrix equality, hence equality of its literal columnwise tensor powers for every f. No scalar linear-combination word is tensorized.',
        'limits':'This driver has not checked current compiler recipes or complete current native scalar endpoints; those require a separate narrow check. The five framework assumptions and external scientific application decision are unchanged.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    result=run();raw=json.dumps(result,sort_keys=True,indent=2)+'\n';path=HERE/'COMPARISON.json'
    if a.write:path.write_text(raw)
    else:need(path.read_text()==raw,'read-only semantic comparison receipt')
    print(json.dumps({k:result[k]for k in ['status','selected6030_raw_tasks','current_raw_tasks','matched_current_tasks','unmatched_current_tasks','unmatched_current_distinct_operators']},sort_keys=True))

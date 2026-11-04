"""Read-only exact controls of the physical delayed-cover routing tables.

Fixtures and the coordinate oracle may inspect simulated tapes. Executed
programs cannot: their only operations are seven-symbol microinstructions.
Author-side evidence, not a Gaussian implementation or scientific admission.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from itertools import product

HERE=Path(__file__).resolve().parent


def authenticate():
    for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
        raw=(HERE/pin['local']).read_bytes()
        if len(raw)!=pin['bytes'] or hashlib.sha256(raw).hexdigest()!=pin['sha256']:
            raise ValueError('Exact retained predecessor: '+pin['local'])
        if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=pin['git_blob']:
            raise ValueError('Retained original blob: '+pin['local'])


# Authenticate retained executable inputs before importing them. The explicit
# package path also supports Python isolated mode without ambient imports.
authenticate()
sys.path.insert(0,str(HERE))
from machine import BLANK, LEFT, RIGHT, ZERO, ONE, Tape, Machine, marked, binary, need
import router


def content(tape):
    # Fixture observer only; no emitted instruction calls this function.
    need(tape.head==1 and tape.read() in (ZERO,ONE,RIGHT),'Output origin')
    out=[];j=1
    while tape.cells.get(j,BLANK)!=RIGHT:
        need(tape.cells.get(j,BLANK) in (ZERO,ONE),'Contiguous opaque output')
        out.append(tape.cells[j]);j+=1
    return out


def fixtures(L,A,R,pattern):
    p=router.ports(L);V=L*A*R
    values=[ZERO if pattern==0 else ONE if pattern==1 else
            (ONE if ((i*i+7*i+3)^(i>>2)).bit_count()%2 else ZERO) for i in range(V)]
    # A coordinate-product oracle; no emitted block-copy loop is consulted.
    expected={l:[] for l in range(L)}
    for a,l,r in product(range(A),range(L),range(R)):
        expected[l].append(values[(a*L+l)*R+r])
    tapes={p['source']:marked(values),p['repeats_input']:binary(A),p['block_input']:binary(R)}
    protected={k:(dict(t.cells),t.head) for k,t in tapes.items()}
    for t in tapes.values():t.cells[-19]=ONE;t.cells[-18]=ZERO
    protected={k:(dict(t.cells),t.head) for k,t in tapes.items()}
    bounds=router.resource_bound(L,A,R)
    split=Machine(router.build(L),tapes).run(bounds['microsteps'])
    for k,(cells,head) in protected.items():
        need(split.tapes[k].cells==cells and split.tapes[k].head==head,'Preserved split input/descriptor')
    for l in range(L):need(content(split.tapes[l])==expected[l],'Whole arbitrary bank oracle')
    for k in (p['repeats'],p['block'],p['binary_work']):
        need(split.tapes[k].cells=={} and split.tapes[k].head==0,'No scratch body or marker survives')
    need(split.steps<=bounds['microsteps'],'Split time bound')
    span=sum(max(s)-min(s)+1 for s in split.visits if s)
    need(span<=bounds['visited_span'],'Split visited-high-water bound')
    # The merge fixture uses changed arbitrary bank data, not just the original
    # split values, so returning the old parent input cannot pass.
    changed={l:[ONE if x==ZERO else ZERO for x in expected[l]] if l%2==0 else expected[l][:]
             for l in range(L)}
    merged_expected=[changed[l][a*R+r] for a,l,r in product(range(A),range(L),range(R))]
    mt={l:marked(changed[l]) for l in range(L)}
    mt[p['repeats_input']]=binary(A);mt[p['block_input']]=binary(R)
    before={k:(dict(t.cells),t.head) for k,t in mt.items()}
    merge=Machine(router.build(L,merge=True),mt).run(bounds['microsteps'])
    need(content(merge.tapes[p['output']])==merged_expected,'Changed child outputs returned to exact parent order')
    for k,(cells,head) in before.items():
        need(merge.tapes[k].cells==cells and merge.tapes[k].head==head,'Merge inputs preserved')
    for k in (p['repeats'],p['block'],p['binary_work']):
        need(merge.tapes[k].cells=={} and merge.tapes[k].head==0,'Merge scratch cleared')
    merge_span=sum(max(s)-min(s)+1 for s in merge.visits if s)
    need(merge.steps<=bounds['microsteps'] and merge_span<=bounds['visited_span'],'Merge resource bounds')
    return {'L':L,'A':A,'R':R,'pattern':pattern,'volume':V,'split_steps':split.steps,
            'merge_steps':merge.steps,'split_visited_span':span,'merge_visited_span':merge_span}


def source_binding():
    # Compare actual TM address outputs with the predecessor's independently
    # encoded Euclidean-division maps, retaining every ancestor high matrix.
    spec=importlib.util.spec_from_file_location('retained_batch_layout',HERE/'inputs/BATCH-LAYOUT.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    cases=[]
    for L,H,D,T in [(2,1,3,1),(2,2,2,1),(3,2,2,2),(2,3,2,1)]:
        layout=m.Layout(L,H,D,T)
        for j in range(D):
            rows=layout.rows//L**j;bits=rows.bit_length()
            values=[ONE if i>>b&1 else ZERO for i in range(rows) for b in range(bits)]
            A=T*(L*H)**(D-j-1);R=H**(j+1)*bits;p=router.ports(L)
            need(A*L*R==len(values),'Exact current whole-batch volume')
            actual=Machine(router.build(L),{p['source']:marked(values),p['repeats_input']:binary(A),
                                          p['block_input']:binary(R)}).run(router.resource_bound(L,A,R)['microsteps'])
            for l in range(L):
                wanted=[]
                for child in range(rows//L):
                    parent=layout.join(l,child,j)
                    need(layout.split(parent,j)==(l,child),'Retained source map inverse')
                    wanted.extend(ONE if parent>>b&1 else ZERO for b in range(bits))
                need(content(actual.tapes[l])==wanted,'Physical table equals retained full-address map')
            cases.append({'L':L,'H':H,'D':D,'T':T,'j':j,'parent_rows':rows,'label_bits':bits,
                          'A':A,'R':R,'physical_steps':actual.steps})
    return {'status':'physical_table_matches_retained_exact_address_maps','cases':cases,
            'source':'PR5829 whole-high-matrix allocation lemma',
            'parent_row':'(U_prime*(L*H)+l*H+h)*H^j+ancestor',
            'child_row':'(U_prime*H+h)*H^j+ancestor',
            'runtime_repeats':'T*(L*H)^(D-j-1)',
            'runtime_block_bits':'H^(j+1)*R_body',
            'child_volume':'V_parent/L; no high matrix or original input dropped'}


def mutations():
    from machine import Rejected
    p=router.ports(2);good=[ZERO,ONE,ZERO,ONE,ONE,ZERO,ONE,ZERO]
    def run(t):return Machine(router.build(2),t).run(10000)
    def base():return {p['source']:marked(good),p['repeats_input']:binary(2),p['block_input']:binary(2)}
    bad=[]
    t=base();t[p['source']]=marked(good[:-1]);bad.append(('short_source',t))
    t=base();t[p['source']]=marked(good+[ONE]);bad.append(('long_source',t))
    t=base();t[p['source']].cells[3]=BLANK;bad.append(('interior_physical_hole',t))
    t=base();t[p['repeats_input']]=marked([ZERO]);bad.append(('zero_extent',t))
    t=base();t[p['block_input']]=marked([ONE,ZERO]);bad.append(('noncanonical_extent',t))
    t=base();t[0]=Tape({0:ONE});bad.append(('dirty_owned_output',t))
    labels=[]
    for label,t in bad:
        try:run(t)
        except Rejected:labels.append(label)
        else:raise ValueError('Invalid physical fixture accepted: '+label)
    return labels


def check():
    authenticate()
    cases=[fixtures(L,A,R,p) for L in (2,3,5) for A in (1,2,5)
           for R in (1,2,7,33) for p in (0,1,2)]
    # Actual GL2(F3) low types with two productive roles, and all q^(4(w-1))
    # high matrices at w=2. L is a compile-time constant, H remains runtime.
    cases.append(fixtures(96,1,81,2))
    cases.append(fixtures(2,7,257,2))
    programs={}
    for L in (2,3,5,96):
        pair=[]
        for merge in (False,True):
            pg=router.build(L,merge)
            raw=json.dumps(pg.instructions,separators=(',',':')).encode()
            pair.append({'direction':'merge' if merge else 'split','microinstructions':len(pg.instructions),
                         'sha256':hashlib.sha256(raw).hexdigest()})
        programs[str(L)]={'tapes':L+7,'tables':pair}
    serialized={str(L):{'split':router.build(L).instructions,'merge':router.build(L,True).instructions,
                        'tapes':router.ports(L)['count']} for L in (2,3,5,96)}
    need(json.loads(json.dumps(serialized))==json.loads((HERE/'TABLES.json').read_text()),
         'Exact complete finite fixture tables')
    return {'status':'PASS_PHYSICAL_DELAYED_COVER_BATCH_ROUTER','case_count':len(cases),
            'cases':cases,'programs':programs,'controls':mutations(),'binding':source_binding(),
            'scope':'Real finite microinstruction split/merge; no Gaussian child, generated-weight evaluator, full production dispatcher, kappa or global assumption discharge.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');a=parser.parse_args()
    r=check();dest=HERE/'RESULT.json'
    if a.write:dest.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    else:need(r==json.loads(dest.read_text()),'Exact frozen physical-router receipt')
    print(json.dumps({'status':r['status'],'cases':r['case_count'],'controls':len(r['controls']),
                      'max_volume':max(x['volume'] for x in r['cases'])}))

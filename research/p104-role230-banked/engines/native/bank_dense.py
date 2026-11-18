#!/usr/bin/env python3
"""Fresh held-array projections of the #7674 parent and role-230 bank graphs."""

import argparse
from fractions import Fraction
from functools import cache
from pathlib import Path
from random import Random
import runpy
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import bank_phase as phase
from custody import need,read,sha


FIELD_PIN = 'e76bc78b132607890b2d9ea234d3a52e608e0e919bdc48308cc0727a2a07c73e'
RECEIPT = 'progress.kappa-leading-20261118t0540z.00000034'
SEED = {1000000009:11,998244353:37}
FAULT_SLOT = 97471
WIDTH=512


def compiled_bank_recipes(directory, certificate, parent, child, mains):
    for name,pin in certificate['artifact_sha256'].items():
        need(sha((directory/name).read_bytes())==pin,'phase component artifact bytes')
    ps,ph,_ = phase.graph_census(parent,mains)
    cs,ch,_ = phase.graph_census(child,mains)
    union = ps.keys()|ph.keys()|cs.keys()|ch.keys()
    records = read(directory/'BANK-RECIPES.json.gz')
    recipe = {}
    for row in records:
        a,b = row['pair']
        if row['in_forward_union']:
            need((a,b) in union and (a,b) not in recipe and row['compared_signed_pauli_and_absolute_phase'],
                 'physically fixed used body against union')
            need((row['peer_moves'],row['candidate_moves'],row['productive_roles']) ==
                 (ps.get((a,b),[]),cs.get((a,b),[]),ph.get((a,b),[])), 'actual per-slot bank and helper occurrences')
            recipe[a,b] = row['recipe']
    need(recipe.keys()==union and len(recipe)==certificate['forward_union'],'complete matched paid and target recipes')
    return recipe


def check(word,parent,child,recipes,prime,seed,checker,field_engine,run_faults):
    field = field_engine['GateInterpreter'](prime,need)
    digest = field_engine['digest']
    basis = word['frames']
    random = Random(seed)
    input_rows = [[random.randrange(prime) for _ in range(WIDTH)] for _ in range(word['public'])]
    pinned_public = digest(input_rows)

    @cache
    def chart(a):
        return checker.frame(basis[a],9)

    @cache
    def raw(a,b):
        if a==b:
            return ()
        return tuple(field.gate(op) for op in checker.adjoint(chart(a))+chart(b))

    @cache
    def compiled(a,b):
        return tuple(field.gate(op) for op in checker.recipe(recipes[a,b]))

    @cache
    def scalar(q):
        return field.coefficient(q)

    def add(dst,q,source):
        if q==1:
            return [(a+b)%prime for a,b in zip(dst,source,strict=True)]
        return [(a+q*b)%prime for a,b in zip(dst,source,strict=True)]

    def factor(q,source):
        return [q*a%prime for a in source]

    def column_controls():
        rows = []
        for a,b in (child.moves[97471],child.moves[102393]):
            compiled_gates = checker.recipe(recipes[a,b])
            target = checker.adjoint(chart(a))+chart(b)
            for direction in ('forward','adjoint'):
                actual,expected = ((compiled_gates,target) if direction=='forward' else
                                    (checker.adjoint(compiled_gates),checker.adjoint(target)))
                gates = tuple(field.gate(op) for op in actual)
                for col in (0,17):
                    unit = [0]*WIDTH
                    unit[col] = 1
                    need(field.apply(gates,unit)==field.column_residue(checker.state(expected,col)),
                         'compiled modular gate orientation against exact Gaussian independent column')
                    rows.append([a,b,direction,col])
        return rows

    def replay(g, fault=None):
        # Graph slots are distinct held banks. Keep the source accumulator and
        # returned snapshot separate until every scheduled terminal is present.
        sources, returned, terminal = {},{},{}
        bars = {~r:row for r,row in enumerate(input_rows)}
        term_count = 0
        for key in g.schedule:
            row=[0]*WIDTH
            for idx,(donor,q) in enumerate(g.forms[key]):
                if fault=='same-price sign' and key==FAULT_SLOT and idx==0:
                    q=-q
                row=add(row,scalar(q),bars[donor])
                term_count += 1
            sources[key]=row
            if key in g.moves:
                a,b=g.moves[key]
                response=field.apply(compiled(a,b),row)
                if fault=='quarter phase' and key==FAULT_SLOT:
                    response=factor(field.i,response)
                need(response is not row,'distinct paid source and returned snapshot')
                returned[key]=bars[key]=response
            else:
                terminal[key-g.first]=row
        n=len(input_rows)
        need(len(returned)==6142 and set(terminal)==set(range(n)) and len(sources)==7643,
             'actual separate paid and terminal banks for the full literal schedule')
        held = [*input_rows, *sources.values(), *returned.values()]
        need(len({id(v) for v in held})==len(held)==15286,'distinct actual VM arrays for all scheduled field banks')
        need(digest(input_rows)==pinned_public,'arbitrary independent input arrays remain intact')
        ports=[terminal[r] for r in range(n)]
        return ports,{'active_nodes':len(g.schedule),'paid_slots':len(g.moves),'terminal_rows':len(ports),
                     'local_scalar_terms':term_count,'independent_entry_banks':n,'distinct_scientific_held_arrays':len(held),
                     'terminal_arrays_sha256':digest(ports),'returns_sha256':digest([returned[k] for k in sorted(returned)])}

    initial,final = parent.initial,parent.final
    live,host = word['live'],word['hosted']
    x2,y2,dport = host['X2'],host['Y2'],set(host['Dports'])
    need(len(live)==104 and len(x2)==len(y2)==len(dport)==96,'real native caller slot geometry')
    mains = set(live)|{r+112 for r in live}|set(x2)|set(y2)

    def from_input(target,donor):
        return field.apply(raw(initial[donor],final[target]),input_rows[donor])

    def main_block(rows,r,s,a,b):
        rows[r]=add(from_input(r,r),scalar(a),from_input(r,s))
        rows[s]=add(factor(scalar(b),from_input(s,r)),scalar(1+a*b),from_input(s,s))

    expected = [None]*len(input_rows)
    alpha,beta,alpha2,beta2=(Fraction(host[name]) for name in ('alpha','beta','alpha2','beta2'))
    for j,x in enumerate(live):
        a,b=(0,1) if j in dport else (alpha,beta)
        main_block(expected,x,x+112,a,b)
    for x,y in zip(x2,y2,strict=True):
        main_block(expected,x,y,alpha2,beta2)
    for r in range(len(input_rows)):
        if r not in mains:
            expected[r]=from_input(r,r)

    controls = column_controls()
    left,lrec = replay(parent)
    right,rrec = replay(child)
    for label,rows in (('peer',left),('candidate',right)):
        mismatch = [r for r in range(len(expected)) if expected[r]!=rows[r]]
        need(not mismatch,f'{label} actual bank graph and independent main/helper physical maps disagree {mismatch[:8]}')
    need(left==right,'identical actual bank boundaries on the admitted projection')
    faults = {}
    if run_faults:
        for kind in ('quarter phase','same-price sign'):
            faulty,_=replay(child,kind)
            diff=[r for r in range(len(expected)) if faulty[r]!=expected[r]]
            need(diff,f'actual {kind} mutation must change a physical public endpoint')
            faults[kind]={'injected_slot':FAULT_SLOT,'changed_public_roles':diff}
    return {'status':'PASS_PAIRED_BANK24_ACTUAL_HELD_ARRAYS','prime':prime,'seed':seed,'imaginary_root':field.i,
            'width':WIDTH,'main_outputs':len(mains),'positive_helper_outputs':len(input_rows)-len(mains),
            'input_sha256':pinned_public,'independent_expected_sha256':digest(expected),
            'peer':lrec,'candidate':rrec,'actual_negative_controls':faults,'exact_column_links':controls,
            'helper_325_1087_boundaries':{r:[initial[r],final[r]] for r in (325,1087)},
            'scope':'Actual forward bank graph and independent direct public boundaries on dense prime projections. Private integer bit format, extent/reset/retirement and tariff are separate components.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--peer-package',type=Path,required=True)
    p.add_argument('--engine-dir',type=Path,required=True)
    p.add_argument('--field-engine',type=Path,required=True)
    p.add_argument('--graphs',type=Path,required=True)
    p.add_argument('--phase',type=Path,required=True)
    p.add_argument('--prime',type=int,choices=tuple(SEED),required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    a.out.mkdir()
    phase_path=a.phase/'RESULT.json'
    phase_sha=sha(phase_path.read_bytes())
    start={'observed_at':phase.stamp(),'phase_sha256':phase_sha,'prime':a.prime,
           'program_sha256':sha(Path(__file__).read_bytes()),'scope':RECEIPT}
    phase.write(a.out/'START.json',start)
    receipt=read(phase_path,phase_sha)
    need(receipt['status']=='PASS_PAIRED_BANK24_EXACT_NATIVE_MAPS','complete exact paired phase component')
    word,parent,child,binding,_,_,mains=phase.graph_inputs(a.peer_package,a.graphs,receipt['graph_pins'])
    recipes=compiled_bank_recipes(a.phase,receipt,parent,child,mains)
    _,checker=phase.engine_pair(a.engine_dir)
    need(sha(a.field_engine.read_bytes())==FIELD_PIN,'exact dense modular interpreter source')
    projector=runpy.run_path(str(a.field_engine))
    result=check(word,parent,child,recipes,a.prime,SEED[a.prime],checker,projector,a.prime==1000000009)
    need(sha(phase_path.read_bytes())==phase_sha and sha(a.field_engine.read_bytes())==FIELD_PIN,'immutable field and catalogue')
    for kind,r in binding['graphs'].items():
        need(sha((a.graphs/r['file']).read_bytes())==r['gzip_sha256'],f'immutable {kind} scientific graph at exit')
    phase.write(a.out/'RESULT.json',{**start,**result,'completed_at':phase.stamp(),'graph_pins':receipt['graph_pins'],
                                   'exact_caller_sha256':phase.DEC_CALLER})
    print('PASS_PAIRED_BANK24_ACTUAL_HELD_ARRAYS',a.prime,1501,6142,flush=True)


if __name__=='__main__':
    main()

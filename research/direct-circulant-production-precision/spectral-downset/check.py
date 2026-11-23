#!/usr/bin/env python3
"""Bounded exact source checks for the sharper unchanged-word analysis.

The universal result is the written proof. The inherited first-wave audit
supplies independent rational matrices; source compiler factories remain the
retained implementation being checked, not the mathematical norm oracle.
"""

import argparse
import ast
from dataclasses import asdict
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent


def need(ok,why):
    if not ok:
        raise ValueError(why)


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def exact_constants():
    need(3200*2318==7417600<2**23,'Actual child constant')
    need(1+2+7+23==33 and 1+3+7==11,'Physical original cuts')
    need(1+2*7+2*23==61 and 2*3+2*7==20,'Relative gate envelope')
    need(2+33+240+1+61==337 and 11+20==31,'Routed root envelope')
    need(2+2*337==676 and 2+2*31==64,'Two-root axis envelope')
    need(2*676+2==1354 and 2*64==128,'Tensor interval exponent')
    need(240+1+61==302 and 302+1==303,'Joined scalar coefficient')
    need(20+257==277 and 303+2*1354==3011,'Selector linear terms')
    return {'B':[7,3],'H':[23,7],'K':[33,11],'G':[61,20],
            'routed_root':[337,31],'axis':[676,64],
            'selector_L':277,'selector_d':3011}


def allocator_cases(modules):
    count,children=0,0
    full,gen=modules['full'],modules['generator']
    for ell in range(1,21):
        t=1<<ell
        for r in sorted({2,t,max(2,t-1)}):
            for p in (1,17):
                old=full.allocation(t,4*t,8*t*r,2*t,p+8,0)
                bnew=2**7*t**3
                need(bnew<old['completed_prefix_bound'],'New B is below unchanged allocation')
                theta=(3*t-2)*bnew*bnew*old['eta']
                need(theta<=old['theta']<=Q(1,4),'Actual unchanged eta funds new downsets')
                need(old['eta']<=Q(1,8*t),'Old scalar grid funds spectral inverse bound')
                need(old['coefficient_error']<=Q(1,1<<(p+8)),'Original exact-word defect retained')
                count+=1
        for m in sorted({1,t//2,t}):
            for rank in sorted({0,min(m,2*ell+8)}):
                child,_=gen.allocation(m,rank,32*t*t,1,old['child_target_bits'],0)
                need(child['alpha']<=320*t**4 and child['kg']<=514*t**3,
                     'Literal generator parameter envelopes')
                need(child['execution_bound']<=2**23*t**7,'Literal child fragment bound')
                children+=1
    return {'unchanged_full':count,'literal_child_allocations':children}


def authentic_parent(parent):
    manifest=json.loads((parent/'ORIGINS.json').read_text())
    matched=[]
    for row in manifest['files']:
        if row['file'] not in ('root_gate_plan.py','spectral.py','product.py'):
            continue
        data=(parent/'retained'/row['file']).read_bytes()
        need(sha256(data).hexdigest()==row['sha256'],'Parent source SHA256 '+row['file'])
        matched.append(row['file'])
    need(set(matched)=={'root_gate_plan.py','spectral.py','product.py'},'Required parent sources pinned')
    return matched


def padded_roots(parent,audit,modules,raw):
    root=load(parent/'retained'/'root_gate_plan.py','root_gate_plan')
    spectral=load(parent/'retained'/'spectral.py','spectral')
    compiler=SimpleNamespace(**modules,raw=raw)
    results=[]
    for r,t,direction in ((2,2,1),(3,4,-1)):
        p=1
        turns=[Q(direction*j*(j+r),2*r) for j in range(r)]
        column,_=spectral.polar_root(compiler,[Q(1)]*r,turns,p+8,phase_grid=2*r)
        plan,builder=root.compile_padded_root(compiler,column.column,t,p+8,
                                            radius=2*t,margin=column.accretivity)
        _,matrix=root.padded_matrix(compiler,column.column,t)
        a=audit.matrix(matrix)
        need(audit.norm_at_most(a,2),'Independent actual root spectral cap')
        need(builder.bound['inverse_bound']==8*t*r,'Literal component inverse input retained')
        for k in range(1,t+1):
            leading=[row[:k] for row in a[:k]]
            ai=audit.inverse(leading)
            need(audit.norm_at_most(ai,4*t),'Independent actual leading spectral inverse cap')
        children=[]
        for atom in plan.atoms:
            if atom['kind']=='leaf':
                continue
            shear=audit.matrix(atom['ideal'])
            need(audit.norm_at_most(shear,8*t),'Independent source split spectral cap')
            child=atom['program'].bound
            need(child['displacement_bound']<=32*t*t,'Actual forwarded displacement component bound')
            need(child['execution_bound']<=2**23*t**7,'Actual prepared child cap')
            children.append({'id':atom['id'],'rank':child['rank'],
                             'be':str(child['displacement_bound']),
                             'fragment':str(child['execution_bound'])})
        bnew=2**7*t**3
        theta=(3*t-2)*bnew*bnew*builder.bound['eta']
        need(theta<=builder.bound['theta']<=Q(1,4),'Actual padded factory new perturbation budget')
        toeplitz=all(a[i][j]==(a[i-j][0] if i>=j else a[0][j-i])
                     for i in range(t) for j in range(t))
        if r<t:
            need(not toeplitz,'Padding fixture must exercise the non-Toeplitz bridge')
        results.append({'r':r,'t':t,'direction':direction,'target':p+8,
                        'layers':len(plan),'atoms':len(plan.atoms),'padded_non_toeplitz':not toeplitz,
                        'theta_new':str(theta),'actual_children':children})
    return results


def selectors(parent):
    new=load(HERE/'precision.py','sharp_precision')
    old=load(parent/'precision.py','parent_precision')
    source=ast.parse((parent/'retained'/'product.py').read_text())
    node=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='production_precision')
    namespace={}
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<pinned original selector>','exec'),namespace)
    original=namespace['production_precision']
    cases=[(30,(1,)),(72,(4,5)),(12288,(128,)*16),
           (6000000,(100000,)*10),(6*10**40,(10**40,))]
    for d in range(1,9):
        for w in (1,2,3,8,17,64):
            widths=tuple(1+(i*7)%w for i in range(d))
            cases.append((6*(sum(widths)+3),widths))
    examples=[]
    for p,widths in cases:
        row=new.precision_budget(p,widths)
        previous=old.precision_budget(p,widths)
        c=row.envelope_coefficient
        k=c.bit_length()
        need(Q(c,1<<k)<1,'Strict raw-error margin')
        need(Q(row.stage_bound*(row.axes+1)**2,1<<k)<Q(1,4),'Noncircular bootstrap')
        need(row.fractional_bits==4*p+277*sum(widths)+3011*len(widths)+(sum(widths)%2)+k,
             'Independent simplified selector expression')
        need(previous.fractional_bits-row.fractional_bits==1084*sum(widths)+1735*len(widths),
             'Exact predecessor selector reduction')
        need(2*Q(c,1<<k)>=1,'A one-bit undercharge must lose this certified envelope')
        if len(examples)<5:
            examples.append({'p':p,'widths':list(widths),'original':original(p,widths),
                             'previous':previous.fractional_bits,'new':row.fractional_bits})
    for p,widths in ((0,(1,)),(1,()),(1,(0,)),(True,(1,)),(1,(True,))):
        try:
            new.precision_budget(p,widths)
        except ValueError:
            pass
        else:
            raise ValueError('Malformed precision input accepted')
    need(new.production_precision(72,(4,5))==8842,'Recorded comparison')
    return {'cases':len(cases),'examples':examples}


def controls(audit,modules):
    swap=audit.matrix([[0,1],[1,0]])
    need(audit.norm_at_most(audit.inverse(swap),1),'Whole swap inverse is bounded')
    try:
        audit.inverse([[swap[0][0]]])
    except ValueError:
        pass
    else:
        raise ValueError('Whole-inverse-only admission was not rejected')
    unit=audit.matrix([[Q(3,5),Q(4,5)],[-Q(4,5),Q(3,5)]])
    need(audit.norm_at_most(unit,1),'Rational rotation spectral cap')
    components=max(sum(abs(x.re)+abs(x.im) for x in row) for row in unit)
    need(components==Q(7,5)>1,'Spectral bound is not the stronger component envelope')
    return ['whole-matrix inverse does not fund every leading section',
            'unit spectral norm does not imply unit component row/column envelope',
            'one-bit raw-error undercharge loses the strict certified envelope',
            'empty, nonpositive and boolean precision inputs reject']


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--parent',type=Path,default=HERE.parent)
    parser.add_argument('--cuts',type=Path,default=HERE.parent/'compiler-cuts')
    args=parser.parse_args()
    parent=args.parent.resolve()
    authenticate=authentic_parent(parent)
    audit=load(args.cuts.resolve()/'audit.py','_source_cut_audit')
    modules,raw,count=audit.load_source()
    result={'status':'PASS_SPECTRAL_DOWNSET_CIRCULANT_PRECISION',
            'inherited_inputs':count,'additional_parent_inputs':authenticate,
            'constants':exact_constants(),'allocation_cases':allocator_cases(modules),
            'actual_padded_roots':padded_roots(parent,audit,modules,raw),
            'selectors':selectors(parent),'negative_controls':controls(audit,modules),
            'scope':'Finite binding checks; universal written theorem retains phase, rank, native and source contracts.'}
    (HERE/'EVIDENCE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'allocation_cases':result['allocation_cases'],
                      'actual_padded_roots':len(result['actual_padded_roots']),
                      'selector_cases':result['selectors']['cases']},sort_keys=True))


if __name__=='__main__':
    main()

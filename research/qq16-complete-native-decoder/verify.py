#!/usr/bin/env python3
"""Complete native QQ16 decoder with charged temporal ownership.

New composition by ywz65 with OpenAI Codex assistance, Apache-2.0.
PR2511 logical decoder and PR2512 native machinery are explicitly credited.
No complete supplier or physical tape/precision bound is claimed.
"""
import argparse
import ast
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import gzip
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('complete_native_checks', HERE/'native_checks.py')
NC = importlib.util.module_from_spec(spec)
spec.loader.exec_module(NC)
N, need = NC.N, NC.need
V = N.A + N.T
OLD = tuple((e, 1) for e in N.AXES[:9])
PRIVATE = ['C'] + [f'{side}{k}' for side in ('F','G') for k in range(8)]


def f(side,p):
    return side+str(p)


def program(R):
    out=[]
    def emit(op, **kw):
        out.append(dict(op=op,**kw))
    def clear(name,frame='current'):
        emit('clear',field=name,frame=frame)
    def add(dst,src,q=1):
        emit('add',dst=dst,src=src,coefficient=str(q))
    # Actual time: capture selected X after F0, before B1 changes those fields.
    for p in V:
        clear(f('R',p),'old')
        add(f('R',p),f('X',p))
    emit('history_boundary',name='complete_B1_with_retained_R_untouched')
    # Owned eventual X outputs receive the early record; early R stays old-frame.
    for p in V:
        clear(f('Z',p),'old')
        add(f('Z',p),f('R',p))
        emit('stage',field=f('Z',p),rank=8,sign=1)
    for p in N.U:
        emit('line',field=f('Y',p),port=p,sign=1)
        clear(f('Z',p))
        add(f('Z',p),f('X',p))
        add(f('Z',p),f('Y',p))
        emit('line',field=f('Y',p),port=p,sign=-1)
    for p in N.U + N.T:
        emit('current_map',field=f('Z',p),port=p,inverse=False)
    emit('private_begin',name='L2',fields=['C'])
    for k in range(8):
        clear('C')
        for p in N.T:
            if R[k][p]: add('C',f('Z',p),R[k][p])
        for p in N.U:
            if R[k][p]: add(f('Z',p),'C',-R[k][p]/4)
        clear('C','identity')
    emit('private_end',name='L2',fields=['C'])
    for p in N.U + N.T:
        emit('current_map',field=f('Z',p),port=p,inverse=True)
    emit('checkpoint',name='all_x1_in_current_frame')
    # F0's actual owner chart is identity: all following ADDs are local.
    fields=[f(side,k) for side in ('F','G') for k in range(8)]
    emit('private_begin',name='F0_inverse',fields=fields)
    for k in range(8):
        clear(f('F',k)); clear(f('G',k))
        for p in N.T:
            if R[k][p]: add(f('F',k),f('Z',p),R[k][p])
        for p in N.A:
            if R[k][p]: add(f('G',k),f('Z',p),R[k][p])
    for p in N.U:
        for k in range(8):
            if R[k][p]: add(f('Z',p),f('F',k),R[k][p]/4)
    for k in range(8):
        add(f('F',k),f('G',k),-1)
        for p in N.U:
            if R[k][p]: add(f('F',k),f('Z',p),-R[k][p])
    for p in V:
        clear(f('Z',p))
        for k in range(8):
            if R[k][p]: add(f('Z',p),f('F' if p in N.A else 'G',k),R[k][p]/4)
    for name in fields: clear(name,'identity')
    emit('private_end',name='F0_inverse',fields=fields)
    emit('checkpoint',name='all_original_x_in_current_frame')
    # Directly construct eventual Y outputs; no separate selected-sum bank.
    for p in N.U:
        clear(f('W',p)); add(f('W',p),f('X',p),-1)
    for p in V:
        emit('line',field=f('Y',p),port=p,sign=1)
        clear(f('W',p))
        add(f('W',p),f('X',p)); add(f('W',p),f('Y',p))
        emit('line',field=f('Y',p),port=p,sign=-1)
        add(f('W',p),f('Z',p),-1)
    # R is owned retained storage. It is retired only after its last read.
    for p in V: clear(f('R',p),'old')
    return out


def logical_reference():
    """Load authenticated, unchanged PR2511 proof checker; reuse is explicit."""
    path=HERE/'vendor/pr2511/audit.py'
    spec=importlib.util.spec_from_file_location('retained_2511_audit',path)
    audit=importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(),str(path),'exec'),audit.__dict__)
    audit.ROOT=ROOT
    o,m,raw,bindings=audit.load()
    need(all(o.MAPS[m.route(0,p)]==(N.AXES,0) for p in range(112)), 'actual identity F0 owner chart')
    packet=json.loads(gzip.decompress(raw['research/joint-query/certificate.json.gz']))
    need(not any(e[0]=='cover_map' for e in packet['programs']['F_0']), 'literal F0 has no cover maps')
    need(N.phase(tuple(map(tuple,packet['native_frame_registry']['f1']['line_terms_Z4'])))==N.phase(OLD),
         'actual F0 common FULL9 source frame')
    # Reference decoder consumes 16 early + 208 observations. Its live sums
    # are formed from 224 physical current symbols, preserving that boundary.
    source={f('E',p):o.variable(j) for j,p in enumerate(V)}
    source.update({f('X',p):o.variable(16+p) for p in range(112)})
    source.update({f('Y',p):o.variable(128+p) for p in range(112)})
    observed=({p:source[f('E',p)] for p in V},
              {p:source[f('X',p)] for p in N.U},
              {p:source[f('Y',p)] for p in N.U},
              {p:o.combine((1,source[f('X',p)]),(1,source[f('Y',p)])) for p in V})
    expected=audit.decode(o,m,observed)
    name_by_index={index: name for name,row in source.items() for (index,_),c in row.items()}
    def convert(row):
        converted={}
        for (index,mapid),coefficient in row.items():
            matrix,shift=o.MAPS[mapid]
            need(shift==0,'logical reference has no payload translation')
            converted[(name_by_index[index],matrix)]=coefficient
        return converted
    expected={f(side,p):convert(bank[p]) for side,bank in zip(('Z','W'),expected) for p in range(112)}
    original=o.independent_pair()
    observed_original=audit.observe(o,m,original)
    need(audit.decode(o,m,observed_original)==original,'retained full original-input inverse')
    free=audit.free(o)
    need(audit.observe(o,m,audit.decode(o,m,free))==free,'retained free-observation inverse')
    return expected,bindings


def replay(word,R,records,expected):
    owned={f(side,p) for side in ('Z','W') for p in range(112)}|{f('R',p) for p in V}
    frames={name:() for name in owned}
    frames.update({f('X',p):OLD for p in V})
    rows={name:{(name,N.AXES):Q(1)} for name in owned}
    rows.update({f('X',p):{(f('E',p),N.AXES):Q(1)} for p in V})
    after_boundary=False
    active=set()
    counts=Counter()
    for index,e in enumerate(word):
        op=e['op']; counts[op]+=1
        if op=='history_boundary':
            need(not after_boundary and not active,'one temporal boundary')
            for p in V:
                need(rows[f('X',p)]==rows[f('R',p)]=={(f('E',p),N.AXES):Q(1)},'early capture and source unchanged')
                need(N.phase(frames[f('R',p)])==N.phase(OLD),'retained early frame')
            # This marker denotes the inherited completed B1 execution, not a
            # zero-cost decoder gate. Its own cost is outside this added invoice.
            for p in range(112):
                for side in ('X','Y'):
                    name=f(side,p)
                    frames[name]=N.START+(((records[p]['q'],-1),) if side=='Y' else ())
                    rows[name]={(name,N.AXES):Q(1)}
            after_boundary=True
        elif op=='private_begin':
            need(after_boundary and not active,'private owner schedule')
            active=set(e['fields'])
            need(active<=set(PRIVATE),'known owned scratch')
            for name in active:
                frames[name]=()
                rows[name]={(name,N.AXES):Q(1)}
        elif op=='private_end':
            need(active==set(e['fields']),'private scope boundary')
            need(all(not rows[name] and not frames[name] for name in active),'private scratch fully cleaned')
            for name in active:
                del rows[name],frames[name]
            active=set()
        elif op=='clear':
            name=e['field']
            need(name in owned|active,'clear only owned fields')
            rows[name]={}
            frames[name]={'current':N.START,'old':OLD,'identity':()}[e['frame']]
        elif op=='add':
            dst,src=e['dst'],e['src']
            need(dst in owned|active,'borrowed destination forbidden')
            need(dst in rows and src in rows and dst!=src,'valid live ADD roles')
            need(N.phase(frames[dst])==N.phase(frames[src]),'ADD frame mismatch at '+str(index))
            rows[dst]=N.combine(rows[dst],rows[src],Q(e['coefficient']))
        elif op=='line':
            name=e['field'];p=e['port']
            need(after_boundary and name==f('Y',p) and e['sign'] in (-1,1),'borrowed Y line')
            frames[name]+=((records[p]['q'],e['sign']),)
        elif op=='stage':
            need(e['field'] in owned and e['rank']==8 and e['sign'] in (-1,1),'owned native stage')
            frames[e['field']]+=tuple((axis,e['sign']) for axis in N.AXES[9:17])
        elif op=='current_map':
            need(not active and e['field'] in owned,'whole cover outside private body')
            rec=records[e['port']]; g=rec['g']
            b=rec['shift']^rec['inverse_shift']
            if e.get('use_old_shift'): b=rec['shift']
            if e.get('omit_translation'): b=0
            if e['inverse']: b=N.act(g,b)
            frames[e['field']]=N.move_frame(frames[e['field']],(g,b))
            rows[e['field']]=N.routed(g,rows[e['field']])
        elif op=='checkpoint':
            need(not active,'checkpoint after complete sweep')
            need(all(N.phase(frames[f('Z',p)])==N.phase(N.START) for p in range(112)),'all X output frames')
            if e['name']=='all_x1_in_current_frame':
                for p in range(112):
                    want={(f('E',p),N.AXES):Q(1)} if p in V else {(f('X',p),N.AXES):Q(1),(f('Y',p),N.AXES):Q(1)}
                    if p in N.U:
                        for t in N.T:
                            c=-sum(R[k][p]*R[k][t] for k in range(8))/4
                            if c: want=N.combine(want,{(f('E',t),N.multiply(records[p]['g'],records[t]['g'])):c})
                    need(rows[f('Z',p)]==want,'L2 full x1 checkpoint')
            elif e['name']=='all_original_x_in_current_frame':
                need(all(rows[f('Z',p)]==expected[f('Z',p)] for p in range(112)),'full original X checkpoint')
        else:
            raise ValueError('unknown event')
    need(after_boundary and not active,'complete temporal word')
    for p in range(112):
        for side in ('X','Y'):
            name=f(side,p)
            want=N.START+(((records[p]['q'],-1),) if side=='Y' else ())
            need(rows[name]=={(name,N.AXES):Q(1)} and N.phase(frames[name])==N.phase(want),'borrowed source restoration')
        for side in ('Z','W'):
            name=f(side,p)
            need(rows[name]==expected[name],'complete decoder output '+name)
            need(N.phase(frames[name])==N.phase(N.START),'common current output frame')
    need(all(not rows[f('R',p)] and N.phase(frames[f('R',p)])==N.phase(OLD) for p in V),'owned early records retired')
    return dict(counts)


def scalar_invoice(word):
    path=ROOT/'research/joint-query/verify_scalar.py'
    tree=ast.parse(path.read_bytes())
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='scalar_cost']
    need(len(nodes)==1,'authenticated scalar cost')
    environment={'F':Q,'need':need}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),environment)
    total=0; profile=Counter()
    for e in word:
        if e['op']=='clear': total+=environment['scalar_cost'](['clear'])
        elif e['op']=='add':
            q=Q(e['coefficient']);profile[str(abs(q))]+=1
            total+=environment['scalar_cost'](['add',None,None,q.numerator,q.denominator])
    return total,dict(profile)


def calculate():
    R,records,pins=N.load_sources()
    expected,bindings=logical_reference()
    word=program(R)
    trace=replay(word,R,records,expected)
    selected={p:records[p] for p in N.U+N.T}
    maps=NC.current_maps(selected)
    phase=NC.direct_current_frame_checks(selected)
    kernels=NC.native_kernels(records)
    scalar,profile=scalar_invoice(word)
    controls={}
    def reject(label,mutation):
        bad=deepcopy(word);mutation(bad)
        try: replay(bad,R,records,expected)
        except (ValueError,KeyError) as error: controls[label]=str(error)
        else: raise ValueError('ineffective control '+label)
    def first(w,pred): return next(e for e in w if pred(e))
    reject('capture after B1',lambda w:w.insert(0,w.pop(next(i for i,e in enumerate(w) if e['op']=='history_boundary'))))
    reject('omit selected X upgrade',lambda w:w.remove(first(w,lambda e:e['op']=='stage')))
    reject('old payload alignment',lambda w:first(w,lambda e:e['op']=='current_map').__setitem__('use_old_shift',True))
    reject('omit payload translation',lambda w:first(w,lambda e:e['op']=='current_map').__setitem__('omit_translation',True))
    reject('wrong original Y sign',lambda w:first(w,lambda e:e['op']=='add' and e.get('dst')=='W1').__setitem__('coefficient','1'))
    reject('wrong inverse F0 source sign',lambda w:first(w,lambda e:e['op']=='add' and e.get('dst')=='F0' and e.get('src')=='G0').__setitem__('coefficient','1'))
    reject('missing selected sum normalization',lambda w:w.remove(first(w,lambda e:e['op']=='line' and e['port'] in V and e['sign']==1)))
    reject('missing selected Y restoration',lambda w:w.remove(first(w,lambda e:e['op']=='line' and e['port'] in V and e['sign']==-1)))
    reject('uncleared output dirt',lambda w:w.remove(first(w,lambda e:e['op']=='clear' and e['field']=='W0')))
    reject('unretired early record',lambda w:w.pop())
    reject('discard borrowed input',lambda w:first(w,lambda e:e['op']=='clear').__setitem__('field','X0'))
    reject('private scratch leak',lambda w:w.remove(next(e for e in reversed(w) if e['op']=='clear' and e['field']=='G7')))
    invoice={'rank_one_children':trace['line'],'rank_eight_children':trace['stage'],
             'native_rank_mass':trace['line']+8*trace['stage'],
             'native_wrappers':2*(trace['line']+trace['stage']),
             'full_cover_maps':trace['current_map'],'scalar_real_primitive_allowance':scalar,
             'absolute_ADD_coefficients':profile,'ADDs':trace['add'],'CLEARs':trace['clear'],
             'owned_full_cover_output_arrays':224,'owned_early_record_banks':16,
             'peak_local_owned_scratch_arrays':16,'restored_current_borrowed_arrays':224,
             'capture_ADDs':16,'capture_CLEARs':16,'retirement_CLEARs':16}
    result={'status':'PASS_QQ16_COMPLETE_NATIVE_DECODER','contract':'All224 original logical arrays in common F_U1; current224 borrowed arrays restored;16 owned early records retired; local scratch zero.',
            'trace':trace,'invoice':invoice,'controls':controls,'native_kernels':kernels,
            'current_maps':maps,'phase_checks':phase,'source_sha256':pins,'logical_bindings':bindings,
            'output_operator_sha256':hashlib.sha256(repr(sorted((r,sorted(v.items())) for r,v in expected.items())).encode()).hexdigest(),
            'limits':'Added finite local decoder invoice includes capture/retirement; inherited F0/B1 execution, physical retention/movement/precision/hosting and output consumer remain outside.'}
    return result,word


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='create absent receipts only')
    args=parser.parse_args()
    result,word=calculate()
    for name,value in [('RESULT.json',result),('WORD.json',word)]:
        path=HERE/name
        if args.write:
            with path.open('x',encoding='utf-8',newline='\n') as out:
                json.dump(value,out,indent=2,sort_keys=True);out.write('\n')
        else:
            need(json.loads(path.read_text(encoding='utf-8'))==json.loads(json.dumps(value)),'committed '+name+' differs')
    print(result['status'],json.dumps(result['invoice'],sort_keys=True),'no_new_kappa')

if __name__=='__main__':
    main()

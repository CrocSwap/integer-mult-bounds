"""Owner-aligned output-slice borrowing; formal algebra reused from PR2651.

The replay state machine is adapted from that credited source. The new part
is physical W-bank identity/liveness, without a hidden private allocation.
"""
from copy import deepcopy
from fractions import Fraction


def need(ok,why):
    if not ok:raise ValueError(why)


def transform(word):
    out=deepcopy(word);active={};windows=[]
    for i,e in enumerate(out):
        if e['op']=='private_begin':
            need(not active,'nonoverlapping source intervals')
            active=dict(zip(e['fields'],[f'W{j}' for j in range(len(e['fields']))]))
            need(len(active)==len(e['fields'])<=16,'bounded distinct private roles')
            begin=i
            e['op']='output_slices_begin';e['aliases']=active.copy()
            e['fields']=list(active.values())
        elif e['op']=='private_end':
            need(set(e['fields'])==set(active),'matching source interval')
            e['op']='output_slices_end';e['fields']=list(active.values())
            windows.append({'name':e['name'],'begin':begin,'end':i,'aliases':active.copy()})
            active={}
        elif active:
            need(e['op'] in ('add','clear'),'owner-local scalar-only body')
            for key in ('field','src','dst'):
                if key in e:e[key]=active.get(e[key],e[key])
    need(not active and len(windows)==2,'exact two source windows')
    for win in windows:
        for role in win['aliases']:
            uses=[e for e in word[win['begin']+1:win['end']]
                  if role in [e.get(k) for k in ('field','src','dst')]]
            need(uses and uses[0]=={'op':'clear','field':role,'frame':'current'}
                 and uses[-1]=={'op':'clear','field':role,'frame':'identity'},
                 'first and last scratch access are charged frame-clears')
        for bank in win['aliases'].values():
            uses=[(i,e) for i,e in enumerate(word)
                  if bank in [e.get(k) for k in ('field','src','dst')]]
            need(uses and uses[0][0]>win['end'] and uses[0][1]['op']=='clear',
                 'output bank unproduced and first future use discards old contents')
    return out,windows


def replay(word,selected,algebra):
    atom,add,operate=algebra.atom,algebra.add_rows,algebra.operate
    outputs={f'{side}{p}' for side in ('Z','W') for p in range(112)}
    rows={name:atom('dirt:'+name) for name in outputs}
    frames={name:'identity' for name in outputs}
    for p in selected:rows[f'X{p}'],frames[f'X{p}']=atom(f'E{p}'),'old'
    active=set();seen_outputs=set();boundary=False;checkpoints={};borrowed_peak=0
    for i,e in enumerate(word):
        op=e['op']
        if op=='history_boundary':
            need(not boundary and not active,'one B1 boundary')
            for p in selected:
                need(rows[f'Z{p}']==atom(f'E{p}') and frames[f'Z{p}']=='old','retained early value')
            for p in range(112):
                for side in ('X','Y'):
                    name=f'{side}{p}';rows[name]=atom(name)
                    frames[name]='current' if side=='X' else ('Y-minus',p)
            boundary=True
        elif op=='output_slices_begin':
            need(boundary and not active,'nonoverlapping output-slice windows')
            fields=e['fields'];aliases=e['aliases']
            need(len(fields)==len(set(fields))==len(aliases) and set(fields)==set(aliases.values()),'injective aliases')
            need(all(n in outputs and n.startswith('W') for n in fields),'only owned Y outputs')
            need(not set(fields)&seen_outputs,'unproduced output slices')
            active=set(fields);borrowed_peak=max(borrowed_peak,len(active))
            # No allocation, initialization, copy, or frame transition here.
        elif op=='output_slices_end':
            need(active==set(e['fields']),'matching borrow release')
            need(all(not rows[n] and frames[n]=='identity' for n in active),'zero identity release')
            active=set()
        elif op=='clear':
            name=e['field'];need(name in outputs,'clear owned output only')
            need(e['frame'] in ('old','current','identity'),'clear frame')
            if active:need(name in active or name.startswith('Z'),'scratch body cannot clear unrelated W output')
            else:seen_outputs.add(name)
            rows[name],frames[name]={},e['frame']
        elif op=='add':
            src,dst=e['src'],e['dst']
            need(src in rows and dst in outputs and src!=dst,'distinct live ADD fields')
            need(frames[src]==frames[dst],'matching ADD frames')
            if active:
                need((src in active or not src.startswith('W')) and
                     (dst in active or not dst.startswith('W')),'no unrelated W in owner-local body')
            else:seen_outputs.add(dst)
            rows[dst]=add(rows[dst],rows[src],Fraction(e['coefficient']))
        elif op=='stage':
            n=e['field'];need(boundary and not active and n in outputs,'stage outside borrow')
            need(e['rank']==8 and e['sign']==1 and frames[n]=='old','old-to-current stage')
            frames[n]='current';rows[n]=operate(rows[n],'stage8',1)
        elif op=='line':
            n,p,s=e['field'],e['port'],e['sign']
            need(boundary and not active and n==f'Y{p}' and s in (-1,1),'borrowed line outside borrow')
            before,after=(('Y-minus',p),'current') if s==1 else ('current',('Y-minus',p))
            need(frames[n]==before,'line frame');frames[n]=after
            rows[n]=operate(rows[n],f'line{p}',s)
        elif op=='current_map':
            n=e['field'];need(boundary and not active and n in outputs and frames[n]=='current','map outside borrow')
            need(type(e['inverse']) is bool,'map sign type')
            rows[n]=operate(rows[n],'map'+str(e['port']),-1 if e['inverse'] else 1)
        elif op=='checkpoint':
            need(not active and all(frames[f'Z{p}']=='current' for p in range(112)),'checkpoint frame')
            checkpoints[e['name']]=algebra.digest_rows({f'Z{p}':rows[f'Z{p}'] for p in range(112)})
        else:raise ValueError('unrecognized event '+op)
    need(boundary and not active,'completed word')
    need(all(frames[n]=='current' for n in outputs),'final output frame')
    need(all(not n.startswith('dirt:') for bank in outputs for n,_ in rows[bank]),'output dirt independent')
    for p in range(112):
        for side in ('X','Y'):
            n=f'{side}{p}'
            need(rows[n]==atom(n),'borrowed input restored')
            need(frames[n]==('current' if side=='X' else ('Y-minus',p)),'borrowed input frame')
    need(set(rows)==outputs|{f'{side}{p}'for side in ('X','Y')for p in range(112)},'no hidden private rows')
    return {n:rows[n] for n in outputs},checkpoints,borrowed_peak

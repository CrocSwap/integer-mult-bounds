"""Independent forward signed Laurent column audit for the two Type A roots."""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import runpy
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = 'ed090b57ed88f8859e5ff4643645099e6ba856ea'
CALLER_HEAD = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
PINS = {
    'CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'check_odd_caller_exact_grid.py': 'abd5a5fd011b71e5b382cbc058855594d4f2fe7b049f375506675c0303180f54',
    'forward_engine.py': '2dbf3dc231e4f1773513ef51e897888698555d1980511ae36a1d933f3760d78e',
}
ROOTS = (0,18)
N = 17
LIMIT = 9568


def decode(raw):
    def unique(pairs):
        result=dict(pairs)
        assert len(result)==len(pairs), 'duplicate JSON key'
        return result
    return json.loads(raw,object_pairs_hook=unique)


def save(out,value):
    tmp=out.with_suffix('.tmp')
    tmp.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    tmp.replace(out)


def classify(rows,root):
    occupied = []
    exponents, parities = set(), set()
    terms = 0
    for r,row in enumerate(rows):
        present = False
        for (source,q,exponent),value in row.items():
            if source==root:
                assert 0<=q<4 and exponent>=0 and any(value)
                present = True
                exponents.add(exponent)
                parities.add(q&1)
                terms+=1
        if present:
            occupied.append(r)
    assert terms
    result = {'column_rows':occupied,'terms':terms}
    if len(exponents)>1:
        return result | {'status':'mixed_body_exponents'}
    if len(parities)>1:
        return result | {'status':'mixed_central_parity'}
    exponent,=exponents
    central,=parities
    body = list(exponent.to_bytes(N,'little'))
    if any(v>1 for v in body):
        return result | {'status':'non_squarefree_body'}
    r=8*sum(body)+central
    assert 0<=r<=137
    return result | {'body':body,'central_parity':central,'ranks':[r,137-r],
                     'status':'positive_column_only' if 0<r<137 else 'zero_rank_side'}


def controls():
    exponents=sum(1<<(8*j) for j in range(8))
    positive=[{(0,1,exponents):(1,0),(0,3,exponents):(0,-2)},
              {(0,3,exponents):(2,3)}]
    a=classify(positive,0)
    assert a['status']=='positive_column_only' and a['ranks']==[65,72] and a['terms']==3
    assert a['column_rows']==[0,1]
    assert classify(positive+[{(0,2,exponents):(1,0)}],0)['status']=='mixed_central_parity'
    assert classify(positive+[{(0,3,0):(1,0)}],0)['status']=='mixed_body_exponents'
    assert classify([{(0,0,2):(1,0)}],0)['status']=='non_squarefree_body'
    assert classify([{(0,2,0):(1,0)}],0)['ranks']==[0,137]
    full=sum(1<<(8*j) for j in range(N))
    assert classify([{(0,3,full):(1,0)}],0)['ranks']==[137,0]
    return ['two_rows_and_even_residual_powers','mixed_parity_and_body_masks_rejected',
            'nonsquarefree_exponent_rejected','zero_rank_both_sides']


def run(root,out,deadline,seconds):
    files={}
    for name,digest in PINS.items():
        raw=(root/name).read_bytes()
        assert sha256(raw).hexdigest()==digest, ('changed input',name)
        files[name]=raw
    c=decode(files['CALLER.json'])
    model=runpy.run_path(str(root/'forward_engine.py'))
    assert model['HEAD']==HEAD and model['PINS'][model['CALLER']]==PINS['CALLER.json']
    events,grid,stage_counts=model['compile_events'](c)
    assert c['stages']==N and c['roles']==72 and len(events)+1==4784
    a=c['types']['A']
    assert a['roles']==36 and a['offset']==0
    assert all(a['diagonal'][r]==[-1,0]+[1]*N for r in ROOTS)
    rows=[{(i,0,0):(grid,0)} if i in ROOTS else {} for i in range(c['roles'])]
    records=[]
    endpoint_controls = {str(r): rows[r] == {(r,0,0):(grid,0)} for r in ROOTS}
    assert all(endpoint_controls.values())
    check = controls()
    for b in range(len(events)+1):
        if monotonic()>=deadline:
            break
        if b:
            model['apply'](rows,events[b-1])
        for r in ROOTS:
            records.append({'root':r,'boundary':b,**classify(rows,r)})
    complete = len(records)==LIMIT
    ending = []
    if complete:
        full=sum(1<<(8*j) for j in range(N))
        assert rows==[{(i,3,full):(grid,0)} if i in ROOTS else {} for i in range(c['roles'])]
        ending=list(ROOTS)
    counts=dict(Counter(row['status'] for row in records))
    unvisited=[[r,b] for b in range(len(records)//2,len(events)+1) for r in ROOTS]
    assert len(records)+len(unvisited)==LIMIT
    save(out,dict(head=HEAD,caller_head=CALLER_HEAD,pins=PINS,controls=check,seconds_cap=seconds,
                  cases_visited=len(records),counts=counts,unvisited=unvisited,
                  roots_starting_endpoints_checked=list(ROOTS),roots_final_endpoints_checked=ending,
                  max_stage_occurrences=max(stage_counts.values()),integer_grid_bits=grid.bit_length(),
                  survivors=[r for r in records if r['status']=='positive_column_only'],records=records))
    print(json.dumps({'counts':counts,'visited':len(records),'unvisited':len(unvisited),
                      'endpoints':ending},sort_keys=True))


def main():
    p=ArgumentParser()
    p.add_argument('dependencies',type=Path,nargs='?',default=Path(__file__).resolve().parent/'dependencies')
    p.add_argument('out',type=Path,nargs='?')
    p.add_argument('--seconds',type=int,default=45,choices=range(3,46),metavar='3..45')
    p.add_argument('--controls-only',action='store_true')
    a=p.parse_args()
    if a.controls_only:
        print(json.dumps(controls()))
        return
    if a.out is None or a.out.exists():
        p.error('a fresh output file is required')

    def timeout(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM,timeout)
    alarm(a.seconds)
    try:
        run(a.dependencies,a.out,monotonic()+min(42,a.seconds-1),a.seconds)
    except TimeoutError:
        save(a.out,dict(head=HEAD,status='hard_timeout',unverified=LIMIT,seconds_cap=a.seconds))
        raise SystemExit(2)
    finally:
        alarm(0)


if __name__=='__main__':
    assert __debug__
    main()

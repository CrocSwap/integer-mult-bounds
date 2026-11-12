"""Exact reverse Gaussian Laurent test of the two paid-fixed rank-17 split cuts."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal
from time import monotonic

ROOT=Path(__file__).resolve().parent
PINS={
 'inputs/CALLER.json':'255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
 'inputs/PRICE.json':'e076ac34017cc3c86c185a3f5982857dd70325012e196a2dcdd8d2d85a3957dc',
 'inputs/reverse.py':'d763b974585a439472bcaacf0913fc5c8469ea24212545287a3a359526ff51cd',
}
HEAD='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER='07a76c5e2738882c0cb322278e56f6cae3c9885d'
ROLE,CUTS,EVENTS,SECONDS=10,(1743,1744),4783,25
ZERO=(0,)*17
B9=tuple(int(j==9) for j in range(1,18))
B10=tuple(int(j==10) for j in range(1,18))
FINAL=tuple(a+b for a,b in zip(B9,B10,strict=True))


def unique(items):
    d=dict(items)
    if len(d)!=len(items):
        raise ValueError('duplicate input key')
    return d


def checked(root,p):
    raw=(root/p).read_bytes()
    if sha256(raw).hexdigest()!=PINS[p]:
        raise ValueError('changed dependency '+p)
    return raw


def inputs(root):
    raw={p:checked(root,p) for p in PINS}
    p,c=(loads(raw['inputs/'+s+'.json'],object_pairs_hook=unique) for s in ('PRICE','CALLER'))
    assert p['head']==HEAD and p['caller']==CALLER and p['chosen']==ROLE and p['cuts']==list(CUTS)
    assert p['delta']=={'8':96,'9':96,'17':-96}
    assert p['paid']==110519 and p['productive']==22557 and p['rank_surplus']==1424
    assert Q(p['quotes']['probe']['one_complete'][0])>0
    assert Q(p['quotes']['old_crossing_upper']['four_with_extra_rank1_per_port_upper'])<0
    a=c['types']['A']
    assert (len(c['events']),c['stages'],a['roles'],len(a['ports']))==(EVENTS,17,36,96)
    assert a['diagonal'][ROLE]==[-1,0,*FINAL]
    assert c['events'][1741:1744]==[['A','ADD',10,0,'2'],['A','IDLE_ONE',10,[9]],['A','ADD',10,0,'-2']]
    assert c['events'][3377][:3]==['J',10,[10,0,18,28]]
    return c,run_path(str(root/'inputs/reverse.py'))


def terms(rows):
    return [[r,q,list(body),str(a),str(b)] for r,row in enumerate(rows)
            for (q,body),(a,b) in sorted(row.items())]


def classify(rows):
    rows=terms(rows)
    assert rows
    wrong_body=next((t for t in rows if tuple(t[2])!=B9),None)
    odd_phase=next((t for t in rows if t[1]%2),None)
    return {'status':'foreign body' if wrong_body else 'odd central phase' if odd_phase else 'positive prefix only',
            'term_count':len(rows),'terms':rows,'first_foreign_body':wrong_body,'first_odd_phase':odd_phase}


def controls(engine):
    base={(0,B9):(Q(1),Q(0))}
    even={(2,B9):(Q(0),Q(-1))}
    odd={(3,B9):(Q(1),Q(0))}
    wrong={(0,B10):(Q(1),Q(0))}
    assert classify([base,even])['status']=='positive prefix only'
    assert classify([base,odd])['status']=='odd central phase'
    assert classify([base,wrong])['status']=='foreign body'
    row=[base.copy(),{}]
    engine['undo'](row,['A','QUERY',1,0,-1],Q(-1))
    assert row[1]=={(3,B9):(Q(-1),Q(0))}
    return [*engine['control'](),'noncoordinate even B9 passes','odd phase mutation rejects',
            'foreign body mutation rejects','negative query direction undo']


def verify(c,engine,deadline,visited):
    a=c['types']['A'];events=c['events']
    rows=[{} for _ in range(a['roles'])]
    rows[ROLE]={(3,FINAL):(Q(1),Q(0))}
    records=[]
    for boundary in range(len(events),-1,-1):
        visited['first_unvisited_boundary']=boundary
        if boundary%128==0 and monotonic()>=deadline:
            break
        if boundary in CUTS:
            records.append(dict(cut=boundary,**classify(rows)))
            visited['cuts_evaluated']+=1
        if boundary:
            engine['undo'](rows,events[boundary-1],Q(a['alpha2']))
            visited['events_undone']+=1
    complete=visited['events_undone']==EVENTS
    if complete:
        assert rows[ROLE]=={(0,ZERO):(Q(1),Q(0))} and all(not row for r,row in enumerate(rows) if r!=ROLE)
        # A global q phase commutes with every normalized event, so this
        # shifted initial root also checks the deliberately wrong endpoint.
        wrong=engine['mapped'](rows[ROLE],q=1)
        assert wrong=={(1,ZERO):(Q(1),Q(0))} and wrong!=rows[ROLE]
        visited['first_unvisited_boundary']=None
    return sorted(records,key=lambda r:r['cut']),complete


def main():
    assert __debug__
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('--root',type=Path,default=ROOT)
    cli.add_argument('--controls-only',action='store_true')
    args=cli.parse_args()
    c,engine=inputs(args.root)
    tests=controls(engine)
    if args.controls_only:
        print(dumps(tests));return
    def stop(*_):
        raise TimeoutError('hard 25-second prefix cap')
    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline=monotonic()+SECONDS-1
    progress={'events_undone':0,'cuts_evaluated':0}
    rows=[]
    complete=False
    error=None
    try:
        rows,complete=verify(c,engine,deadline,progress)
    except TimeoutError as e:
        error=str(e)
    finally:
        alarm(0)
    result={'head':HEAD,'caller':CALLER,'pins':PINS,'role':ROLE,'cuts':CUTS,
            'caps':{'cases':2,'events':EVENTS,'seconds':SECONDS},'controls':tests,'rows':rows,
            'counts':Counter(r['status'] for r in rows),'endpoint_recovered':complete,'progress':progress,
            'unvisited':sorted(set(CUTS)-{r['cut'] for r in rows}),'timeout':error}
    if not complete:
        result['unresolved']='full original endpoint replay incomplete'
    print(dumps(result,indent=2,sort_keys=True))
    if not complete:
        raise SystemExit(2)


if __name__=='__main__':
    main()

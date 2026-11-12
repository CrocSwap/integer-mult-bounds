"""Necessary support of one rank-one leg in each fixed old signed host."""
from fractions import Fraction as F
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import alarm

R=Path(__file__).resolve().parent/'inputs'
PINS={
 'CALLER.json':'255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
 'forward.py':'75d94780f9db49a4b08bb0e7fb4bd7fc04adb8cabbf73d83a809179c04c3d439',
 'dependency.py':'82959a8be9c332698e402fc963e0c3af8dfac6522128100851dd96c767e162d5',
 'TARGET.json':'7f72ff06f411cf86ebed076ed004660e7ffb04fc9ef317efb1f4a2a5525e1884',
}


def main():
    assert __debug__
    alarm(30)
    for n,h in PINS.items():
        assert sha256((R/n).read_bytes()).hexdigest()==h
    m=run_path(str(R/'dependency.py'))
    f=run_path(str(R/'forward.py'))
    add,dot,product=m['add'],m['dot'],m['product']
    rank=lambda rows:len(m['rref'](rows)[1])
    unit,apply=f['unit'],f['apply']
    tape=loads((R/'CALLER.json').read_bytes())['events']
    rec=loads((R/'TARGET.json').read_bytes())
    selected=set(rec['chosen'])
    factors,keys=m['source_factors'](unit,apply,tape)
    units=[unit(i) for i in range(36)]
    remainder=[f for i,f in enumerate(factors) if i not in selected]
    target=[[F(a) for a in col] for col in rec['target_columns']]
    assert target==[[-x for x in product(remainder,e,inverse=True)] for e in units]
    delta=[add(t,e,-1) for t,e in zip(target,units,strict=True)]
    dual=list(map(list,zip(*delta,strict=True)))
    assert rank(delta)==rank(dual)==19
    rows=[]
    for i in sorted(selected):
        clock,dest,source=keys[i]
        event=tape[clock]
        if event[0]!='J' or event[1]==1:
            continue
        stage,roles=event[1:3]
        assert len(set(roles))==4 and i+1 not in selected and keys[i+1][0]==clock
        after=[f for j,f in enumerate(factors) if j>i and j not in selected]
        minus=[apply(tape[:clock],e,-1) for e in units]
        columns=[product(after,apply(tape[:clock],units[j],-1,inverse=True)) for j in roles]
        covectors=[]
        for j in roles:
            v=[col[j] for col in minus]
            for u,c in after:
                v=add(v,c,-dot(v,u))
            covectors.append(v)
        assert [[dot(v,u) for u in columns] for v in covectors]==[[int(i==j) for j in range(4)] for i in range(4)]
        assert rank(columns)==rank(covectors)==4
        a,b=23-rank(delta+columns),23-rank(dual+covectors)
        rows.append({'stage':stage,'clock':clock,'physical_roles':roles,'selected_factor':i,
                     'image_intersection_dim':a,'covector_intersection_dim':b,'excluded':min(a,b)==0})
    assert [r['stage'] for r in rows]==list(range(2,18))
    blocked=sum(r['excluded'] for r in rows)
    p=F('125835302963450101082086151823291979224042333232591/2500000000000000000000000000000000000000000000000')
    upper=p-blocked*(96-p)
    alarm(0)
    print(dumps({'pins':PINS,'target_rank':19,'hosts':rows,'blocked':blocked,'best_gross_upper':str(upper),
                 'host_cap':16,'runner_cap_seconds':30,'scope':'fixed old negative-sign frames and unit bodies'},sort_keys=True,indent=2))


if __name__=='__main__':
    main()

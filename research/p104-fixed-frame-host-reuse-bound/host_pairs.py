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

    def kernel(equations,width):
        if not equations:
            return [[F(i==j) for i in range(width)] for j in range(width)]
        reduced,piv=m['rref'](equations)
        out=[]
        for j in sorted(set(range(width))-set(piv)):
            u=[F(i==j) for i in range(width)]
            for rr,k in zip(reduced[:len(piv)],piv,strict=True):
                u[k]=-rr[j]
            assert all(not dot(u,eq) for eq in equations)
            out.append(u)
        return out

    def allowed(global_rows,local_basis):
        equations=[[dot(z,v) for v in local_basis] for z in kernel(global_rows,36)]
        return kernel(equations,4)

    rows=[]
    proposed_images=[]
    proposed_rows=[]
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
        img=allowed(delta,columns)
        cov=allowed(dual,covectors)
        assert len(img)==1 and len(cov)==2
        _,mate_dest,mate_src=keys[i+1]
        a,b=roles.index(mate_dest),roles.index(mate_src)
        u,=img
        eq=[[v[a] for v in cov],[dot(v,u) for v in cov]]
        solutions=[]
        for w in kernel(eq,len(cov)):
            v=[sum(c*x for c,x in zip(w,col,strict=True)) for col in zip(*cov,strict=True)]
            assert not v[a] and not dot(v,u)
            if any(z for j,z in enumerate(v) if j!=b):
                solutions.append(v)
        good=not u[b] and any(z for j,z in enumerate(u) if j!=a) and bool(solutions)
        if good:
            proposed_images.append([sum(c*x for c,x in zip(u,col,strict=True)) for col in zip(*columns,strict=True)])
            v=solutions[0]
            proposed_rows.append([sum(c*x for c,x in zip(v,col,strict=True)) for col in zip(*covectors,strict=True)])
        rows.append({'stage':stage,'clock':clock,'physical_roles':roles,'selected_factor':i,
                     'old_mate':[mate_dest,mate_src],'local_image':u,'allowed_local_covectors':solutions,
                     'excluded':not good})
    assert [r['stage'] for r in rows]==list(range(2,18))
    blocked=sum(r['excluded'] for r in rows)
    p=F('125835302963450101082086151823291979224042333232591/2500000000000000000000000000000000000000000000000')
    upper=p-blocked*(96-p)
    alarm(0)
    print(dumps({'pins':PINS,'target_rank':19,'hosts':rows,'blocked':blocked,'best_gross_upper':str(upper),
                 'host_cap':16,'proposed_image_rank':rank(proposed_images) if proposed_images else 0,
                 'proposed_covector_rank':rank(proposed_rows) if proposed_rows else 0,
                 'gathered_image_lines':proposed_images,'gathered_covector_choices':proposed_rows,'runner_cap_seconds':30,'scope':'fixed old negative-sign frames and unit bodies'},sort_keys=True,indent=2,default=str))


if __name__=='__main__':
    main()

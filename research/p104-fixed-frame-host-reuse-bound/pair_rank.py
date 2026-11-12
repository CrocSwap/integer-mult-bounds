"""Exact fixed-frame host-mate nullspaces and simultaneous image rank."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import alarm

ROOT = Path(__file__).resolve().parent
BASE_SHA = 'a733b4742670f5b48a48f0ceba20c0a2e4073552653c95a7533be86d4e87dee3'


def kernel(equations, width, basis, dot):
    echelon = basis(equations)
    for j in sorted(set(range(width)) - echelon.keys()):
        vector = [Q(i == j) for i in range(width)]
        for pivot, row in sorted(echelon.items(), reverse=True):
            vector[pivot] = -Q(dot(vector,row),row[pivot])
        assert all(not dot(vector, row) for row in equations)
        yield vector


def mix(weights, vectors):
    return [sum(a*b for a,b in zip(weights, column, strict=True)) for column in zip(*vectors,strict=True)]


def main():
    assert __debug__
    alarm(30)
    assert sha256((ROOT/'reverse_host.py').read_bytes()).hexdigest() == BASE_SHA
    m = run_path(str(ROOT/'reverse_host.py'))
    src = {}
    for name,digest in m['PINS'].items():
        raw = (ROOT/name).read_bytes()
        assert sha256(raw).hexdigest() == digest
        src[name] = loads(raw)
    unit,plus,dot,apply,carry_row,basis = [m[x] for x in ('unit','plus','dot','apply','carry_row','basis')]
    tape = src['inputs/CALLER.json']['events']
    frozen = src['inputs/R209-REVERSE.json']
    selected = m['SELECTED']
    assert len(tape) == 4783 and tuple(frozen['chosen']) == selected
    factors, hosts = m['prefix'](tape)
    kept = [(j,v) for j,v in enumerate(factors) if j not in selected]
    target = [apply(factors, apply([v for _,v in kept], unit(i), inverse=True)) for i in range(36)]
    assert target == [[Q(x) for x in c] for c in frozen['target_columns']]
    d = [plus(col,unit(i),-1) for i,col in enumerate(target)]
    spaces = (d, list(zip(*d,strict=True)))
    assert all(len(basis(s)) == 19 for s in spaces)
    annihilators = [list(m['annihilator'](s)) for s in spaces]
    all_images, all_rows, records = [],[],[]
    for host,clock,i,axes,images,covectors in hosts[1:]:
        assert i in selected and i+1 not in selected
        suffix = [v for j,v in kept if j>i]
        cols = [apply(suffix,x) for x in images]
        rows = [carry_row(suffix,x) for x in covectors]
        assert [[dot(r,c) for c in cols] for r in rows] == [[int(a==b) for b in range(4)] for a in range(4)]
        eq_u = [[Q(dot(p,x)) for x in cols] for p in annihilators[0]]
        eq_v = [[Q(dot(p,x)) for x in rows] for p in annihilators[1]]
        u, = kernel(eq_u,4,basis,dot)
        assert len(list(kernel(eq_v,4,basis,dot))) == 2
        mate_image, mate_row = factors[i+1]
        mate_image = apply(suffix,mate_image)
        mate_row = carry_row(suffix,mate_row)
        assert mate_image == [-2*x for x in cols[2]] and mate_row == rows[3]
        gu = mix(u,cols)
        assert not dot(mate_row,gu)
        eq_v.append([Q(dot(r,mate_image)) for r in rows])
        eq_v.append([Q(dot(r,gu)) for r in rows])
        v, = kernel(eq_v,4,basis,dot)
        gv = mix(v,rows)
        assert not dot(gv,mate_image) and not dot(gv,gu)
        assert u == [1,1,0,0] and v == [-1,1,0,0]
        assert gu in [unit(0),[-x for x in unit(0)]]
        assert len(basis([*spaces[0], gu])) == len(basis([*spaces[1],gv])) == 19
        bad = gv.copy()
        bad = plus(bad,rows[2],1)
        assert dot(bad,mate_image) == -2
        all_images.append(gu)
        all_rows.append(gv)
        records.append(dict(host=host,clock=clock,axes=axes,selected_index=i,
                            local_image=list(map(str,u)),local_covector=list(map(str,v)),
                            gathered_image=list(map(str,gu)),gathered_covector=list(map(str,gv))))
    assert len(records) == 16
    im_rank, cov_rank = [len(basis(x)) for x in (all_images,all_rows)]
    assert im_rank == 1 and cov_rank == 16
    p = Q('125835302963450101082086151823291979224042333232591/2500000000000000000000000000000000000000000000000')
    missing = 16-im_rank
    upper = p-missing*(96-p)
    assert missing == 15 and upper < Q('-634.654061')
    alarm(0)
    print(dumps(dict(pins=m['PINS'],base_sha256=BASE_SHA,unit_bodies=True,sectors=[-1,1],
                     host_cap=16,runner_cap_seconds=30,selected=selected,target_rank=19,
                     records=records,gathered_image_rank=im_rank,gathered_covector_rank=cov_rank,
                     blocked_local=0,max_reused_hosts=im_rank,min_missing_hosts=missing,
                     raw_upper=str(upper),single_host_credit_upper=str(p),mate_mutation_rejected=True),
                sort_keys=True,indent=2))


if __name__ == '__main__':
    main()

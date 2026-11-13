"""Test the existing role-992 route for the exact chart-529 repair."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent


def timeout(_signal, _frame):
    raise SystemExit(124)


def dot(row, probe):
    return sum(value * probe.get(index, 0) for index, value in row.items())


def dual(pivots, reduced):
    free = min(reduced)
    assert free not in pivots
    probe = {free: Q(1) / reduced[free]}
    for key, (row, _) in sorted(pivots.items(), reverse=True):
        value = -dot(row, probe)
        if value:
            probe[key] = value
    return probe


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(30)
    source = ROOT / 'gate.py'
    assert sha256(source.read_bytes()).hexdigest() == 'aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9'
    mod = run_path(str(source))
    raw = (ROOT / '7481-WORD.json.gz').read_bytes()
    assert sha256(raw).hexdigest() == mod['PINS']['7481-WORD.json.gz']
    word = loads(decompress(raw))
    tape, public = word['program'], word['public']
    assert tape[39818] == ['MOVE', 992, 520, 529, False]
    assert tape[39876] == ['ADD', 1532, 497, '4', 520]
    assert tape[39877] == ['MOVE', 1451, 737, 529, False]
    assert tape[39884:39888] == [['MOVE',1532,520,529,True], ['SCALE',1532,'-1/2',529],
                                  ['ADD',913,1532,'1',529], ['CLEAR',1532,529]]
    touches = [i for i in range(39819,39884) if tape[i][1]==992 or
               (tape[i][0] in ('ADD','COPY') and tape[i][2]==992)]
    assert touches == [39819,39878,39883]
    rows, basis, representation, census, add = (mod[name] for name in
                                              ('exact_cut_rows','basis','representation','census','add'))
    _,active,_ = census(word,39884)
    bank = [r for r,c in active.items() if c==529 and r!=992]
    values = dict(zip(bank+[992,1532],rows(tape[:39884],bank+[992,1532],public)))
    form = {146:Q(4)}
    for role, factor in ((146,8),(992,-4),(913,2),(1444,-4),(228,-4)):
        for j, coefficient in values[role].items():
            add(form,j,factor*coefficient)
    assert form == values[1532]
    required913 = values[913].copy()
    for index, coefficient in values[1532].items():
        add(required913,index,-coefficient/2)
    fixed = [values[r] for r in bank]
    targets = [values[992],required913]
    base = basis(fixed)
    with_first = basis(fixed+[targets[0]])
    union = basis(fixed+targets)
    certificate = []
    if len(union)-len(base)==2:
        for pivots, target in ((base,targets[0]),(with_first,targets[1])):
            residual,_ = representation(pivots,target)
            probe = dual(pivots,residual)
            assert all(not dot(row,probe) for row in fixed)
            certificate.append({'probe':probe,'required_values':[dot(row,probe) for row in targets]})
        assert certificate[0]['required_values'][0] == 1 and certificate[1]['required_values'] == [0,1]
    assert not [i for i in range(39894,len(tape)) if tape[i][0]=='MOVE' and tape[i][3]==529]
    print(dumps({'status':'SINGLE_RETIMED_PRODUCER_EXCLUDED' if certificate else 'SPAN_GATE_SURVIVES',
                 'case_cap':1,'runner_cap_seconds':30,'bank':bank,'rank':len(base),
                 'with_old992':len(with_first),'union':len(union),'certificate':certificate,
                 'removed_native_paid_rank':1,'signed_gross_raw':17,'new_rank1_charge_raw':17},
                sort_keys=True,indent=2,default=str))
    alarm(0)


if __name__ == '__main__':
    main()

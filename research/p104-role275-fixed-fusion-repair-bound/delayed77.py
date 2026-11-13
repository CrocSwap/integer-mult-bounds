"""Exact two-probe gate for one already-paid chart-312 arrival on #7481."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import exit

ROOT = Path(__file__).resolve().parent
PINS = {
    '7481-WORD.json.gz': 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9',
    'gate.py': 'aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9',
    '7481-APPLICATION.json': '1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799',
    'pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
}
READ, AFTER, CHART = 31452, 31459, 312
ROLES = (275, 77)


def timeout(signum, frame):
    print(dumps({'status':'unresolved_timeout','cases_completed':0,'runner_cap_seconds':30}))
    exit(124)


def dot(row, probe):
    return sum((weight * probe.get(j, Q(0)) for j, weight in row.items()), Q(0))


def forward(word, probe):
    public = word['public']
    values = [probe.get(i, Q(0)) for i in range(public)] + [None] * word['owned_fields']
    charts = word['initial'] + [None] * word['owned_fields']
    old = None
    for clock, (op, dst, *args) in enumerate(word['program'][:AFTER]):
        if clock == READ:
            assert set(j for j,c in enumerate(charts) if c == CHART) == set(ROLES)
            old = [values[j] for j in ROLES]
        if op == 'INIT':
            assert charts[dst] is None and values[dst] is None
            charts[dst], values[dst] = args[0], Q(0)
        elif op == 'CLEAR':
            assert charts[dst] == args[0]
            charts[dst], values[dst] = None, None
        elif op == 'MOVE':
            assert charts[dst] == args[0] and args[2] == (dst >= public)
            charts[dst] = args[1]
        elif op == 'SCALE':
            assert charts[dst] == args[1]
            values[dst] *= Q(args[0])
        else:
            src, coefficient, chart = args
            assert op in ('ADD','COPY') and charts[dst] == charts[src] == chart
            if op == 'COPY':
                assert values[dst] == 0
            values[dst] += Q(coefficient) * values[src]
    assert old is not None
    return old, [values[j] for j in ROLES]


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(30)
    data = {name:(ROOT/name).read_bytes() for name in PINS}
    assert {name:sha256(raw).hexdigest() for name, raw in data.items()} == PINS
    native = decompress(data['7481-WORD.json.gz'])
    assert sha256(native).hexdigest() == '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
    word = loads(native)
    tape, public = word['program'], word['public']
    assert tape[31439] == ['ADD', 274, 100, '1', 93]
    assert tape[31442] == ['ADD', 275, 274, '1', 93]
    assert tape[31450:31453] == [['MOVE',275,93,312,False],['MOVE',77,71,312,False],['ADD',275,77,'1',312]]
    assert tape[31458] == ['ADD',77,275,'-1/2',312]
    assert tape[31460:31462] == [['MOVE',275,312,321,False],['ADD',278,275,'1',321]]
    assert not [t for t,e in enumerate(tape[31452:31849],31452) if e[0]=='MOVE' and e[3]==CHART]
    lo, hi = map(Q, loads(data['7481-APPLICATION.json'])['directed_crossing_bracket'])
    power = run_path(str(ROOT/'pricing.py'))['power_bounds']
    gross = [17*(2-power(2,lo)[1]),17*(2-power(2,hi)[0])]
    assert 0 < gross[0] <= gross[1] < 17
    engine = run_path(str(ROOT/'gate.py'))
    rows, basis, representation, add = (engine[k] for k in ('exact_cut_rows','basis','representation','add'))
    a, b = rows(tape[:READ], ROLES, public)
    assert rows(tape[:31439], [100], public) == [{100:Q(1)}]
    direct = a.copy()
    add(direct, 100, Q(-1))
    outputs = rows(tape[:AFTER], ROLES, public)
    fixed = basis([direct])
    rank = len(basis([direct]+outputs)) - len(fixed)
    probe1 = {100:Q(1)}
    assert not dot(direct,probe1)
    remainder,_ = representation(fixed,b)
    assert remainder
    free = min(remainder)
    probe2 = {free:1/remainder[free]}
    for j,(row,_) in sorted(fixed.items(),reverse=True):
        value = -dot(row,probe2)
        if value:
            probe2[j] = value
    witnesses = []
    for probe in (probe1,probe2):
        before,after = forward(word,probe)
        assert not dot(direct,probe) and before == [dot(a,probe),dot(b,probe)]
        assert after == [dot(row,probe) for row in outputs]
        witnesses.append({'probe':probe,'old_inputs':before,'old_outputs':after})
    x,y = (w['old_outputs'] for w in witnesses)
    determinant = x[0]*y[1]-x[1]*y[0]
    assert rank==2 and determinant
    alarm(0)
    print(dumps({'status':'EXACT_ROLE77_ONE_ARRIVAL_EXCLUDED','cases_completed':1,'case_cap':1,
                 'runner_cap_seconds':30,'chart':CHART,'read':READ,'after':AFTER,
                 'roles':ROLES,'direct_arrival':'old275_before_ADD31452_minus_x100',
                 'fixed_rank':len(fixed),'quotient_rank':rank,'target_determinant':determinant,
                 'witnesses':witnesses,'signed_paid_delta':{1:-34,2:17},
                 'signed_productive_delta':{},'directed_gross':gross,'source_sha256':PINS['7481-WORD.json.gz']},
                indent=2,sort_keys=True,default=str))


if __name__=='__main__':
    main()

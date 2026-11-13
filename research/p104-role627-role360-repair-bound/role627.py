"""Exact fixed-bank quotient for the proposed role-360 repair at ADD43805."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent


def expire(_signum, _frame):
    raise SystemExit(124)


def evaluate(row, probe):
    return sum(value * probe.get(index, 0) for index, value in row.items())


def separator(pivots, remainder):
    free = min(remainder)
    assert free not in pivots
    probe = {free: 1 / remainder[free]}
    for index, (row, _) in sorted(pivots.items(), reverse=True):
        coefficient = -evaluate(row, probe)
        if coefficient:
            probe[index] = coefficient
    return probe


def main():
    assert __debug__
    signal(SIGALRM, expire)
    alarm(30)
    helper = ROOT / 'gate.py'
    assert sha256(helper.read_bytes()).hexdigest() == 'aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9'
    functions = run_path(str(helper))
    names = ('7481-WORD.json.gz', '7481-APPLICATION.json', 'pricing.py')
    inputs = {name:(ROOT/name).read_bytes() for name in names}
    assert all(sha256(raw).hexdigest() == functions['PINS'][name] for name,raw in inputs.items())
    payload = decompress(inputs[names[0]])
    assert sha256(payload).hexdigest() == '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
    word = loads(payload)
    tape = word['program']
    public = word['public']
    assert tape[32947] == ['MOVE',627,3,117,False]
    assert tape[32949] == ['MOVE',732,3,117,False]
    assert tape[42212] == ['MOVE',360,417,836,False]
    assert tape[43804:43806] == [['MOVE',627,117,836,False],['ADD',627,360,'1',836]]
    assert tape[44298] == ['MOVE',732,117,222,False]
    rows, basis, represent, census = (functions[name] for name in
                                       ('exact_cut_rows', 'basis', 'representation', 'census'))
    _, active, _ = census(word,43805)
    assert active[732] == 117
    fixed_roles = sorted(role for role,chart in active.items() if chart==836 and role not in (627,360))
    direct, = rows(tape[:32947],[627],public)
    fixed = rows(tape[:43805],fixed_roles,public) + [direct]
    targets = rows(tape[:43805],[627,360],public)
    base = basis(fixed)
    union = basis(fixed+targets)
    certificate = []
    if len(union)-len(base)==2:
        for known,target in ((base,targets[0]),(basis(fixed+targets[:1]),targets[1])):
            remainder,_ = represent(known,target)
            probe = separator(known,remainder)
            assert not any(evaluate(row,probe) for row in fixed)
            certificate.append({'input':probe,'old_targets':[evaluate(row,probe) for row in targets]})
        assert certificate[0]['old_targets'][0] == 1 and certificate[1]['old_targets'] == [0,1]
    lo, hi = map(Q,loads(inputs[names[1]])['directed_crossing_bracket'])
    power = run_path(str(ROOT/names[2]))['power_bounds']
    old,new = [5,1,5,3],[6,5,1,2]
    gross = [17*(sum(power(r,hi)[0] for r in old)-sum(power(r,lo)[1] for r in new)),
             17*(sum(power(r,lo)[1] for r in old)-sum(power(r,hi)[0] for r in new))]
    assert Q('.0488')<gross[0]<=gross[1]<Q('.0489')
    print(dumps({'status':'FIXED_ROLE360_REPAIR_EXCLUDED' if certificate else 'RECEIVER_GATE_SURVIVES',
                 'cut':43805,'fixed_roles':fixed_roles,'direct_source':[627,32947],
                 'rank':len(base),'union':len(union),'certificate':certificate,'case_cap':1,
                 'runner_cap_seconds':30,'old_paid_ranks':old,'new_paid_ranks':new,
                 'gross_signed_before_repairs':gross},default=str,sort_keys=True,indent=2))
    alarm(0)


if __name__=='__main__':
    main()

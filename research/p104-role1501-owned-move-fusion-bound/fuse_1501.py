"""Exact support check for one owned monotone route fusion."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import alarm

ROOT = Path(__file__).resolve().parent


def dot(row, probe):
    return sum(coefficient * probe.get(key, 0) for key, coefficient in row.items())


def span(vectors):
    result = {0}
    for vector in vectors:
        result |= {value ^ vector for value in result}
    return result


def main():
    assert __debug__
    alarm(30)
    helper = ROOT / 'gate.py'
    assert sha256(helper.read_bytes()).hexdigest() == 'aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9'
    model = run_path(str(helper))
    names = ['7481-WORD.json.gz', '7481-APPLICATION.json', 'pricing.py']
    data = {name: (ROOT / name).read_bytes() for name in names}
    assert all(sha256(raw).hexdigest() == model['PINS'][name] for name, raw in data.items())
    payload = decompress(data[names[0]])
    assert sha256(payload).hexdigest() == '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
    word = loads(payload)
    tape = word['program']
    assert tape[40563:40569] == [
        ['MOVE',1501,549,115,True], ['ADD',1501,1525,'1/4',115], ['CLEAR',1525,115],
        ['MOVE',174,3,593,False], ['MOVE',1501,115,593,True], ['ADD',174,1501,'-2',593],
    ]
    frames = [word['frames'][chart] for chart in (549,115,593)]
    assert list(map(len,frames)) == [7,5,1] and span(frames[2]) < span(frames[1]) < span(frames[0])
    rows, basis, represent, census = (model[name] for name in
                                       ('exact_cut_rows', 'basis', 'representation', 'census'))
    points = [(40563,549),(40567,593)]
    banks = []
    fixed = []
    for cut,chart in points:
        _, live, _ = census(word,cut)
        bank = sorted(role for role,frame in live.items() if frame == chart)
        banks.append(bank)
        fixed.extend(rows(tape[:cut],bank,word['public']))
    target, = rows(tape[:40564],[1525],word['public'])
    assert target == {607:Q(-1),770:Q(1)}
    pivots = basis(fixed)
    residual,_ = represent(pivots,target)
    probe = None
    if residual:
        free = min(residual)
        assert free not in pivots
        probe = {free: 1 / residual[free]}
        for column,(row,_) in sorted(pivots.items(),reverse=True):
            value = -dot(row,probe)
            if value:
                probe[column] = value
        assert not any(dot(row,probe) for row in fixed) and dot(target,probe) == 1
    lo,hi = map(Q,loads(data[names[1]])['directed_crossing_bracket'])
    price = run_path(str(ROOT / names[2]))['power_bounds']
    gross = [17*(price(2,hi)[0]+price(4,hi)[0]-price(6,lo)[1]),
             17*(price(2,lo)[1]+price(4,lo)[1]-price(6,hi)[0])]
    assert Q('.2355') < gross[0] <= gross[1] < Q('.2356')
    print(dumps({'status':'LOCAL_FUSION_EXCLUDED' if probe else 'SUPPORT_GATE_SURVIVES',
                 'case_cap':1,'runner_cap_seconds':30,'banks':banks,'points':points,
                 'target':target,'probe':probe,'bank_rank':len(pivots),
                 'union_rank':len(basis(fixed+[target])), 'whole_signed_gross':gross},
                sort_keys=True,indent=2,default=str))
    alarm(0)


if __name__ == '__main__':
    main()

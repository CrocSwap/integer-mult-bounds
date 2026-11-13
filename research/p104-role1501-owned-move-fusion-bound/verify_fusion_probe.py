"""Literal forward check of one normalized input separating the owned route fusion."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import alarm

SOURCE = Path(__file__).with_name('7481-WORD.json.gz')


def replay(word, probe):
    values = [probe.get(role, Fraction()) for role in range(word['public'])] + [None]*word['owned_fields']
    frames = word['initial'] + [None]*word['owned_fields']
    observations = {}
    for clock, (op, dst, *args) in enumerate(word['program'][:40569]):
        if clock in (40563,40567):
            chart = 549 if clock == 40563 else 593
            observations[clock] = {role: values[role] for role,frame in enumerate(frames) if frame==chart}
        if clock == 40564:
            observations['owned_donor'] = values[1525]
        if clock == 40568:
            observations['old_outward_increment'] = -2*values[1501]
        if op == 'INIT':
            assert values[dst] is None and frames[dst] is None
            values[dst],frames[dst] = Fraction(),args[0]
        elif op == 'CLEAR':
            assert frames[dst] == args[0]
            values[dst],frames[dst] = None,None
        elif op == 'MOVE':
            assert frames[dst] == args[0] and (dst >= word['public']) == args[2]
            frames[dst] = args[1]
        elif op == 'SCALE':
            assert frames[dst] == args[1]
            values[dst] *= Fraction(args[0])
        else:
            src,coefficient,chart = args
            assert op in ('ADD','COPY') and frames[dst] == frames[src] == chart
            if op == 'COPY':
                assert not values[dst]
            values[dst] += Fraction(coefficient)*values[src]
    return observations


def main():
    assert __debug__
    alarm(30)
    blob = SOURCE.read_bytes()
    assert sha256(blob).hexdigest() == 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
    raw = decompress(blob)
    assert sha256(raw).hexdigest() == '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
    word = loads(raw)
    probe = {10:Fraction(-1),173:Fraction(-1,2),607:Fraction(-1)}
    result = replay(word,probe)
    zero = replay(word,{})
    assert all(result[clock]==zero[clock] and not any(result[clock].values()) for clock in (40563,40567))
    assert result['owned_donor'] == 1 and result['old_outward_increment'] == Fraction(-1,2)
    assert zero['owned_donor'] == zero['old_outward_increment'] == 0
    print(dumps({'status':'PASS_LITERAL_FORWARD_SEPARATOR','inputs':probe,
                 'bank_roles':[sorted(result[clock]) for clock in (40563,40567)],
                 'owned_donor':result['owned_donor'],'old_outward_increment':result['old_outward_increment'],
                 'zero_control':True},default=str,sort_keys=True,indent=2))
    alarm(0)


if __name__ == '__main__':
    main()

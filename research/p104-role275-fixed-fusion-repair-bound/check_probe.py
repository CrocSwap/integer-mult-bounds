"""One exact source-side probe for the role-275 producer fusion."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

SOURCE = Path(__file__).with_name('7481-WORD.json.gz')


def stop(_signal, _frame):
    print('{"status":"UNRESOLVED_TIMEOUT"}')
    raise SystemExit(124)


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(30)
    blob = SOURCE.read_bytes()
    assert sha256(blob).hexdigest() == 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
    word = loads(decompress(blob))
    tape = word['program']
    assert tape[31438:31443] == [['MOVE',274,3,93,False],['ADD',274,100,'1',93],
                                ['ADD',178,1275,'1/2',3],['MOVE',275,3,93,False],
                                ['ADD',275,274,'1',93]]
    assert tape[31450] == ['MOVE',275,93,312,False]
    values = [Fraction(r == 100) for r in range(word['public'])] + [None]*word['owned_fields']
    charts = word['initial'] + [None]*word['owned_fields']
    bank = None
    old_target = None
    for clock, (op, role, *args) in enumerate(tape[:31443]):
        if clock == 31438:
            bank = [(r,value) for r,value in enumerate(values) if charts[r] == 3]
        if clock == 31442:
            old_target = values[274]
            assert values[100] == 1
        if op == 'INIT':
            assert values[role] is None
            values[role],charts[role] = Fraction(),args[0]
        elif op == 'CLEAR':
            assert charts[role] == args[0]
            values[role],charts[role] = None,None
        elif op == 'MOVE':
            assert charts[role] == args[0]
            charts[role] = args[1]
        elif op == 'SCALE':
            assert charts[role] == args[1]
            values[role] *= Fraction(args[0])
        else:
            donor,coefficient,chart = args
            assert charts[role] == charts[donor] == chart and op in ('ADD','COPY')
            if op == 'COPY':
                assert not values[role]
            values[role] += Fraction(coefficient)*values[donor]
    assert bank is not None and old_target is not None
    support = {role:value for role,value in bank if value}
    status = 'UNIT_PROBE_EXCLUDES_SOURCE_BANK' if not support and old_target else 'UNIT_PROBE_INCONCLUSIVE'
    print(dumps({'status':status,'probe':{100:1},'bank_size':len(bank),'nonzero_available':support,
                 'old_target_value':old_target,'cut':31438},default=str,sort_keys=True,indent=2))
    alarm(0)


if __name__ == '__main__':
    main()

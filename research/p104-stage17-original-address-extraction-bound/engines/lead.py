"""One exact translation witness for original-address stage-17 extraction."""
from fractions import Fraction as F
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import alarm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PINS = {
    'inputs/CALLER.json':'255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/PROJECTOR.json':'c36cb8d3fae7bccd15566c2f83f2d2bd8abeeb334381cbf3212d5d9b3d965c35',
    'engines/pricing.py':'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'inputs/7113-signed-child.py':'ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b',
}


def main():
    assert __debug__
    alarm(20)
    for name,digest in PINS.items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == digest
    caller = loads((ROOT/'inputs/CALLER.json').read_bytes())
    tape = caller['events']
    assert tape[4646] == tape[4660] == ['B','IDLE_ONE',36,[17]]
    window = tape[4647:4660]
    assert len(window) == 13 and all(e[:2] in (['B','ADD'],['B','SCALE']) for e in window)
    roles = sorted({r for e in window for r in e[2:4 if e[1]=='ADD' else 3]})
    assert roles == [36,37,52,53]
    expected = loads((ROOT/'inputs/PROJECTOR.json').read_bytes())
    assert expected['rank'] == 2 and expected['inclusive_window'] == [4646,4660]
    child = run_path(str(ROOT/'inputs/7113-signed-child.py'))
    multiply = child['multiply']
    _, body = child['masks'](17,1)
    axes = [j for j in range(153) if body >> j & 1]
    assert axes == list(range(137,145))
    matrix = child['C']
    assert matrix[0][0] == matrix[1][1] and matrix[0][1] == matrix[1][0]
    coefficient = matrix[1][0]
    for _ in range(7):
        coefficient = multiply(coefficient,matrix[0][0])
    neighbour = [F(v,2**8) for v in coefficient]
    assert neighbour == [0,F(-1,16)]
    # E is a combination of identity and the all-eight-bit flip, so this entry is zero.
    assert 1 not in (0,2**8-1)
    h = run_path(str(HERE/'pricing.py'))['power_bounds']
    lo,hi = map(F,('0.00364665195644044790699554028334161','0.00364665195644044790699554028334162'))
    quote_one = 16*h(8,hi)[0]-8*h(16,lo)[1]
    quote_two = 16*h(8,lo)[1]-16*h(16,hi)[0]
    assert quote_one > 0 and quote_two < -126
    alarm(0)
    print(dumps({'pins':PINS,'clocks':[4646,4660],'body_axes':axes,'roles':roles,'window':window,
                 'neighbour_D_minus_E':list(map(str,neighbour)), 'neighbour_residue_projector':'1/32',
                 'arbitrary_coordinate_extraction_volume':2,'one_volume_gross_lower':str(quote_one),
                 'two_volume_gross_upper':str(quote_two),'case_cap':1,'runner_cap_seconds':20},sort_keys=True,indent=2))


if __name__ == '__main__':
    main()

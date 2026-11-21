"""Emit dyadic root certificates from the commit-pinned complex histogram."""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
import json


SOURCE = '87fbf4f7b35b0f18ab12b5767775a9a424cf0b15'
REPORT = 'research/p104-mixed-rank-supplier/AUDIT.json'
HERE = Path(__file__).resolve().parent
GRID = 160
TRIAL = F(388013, 10**8)
TILT = F(11, 50)
DROP = F(31, 100)


def root(rank, power):
    with localcontext() as ctx:
        ctx.prec = 90
        real = Decimal(rank) ** (Decimal(power.numerator) / Decimal(power.denominator))
        proposal = int(real * 2**GRID)
    return f'⟨{rank}, {power.numerator}, {power.denominator}, {proposal-2}, {proposal+3}⟩'


def table(name, power, paid, target):
    rows = []
    for rank in sorted(set(paid) | set(target)):
        rows.append(f'  ⟨{root(rank,power)}, {paid.get(rank,0)}, {target.get(rank,0)}⟩')
    return f'def {name} : List Row := [\n' + ',\n'.join(rows) + ']\n'


def build(source):
    signed = source['signed']
    paid, target = ({int(k):v for k,v in signed[key].items()} for key in ('paid','productive'))
    lower, upper = {7:1,3:1,5:1}, {9:1,4:1,1:2}
    t = 1-TRIAL
    blocks = [table('main',t,paid,target),table('split',t+TILT,paid,{}),
              table('prune',t-DROP,{},target),table('lift',t,upper,lower)]
    return '\n'.join(blocks+[f'def splitScale : Claim := {root(10,TILT)}',
                              f'def floorScale : Claim := {root(17,DROP)}'])+'\n'


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    report=json.loads((HERE/'vendor'/'mixed-audit.json').read_bytes())
    intro = '''import DyadicRoot

/-! Dyadic proposals for the fixed complex word. All enclosing powers use
the integer multiplication certificates of the predecessor. -/
namespace CarrierTrial
open DyadicRoot

structure Row where
  power : Claim
  paid : Nat
  target : Nat

'''
    args.output.write_text(intro + build(report)+'end CarrierTrial\n',encoding='utf-8')

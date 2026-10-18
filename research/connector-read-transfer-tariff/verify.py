"""All-price frontier, independent physical oracle and arbitrary-dirty replay."""
from pathlib import Path
import argparse
from fractions import Fraction as Q
import hashlib
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_sources import HERE, predecessor
import synthesis as s
import oracle


def encode(value): return json.dumps(value, indent=2, sort_keys=True)+'\n'


def reject(action, expected):
    try: action()
    except ValueError as error:
        s.need(str(error) == expected, 'unexpected fault '+str(error))
        return str(error)
    raise ValueError('ineffective control '+expected)


def result():
    legacy = predecessor()  # Authenticity gate precedes any predecessor execution.
    old = legacy.synthesize(list(s.WORD), list(s.COLORS), list(range(1, 8)))
    s.need(sum(old['minimum_reads'].values()) == 15 and old['transfers'] == 6, 'credited minimum-read baseline')
    # Predecessor child operations include the fixed physical port.
    s.need(all(len(op) == 2 or op[2] == 0 for op in old['program']), 'baseline physical port')
    old_invoice = oracle.formal([op[:2] for op in old['program']])
    witnesses, records, states = s.synthesize()
    expected = [[2, 2, 2, 2, 2, 2, 2, 2, 4], [3, 3, 2, 2, 2, 2, 2, 2, 3], [4, 2, 2, 2, 2, 2, 2, 2, 3]]
    s.need([w['invoice'] for w in witnesses] == expected, 'complete count Pareto frontier')
    for w in witnesses: s.need(oracle.formal(w['program']) == w['invoice'], 'formal full dirty endpoint and invoice')
    rectangle = oracle.physical_rectangle()
    clipped = [r for r in records if r[-2] <= 4 and r[-1] <= 3]
    s.need(clipped == rectangle, 'independent entire physical-state rectangle')
    terminal = []
    for cut, a, b, available, u, v in rectangle:
        if cut != 6 or (a, b) != (8, 16): continue
        minima = oracle.subset_reads(available)
        s.need(len(minima) == 7, 'complete terminal read span')
        terminal.append((u, v, *(minima[t] for t in range(1, 8))))
    front = sorted(x for x in set(terminal) if not any(y != x and s.leq(y, x) for y in terminal))
    s.need([list(x) for x in front] == expected, 'independent subset-read frontier')
    # Complete call-count price envelope, including unequal orientation prices.
    prices = []
    for u in (Q(1,4), Q(1), Q(4)):
        for v in (Q(1,4), Q(1), Q(4)):
            for a7 in (Q(1,3), min(u+v, 2*u), Q(12)):
                aa = [Q(k, 7) for k in range(1, 7)] + [a7]
                bb = [Q(2), Q(3,2), Q(5)]
                direct = min(2*sum(bb)+r[0]*u+r[1]*v+sum(a*n for a,n in zip(aa,r[2:])) for r in expected)
                formula = 2*sum(bb)+2*sum(aa)+min(2*u+2*v+2*a7, 3*u+3*v+a7, 4*u+2*v+a7)
                s.need(direct == formula, 'exact positive-price formula')
                prices.append([str(u), str(v), str(a7), str(formula)])
    dense_columns = 0
    for w in witnesses:
        for width in (1, 2, 3):
            for seed in range(8):
                # Includes zero, singular and noncommuting binary linear maps.
                matrices = [[((seed+3*k+5*j)*(seed+1+j)) % (1 << width) for j in range(width)] for k in range(10)]
                for column in range(12*width):
                    state = [0]*12; state[column//width] = 1 << (column % width)
                    want = oracle.expected(matrices, state)
                    got = oracle.dense(w['program'], width, matrices, state)
                    s.need(got == want, 'dense arbitrary-dirty forward column')
                    s.need(oracle.dense(w['program'], width, matrices, got, True) == state, 'dense inverse restores every row')
                    dense_columns += 1
    controls = {}
    p = witnesses[0]['program']
    for label, kind, failure in [('omitted_read', 'A', 'dirty target endpoint'), ('omitted_source', 'B', 'fixed source word')]:
        i = next(i for i,x in enumerate(p) if x[0] == kind)
        controls[label] = reject(lambda i=i: oracle.formal(p[:i]+p[i+1:]), failure)
    # Removing the last transfer need not alter source legality, but breaks return.
    i = max(i for i,x in enumerate(p) if x[0] == 'C')
    controls['omitted_final_transfer'] = reject(lambda: oracle.formal(p[:i]+p[i+1:]), 'root return')
    controls['state_cap'] = reject(lambda: s.synthesize(1), 'exact state cap exceeded')
    # A strict price foil: minimum reads can cost more despite fewer A calls.
    s.need(min(sum(r) for r in expected) == 20 and sum(old_invoice) == 21, 'unit-price minread foil')
    controls['minimum_read_is_price_optimum'] = 'REJECT: unit calls20 versus21, before common6 source calls'
    return {'status':'PASS_CONNECTOR_READ_TRANSFER_TARIFF','source_word':list(s.WORD),'colors':list(s.COLORS),
            'witnesses':witnesses,'complete_states':states,'complete_cost_labels':len(records),
            'complete_labels_sha256':hashlib.sha256(encode(records).encode()).hexdigest(),
            'independent_rectangle_records':len(rectangle),
            'independent_rectangle_sha256':hashlib.sha256(encode(rectangle).encode()).hexdigest(),
            'predecessor_minimum_read_invoice':old_invoice,
            'exact_price_cases':prices,'dense_forward_inverse_columns':dense_columns,
            'controls':controls,
            'scope':'All-length exact positive complete-call tariffs for fixed B001122/colors112. No selected caller, source-order optimum, physical overhead bound or new kappa.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',type=Path);args=parser.parse_args()
    if args.write and args.write.exists(): raise FileExistsError(args.write)
    receipt=result()
    if args.write:
        with args.write.open('x',encoding='utf-8',newline='\n') as f:f.write(encode(receipt))
    else:s.need(encode(receipt)==encode(json.loads((HERE/'RESULT.json').read_text())), 'complete typed receipt mismatch')
    print('PASS_CONNECTOR_READ_TRANSFER_TARIFF front=3 states='+str(receipt['complete_states'])+' dense='+str(receipt['dense_forward_inverse_columns']))


if __name__=='__main__':main()

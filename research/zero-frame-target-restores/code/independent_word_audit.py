"""Independent standard-library bitset replay and literal cost recount.

Reads the final modified word directly; does not import repository code or use
native PASS statuses as a substitute for the following calculations.
"""
from array import array
from collections import Counter
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import time
import sys

START = time.monotonic()
HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]).resolve()
LEAD = OUT if (OUT / 'COHORT249-RECORDS.bin').exists() else OUT / ('targeted' if (OUT / 'targeted').exists() else 'lead')
path = LEAD / 'COHORT249-RECORDS.bin'
data = path.read_bytes()
word = array('i')
word.frombytes(data)
assert word.itemsize == 4 and len(word) % 6 == 0
n, v, replicas, m, R = 20107, 1760, 120, 120, 16587
expected = [1 << s for s in range(n)]
for s in range(v, 2*v):
    expected[s] ^= 1 << (s-v)

def replay(reverse):
    rows = [1 << s for s in range(n)] + [0]
    order = range(len(word)-6, -1, -6) if reverse else range(0, len(word), 6)
    copies = erasures = 0
    for i in order:
        op, a, b, c, f, z = word[i:i+6]
        assert op in (0, 1, 2, 3) and 0 <= a <= n
        if op == 1:
            assert 0 <= b <= n and a != b
            if c & 1:
                rows[a] ^= rows[b]
        elif op == (3 if reverse else 2):
            assert b == n
            rows[b] = rows[a]
            copies += 1
        elif op == (2 if reverse else 3):
            assert b == n and rows[a] == rows[b], 'COPY/ERASE value mismatch'
            rows[b] = 0
            erasures += 1
    assert copies == erasures == 24 and rows[n] == 0
    assert rows[:n] == expected, 'final formal-column mismatch'
    return {'direction': 'inverse' if reverse else 'forward',
            'formal_columns': n, 'copies': copies, 'erasures': erasures}

columns = [replay(False), replay(True)]
H = Counter()
adds = units = copies = 0
for i in range(0, len(word), 6):
    op, a, b, c, f, z = word[i:i+6]
    if op == 0 and f:
        assert f > 0
        H[f] += 1
    elif op == 1:
        adds += 1
        units += abs(c)
    elif op == 2:
        H[z] += 1
        copies += 1
literal = Counter({r: 600*count for r, count in H.items()})
for r in (4, 23, 46, 50):
    literal[r] += 120*2*v
calls = sum(literal.values())
mass = sum(r*count for r, count in literal.items())
invoice = json.loads((OUT / 'temporal/COHORT-FINITE-INVOICE.json').read_text())
bank_path = OUT / 'compiler/BANK-REVIEW.json'
if not bank_path.exists(): bank_path = OUT / 'compiler/COHORT-BANK-REVIEW.json'
bank = json.loads(bank_path.read_text())
price = json.loads((LEAD / 'FIXED-PRICE.json').read_text())
stock = invoice['literal_stock']
assert copies == 24 and max(literal) < 60
assert stock == bank['literal_stock'] == 5*invoice['normalized_stock']
assert 120*stock-mass == 528000
assert {str(r): str(count) for r, count in literal.items()} == invoice['literal_histogram']
assert calls == int(invoice['positive_rank_children']) and mass == int(invoice['literal_rank_mass'])
weighted = replicas*(5*adds+6*v)
unit = replicas*(5*units+6*v)
routes = replicas*(24*v+10*R)
normalizer = max(548, int(bank['max_new_chart_factors'])) + 239
assert normalizer == int(invoice['normalizer_factor_bound'])
selectors = 10*replicas*((stock-1)+R*120*normalizer)
coefficient = (unit+routes*16*14401*14401+routes*(stock+24)
               +calls*(8*120*120+8)+calls*(128*240**3)
               +16*120**3+120*replicas+calls+selectors+1)
for name, count in [('global_weighted_additions', weighted),
                    ('global_unit_expanded_additions', unit), ('route_families', routes),
                    ('extra_selector_calls', selectors), ('full_counted_primitive_coefficient', coefficient)]:
    assert count == int(invoice[name]), name
assert coefficient == int(price['finite_coefficient_recomputed']) and coefficient < 2**80
assert len(price['strict_constraints']) == 47
assert all(Fraction(value) > 0 for value in price['strict_constraints'].values())
assert all(Fraction(value) > Fraction(price['kappa']) for value in price['seven_margins'].values())
result = {'status': 'PASS_INDEPENDENT_PYTHON_BITSET_COLUMNS_AND_LITERAL_CENSUS',
          'word_sha256': hashlib.sha256(data).hexdigest(), 'columns': columns,
          'raw_rank_mass': sum(r*count for r, count in H.items()), 'raw_additions': adds,
          'literal_calls': calls, 'literal_rank_mass': mass, 'literal_stock': stock,
          'selector_calls': selectors, 'coefficient': coefficient,
          'strict_positive_constraints': 47, 'positive_margin_above_kappa': 7,
          'elapsed_seconds': time.monotonic()-START,
          'limitations': 'Does not independently prove frame geometry, chart compiler, recurrence enclosures, inherited constants or all-size interfaces.'}
(OUT / 'independent-word-audit.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))

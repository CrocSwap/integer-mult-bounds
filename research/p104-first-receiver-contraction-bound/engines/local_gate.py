"""Certify the invertible one-receiver obstruction from the frozen transpose."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
import sys

PIN = 'a7b794a3a3d1f79c1f277334a03bf6ff98044d132a9e8fdb1122a8cc59d3f9ac'


def classify(values, receiver, required):
    old = values[receiver]
    after = old + required
    if any(v for r, v in values.items() if r != receiver):
        return 'unresolved', after, None
    diagonal = after / old if old else None
    if required and (not old or not diagonal):
        return 'excluded', after, diagonal
    return 'unresolved', after, diagonal


assert classify({1: Q(1), 2: Q(0)}, 1, Q(-1)) == ('excluded', 0, 0)
assert classify({1: Q(1), 2: Q(0)}, 1, Q(1)) == ('unresolved', 2, 2)
assert classify({1: Q(1), 2: Q(1)}, 1, Q(-1)) == ('unresolved', 0, None)
assert classify({1: Q(0), 2: Q(0)}, 1, Q(1)) == ('excluded', 1, None)
raw = Path(sys.argv[1]).read_bytes()
assert sha256(raw).hexdigest() == PIN, 'changed transpose receipt'
data = loads(raw)
assert data['case_count'] == 1 and data['cut'] == 42651
assert data['bank_owned'] == [] and data['bank_public'] == [165, 586, 793]
bank = {role: Q(v) for role, v in data['bank_values']}
receiver = data['receiver']
assert bank[receiver] == Q(data['receiver_old_coordinate'])
result, after, diagonal = classify(bank, receiver, Q(data['required_coordinate']))
assert result == 'excluded' and after == diagonal == 0
print(dumps({
    'cut': 42651, 'input_axis': 930, 'case_count': 1,
    'scope': 'same-clock chart652 one-receiver replacement with unchanged donors',
    'old_receiver': str(bank[receiver]), 'required_add': data['required_coordinate'],
    'distinct_donor_values': {str(r): str(v) for r, v in bank.items() if r != receiver},
    'required_receiver_return': str(after), 'necessary_receiver_diagonal': str(diagonal),
    'status': result, 'pin': PIN,
}, indent=2, sort_keys=True))

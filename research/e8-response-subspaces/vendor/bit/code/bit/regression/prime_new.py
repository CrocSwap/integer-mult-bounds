"""PR #315's prime-witness rule on every frame the edit adds (determinant factored over the allowed primes, residual < 2^80)."""
import json, sys, importlib.util, os
H = os.path.dirname(os.path.abspath(__file__))
def load(n):
    s = importlib.util.spec_from_file_location(n, os.path.join(H, n + '.py')); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
pw = load('prime_witnesses')
def validate_record(row, dimension, determinant, allowed_primes):   # PR #315 prime_check.validate_record, verbatim logic
    assert type(row['dimension']) is int and type(row['determinant']) is int and type(row['residual']) is int, 'exact integer witness fields'
    assert row['dimension'] == dimension and row['determinant'] == determinant != 0, 'exact determinant mismatch or singular basis'
    assert 0 < row['residual'] < 2**80, 'retained prime lower bound'
    product = row['residual']
    for prime, exponent in row['factors'].items():
        q = int(prime); assert q in allowed_primes and type(exponent) is int and exponent > 0, 'factor shape'; product *= q**exponent
    assert product == abs(determinant), 'factor identity'
base = json.load(open(sys.argv[1] + '/frames.json'))['frames']; word = json.load(open(sys.argv[2] + '/frames.json'))['frames']
new = {k: f for k, f in word.items() if k not in base}; primes = set(); bits = 0
for k, f in new.items():
    B = f['B']; s = list(map(sum, B))
    gram = [[9*sum(a*b for a, b in zip(x, y)) - s[i]*s[j] for j, y in enumerate(B)] for i, x in enumerate(B)]
    det = pw.det(gram); powers, residual = pw.factor_witness(det)
    row = dict(dimension=len(B), determinant=det, residual=residual, factors={p: e for p, e in powers.items() if e})
    validate_record(row, len(B), det, pw.PRIMES); primes.update(map(int, row['factors'])); bits = max(bits, abs(det).bit_length())
print('PASS prime witnesses for', len(new), 'new frames; max determinant bits', bits, '; primes', sorted(primes))

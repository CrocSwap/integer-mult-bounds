"""Independent local algebra and frozen-source checks for literal layer egress.

This is not another whole-machine simulator. The root reviewer separately
implemented one. Here all numerical checks use integer identities independently
of the author's numerical verifier; finite checks supplement REVIEW.md.
"""
from pathlib import Path
import hashlib
import importlib.util
import itertools
import json
import sys

PACKAGE = (Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else
           Path(__file__).resolve().parents[1])
EXPECTED_SOURCE = '5875981b27bbb131a1e13ffca7f7eb920aa85b90699e6d40a85bd3902ff073e7'
EXPECTED_TABLE = 'd3021bc0d7b378741e64ae768171f5aec1f289b15265f4463e7b91b887f11243'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def signed_value(bits):
    return sum(b << j for j, b in enumerate(bits)) - (bits[-1] << len(bits))


def row_bits(a, c, width, alpha, beta):
    carry = 0
    result = []
    for j in range(width + 2):
        # Python signed shift supplies the infinite two's-complement extension.
        x, y = (a >> j) & 1, (c >> j) & 1
        total = carry + alpha*x + beta*y
        result.append(total & 1)
        carry = total // 2
    return result


def restored_stream(magnitude, negative, length):
    carry, bits = int(negative), []
    for j in range(length):
        source = (magnitude >> j) & 1
        total = 1-source+carry if negative else source
        bits.append(total & 1)
        carry = total // 2 if negative else 0
    return bits


pins = json.loads((PACKAGE / 'SOURCES.json').read_text())
authenticated = []
for pin in pins['files']:
    data = (PACKAGE / pin['local']).read_bytes()
    need(len(data) == pin['bytes'], 'byte count: '+pin['local'])
    need(hashlib.sha256(data).hexdigest() == pin['sha256'], 'SHA256: '+pin['local'])
    blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    need(blob == pin['blob'], 'Git blob: '+pin['local'])
    authenticated.append(pin['local'])
source = (PACKAGE / 'egress.py').read_bytes()
need(hashlib.sha256(source).hexdigest() == EXPECTED_SOURCE, 'science source drift')
spec = importlib.util.spec_from_file_location('peer_checked_egress', PACKAGE/'egress.py')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
code, alphabet = module.compile_egress()
table_hash = hashlib.sha256(json.dumps(code, separators=(',', ':'), sort_keys=True).encode()).hexdigest()
need(table_hash == EXPECTED_TABLE, 'emitted table drift')
need(len(code) == 17814 and set(alphabet) == {'_', '0', '1', '|'}, 'table inventory')
need(all(ins[0] in {'read', 'write', 'move', 'goto', 'halt'} for ins in code), 'nonliteral opcode')

# Derive powers by repeated Gaussian integer multiplication, without the
# production parity/rotation recurrence. This is finite corroboration of the
# universal b^2=-i/2 identity in the written review.
rows = set()
real, imag = 1, 0
for degree in range(1, 129):
    real, imag = real+imag, imag-real
    denominator = 1 << (degree//2)
    need(real % denominator == imag % denominator == 0, 'Gaussian numerator divisibility')
    r, s = real//denominator, imag//denominator
    expected = ((r, -s), (s, r))
    need(module.numerator_rows(degree % 8) == expected, 'fixed Gaussian row')
    rows.update(expected)

carry_checks = 0
for (alpha, beta), carry, x, y in itertools.product(rows, (-2, -1, 0, 1), (0, 1), (0, 1)):
    total = carry+alpha*x+beta*y
    next_carry, digit = divmod(total, 2)
    need(next_carry in (-2, -1, 0, 1), 'finite carry closure')
    need(total == digit+2*next_carry, 'finite carry recurrence')
    carry_checks += 1

signed_checks = 0
for width in range(1, 8):
    values = range(-(1 << (width-1)), 1 << (width-1))
    for a, c, (alpha, beta) in itertools.product(values, values, rows):
        result = signed_value(row_bits(a, c, width, alpha, beta))
        need(result == alpha*a+beta*c, 'two sign-extension cells')
        need(abs(result) <= 1 << width, 'numerator magnitude bound')
        signed_checks += 1

range_checks = 0
for width in range(1, 10):
    length = width+4
    for magnitude in range((1 << (width+1))+1):
        for negative in (False, True):
            bits = restored_stream(magnitude, negative, length)
            value = -magnitude if negative else magnitude
            need(signed_value(bits) == value, 'sign restoration including negative zero')
            accepted = all(bit == bits[width-1] for bit in bits[width:])
            need(accepted == (-(1 << (width-1)) <= value < (1 << (width-1))), 'range criterion')
            range_checks += 1

# Concrete negative controls for tempting incorrect replacements of proved
# steps. They exercise the independent oracle, not altered production code.
need((-1)//2 != 0, 'control: floor differs from toward-zero')
need(signed_value(row_bits(63, 63, 7, 1, 1)[:7]) != 126, 'control: narrow sum overflows')
need(2*100+2*max(7, 100) > 2*100+2*7, 'control: source-only commit trace undercharges')
need(16+1 > 16, 'control: independent width bounds do not imply zero padding fits')

receipt = {
    'status': 'PASS_INDEPENDENT_LOCAL_ALGEBRA_AND_SOURCE_CHECK',
    'source_sha256': EXPECTED_SOURCE,
    'proof_sha256': hashlib.sha256((PACKAGE/'PROOF.md').read_bytes()).hexdigest(),
    'table_sha256': table_hash,
    'instruction_locations': len(code),
    'authenticated_files': authenticated,
    'Gaussian_power_degrees': [1, 128],
    'local_carry_checks': carry_checks,
    'signed_row_checks': signed_checks,
    'range_checks': range_checks,
    'negative_controls': 4,
    'limits': [
        'Finite checks are not an all-size proof; see REVIEW.md.',
        'No author numerical verifier or full-machine interpreter is executed here.',
        'Source blobs are authenticated against the supplied exact provenance pins.',
        'Parent reviewer supplies separately executed dense-machine evidence.'
    ]
}
print(json.dumps(receipt, sort_keys=True))
need(receipt == json.loads(Path(__file__).with_name('ALGEBRA-SOURCE-RESULT.json').read_text()), 'committed independent receipt')

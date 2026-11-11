"""Authenticate and independently replay the fixed-word singleton exclusion."""
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import runpy

HERE = Path(__file__).resolve().parent
WORD = 'inputs/WORD.json.gz'
CONTINUATION = 'CONTINUATION.json'
PRIMARY = runpy.run_path(str(HERE / 'singleton.py'))
INDEPENDENT = runpy.run_path(str(HERE / 'verify.py'))
read_json = INDEPENDENT['read_json']


def verify_word(raw, pin):
    assert sha256(raw).hexdigest() == pin['sha256'] == PRIMARY['WORD_SHA256'] == INDEPENDENT['DIGEST']
    assert sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == pin['git_blob']
    return read_json(gzip.decompress(raw))


def verify_controls(raw, pin):
    for check in (lambda: read_json('{"inputs": {}, "inputs": {}}'),
                  lambda: verify_word(raw + b'\0', pin)):
        try:
            check()
        except AssertionError:
            continue
        raise AssertionError('Mutation control accepted')
    return ['REJECT_DUPLICATE_MANIFEST_KEYS', 'REJECT_CHANGED_WORD']


def tariff():
    # For 0 <= k <= 1/200, 2**k - 1 <= k/(1-k) by
    # log(2) < 1 and comparison of the exponential and geometric series.
    # The maximum rank and 17-copy caller give the factor 153.
    k_max = Fraction(1, 200)
    r_max, copies = 9, 17
    maximum = copies * r_max * k_max / (1 - k_max)
    assert maximum == Fraction(153, 199) < 1
    return {'kappa_upper': str(k_max), 'copies': copies, 'rank_upper': r_max,
            'gross_upper': str(maximum), 'positive_paid_child_lower': 1}


def run():
    provenance = read_json((HERE / 'PROVENANCE.json').read_bytes())
    assert set(provenance['inputs']) == {WORD}
    pin = provenance['inputs'][WORD]
    assert pin['commit'] == 'ed090b57ed88f8859e5ff4643645099e6ba856ea'
    assert pin['path'] == 'research/p104-terminal-cut-rechart/WORD.json.gz'
    raw = (HERE / WORD).read_bytes()
    word = verify_word(raw, pin)
    receipt = (HERE / CONTINUATION).read_bytes()
    expected = read_json(receipt)
    primary = PRIMARY['assess'](word, 1396, 1)
    assert read_json(json.dumps(primary)) == expected
    checked = INDEPENDENT['run'](word, expected)
    checked['dependencies'] = {WORD: pin['sha256'], CONTINUATION: sha256(receipt).hexdigest()}
    return {'singleton': checked, 'tariff': tariff(), 'controls': verify_controls(raw, pin),
            'status': 'PASS_FIXED_WORD_SINGLETON_SPLIT_BOUND'}


if __name__ == '__main__':
    assert __debug__
    result = json.dumps(run(), sort_keys=True, indent=2) + '\n'
    frozen = HERE / 'RESULT.json'
    if frozen.exists():
        assert result == frozen.read_text()
    print(result, end='')

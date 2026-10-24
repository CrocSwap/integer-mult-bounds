#!/usr/bin/env python3
"""Compare the independently emitted scalar factors after namespace changes."""

from hashlib import sha256
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PINS = {
    'integrated': 'a0e9cd4f125089844e67090ab0e8e3fc94e449a146e06dbcc36345dd517a6b9e',
    'five_minor_source': 'f5c9a49201d3900d3760804b4801b06df21ae100ae62e7b6e0ced283f4f4fc56',
    'one_minor_source': '525822746e2d760a81c5a4c8847c25974d0a419a2c5abbaa0472d13bde1c6aa9',
}


def read(path, pin, compressed):
    raw = path.read_bytes()
    if compressed:
        raw = gzip.decompress(raw)
    assert sha256(raw).hexdigest() == pin
    return json.loads(raw)


def main():
    native = read(HERE / 'SERIAL-BALANCED-PROGRAMS.json.gz', PINS['integrated'], True)
    five = read(HERE.parent / 'bridge-access-20261017/weighted-gauges/SCALED-ROWS-PROGRAMS.json.gz',
                PINS['five_minor_source'], True)
    one = read(HERE.parent / 'independent-review-20261017/odd-grid-a8-20261017/A8-ODD-GRID-WORDS.json',
               PINS['one_minor_source'], False)
    matches = {}
    for variant, part, five_key, five_part, one_key, offset, frame in (
        ('balanced_forward', 'prefix', 'ordinary_forward', 'initial_Y_events', 'H', 112, 0),
        ('balanced_backward', 'suffix', 'ordinary_inverse', 'completed_X_events', 'H_inverse', 0, 1),
        ('diagonal_backward', 'suffix', 'fused_inverse', 'completed_X_events', 'H_inverse_fused_upper', 0, 1),
    ):
        old = five['words'][five_key][five_part]
        for e in old:
            for key in ('target', 'source'):
                if e.get(key) == 704:
                    e[key] = 632
        old_one = []
        for e in one[one_key]:
            if e[0] == 'clear' and old_one and old_one[-1][0] == 'clear':
                continue
            old_one.append(e)
        def field(p):
            return 632 if p == 112 else p + offset
        translated = []
        for e in old_one:
            item = {'kind': e[0], 'target': field(e[1]), 'frame': frame}
            if e[0] == 'add':
                item.update(source=field(e[2]), coefficient=e[3])
            elif e[0] == 'scale':
                item['coefficient'] = e[2]
            elif e[0] == 'divide_odd':
                item['divisor'] = e[2]
            else:
                assert e[0] == 'clear'
            translated.append(item)
        translated[-1]['frame'] = 0
        for provider in ('base', 'extra'):
            assert native['families']['five_minors']['providers'][provider]['programs'][variant][part] == old
            assert native['families']['one_minor']['providers'][provider]['programs'][variant][part] == translated
        matches[variant] = {'five_minor_events': len(old), 'one_minor_events': len(translated),
                            'both_provider_matches': True}
    receipt = {'status': 'PASS_INDEPENDENT_SERIAL_FACTOR_SOURCE_MATCH', 'source_pins': PINS,
               'matches': matches, 'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
               'changes': ['Rename old C0 roles to 632.',
                           'Remove seven adjacent duplicate owned CLEARs in the one-minor source.',
                           'Bind each one-minor factor to its common input-I or output-FULL frame; final C0 is I.']}
    (HERE / 'SERIAL-SOURCE-COMPARISON.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'])


if __name__ == '__main__':
    main()

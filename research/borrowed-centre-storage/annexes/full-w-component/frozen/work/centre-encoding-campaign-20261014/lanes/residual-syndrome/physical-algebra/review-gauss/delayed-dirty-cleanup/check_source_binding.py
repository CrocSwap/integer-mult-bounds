"""Bind the retained source slice and the separate prefix receipt."""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[3]
SOURCE = LANES / 'residual-syndrome/physical-algebra/eight-record-review-20261015'
PINS = {}


def read(path, digest, as_json=True):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError('Source pin: ' + str(path))
    PINS[str(path.relative_to(LANES))] = digest
    return json.loads(raw) if as_json else raw


def main():
    word = read(LANES / 'portable-source-codes/dirty-record-hosting-20261015/eight-records/EIGHT-RECORD-WORDS.json',
                '8dcb0f29d2b0275e5d5395511d10451b8675c9ffe37ebdbd452c0132a17b15f4')
    f0 = read(SOURCE / 'DELAYED-CLEANUP-WORD.json',
              'bf3df2f047e4edb26ce2b73d3919db862f1cd630ee90fda5f3144469bdde7883')['scalar_F0_content']
    original = word['owned_eight_A']['repair'][1459:2429]
    inverted = []
    for event in original[::-1]:
        new = dict(event)
        c = F(new['c'])
        new['c'] = str(-c if new['op'] == 'add' else 1 / c)
        inverted.append(new)
    if f0[16:986] != inverted:
        raise ValueError('The retained 970-event inverse slice')

    consumer = LANES / 'portable-source-codes/common-f-independent-review-20261015'
    review = read(consumer / 'REVIEW.json',
                  'a930a9cda3f573f16b59d4538bc2920d9d22a8ba0e74e4a0e5ad6ce926a16fef')
    for name, digest in review['files'].items():
        read(consumer / name, digest, False)
    manifest = read(SOURCE / 'CLEANUP-PRECISION-MANIFEST.json',
                    '33c85919f7e4416a7206f4c1fca99096e95eefb9b74958aa0a9e9c7dedf9123d')
    for name, digest in manifest.items():
        read(SOURCE / name, digest, False)
    own = json.loads((HERE / 'PREFIX-CHECK.json').read_text())
    produced = json.loads((SOURCE / 'DELAYED-CLEANUP-PREFIX.json').read_text())
    if not (own['maximum_l1'] == produced['maximum_free_route_row_l1'] == '1407'
            and own['maximum_debt'] == produced['fractional_reserve'] == 3
            and own['l1_event'] == 2620 and own['debt_event'] == 2614):
        raise ValueError('Independent prefix values')
    result = {'status': 'PASS_STATIC_SOURCE_AND_PREFIX_BINDING',
              'source_inverse_events': 970, 'source_inverse_slice': [1459, 2429],
              'f0_forward_slice': [16, 986], 'source_inverse_bytes_equal': True,
              'source_pins': PINS, 'producer_or_review_module_imported': False}
    (HERE / 'SOURCE-BINDING.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()

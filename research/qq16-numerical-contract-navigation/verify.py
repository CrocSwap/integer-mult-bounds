#!/usr/bin/env python3
"""Bind QQ16 numerical navigation to sources; do not replay a supplier."""

import copy
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAP = ROOT / 'docs/research/qq16-numerical-contract-map.md'
CHAIN = (
    (2707, 1600, 'efa51a6c7ffec6edd556a98deedfe9deeba65809', 'qq16-line-normalized-decoder', 'ywz65'),
    (2736, 1700, 'eba0d6111a773cd13f5c0afb4354af2c85d04c3a', 'qq16-zero-retention-defects', 'petalas'),
    (2771, 1700, 'e707681c3f6db70d0432501403e2122794a36ade', 'qq16-rounded-native-line', 'petalas'),
    (2807, 1700, '6fbab8c4b95cdf75dfcbb33806c31349408d73a2', 'qq16-finite-dyadic-format', 'petalas'),
    (2811, 1700, '3d07cfe7f5035bccf7975616b0f3bd53a3b78ca8', 'qq16-rounded-pair-bit-circuit', 'petalas'),
)
SCAN_HEAD = '28c5c068b64c18074ab4044e47a7c9f52eb6e5de'
MAX_BYTES = 1_048_576


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    with path.open('rb') as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, 'source exceeds 1 MiB: ' + str(path))
    return raw


def check_digest(raw, pin):
    require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'SHA256 source binding')
    blob = b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw
    require(hashlib.sha1(blob).hexdigest() == pin['git_blob'], 'Git blob source binding')


def load_sources():
    manifest = json.loads(read(HERE / 'SOURCES.json'))
    pins = [row for row in manifest['files'] if row['usage'] == 'input']
    expected = {f'research/community-efficient{n}-audit/DISPOSITIONS.json' for n in (1600, 1700)}
    expected.update(f'research/{row[3]}/README.md' for row in CHAIN)
    expected.update(f'research/{row[3]}/RESULT.json' for row in CHAIN[1:])
    require(len(pins) == len(expected) == 11, 'fixed source inventory')
    require({row['path'] for row in pins} == expected, 'complete source inventory')
    data = {}
    for pin in pins:
        raw = read(ROOT / pin['path'])
        check_digest(raw, pin)
        if pin['path'].endswith('.json'):
            data[pin['path']] = json.loads(raw)
    pending = json.loads(read(HERE / 'PENDING.json'))
    require(pending['pr'] == 2876 and pending['author'] == 'Arham-Tahir64', 'pending credit')
    require(pending['head'] == SCAN_HEAD, 'pending exact head')
    snapshots = {'source/PR2876-README.md', 'source/PR2876-RESULT.json'}
    require(len(pending['files']) == 2, 'two pending snapshots')
    require({pin['path'] for pin in pending['files']} == snapshots, 'pending inventory')
    for pin in pending['files']:
        check_digest(read(HERE / pin['path']), pin)
    data['scan'] = json.loads(read(HERE / 'source/PR2876-RESULT.json'))
    return data, manifest['files'][0]


def check_chain(data):
    for number, review, head, package, author in CHAIN:
        rows = data[f'research/community-efficient{review}-audit/DISPOSITIONS.json']['pull_requests']
        require(len(rows) <= 100, 'bounded review inventory')
        found = [row for row in rows if row['number'] == number]
        require(len(found) == 1, 'one exact reviewed PR')
        row = found[0]
        require(row['reviewed_head'] == row['current_head'] == head, 'reviewed source head')
        require(row['disposition'] == 'incorporated', 'incorporation status')
        require(row['integration_location'] == ['research/' + package], 'retained location')
        require(row['metadata']['author']['login'] == author, 'source credit')


def check_facts(data):
    error = data['research/qq16-zero-retention-defects/RESULT.json']
    require((error['events'], error['cuts'], error['relative_guard_bits']) == (3823, 3816, 22), 'word/guard')
    require(error['peaks'][:3] == ['32368', '2919388', '199144'], 'relative majorant')
    require(2**21 < 2919388 + 199144 < 2**22, 'strict guard arithmetic')
    line = data['research/qq16-rounded-native-line/RESULT.json']
    require(line['source'] == {'events': 3823, 'negative': 112, 'positive': 224, 'signed_lines': 336}, 'signed lines')
    grid = data['research/qq16-finite-dyadic-format/RESULT.json']
    require(grid['grid_certificate']['grid_bound'] == 'Q0+3*k+6', 'finite grid recurrence')
    require(grid['signed_bits'] == 'Qmax + E + 20', 'finite register width')
    require(grid['grid_certificate']['changed_cuts'] == error['cuts'], 'same changed cuts')
    reserve = 64 + 22 + 73 // 2
    qmax = 64 + 3 * reserve + 6
    width = qmax + 20
    require((reserve, qmax, width) == (122, 436, 456), 'common example')
    w = width - 3
    out_bits, ell = w + 2, w.bit_length()
    pair_gates = 24 * out_bits * ell + 52 * out_bits + 4 * 2**ell + 4 * ell + 4
    pair = data['research/qq16-rounded-pair-bit-circuit/RESULT.json']['invoice']
    examples = [row for row in pair['runtime_examples'] if row['input_bits'] == w]
    require(len(examples) == 1 and examples[0]['gates'] == pair_gates == 124028, 'pair width and bill')
    popcount = sum(i.bit_count() for i in range(w - reserve))
    constant = 2 * w - 2 * reserve + popcount + 3
    coefficient = 8 * w
    expected = {'width': w, 'reserve': reserve, 'pair_gates': pair_gates,
                'popcount_sum': popcount, 'scan_D_coefficient': coefficient,
                'scan_constant': constant, 'decoder_pairs_lambda_ND_coefficient': 336 * pair_gates // 2,
                'decoder_scan_ND_coefficient': 336 * coefficient,
                'decoder_scan_N_constant': 336 * constant}
    require(data['scan']['example'] == expected, 'pending scan receipt and units')
    require(expected['decoder_pairs_lambda_ND_coefficient'] == pair['example_pair_evaluations_coefficient'], 'pair subtotal')
    require((336 * pair_gates // 2 + 336 * coefficient, 336 * constant) == (22054368, 666624), 'lambda=1 subtotal')


def check_map(document):
    require(len(document) <= 30_000, 'bounded navigation page')
    for row in CHAIN:
        require(row[2] in document, 'map cites exact retained head')
    require(SCAN_HEAD in document and 'PR2876 is pending' in document, 'pending status explicit')
    require('22,054,368*N*D + 666,624*N' in document, 'map subtotal')
    links = re.findall(r'\]\(([^)\n]+)\)', document)
    require(len(links) <= 100, 'bounded local link inventory')
    for link in links:
        if link.startswith('https://'):
            continue
        path = (MAP.parent / link.split('#', 1)[0]).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(), 'local source link: ' + link)


def controls(data, document, pin):
    for case in range(7):
        changed = copy.deepcopy(data)
        text = document
        if case == 0:
            changed['research/community-efficient1700-audit/DISPOSITIONS.json']['pull_requests'] = []
        elif case == 1:
            changed['research/qq16-zero-retention-defects/RESULT.json']['relative_guard_bits'] = 21
        elif case == 2:
            changed['research/qq16-finite-dyadic-format/RESULT.json']['signed_bits'] = 'Qmax + E + 19'
        elif case == 3:
            changed['scan']['example']['decoder_scan_ND_coefficient'] = 0
        elif case == 4:
            text = text.replace('PR2876 is pending', 'PR2876 is incorporated')
        elif case == 5:
            text = text.replace('22,054,368*N*D + 666,624*N', '20,836,704*N*D')
        try:
            if case == 6:
                check_digest(b'changed source bytes', pin)
            check_chain(changed)
            check_facts(changed)
            check_map(text)
        except ValueError:
            continue
        raise ValueError('undetected negative control ' + str(case))


def main():
    data, pin = load_sources()
    document = read(MAP).decode('utf-8')
    check_chain(data)
    check_facts(data)
    check_map(document)
    controls(data, document, pin)
    print('PASS_QQ16_NUMERICAL_NAVIGATION retained=5 pending=1 controls=7 bindings_only no_new_kappa')


if __name__ == '__main__':
    main()

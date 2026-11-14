#!/usr/bin/env python3
"""One exact unobserved MOVE fusion on the pinned PR7603 word.

Hao Yan (@FanPUYen), with substantial OpenAI Codex assistance. Apache-2.0.
Preserves SYLforge's two contractions, DreamingOfClouds' token settlement, and all credited predecessor work.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE / 'retained/two-contractions/word.json.gz'
BASE_SHA = 'b3b991e9fc8d9eb684d2ee80ca477a04ad72106d6eee3f41f7b2284800c25d22'
FIRST, SECOND = 42077, 42156
CLAIM = '0.0036502223357'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def build_word():
    raw = BASE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == BASE_SHA, 'PR7603 source hash')
    word = json.loads(gzip.decompress(raw))
    program = word['program']
    require(program[FIRST] == ['MOVE', 315, 729, 789, False], 'first source event')
    require(program[SECOND] == ['MOVE', 315, 789, 808, False], 'second source event')
    require(program[SECOND + 2] == ['ADD', 315, 331, '1', 808], 'first subsequent contact')
    known = {'MOVE', 'ADD', 'COPY', 'SCALE', 'INIT', 'CLEAR'}
    for i in range(FIRST + 1, SECOND):
        event = program[i]
        require(event[0] in known, 'unknown opcode in no-access interval')
        used = event[1:3] if event[0] in {'ADD', 'COPY'} else event[1:2]
        require(315 not in used, 'intervening access at ' + str(i))
    require([len(word['frames'][f]) for f in (729, 789, 808)] == [4, 5, 6], 'frame dimensions')
    word['program'] = [(['MOVE', 315, 729, 808, False] if i == SECOND else event)
                       for i, event in enumerate(program) if i != FIRST]
    return word


def invoice():
    original = json.loads((HERE / 'data/invoice-7603.json').read_bytes())
    receipt = json.loads((HERE / 'retained/two-contractions/receipt.json').read_bytes())
    require(original['paid'] == receipt['complete_invoice']['P'] and original['targets'] == receipt['complete_invoice']['T'], 'source complete7603 invoice')
    result = copy.deepcopy(original)
    for rank, delta in [('1', -34), ('2', 17)]:
        result['paid'][rank] += delta
        require(result['paid'][rank] >= 0, 'negative paid count')
    require(sum(result['paid'].values()) == 110383, 'complete paid positions')
    require(sum(result['targets'].values()) == 22461, 'complete target positions')
    mass = lambda h: sum(int(r) * n for r, n in h.items())
    require(mass(result['targets']) - mass(result['paid']) == 1424, 'rank surplus')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    word, price = build_word(), invoice()
    data = HERE / 'data'
    if args.write:
        data.mkdir(exist_ok=True)
        raw = json.dumps(word, separators=(',', ':')).encode('utf-8')
        (data / 'word.json.gz').write_bytes(gzip.compress(raw, mtime=0))
        (data / 'invoice-new.json').write_text(json.dumps(price, indent=2) + '\n', encoding='utf-8')
    require(json.loads(gzip.decompress((data / 'word.json.gz').read_bytes())) == word,
            'committed word differs from exact construction')
    require(json.loads((data / 'invoice-new.json').read_bytes()) == price,
            'committed invoice differs from exact construction')
    print(json.dumps({'status': 'PASS_ROLE315_CONSTRUCTION', 'events': len(word['program']),
                      'claim': CLAIM, 'native_paid_delta': {'1': -2, '2': 1},
                      'complete_paid_delta': {'1': -34, '2': 17},
                      'public_fields': word['public'], 'owned_fields': word['owned_fields'],
                      'unobserved_events': SECOND - FIRST - 1}, indent=2))


if __name__ == '__main__':
    main()

"""Check the nine-relation BIT supplier and its complete conditional cost.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import sys

sys.dont_write_bytecode = True
import local as L
import price as P


def authenticate():
    count = 0
    for row in json.loads((L.HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input':
            continue
        raw = (L.ROOT/row['path']).read_bytes()
        L.need(sha256(raw).hexdigest() == row['sha256'], 'Changed source: '+row['path'])
        L.need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'],
               'Changed source Git object: '+row['path'])
        count += 1
    return count


def columns(program, pivots):
    owned = set(pivots) | {L.SIZE}
    for column in range(L.SIZE+1):
        state = bytearray(L.SIZE+1)
        state[column] = 1
        for event in program:
            op = event[0]
            if op == 'CLEAR':
                state[event[1]] = 0
            elif op == 'ADD':
                state[event[1]] ^= state[event[2]]
            elif op == 'ZERO_MOVE':
                L.need(state[event[1]] == 0, 'Separate column replay: zero transport')
            else:
                L.need(op == 'MOVE', 'Separate column replay: known operation')
        expected = bytearray(L.SIZE+1)
        if column not in owned:
            expected[column] = 1
            if column < L.PORTS:
                expected[column+L.PORTS] = 1
        L.need(state == expected, 'Separate Boolean replay of every retained and owned column')
    return {'columns': L.SIZE+1, 'method':'One Boolean input at a time; bytearray state; no symbolic row algebra'}


def run():
    pins = authenticate()
    local, program = L.run()
    column_check = columns(program, map(int, local['relation_basis']))
    price = P.run(local)
    result = {'status':'PASS_BIT_NINE_OWNED_RELATIONS_00344412_NO_NEW_MULTIPLICATION_KAPPA',
              'source_inputs_authenticated':pins, 'local':local, 'separate_columns':column_check,
              'complete_cost':price,
              'limits':['The complex supplier still limits the complete multiplication bound.',
                        'Native all-column, owned-erasure, compiler, precision/tape and analytic recovery premises remain conditional.',
                        'The full GL cover, winning uniform word and complete integer multiplier are not materialized.',
                        'No Lean or proof-kernel check is included.']}
    artifact = {'schema':'bit-nine-owned-relations/1', 'source_word_sha256':L.sha256((L.SOURCE/'WORD.json.gz').read_bytes()).hexdigest(),
                'owned':sorted([int(p) for p in local['relation_basis']]+[L.SIZE]),
                'program':program}
    return P.encode(result), artifact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result, artifact = run()
    if args.write:
        (L.HERE/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
        (L.HERE/'WORD.json.gz').write_bytes(gzip.compress(json.dumps(artifact, separators=(',',':')).encode(), mtime=0))
    else:
        L.need(json.loads((L.HERE/'RESULT.json').read_text()) == result, 'Frozen complete result')
        L.need(json.loads(gzip.decompress((L.HERE/'WORD.json.gz').read_bytes())) == artifact, 'Frozen emitted word payload')
    print(result['status'])
    print(json.dumps({'retained_inputs':result['local']['retained_inputs'],
                      'owned_entries':result['local']['arbitrary_owned_entries'],
                      'paid_calls':result['complete_cost']['paid_count'],
                      'productive_fields':result['complete_cost']['target_count'],
                      'ordinary_BIT':result['complete_cost']['ordinary_BIT']}, sort_keys=True))


if __name__ == '__main__':
    main()

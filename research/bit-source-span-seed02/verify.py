#!/usr/bin/env python3
"""Independent finite source-mask exclusion checker; standard library only.

Set-valued symbolic responses, rational nullspaces and direct parity witnesses.
No generator/predecessor checker is imported. Hanson Sun with substantial
OpenAI Codex assistance. Apache-2.0; not independent human or Lean review.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction
import gzip
import hashlib
import json
from math import lcm
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
SHA256 = 'e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f'
SUMMARY = dict(helpers=439, retained_helpers=9, screened_helpers=430,
               rational_frames=636, reads=2102,
               all_source_span_pass_reads=2037, all_source_span_fail_reads=65,
               frame_span_pass_reads=90, frame_span_fail_reads=2012,
               clean_span_blocked_helpers=65, frame_span_blocked_helpers=364,
               necessary_condition_survivors=1)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key: ' + key)
            result[key] = value
        return result

    def constant(value):
        raise ValueError('nonfinite JSON constant: ' + value)

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def normal_vectors(vectors, dimension):
    """Full rational RREF; return an integer basis of the orthogonal space."""
    matrix = [list(map(Fraction, row)) for row in vectors]
    pivot_columns, row = [], 0
    for column in range(dimension):
        pivot = next((i for i in range(row, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        factor = matrix[row][column]
        matrix[row] = [x/factor for x in matrix[row]]
        for i in range(len(matrix)):
            if i != row and matrix[i][column]:
                factor = matrix[i][column]
                matrix[i] = [a-factor*b for a, b in zip(matrix[i], matrix[row])]
        pivot_columns.append(column)
        row += 1
    normals = []
    for free in set(range(dimension)) - set(pivot_columns):
        vector = [Fraction(0)] * dimension
        vector[free] = Fraction(1)
        for i, pivot in enumerate(pivot_columns):
            vector[pivot] = -matrix[i][free]
        denominator = lcm(*(x.denominator for x in vector))
        normals.append(tuple(int(x*denominator) for x in vector))
    return normals


def rational_closures(word):
    closures = []
    for frame in word['frames']:
        normals = normal_vectors([word['lines'][i] for i in frame], word['h'])
        closure = frozenset(i for i, line in enumerate(word['lines'])
                            if all(sum(a*b for a, b in zip(line, normal)) == 0
                                   for normal in normals))
        require(closure == frozenset(frame), 'nonclosed rational frame')
        closures.append(closure)
    return closures


def spans(vectors, target):
    echelon = {}
    for vector in vectors:
        row = set(vector)
        while row:
            pivot = min(row)
            if pivot not in echelon:
                echelon[pivot] = frozenset(row)
                break
            row.symmetric_difference_update(echelon[pivot])
    residual = set(target)
    while residual:
        pivot = min(residual)
        if pivot not in echelon:
            return False
        residual.symmetric_difference_update(echelon[pivot])
    return True


def response_trace(word):
    v, n = word['v'], 2*word['v']+word['R']
    values = [frozenset([i]) if i < v else frozenset() for i in range(n)]
    helpers = set(range(2*v, n)) - set(word['ret'])
    frames = word['start'][:]
    touches = [[(-1, frame)] for frame in frames]
    incidents = {q: set() for q in helpers}
    reads = {q: [] for q in helpers}
    clock = 0
    for phase in ['A', 'B']:
        if phase == 'B':
            # All immutable COPY boundaries occupy one independent time step.
            for q in word['ret']:
                touches[q].append((clock, frames[q]))
            for target, slots in enumerate(word['scatter']):
                for slot in slots:
                    values[v+target] = values[v+target] ^ values[word['ret'][slot]]
            clock += 1
        for index, (frame, dest, operands) in enumerate(word[phase]):
            for register in [dest] + operands:
                touches[register].append((clock, frame))
                frames[register] = frame
                if register in helpers:
                    incidents[register].add(clock)
            for q in helpers.intersection(operands):
                wanted = values[q]
                for s in operands:
                    if s < v:
                        wanted = wanted ^ values[s]
                reads[q].append(dict(clock=clock, section=phase, index=index,
                                     destination=dest, target=wanted,
                                     source_rows=tuple(values[:v])))
            update = frozenset()
            for s in operands:
                update = update ^ values[s]
            values[dest] = values[dest] ^ update
            clock += 1
    for register, final in enumerate(word['final']):
        touches[register].append((clock, final))
    return reads, touches, incidents


def analyze(word):
    closures = rational_closures(word)
    reads, touches, incidents = response_trace(word)
    v = word['v']
    summary = Counter()
    for q, queries in reads.items():
        clean_fail = frame_fail = False
        fixed = [[item for item in register if item[0] not in incidents[q]]
                 for register in touches]
        for query in queries:
            def bracket(register):
                prior = [f for time, f in fixed[register] if time < query['clock']]
                later = [f for time, f in fixed[register] if time > query['clock']]
                require(prior and later, 'missing frame anchor')
                return prior[-1], later[0]

            dest = query['destination']
            low, high = bracket(dest)
            eligible = []
            for source in range(v):
                if source == dest:
                    continue
                before, after = bracket(source)
                if closures[low] <= closures[after] and closures[before] <= closures[high]:
                    eligible.append(source)
            source_rows, target = query['source_rows'], query['target']
            clean = spans([r for s, r in enumerate(source_rows) if s != dest], target)
            geometry = spans([source_rows[s] for s in eligible], target)
            query.update(eligible_sources=eligible, clean=clean, geometry=geometry,
                         bounds={r: bracket(r) for r in [dest] + eligible})
            summary['reads'] += 1
            summary['all_source_span_pass_reads' if clean else 'all_source_span_fail_reads'] += 1
            summary['frame_span_pass_reads' if geometry else 'frame_span_fail_reads'] += 1
            clean_fail |= not clean
            frame_fail |= not geometry
        summary['clean_span_blocked_helpers' if clean_fail else
                'frame_span_blocked_helpers' if frame_fail else
                'necessary_condition_survivors'] += 1
    summary.update(helpers=word['R'], retained_helpers=len(word['ret']),
                   screened_helpers=len(reads), rational_frames=len(closures))
    return dict(summary=dict(summary), reads=reads, closures=closures)


def indices(value, width, label):
    require(isinstance(value, list) and all(type(x) is int and 0 <= x < width for x in value)
            and value == sorted(set(value)), 'invalid ' + label)
    return frozenset(value)


def check_certificate(analysis, certificate):
    require(certificate['schema_version'] == 1 and certificate['assignment_seed'] == 2,
            'certificate identity')
    require(certificate['source'] == SOURCE and certificate['source_sha256'] == SHA256,
            'certificate source identity')
    require(analysis['summary'] == SUMMARY, 'independent census differs from recorded result')
    require(certificate['summary'] == analysis['summary'], 'certificate census coverage')
    excluded = certificate['exclusions']
    survivors = certificate['survivors']
    ids = [item['helper'] for item in excluded] + [item['helper'] for item in survivors]
    require(len(ids) == len(set(ids)) and set(ids) == set(analysis['reads']),
            'helper partition incomplete or duplicated')
    require([r['helper'] for r in survivors] == [470], 'survivor inventory')
    for record in excluded:
        q = record['helper']
        queries = analysis['reads'][q]
        query = next((r for r in queries if (r['section'], r['index']) ==
                      (record['section'], record['index'])), None)
        require(query is not None, 'exclusion read missing')
        require(record['destination'] == query['destination'] and
                record['target'] == sorted(query['target']) and
                record['eligible_sources'] == query['eligible_sources'], 'exclusion boundary data')
        kind = 'clean-span' if any(not r['clean'] for r in queries) else 'frame-span'
        require(record['kind'] == kind and not query['geometry'], 'exclusion classification')
        if kind == 'clean-span':
            require(not query['clean'], 'false unrestricted exclusion')
            donors = [s for s in range(111) if s != query['destination']]
        else:
            require(query['clean'], 'false frame-only classification')
            donors = query['eligible_sources']
        dual = indices(record['dual'], 111, 'dual')
        require(len(dual & query['target']) % 2 == 1, 'dual does not separate target')
        require(all(len(dual & query['source_rows'][s]) % 2 == 0 for s in donors),
                'dual does not annihilate source span')
    for survivor in survivors:
        queries = analysis['reads'][survivor['helper']]
        records = survivor['reads']
        require(len(records) == len(queries), 'survivor read coverage')
        for record, query in zip(records, queries):
            require(query['geometry'] and record['helper'] == survivor['helper'] and
                    record['section'] == query['section'] and record['index'] == query['index'] and
                    record['destination'] == query['destination'] and
                    record['target'] == sorted(query['target']) and
                    record['eligible_sources'] == query['eligible_sources'], 'survivor boundary')
            donors = indices(record['source_mask'], 111, 'source mask')
            require(donors <= set(query['eligible_sources']), 'ineligible source donor')
            result = frozenset()
            for source in donors:
                result = result ^ query['source_rows'][source]
            require(result == query['target'], 'source-mask response mismatch')


def controls(analysis, certificate):
    count = 0

    def reject(change, reason):
        nonlocal count
        changed = copy.deepcopy(certificate)
        change(changed)
        try:
            check_certificate(analysis, changed)
        except ValueError as error:
            require(reason in str(error), 'control rejected for wrong reason: ' + str(error))
            count += 1
        else:
            raise ValueError('mutation accepted: ' + reason)

    reject(lambda c: c['exclusions'][0].update(dual=[]), 'dual does not separate target')
    reject(lambda c: c['exclusions'][0].update(target=[]), 'exclusion boundary data')
    reject(lambda c: c['exclusions'][0].update(eligible_sources=[110]), 'exclusion boundary data')
    reject(lambda c: c['exclusions'][0].update(index=-1), 'exclusion read missing')
    reject(lambda c: c['exclusions'].pop(), 'helper partition')
    reject(lambda c: c['exclusions'].append(c['exclusions'][0]), 'helper partition')
    reject(lambda c: c['summary'].update(reads=2101), 'census coverage')
    reject(lambda c: c['survivors'][0]['reads'][0].update(source_mask=[]),
           'source-mask response mismatch')
    reject(lambda c: c['survivors'][0].update(reads=[]), 'survivor read coverage')
    reject(lambda c: c.update(source_sha256='0'*64), 'source identity')
    # Keep the target pairing odd while making a donor pairing odd too.
    # This exercises annihilation, separately from the zero-dual control.
    corrupted = False
    for index, record in enumerate(certificate['exclusions']):
        query = next(r for r in analysis['reads'][record['helper']]
                     if (r['section'], r['index']) == (record['section'], record['index']))
        donors = (query['eligible_sources'] if record['kind'] == 'frame-span' else
                  [s for s in range(111) if s != query['destination']])
        coordinate = next((i for i in range(111) if i not in query['target'] and
                           any(i in query['source_rows'][s] for s in donors)), None)
        if coordinate is not None:
            dual = sorted(set(record['dual']) ^ {coordinate})
            reject(lambda c: c['exclusions'][index].update(dual=dual),
                   'dual does not annihilate source span')
            corrupted = True
            break
    require(corrupted, 'missing non-annihilating dual control')

    # The new multi-source class is exercised, rather than just single donors.
    require(not spans([{0}, {1}], {0, 2}), 'outside-span control')
    require(spans([{0}, {1}], {0, 1}), 'two-source positive control')
    require(spans([{0}, {1}, {2}], {0, 1, 2}), 'three-source positive control')
    require(spans([{0}, {1}, {0, 1}], set()), 'dependent/empty mask positive control')
    # Rational spans must not be computed modulo two.
    require(normal_vectors([[1, 1], [1, -1]], 2) == [], 'rational rank control')
    require(normal_vectors([[1, 1]], 2), 'proper subspace control')
    # Existing helper470's read has a legal frame186; its old frame79 is too low.
    query = analysis['reads'][470][0]
    require((query['section'], query['index'], query['destination']) == ('A', 1993, 444),
            'known boundary positive control')
    closure = analysis['closures']
    for register in [444, 77]:
        low, high = query['bounds'][register]
        require(closure[low] <= closure[186] <= closure[high], 'known legal frame186')
    require(not closure[query['bounds'][77][0]] <= closure[79],
            'late source access at frame79 must fail')
    return count


def load_source(root=ROOT):
    pins = strict_json((HERE / 'SOURCES.json').read_text())
    inputs = [p for p in pins['files'] if p['usage'] == 'input']
    require(len(inputs) == 1 and inputs[0]['path'] == SOURCE and inputs[0]['sha256'] == SHA256,
            'input pin inventory')
    payload = (root / SOURCE).read_bytes()
    require(hashlib.sha256(payload).hexdigest() == SHA256, 'source hash mismatch')
    return strict_json(gzip.decompress(payload).decode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, default=HERE / 'CERTIFICATE.json')
    args = parser.parse_args()
    analysis = analyze(load_source())
    certificate = strict_json(args.certificate.read_text())
    check_certificate(analysis, certificate)
    count = controls(analysis, certificate)
    print('PASS_SOURCE_SPAN_INDEPENDENT helpers=430 clean_blocked=65 frame_blocked=364 '
          f'survivor=470 reads=2102 exclusion_witnesses=429 controls={count} no_new_kappa')


if __name__ == '__main__':
    main()

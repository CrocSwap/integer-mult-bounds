"""Complete integer-copy compiler counts using a historical independent flow model.

Source-aware adaptation of B12S9 weighted ordered words. Neither actual Flow
nor compile_counts nor the current peer model is imported or executed.
"""
import argparse
import hashlib
from itertools import product
import json
from math import gcd
from pathlib import Path
import re
import sys

META_SHA256 = {
    'CASES.json': 'ce0152497423d200f0e2c8b83b9efce992c95c92743e238cd5a060306bf329a0',
    'SOURCE-PINS.json': 'f2031ec3b25d187bd924037b63e46943c4d19ece39175e2c58327d7a4f0e59ed',
}
BYTE_CAP = 16 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def positive_integer(value, label):
    require(type(value) is int and value > 0, 'positive integer ' + label)
    return value


def inventory_pairs(value, label):
    if type(value) is dict:
        pairs = [(int(rank), count) for rank, count in value.items()]
    else:
        require(type(value) is list, 'inventory list: ' + label)
        pairs = value
    result = {}
    for pair in pairs:
        require(type(pair) in (tuple, list) and len(pair) == 2, 'inventory pair')
        rank = positive_integer(pair[0], label + ' rank')
        count = positive_integer(pair[1], label + ' count')
        require(rank not in result, 'duplicate inventory rank')
        result[rank] = count
    require(result, 'nonempty inventory: ' + label)
    return result


def increment(histogram, rank, count):
    valid_key = type(rank) is int or (type(rank) is tuple and
                                     all(type(value) is int and value >= 0 for value in rank))
    require(valid_key and type(count) is int and count >= 0,
            'integer histogram contribution')
    if count:
        histogram[rank] = histogram.get(rank, 0) + count


def histogram_rows(histogram):
    return [[rank, histogram[rank]] for rank in sorted(histogram) if histogram[rank] > 0]


class OrderedWords:
    """Count multiplicity-weighted support words; no comb/factorial formula."""
    def __init__(self, targets, paid, n):
        self.targets, self.paid = targets, paid
        self.keys, self.pkeys = tuple(sorted(targets)), tuple(sorted(paid))
        self.indices = {rank: index for index, rank in enumerate(self.keys)}
        self.n = positive_integer(n, 'parent')
        self.maximum, minimum = max(self.keys), min(self.keys)
        require(minimum >= 2 and max(self.pkeys) < self.maximum <= n, 'flow rank domain')
        self.cap, self.height = n // self.maximum, 0
        least = 1
        while least * minimum <= self.cap:
            self.height += 1
            least *= minimum
        self.columns, self.batch_cache, self.request_cache = {}, {}, {}

    def target_word(self, word):
        counts = [0] * len(self.keys)
        column, weight = 1, 1
        for rank in word:
            counts[self.indices[rank]] += 1
            column *= rank
            weight *= self.targets[rank]
        key = tuple(counts)
        require(key not in self.columns or self.columns[key] == column,
                'word column consistency')
        self.columns[key] = column
        return key, column, weight

    def batch(self, degree, scale):
        cache_key = degree, scale
        if cache_key not in self.batch_cache:
            result = {}
            for word in product(self.keys, repeat=degree):
                key, column, weight = self.target_word(word)
                if scale * column <= self.cap:
                    increment(result, key, weight)
            self.batch_cache[cache_key] = result
        return self.batch_cache[cache_key]

    def requests(self, prefix_degree, scale):
        """An ordered unit-prefix word followed by one unrestricted target."""
        cache_key = prefix_degree, scale
        if cache_key not in self.request_cache:
            result = {}
            for word in product(self.keys, repeat=prefix_degree + 1):
                key, column, weight = self.target_word(word)
                prefix_column = column // word[-1]
                if scale * prefix_column <= self.cap:
                    increment(result, key, weight)
            self.request_cache[cache_key] = result
        return self.request_cache[cache_key]

    def paid_paths(self, degree):
        for word in product(self.pkeys, repeat=degree):
            scale, weight = 1, 1
            for rank in word:
                scale *= rank
                weight *= self.paid[rank]
            yield scale, weight

    def process_edge(self, batch, degree, child_scale, copies, sources, exits, boundary):
        child = self.requests(degree - 1, child_scale)
        matched = 0
        for key in set(batch) | set(child):
            supplied, wanted = batch.get(key, 0), child.get(key, 0)
            rank = child_scale * self.columns[key]
            paired = min(supplied, wanted)
            matched += copies * paired
            if supplied > wanted:
                count = copies * (supplied - wanted)
                increment(exits, rank, count)
                increment(boundary, rank, count)
            elif wanted > supplied:
                require(supplied == 0, 'word Pascal inequality')
                increment(sources, rank, copies * (wanted - supplied))
        return matched

    def flow(self):
        sources, exits, boundary = {}, {}, {}
        for key, count in self.requests(self.height, 1).items():
            increment(sources, self.columns[key], count)
        units = columns = matched = 0
        for depth in range(self.height + 1):
            degree = self.height - depth
            for scale, path_weight in self.paid_paths(depth):
                if scale > self.cap:
                    continue
                batch = self.batch(degree, scale)
                units += path_weight * sum(batch.values())
                columns += path_weight * sum(count * scale * self.columns[key]
                                             for key, count in batch.items())
                for rank in self.pkeys:
                    child_scale, copies = scale * rank, path_weight * self.paid[rank]
                    if degree == 0:
                        for key, count in batch.items():
                            increment(exits, child_scale * self.columns[key], copies * count)
                    else:
                        matched += self.process_edge(batch, degree, child_scale, copies,
                                                     sources, exits, boundary)
        return self.finish(sources, exits, boundary, units, columns, matched)

    def finish(self, sources, exits, boundary, units, columns, matched):
        require(sources and all(1 <= s <= self.n and self.n < self.maximum * s
                               for s in sources), 'source support')
        require(all(1 <= e < self.n and self.maximum * e <= max(self.pkeys) * self.n
                    for e in exits), 'exit support')
        require(all(self.maximum * e > min(self.keys) * self.n for e in boundary),
                'boundary support')
        surplus = sum(k * count for k, count in self.targets.items())
        surplus -= sum(k * count for k, count in self.paid.items())
        source_mass = sum(k * count for k, count in sources.items())
        exit_mass = sum(k * count for k, count in exits.items())
        require(source_mass - exit_mass == surplus * columns, 'word-flow conservation')
        W, P = sum(self.targets.values()), sum(self.paid.values())
        upper = sum(P ** d * W ** (self.height - d) for d in range(self.height + 1))
        source_count = sum(sources.values())
        require(units <= upper and source_count <= W * units, 'complete count bounds')
        mirror = dict(exits)
        for rank, count in sources.items():
            increment(mirror, self.n - rank, count)
        require(self.n * source_count - sum(k * v for k, v in mirror.items())
                == surplus * columns, 'mirror conservation')
        return {'n': self.n, 'height': self.height, 'sources': histogram_rows(sources),
                'exits': histogram_rows(exits), 'boundary_exits': histogram_rows(boundary),
                'units': units, 'column_mass': columns, 'source_count': source_count,
                'matched_jobs': matched, 'minimum_source': min(sources),
                'all_sources_above_n_over_m': all(self.n < self.maximum * s for s in sources),
                'rank_one_surplus': surplus, 'unit_count_upper': upper,
                'mirror': histogram_rows(mirror)}


def bigint_record(value):
    require(type(value) is int and value >= 0, 'nonnegative bigint')
    bits = value.bit_length()
    raw = value.to_bytes((bits + 7) // 8, 'big')
    return {'bits': bits, 'unsigned_big_endian_sha256': hashlib.sha256(raw).hexdigest()}


def rational_text(numerator, denominator):
    divisor = gcd(numerator, denominator)
    top, bottom = numerator // divisor, denominator // divisor
    return str(top) if bottom == 1 else str(top) + '/' + str(bottom)


def outward_ratio(numerator, denominator):
    scale = 10 ** 18
    lower = numerator * scale // denominator
    return {'lower': rational_text(lower, scale),
            'upper': rational_text(lower + 1, scale)}


def compile_case(case):
    targets = inventory_pairs(case['targets'], 'targets')
    paid = inventory_pairs(case['paid'], 'paid')
    N = positive_integer(case['maximum'], 'maximum')
    m, W, P = max(targets), sum(targets.values()), sum(paid.values())
    require(N >= m and min(targets) >= 2 and max(paid) < m, 'compiler domain')
    delta = sum(k * v for k, v in targets.items()) - sum(k * v for k, v in paid.items())
    require(delta > 0, 'positive surplus')
    vectors = {'widths': [1] * (N + 1), 'leaves': [n if n < m else 0 for n in range(N + 1)],
               'units': [0] * (N + 1), 'columns': [0] * (N + 1), 'slots': [0] * (N + 1)}
    largest, last_flow = 1, None
    for n in range(m, N + 1):
        f = OrderedWords(targets, paid, n).flow()
        a = vectors['widths'][n - 1]
        vectors['widths'][n] = a * f['source_count']
        local_slots = 2 * (W + P) * f['units'] - 2 * f['matched_jobs']
        require(local_slots == f['source_count'] + sum(v for k, v in f['exits'])
                + (W + P) * f['units'], 'complete local slot identity')
        local = {'leaves': 0, 'units': a * f['units'], 'columns': a * f['column_mass'],
                 'slots': a * local_slots}
        for rank, count in f['mirror']:
            require(0 <= rank < n and a % vectors['widths'][rank] == 0,
                    'integer lower-rank child batch')
            copies = count * (a // vectors['widths'][rank])
            for field in local:
                local[field] += copies * vectors[field][rank]
        for field, value in local.items():
            vectors[field][n] = value
        require(vectors['widths'][n] % a == 0, 'nested width divisibility')
        require(vectors['widths'][n] * n - local['leaves'] == delta * local['columns'],
                'expanded rank-one identity')
        require(local['units'] <= local['columns'] <= vectors['widths'][n] * n // delta,
                'expanded unit/column bound')
        require(local['slots'] <= 2 * (W + P) * local['units'], 'expanded slot bound')
        largest, last_flow = max(largest, f['source_count']), f
    envelope = W * (W + P + 1) ** (last_flow['height'] + 1)
    require(largest <= envelope and vectors['widths'][N] <= envelope ** N,
            'source width envelope')
    summary = summary_row(N, vectors, delta, envelope, N - m + 1)
    encoded = {name: [format(value, 'x') for value in array]
               for name, array in vectors.items()}
    return {'name': case['name'], 'maximum': N, 'vectors': encoded, 'summary': summary}


def summary_row(N, vectors, delta, envelope, checks):
    fields = {'productive_width': 'widths', 'paid_rank_one_leaves': 'leaves',
              'raw_instances': 'units', 'column_mass': 'columns', 'routing_slots': 'slots'}
    result = {'n': N}
    for public, internal in fields.items():
        result[public] = bigint_record(vectors[internal][N])
    B, leaves = vectors['widths'][N], vectors['leaves'][N]
    result.update({'leaves_per_array': outward_ratio(leaves, B),
                   'width_exponent_envelope': envelope.bit_length() * N,
                   'source_count_upper': envelope, 'rank_one_surplus': delta,
                   'paid_above_99_percent_linear': leaves > 99 * B * N // 100,
                   'nested_batch_checks': checks})
    return result


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True) + '\n').encode('ascii')


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def forbidden_number(token):
    raise ValueError('float/nonfinite JSON token: ' + token)


def strict_json(data):
    require(len(data) <= BYTE_CAP, 'JSON byte cap')
    return json.loads(data, object_pairs_hook=unique_keys,
                      parse_float=forbidden_number, parse_constant=forbidden_number)


def read_raw(path, cap=BYTE_CAP):
    with path.open('rb') as stream:
        data = stream.read(cap + 1)
    require(len(data) <= cap, 'raw input byte cap')
    return data


def authenticate(base):
    metadata = {}
    for filename, sha in META_SHA256.items():
        data = read_raw(base / filename)
        require(hashlib.sha256(data).hexdigest() == sha, 'metadata byte drift: ' + filename)
        metadata[filename] = strict_json(data)
    rows = metadata['SOURCE-PINS.json']['objects']
    require(type(rows) is list and len(rows) == 6, 'six source inputs')
    source_data = {}
    for row in rows:
        name, size = row['local_path'], row['bytes']
        require(type(name) is str and not Path(name).is_absolute()
                and '..' not in Path(name).parts and name not in source_data, 'source path')
        require(type(size) is int and size >= 0, 'source size type')
        data = read_raw(base / name, size)
        blob = b'blob ' + str(len(data)).encode('ascii') + b'\0' + data
        require(len(data) == size and hashlib.sha256(data).hexdigest() == row['sha256']
                and hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source byte drift: ' + name)
        source_data[name] = data
    cases = metadata['CASES.json']
    require(cases['schema'] == 'direct-compiler-counts-cases/1', 'case schema')
    raw = strict_json(source_data['inputs/p7-RESULT.json.txt'])['strictification']
    for case in cases['cases']:
        if case['name'] == 'raw-p7':
            require(inventory_pairs(case['targets'], 'case targets') ==
                    inventory_pairs(raw['targets'], 'raw targets'), 'raw target binding')
            require(inventory_pairs(case['paid'], 'case paid') ==
                    inventory_pairs(raw['paid'], 'raw paid'), 'raw paid binding')
    return cases


def build_packet(cases):
    require(type(cases['cases']) is list and len(cases['cases']) == 4, 'four cases')
    names = [case['name'] for case in cases['cases']]
    require(all(type(name) is str for name in names) and len(set(names)) == len(names),
            'unique ordered case names')
    return {'schema': 'direct-compiler-counts-audit/1',
            'cases': [compile_case(case) for case in cases['cases']]}


def same_types(actual, expected):
    require(type(actual) is type(expected), 'strict reference type')
    if type(expected) is dict:
        require(set(actual) == set(expected), 'reference exact keys')
        for key in expected:
            same_types(actual[key], expected[key])
    elif type(expected) is list:
        require(len(actual) == len(expected), 'reference list length/order')
        for left, right in zip(actual, expected):
            same_types(left, right)


def reference_shape(value, cases):
    require(value['schema'] == 'direct-compiler-counts-audit/1', 'reference schema')
    require(len(value['cases']) == len(cases['cases']), 'reference case count')
    for row, case in zip(value['cases'], cases['cases']):
        require(row['name'] == case['name'] and type(row['maximum']) is int
                and row['maximum'] == case['maximum'], 'reference case order')
        for vector in row['vectors'].values():
            require(len(vector) == case['maximum'] + 1, 'full rank vector')
            for text in vector:
                require(type(text) is str and re.fullmatch(r'0|[1-9a-f][0-9a-f]*', text),
                        'canonical lowercase integer hex')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--emit', action='store_true')
    selection.add_argument('--reference', type=Path)
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    cases = authenticate(base)
    packet = build_packet(cases)
    encoded = canonical(packet)
    require(len(encoded) <= BYTE_CAP, 'output packet byte cap')
    if args.emit:
        sys.stdout.buffer.write(encoded)
    else:
        raw = read_raw(args.reference or base / 'CERTIFICATE.json')
        incoming = strict_json(raw)
        same_types(incoming, packet)
        reference_shape(incoming, cases)
        require(raw == encoded, 'complete regenerated packet mismatch')
        print('PASS_PRIMARY_COMPLETE_COMPILER', hashlib.sha256(encoded).hexdigest(), len(encoded))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, IndexError, UnicodeError) as error:
        print('FAIL_PRIMARY_COMPLETE_COMPILER', str(error), file=sys.stderr)
        sys.exit(1)

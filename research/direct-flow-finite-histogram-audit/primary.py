"""Weighted ordered-word finite-flow model, independent of source Flow code.

Pure build_cases API. Authentication/CLI wiring is supplied by the coordinator
before first seals; this model never imports or executes the source Flow.
"""
from itertools import product


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


def build_cases(contract, raw_inventory):
    require(type(contract) is dict and type(contract.get('cases')) is list,
            'case contract')
    require(type(raw_inventory) is dict, 'full raw inventory JSON')
    result = {}
    for case in contract['cases']:
        name = case['id']
        require(type(name) is str and name not in result, 'unique case id')
        if case.get('inventory') == 'raw_p7':
            inventory = raw_inventory['strictification']
            targets = inventory_pairs(inventory['targets'], 'raw targets')
            paid = inventory_pairs(inventory['paid'], 'raw paid')
        else:
            targets = inventory_pairs(case['targets'], 'toy targets')
            paid = inventory_pairs(case['paid'], 'toy paid')
        value = OrderedWords(targets, paid, case['n']).flow()
        require(set(value) == set(contract['fields']), 'whole-case field set')
        result[name] = value
    return result


# Shared coordinator-authored byte/CLI wrapper; not an independent math model.
def _run_cli():
    import argparse
    import hashlib
    import json
    from pathlib import Path
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description='Complete finite flow certificate')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--emit', type=Path)
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    contract_raw = (base / 'CONTRACT.json').read_bytes()
    if hashlib.sha256(contract_raw).hexdigest() != '4fc49527e728be80abaa4c5f7f0bd62da30afaea70b71be2c77b8457136da1f1':
        raise ValueError('contract byte drift')
    pins_raw = (base / 'SOURCE-PINS.json').read_bytes()
    if hashlib.sha256(pins_raw).hexdigest() != 'a533c5c9513470c2294c3b6217caf052eca63ce568a075d35e5f6c2251358812':
        raise ValueError('source manifest byte drift')
    for row in json.loads(pins_raw)['objects']:
        data = (base / row['local_path']).read_bytes()
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256'] or blob != row['git_blob']:
            raise ValueError('source byte drift: '+row['local_path'])
    # These fixed mathematical inputs cannot be replaced by changing pin metadata.
    if hashlib.sha256((base/'inputs/flow.py.txt').read_bytes()).hexdigest() != '460f0b0262d7b6880973f46240b3fff1e9f04601fa1d658dda18688b1e26575a':
        raise ValueError('canonical flow drift')
    raw = (base/'inputs/p7-RESULT.json.txt').read_bytes()
    if hashlib.sha256(raw).hexdigest() != '9b814be97e3b45fcc28eafa8a65694897a7387f71a14d44796c6aadf303d7fab':
        raise ValueError('raw inventory drift')
    contract, inventory = json.loads(contract_raw), json.loads(raw)
    if 'build_packet' in globals():
        packet = build_packet(contract, inventory)
    else:
        packet = {'schema': contract['schema'], 'cases': build_cases(contract, inventory)}
    encoded = json.dumps(packet, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')+b'\n'
    if args.emit is not None:
        if args.emit.exists():
            raise ValueError('refusing to replace first packet')
        args.emit.write_bytes(encoded)
    else:
        reference = base / globals().get('REFERENCE_FILE', 'FIRST.json')
        if encoded != reference.read_bytes():
            raise ValueError('complete packet mismatch')
    print('PASS_COMPLETE_FINITE_FLOW', hashlib.sha256(encoded).hexdigest(), len(encoded))


if __name__ == '__main__':
    try:
        _run_cli()
    except (ValueError, OSError) as error:
        import sys
        print('FAIL_COMPLETE_FINITE_FLOW', error, file=sys.stderr)
        raise SystemExit(1)

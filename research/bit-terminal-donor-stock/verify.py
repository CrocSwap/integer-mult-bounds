"""Census of 523 unchanged-geometry BIT terminal donor ports."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
from time import monotonic


NATIVE = 'research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz'
INVOICE = 'research/paired-query-only-bit/EFREE-RESULT.json'


def import_file(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_pinned(root):
    pins = {}
    for line in Path(__file__).with_name('SOURCES.tsv').read_text().splitlines():
        name, digest, _ = line.split('\t')
        if name in pins:
            raise ValueError(f'duplicate dependency path: {name}')
        pins[name] = digest
    result = {}
    for path, digest in pins.items():
        blob = (root/path).read_bytes()
        if sha256(blob).hexdigest() != digest:
            raise ValueError(f'SHA-256 mismatch: {path}')
        result[path] = blob
    return pins, result


def timeline(w, deadline):
    n = w['public']
    frames = w['start'] + [None]*w['owned_fields']
    rows = [1 << i for i in range(n)] + [0]*w['owned_fields']
    observed = defaultdict(dict)
    touches = defaultdict(list)
    arrivals = {}

    def record(j, cut, op):
        if rows[j]:
            observed[frames[j]].setdefault((j, rows[j]), (cut, op))

    for i in range(n):
        record(i, 0, 'initial')
    for t, (op, i, *args) in enumerate(w['program']):
        if t % 1024 == 0 and monotonic() >= deadline:
            raise TimeoutError('523-port donor census exceeded cap')
        touches[i].append(t)
        if op == 'MOVE':
            f, g = args
            assert frames[i] == f and f != 1
            if g == 1:
                peers = {rows[j]: ('live', f, t, j) for j, chart in enumerate(frames)
                         if j != i and chart == f and rows[j]}
                arrivals[t] = i, f, rows[i], peers
            frames[i] = g
        elif op == 'ADD':
            j, f = args
            assert frames[i] == frames[j] == f
            touches[j].append(t)
            rows[i] ^= rows[j]
        elif op == 'SWAP':
            j, = args
            touches[j].append(t)
            frames[i], frames[j] = frames[j], frames[i]
            rows[i], rows[j] = rows[j], rows[i]
            record(j, t+1, op)
        else:
            assert op in ('INIT', 'CLEAR') and args[0] != 1
            assert frames[i] == (None if op == 'INIT' else args[0])
            frames[i] = args[0] if op == 'INIT' else None
            rows[i] = 0
        record(i, t+1, op)
    want = [1 << i for i in range(n)] + [0]*w['owned_fields']
    for i in range(111):
        want[111+i] ^= 1 << i
    assert rows == want and frames == w['final'] + [None]*w['owned_fields']
    assert len(arrivals) == 545
    ends = {}
    for t, (i, _, _, _) in arrivals.items():
        uses = touches[i]
        j = uses.index(t)
        ends[t] = uses[j+1] if j+1 < len(uses) else len(w['program'])
    return arrivals, observed, ends, [row for f, row in zip(frames, rows) if f == 1]


def components(bases):
    parent = list(range(len(bases)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, space in enumerate(bases):
        for x, _ in space:
            while x:
                b = x & -x
                j = b.bit_length()-1
                parent[root(j)] = root(i)
                x ^= b
    groups = defaultdict(list)
    for i in range(len(bases)):
        groups[root(i)].append(i)
    return sorted(groups.values())


def cap(support, shift, old_stock=12):
    assert support <= shift <= 22
    return min(22, old_stock + support + shift)


def charged_refinements(root, price, word, dims, invoice):
    """A separate full-volume positive-rank split for every new donor."""
    interval = import_file('interval', root/'research/paired-query-only-bit/independent/interval_gate.py')
    ledger = price.terminal_ledger(word,dims)
    copies = len(invoice['native_instances'])
    assert copies == 36
    result = []
    for h in range(5):
        stock = min(22,14+2*h)
        relaxed = price.prices(root,invoice,word,dims,ledger,stock)
        row = {'new_charged_donors': h, 'stock_upper': stock, 'also_bounds_all_larger_h': h == 4,
               'directed': {}}
        for key, rec in relaxed.items():
            k = Fraction(key)
            charge = interval.smul(interval.sub(interval.exact(2),interval.power(2,k)),copies)
            lower, upper = map(Fraction,rec['net_upper'])
            c0,c1 = map(Fraction,interval.show(charge))
            assert 0 < c0 <= c1
            net = lower-h*c1, upper-h*c0
            assert net[1] < 0
            row['directed'][key] = {'minimum_split_tariff_interval': [str(c0),str(c1)],
                                    'unbilled_net_upper_interval': [str(lower),str(upper)],
                                    'net_upper_after_split_lower_tariff': list(map(str,net))}
        result.append(row)
    return result


def run(root, seconds):
    deadline = monotonic()+seconds
    pins, data = read_pinned(root)
    prev = import_file('round22', root/'round22/verify.py')
    price = import_file('pr7209', root/'pr7209/verify.py')
    assert cap(0, 0) == 12 and cap(4, 4) == 20 and cap(5, 5) == 22
    control = prev.transversal([[(1, 0), (2, 0)], [(1, 0)]])
    assert len(control[0]) == 2
    # An alternative leaving W cannot carry a valid new terminal payload.
    example = {}
    prev.insert(example, 1, 1)
    assert prev.intersection_projection([2], example) == (0, [])
    assert prev.intersection_projection([2, 3], example) == (1, [(1, 1)])
    word = json.loads(gzip.decompress(data[NATIVE]))
    assert 1 not in word['start']
    dims = {int(f): x['dim'] for f, x in word['frames'].items()}
    assert [f for f in dims if dims[f] == 8] == [1]
    invoice = json.loads(data[INVOICE])
    peer = json.loads(data['pr7244/PROPOSED-CLAIM.json'])
    assert peer['complex_BIT_premise'] == '376669/100000000'
    marks = [x['event'] for x in json.loads(data['pr7209/RESULT.json'])['bank_maps']]
    prev_result = json.loads(data['round22/RESULT.json'])
    quiet = prev_result['scope'][1]
    assert [v['event'] for v in quiet['banks']] == marks
    old_gate = quiet['endpoint_consistency']
    assert old_gate['endpoint_preserving_independent_upper'] == 12
    singletons = [b['banks'][0] for b in old_gate['blocks'] if len(b['banks']) == 1]
    assert len(singletons) == 10
    singleton_mask = prev.encoded(singletons)
    arrivals, observed, ends, required = timeline(word, deadline)
    donors = sorted(set(arrivals)-set(marks))
    assert len(donors) == 523
    order = donors+marks
    marked_offset = len(donors)
    W = {}
    for i, t in enumerate(order):
        assert prev.insert(W, arrivals[t][2], 1 << i)[0]
    assert len(W) == prev.rnk(required) == 545
    assert all(not prev.reduce(W, x)[0] for x in required)
    marked_spaces = []
    for i, entry in enumerate(quiet['banks']):
        raw = prev.raw_basis(prev.encoded(x['row']) for x in entry['source_witnesses'])
        _, space = prev.intersection_projection(raw, W)
        assert prev.rnk(v >> marked_offset for v, _ in space) == entry['projected_rank']
        marked_spaces.append(space)
    all_scopes = []
    for retime in (False, True):
        donor_maps = []
        donor_spaces = []
        eligible = []
        full_bases = []
        single_bases = []
        donor_sets = []
        for i, t in enumerate(donors):
            j, f, old, live = arrivals[t]
            candidates = dict(live)
            if retime:
                for (owner, row), (cut, op) in observed[f].items():
                    if cut <= ends[t] and (owner, row) != (j, old):
                        candidates.setdefault(row, ('cached', f, cut, owner, op))
            raw = prev.raw_basis(sorted(candidates))
            inside, space = prev.intersection_projection(raw, W)
            assert inside == len(space)
            donor_spaces.append(space)
            coord_space = [(v, row) for v, row in space if v != 1 << i]
            # A pure cancellation is infeasible alone. If a bank has more
            # choices, its whole span is still a safe upper for its projection.
            if coord_space:
                eligible.append(i)
            mark_b = {}
            sing_b = {}
            for v, row in space:
                proj = v >> marked_offset
                prev.insert(mark_b, proj, row)
                prev.insert(sing_b, proj & singleton_mask, row)
            full_bases.append(list(mark_b.values()))
            single_bases.append(list(sing_b.values()))
            if mark_b:
                donor_sets.append(i)
            donor_maps.append({'event': t, 'owner': j, 'source_chart': f,
                               'horizon': ends[t] if retime else t,
                               'old_row': prev.positions(old),
                               'source_rows': [{'row': prev.positions(x), 'witness': path}
                                               for x, path in sorted(candidates.items())],
                               'V_intersection_W_rank': inside,
                               'projection_marked_basis': [prev.positions(v) for v, _ in mark_b.values()],
                               'projection_singleton_basis': [prev.positions(v) for v, _ in sing_b.values()],
                               'full_terminal_basis': [prev.positions(v) for v, _ in space]})
            if monotonic() >= deadline:
                raise TimeoutError('523-port donor census exceeded cap')
        matches = []
        for choices in (full_bases, single_bases):
            assignment, restricted, restricted_rank = prev.transversal(choices)
            matches.append({'rank': len(assignment),
                            'assignments': [{'donor_index': i, 'event': donors[i], 'projection': prev.positions(v),
                                             'delta': prev.positions(x)} for i, v, x in assignment],
                            'rado_restricted': restricted, 'rado_restricted_rank': restricted_rank})
        t, s = (m['rank'] for m in matches)
        group = components(donor_spaces+marked_spaces)
        caps = cap(s,t)
        all_scopes.append({'scope': 'same-chart historical/quiet cache' if retime else 'same-cut physical peers',
                           'donors': donor_maps, 'possibly_changed_donors': len(eligible),
                           'donors_with_nonzero_old_marked_projection': len(donor_sets),
                           'marked_quotient_rank': matches[0], 'isolated_singleton_projection_rank': matches[1],
                           'terminal_support_component_sizes': dict(sorted(Counter(map(len,group)).items())),
                           'maximum_component': max(map(len,group)),
                           'components_with_marks': [[order[k] for k in g] for g in group if any(k>=523 for k in g)],
                           'raw_stock_upper': caps,
                           'price_upper': price.prices(root, invoice, word, dims, price.terminal_ledger(word,dims),caps)})
    return {'status':'NO VERIFIED GAIN','pins':pins,'seconds_cap':seconds,'completed_donor_slots':523,
            'pending_donor_slots':0,'new_sites':0,'quiet_singleton_mark_positions':singletons,
            'target':'10018846261809/2500000000000000','scopes':all_scopes,
            'one_separately_charged_split_per_additional_donor': charged_refinements(root,price,word,dims,invoice)}


if __name__ == '__main__':
    p = ArgumentParser(description=__doc__)
    p.add_argument('input_root',type=Path)
    p.add_argument('--seconds',type=int,default=480)
    args = p.parse_args()
    if not 1 <= args.seconds <= 480:
        p.error('--seconds must be in 1..480')
    print(json.dumps(run(args.input_root,args.seconds),sort_keys=True,indent=2))

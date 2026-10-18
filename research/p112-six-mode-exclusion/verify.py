#!/usr/bin/env python3
"""Read-only exact replay of the selected bilateral six-mode exclusion.

Python standard library only.  No solver, Git, discovery search, generated
receipt, sibling verifier, or workspace scratch module is used.
"""
from argparse import ArgumentParser
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from io import BytesIO
from math import comb, gcd
from pathlib import Path
import json
import tarfile

HERE = Path(__file__).resolve().parent
MODES = (1, 2, 0, 2, 3, 0, 0, 4, 5, 5, 4, 2, 4, 3, 1, 5, 3, 1)
F = (0, 2, 3, 5)
FULL = (1 << 38) - 1
CANDIDATE_SHA = 'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b'
ARCHIVE_PATH = 'research/community-frontier1094-audit/selected-replay.tar.gz'
ARCHIVE_SHA = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
MEMBER_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def object_pairs(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, 'duplicate JSON key: ' + key)
        out[key] = value
    return out


def decode(raw):
    return json.loads(raw, object_pairs_hook=object_pairs)


def pinned(raw, expected, name):
    require(sha256(raw).hexdigest() == expected, name + ' SHA256')
    return raw


def integer(x, low, high):
    return type(x) is int and low <= x <= high


def f2basis(rows):
    pivots = {}
    for value in rows:
        for p in sorted(pivots, reverse=True):
            if value >> p & 1:
                value ^= pivots[p]
        if value:
            p = value.bit_length() - 1
            for q in tuple(pivots):
                if pivots[q] >> p & 1:
                    pivots[q] ^= value
            pivots[p] = value
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def f2contains(basis, value):
    for row in basis:
        if value >> (row.bit_length() - 1) & 1:
            value ^= row
    return value == 0


def rho(left, right):
    return len(f2basis(sum(((a & b).bit_count() & 1) << j
                          for j, b in enumerate(right)) for a in left))


def join_closure(seeds):
    spans = {()}
    for seed in seeds:
        spans.update(f2basis(w + tuple(seed)) for w in tuple(spans))
    # A direct generator-closure check makes completeness explicit.
    require(all(f2basis(w + tuple(seed)) in spans
                for w in spans for seed in seeds), 'join closure is closed')
    return sorted(spans, key=lambda x: (len(x), x))


class QSpan:
    """Integer fraction-free row echelon space over Q."""
    def __init__(self, rows=()):
        self.pivots = {}
        for row in rows:
            self.add(row)

    def reduce(self, row):
        row = list(row)
        for p in sorted(self.pivots):
            base = self.pivots[p]
            if row[p]:
                a, b = base[p], row[p]
                row = [a*x - b*y for x, y in zip(row, base)]
                common = gcd(*row)
                if common:
                    row = [x // common for x in row]
        return row

    def add(self, row):
        row = self.reduce(row)
        p = next((j for j, x in enumerate(row) if x), None)
        if p is not None:
            common = gcd(*row)
            self.pivots[p] = tuple(x // common for x in row)

    def contains(self, rows):
        return all(not any(self.reduce(row)) for row in rows)

    def rows(self):
        return tuple(self.pivots[p] for p in sorted(self.pivots))

    def __len__(self):
        return len(self.pivots)


def canonical_intersection(rows, k):
    # Exterior-first elimination computes W intersect Q^57, not pi(W).
    reordered = QSpan(tuple(r[57:]) + tuple(r[:57]) for r in rows)
    return tuple(r[k:] for r in reordered.rows() if not any(r[:k]))


def qpair_rank(left, right):
    return len(QSpan(tuple(sum(x*y for x, y in zip(a, b)) for b in right)
                     for a in left)) if left and right else 0


def validate_header(cert):
    require(type(cert.get('schema_version')) is int and cert['schema_version'] == 2,
            'certificate schema 2')
    require(cert.get('modes') == list(MODES) and
            all(type(x) is int for x in cert['modes']), 'fixed mode assignment')
    require(type(cert.get('residual_axis')) is int and cert['residual_axis'] == 1,
            'residual must annihilate the exterior axis')
    require(type(cert.get('cover_library')) is list and len(cert['cover_library']) == 1598,
            'complete cover library')
    require(type(cert.get('families')) is list and len(cert['families']) == 4928,
            'complete family count')


def expand_covers(cert, family):
    refs = family.get('covers')
    require(type(refs) is list and len(refs) <= 2 and len(set(refs)) == len(refs),
            'distinct cover references for positive levels')
    require(all(integer(i, 0, len(cert['cover_library'])-1) for i in refs),
            'typed in-range cover references')
    covers = [cert['cover_library'][i] for i in refs]
    require([c.get('level') for c in covers] == list(range(1,len(covers)+1)) and
            all(type(c['level']) is int for c in covers), 'cover levels 1 and 2')
    return covers


class Replay:
    def __init__(self, repo_root):
        source = decode((HERE / 'SOURCES.json').read_bytes())
        require(source['candidate']['sha256'] == CANDIDATE_SHA and
                source['archive_member']['sha256'] == MEMBER_SHA,
                'manifest scientific pins')
        archive_entry = [x for x in source['files'] if x['path'] == ARCHIVE_PATH]
        require(len(archive_entry) == 1 and archive_entry[0]['sha256'] == ARCHIVE_SHA,
                'manifest archive pin')
        raw = pinned((HERE / 'CERTIFICATE.json').read_bytes(),
                     source['certificate']['sha256'], 'certificate')
        self.certificate_sha = sha256(raw).hexdigest()
        self.cert = decode(raw)
        validate_header(self.cert)
        candidate = decode(pinned((HERE / 'CANDIDATE.json').read_bytes(),
                                  CANDIDATE_SHA, 'candidate'))
        archive = pinned((repo_root / ARCHIVE_PATH).read_bytes(), ARCHIVE_SHA, 'archive')
        with tarfile.open(fileobj=BytesIO(archive), mode='r:gz') as tar:
            matches = [x for x in tar.getmembers() if x.name == MEMBER]
            require(len(matches) == 1 and matches[0].isfile(), 'unique data member')
            payload = decode(pinned(tar.extractfile(matches[0]).read(), MEMBER_SHA, 'member'))
        q = {row['port']: row['q'] for row in payload['recipes']}
        require(len(q) == len(payload['recipes']) == 112 and set(q) == set(range(112)),
                '112 distinct port records')
        require(all(integer(x, 1, 511) for x in q.values()) and len(set(q.values())) == 112,
                '112 distinct binary labels')
        self.groups = candidate['groups']
        require(len(self.groups) == 38 and len(self.groups[0]) == 1 and
                all(len(g) == 3 for g in self.groups[1:]) and
                sorted(p for g in self.groups for p in g) == list(range(112)),
                'physical port partition')
        self.E = tuple(tuple(q[p] for p in g) for g in self.groups)
        for group in self.E:
            require(all(((x & y).bit_count() & 1) == int(i == j)
                        for i, x in enumerate(group) for j, y in enumerate(group)),
                    'own-group binary identity')
        closure = join_closure(self.E)
        require(len(closure) == 2213, '2213 physical spans')
        self.allowed = tuple(sum(1 << g for g, seed in enumerate(self.E)
                                 if all(f2contains(w, x) for x in seed)) for w in closure)
        require(len(set(self.allowed)) == 2213, 'full-membership closure masks')
        self.chart_cache = {}
        self.span_cache = {}

    @lru_cache(None)
    def physical(self, mask):
        return f2basis(x for g, seed in enumerate(self.E) if mask >> g & 1 for x in seed)

    @lru_cache(None)
    def charge(self, left, right):
        return rho(self.physical(left), self.physical(right))

    def local_intersection(self, mask, modes, k):
        width = 57+k
        rows = []
        alive = [True]*k
        for i, mode in enumerate(modes):
            odd, even = bool(mask >> (2*i+1) & 1), bool(mask >> (2*i+2) & 1)
            if mode >= 0 and not (odd or even):
                alive[mode] = False
            if odd and even:
                for axis in range(3):
                    if i == 7 and axis == 1 and not mask & 1:
                        continue
                    row = [0]*width
                    row[3*i+axis] = 1
                    rows.append(tuple(row))
        if mask >> 37 & 1:
            for j in range(54, 57):
                row = [0]*width
                row[j] = 1
                rows.append(tuple(row))
        for mode, active in enumerate(alive):
            if active:
                row = [0]*width
                row[57+mode] = 1
                for i, value in enumerate(modes):
                    if value == mode and not mask >> (2*i+2) & 1:
                        row[3*i] = -1
                rows.append(tuple(row))
        actual = projected = 0
        for row in rows:
            sm, pm = self.vector_masks(row, modes)
            actual |= sm
            projected |= pm
        require(actual & ~mask == 0, 'intersection satisfies all missing groups')
        return tuple(rows), actual, projected

    @staticmethod
    def vector_masks(row, modes):
        actual = projected = 0
        for i, mode in enumerate(modes):
            block = row[3*i:3*i+3]
            even = (block[0] + (row[57+mode] if mode >= 0 else 0), block[1], block[2])
            if any(block):
                actual |= 1 << (2*i+1)
                projected |= (1 << (2*i+1)) | (1 << (2*i+2))
            if any(even):
                actual |= 1 << (2*i+2)
        if any(row[54:57]):
            actual |= 1 << 37
            projected |= 1 << 37
        if row[22]:
            actual |= 1
            projected |= 1
        return actual, projected

    def chart(self, blocks):
        blocks = tuple(tuple(x) for x in blocks)
        if blocks in self.chart_cache:
            return self.chart_cache[blocks]
        lookup = {a: i for i, block in enumerate(blocks) for a in block}
        require(len(lookup) == sum(map(len, blocks)), 'disjoint quotient blocks')
        modes = tuple(lookup.get(a, -1) for a in MODES)
        records = {}
        for mask in self.allowed:
            rows, actual, projected = self.local_intersection(mask, modes, len(blocks))
            if not rows:
                continue
            if actual in records:
                require(records[actual]['projected'] == projected and
                        len(records[actual]['rows']) == len(rows), 'stratum deduplication')
            else:
                records[actual] = {'rows': rows, 'projected': projected}
        self.chart_cache[blocks] = records
        return records

    def cover_space(self, blocks, masks):
        key = (blocks, tuple(masks))
        if key not in self.span_cache:
            chart = self.chart(blocks)
            space = QSpan(row for mask in masks for row in chart[mask]['rows'])
            inside = frozenset(mask for mask, s in chart.items() if space.contains(s['rows']))
            canon = canonical_intersection(space.rows(), len(blocks))
            self.span_cache[key] = (space, inside, canon)
        return self.span_cache[key]

    def edges(self, sb, tb):
        result = {1: [], 2: []}
        for a, s in self.chart(sb).items():
            for b, t in self.chart(tb).items():
                loss = min(6, self.charge(s['projected'], t['projected'])) - self.charge(a, b)
                require(loss <= 2, 'effective loss at most two')
                for level in range(1, loss+1):
                    result[level].append((a, b))
        return result

    def cover(self, sb, tb, entry, edges):
        require(set(entry) == {'level', 'source_masks', 'reader_masks',
                              'line_source_masks', 'line_reader_masks'}, 'cover fields')
        charts = self.chart(sb), self.chart(tb)
        masks = []
        for key, chart in zip(('source_masks', 'reader_masks'), charts):
            values = entry[key]
            require(type(values) is list and all(integer(x, 1, FULL) for x in values)
                    and len(values) == len(set(values)) and all(x in chart for x in values),
                    'cover masks identify exact support intersections')
            masks.append(tuple(values))
        ws, cs, c = self.cover_space(sb, masks[0])
        wt, ct, d = self.cover_space(tb, masks[1])
        require(all(a in cs or b in ct for a, b in edges), 'complete positive-edge cover')
        kappa = len(c)+len(d)-qpair_rank(c, d)
        line_values = entry['line_source_masks'], entry['line_reader_masks']
        require((line_values[0] is None) == (line_values[1] is None), 'paired line cover fields')
        line_cap = None
        if line_values[0] is not None:
            for values, chart in zip(line_values, charts):
                require(type(values) is list and all(integer(x, 1, FULL) for x in values)
                        and len(values) == len(set(values)) and all(x in chart for x in values),
                        'line masks identify support intersections')
                require(all(len(chart[x]['rows']) == 1 for x in values), 'actual line dimensions')
            ls, lt = map(set, line_values)
            require(all(a in ls or b in lt for a, b in edges), 'complete line cover')
            line_cap = len(ls)+len(lt)
        return kappa, line_cap, (len(c), len(d), qpair_rank(c, d))

    def canonical_prerequisites(self):
        h = [f2basis(self.E[2*i+1]+self.E[2*i+2]) for i in range(18)]
        j = f2basis(self.E[37])
        require(rho(j, j) == 3 and all(rho(j, a) == rho(a, j) == 3 for a in h), 'J prices')
        require(all(rho(a, b) >= 4 for a in h for b in h), 'ordinary prices')
        require(all(rho(f2basis(a+j), f2basis(b+j)) >= 6 for a in h for b in h),
                'J plus ordinary prices')
        seeds = h+[j]
        spans = join_closure(seeds)
        require(len(spans) == 40, '40 canonical component spans including zero')
        membership = {a: {i for i, seed in enumerate(seeds)
                          if all(f2contains(a, x) for x in seed)} for a in spans}
        counts = Counter()
        for a in spans:
            for b in spans:
                sa, sb = membership[a], membership[b]
                price = rho(a, b)
                if sa & set(range(18)) and sb & set(range(18)) and price < 6:
                    require(not sa & sb and price in (4, 5), 'cheap disjoint component supports')
                    require((6-price)*comb(len(sa)+len(sb), len(sa)) <= 4,
                            'acyclic selection discount')
                    counts[(price, len(sa), len(sb))] += 1
        expected = {(4,1,1):20, (5,1,1):178, (5,1,2):33,
                    (5,2,1):33, (5,1,3):4, (5,3,1):4}
        require(dict(counts) == expected and sum(counts.values()) == 272,
                '272 exact cheap rectangles')
        return {'join_spans': 40, 'cheap_rectangles': 272,
                'rank4_rectangles': 20, 'rank5_rectangles': 252}

    def baseline(self):
        coord = {}
        for i in range(18):
            for group in (2*i+1, 2*i+2):
                for axis, port in enumerate(self.groups[group]):
                    coord[port] = 3*i+axis
        for axis, port in enumerate(self.groups[37]):
            coord[port] = 54+axis
        coord[self.groups[0][0]] = 22
        strict = 0
        for g, left in enumerate(self.groups):
            for h, right in enumerate(self.groups):
                if g == h or rho(self.E[g], self.E[h]):
                    for a in left:
                        for b in right:
                            require(int(coord[a] == coord[b]) == int(a == b), 'baseline strict endpoint')
                            strict += 1
        masks = [sum(1 << g for g, ports in enumerate(self.groups)
                     if any(coord[p] == j for p in ports)) for j in range(57)]
        cost = sum(self.charge(mask, mask) for mask in masks)
        require(cost == 334 and strict == 12124, 'baseline 334 and strict-entry count')
        residual = 1 | (1 << 15) | (1 << 16)
        require(self.charge(residual, residual) == 7, 'mandatory residual negative unit')
        require(all(self.vector_masks(tuple(int(k == 22) for k in range(63)), MODES)[s]
                    & residual == residual for s in (0,1)), 'residual implication on both projections')
        return {'strict_entries': strict, 'terms': 57, 'invoice': cost,
                'mandatory_residual_tariff': 7}

    def run(self):
        canonical = self.canonical_prerequisites()
        baseline = self.baseline()
        ambient_blocks = tuple((a,) for a in range(6))
        ambient = self.chart(ambient_blocks)
        require(len(ambient) == 80, '80 ambient support intersections')
        e = self.edges(ambient_blocks, ambient_blocks)
        prices = [self.charge(a, b) for a in ambient for b in ambient]
        require(min(prices) == 1 and len(prices) == 6400 and e[2], '6400 ambient prices and nonzero loss2')
        zero_masks = [sum(1 << (2*i+2) for i, a in enumerate(MODES) if bits >> a & 1)
                      for bits in range(1, 64)]
        zero_min = min(self.charge(a, b) for a in zero_masks for b in ambient)
        require(len(set(zero_masks)) == 63 and zero_min == 3, 'projection-zero actual supports')
        ambient_covers = self.cert['ambient_covers']
        require([x['level'] for x in ambient_covers] == [1,2], 'ambient cover levels')
        ac = [self.cover(ambient_blocks, ambient_blocks, c, e[c['level']]) for c in ambient_covers]
        require(ac[0][0] == 39 and ac[0][2] == (39,39,39) and ac[1][:2] == (0,8),
                'ambient quotient constants and line cap')
        for key in ('line_source_masks','line_reader_masks'):
            lines = ambient_covers[1][key]
            axes = []
            for mask in lines:
                row = ambient[mask]['rows'][0]
                support = [i for i, x in enumerate(row[57:]) if x]
                require(len(support) == 1, 'loss2 quotient is a coordinate axis')
                axes.extend(support)
            require(sorted(axes) == list(F), 'four independent loss2 axes')
        expected = []
        for aa in range(16):
            a = tuple(F[i] for i in range(4) if aa >> i & 1)
            for jj in range(1,64):
                j = tuple(i for i in range(6) if jj >> i & 1)
                if set(a) & set(j):
                    continue
                for bb in range(16):
                    b = tuple(F[i] for i in range(4) if bb >> i & 1)
                    expected.append((a,j,b))
        require(len(expected) == 4928, 'complete quotient-family enumeration')
        histogram = Counter()
        for index, ((a,j,b), family) in enumerate(zip(expected, self.cert['families'])):
            require(set(family) == {'index','A','J','B','covers'} and
                    integer(family['index'],0,4927) and family['index'] == index and
                    family['A'] == list(a) and family['J'] == list(j) and family['B'] == list(b) and
                    all(type(x) is int for key in ('A','J','B') for x in family[key]),
                    'complete exact family domain')
            sb, tb = tuple((x,) for x in a)+(j,), tuple((x,) for x in b)
            edges = self.edges(sb, tb)
            covers = expand_covers(self.cert,family)
            require([c['level'] for c in covers] == [level for level in (1,2) if edges[level]],
                    'a cover for every positive loss level')
            bounds = [self.cover(sb,tb,c,edges[c['level']])
                      for c in covers]
            terms = [57+len(sb)+len(tb)]
            if len(j) == 1 and j[0] in F:
                terms.append(terms[0]+1)
            for m in terms:
                floor = 2*m+220-sum(min(m,m-57+k,cap if cap is not None else m)
                                   for k,cap,_ in bounds)
                require(floor >= 297, 'every necessary term case excludes target296')
                histogram[floor] += 1
        require(sum(histogram.values()) == 5440 and min(histogram) == 297, '5440 cases, floor297')
        controls = self.controls(ambient_blocks, e)
        return {'status':'PASS','certificate_sha256':self.certificate_sha,
                'physical_spans':2213,'ambient_strata':80,'ordered_rectangles':6400,
                'projection_zero_supports_per_side':63,'projection_zero_minimum':zero_min,
                'canonical_prerequisites':canonical,'baseline':baseline,
                'families':4928,'term_cases':5440,'minimum_floor':min(histogram),
                'floor_histogram':dict(sorted(histogram.items())), 'fault_controls':controls,
                'scope':'Only the fixed endpoint and aligned bilateral six-mode spaces; no attaining construction.'}

    def controls(self, ambient_blocks, edges):
        def rejects(call):
            try:
                call()
            except (ValueError, KeyError, TypeError):
                return
            raise ValueError('fault control was accepted')
        rejects(lambda: decode('{"a":1,"a":2}'))
        bad = dict(self.cert, families=self.cert['families'][:-1])
        rejects(lambda: validate_header(bad))
        bad = dict(self.cert, modes=list(MODES[:-1]) + [0])
        rejects(lambda: validate_header(bad))
        bad = dict(self.cert, residual_axis=0)
        rejects(lambda: validate_header(bad))
        for value in (True, 0.0, -1, len(self.cert['cover_library'])):
            bad = dict(self.cert['families'][0], covers=[value,1])
            rejects(lambda bad=bad: expand_covers(self.cert,bad))
        empty = {'level':1,'source_masks':[],'reader_masks':[],
                 'line_source_masks':None,'line_reader_masks':None}
        rejects(lambda: self.cover(ambient_blocks,ambient_blocks,empty,edges[1]))
        return ['duplicate_json_key','missing_family','changed_mode','residual_axis',
                'boolean_reference','float_reference','negative_reference','oversize_reference',
                'missing_cover_edge']


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=HERE.parents[1])
    args = parser.parse_args()
    print(json.dumps(Replay(args.repo_root.resolve()).run(), sort_keys=True, indent=2))


if __name__ == '__main__':
    main()

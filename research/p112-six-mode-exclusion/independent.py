#!/usr/bin/env python3
"""Portable exact independent replay of the selected six-mode certificate.

Standard library only; no imports from the primary checker or predecessor
programs, no subprocesses/network, and no writes. All input geometry bytes are
authenticated before parsing. The certificate supplies covers, not trusted
ranks or prices. Every ambient and restricted geometric cover is replayed.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
from math import gcd, lcm
from pathlib import Path
import io
import json
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {
    "candidate": "dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b",
    "archive": "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6",
    "member": "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
}
MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
MODES = (1, 2, 0, 2, 3, 0, 0, 4, 5, 5, 4, 2, 4, 3, 1, 5, 3, 1)
F_AXES = (0, 2, 3, 5)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated(raw, expected, label):
    need(sha256(raw).hexdigest() == expected, label + " SHA256")
    return raw


def members(bits):
    while bits:
        low = bits & -bits
        yield low.bit_length() - 1
        bits ^= low


def binary_span(bits, vectors):
    for value in vectors:
        if not (bits >> value) & 1:
            bits |= sum(1 << (x ^ value) for x in members(bits))
    return bits


def binary_basis(vectors):
    pivots = {}
    for v in vectors:
        while v:
            p = v.bit_length() - 1
            if p in pivots:
                v ^= pivots[p]
            else:
                pivots[p] = v
                break
    return tuple(pivots.values())


def integer_row(values):
    row = list(values)
    if any(isinstance(x, Fraction) for x in row):
        den = lcm(*(Fraction(x).denominator for x in row))
        row = [int(x * den) for x in row]
    need(all(type(x) is int for x in row), "exact integer rank rows")
    factor = gcd(*row) if row else 0
    return [x // factor for x in row] if factor else row


class Span:
    """Integer elimination with gcd normalization; all ranks are over Q."""
    def __init__(self, rows=()):
        self.pivots = {}
        for row in rows:
            self.add(row)

    def reduce(self, row):
        row = integer_row(row)
        for p, basis in sorted(self.pivots.items()):
            if row[p]:
                g = gcd(row[p], basis[p])
                a, b = basis[p] // g, row[p] // g
                row = [a*x-b*y for x, y in zip(row, basis)]
                factor = gcd(*row)
                if factor:
                    row = [x // factor for x in row]
        return row

    def add(self, row):
        row = self.reduce(row)
        p = next((j for j, x in enumerate(row) if x), None)
        if p is None:
            return False
        self.pivots[p] = row
        return True

    def contains(self, rows):
        return all(not any(self.reduce(row)) for row in rows)


def canonical_intersection(rows, k):
    # Eliminate latent coordinates before canonical ones. The echelon rows
    # whose pivot is canonical form the exact zero-latent intersection.
    E = Span(row[57:] + row[:57] for row in rows)
    return [row[k:] for p, row in sorted(E.pivots.items()) if p >= k]


def pairing_rank(left, right):
    return len(Span([sum(x*y for x, y in zip(a, b)) for b in right] for a in left).pivots)


class Geometry:
    def __init__(self):
        candidate_raw = authenticated((HERE / "CANDIDATE.json").read_bytes(), PINS["candidate"], "candidate")
        archive_raw = authenticated((ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes(), PINS["archive"], "archive")
        with tarfile.open(fileobj=io.BytesIO(archive_raw)) as stream:
            handle = stream.extractfile(MEMBER)
            need(handle is not None, "exact archive member")
            member = authenticated(handle.read(), PINS["member"], "label member")
        candidate = json.loads(candidate_raw)
        labels = json.loads(member)["recipes"]
        q = {r["port"]: r["q"] for r in labels}
        need(len(labels) == len(q) == 112 and set(q) == set(range(112)), "112 literal port labels")
        need(len(set(q.values())) == 112 and all(type(x) is int and 0 < x < 512 for x in q.values()), "distinct binary9 labels")
        self.groups = candidate["groups"]
        need(len(self.groups) == 38 and len(self.groups[0]) == 1 and all(len(g) == 3 for g in self.groups[1:]), "residual and 37 triads")
        flat = [p for group in self.groups for p in group]
        need(len(flat) == 112 and set(flat) == set(range(112)), "complete literal port partition")
        self.spaces = [tuple(q[p] for p in group) for group in self.groups]
        need(all(((a & b).bit_count() & 1) == int(i == j) for E in self.spaces for i, a in enumerate(E) for j, b in enumerate(E)), "complete orthonormal physical groups")
        free = [[a, b] for a, b in combinations(range(38), 2) if self.price(1 << a, 1 << b) == 0]
        need(free == candidate["orthogonal_group_pairs"], "all actual free pairs")
        need(candidate["disjoint_free_triad_pairs"] == [[a, a+1] for a in range(1, 37, 2)], "literal paired groups")
        family = {1}
        for E in self.spaces:
            family |= {binary_span(W, E) for W in tuple(family)}
        need(len(family) == 2213, "complete generated binary span family")
        self.closed_masks = sorted(sum(1 << g for g, E in enumerate(self.spaces) if all(W >> x & 1 for x in E)) for W in family)

    @lru_cache(None)
    def physical(self, mask):
        need(type(mask) is int and 0 <= mask < 1 << 38, "physical group mask domain")
        return binary_basis(x for g in members(mask) for x in self.spaces[g])

    @lru_cache(None)
    def price(self, left, right):
        B = self.physical(right)
        rows = [sum(((x & y).bit_count() & 1) << j for j, y in enumerate(B)) for x in self.physical(left)]
        return len(binary_basis(rows))


def literal_intersection(modes, k, mask):
    """Solve all missing physical rows independently as x=0 or x+t=0."""
    zero = (0,) * k
    prescribed = [[] for _ in range(57)]
    for role, mode in enumerate(modes):
        for axis in range(3):
            j = 3*role+axis
            if not mask >> (2*role+1) & 1:
                prescribed[j].append(zero)
            if not mask >> (2*role+2) & 1:
                row = [0] * k
                if axis == 0 and mode >= 0:
                    row[mode] = -1
                prescribed[j].append(tuple(row))
    if not mask & 1:
        prescribed[22].append(zero)
    if not mask >> 37 & 1:
        for j in range(54, 57):
            prescribed[j].append(zero)
    forced = set()
    for choices in prescribed:
        for other in choices[1:]:
            changed = [i for i, (x, y) in enumerate(zip(choices[0], other)) if x != y]
            need(len(changed) <= 1, "one-mode missing-row equation")
            forced.update(changed)
    basis = []
    for j, choices in enumerate(prescribed):
        if not choices:
            row = [0] * (57+k)
            row[j] = 1
            basis.append(row)
    for mode in range(k):
        if mode not in forced:
            basis.append([choices[0][mode] if choices else 0 for choices in prescribed] + [int(mode == a) for a in range(k)])
    actual = projected = 0
    for v in basis:
        a = p = 0
        for role, mode in enumerate(modes):
            odd = v[3*role:3*role+3]
            even = odd[:]
            if mode >= 0:
                even[0] += v[57+mode]
            if any(odd):
                a |= 1 << (2*role+1)
                p |= 3 << (2*role+1)
            if any(even):
                a |= 1 << (2*role+2)
        if v[22]:
            a |= 1
            p |= 1
        if any(v[54:57]):
            a |= 1 << 37
            p |= 1 << 37
        need(a & ~mask == 0, "literal missing physical rows satisfied")
        actual |= a
        projected |= p
    return {"basis": basis, "mask": actual, "projected": projected, "dimension": len(basis)}


class Replay:
    def __init__(self, geometry):
        self.G = geometry
        self.ambient = self.make_strata(MODES, 6, geometry.closed_masks)
        need(len(self.ambient) == 80, "complete ambient support strata")
        self.chart_cache = {}
        self.cover_cache = {}
        self.side_cache = {}
        self.rectangle_count = 0
        self.cover_count = 0

    def make_strata(self, modes, k, allowed):
        records = {}
        for mask in allowed:
            r = literal_intersection(modes, k, mask)
            if not r["basis"]:
                continue
            if r["mask"] in records:
                old = records[r["mask"]]
                need(r["projected"] == old["projected"] and r["dimension"] == old["dimension"], "duplicate exact support intersection")
            else:
                records[r["mask"]] = r
        return records

    def chart(self, groups):
        groups = tuple(tuple(g) for g in groups)
        if groups not in self.chart_cache:
            lookup = {a: i for i, group in enumerate(groups) for a in group}
            need(len(lookup) == sum(map(len, groups)), "disjoint quotient coordinates")
            modes = tuple(lookup.get(a, -1) for a in MODES)
            # Ambient V_W has actual support M_W within W. Restricting the
            # quotient gives V_W intersect chart = V_M_W intersect chart.
            # Therefore the complete 80 ambient masks suffice for every chart.
            self.chart_cache[groups] = (self.make_strata(modes, len(groups), self.ambient), len(groups))
        return self.chart_cache[groups]

    @lru_cache(None)
    def loss(self, actual_a, projected_a, actual_b, projected_b):
        return min(6, self.G.price(projected_a, projected_b)) - self.G.price(actual_a, actual_b)

    def edges(self, S, T):
        edges = {1: [], 2: []}
        for a, u in S.items():
            for b, v in T.items():
                loss = self.loss(a, u["projected"], b, v["projected"])
                need(loss <= 2, "selected family maximum capped loss2")
                for level in range(1, loss+1):
                    edges[level].append((a, b))
                self.rectangle_count += 1
        return {level: value for level, value in edges.items() if value}

    def cover(self, certificate, S, T, ks, kt, edges):
        source_ids = certificate["source_masks"]
        reader_ids = certificate["reader_masks"]
        need(len(set(source_ids)) == len(source_ids) and len(set(reader_ids)) == len(reader_ids), "distinct cover masks")
        need(all(a in S for a in source_ids) and all(b in T for b in reader_ids), "literal cover support identifiers")
        def side(space, ids, k):
            key = (id(space), tuple(sorted(ids)))
            if key not in self.side_cache:
                L = Span(row for a in ids for row in space[a]["basis"])
                C = canonical_intersection(list(L.pivots.values()), k)
                covered = {a for a, v in space.items() if L.contains(v["basis"])}
                self.side_cache[key] = (C, covered)
            return self.side_cache[key]
        C, covered_source = side(S, source_ids, ks)
        D, covered_reader = side(T, reader_ids, kt)
        key = (tuple(tuple(row) for row in C), tuple(tuple(row) for row in D))
        if key not in self.cover_cache:
            pairing = pairing_rank(C, D)
            self.cover_cache[key] = len(C)+len(D)-pairing
        kappa = self.cover_cache[key]
        need(all(a in covered_source or b in covered_reader for a, b in edges), "every actual loss edge covered")
        left = certificate.get("line_source_masks")
        right = certificate.get("line_reader_masks")
        need((left is None) == (right is None), "both optional line-cover sides")
        cap = None
        if left is not None:
            need(len(set(left)) == len(left) and len(set(right)) == len(right), "distinct line-cover masks")
            need(all(a in S and S[a]["dimension"] == 1 for a in left) and all(b in T and T[b]["dimension"] == 1 for b in right), "actual one-dimensional lines")
            need(all(a in left or b in right for a, b in edges), "complete actual line cover")
            cap = len(left)+len(right)
        self.cover_count += 1
        return kappa, cap


def check_family_keys(records):
    expected = []
    for aa in range(16):
        A = [a for i, a in enumerate(F_AXES) if aa >> i & 1]
        for jj in range(1, 64):
            J = list(members(jj))
            if set(A).intersection(J):
                continue
            for bb in range(16):
                B = [a for i, a in enumerate(F_AXES) if bb >> i & 1]
                expected.append((A, J, B))
    need(len(records) == len(expected) == 4928, "complete finite quotient family")
    for i, (r, key) in enumerate(zip(records, expected)):
        need(r["index"] == i and (r["A"], r["J"], r["B"]) == key, "every finite family exactly once in canonical order")


def canonical_invoice_census(G):
    components = [3 << (2*i+1) for i in range(18)] + [1 << 37]
    need(all(G.price(components[18], H) == 3 and G.price(H, components[18]) == 3 for H in components), "J/paired canonical prices")
    need(all(G.price(H, Q) >= 4 for H in components[:18] for Q in components[:18]), "ordinary canonical component prices")
    need(all(G.price(H | components[18], Q | components[18]) >= 6 for H in components[:18] for Q in components[:18]), "two-sided J surcharge")
    physical = [G.physical(mask) for mask in components]
    closure = {1}
    for E in physical:
        closure |= {binary_span(W, E) for W in tuple(closure)}
    need(len(closure) == 40, "complete19component join closure including zero")
    records = []
    for W in closure:
        if W == 1:
            continue
        contained = frozenset(i for i, E in enumerate(physical) if all(W >> x & 1 for x in E))
        mask = 0
        for i in contained:
            mask |= components[i]
        records.append((contained, mask))
    counts = Counter()
    for A, a in records:
        for B, b in records:
            price = G.price(a, b)
            if price not in (4, 5):
                continue
            need(not A.intersection(B) and A - {18} and B - {18}, "cheap rectangles are disjoint and nonpure")
            if price == 4:
                need(len(A) == len(B) == 1, "tariff4 selection probability at least1/2")
            else:
                need(min(len(A), len(B)) == 1 and max(len(A), len(B)) <= 3, "tariff5 selection probability at least1/4")
            # Deleting J cannot make either support empty or reduce the
            # ordering-selection probability used for the I54 inequality.
            need(min(len(A-{18}), len(B-{18})) == 1 and max(len(A-{18}), len(B-{18})) <= (1 if price == 4 else 3), "same cheap-term probabilities after deleting J")
            counts[(price, len(A), len(B))] += 1
    expected = {(4, 1, 1): 20, (5, 1, 1): 178, (5, 1, 2): 33,
                (5, 2, 1): 33, (5, 1, 3): 4, (5, 3, 1): 4}
    need(dict(counts) == expected and sum(counts.values()) == 272, "all canonical cheap rectangle classes")
    return {"component_spans_including_zero": 40, "cheap_rectangles": 272,
            "classes": [{"price": p, "left_components": a, "right_components": b, "count": n}
                        for (p, a, b), n in sorted(counts.items())]}


def controls(G, R):
    # Literal canonical endpoint, full strict mask and baseline334.
    def coordinate(port):
        g = next(i for i, pp in enumerate(G.groups) if port in pp)
        if g == 0:
            return 22
        if g == 37:
            return 54+G.groups[g].index(port)
        return 3*((g-1)//2)+G.groups[g].index(port)
    c = [coordinate(p) for p in range(112)]
    owner = {p: g for g, pp in enumerate(G.groups) for p in pp}
    required = 0
    for p in range(112):
        for q in range(112):
            if owner[p] == owner[q] or G.price(1 << owner[p], 1 << owner[q]):
                need(int(c[p] == c[q]) == int(p == q), "literal strict endpoint")
                required += 1
    baseline = 0
    for j in range(57):
        mask = sum(1 << g for g, pp in enumerate(G.groups) if any(c[p] == j for p in pp))
        baseline += G.price(mask, mask)
    need(required == 12124 and baseline == 334, "all required entries and canonical334 positive control")
    residual = 1 | (1 << 15) | (1 << 16)
    need(G.price(residual, residual) == 7, "negative effective residual unit")
    # Nontrivial dual rational gauge, all112 squared entries and every mode.
    lambdas = (Fraction(1), Fraction(1, 2), Fraction(1), Fraction(1), Fraction(-2, 3), Fraction(4, 7))
    scale = [Fraction(1)]*112
    for i, mode in enumerate(MODES):
        scale[G.groups[2*i+1][0]] = scale[G.groups[2*i+2][0]] = lambdas[mode]
    need(all(scale[p] == scale[q] for p in range(112) for q in range(112) if c[p] == c[q]), "all endpoint entries invariant under dual gauge")
    v = (0, Fraction(2), 0, 0, Fraction(-3, 2), Fraction(7, 4))
    need([v[i]*lambdas[i] for i in range(6)] == [0, 1, 0, 0, 1, 1], "arbitrary nonzero quotient amplitudes normalize")
    # Simultaneous proportional coalescence is not rank preserving.
    U = [[1, 1, 0], [0, 0, 1]]
    V = [[1, 0, 0], [0, 0, 1], [1, -1, 0]]
    merged = [[1, 0], [0, 1], [0, 0]]
    need(len(Span(V).pivots) == 3 and len(Span(merged).pivots) == 2, "opposite rank can drop under coalescence")
    need([[sum(u[t]*v[t] for t in range(3)) for v in V] for u in U] == [[1, 0, 0], [0, 1, 0]], "coalescence endpoint control")
    # Guards must remain active under -O.
    faults = 0
    for operation in (lambda: authenticated(b"corrupt", PINS["candidate"], "fault"),
                      lambda: need(G.price(residual, residual) <= 6, "underpriced residual fault"),
                      lambda: check_family_keys([]),
                      lambda: need(R.loss(residual, residual, residual, residual) == 0, "discarded negative residual fault")):
        try:
            operation()
        except ValueError:
            faults += 1
    need(faults == 4, "semantic fault guards active")
    # Removing both sides of a real positive-loss edge is rejected by the
    # same geometric coverage check used for every committed certificate.
    edge = next((a, b) for a, u in R.ambient.items() for b, v in R.ambient.items()
                if R.loss(a, u["projected"], b, v["projected"]) > 0)
    try:
        R.cover({"source_masks": [], "reader_masks": []}, R.ambient, R.ambient, 6, 6, [edge])
    except ValueError:
        faults += 1
    need(faults == 5, "deleted physical edge-cover fault rejected")
    return {"required_endpoint_entries": required, "baseline_cost": baseline, "fault_controls": faults,
            "dual_rational_gauge": "all112squared entries preserved", "coalescence_rank_loss": [3, 2]}


def run():
    G = Geometry()
    raw = (HERE / "CERTIFICATE.json").read_bytes()
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    need(sources["candidate"]["path"] == "CANDIDATE.json" and sources["candidate"]["sha256"] == PINS["candidate"] and
         sources["archive_member"]["path"] == MEMBER and sources["archive_member"]["sha256"] == PINS["member"], "source manifest fixed geometry bindings")
    need(sources["certificate"]["path"] == "CERTIFICATE.json", "literal certificate path")
    authenticated(raw, sources["certificate"]["sha256"], "certificate")
    certificate = json.loads(raw)
    need(certificate["schema_version"] == 2 and tuple(certificate["modes"]) == MODES and certificate["residual_axis"] == 1, "selected six-mode scope")
    library = certificate["cover_library"]
    need(isinstance(library, list) and all(isinstance(c, dict) for c in library), "explicit deduplicated cover library")
    replay = Replay(G)
    ambient_edges = replay.edges(replay.ambient, replay.ambient)
    ambient_bounds = {}
    need({c["level"] for c in certificate["ambient_covers"]} == set(ambient_edges), "ambient threshold coverage")
    for c in certificate["ambient_covers"]:
        level = c["level"]
        ambient_bounds[level] = replay.cover(c, replay.ambient, replay.ambient, 6, 6, ambient_edges[level])
    need(ambient_bounds[1][0] == 39 and ambient_bounds[2][1] == 8, "audited deficit finite premises")
    second = next(c for c in certificate["ambient_covers"] if c["level"] == 2)
    for side in ("line_source_masks", "line_reader_masks"):
        lines = second[side]
        quotient = []
        axes = []
        for mask in lines:
            row = replay.ambient[mask]["basis"][0][57:]
            nz = [j for j, x in enumerate(row) if x]
            need(len(nz) == 1, "loss2 cover line is a coordinate quotient axis")
            quotient.append(row)
            axes.append(nz[0])
        need(sorted(axes) == list(F_AXES) and len(Span(quotient).pivots) == 4, "four independent loss2 axes per side")
    # Canonical-projection-zero vectors have one arbitrary nonzero coefficient
    # per selected mode. Disjoint supports make these63 masks complete.
    zero_minimum = 10
    for mask in range(1, 64):
        physical = sum(1 << (2*i+2) for i, mode in enumerate(MODES) if mask >> mode & 1)
        zero_minimum = min(zero_minimum, *(G.price(physical, a) for a in replay.ambient))
    need(zero_minimum == 3, "all projection-zero terms cost at least2")
    data = certificate["families"]
    check_family_keys(data)
    floors = []
    for r in data:
        S, ks = replay.chart(tuple((a,) for a in r["A"]) + (tuple(r["J"]),))
        T, kt = replay.chart(tuple((b,) for b in r["B"]))
        edges = replay.edges(S, T)
        refs = r["covers"]
        need(isinstance(refs, list) and all(type(i) is int and 0 <= i < len(library) for i in refs), "strict integer cover-library references")
        covers = [library[i] for i in refs]
        need(len(covers) == len(edges) and {c["level"] for c in covers} == set(edges), "every positive family threshold covered once")
        bounds = [replay.cover(c, S, T, ks, kt, edges[c["level"]]) for c in covers]
        slack = (0, 1) if len(r["J"]) == 1 and r["J"][0] in F_AXES else (0,)
        for e in slack:
            m = 57+ks+kt+e
            bound = 2*m+220-sum(min(m, m-57+k, cap if cap is not None else m) for k, cap in bounds)
            need(bound >= 297, "every admissible term count excludes296")
            floors.append(bound)
    need(len(floors) == 5440 and min(floors) == 297, "complete final bound accounting")
    canonical_census = canonical_invoice_census(G)
    positive = controls(G, replay)
    return {"status": "PASS", "input_pins": PINS, "certificate_sha256": sha256(raw).hexdigest(),
            "binary_spans": 2213, "ambient_support_strata": len(replay.ambient),
            "families": len(data), "term_count_cases": len(floors), "minimum_floor": min(floors),
            "covers_replayed": replay.cover_count, "rectangle_instances": replay.rectangle_count,
            "projection_zero_minimum": zero_minimum, "controls": positive,
            "canonical_invoice_census": canonical_census,
            "scope": "Selected aligned six-mode bilateral family only, with exact K=RR^T, residual axis2 and all rational finite factorizations in the specified ambient spaces. Independent full geometric replay; no improved decoder or global P112 bound."}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))

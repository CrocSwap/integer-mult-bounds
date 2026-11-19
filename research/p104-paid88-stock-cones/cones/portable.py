#!/usr/bin/env python3
"""Replay all 934 R12 linked nominations and the 139 directed price certificates.

The source-chart extraction and span rules retain the R4 scan, orientation
and band implementations. The sparse integer flow and directed tariff
follow the R8 and R12 chart experiments. The directed power enclosure is
from the predecessor's evaluate_recursive_power.py (Apache-2.0).
"""
from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from fractions import Fraction
from functools import cache, lru_cache
import gzip
from hashlib import sha256
from itertools import product
import json
from math import isqrt
from pathlib import Path
import resource
from time import process_time
from types import SimpleNamespace
import sys

if not __debug__:
    raise SystemExit("Run this replay without Python optimization")

Q = Fraction
HERE = Path(__file__).resolve().parent
LINKED = HERE / "LINKED.json.gz"
EARLIER_NOMINATIONS = HERE / "REVERSALS-single.json.gz"
DIM = 9
FULL = (1 << (1 << DIM)) - 1
MAX_RANK = 10**9
CALLS = 48
SCALE = 10**24
SPACE = frozenset
POINT = frozenset({0})
TARGET = Q("0.00387981257853")
RESIDUAL = (Q("0.379442169416081001142560448506083557440402716"),
            Q("0.379442169416081001142560448506083557440402957"))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def read(path):
    payload = path.read_bytes()
    if path.suffix == ".gz":
        payload = gzip.decompress(payload)
    return json.loads(payload)

def dimension(space):
    count = space.bit_count() if isinstance(space, int) else len(space)
    assert count and not count & (count - 1)
    return count.bit_length() - 1

def sum_spans(a, b):
    return a if b <= a else b if a <= b else frozenset(v ^ w for v in a for w in b)

def write(name, payload):
    archived = read(HERE / name)
    archived.pop("cpu_seconds")
    actual = json.loads(json.dumps(payload))
    actual.pop("cpu_seconds")
    assert actual == archived, "portable replay differs from recorded receipt"


HEAD = "89a67c404226d51028e135de2b9169e9020d57af"
WORD = "c447b6d5ba956fbe40834fe3c1bc69af2f225736f1b97ecd84b57bab9dd283cb"
LAYOUT = "f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7"
LINKED_SHA = "536cf76cb4f307bdaa6fd27cb12db7e673866cf1f8ed3e4d79091f56343d69b8"
EARLIER_SHA = "31f5362aa6faaea81565b22e2ef85520d1f46ca665b242a5930577563164265a"
SCOPE_SHA = "f5087c4d8aa394049eb0ab08adace0d295009306900f29e9db1a07706a10fba2"
APP_SHA = "2a3946fc2fdcbf2b52f6fd4d67bcfb8920b5ef871a556bd939501f384fc82203"

def power_bounds(rank, exponent, bits=128):
    """Enclose rank**exponent by directed integer square roots and products."""
    require(type(rank) is int and 1 <= rank <= MAX_RANK, 'rank is outside 1..10^9')
    require(isinstance(exponent, Q) and 0 < exponent < 1, 'need an exact rational 0 < t < 1')
    require(type(bits) is int and 16 <= bits <= 256, 'bits must be an integer in 16..256')
    scale = 1 << bits
    digits, remainder = divmod(exponent.numerator * scale, exponent.denominator)
    lower = upper = scale
    root_lower = root_upper = rank * scale
    for shift in range(bits - 1, -1, -1):
        root_lower = isqrt(root_lower * scale)
        radicand = root_upper * scale
        root_upper = isqrt(radicand)
        root_upper += root_upper * root_upper < radicand
        if digits & (1 << shift):
            lower = lower * root_lower // scale
            upper = (upper * root_upper + scale - 1) // scale
    if remainder:
        upper = (upper * root_upper + scale - 1) // scale
    return Q(lower, scale), Q(upper, scale)


class Partition:
    def __init__(self):
        self.parents = {}

    def root(self, key):
        parent = self.parents.setdefault(key, key)
        if key != parent:
            self.parents[key] = self.root(parent)
        return self.parents[key]

    def join(self, a, b):
        a, b = self.root(a), self.root(b)
        if a != b:
            self.parents[max(a, b)] = min(a, b)


def components(graph, layout):
    paid = {key: (a, b) for key, a, b in graph["moves"]}
    first = graph["first_output"]
    n = layout["public"]
    assert n == len(graph["initial"]) == len(graph["final"])
    inputs = {~i: chart for i, chart in enumerate(graph["initial"])}
    outputs = {first + i: chart for i, chart in enumerate(graph["final"])}
    original = {(key, 0): a for key, (a, b) in paid.items()}
    original.update({(key, 1): b for key, (a, b) in paid.items()})
    original.update({(key, 1): a for key, a in inputs.items()})
    original.update({(key, 0): b for key, b in outputs.items()})
    partition = Partition()
    clocks = {key: i for i, key in enumerate(graph["schedule"])}
    assert set(clocks) == set(paid) | set(outputs)
    for key, terms in graph["forms"]:
        for donor, _ in terms:
            assert donor in inputs or donor in paid and clocks[donor] < clocks[key]
            assert original[key, 0] == original[donor, 1]
            partition.join((key, 0), (donor, 1))
    vertices = sorted({partition.root(k) for k in original})
    index = {k: i for i, k in enumerate(vertices)}
    vertex = {k: index[partition.root(k)] for k in original}
    labels = [original[k] for k in vertices]
    assert all(labels[vertex[k]] == a for k, a in original.items())
    public = {vertex[key, 0] for key in outputs} | {vertex[key, 1] for key in inputs}
    ends = {key: (vertex[key, 0], vertex[key, 1]) for key in paid}
    from_main = set(layout["live"]) | {x + 112 for x in layout["live"]}
    from_main.update(layout["hosted"]["X2"] + layout["hosted"]["Y2"])
    assert len(from_main) == 400
    main = {vertex[key, 0] for key in outputs if key - first in from_main}
    main.update(vertex[key, 1] for key in inputs if ~key in from_main)
    helper_ends = [(vertex[~i, 1], vertex[first + i, 0]) for i in range(n) if i not in from_main]
    return vertices, labels, ends, public, main, helper_ends


def span(basis):
    vectors = {0}
    for v in basis:
        assert 0 < v < 1 << DIM and v not in vectors
        vectors |= {v ^ w for w in vectors}
    return frozenset(vectors)


def vectors_in(bits):
    while bits:
        bit = bits & -bits
        bits ^= bit
        yield bit.bit_length() - 1


def canon_basis(bits):
    basis, words = [], 1
    for v in vectors_in(bits):
        if words >> v & 1:
            continue
        basis.append(v)
        words |= sum(1 << (w ^ v) for w in vectors_in(words))
    assert words == bits
    return tuple(basis)


@lru_cache(maxsize=12000)
def join(left, right):
    if left & right == left:
        return right
    if left & right == right:
        return left
    out = left
    for v in canon_basis(right):
        if not (out >> v & 1):
            out |= sum(1 << (w ^ v) for w in vectors_in(out))
    return out


@cache
def contents(mask):
    values = []
    while mask:
        last = mask & -mask
        values.append(last.bit_length()-1)
        mask ^= last
    return frozenset(values)


def topo_closure(edges, forced, ranks, spans, fixed, omit=None):
    n = len(spans)
    outgoing = [[] for _ in spans]
    incoming = [[] for _ in spans]
    oriented_edges = []
    for e,(p,t1,t2) in edges.items():
        if omit in e:
            continue
        a,b = e
        if ranks[a]>ranks[b]:
            a,b = b,a
        gap = bool(t1+t2)
        if e in forced:
            assert p and not gap
            a,b,gap = b,a,True
        assert (spans[a]&spans[b]==spans[a]) == (e not in forced)
        outgoing[a].append((b,int(gap)))
        incoming[b].append((a,int(gap)))
        oriented_edges.append((a,b,int(gap),p,t1+t2))
    indegree = list(map(len,incoming))
    ready = deque(v for v,k in enumerate(indegree) if not k)
    order = []
    while ready:
        a = ready.popleft()
        order.append(a)
        for b,_ in outgoing[a]:
            indegree[b] -= 1
            if indegree[b]==0:
                ready.append(b)
    if len(order)<n:
        return None, "strict_cycle"
    low, high = [1]*n,[FULL]*n
    lower, upper = [0]*n,[9]*n
    for v in fixed:
        low[v]=high[v]=spans[v]
        lower[v]=upper[v]=ranks[v]
    for v in order:
        lower[v] = max(lower[v],dimension(low[v]))
        if lower[v]>upper[v] or low[v]&high[v]!=low[v]:
            return None, "small_chart_fails_forward_closure"
        for w,gap in outgoing[v]:
            low[w] = join(low[w],low[v])
            lower[w] = max(lower[w],lower[v]+gap)
    for v in reversed(order):
        upper[v] = min(upper[v],dimension(high[v]))
        if lower[v]>upper[v] or low[v]&high[v]!=low[v]:
            return None, "small_chart_fails_backward_closure"
        for w,gap in incoming[v]:
            high[w] &= high[v]
            upper[w] = min(upper[w],upper[v]-gap)
    return (oriented_edges, lower, upper, low, high), None


def candidate_pairs(edges, ranks, pins, maximum):
    outgoing = [set() for _ in ranks]
    for e in edges:
        a,b = sorted(e,key=lambda v:ranks[v])
        outgoing[a].add(b)
    reachable = [0]*len(ranks)
    for a in sorted(range(len(ranks)),key=lambda v:-ranks[v]):
        for b in outgoing[a]:
            reachable[a] |= 1<<b | reachable[b]
    all_pairs, single_pairs = [], []
    for e,(paid,left,right) in edges.items():
        if not paid or paid>maximum or left or right or set(e)<=pins:
            continue
        a,b = sorted(e,key=lambda v:ranks[v])
        all_pairs.append(e)
        if not any(reachable[c]>>b&1 for c in outgoing[a] if c!=b):
            single_pairs.append(e)
    return sorted(all_pairs),sorted(single_pairs)


class Flow:
    def __init__(self, count):
        self.arcs = [[] for _ in range(count)]
        self.original = []

    def edge(self, a, b, capacity):
        assert a != b and capacity > 0 and isinstance(capacity, int)
        self.original.append((a, b, capacity))
        fa = [b, capacity, len(self.arcs[b])]
        ba = [a, 0, len(self.arcs[a])]
        self.arcs[a].append(fa)
        self.arcs[b].append(ba)

    def levels(self, source):
        level = [-1] * len(self.arcs)
        level[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v, cap, _ in self.arcs[u]:
                if cap and level[v] < 0:
                    level[v] = level[u] + 1
                    queue.append(v)
        return level

    def run(self, source, sink, cap):
        throughput = 0
        while (level := self.levels(source))[sink] >= 0:
            cursor = [0] * len(self.arcs)

            def send(u, allowance):
                if u == sink:
                    return allowance
                outgoing = self.arcs[u]
                while cursor[u] < len(outgoing):
                    item = outgoing[cursor[u]]
                    v, capacity, reverse = item
                    if capacity and level[v] == level[u] + 1:
                        used = send(v, min(allowance, capacity))
                        if used:
                            item[1] -= used
                            self.arcs[v][reverse][1] += used
                            return used
                    cursor[u] += 1
                return 0

            while used := send(source, cap):
                throughput += used
        chosen = {v for v, step in enumerate(level) if step >= 0}
        assert source in chosen and sink not in chosen
        cut = sum(capacity for a, b, capacity in self.original if a in chosen and b not in chosen)
        assert cut == throughput
        return cut, chosen


def band(rank, lo, hi):
    if not (lo <= hi and dimension(lo) <= rank <= dimension(hi)):
        return None
    if dimension(lo) == rank:
        hi = lo
    if dimension(hi) == rank:
        lo = hi
    return rank, lo, hi


@cache
def compatible(a, b, ordinary=False):
    if a[0] == b[0]:
        if not ordinary:
            return False
        lower = sum_spans(a[1], b[1])
        upper = a[2] & b[2]
        return lower <= upper and dimension(lower) <= a[0] <= dimension(upper)
    if a[0] > b[0]:
        a, b = b, a
    ra, la, ua = a
    rb, lb, ub = b
    shared = ua & ub
    if not la <= shared or dimension(shared) < ra:
        return False
    # Maximize the overlap of the rank-ra small chart with the mandatory
    # vectors of the large chart, while extending the small lower subspace.
    overlap = min(dimension(lb & shared), dimension(lb & la) + ra - dimension(la))
    return dimension(lb) + ra - overlap <= rb


class EmptyDomain(Exception):
    pass


def allowed_pair(a, b, ra, rb, allowed):
    if allowed is None:
        return True
    return (ra, rb) in allowed[a, b] if a < b else (rb, ra) in allowed[b, a]


def propagate(domains, adj, dims=None, spans=None, allowed=None, ordinary=False):
    passes = 0
    for iteration in range(100):
        passes += 1
        changed = False
        for v, domain in enumerate(domains):
            if allowed is None and len(domain) == 1 and domain[0][1] == domain[0][2]:
                continue
            narrowed = []
            for here in domain:
                r, lo, hi = here
                for w in adj[v]:
                    possible = [other for other in domains[w] if allowed_pair(v, w, r, other[0], allowed)
                                and compatible(here, other, ordinary)]
                    if not possible:
                        break
                    if all(s <= r for s, _, _ in possible):
                        common = SPACE.intersection(*(p[1] for p in possible))
                        lo = sum_spans(lo, common)
                    if all(s >= r for s, _, _ in possible):
                        combined = POINT
                        for _, _, upper_bound in possible:
                            combined = sum_spans(combined, upper_bound)
                        hi &= combined
                else:
                    new_band = band(r, lo, hi)
                    if new_band is not None:
                        narrowed.append(new_band)
            narrowed = tuple(narrowed)
            if dims is not None:
                assert any(r == dims[v] and lo <= spans[v] <= hi for r, lo, hi in narrowed)
            if not narrowed:
                raise EmptyDomain(v)
            if narrowed != domain:
                changed = True
                domains[v] = narrowed
        if not changed:
            return passes
    raise ValueError("domain propagation did not stabilize")


def domain_state(geo,proof):
    directions,lows,highs,lo,hi=proof
    domains=[tuple(band(r,contents(a),contents(b)) for r in range(x,y+1))
             for x,y,a,b in zip(lows,highs,lo,hi,strict=True)]
    require(all(all(xs) for xs in domains),'nonempty directed subspace intervals')
    allowed={}
    for a,b,gap,p,t in directions:
        high_side=a<b
        i,j=sorted((a,b))
        allowed[i,j]={(x[0],y[0]) for x,y in product(domains[i],domains[j])
                      if (y[0]-x[0] if high_side else x[0]-y[0])>=gap and compatible(x,y,True)}
    passes=propagate(domains,geo.neighbors,allowed=allowed,ordinary=True)
    allowed={e:options&{(x[0],y[0]) for x,y in product(domains[e[0]],domains[e[1]]) if compatible(x,y,True)}
             for e,options in allowed.items()}
    return domains,allowed,passes


def decode(rows):
    return {(a, b): {(v, r): p for v, r, p in zs} for a, b, zs in rows}


def native_census(geo, dims=None):
    ranks=geo.ranks if dims is None else dims
    paid,productive=Counter(),Counter()
    for (a,b),(p,u,d) in geo.edges.items():
        difference=ranks[b]-ranks[a]
        require(not u or difference>0,'production increasing')
        require(not d or difference<0,'production increasing')
        if difference:
            paid[abs(difference)]+=p
            productive[abs(difference)]+=u+d
    return +paid,+productive


def margin(hist, k):
    lo = hi = Fraction()
    for rank, count in hist.items():
        if not count:
            continue
        a, b = power_bounds(rank, 1-k, 192)
        if count < 0:
            a, b = b, a
        lo, hi = lo+count*a, hi+count*b
    return lo, hi


@cache
def value(items):
    return margin(dict(items), TARGET)


def decimal_bounds(bounds, places=18):
    scale = 10 ** places
    lo = bounds[0] * scale
    hi = bounds[1] * scale
    rounded = (lo.numerator // lo.denominator, -(-hi.numerator // hi.denominator))
    return [f"{'-' if x < 0 else ''}{abs(x) // scale}.{abs(x) % scale:0{places}d}" for x in rounded]


def key(cells):
    return tuple(sorted(map(tuple, cells)))


def forced_of(record):
    return key(edge["pair"] for edge in record["forced"])


def network_data(edges, lower, upper, coefficients, constant):
    labels = [(v, r) for v, low in enumerate(lower) for r in range(low+1, upper[v]+1)]
    nodes = {label: index for index, label in enumerate(labels)}
    start, end = len(labels), len(labels)+1
    infinity = 1 + sum(abs(coefficients[v]) for v, _ in labels)
    offset = constant + sum(c*r for c, r in zip(coefficients, lower, strict=True))
    arcs = []
    for index, (v, r) in enumerate(labels):
        c = coefficients[v]
        if c > 0:
            arcs.append((index, end, c))
        elif c < 0:
            arcs.append((start, index, -c))
            offset += c
        if (v, r-1) in nodes:
            arcs.append((index, nodes[v, r-1], infinity))
    for a, b, gap, _, _ in edges:
        for r in range(lower[a]+1, upper[a]+1):
            if r+gap > lower[b]:
                arcs.append((nodes[a, r], nodes[b, r+gap], infinity))
    return labels, start, end, infinity, offset, arcs


def flow_floor(edges, lower, upper, coefficients, constant):
    labels, start, end, infinity, offset, arcs = network_data(edges, lower, upper, coefficients, constant)
    flow = Flow(end+1)
    positions = []
    for a, b, capacity in arcs:
        positions.append(len(flow.arcs[a]))
        flow.edge(a, b, capacity)
    cut, chosen = flow.run(start, end, infinity)
    assert cut < infinity
    support = []
    for i, ((a, _, capacity), index) in enumerate(zip(arcs, positions, strict=True)):
        sent = capacity - flow.arcs[a][index][1]
        if sent:
            support.append((i, sent))
    trial = lower.copy()
    for i, (v, _) in enumerate(labels):
        if i in chosen:
            trial[v] += 1
    assert offset + cut == constant + sum(c*r for c, r in zip(coefficients, trial, strict=True))
    assert all(trial[a] + gap <= trial[b] for a, b, gap, _, _ in edges)
    result = {"floor": offset+cut, "flow": support}
    assert replay_flow(edges, lower, upper, coefficients, constant, result) == offset+cut
    return result, trial


def replay_flow(edges, lower, upper, coefficients, constant, result):
    _, start, end, _, offset, arcs = network_data(edges, lower, upper, coefficients, constant)
    balances = [0] * (end+1)
    prior_id = -1
    for i, sent in result["flow"]:
        assert type(i) is type(sent) is int and prior_id < i < len(arcs)
        a, b, capacity = arcs[i]
        assert 0 < sent <= capacity
        balances[a] -= sent
        balances[b] += sent
        prior_id = i
    assert not any(balances[:start]) and -balances[start] == balances[end]
    floor = offset + balances[end]
    assert floor == result["floor"]
    return floor


def directed_cap(baseline, floor):
    return CALLS * (baseline - Q(floor, SCALE))


def diagnostic_limit():
    resource.setrlimit(resource.RLIMIT_AS, (2048*1024**2, 2048*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU, (295, 300))
    sys.setrecursionlimit(5000)


def old_roster(geo):
    """Transfer R11 nominations by paid ID, deduplicating the current endpoint pair."""
    old=read(EARLIER_NOMINATIONS)
    require(old['source_word']=='65bbf7c22efcc66d85b49b3296116dff2af42fa6a481238584c63b088a4a6eb4','prior external bank nominations')
    result={}
    for row in sorted(old['records'],key=lambda q:-Q(q.get('signed_gain_upper','0'))):
        if 'signed_gain_upper' not in row:
            continue
        for slot in row['paid_slots']:
            if slot in geo.paid:
                pair=tuple(sorted(geo.paid[slot]))
                p,ab,ba=geo.edges[pair]
                if p and not (ab or ba) and not set(pair)<=geo.mains:
                    result.setdefault(pair,dict(source_paid=slot,old_score=row['signed_gain_upper'],old_slots=row['paid_slots']))
    return result



weights = {0: (Q(), Q())} | {r: power_bounds(r, 1-TARGET, 192) for r in range(1, 10)}
LO = {r: (a*SCALE).__floor__() for r, (a, b) in weights.items()}
HI = {r: (b*SCALE).__ceil__() for r, (a, b) in weights.items()}


def source():
    assert sha256(LINKED.read_bytes()).hexdigest() == LINKED_SHA
    assert sha256(EARLIER_NOMINATIONS.read_bytes()).hexdigest() == EARLIER_SHA
    assert sha256((HERE / "SOURCE.json").read_bytes()).hexdigest() == SCOPE_SHA
    info = read(HERE / "SOURCE.json")
    assert info["source_head"] == HEAD
    assert info["source_word"] == WORD and info["source_layout"] == LAYOUT
    assert info["linked_archive_sha256"] == LINKED_SHA
    assert info["native_calls"] == CALLS and Q(info["target"]) == TARGET
    assert tuple(Q(info["required_saving"][end]) for end in ("lower", "upper")) == RESIDUAL
    payloads = []
    for filename, pin in (("WORD", WORD), ("LAYOUT", LAYOUT)):
        payload = gzip.decompress((SOURCE_DIR / (filename+".json.gz")).read_bytes())
        assert sha256(payload).hexdigest() == pin
        payloads.append(json.loads(payload))
    graph, layout = payloads
    assert graph["frames"] == layout["frames"] and layout["public"] == 1289
    app_path = SOURCE_DIR / "application.json"
    if not app_path.is_file():
        app_path = SOURCE_DIR / "evidence" / "application.json"
    app_bytes = app_path.read_bytes()
    assert sha256(app_bytes).hexdigest() == APP_SHA
    app = json.loads(app_bytes)
    assert app["word_sha256"] == WORD and app["layout_sha256"] == LAYOUT
    invoice = app["application"]["invoice"]
    assert invoice == info["complete_invoice"]
    bill_paid, bill_targets = (Counter({int(rank): n for rank, n in invoice[name].items()})
                              for name in ("paid", "targets"))
    assert sum(bill_paid.values()) == 283248 and sum(bill_targets.values()) == 52512
    bill_paid.subtract(bill_targets)
    low, high = margin(bill_paid, TARGET)
    assert RESIDUAL[0] <= low <= high <= RESIDUAL[1]

    vertices, labels, paid, _, mains, helpers = components(graph, layout)
    assert len(paid) == 5709 and len(helpers) == 889
    atlas = list(map(span, graph["frames"]))
    spans = [atlas[chart] for chart in labels]
    ranks = list(map(dimension, spans))
    edges = defaultdict(lambda: [0,0,0])
    inventory = defaultdict(lambda: ([],[],[]))
    neighbors = [set() for _ in vertices]
    for family, rows in ((0, paid), (1, dict(enumerate(helpers)))):
        for slot, (a,b) in rows.items():
            edge = min(a,b), max(a,b)
            assert a != b and ranks[a] != ranks[b]
            if family:
                assert spans[a] < spans[b]
            else:
                assert spans[a] < spans[b] or spans[b] < spans[a]
            mode = family if a < b or not family else 2
            edges[edge][mode] += 1
            inventory[edge][mode].append(slot)
            neighbors[a].add(b)
            neighbors[b].add(a)
    geo = SimpleNamespace(paid=paid, edges=dict(edges), inventory=inventory,
                          labels=labels, ranks=ranks, mains=mains, neighbors=neighbors)
    inventory_counts = native_census(geo)
    assert json.loads(json.dumps(dict(zip(("paid", "targets"), inventory_counts)))) == info["source_native"]
    net = Counter(inventory_counts[0])
    net.subtract(inventory_counts[1])
    baseline = margin(net, TARGET)
    assert decimal_bounds(baseline, 39) == info["signed_native_cost_before_per_call"]
    archive = read(LINKED)
    assert archive["source_word"] == WORD and archive["source_layout"] == LAYOUT
    prior = {forced_of(row): row for row in archive["individual_replays"]}
    archived = [key(case) for case in archive["geometry_survivors"]]
    remaining = [(i, case) for i, case in enumerate(archived) if case not in prior]
    assert len(prior) == 66 and len(remaining) == 73
    assert json.loads(json.dumps(remaining)) == info["unpriced_cones"]
    return geo, [sum(1 << v for v in space) for space in spans], baseline[1], RESIDUAL[0], prior, remaining, info


def closure(geo, spans, cells):
    return topo_closure(geo.edges, frozenset(cells), geo.ranks, spans, geo.mains)


def exact_roster(geo):
    all_pairs, _ = candidate_pairs(geo.edges, geo.ranks, geo.mains, 10000)
    offcenter = [edge for edge in all_pairs if not {117, 288, 304} & {geo.labels[v] for v in edge}]
    assert len(offcenter) == 3726
    at = defaultdict(list)
    for edge in offcenter:
        for v in edge:
            if v not in geo.mains:
                at[v].append(edge)
    offcenter = set(offcenter)
    choices = {tuple(sorted((first, second)))
               for first in old_roster(geo) if first in offcenter
               for v in first for second in at[v] if first != second}
    return sorted(choices, key=lambda group: (sum(geo.edges[e][0] for e in group), group))


def check_directions(geo, spans, cells, proof):
    dirs, lows, highs, lower, upper = proof
    assert len(dirs) == len(geo.edges)
    observed = set()
    for a, b, strict, paid, productive in dirs:
        edge = min(a, b), max(a, b)
        assert edge not in observed
        observed.add(edge)
        p, increasing, decreasing = geo.edges[edge]
        assert (paid, productive) == (p, increasing+decreasing)
        if productive:
            assert strict == 1 and (a < b) == bool(increasing)
        elif edge in cells:
            assert strict == 1 and paid and geo.ranks[a] > geo.ranks[b]
        else:
            assert strict == 0 and geo.ranks[a] < geo.ranks[b]
    assert observed == geo.edges.keys()
    for v in geo.mains:
        assert lows[v] == highs[v] == geo.ranks[v]
        assert lower[v] == upper[v] == spans[v]
    return dirs, lows, highs


def certified_coefficients(dirs, lows, highs, initial, mass=False):
    constant = 0
    coeff = [0] * len(initial)
    for a, b, strict, paid, productive in dirs:
        first, last = max(strict, lows[b]-highs[a]), highs[b]-lows[a]
        assert 0 <= first <= last < 10
        if mass:
            slope, intercept = paid-productive, 0
        else:
            table = {r: paid*LO[r]-productive*HI[r] for r in range(first, last+1)}
            if first == last:
                slope = 0
            elif paid >= productive:
                slope = (table[last]-table[first])//(last-first)
            else:
                point = max(first, min(last-1, abs(initial[a]-initial[b])))
                slope = table[point+1]-table[point]
            intercept = min(q-slope*r for r, q in table.items())
            assert all(r*slope+intercept <= q for r, q in table.items())
        coeff[a] -= slope
        coeff[b] += slope
        constant += intercept
    return coeff, constant


def integer_local_price(geo, proof, tax, inherited, exact_endpoints):
    domains, allowed, _ = domain_state(geo, proof)
    vertices = [{r: 0 for r, _, _ in states} for states in domains]
    separate_edges = 0
    used = set()
    for (a, b), (paid, pos, neg) in geo.edges.items():
        left, right = vertices[a], vertices[b]
        permitted = [(r, s) for r, s in allowed[a,b] if r in left and s in right]
        assert {r for r, _ in permitted} == left.keys()
        assert {s for _, s in permitted} == right.keys()
        table = {}
        for r, s in permitted:
            distance = abs(r-s)
            table[r,s] = paid*LO[distance]-(pos+neg)*HI[distance]-(paid-pos-neg)*distance*tax
        if len(left) == len(right) == 1:
            separate_edges += next(iter(table.values()))
        elif len(left) == 1:
            for (_, s), q in table.items():
                right[s] += q
        elif len(right) == 1:
            for (r, _), q in table.items():
                left[r] += q
        else:
            used.add((a, b))
            msg = inherited.get((a, b), {})
            if exact_endpoints:
                assert msg.keys() == ({(a,r) for r in left} | {(b,s) for s in right})
            assert all(type(number) is int for number in msg.values())
            for r in left:
                left[r] += msg.get((a, r), 0)
            for s in right:
                right[s] += msg.get((b, s), 0)
            separate_edges += min(q-msg.get((a, r), 0)-msg.get((b, s), 0)
                                  for (r, s), q in table.items())
    if exact_endpoints:
        assert used == inherited.keys()
    return separate_edges + sum(min(q.values()) for q in vertices)


def read_lines(path):
    with path.open() as raw:
        return list(map(json.loads, raw))


def main():
    diagnostic_limit()
    began = process_time()
    geo, spans, baseline, residual, old, unpriced, source_info = source()
    incumbent_paid, incumbent_targets = native_census(geo)
    assert sum(incumbent_paid.values()) == 5709 and sum(incumbent_targets.values()) == 889
    source_native_net = Counter(incumbent_paid)
    source_native_net.subtract(incumbent_targets)
    incumbent_mass = sum(r*q for r, q in source_native_net.items())
    edge_mass = sum((p-u-d)*abs(geo.ranks[a]-geo.ranks[b])
                    for (a,b),(p,u,d) in geo.edges.items())
    assert edge_mass == incumbent_mass
    assert value(tuple(sorted(source_native_net.items())))[1] == baseline

    geometry = Counter()
    survivors = []
    archived = read(LINKED)
    for cells in exact_roster(geo):
        proof, why = closure(geo, spans, cells)
        if proof is None:
            geometry[why] += 1
        else:
            geometry["passed_anchor_closure"] += 1
            survivors.append(cells)
    assert survivors == [key(c) for c in archived["geometry_survivors"]]
    assert all(geometry[tag] == archived["counts"][tag] for tag in geometry)
    assert sum(geometry.values()) == archived["branch_count"] == 934
    print("Geometry roster replayed", dict(geometry), flush=True)

    a_path = HERE / "AFFINE.ndjson"
    t_paths = sorted(HERE.glob("TIGHT-*-OF-*.ndjson"))
    affine_rows = read_lines(a_path)
    assert [row["position"] for row in affine_rows] == [-1] + [i for i, _ in unpriced]
    aff = {row["position"]: row for row in affine_rows}
    audit = []
    discarded = set()
    for pos, cells in [(-1, tuple())] + unpriced:
        row = aff[pos]
        assert key(row["pairs"]) == cells
        proof, why = closure(geo, spans, cells)
        assert proof is not None and why is None
        dirs, lows, highs = check_directions(geo, spans, cells, proof)
        coeff, constant = certified_coefficients(dirs, lows, highs, geo.ranks)
        floor = replay_flow(dirs, lows, highs, coeff, constant, row["affine_price_certificate"])
        cap = directed_cap(baseline, floor)
        assert row["optimistic_48_call_upper"] == decimal_bounds((cap,cap), 34)[1]
        if pos == -1:
            assert cap >= 0
            corrupt = dict(row["affine_price_certificate"])
            corrupt["floor"] += 1
            try:
                replay_flow(dirs, lows, highs, coeff, constant, corrupt)
            except AssertionError:
                pass
            else:
                raise AssertionError("Perturbed flow floor accepted")
        elif cap < residual:
            assert cap < 0
            discarded.add(pos)
            audit.append({"position": pos, "pairs": cells, "paid_slots": row["paid_slots"],
                          "method": "affine_exact_flow", "upper": row["optimistic_48_call_upper"]})
    assert len(discarded) == 17
    print("Affine certificates replayed", len(aff), "closed", len(discarded), flush=True)

    inherited_with_messages = {}
    old_upper = []
    for cells, row in old.items():
        proof, why = closure(geo, spans, cells)
        assert proof is not None and why is None
        dirs, lows, highs = check_directions(geo, spans, cells, proof)
        coeff, constant = certified_coefficients(dirs, lows, highs, geo.ranks, mass=True)
        certificate, _ = flow_floor(dirs, lows, highs, coeff, constant)
        mass = certificate["floor"]
        assert incumbent_mass == row["signed_rank_mass_before"]
        assert mass == row["signed_rank_mass_floor"]
        cycle, = row["cycles"]
        inherited_with_messages[cells] = messages = decode(cycle["integer_potentials"])
        tax = int(Q(cycle["mass_tax"])*SCALE)
        floor = integer_local_price(geo, proof, tax, messages, exact_endpoints=True) + tax*mass
        cap = directed_cap(baseline, floor)
        assert floor == cycle["integer_cost_bound"] and cap < 0
        assert decimal_bounds((cap,cap), 34)[1] == row["best_directed_upper"] == cycle["signed_gain_upper"]
        old_upper.append(row["best_directed_upper"])
    print("Inherited dual certificates replayed", len(old), flush=True)

    tightened = [row for p in t_paths for row in read_lines(p)]
    assert len(set(row["position"] for row in tightened)) == len(tightened) == 56
    assert {r["position"] for r in tightened} == {i for i, _ in unpriced} - discarded
    assert all(row["status"] == "excluded_by_reused_integer_potentials" for row in tightened)
    for row in tightened:
        pos = row["position"]
        cells = key(row["pairs"])
        proof, why = closure(geo, spans, cells)
        assert cells == key(aff[pos]["pairs"]) and proof is not None and why is None
        dirs, lows, highs = check_directions(geo, spans, cells, proof)
        coeff, constant = certified_coefficients(dirs, lows, highs, geo.ranks, mass=True)
        mass = replay_flow(dirs, lows, highs, coeff, constant, aff[pos]["rank_mass_certificate"])
        assert mass == row["mass_floor"]
        cycle, = row["cycles"]
        inherited_case = key(cycle["from_inherited_pairs"])
        tax = int(Q(cycle["mass_tax"])*SCALE)
        floor = integer_local_price(geo, proof, tax, inherited_with_messages[inherited_case], exact_endpoints=False) + tax*mass
        cap = directed_cap(baseline, floor)
        assert cap < 0
        assert floor == cycle["integer_lower"]
        assert decimal_bounds((cap,cap), 34)[1] == cycle["certified_48_call_upper"] == row["certified_48_call_upper"]
        audit.append({"position": pos, "pairs": cells, "paid_slots": row["paid_slots"],
                      "chart_pairs": row["chart_pairs"], "method": "reused_exact_potentials",
                      "inherited_pairs": inherited_case, "upper": row["certified_48_call_upper"]})
    strongest = max(audit, key=lambda row: Q(row["upper"]))
    result = dict(status="certified_scoped_exclusion", source_head=source_info["source_head"],
                  source_word=source_info["source_word"], source_layout=source_info["source_layout"],
                  linked_archive_sha256=source_info["linked_archive_sha256"],
                  source_invoice_sha256=source_info["source_invoice_sha256"],
                  server_receipt=source_info["server_receipt"], target=source_info["target"],
                  required_saving=source_info["required_saving"], calls=CALLS,
                  geometry_roster=archived["branch_count"], geometry_counts=geometry,
                  rechecked_inherited_ceilings=len(old), strongest_inherited_48_call_upper=max(old_upper,key=Q),
                  rechecked_new_ceilings=len(audit), strongest_new=strongest,
                  maximum_48_call_upper=max([strongest["upper"]]+old_upper,key=Q),
                  remaining_saved_positions=sorted({i for i, _ in unpriced}-{r["position"] for r in audit}),
                  priced_affine=len(discarded), priced_reused=len(tightened), lp_solver_calls=0,
                  literal_candidates=0, source_signed_rank_mass=incumbent_mass,
                  content_hashes={p.name: sha256(p.read_bytes()).hexdigest()
                                  for p in [HERE/"SOURCE.json",a_path,*t_paths]},
                  controls={"source_native_histogram_matches_literal_primal_and_adjoint_census": True,
                            "nomination_indices_match_independent_regeneration": True,
                            "all_ordered_productive_directions_and_physical_chart_pins_checked": True,
                            "zero_reversal_control_contains_replayed_source": True,
                            "perturbed_flow_floor_rejected": True},
                  cpu_seconds=process_time()-began,
                  cones=sorted(audit,key=lambda row:row["position"]))
    write("VERIFIED.json", result)
    print("All directed bounds replayed", len(audit), strongest, flush=True)



if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=HERE.parent / "sources")
    SOURCE_DIR = parser.parse_args().source_dir
    main()

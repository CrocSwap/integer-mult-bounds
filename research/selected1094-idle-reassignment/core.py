"""Source-bound selected-word axis assignment; exact integer checks, no solver.

Gareth Davidson, substantial OpenAI Codex assistance; Apache-2.0.
The input and move lineage is credited in README.md and PROOF.md.
"""
import collections
import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
REPLAY = 'research/community-frontier1094-audit/selected-replay.tar.gz'
SOURCE = 'research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz'
DATA = 'research/complex-t16-rare-pattern-exchanges/data/'
ASSEMBLY = 'research/community-frontier1094-audit/ASSEMBLY.json'
ENGINES = 'research/complex-k492-owner-repair/vendor/multicold/engines/'
BIT = 'research/gauge44-slots-t16/inputs/PR589-EXPECTED.json'
OLD_BIT = 'research/complex-k492-owner-repair/vendor/multicold/inputs/PR543-EXPECTED.json'
GEOMETRY = 'research/split-centres-global/proofs/INHERITED-COMPLEX-GEOMETRY.txt'
INPUTS = {REPLAY, SOURCE, ASSEMBLY, BIT, OLD_BIT, GEOMETRY, *(DATA+n for n in ('SPEC.json', 'PLAN.json', 'OWNERS.json.gz')),
          *(ENGINES+n+'.py' for n in ('moment', 'base_two_moment', 'outer'))}
MEMBERS = ('hosted/IDLE-REMAINDER-FRAMES.json.gz',
           'base/work/complex-nine-native/DATA-PHASES.json',
           'audit/OWNERS-AND-PROFILE.json')
CAP = 51


def need(condition, message):
    if not condition:
        raise ValueError(message)


def pairs(items):
    out = {}
    for k, v in items:
        need(k not in out, 'duplicate JSON key: '+k)
        out[k] = v
    return out


def decode(raw):
    def bad(x):
        raise ValueError('nonfinite JSON: '+x)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad)


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return decode(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def canonical(x):
    # JSON object keys are strings. Normalize before sorting so in-memory integer
    # histograms and their JSON round trips have exactly the same canonical bytes.
    def normalize(v):
        if isinstance(v, dict):
            out = {}
            for key, value in v.items():
                need(type(key) in (str, int), 'unsupported JSON object key')
                name = str(key)
                need(name not in out, 'colliding JSON object keys')
                out[name] = normalize(value)
            return out
        if isinstance(v, (tuple, list)):
            return [normalize(a) for a in v]
        return v
    return json.dumps(normalize(x), sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def write(path, x):
    Path(path).write_text(json.dumps(x, indent=2, sort_keys=True, allow_nan=False)+'\n')


def sources(root=ROOT):
    rows = read(PACKAGE/'SOURCES.json')['files']
    active = [x for x in rows if x['usage'] == 'input']
    need(len(active) == len(INPUTS) and {x['path'] for x in active} == INPUTS,
         'missing, extra or duplicate live source pin')
    for x in active:
        need(sha(root/x['path']) == x['sha256'], 'source drift: '+x['path'])
    return {x['path']: x['sha256'] for x in active}


def inputs(root=ROOT):
    with tarfile.open(root/REPLAY) as archive:
        names = archive.getnames()
        need(len(names) == len(set(names)), 'duplicate archive member')
        objs = []
        for name in MEMBERS:
            raw = archive.extractfile('candidate/strict/global/'+name).read()
            objs.append(decode(gzip.decompress(raw) if name.endswith('.gz') else raw))
    frames, phases, audit = objs
    owners = read(root/(DATA+'OWNERS.json.gz'))
    return frames, phases, audit, owners


def dot(v, w):
    return (v & w).bit_count() & 1


def label(row):
    return row['replica'], row['port'], row['child']


def eligible_groups(frames, owners):
    roles = {(r['owner_replica'], r['port'], r['child']) for r in owners}
    need(len({label(r) for r in frames}) == len(frames), 'duplicate frame label')
    groups = collections.defaultdict(list)
    for r in frames:
        if r['rank'] == 48 and r['hosted'] == r['pending_offset'] == 0 and label(r) not in roles:
            groups[r['replica'], r['port']].append(r)
    return dict(sorted(groups.items()))


def context(rows, recipe):
    """Enumerate the declared domains and every pairwise orthogonality constraint."""
    k = len(rows)
    need(1 <= k <= 4, 'outside the stated group-size domain')
    stage = [int(s[n]) for s in recipe['stage_alignment']
             for n in ('entry_X', 'entry_Y', 'exit_X', 'exit_Y')]
    stage.append(int(recipe['terminal_Y_translation']))
    translations = [int(recipe['idle_children'][r['child']]['translation_after']) for r in rows]
    vertices = [(i, int(v)) for i, r in enumerate(rows) for v in r['orthogonal_axes']]
    need(len(vertices) == 48*k, 'source child rank is not its axis count')
    need(all(0 < v < 1 << 73 and dot(v, v) == 1 for _, v in vertices), 'invalid source axis')
    domains = []
    for i, v in vertices:
        d = {i}
        if all(dot(v, s) == 0 for s in stage+[translations[i]]):
            d.update(j for j in range(k) if dot(v, translations[j]) == 0)
        domains.append(d)
    adjacency = [set() for _ in vertices]
    for i, (ci, v) in enumerate(vertices):
        for j, (cj, w) in enumerate(vertices[:i]):
            if dot(v, w):
                need(ci != cj, 'source frame is not orthonormal')
                adjacency[i].add(j)
                adjacency[j].add(i)
    # Logically forced colours; the original assignment is always a witness.
    stack = [i for i, d in enumerate(domains) if len(d) == 1]
    while stack:
        i = stack.pop()
        colour = next(iter(domains[i]))
        for j in adjacency[i]:
            if len(domains[j]) == 1:
                need(colour not in domains[j], 'forced-colour conflict')
            elif colour in domains[j]:
                domains[j].remove(colour)
                if len(domains[j]) == 1:
                    stack.append(j)
    todo = {i for i, d in enumerate(domains) if len(d) > 1}
    components = []
    while todo:
        i = min(todo)
        todo.remove(i)
        stack, comp = [i], []
        while stack:
            i = stack.pop()
            comp.append(i)
            neighbours = adjacency[i] & todo
            todo.difference_update(neighbours)
            stack.extend(sorted(neighbours))
        comp.sort()
        need(all(domains[v] == set(range(k)) for v in comp), 'nonuniform component domains')
        need(all(b in adjacency[a] for a, b in itertools.combinations(comp, 2)),
             'component is not a clique')
        need(len({vertices[v][1] for v in comp}) == 1, 'component axes differ')
        components.append(comp)
    fixed = [sum(d == {i} for d in domains) for i in range(k)]
    need(len(set(fixed)) == 1, 'asymmetric fixed counts')
    return dict(children=[r['child'] for r in rows], vertices=vertices,
                domains=[sorted(d) for d in domains], components=components,
                fixed=fixed[0], k=k)


def motif(ctx):
    counts = collections.Counter(map(len, ctx['components']))
    return ctx['k'], ctx['fixed'], tuple(sorted(counts.items()))


def upper_prefixes(k, fixed, counts):
    return [min(CAP*s, fixed*s+sum(min(q, s)*n for q, n in counts)) for s in range(k+1)]


def optimum(ctx):
    k, f, counts = motif(ctx)
    upper = upper_prefixes(k, f, counts)
    target = [upper[i+1]-upper[i] for i in range(k)]
    need(target == sorted(target, reverse=True) and 1 <= min(target) <= max(target) <= CAP,
         'prefix differences are not a legal rank vector')
    need(sum(target) == 48*k, 'rank mass')
    destinations = [d[0] if len(d) == 1 else None for d in ctx['domains']]
    left = [r-f for r in target]
    for comp in sorted(ctx['components'], key=lambda x: (-len(x), x)):
        colours = sorted(range(k), key=lambda i: (-left[i], i))[:len(comp)]
        need(all(left[i] > 0 for i in colours), 'attaining assignment failed')
        for v, colour in zip(comp, colours):
            need(colour in ctx['domains'][v], 'invalid attaining colour')
            destinations[v] = colour
            left[colour] -= 1
    need(not any(left), 'unfilled target counts')
    return target, destinations


def derive(frames, phases, owners):
    groups = eligible_groups(frames, owners)
    recipes = {r['port']: r for r in phases['recipes']}
    contexts, aliases = [], {}
    motifs = collections.Counter()
    edits = {}
    groups_out = []
    for key, rows in groups.items():
        signature = (key[1], tuple((r['child'], tuple(map(int, r['orthogonal_axes']))) for r in rows))
        if signature not in aliases:
            ctx = context(rows, recipes[key[1]])
            target, dest = optimum(ctx)
            ctx.update(target=target, destinations=dest)
            aliases[signature] = len(contexts)
            contexts.append(ctx)
        ctx = contexts[aliases[signature]]
        motifs[motif(ctx)] += 1
        # Retain each child's surviving axes in order, then append arrivals.
        final = [[] for _ in rows]
        incoming = [[] for _ in rows]
        for (src, v), dst in zip(ctx['vertices'], ctx['destinations']):
            (final if src == dst else incoming)[dst].append(v)
        final = [x+y for x, y in zip(final, incoming)]
        for r, axes in zip(rows, final):
            edits[label(r)] = axes
        groups_out.append(dict(key=list(key), children=ctx['children'], ranks=ctx['target'],
                               destinations=ctx['destinations']))
    result = copy.deepcopy(frames)
    for r in result:
        if label(r) in edits:
            r['orthogonal_axes'] = edits[label(r)]
            r['rank'] = len(edits[label(r)])
    table = []
    for (k, f, counts), multiplicity in sorted(motifs.items()):
        upper = upper_prefixes(k, f, counts)
        table.append(dict(k=k, fixed=f, cliques=dict(counts), groups=multiplicity,
                          prefix_bounds=upper[1:], ranks=[upper[i+1]-upper[i] for i in range(k)]))
    return result, groups_out, table, contexts


def legacy_flattened_operator(frames, recipe):
    """Reproduce the inherited abstract scalar check, NOT the physical operator.

    It erases family labels and models address translations as Fourier shifts.
    stream_check.py supplies the separating physical counterexample.
    """
    shift = 0
    for s in recipe['stage_alignment']:
        for name in ('entry_X', 'entry_Y', 'exit_X', 'exit_Y'):
            shift ^= int(s[name])
    constant = 0
    linear = [0]*73
    quadratic = collections.Counter()
    for r in sorted(frames, key=lambda r: r['child']):
        for v in map(int, r['orthogonal_axes']):
            bit = dot(shift, v)
            constant += bit
            support = [i for i in range(73) if v >> i & 1]
            for i in support:
                linear[i] += 1-2*bit
            for i, j in itertools.combinations(support, 2):
                quadratic[i, j] += 2
        shift ^= int(recipe['idle_children'][r['child']]['translation_after'])
    shift ^= int(recipe['terminal_Y_translation'])
    return shift, constant % 4, [x % 4 for x in linear], sorted((i, j, v % 4) for (i, j), v in quadratic.items() if v % 4)


def check_assignment(old, new, phases, owners):
    """Independent of component reduction, target formula and witness construction."""
    before = {label(r): r for r in old}
    after = {label(r): r for r in new}
    need(len(before) == len(old) == len(after) == len(new) and before.keys() == after.keys(), 'frame inventory')
    groups = eligible_groups(old, owners)
    eligible = {label(r) for rows in groups.values() for r in rows}
    recipes = {r['port']: r for r in phases['recipes']}
    for key, r in before.items():
        s = after[key]
        if key not in eligible:
            need(r == s, 'ineligible frame changed')
        need(canonical({k: v for k, v in r.items() if k not in ('rank', 'orthogonal_axes')}) ==
             canonical({k: v for k, v in s.items() if k not in ('rank', 'orthogonal_axes')}), 'frame metadata changed')
        axes = list(map(int, s['orthogonal_axes']))
        need(type(s['rank']) is int and s['rank'] == len(axes) <= CAP, 'rank/guard')
        need(all(dot(v, w) == (i == j) for i, v in enumerate(axes) for j, w in enumerate(axes)), 'nonorthonormal child')
    moves = 0
    changed = 0
    for (rep, port), rows in groups.items():
        recipe = recipes[port]
        all_translations = [int(s[n]) for s in recipe['stage_alignment']
                            for n in ('entry_X', 'entry_Y', 'exit_X', 'exit_Y')]
        all_translations += [int(recipe['terminal_Y_translation'])]
        all_translations += [int(c['translation_after']) for c in recipe['idle_children']]
        old_multiset = collections.Counter(v for r in rows for v in map(int, r['orthogonal_axes']))
        new_multiset = collections.Counter(v for r in rows for v in map(int, after[label(r)]['orthogonal_axes']))
        need(old_multiset == new_multiset, 'group axis multiset changed')
        for r in rows:
            old_axes = set(map(int, r['orthogonal_axes']))
            new_axes = set(map(int, after[label(r)]['orthogonal_axes']))
            changed += old_axes != new_axes
            moves += len(old_axes-new_axes)
            # Stronger than the declared endpoint-only dot-product restriction.
            need(all(dot(v, t) == 0 for v in old_axes ^ new_axes for t in all_translations),
                 'moved axis violates the declared dot-product restriction')
    for fr in (old, new):
        families = collections.defaultdict(collections.Counter)
        for r in fr:
            families[r['family']].update(map(int, r['orthogonal_axes']))
        need(all(max(c.values(), default=0) <= 1 for c in families.values()), 'X2 family collision')
    old_ports, new_ports = collections.defaultdict(list), collections.defaultdict(list)
    for r in old:
        old_ports[r['replica'], r['port']].append(r)
    for r in new:
        new_ports[r['replica'], r['port']].append(r)
    for key in old_ports:
        need(legacy_flattened_operator(old_ports[key], recipes[key[1]]) ==
             legacy_flattened_operator(new_ports[key], recipes[key[1]]),
             'legacy flattened polynomial differs')
    return dict(groups=len(groups), eligible_children=len(eligible), changed_children=changed,
                moved_axis_occurrences=moves, legacy_flattened_groups=len(old_ports), x2_families=len(families))


def profile(old, new, audit):
    p = collections.Counter({int(k): v for k, v in audit['paid_profile'].items()})
    p.subtract(r['rank'] for r in old)
    p.update(r['rank'] for r in new)
    need(all(v >= 0 for v in p.values()), 'negative profile count')
    p = dict(sorted((+p).items()))
    need(sum(r*n for r, n in p.items()) == 73*14336-5120, 'paid mass')
    need(73**2 > 2*max(p)**2, 'halving guard')
    return p

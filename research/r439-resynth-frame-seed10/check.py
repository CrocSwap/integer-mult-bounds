#!/usr/bin/env python3
"""Independent finite frame verifier for the pinned PR952 word (seed 10).

Geometry uses primitive integer row elimination over Q, not modular rank.
Costs are sums over register timelines, not a replay of the producer's gate
loop. DFS rejects a partial assignment as soon as an adjacent chain fails.
The scope fixes gate order/operands, start/final frames and actual COPY frames;
C-frame freedom is a relaxation. This does not check scalar program semantics,
hosting, an asymptotic recurrence, or assert a new kappa.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
from math import gcd, prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/r439-six-wire-boolean/candidate.json.gz'
WORD_SHA = '5c67c7949c07a89ea8394a936a155585d22e6b258997df73e36e7be47fc84cb0'
ENGINE = 'research/complex-k492-owner-repair/vendor/multicold/engines/base_two_moment.py'
ENGINE_SHA = 'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098'
C = Fraction(1733427039589844234749, 10**24)
BASE_PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}


def need(ok, message):
    """Checks remain active with Python -O."""
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def primitive(row):
    """Divide by gcd and choose positive first pivot; preserve rational span."""
    divisor = 0
    for value in row:
        divisor = gcd(divisor, value)
    if not divisor:
        return tuple(row)
    if next(value for value in row if value) < 0:
        divisor = -divisor
    return tuple(value // divisor for value in row)


def remainder(row, basis):
    """Integer cross multiplication eliminates each pivot without division."""
    row = tuple(row)
    for pivot, vector in sorted(basis.items()):
        if row[pivot]:
            coefficient = row[pivot]
            row = primitive(tuple(vector[pivot] * a - coefficient * b
                                  for a, b in zip(row, vector)))
    return row


class Geometry:
    def __init__(self, lines):
        need(lines and all(len(row) == 8 for row in lines), 'eight-dimensional lines')
        need(all(all(type(x) is int for x in row) and any(row) for row in lines),
             'nonzero integer lines')
        self.lines = [tuple(row) for row in lines]
        self.full = (1 << len(lines)) - 1
        self.cache = {0: (0, 0)}

    def close(self, mask):
        need(type(mask) is int and 0 <= mask <= self.full, 'frame mask range')
        if mask not in self.cache:
            basis = {}
            for i in bits(mask):
                row = remainder(self.lines[i], basis)
                if any(row):
                    pivot = next(j for j, value in enumerate(row) if value)
                    basis[pivot] = primitive(row)
            closure = sum(1 << i for i, row in enumerate(self.lines)
                          if not any(remainder(row, basis)))
            need(mask & ~closure == 0, 'closure must contain its generators')
            value = (closure, len(basis))
            self.cache[mask] = value
            self.cache[closure] = value
        return self.cache[mask]

    def dim(self, mask):
        return self.close(mask)[1]

    def choices(self, lower, upper):
        """All flats in [lower, upper], by adjoining one line and closing.

        Every intermediate flat is reached: take its lines one at a time;
        closure of every prefix remains inside that flat and hence upper.
        """
        need(self.close(lower)[0] == lower and self.close(upper)[0] == upper,
             'bounds must be closed')
        need(lower & ~upper == 0, 'inconsistent bounds')
        pending, seen = [lower], {lower}
        while pending:
            frame = pending.pop()
            for line in bits(upper & ~frame):
                new = self.close(frame | (1 << line))[0]
                need(new & ~upper == 0, 'closed upper bound escaped')
                if new not in seen:
                    seen.add(new)
                    pending.append(new)
        return sorted(seen, key=lambda m: (self.dim(m), m))


class Problem:
    def __init__(self, word):
        self.word = word
        need(word['format'] == 'bitE8/1+mut' and word['h'] == 8, 'word format')
        self.v, self.n = word['v'], 2 * word['v'] + word['R']
        need(self.v == len(word['lines']), 'line count')
        self.geometry = geo = Geometry(word['lines'])
        self.frames = []
        for members in word['frames']:
            need(type(members) is list and len(set(members)) == len(members), 'frame members')
            need(all(type(i) is int and 0 <= i < self.v for i in members), 'frame line index')
            mask = sum(1 << i for i in members)
            need(geo.close(mask)[0] == mask, 'catalogue frame not closed')
            self.frames.append(mask)
        self.start = self.decode(word['start'])
        self.final = self.decode(word['final'])
        need(len(self.start) == self.n == len(self.final), 'register frame count')
        self.ret = word['ret']
        need(len(self.ret) == len(set(self.ret)) and all(2*self.v <= q < self.n for q in self.ret),
             'retained registers')
        self.gates, self.original, self.keys = [], [], []
        for phase in 'DABC':
            for index, gate in enumerate(word[phase]):
                need(len(gate) == 3 and type(gate[2]) is list, 'gate schema')
                frame, target, sources = gate
                registers = [target, *sources]
                need(sources and all(type(r) is int and 0 <= r < self.n for r in registers),
                     'gate register range')
                need(len(registers) == len(set(registers)), 'repeated gate participant')
                self.gates.append(registers)
                self.keys.append((phase, index))
                self.original.extend(self.decode([frame]))
        self.scatter = len(word['D']) + len(word['A'])
        self.chains = [[] for _ in range(self.n)]
        for index, registers in enumerate(self.gates):
            for r in registers:
                self.chains[r].append(index)
        self.pre = [next((g for g in reversed(chain) if g < self.scatter), None)
                    for chain in self.chains]
        self.pin = {r: self.pre_frame(r, self.original) for r in self.ret}
        self.check_scatter(self.original)
        self.lower, self.upper = self.bounds()
        self.options = {g: geo.choices(lo, hi) for g, (lo, hi) in
                        enumerate(zip(self.lower, self.upper)) if lo != hi}
        need(all(self.original[g] in choices for g, choices in self.options.items()),
             'original frame missing from exhaustive closed-frame choices')
        self.validate(self.original)
        need(all(self.lower[g] == self.upper[g] == 0 for g, key in enumerate(self.keys)
                 if key[0] == 'D'), 'D gates must be fixed at zero')
        self.components = self.connected_components()
        self.before, self.after = [[] for _ in self.gates], [[] for _ in self.gates]
        for r, chain in enumerate(self.chains):
            for j, gate in enumerate(chain):
                self.before[gate].append((chain[j-1], None) if j else (None, self.start[r]))
                self.after[gate].append((chain[j+1], None) if j+1 < len(chain) else (None, self.final[r]))

    def decode(self, indices):
        need(all(type(i) is int and 0 <= i < len(self.frames) for i in indices), 'frame index')
        return [self.frames[i] for i in indices]

    def pre_frame(self, register, assignment):
        gate = self.pre[register]
        return self.start[register] if gate is None else assignment[gate]

    def check_scatter(self, assignment):
        need(all(self.pre_frame(r, assignment) == frame for r, frame in self.pin.items()),
             'actual pre-scatter COPY frame differs from original pin')
        need(all(self.pre_frame(r, assignment) == 0 for r in range(self.v, 2*self.v)),
             'target frame is not zero at scatter')

    def bounds(self):
        lower, current = [], list(self.start)
        for g, registers in enumerate(self.gates):
            if g == self.scatter:
                for r, frame in self.pin.items():
                    need(current[r] & ~frame == 0, 'least frame exceeds COPY pin')
                    current[r] = frame
            union = 0
            for r in registers:
                union |= current[r]
            frame = self.geometry.close(union)[0]
            lower.append(frame)
            for r in registers:
                current[r] = frame
        upper, current = [None] * len(self.gates), list(self.final)
        for g in reversed(range(len(self.gates))):
            if g == self.scatter - 1:
                for r in range(self.v, 2*self.v):
                    current[r] = 0
                for r, frame in self.pin.items():
                    need(frame & ~current[r] == 0, 'COPY pin exceeds post-scatter upper frame')
                    current[r] = frame
            intersection = self.geometry.full
            for r in self.gates[g]:
                intersection &= current[r]
            upper[g] = intersection
            for r in self.gates[g]:
                current[r] = intersection
        return lower, upper

    def connected_components(self):
        """Conservatively retain adjacency across scatter, matching its fixed word.

        A fixed gate breaks coupling: both legality and cost have fixed
        endpoints there. Retaining extra scatter edges can only merge searches.
        """
        adjacency = {g: set() for g in self.options}
        for chain in self.chains:
            for left, right in zip(chain, chain[1:]):
                if left in adjacency and right in adjacency:
                    adjacency[left].add(right)
                    adjacency[right].add(left)
        unseen, result = set(adjacency), []
        while unseen:
            pending, component = [min(unseen)], set()
            while pending:
                gate = pending.pop()
                if gate in component:
                    continue
                component.add(gate)
                pending.extend(adjacency[gate] - component)
            unseen -= component
            result.append(sorted(component))
        return result

    def local_profile(self, assignment, registers):
        """Every climb appears exactly once on its register; COPY cost is separate."""
        profile = Counter()
        for r in registers:
            previous = self.start[r]
            for frame in [*(assignment[g] for g in self.chains[r]), self.final[r]]:
                need(previous & ~frame == 0, 'register chain does not nest')
                if previous != frame:
                    step = self.geometry.dim(frame) - self.geometry.dim(previous)
                    need(step > 0, 'distinct nested closed frames must increase rank')
                    profile[step] += 1
                previous = frame
            if r in self.pin:
                rank = self.geometry.dim(self.pre_frame(r, assignment))
                need(rank > 0, 'zero-rank retained COPY')
                profile[rank] += 1
        return profile

    def validate(self, assignment):
        need(len(assignment) == len(self.gates), 'assignment length')
        for g, frame in enumerate(assignment):
            need(self.geometry.close(frame)[0] == frame, 'assigned frame not closed')
            need(self.lower[g] & ~frame == 0 and frame & ~self.upper[g] == 0,
                 'assigned frame outside bounds')
        self.check_scatter(assignment)
        return self.local_profile(assignment, range(self.n))

    def enumerate_component(self, component):
        """Pruned DFS, with exact multiplicities for unvisited illegal suffixes."""
        component_set = set(component)
        remaining = [prod(len(self.options[g]) for g in component[j:])
                     for j in range(len(component)+1)]
        assignment = list(self.original)
        assigned = set()
        stats = {'cartesian_assignments': remaining[0], 'non_nesting_rejected': 0,
                 'legal_assignments': 0, 'scatter_pin_rejected': 0}
        invalid = []

        def known(endpoint, fixed):
            return fixed if endpoint is None else (
                assignment[endpoint] if endpoint not in component_set or endpoint in assigned else None)

        def visit(depth):
            if depth == len(component):
                stats['legal_assignments'] += 1
                try:
                    self.check_scatter(assignment)
                except ValueError:
                    stats['scatter_pin_rejected'] += 1
                    return
                yield list(assignment)
                return
            g = component[depth]
            for frame in self.options[g]:
                assignment[g] = frame
                assigned.add(g)
                nested = all(value is None or value & ~frame == 0
                             for endpoint, fixed in self.before[g]
                             for value in [known(endpoint, fixed)]) and all(
                             value is None or frame & ~value == 0
                             for endpoint, fixed in self.after[g]
                             for value in [known(endpoint, fixed)])
                if nested:
                    yield from visit(depth + 1)
                else:
                    stats['non_nesting_rejected'] += remaining[depth+1]
                    if not invalid:
                        witness = list(assignment)
                        for later in component[depth+1:]:
                            witness[later] = self.options[later][0]
                        invalid.append(witness)
                assigned.remove(g)
            assignment[g] = self.original[g]

        return visit(0), stats, invalid


def signed_difference(left, right):
    return {d: left.get(d, 0) - right.get(d, 0) for d in sorted(set(left) | set(right))
            if left.get(d, 0) != right.get(d, 0)}


def truncations(delta):
    """Integer concave-order witnesses, with terminal value the rank-mass delta."""
    return [sum(n * min(d, k) for d, n in delta.items()) for k in range(1, 9)]


def uniform_classification(delta):
    """Certify precisely the two observed uniform inequalities, not others.

    For f(d)=d**(1-c), 0<c<1, its decreasing slopes give the expansion
    f(d)=a*d + sum(b[k]*min(d,k), k=1..7), with every b[k]>0.
    Equal rank mass and nonnegative truncated sums therefore prove dominance.
    If all truncated sums vanish, invert their successive differences to get
    delta=0; a nonempty delta thus gives a strict inequality.

    The only additional accepted profile is {1:3, 2:-3, 3:1}. Dividing its
    moment by 3*64**c gives g(c)=1-2*2**(-c)+3**(-c). It has g(0)=0 and
    g'(c)>0 for c>=0: 2*log(2)>log(3) because 4>3, and 2**(-c)>=3**(-c).
    This exact symbolic lemma proves positivity without a numerical sample.
    """
    need(bool(delta), 'uniform classification requires a strict profile difference')
    values = truncations(delta)
    if values[-1] == 0 and all(value >= 0 for value in values):
        need(any(values[:-1]), 'nonzero delta with vanishing truncated sums')
        return 'truncated_rank_dominance'
    need(delta == {1: 3, 2: -3, 3: 1}, 'uncovered uniform power-profile inequality')
    return 'three_one_minus_three_two_plus_three_lemma'


def load_prices():
    need(digest((ROOT / ENGINE).read_bytes()) == ENGINE_SHA, 'exact interval engine hash')
    spec = importlib.util.spec_from_file_location('r439_independent_interval', ROOT / ENGINE)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    return {d: tuple(64 * value for value in engine.moment(64, 1, [(d, 1)], C))
            for d in range(1, 9)}


def interval(delta, prices):
    """Independent signed interval accumulation; never compare float midpoints."""
    lower = upper = Fraction(0)
    for d, count in delta.items():
        lo, hi = prices[d]
        lower += count * (lo if count >= 0 else hi)
        upper += count * (hi if count >= 0 else lo)
    need(not delta or lower > 0 or upper < 0, 'unresolved fixed-c comparison')
    return lower, upper


def as_profile(profile):
    return [[d, n] for d, n in sorted(profile.items()) if n]


def expect_rejected(name, operation):
    try:
        operation()
    except ValueError:
        return name
    raise ValueError('negative control was accepted: ' + name)


def verify_receipt(expected, actual):
    need(expected == actual, 'independent certificate differs from fresh computation')


def check_sources():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    files = sources['files']
    need(files.get(WORD) == WORD_SHA and files.get(ENGINE) == ENGINE_SHA, 'required source pins')
    need(type(files) is dict and bool(files), 'source pin inventory')
    for name, expected in files.items():
        path = Path(name)
        need(not path.is_absolute() and '..' not in path.parts, 'source path confinement')
        need(digest((ROOT / path).read_bytes()) == expected, 'source hash mismatch: ' + name)
    return sources


def compare_nomination(problem, summary, base_commit):
    """Compare structural claims and exact count/profile fields, ignoring display floats."""
    nomination = json.loads((HERE / 'NOMINATION.json').read_text())
    need(nomination['schema'] == 'r439-resynth-frame-nomination-v1'
         and nomination['base_commit'] == base_commit, 'nomination identity')
    nodes = [{'gate': list(problem.keys[g]), 'registers': problem.gates[g],
              'lower': str(problem.lower[g]), 'upper': str(problem.upper[g]),
              'original': str(problem.original[g]),
              'choices': sorted(str(m) for m in choices)}
             for g, choices in sorted(problem.options.items(), key=lambda pair: problem.keys[pair[0]])]
    components = sorted(sorted(list(problem.keys[g]) for g in group) for group in problem.components)
    need(nomination['free_nodes'] == nodes, 'nomination free-frame domain')
    need(nomination['components'] == components, 'nomination components')
    need(nomination['original_copy_frames'] == {str(r): str(m) for r, m in sorted(problem.pin.items())},
         'nomination original COPY frames')
    need(nomination['source_word'] == WORD and Fraction(nomination['c']) == C
         and nomination['assignment_seed'] == 10, 'nomination scope')
    for field in ['gates', 'free_gates', 'components', 'component_sizes', 'assignments_enumerated',
                  'non_nesting_rejected', 'same_profile_alternatives', 'start_profile',
                  'optimum_profile', 'improving_components']:
        need(nomination['summary'][field] == summary[field], 'nomination summary field: ' + field)
    return digest(canonical(nodes)), digest(canonical(components))


def build_receipt():
    sources = check_sources()
    word_bytes = (ROOT / WORD).read_bytes()
    need(digest(word_bytes) == WORD_SHA, 'word bytes')
    word = json.loads(gzip.decompress(word_bytes))
    problem = Problem(word)
    prices = load_prices()
    baseline = problem.validate(problem.original)
    need(dict(baseline) == BASE_PROFILE, 'baseline paid profile')
    records, invalid_witness = [], None
    total = Counter()
    all_dominant = True
    degraded = list(problem.original)
    for g, choices in problem.options.items():
        degraded[g] = problem.lower[g]
    degraded_profile = problem.validate(degraded)
    recovered = Counter(degraded_profile)
    recovery_components = 0
    smallest_loss = None
    for component in problem.components:
        registers = sorted({r for g in component for r in problem.gates[g]})
        local_base = problem.local_profile(problem.original, registers)
        iterator, counts, invalid = problem.enumerate_component(component)
        ties, distinct_deltas, strict_losses = 0, {}, []
        dominance_passed = dominance_failed = analytic_exception = 0
        for assignment in iterator:
            local = problem.local_profile(assignment, registers)
            delta = signed_difference(local, local_base)
            if not delta:
                ties += any(assignment[g] != problem.original[g] for g in component)
                continue
            values = truncations(delta)
            dominant = values[-1] == 0 and all(value >= 0 for value in values)
            all_dominant &= dominant
            dominance_passed += int(dominant)
            dominance_failed += int(not dominant)
            classification = uniform_classification(delta)
            analytic_exception += int(classification != 'truncated_rank_dominance')
            bounds = interval(delta, prices)
            need(bounds[0] > 0, 'strictly improving frame assignment found')
            strict_losses.append(bounds)
            signature = tuple(sorted(delta.items()))
            distinct_deltas[signature] = {'delta': [list(pair) for pair in signature],
                                         'truncated_rank_sums': values,
                                         'uniform_positivity_proof': classification,
                                         'fixed_c_delta_interval': [str(x) for x in bounds]}
        need(counts['cartesian_assignments'] == counts['legal_assignments'] + counts['non_nesting_rejected'],
             'DFS assignment coverage')
        # This equality proves the producer's implicit COPY-pin relaxation is
        # harmless on this exact candidate, rather than assuming it generally.
        need(counts['scatter_pin_rejected'] == 0, 'producer relaxation admits altered scatter frames')
        counts['same_profile_alternatives'] = ties
        counts['strict_alternatives_dominated'] = dominance_passed
        counts['strict_alternatives_not_dominated'] = dominance_failed
        counts['strict_alternatives_analytic_exception'] = analytic_exception
        need(counts['legal_assignments'] == 1 + ties + dominance_passed + dominance_failed,
             'component profiles do not partition the legal assignments')
        total.update(counts)
        if invalid and invalid_witness is None:
            invalid_witness = invalid[0]
        if strict_losses:
            lower = min(bounds[0] for bounds in strict_losses)
            smallest_loss = lower if smallest_loss is None else min(smallest_loss, lower)
        component_degraded = list(problem.original)
        for g in component:
            component_degraded[g] = problem.lower[g]
        local_degraded = problem.local_profile(component_degraded, registers)
        recovery = signed_difference(local_base, local_degraded)
        if recovery:
            need(interval(recovery, prices)[1] < 0, 'least-frame control component not improved')
            recovery_components += 1
            for d, n in recovery.items():
                recovered[d] += n
        records.append({'gates': [list(problem.keys[g]) for g in component], **counts,
                        'distinct_strict_profile_deltas': [distinct_deltas[k] for k in sorted(distinct_deltas)]})
    need(+recovered == baseline and recovery_components > 0, 'degraded positive control failed to recover optimum')
    need(interval(signed_difference(degraded_profile, baseline), prices)[0] > 0,
         'least-frame control was not degraded')
    summary = {'gates': len(problem.gates), 'free_gates': len(problem.options),
               'components': len(problem.components),
               'component_sizes': {str(k): v for k, v in sorted(Counter(map(len, problem.components)).items())},
               'assignments_enumerated': total['cartesian_assignments'],
               'non_nesting_rejected': total['non_nesting_rejected'],
               'same_profile_alternatives': total['same_profile_alternatives'],
               'start_profile': {str(d): n for d, n in sorted(baseline.items())},
               'optimum_profile': {str(d): n for d, n in sorted(baseline.items())},
               'improving_components': 0}
    node_hash, component_hash = compare_nomination(problem, summary, sources['base_commit'])
    controls = []
    outside = list(problem.original)
    outside[0] = problem.geometry.full
    controls.append(expect_rejected('nonzero D frame outside bounds', lambda: problem.validate(outside)))
    need(invalid_witness is not None, 'missing actual non-nesting witness')
    controls.append(expect_rejected('closed in-bounds non-nesting assignment',
                                    lambda: problem.validate(invalid_witness)))
    nonclosed = next((mask ^ (1 << i) for mask in problem.frames for i in bits(mask)
                      if problem.geometry.close(mask ^ (1 << i))[0] != mask ^ (1 << i)), None)
    need(nonclosed is not None, 'missing nonclosed frame control')
    altered = list(problem.original)
    rotated_free = sorted(problem.options)[10 % len(problem.options)]
    altered[rotated_free] = nonclosed
    controls.append(expect_rejected('nonclosed assigned frame', lambda: problem.validate(altered)))
    changed_copy = list(problem.original)
    retained = problem.ret[10 % len(problem.ret)]
    need(problem.pre[retained] is not None and problem.pin[retained] != 0, 'COPY control setup')
    changed_copy[problem.pre[retained]] = 0
    controls.append(expect_rejected('actual COPY frame equality', lambda: problem.check_scatter(changed_copy)))
    wrong_same_rank = next(mask for mask in problem.frames
                           if mask != problem.pin[retained]
                           and problem.geometry.dim(mask) == problem.geometry.dim(problem.pin[retained]))
    same_rank_copy = list(problem.original)
    same_rank_copy[problem.pre[retained]] = wrong_same_rank
    controls.append(expect_rejected('same-rank wrong COPY frame', lambda: problem.check_scatter(same_rank_copy)))
    changed_target = list(problem.original)
    targets = [r for r in range(problem.v, 2*problem.v) if problem.pre[r] is not None]
    need(bool(targets), 'target frame negative-control setup')
    target = targets[10 % len(targets)]
    changed_target[problem.pre[target]] = problem.geometry.full
    controls.append(expect_rejected('target zero frame at scatter', lambda: problem.check_scatter(changed_target)))
    controls.append(expect_rejected('changed receipt summary', lambda: verify_receipt(summary, {**summary, 'free_gates': -1})))
    controls.append(expect_rejected('unproved reversed analytic exception',
                                    lambda: uniform_classification({1: -3, 2: 3, 3: -1})))
    controls.append(expect_rejected('altered analytic exception coefficient',
                                    lambda: uniform_classification({1: 3, 2: -3, 3: 2})))
    return {'schema': 'r439-resynth-frame-independent-v1', 'assignment_seed': 10,
            'base_commit': sources['base_commit'], 'source_word': WORD,
            'source_sha256': sources['files'],
            'sources_manifest_sha256': digest((HERE / 'SOURCES.json').read_bytes()),
            'word_canonical_sha256': digest(canonical(word)),
            'nomination_sha256': digest((HERE / 'NOMINATION.json').read_bytes()),
            'free_nodes_sha256': node_hash, 'components_sha256': component_hash,
            'c': str(C), 'summary': summary,
            'free_gates_by_phase': dict(sorted(Counter(problem.keys[g][0] for g in problem.options).items())),
            'D_fixed_zero': True, 'all_ABC_gates_single_source': all(len(g[2]) == 1 for s in 'ABC' for g in word[s]),
            'actual_copy_pins': {str(r): str(m) for r, m in sorted(problem.pin.items())},
            'nested_assignments_checked': total['legal_assignments'],
            'scatter_pin_rejected': total['scatter_pin_rejected'],
            'copy_relaxation_proved_harmless_for_this_word': True,
            'all_alternatives_concave_dominated': all_dominant,
            'strict_alternatives_dominated': total['strict_alternatives_dominated'],
            'strict_alternatives_not_dominated': total['strict_alternatives_not_dominated'],
            'strict_alternatives_analytic_exception': total['strict_alternatives_analytic_exception'],
            'all_strict_alternatives_uniformly_positive': True,
            'uniform_scope': 'All real 0<c<1: truncated-rank dominance or the exact delta {1:3,2:-3,3:1} lemma; fixed idle terms cancel.',
            'minimum_strict_fixed_c_loss_lower_bound': str(smallest_loss),
            'positive_control': {'least_frame_profile': as_profile(degraded_profile),
                                 'recovered_profile': as_profile(recovered),
                                 'improving_components': recovery_components,
                                 'degraded_minus_optimum_interval': [str(x) for x in interval(signed_difference(degraded_profile, baseline), prices)]},
            'negative_controls_rejected': controls, 'components': records,
            'negative_control_seed_rotation': {'seed': 10, 'free_gate': list(problem.keys[rotated_free]),
                                               'retained_register': retained, 'target_register': target},
            'scope': 'Fixed PR952 serialized gate order and operands, start/final frames and actual COPY frames; D fixed zero; C frames relaxed. Finite frame-only negative result, no new kappa or scalar/hosting validation.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', action='store_true', help='regenerate sibling CERTIFICATE.json')
    parser.add_argument('--certificate', type=Path, default=HERE / 'CERTIFICATE.json')
    args = parser.parse_args()
    receipt = build_receipt()
    if args.write_certificate:
        need(args.certificate == HERE / 'CERTIFICATE.json', 'write only the package certificate')
        args.certificate.write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    else:
        verify_receipt(json.loads(args.certificate.read_text()), receipt)
    print('PASS_R439_RESYNTH_FRAME_INDEPENDENT ' + json.dumps({
        **receipt['summary'], 'uniform_concave_dominance': receipt['all_alternatives_concave_dominated'],
        'uniform_power_moment_optimality': receipt['all_strict_alternatives_uniformly_positive'],
        'controls': len(receipt['negative_controls_rejected'])}, sort_keys=True))


if __name__ == '__main__':
    main()

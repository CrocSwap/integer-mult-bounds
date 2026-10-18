#!/usr/bin/env python3
"""Independent finite checks for coupled read-exchange nominations.

No search or SW4-builder code is imported. Binary subspaces are represented by
all their vectors, and scalar B maps use exact Fractions on every register.
The fixed A+cut prefix is unchanged; equality as maps on arbitrary B inputs
therefore implies equality after that prefix. This does not replace native,
wrapper, phase, owner, finite-invoice or outer-assembly admission.

With --search-report, exact pricing covers every reported legal profile.
Adding --replay-refusals independently reconstructs the completed finite domain,
checks every F2 refusal and survivor profile, and compares the failure digest.
Neither mode establishes a general impossibility theorem.
Apache-2.0. Prepared with OpenAI Codex assistance.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import itertools
import json
from pathlib import Path

V, DIM = 112, 9
CURRENT_B = Q('0.001663428754540205730067')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = Path(path).read_bytes()
    if str(path).endswith('.gz'):
        raw = gzip.decompress(raw)
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def encoded(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


@lru_cache(None)
def span(vectors):
    out = {0}
    for x in vectors:
        need(type(x) is int and 0 <= x < (1 << DIM), 'Invalid F2 vector')
        out |= {y ^ x for y in tuple(out)}
    return frozenset(out)


def subspace(vectors):
    return span(tuple(vectors))


def rank(space):
    n = len(space)
    need(n > 0 and n & (n - 1) == 0, 'Invalid subspace cardinality')
    return n.bit_length() - 1


def frame(space):
    # The least vector at each occurring highest bit is the reduced pivot row.
    return [min(x for x in space if x.bit_length() == bit + 1)
            for bit in range(DIM - 1, -1, -1)
            if any(x.bit_length() == bit + 1 for x in space)]


@lru_cache(None)
def union_space(left, right):
    return subspace(frame(left) + frame(right))


FULL = subspace(1 << i for i in range(DIM))
ZERO = subspace(())


def registers(g):
    need(g[0] in ('add', 'scale'), 'Unknown gate opcode')
    return g[1:3] if g[0] == 'add' else g[1:2]


def coefficient(g):
    a, b = g[3:5] if g[0] == 'add' else g[2:4]
    need(type(a) is int and type(b) is int and b != 0, 'Invalid rational coefficient')
    q = Q(a, b)
    need(q.denominator & (q.denominator - 1) == 0, 'Coefficient is not dyadic')
    if g[0] == 'scale':
        need(q != 0, 'Singular scalar gate')
    return q


def geometry(word):
    n = 2 * V + word['report']['R']
    need(len(word['ports']) == V and n > 2 * V, 'Unexpected geometry')
    caps = [frozenset(x for x in range(1 << DIM)
                      if bin(x & p).count('1') % 2 == 0) for p in word['ports']]
    starts = [subspace((p,)) for p in word['ports']] + [ZERO] * (n - V)
    ends = [FULL] * V + caps + [FULL] * (n - 2 * V)
    for q, f in word.get('start_extra', {}).items():
        need(2 * V <= int(q) < n, 'Non-helper entrance override')
        starts[int(q)] = subspace(f)
    for q, f in word.get('helper_final', {}).items():
        need(2 * V <= int(q) < n, 'Non-helper terminal override')
        ends[int(q)] = subspace(f)
    for q in range(n):
        need(starts[q] <= ends[q], 'Entrance not contained in terminal frame')
    return n, caps, starts, ends


def validate_gate(g, n):
    for q in registers(g):
        need(type(q) is int and 0 <= q < n, 'Gate register out of range')
    need(g[0] != 'add' or g[1] != g[2], 'Self-add outside nomination model')
    coefficient(g)


def scalar_b_map(word):
    """Exact linear B map on arbitrary independent B-entry register values."""
    n = 2 * V + word['report']['R']
    rows = [{i: Q(1)} for i in range(n)]
    for g in word['B']:
        validate_gate(g, n)
        t, c = g[1], coefficient(g)
        if g[0] == 'scale':
            rows[t] = {k: c * x for k, x in rows[t].items() if c * x}
        else:
            for k, x in tuple(rows[g[2]].items()):
                value = rows[t].get(k, Q(0)) + c * x
                if value:
                    rows[t][k] = value
                else:
                    rows[t].pop(k, None)
    return rows


def scalar_compare(original, candidate):
    left, right = scalar_b_map(original), scalar_b_map(candidate)
    changed = [i for i, (a, b) in enumerate(zip(left, right)) if a != b]
    need(not changed, 'Exact B map changed at registers ' + str(changed[:16]))
    return len(left)


def rewrite(original, moves):
    """Apply validated scalar edits simultaneously using original B indices."""
    n, _, _, _ = geometry(original)
    gates = original['B']
    edits, deleted, inserted = {}, set(), defaultdict(list)
    for m in moves:
        need(m.get('kind') in ('h2r', 'r2h'), 'Unknown move kind')
        h, r, i, t = (m[k] for k in ('h', 'r', 'read_index', 'target'))
        need(all(type(x) is int for x in (h, r, i, t)), 'Noninteger move index')
        need(2 * V <= h < n and str(h) in original['start_extra'], 'Non-entering helper')
        need(0 <= r < n and not V <= r < 2 * V and r != h, 'Invalid copy source')
        need(0 <= i < len(gates) and V <= t < 2 * V, 'Invalid target read')
        writes = [j for j, g in enumerate(gates) if g[1] == h]
        need(bool(writes), 'Copy helper has no B write')
        copy = writes[0]
        need(gates[copy][:5] == ['add', h, r, 1, 1], 'First B write is not the copy')
        before = [j for j in range(copy) if h in registers(gates[j])]
        need(all(gates[j][0] == 'add' and V <= gates[j][1] < 2 * V
                 and gates[j][2] == h for j in before), 'Invalid pre-copy use')
        stop = next((j for j in range(copy + 1, len(gates))
                     if gates[j][1] in (h, r)), len(gates))
        need(copy < i < stop, 'Read outside stable copy interval')
        g = gates[i]
        source = h if m['kind'] == 'h2r' else r
        need(g[:3] == ['add', t, source] and g[3:5] == m['coef'], 'Read/recipe mismatch')
        a, b = m['coef']
        need(i not in edits, 'Duplicate read edit')
        edits[i] = ['add', t, r if source == h else h, a, b, None]
        if m['kind'] == 'h2r':
            j = m['delete_preread_index']
            need(type(j) is int and j in before, 'Deleted pre-read outside prefix')
            need(gates[j][:5] == ['add', t, h, -a, b], 'Deleted pre-read mismatch')
            need(j not in deleted, 'Duplicate pre-read deletion')
            deleted.add(j)
        else:
            j = m['insert_preread_before']
            need(j == (before[-1] + 1 if before else copy), 'Insertion point outside declared rule')
            need(m['preread'] == ['add', t, h, -a, b], 'Inserted pre-read mismatch')
            inserted[j].append(['add', t, h, -a, b, None])
    need(not deleted.intersection(edits), 'Read both edited and deleted')
    out, changed = [], []
    for i, g in enumerate(gates):
        for new in inserted.get(i, []):
            out.append(deepcopy(new)); changed.append(True)
        if i not in deleted:
            out.append(deepcopy(edits.get(i, g))); changed.append(i in edits)
    word = deepcopy(original)
    word['B'] = out
    profile, widths = recount(word, refit=changed)
    word['report']['local_profile'] = profile
    word['report']['local_rank_mass'] = sum(int(k) * v for k, v in profile.items())
    return word, profile, widths


def recount(word, refit=None):
    """Independent span-set path check and complete inherited paid ledger."""
    n, caps, starts, ends = geometry(word)
    cur, paid = starts[:], Counter()
    for section in ('A', 'cut', 'B', 'cleanup'):
        for g in word[section]:
            validate_gate(g, n)

    def move(g, floor=None):
        rs = registers(g)
        f = subspace(g[-1]) if floor is None else floor
        if floor is not None:
            for q in rs:
                f = union_space(f, cur[q])
            g[-1] = frame(f)
        for q in rs:
            need(cur[q] <= f, 'Nonmonotone frame at register ' + str(q))
            if V <= q < 2 * V:
                need(f <= caps[q - V], 'Target hyperplane violation at ' + str(q))
            d = rank(f) - rank(cur[q])
            if d:
                paid[d] += 1
            cur[q] = f

    for g in word['A']:
        move(g)
    # The unchanged centre-cut interface charges its nested served levels.
    levels = {int(t): subspace(f) for t, f in word.get('target_levels', {}).items()}
    for q, f in zip(word['centers'], word['center_frames']):
        old = subspace(f)
        served = {levels.get(g[1] - V, ZERO) for g in word['cut'] if g[2] == q}
        for new in sorted(served, key=lambda s: -rank(s)):
            need(new <= old, 'Non-nested centre-cut levels')
            d = rank(old) - rank(new)
            if d:
                paid[d] += 1
            old = new
    for i, g in enumerate(word['B']):
        if refit is None:
            move(g)
        else:
            move(g, ZERO if refit[i] else subspace(g[-1]))
    seen = set()
    for entry in word.get('early_cleanup', []):
        i, f = entry
        need(type(i) is int and 0 <= i < len(word['cleanup']) and i not in seen,
             'Invalid or repeated early-cleanup index')
        seen.add(i)
        g = deepcopy(word['cleanup'][i]); g[-1] = list(f)
        if refit is None:
            move(g)
        else:
            move(g, subspace(f)); entry[1] = g[-1]
        for q in registers(g):
            need(cur[q] <= ends[q], 'Early tail exceeds terminal frame')
    for q in range(n):
        need(cur[q] <= ends[q], 'Terminal frame violation at ' + str(q))
        d = rank(ends[q]) - rank(cur[q])
        if d:
            paid[d] += 1
    widths = [rank(ends[q]) - rank(starts[q]) for q in range(2 * V, n)]
    return {str(k): v for k, v in sorted(paid.items()) if v}, widths


def boundary_check(original, candidate):
    keys = ('ports', 'start_extra', 'helper_final', 'A', 'cut', 'cleanup',
            'target_levels', 'centers', 'center_frames')
    for key in keys:
        need(original.get(key) == candidate.get(key), 'Changed fixed boundary/section: ' + key)
    need(original['report']['R'] == candidate['report']['R'], 'Changed helper count')
    need([i for i, _ in original.get('early_cleanup', [])]
         == [i for i, _ in candidate.get('early_cleanup', [])], 'Changed scalar tail order')
    a, b = geometry(original), geometry(candidate)
    need(a[2:] == b[2:], 'Changed per-register entrance or terminal subspace')
    widths = [rank(b[3][q]) - rank(b[2][q]) for q in range(2 * V, b[0])]
    return {'helper_count': len(widths), 'total_width': sum(widths),
            'per_helper_width_sha256': hashlib.sha256(encoded(widths)).hexdigest()}


@lru_cache(None)
def logarithm(n):
    """Rational ln(n) interval, via range reduction and positive atanh series."""
    need(type(n) is int and n >= 1, 'Invalid rank in moment')
    def small(x):
        t = (x - 1) / (x + 1)
        value = Q(0); power = t
        terms = 70
        for j in range(terms):
            value += 2 * power / (2 * j + 1)
            power *= t * t
        tail = 2 * power / ((2 * terms + 1) * (1 - t * t))
        return value, value + tail
    k = n.bit_length() - 1
    a, b = small(Q(n, 1 << k)); c, d = small(Q(2))
    return a + k * c, b + k * d


@lru_cache(None)
def weight(n, exponent):
    """Bounds on n**(1-exponent); exp(-y) alternating Taylor bounds."""
    lo, hi = logarithm(n)
    ylo, yhi = exponent * lo, exponent * hi
    need(0 <= ylo <= yhi < 1, 'Exponent outside supported moment interval')
    def partial(y, degree):
        total, term = Q(1), Q(1)
        for j in range(1, degree + 1):
            term *= -y / j
            total += term
        return total
    return n * partial(yhi, 17), n * partial(ylo, 16)


def price(profile, baseline, exponent=CURRENT_B):
    delta = {int(k): profile.get(str(k), 0) - baseline.get(str(k), 0)
             for k in set(profile) | set(baseline)}
    need(all(type(v) is int and v >= 0 for v in profile.values()), 'Invalid profile count')
    need(sum(r * v for r, v in delta.items()) == 0, 'Changed local rank mass')
    lo = hi = Q(0)
    for r, count in delta.items():
        if not count:
            continue
        a, b = weight(r, exponent)
        lo += count * (a if count > 0 else b)
        hi += count * (b if count > 0 else a)
    relation = ('identical_profile' if not any(delta.values()) else
                'strictly_cheaper' if hi < 0 else
                'strictly_more_expensive' if lo > 0 else 'unresolved_interval')
    return {'relation': relation, 'local_cost_delta_lower': str(lo),
            'local_cost_delta_upper': str(hi),
            'local_rank_mass': sum(int(k) * v for k, v in profile.items()),
            'complete_global_profile_rule': '72 * local + idle {1:1,3:1,44:1,48:2396}',
            'scope': 'Exact sign at stated endpoint; no new endpoint or outer kappa certification.'}



def enumerate_pairs(word):
    """Reconstruct the finite eligibility rule directly from scalar B gates."""
    gates = word['B']
    writes, touches = defaultdict(list), defaultdict(list)
    for i, g in enumerate(gates):
        writes[g[1]].append(i)
        for r in registers(g):
            touches[r].append(i)
    pairs = []
    for helper in sorted(int(x) for x in word['start_extra']):
        if not writes[helper]:
            continue
        copy_index = writes[helper][0]
        copy = gates[copy_index]
        if copy[0] != 'add' or copy[3:5] != [1, 1]:
            continue
        source = copy[2]
        if V <= source < 2 * V:
            continue
        prefix = [j for j in touches[helper] if j < copy_index]
        if any(gates[j][0] != 'add' or gates[j][2] != helper
               or not V <= gates[j][1] < 2 * V for j in prefix):
            continue
        stops = [j for r in (helper, source) for j in writes[r] if j > copy_index]
        stop = min(stops, default=len(gates))
        insertion = max(prefix) + 1 if prefix else copy_index
        moves = []
        for i in range(copy_index + 1, stop):
            g = gates[i]
            if g[0] != 'add' or g[2] not in (helper, source) or not V <= g[1] < 2 * V:
                continue
            target, a, b = g[1], g[3], g[4]
            move = dict(h=helper, r=source, read_index=i, target=target, coef=[a, b])
            if g[2] == helper:
                matching = [j for j in prefix if gates[j][:5] == ['add', target, helper, -a, b]]
                if len(matching) != 1:
                    continue
                move.update(kind='h2r', delete_preread_index=matching[0])
            else:
                move.update(kind='r2h', insert_preread_before=insertion,
                            preread=['add', target, helper, -a, b])
            moves.append(move)
        if moves:
            pairs.append(dict(h=helper, r=source, copy_index=copy_index,
                              stop_index=stop, moves=moves))
    return pairs


class RefusalProbe:
    """Only the failure path: independently propagate explicit vector sets.

    This deliberately does not price or claim scalar correctness of survivors.
    Gates use original B indices; inserted gates use ['insert', original index].
    Tail failure indices are positions in early_cleanup, not cleanup indices.
    """
    def __init__(self, word):
        self.word = word
        _, self.caps, cur, self.ends = geometry(word)
        for g in word['A']:
            f = subspace(g[-1])
            for q in registers(g):
                need(cur[q] <= f, 'Invalid fixed A frame')
                cur[q] = f
        self.initial = cur
        self.gates = [(tuple(registers(g)), subspace(g[-1])) for g in word['B']]
        self.tails = [(tuple(registers(word['cleanup'][i])), subspace(f))
                      for i, f in word.get('early_cleanup', [])]

    def run(self, moves):
        replaced, deleted, inserted = {}, set(), defaultdict(list)
        for m in moves:
            i = m['read_index']
            if i in replaced:
                return ('conflicting_read', i), None
            replaced[i] = (m['target'], m['r'] if m['kind'] == 'h2r' else m['h'])
            if m['kind'] == 'h2r':
                if m['delete_preread_index'] in deleted:
                    return ('conflicting_delete', i), None
                deleted.add(m['delete_preread_index'])
            else:
                inserted[m['insert_preread_before']].append((m['target'], m['h']))
        if deleted.intersection(replaced):
            return ('edit_delete',), None
        cur = self.initial[:]
        for i, (old_rs, floor) in enumerate(self.gates):
            pending = [(rs, ZERO, ['insert', i]) for rs in inserted.get(i, ())]
            if i not in deleted:
                pending.append((replaced.get(i, old_rs), ZERO if i in replaced else floor, i))
            for rs, f, origin in pending:
                for q in rs:
                    f = union_space(f, cur[q])
                for q in rs:
                    if V <= q < 2 * V and not f <= self.caps[q - V]:
                        return ('cap', origin, q), min(f - self.caps[q - V])
                for q in rs:
                    cur[q] = f
        for i, (rs, f) in enumerate(self.tails):
            for q in rs:
                f = union_space(f, cur[q])
            for q in rs:
                if not f <= self.ends[q]:
                    return ('tail', i, q), min(f - self.ends[q])
            for q in rs:
                cur[q] = f
        for q, f in enumerate(self.ends):
            if not cur[q] <= f:
                return ('end', q), min(cur[q] - f)
        return None, None



def finite_groups(pairs, arity, domain):
    """Enumerate complete groups and their exact nonempty, non-all-full counts."""
    targets = {p['h']: {m['target'] for m in p['moves']} for p in pairs}
    groups = []
    for group in itertools.combinations(pairs, arity):
        ids = [p['h'] for p in group]
        if domain == 'shared-targets':
            # Check every cut of this small graph, not the search's reachability code.
            connected = True
            for mask in range(1, (1 << arity) - 1):
                if not any(targets[ids[i]].intersection(targets[ids[j]])
                           for i in range(arity) for j in range(arity)
                           if mask & (1 << i) and not mask & (1 << j)):
                    connected = False
                    break
            if not connected:
                continue
        count = 1
        for pair in group:
            count *= (1 << len(pair['moves'])) - 1
        groups.append((group, count - 1))
    return groups

def replay_refusals(word, rec, search, declared_pairs):
    need(search['status'] == 'COMPLETE_FINITE_DOMAIN', 'Refusal replay requires a completed domain')
    need(search['at_least_one_partial'] is True and search['unchanged_other_sw4_pairs'] is True,
         'Different coupling rule')
    arity = search.get('arity', 2)
    domain = search['domain']
    need(arity in (2, 3) and domain in ('all', 'shared-targets'), 'Unknown finite domain')
    pairs = enumerate_pairs(word)
    need(declared_pairs['input_sha256'] == rec['input_sha256'], 'Candidate input pin mismatch')
    need(pairs == declared_pairs['pairs'], 'Independent eligible-pair enumeration differs')
    all_groups = finite_groups(pairs, arity, domain)
    expected_groups = [[*[p['h'] for p in g], n] for g, n in all_groups]
    need(expected_groups == search['pairs_tested'], 'Incomplete or inconsistent group/mask declaration')
    need(sum(n for _, n in all_groups) == search['counts']['coupled_total'], 'Incomplete candidate total')
    probe = RefusalProbe(word)
    need(probe.run([])[0] is None, 'Identity unexpectedly refused')
    need(probe.run(rec['moves'])[0] is None, 'Known SW4 unexpectedly refused')
    count, profiles = Counter(), Counter()
    for pair in pairs:
        for mask in range(1, 1 << len(pair['moves'])):
            moves = [m for i, m in enumerate(pair['moves']) if mask & (1 << i)]
            failure, _ = probe.run(moves)
            count['single_total'] += 1
            count['single_' + (failure[0] if failure else 'legal')] += 1
    witness_hash = hashlib.sha256()
    site_hash = hashlib.sha256()
    groups, witnesses = [], []
    for group, _ in all_groups:
        ids = [p['h'] for p in group]
        fixed = [m for m in rec['moves'] if m['h'] not in ids]
        checked = 0
        for masks in itertools.product(*(range(1, 1 << len(p['moves'])) for p in group)):
            if all(m == (1 << len(p['moves'])) - 1 for p, m in zip(group, masks)):
                continue
            moves = fixed + [move for p, mask in zip(group, masks)
                             for i, move in enumerate(p['moves']) if mask & (1 << i)]
            failure, vector = probe.run(moves)
            count['coupled_total'] += 1
            count['coupled_' + (failure[0] if failure else 'legal')] += 1
            checked += 1
            site = [ids, list(masks), list(failure) if failure else None]
            site_hash.update(encoded(site) + b'\n')
            witness_hash.update(encoded(site + [vector]) + b'\n')
            if len(witnesses) < 4:
                witnesses.append(site + [vector])
            if failure is None:
                _, profile, _ = rewrite(word, moves)
                profiles[tuple(sorted((int(k), v) for k, v in profile.items()))] += 1
        groups.append(ids + [checked])
    observed = {k: v for k, v in search['counts'].items()
                if k.startswith('single_') or k.startswith('coupled_')}
    need(dict(count) == observed, 'Independent failure/survivor counts differ')
    need(groups == search['pairs_tested'], 'Independent group/mask enumeration differs')
    reported = Counter({tuple(sorted((int(k), v) for k, v in x['profile'].items())): x['count']
                        for x in search['distinct_legal_profiles']})
    need(profiles == reported, 'Independently recounted surviving profiles differ')
    if 'failure_site_sha256' in search:
        need(search['failure_site_sha256'] == site_hash.hexdigest(), 'Failure-site digest differs')
    return {'status': 'PASS_INDEPENDENT_FINITE_REFUSAL_REPLAY', 'arity': arity, 'domain': domain,
            'eligible_pairs': len(pairs), 'groups': len(groups), 'counts': dict(count),
            'failure_site_sha256': site_hash.hexdigest(),
            'failure_witness_sha256': witness_hash.hexdigest(), 'first_witnesses': witnesses,
            'digest_encoding': 'SHA256 over compact sorted-key JSON [helper_ids,masks,failure] + LF per candidate; witness digest appends least offending F2 vector. Original B index; insertion origin [insert,index]; early_cleanup-list position for tails.',
            'scope': 'Independent complete enumeration and F2 rejection of this pinned finite domain; no general impossibility claim or scalar correctness claim for any survivor.'}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('word', type=Path, help='Pinned promoted P6k4 input')
    ap.add_argument('--baseline-recipe', type=Path, required=True)
    ap.add_argument('--recipe', type=Path, help='Nomination containing moves; defaults to baseline SW4')
    ap.add_argument('--candidate-word', type=Path, help='Optional emitted word to bind to independent rewrite')
    ap.add_argument('--search-report', type=Path, help='Exact-price all reported distinct legal profiles')
    ap.add_argument('--output', type=Path)
    ap.add_argument('--replay-refusals', action='store_true', help='Independently enumerate the completed --search-report domain and check every refusal')
    args = ap.parse_args()
    need(not args.replay_refusals or args.search_report is not None, '--replay-refusals needs --search-report')
    original, source_sha = read(args.word)
    rec, _ = read(args.baseline_recipe)
    need(source_sha == rec['input_sha256'], 'Input hash mismatch')
    original_profile, _ = recount(original)
    need(original_profile == rec['profile_in'], 'Input profile mismatch')
    baseline, baseline_profile, _ = rewrite(original, rec['moves'])
    need(hashlib.sha256(encoded(baseline)).hexdigest() == rec['output_sha256'], 'Independent SW4 bytes mismatch')
    need(baseline_profile == rec['profile_out'], 'SW4 profile mismatch')
    scalar_columns = scalar_compare(original, baseline)
    nomination = read(args.recipe)[0] if args.recipe else rec
    candidate, candidate_profile, _ = rewrite(original, nomination['moves'])
    if 'profile' in nomination:
        need(candidate_profile == nomination['profile'], 'Nomination profile mismatch')
    if args.candidate_word:
        submitted, _ = read(args.candidate_word)
        need(encoded(submitted) == encoded(candidate), 'Submitted word differs from independent rewrite')
    bounds = boundary_check(original, candidate)
    need(recount(candidate)[0] == candidate_profile, 'Emitted frame recount mismatch')
    scalar_compare(original, candidate)
    report = {'status': 'PASS_INDEPENDENT_LOCAL_NOMINATION_CHECK', 'input_sha256': source_sha,
              'baseline_sha256': rec['output_sha256'],
              'candidate_sha256': hashlib.sha256(encoded(candidate)).hexdigest(),
              'exact_scalar_columns': scalar_columns, 'boundary_identity': bounds,
              'profile': candidate_profile, 'exponent': str(CURRENT_B),
              'price': price(candidate_profile, baseline_profile),
              'scope': 'Local recipe, exact B map, F2 paths, boundaries and complete-profile cost comparison; native/global admission remains required.'}
    if args.search_report:
        search, _ = read(args.search_report)
        need(search['input_sha256'] == source_sha and search['comparison_sha256'] == rec['output_sha256'],
             'Search report baseline mismatch')
        pricing = []
        for row in search['distinct_legal_profiles']:
            profile = {str(k): v for k, v in row['profile'].items()}
            pricing.append({'profile': profile, 'reported_count': row['count'],
                            'price': price(profile, baseline_profile)})
        report['reported_profiles'] = pricing
        if args.replay_refusals:
            declared = read(args.search_report.parent / 'CANDIDATES.json')[0]
            report['refusal_replay'] = replay_refusals(original, rec, search, declared)
        report['negative_evidence_scope'] = ('Independent complete enumeration, F2 refusal replay and survivor-profile recount for the pinned finite domain; no general impossibility claim.' if args.replay_refusals else 'Exact pricing of reported profiles only; no independent enumeration, legality or completeness claim.')
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    if 'refusal_replay' in report:
        r = report['refusal_replay']
        print('PASS independent refusal replay: %d groups, %d candidates; site digest %s' % (r['groups'], r['counts']['coupled_total'], r['failure_site_sha256']))
    relations = Counter(x['price']['relation'] for x in report.get('reported_profiles', []))
    print('PASS independent exact B map (%d columns), F2 paths, helper boundaries; candidate %s; reported profiles %s'
          % (scalar_columns, report['price']['relation'], dict(relations)))


if __name__ == '__main__':
    main()

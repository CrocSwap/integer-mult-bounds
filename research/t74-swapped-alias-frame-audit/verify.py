#!/usr/bin/env python3
"""Independent finite-set frame audit; no predecessor code is imported.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Apache-2.0. Scalar endpoints and native Clifford phases are outside scope.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from functools import lru_cache
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AMBIENT = frozenset(range(512))
ZERO = frozenset([0])


class Invalid(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise Invalid(message)


@lru_cache(maxsize=None)
def span_tuple(generators):
    """Enumerate the span, rather than perform row reduction."""
    result = {0}
    for x in generators:
        need(type(x) is int and 0 <= x < 512, 'frame vector outside GF(2)^9')
        result |= {y ^ x for y in result}
    return frozenset(result)


def span(generators):
    need(isinstance(generators, list), 'frame must be a list')
    return span_tuple(tuple(generators))


def dim(space):
    n = len(space)
    need(n > 0 and n & (n - 1) == 0, 'invalid subspace cardinality')
    return n.bit_length() - 1


@lru_cache(maxsize=None)
def perp(space):
    return frozenset(x for x in AMBIENT
                     if all((x & u).bit_count() % 2 == 0 for u in space))


def encode_space(space):
    """Exact 512-bit incidence mask, independent of the supplied basis."""
    return format(sum(1 << x for x in space), '0128x')


@lru_cache(maxsize=None)
def warp_tables(columns):
    need(len(columns) == 9, 'warp column count')
    need(all(type(x) is int and 0 <= x < 512 for x in columns), 'warp column range')
    forward = []
    for x in range(512):
        y = 0
        for i, column in enumerate(columns):
            if x & (1 << i):
                y ^= column
        forward.append(y)
    need(set(forward) == set(AMBIENT), 'singular warp')
    inverse = [0] * 512
    for x, y in enumerate(forward):
        inverse[y] = x
    # G^-T on every functional, derived from the enumerated inverse permutation.
    inverse_transpose = tuple(sum(((inverse[1 << i] & z).bit_count() % 2) << i
                                  for i in range(9)) for z in range(512))
    return tuple(forward), tuple(inverse), inverse_transpose


def check_warp_frames(columns, source, target):
    g, gi, git = warp_tables(tuple(columns))
    need(frozenset(g[x] for x in source) == target, 'warp source image differs from target')
    need(frozenset(git[z] for z in perp(source)) == perp(target), 'dual warp frame image')
    # All 512 elements of L_U = {(x,x+z): x in U, z in U^perp}.
    lu = {(x, x ^ z) for x in source for z in perp(source)}
    le = {(x, x ^ z) for x in target for z in perp(target)}
    image = {(g[x], g[x] ^ git[x] ^ git[y]) for x, y in lu}
    need(len(lu) == len(le) == 512 and image == le, 'Lagrangian frame image')
    need(all(g[gi[x]] == x for x in AMBIENT), 'warp inverse')


def registers(event):
    need(event[0] in ('add', 'scale'), 'unknown scalar gate')
    return event[1:3] if event[0] == 'add' else event[1:2]


def signed(counter):
    return {str(k): counter[k] for k in sorted(counter) if counter[k]}


def audit(word, keep_trace=False):
    need(word['kind'] == 'BORROW-WORD', 'word kind')
    need(tuple(word['report'][k] for k in ('v', 'h', 'R')) == (112, 9, 480), 'geometry')
    v, n = 112, 704
    ports = word['ports']
    need(len(ports) == len(set(ports)) == v, 'port count/uniqueness')
    need(all(type(p) is int and 0 < p < 512 for p in ports), 'port range')
    removed = set(word['removed'])
    need(len(removed) == len(word['removed']) and all(224 <= r < n for r in removed), 'removed helpers')
    live = set(range(n)) - removed
    extra, cold = word['start_extra'], word['helper_final']
    need(all(str(int(r)) == r and int(r) in live and int(r) >= 224
             for r in list(extra) + list(cold)), 'helper boundary index')
    start = [span([p]) for p in ports] + [ZERO] * (n - v)
    end = [AMBIENT] * v + [perp(span([p])) for p in ports] + [AMBIENT] * 480
    for r, f in extra.items():
        start[int(r)] = span(f)
    for r, f in cold.items():
        end[int(r)] = span(f)
    current = start.copy()
    traces, section_counts, role_counts = defaultdict(list), defaultdict(Counter), defaultdict(Counter)
    profile, charge_records, warp_records = Counter(), [], []

    def charge(section, index, role, before, after, kind='climb'):
        rank = abs(dim(after) - dim(before))
        if rank:
            profile[rank] += 1
            section_counts[section][rank] += 1
            role_counts[role][rank] += 1
            record = dict(section=section, index=index, role=role, kind=kind,
                          rank=rank, before=encode_space(before), after=encode_space(after))
            charge_records.append(record)
            traces[role].append(record)

    def climb(section, index, role, destination):
        need(type(role) is int and role in live, 'gate references removed/invalid register')
        need(current[role] <= destination, f'nonmonotone frame {section}:{index}:{role}')
        charge(section, index, role, current[role], destination)
        current[role] = destination

    def scalar(section, index, event):
        need(len(event) == (6 if event[0] == 'add' else 5), 'scalar gate shape')
        if event[0] == 'add':
            need(event[1] != event[2], 'self ADD')
        for r in registers(event):
            climb(section, index, r, span(event[-1]))

    # Fixed zero-frame prefix; a source-line or raised helper cannot be accessed.
    for section in ('precondition', 'compensation'):
        for e in word[section]:
            need(e[0] in ('add', 'scale') and 112 <= e[1] < 224 and span(e[-1]) == ZERO,
                 'nonzero wrapper frame/target')
            need(all(r in live and current[r] == ZERO for r in registers(e)), 'wrapper source not at zero')
    for c in word['initial_corrections']:
        need(112 <= c['target'] < 224 and c['source'] in live and c['source'] >= 224,
             'initial correction role')
        need(start[c['source']] == ZERO, 'initial correction entrance')
        need(c['operator_word'], 'empty initial operator word')
        for op in c['operator_word']:
            need(type(op) is int and 1 <= abs(op) <= len(word['warps']), 'initial operator index')
            need(word['warps'][abs(op) - 1][1] == c['source'], 'initial correction lender')

    by_position = defaultdict(list)
    for i, record in enumerate(word['warps'], 1):
        need(len(record) == 5, 'warp record shape')
        position, lender, columns, source, target = record
        need(type(position) is int and 0 <= position <= len(word['B']), 'warp position')
        need(lender in live and not 112 <= lender < 224, 'warp lender')
        source, target = span(source), span(target)
        need(dim(source) == dim(target), 'warp rank preservation')
        check_warp_frames(columns, source, target)
        by_position[position].append((i, lender, source, target))

    prelude_count = word['prelude_events']
    need(type(prelude_count) is int and 0 <= prelude_count <= len(word['A']), 'prelude length')
    for index, e in enumerate(word['A']):
        section = 'prelude' if index < prelude_count else 'A'
        if e[0] == 'warp':
            need(section == 'prelude' and len(e) == 5, 'prelude warp placement/shape')
            _, r, op, source, target = e
            need(type(op) is int and 1 <= abs(op) <= len(word['warps']), 'prelude operator index')
            record = word['warps'][abs(op) - 1]
            source, target = span(source), span(target)
            need(r == record[1] and current[r] == source, 'prelude warp lender/frame')
            check_warp_frames(record[2], source if op > 0 else target, target if op > 0 else source)
            current[r] = target
            warp_records.append(dict(section=section, index=index, role=r, operator=op,
                                     before=encode_space(source), after=encode_space(target)))
        else:
            need(section != 'prelude' or 112 <= e[1] < 224, 'prelude writes non-target')
            scalar(section, index, e)

    levels = {int(t): span(f) for t, f in word['target_levels'].items()}
    need(all(0 <= t < v for t in levels), 'target level index')
    need(all(current[v + t] == levels.get(t, ZERO) for t in range(v)), 'cut target level')
    centers = word['centers']
    need(len(centers) == len(set(centers)) == len(word['center_frames']) == 8, 'center count')
    served = defaultdict(set)
    for e in word['cut']:
        need(e[0] == 'add' and len(e) == 6 and e[-1] is None, 'cut gate shape')
        need(e[2] in centers and 112 <= e[1] < 224, 'cut must read declared center')
        served[e[2]].add(current[e[1]])
    for i, (r, generators) in enumerate(zip(centers, word['center_frames'])):
        center = span(generators)
        need(r in live and current[r] == center and dim(center) == 8, 'center source frame')
        # COPY descends through distinct rooms; its source frame stays put.
        for j, room in enumerate(sorted(served[r], key=lambda s: (-len(s), encode_space(s)))):
            need(room <= center, 'incomparable center COPY rooms')
            charge('cut', [i, j], r, center, room, 'copy')
            center = room

    for index in range(len(word['B']) + 1):
        for op, r, source, target in by_position[index]:
            need(current[r] == source, f'handoff frame mismatch {op}:{r}')
            current[r] = target
            warp_records.append(dict(section='B', index=index, role=r, operator=op,
                                     before=encode_space(source), after=encode_space(target)))
        if index < len(word['B']):
            scalar('B', index, word['B'][index])
    for index, e in enumerate(word['restore']):
        need(not 112 <= e[1] < 224, 'restore writes a target')
        scalar('restore', index, e)
    for r in sorted(live):
        climb('final', r, r, end[r])

    # Cleanup touches FULL roles and FULL private zero-buffer counterparts.
    # This checks frame availability, not zero-buffer values or their stock bill.
    cold_ids = set(map(int, cold))
    for e in word['cleanup']:
        need(span(e[-1]) == AMBIENT, 'cleanup not at full frame')
        regs = [e[1]] if e[0] == 'warp' else registers(e)
        for r in regs:
            need((r in live and r not in cold_ids and end[r] == AMBIENT) or
                 (r >= n and r - n in cold_ids), 'cleanup role/frame')
    inventory = Counter(dim(end[r]) - dim(start[r]) for r in live if r >= 224)
    need(signed(profile) == word['report']['local_profile'], 'reported profile mismatch')
    need(signed(inventory) == word['report']['width_inventory'], 'reported inventory mismatch')
    digest = lambda rows: hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    result = dict(profile=signed(profile), local_rank_mass=sum(r * c for r, c in profile.items()),
                  helper_inventory=signed(inventory), helpers=sum(inventory.values()),
                  helper_rank_mass=sum(r * c for r, c in inventory.items()),
                  removed_helpers=len(removed), independent_input_roles=len(live),
                  charges=len(charge_records), handoffs=len(word['warps']),
                  prelude_warps=len(warp_records) - len(word['warps']), cleanup_events=len(word['cleanup']),
                  sections={k: signed(c) for k, c in sorted(section_counts.items())},
                  role_profiles={str(k): signed(c) for k, c in sorted(role_counts.items())},
                  charge_trace_sha256=digest(charge_records), warp_trace_sha256=digest(warp_records))
    if keep_trace:
        result['traces'], result['warp_records'] = dict(traces), warp_records
    return result


def load_inputs():
    manifest = json.loads((HERE / 'INPUTS.json').read_text())
    words = {}
    for source in manifest['files']:
        raw = (HERE / source['local_path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == source['sha256'], 'input container pin')
        payload = gzip.decompress(raw)
        need(hashlib.sha256(payload).hexdigest() == source['payload_sha256'], 'input payload pin')
        provider = Path(source['local_path']).name.split('-')[1].split('.')[0]
        words[source['pr'], provider] = json.loads(payload)
    need(set(words) == {(p, s) for p in (2575, 2588) for s in ('base', 'extra')}, 'input domain')
    return words


def delta(a, b):
    return {str(k): b.get(str(k), 0) - a.get(str(k), 0)
            for k in sorted(set(map(int, a)) | set(map(int, b)))
            if b.get(str(k), 0) != a.get(str(k), 0)}


def compare(before, after):
    d = delta(before['profile'], after['profile'])
    need(d == {'1': -2, '3': -2, '4': 2}, 'unexpected local delta')
    need(before['helper_inventory'] == after['helper_inventory'], 'inventory changed')
    need(before['local_rank_mass'] == after['local_rank_mass'], 'local mass changed')
    changed = []
    for r in sorted(set(before['role_profiles']) | set(after['role_profiles']), key=int):
        rd = delta(before['role_profiles'].get(r, {}), after['role_profiles'].get(r, {}))
        if rd:
            changed.append(dict(role=int(r), delta=rd, before=before['traces'].get(int(r), []),
                                after=after['traces'].get(int(r), [])))
    return dict(local_delta=d, section_deltas={s: delta(before['sections'].get(s, {}), after['sections'].get(s, {}))
                                              for s in sorted(set(before['sections']) | set(after['sections']))},
                changed_role_profiles=changed)


def concatenate(left, right):
    """Multiply free-group words in order, reducing adjacent inverse pairs."""
    result = list(left)
    for symbol in right:
        if result and result[-1] == -symbol:
            result.pop()
        else:
            result.append(symbol)
    return tuple(result)


def readback(prefix, role):
    """Pull one output covector backwards through exact noncommuting gates.

    Keys are (initial input role, free operator word), values are rational.
    This uses right multiplication of covectors, independently of the source
    checker's forward propagation of every input column.
    """
    row = {(role, ()): Fraction(1)}

    def accumulate(key, value):
        total = row.get(key, Fraction(0)) + value
        if total:
            row[key] = total
        else:
            row.pop(key, None)

    for e in reversed(prefix):
        tag, target = e[:2]
        terms = [(key, value) for key, value in row.items() if key[0] == target]
        if tag == 'add':
            coefficient = Fraction(e[3], e[4])
            for (_, word), value in terms:
                accumulate((e[2], word), value * coefficient)
        elif tag == 'scale':
            coefficient = Fraction(e[2], e[3])
            need(coefficient != 0, 'zero scale in readiness prefix')
            for key, value in terms:
                row[key] = value * coefficient
        elif tag == 'warp':
            for key, _ in terms:
                del row[key]
            for (r, word), value in terms:
                accumulate((r, concatenate(word, (e[2],))), value)
        else:
            raise Invalid('unknown readiness gate')
    return row


def serialize_row(row):
    return [dict(input=r, operator_word=list(word), coefficient=str(c))
            for (r, word), c in sorted(row.items())]


def readiness(word, run_controls=False):
    """Only PR2588's two moved lender handoffs, not the predecessor schedule."""
    selected = {80, 88}
    # These pinned words have no initial operator corrections. No source reads
    # a target, so the zero-frame target-only prefix also cannot affect a query.
    need(not word['initial_corrections'], 'unexpected initial corrections in readiness domain')
    need(all(e[0] != 'add' or 112 <= e[1] < 224 or not 112 <= e[2] < 224
             for e in word['A'] + word['B']), 'non-target reads target')
    prefix = word['precondition'] + word['compensation'] + word['A'] + word['cut']
    positions = defaultdict(list)
    for op, rec in enumerate(word['warps'], 1):
        positions[rec[0]].append((op, rec[1]))
    checks, mutations = [], []
    for index in range(len(word['B']) + 1):
        for op, lender in positions[index]:
            if lender in selected:
                row = readback(prefix, lender)
                need(row == {(lender, ()): Fraction(1)}, 'source partner not restored at handoff')
                checks.append(dict(operator=op, lender=lender, B_cut=index,
                                   prefix_events=len(prefix), row=serialize_row(row)))
                if run_controls and lender in (80, 88):
                    # A coefficient sign error leaves all frames and all ranks
                    # unchanged, but must break arbitrary-dirty handoff readiness.
                    last = max(i for i, e in enumerate(prefix) if e[0] == 'add' and e[1] == lender)
                    altered = deepcopy(prefix)
                    altered[last][3] *= -1
                    wrong = readback(altered, lender)
                    need(wrong != row, 'readiness control survived coefficient flip')
                    b_index = max(i for i, e in enumerate(word['B'][:index])
                                  if e[0] == 'add' and e[1] == lender)
                    need(word['B'][b_index] == prefix[last], 'control binding to B')
                    changed_word = deepcopy(word)
                    changed_word['B'][b_index][3] *= -1
                    need(audit(changed_word) == audit(word), 'sign mutation changed frame receipt')
                    mutations.append(dict(lender=lender, prefix_index=last, B_index=b_index,
                                          frame_receipt_unchanged=True, original=prefix[last],
                                          mutant_row=serialize_row(wrong)))
            prefix.append(['warp', lender, op])
        if index < len(word['B']):
            prefix.append(word['B'][index])
    need({c['lender'] for c in checks} == selected and len(checks) == 2, 'moved-handoff domain')
    return dict(handoffs=checks, rank_preserving_sign_mutations=mutations)


def readback_controls():
    # Distinct noncommuting operators make an order error observable.
    toy = [['warp', 0, 1], ['add', 1, 0, 2, 3], ['warp', 1, 2]]
    need(readback(toy, 1) == {(1, (2,)): Fraction(1), (0, (2, 1)): Fraction(2, 3)},
         'noncommuting reverse-covector control')
    inverse = [['warp', 1, -2], ['add', 1, 0, -2, 3], ['warp', 0, -1]]
    need(readback(toy + inverse, 1) == {(1, ()): Fraction(1)}, 'inverse-prefix control')
    return ['noncommuting K2*K1 coefficient 2/3', 'exact inverse prefix']


def controls(words):
    failures, positives = [], []
    for provider in ('base', 'extra'):
        original = words[2588, provider]
        def reject(name, mutate, expected):
            w = deepcopy(original)
            mutate(w)
            try:
                audit(w)
            except Invalid as error:
                need(expected in str(error), f'wrong control rejection {name}: {error}')
                failures.append(dict(provider=provider, name=name, rejection=str(error)))
            else:
                raise Invalid('accepted mutation: ' + name)
        reject('wrong_report', lambda w: w['report']['local_profile'].__setitem__('1', 2368), 'profile mismatch')
        reject('singular_warp', lambda w: w['warps'][55][2].__setitem__(0, 0), 'singular warp')
        reject('wrong_warp_target', lambda w: w['warps'][55].__setitem__(4, [1, 2, 4, 8]), 'source image')
        reject('late_handoff', lambda w: w['warps'][55].__setitem__(0, len(w['B'])), 'nonmonotone')
        reject('noncenter_cut_read', lambda w: w['cut'][0].__setitem__(2, 0), 'declared center')
        reject('wrong_target_level', lambda w: w['target_levels'].__setitem__('11', []), 'cut target level')
        reject('wrong_inventory', lambda w: w['report']['width_inventory'].__setitem__('7', 63), 'inventory mismatch')
        reject('removed_helper_touch', lambda w: w['A'][-1].__setitem__(1, 596), 'removed/invalid register')
        reject('nonzero_wrapper', lambda w: w['precondition'][0].__setitem__(-1, [1]), 'wrapper frame')
        # Alternative generating lists for exactly the same subspaces are valid.
        w = deepcopy(original)
        for section in ('A', 'B', 'restore'):
            for e in w[section]:
                if e[0] != 'warp' and e[-1]:
                    e[-1] = [0] + list(reversed(e[-1])) + [e[-1][0]]
        need(audit(w) == audit(original), 'equivalent-basis control changed receipt')
        positives.append(provider + ': reordered, zero-augmented and redundant scalar-frame generators')
    return dict(rejecting=failures, positive=positives)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', type=Path, help='write a new certificate to an explicit path')
    args = parser.parse_args()
    words = load_inputs()
    receipts, differences, handoffs = {}, {}, {}
    for provider in ('base', 'extra'):
        before, after = (audit(words[p, provider], keep_trace=True) for p in (2575, 2588))
        differences[provider] = compare(before, after)
        old, new = (words[p, provider] for p in (2575, 2588))
        need(old['ports'] == new['ports'] and old['centers'] == new['centers'] and
             [span(f) for f in old['center_frames']] == [span(f) for f in new['center_frames']],
             'changed public port/center boundary')
        differences[provider]['target_level_changes'] = [
            dict(target=t, before=old['target_levels'].get(str(t), []),
                 after=new['target_levels'].get(str(t), []))
            for t in range(112)
            if span(old['target_levels'].get(str(t), [])) != span(new['target_levels'].get(str(t), []))]
        differences[provider]['removed_helper_changes'] = dict(
            restored_to_inventory=sorted(set(old['removed']) - set(new['removed'])),
            newly_aliased=sorted(set(new['removed']) - set(old['removed'])))
        for pr, receipt in ((2575, before), (2588, after)):
            receipt.pop('traces')
            receipt.pop('warp_records')
            receipts[f'pr{pr}-{provider}'] = receipt
            if pr == 2588:
                handoffs[f'pr{pr}-{provider}'] = readiness(words[pr, provider], run_controls=True)
    evidence = dict(schema_version=1, status='PASS_SCOPED_FRAME_AUDIT_NO_NEW_KAPPA',
                    receipts=receipts, differences=differences, source_partner_readiness=handoffs,
                    readback_controls=readback_controls(), controls=controls(words))
    if args.write_certificate:
        with args.write_certificate.open('x') as stream:
            stream.write(json.dumps(evidence, sort_keys=True, indent=2) + '\n')
    else:
        need(evidence == json.loads((HERE / 'CERTIFICATE.json').read_text()), 'certificate mismatch')
    print('PASS_T74_SWAPPED_ALIAS_FRAME_AUDIT words=4 providers=2 '
          'delta=-2r1-2r3+2r4 helpers=422 handoff_rows=4 '
          'frame_controls=18 readiness_controls=4 positive=4 no_new_kappa')


if __name__ == '__main__':
    main()

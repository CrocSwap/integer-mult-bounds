#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact later-source carry guard; Arham Tahir with OpenAI Codex assistance.

Independent quotient arithmetic and digit enumeration. The retained physical
interpreter is used only for separately counted full-field comparisons.
Normal verification regenerates no source artifacts.
"""
import argparse
from fractions import Fraction
import hashlib
import importlib
import itertools
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pins():
    rows = json.loads((HERE / 'SOURCES.json').read_text())['files']
    live = [r for r in rows if r['usage'] == 'input']
    for row in live:
        data = (ROOT / row['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'Source SHA256 drift: ' + row['path'])
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        need(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'Source Git blob drift: ' + row['path'])
    return len(live)


class Rectangle:
    def __init__(self, n, K, G, rho):
        need(n >= 1 and G >= 1 and K >= G + 1 and 0 <= rho < K, 'Outside stated domain')
        self.n, self.K, self.G, self.rho = n, K, G, rho
        self.B, self.A = 1 << G, 1 << (K - 1)
        self.Y, self.C = 1 << ((n + 1) * K - rho), 1 << (n * G)
        self.rs = [1 << (i * K) for i in range(n)]
        self.bs = [1 << (i * G) for i in range(n)]
        self.masks = [sum(((c >> i) & 1) * self.rs[i] for i in range(n)) for c in range(1 << n)]
        self.loads = [sum(((c >> i) & 1) * self.bs[i] for i in range(n)) for c in range(1 << n)]

    def digits(self, t):
        return [(t >> (i * self.G)) & (self.B - 1) for i in range(self.n)]

    def parity(self, u):
        return sum(((u >> (i * self.G)) & 1) << i for i in range(self.n))

    def pack(self, y):
        return sum(((y >> (i * self.K)) & 1) * self.bs[i] for i in range(self.n))

    def first_offset(self, t, z):
        return 2 * sum(((z >> i) & 1) * v * self.rs[i] for i, v in enumerate(self.digits(t)))

    def second_offset(self, t, z):
        return sum(((z >> i) & 1) * (1 - 2 * v) * self.rs[i] for i, v in enumerate(self.digits(t)))

    def early(self, y, t, z, inverse=False):
        if inverse:
            loaded = (t + self.pack(y ^ self.masks[z])) % self.C
            before_second = (y - self.second_offset(loaded, z)) % self.Y
            original_t = (loaded - self.pack(before_second)) % self.C
            return (before_second - self.first_offset(original_t, z)) % self.Y, original_t
        first = (y + self.first_offset(t, z)) % self.Y
        loaded = (t + self.pack(first)) % self.C
        second = (first + self.second_offset(loaded, z)) % self.Y
        return second, (loaded - self.pack(second ^ self.masks[z])) % self.C

    def actual(self, state, inverse=False):
        y, t, u, c = state
        if inverse:
            loaded_u = (u + self.loads[c]) % self.C
            y, t = self.early(y, t, self.parity(loaded_u), inverse=True)
            original_u = (loaded_u - self.loads[c]) % self.C
            y, t = self.early(y, t, self.parity(original_u), inverse=True)
            return y, t, original_u, c
        y, t = self.early(y, t, self.parity(u))
        loaded_u = (u + self.loads[c]) % self.C
        y, t = self.early(y, t, self.parity(loaded_u))
        return y, t, (loaded_u - self.loads[c]) % self.C, c

    def ideal(self, state):
        y, t, u, c = state
        return y ^ self.masks[c], t, u, c

    def guard(self, state, *, incoming=True, source_load=True, target=True):
        y, t, u, c = state
        carry = 0
        for i, (ti, ui) in enumerate(zip(self.digits(t), self.digits(u))):
            ci = (c >> i) & 1
            q = (ui & 1) | ci
            a = (y >> (i * self.K)) & 1
            g = (y >> (i * self.K + 1)) & (self.A - 1)
            if q and (ti == self.B - 1 or (incoming and carry)):
                return False
            if i < self.n - 1:
                if source_load and ui + ci >= self.B:
                    return False
                if target and g + q * ti >= self.A:
                    return False
            carry = (ti + a + carry) // self.B
        return True

    def previous_guard(self, state):
        return all(t < self.B - 1 for t in self.digits(state[1])) and self.guard(state)

    def index(self, state):
        y, t, u, c = state
        return (((c * self.C + u) * self.C + t) * self.Y + y)

    def state(self, index):
        index, y = divmod(index, self.Y)
        index, t = divmod(index, self.C)
        c, u = divmod(index, self.C)
        return y, t, u, c


def transfer(A, B, last=False):
    z = A * B // 2
    active = 3 * B // 2 if last else 3 * B // 2 - 1
    safe = 2 * A * (B - 1)
    if not last:
        safe -= (B - 1) * (B - 2)
    return [[z * (2 * B - 1) + active * safe, z], [z * (2 * B - 3), 3 * z]]


def density(n, K, G):
    A, B = 1 << (K - 1), 1 << G
    row = [1, 0]
    for i in range(n):
        matrix = transfer(A, B, last=i == n - 1)
        row = [sum(row[j] * matrix[j][k] for j in range(2)) for k in range(2)]
    return Fraction(sum(row), (4 * A * B * B) ** n)


def transition_checks():
    cases = 0
    pairs = [(K, G) for G in range(1, 4) for K in range(G + 1, G + 4)] + [(6, 2)]
    for K, G in pairs:
        A, B = 1 << (K - 1), 1 << G
        for last in (False, True):
            matrix = [[0, 0], [0, 0]]
            # Enumerate (g,a,t,u,c,d); neither formula nor guard() is used.
            for g, a, t, u, c, d in itertools.product(
                    range(A), range(2), range(B), range(B), range(2), range(2)):
                cases += 1
                active = (u & 1) or c
                if active and (d or t == B - 1):
                    continue
                if not last and (u + c >= B or g + active * t >= A):
                    continue
                matrix[d][(t + a + d) // B] += 1
            need(matrix == transfer(A, B, last), 'Digit transfer count')
    return dict(parameter_pairs=pairs, enumerated_cases=cases)


def check_payloads(rect, records, holes):
    ordered = sorted(records)
    need([dst for dst, _ in ordered] == sorted(holes), 'Repair destinations do not fill holes exactly')
    for dst, payload in ordered:
        need(payload == rect.index(rect.ideal(rect.state(dst))), 'Wrong repaired payload')


def exhaustive(n, K, G, rho, repair=False):
    rect = Rectangle(n, K, G, rho)
    seen, records, wrong_keys, holes = set(), [], [], []
    good_count = old_count = agreement = core = states = 0
    for c, u, t, y in itertools.product(range(1 << n), range(rect.C), range(rect.C), range(rect.Y)):
        state = y, t, u, c
        expected = rect.ideal(state)
        output = rect.actual(state)
        recovered = rect.actual(output, inverse=True)
        need(recovered == state, 'Literal inverse')
        idx, outidx = rect.index(state), rect.index(output)
        need(outidx not in seen, 'Raw map is not injective')
        seen.add(outidx)
        good = rect.guard(state)
        need(rect.guard(expected) == good, 'Ideal guard invariance')
        need(rect.guard(output) == good, 'Actual guard invariance')
        if good:
            need(output == expected, 'Admitted full map is wrong')
            good_count += 1
        if rect.previous_guard(state):
            need(good, 'Previous guard not contained')
            old_count += 1
        exact = output == expected
        agreement += exact
        if n == 1:
            maximal = exact and rect.actual(expected) == state
            core += maximal
            need(good == maximal, 'One-digit maximal invariant guard')
            predicted = t < rect.B - 1 or (c == 0 and u % 2 == 0) or (c == 1 and y % 2 == 0)
            need(exact == predicted, 'One-digit exact agreement')
        if repair and not good:
            holes.append(idx)
            records.append((rect.index(rect.ideal(recovered)), idx))
            wrong_keys.append((outidx, idx))
        states += 1
    need(Fraction(good_count, states) == density(n, K, G), 'Complete-rectangle density')
    B, A = rect.B, rect.A
    old_fraction = Fraction(B - 1, B) ** n * (
        1 - Fraction(1, 2 * B) - Fraction((3 * B - 2) * (B - 2), 8 * A * B)) ** (n - 1)
    need(Fraction(old_count, states) == old_fraction, 'PR1247 density')
    need(good_count > old_count, 'Strict guard enlargement fixture')
    result = dict(n=n, K=K, G=G, rho=rho, states=states, admitted=good_count,
                  previous_admitted=old_count, agreement=agreement,
                  good_fraction=str(Fraction(good_count, states)))
    if n == 1:
        result['maximal_invariant_count'] = core
    if repair:
        check_payloads(rect, records, holes)
        rejected = False
        try:
            check_payloads(rect, wrong_keys, holes)
        except ValueError:
            rejected = True
        need(rejected, 'Wrong-key hole-filling control accepted')
        result['repair_payloads'] = len(records)
        result['wrong_key_mismatches'] = sum(payload != rect.index(rect.ideal(rect.state(dst)))
                                              for dst, payload in wrong_keys)
    return result


def mathematical_controls():
    controls = {}
    r = Rectangle(2, 3, 2, 2)
    for name, state, weakened in [
            ('incoming_carry', (1, 3, 4, 0), {'incoming': False}),
            ('source_load_carry', (0, 0, 3, 1), {'source_load': False}),
            ('wide_target_carry', (6, 1, 0, 1), {'target': False})]:
        need(not r.guard(state) and r.guard(state, **weakened), name + ' guard separation')
        need(r.actual(state) != r.ideal(state), name + ' full map must fail')
        controls[name] = dict(input=state, actual=r.actual(state), ideal=r.ideal(state))
    state = (127, 4, 0, 2)
    need(r.guard(state) and r.actual(state) == r.ideal(state), 'Harmless final carry')
    controls['final_carry_allowed'] = dict(input=state, actual=r.actual(state))
    one = Rectangle(1, 3, 2, 2)
    state = (0, 3, 0, 0)
    need(one.guard(state) and not one.previous_guard(state) and one.actual(state) == state,
         'Inactive saturation should be admitted')
    controls['inactive_saturation'] = dict(input=state, actual=one.actual(state))
    state = (0, 3, 0, 1)
    out = one.actual(state)
    need(out == one.ideal(state) and one.actual(out) != one.ideal(out), 'Unsafe agreement guard')
    controls['unsafe_agreement_guard'] = dict(input=state, first=out, second=one.actual(out))
    wide = Rectangle(2, 6, 2, 1)
    state = (62, 1, 0, 1)
    out = wide.actual(state)
    need(out[0] == wide.ideal(state)[0] and out[1] != state[1], 'Target-only false acceptance')
    controls['target_only_false_acceptance'] = dict(input=state, actual=out, ideal=wide.ideal(state))
    need(density(2, 6, 2) == Fraction(9085, 16384), 'Headline density')
    return controls


def physical_comparisons():
    sys.path.insert(0, str(ROOT / 'scripts'))
    original = importlib.import_module('audit_compact_controls')
    rng, count = random.Random(1588), 0
    regimes = dict(good=0, bad=0, admitted_saturation=0)
    for n, K, G in [(1, 3, 2), (2, 3, 2), (2, 6, 2), (3, 5, 2)]:
        for rho in range(K):
            rect = Rectangle(n, K, G, rho)
            for sample in range(32):
                state = {k: rng.randrange(1 << ((n + 1) * K if k in ('x', 'y') else n * G))
                         for k in ('u', 't', 'y', 'x', 'b')}
                if sample % 2 == 0:
                    state['t'] |= (rect.B - 1) << ((sample % n) * G)
                c = sum(((state['x'] >> (rho + i * K)) & 1) << i for i in range(n))
                quotient = state['y'] >> rho, state['t'], state['u'], c
                qout = rect.actual(quotient)
                out = original.execute(state, n, K, rho, G, late=True)
                need((out['y'] >> rho, out['t'], out['u'], c) == qout, 'Physical quotient disagreement')
                need(out['y'] % (1 << rho) == state['y'] % (1 << rho)
                     and out['x'] == state['x'] and out['b'] == state['b'], 'Physical spectators')
                need(original.execute(out, n, K, rho, G, late=True, inverse=True) == state, 'Physical inverse')
                expected = original.ideal(state, n, K, rho)
                good = rect.guard(quotient)
                current = out['y'] >> rho, out['t'], out['u'], c
                need(rect.guard(current) == good, 'Physical actual guard invariance')
                regimes['good' if good else 'bad'] += 1
                if good and rect.B - 1 in rect.digits(state['t']):
                    regimes['admitted_saturation'] += 1
                if rect.guard(current):
                    need(out == expected, 'Physical admitted map')
                else:
                    old = original.execute(out, n, K, rho, G, late=True, inverse=True)
                    out = original.ideal(old, n, K, rho)
                need(out == expected, 'Physical repair')
                top = rho + n * K
                completed = dict(out, y=out['y'] ^ (((state['x'] >> top) & 1) << top))
                full_mask = sum(((state['x'] >> (rho + i * K)) & 1) << (rho + i * K) for i in range(n + 1))
                need(completed == dict(state, y=state['y'] ^ full_mask), 'Highest-bit completion')
                count += 1
    need(all(regimes.values()), 'Physical coverage needs good, bad and admitted saturated states')
    return dict(states=count, regimes=regimes, deterministic_seed=1588)


def verify():
    source_count = pins()
    transitions = transition_checks()
    controls = mathematical_controls()
    domains = [exhaustive(*args, repair=repair) for args, repair in [
        ((1, 2, 1, 1), False), ((1, 3, 2, 2), False),
        ((2, 3, 1, 2), True), ((2, 4, 2, 3), False), ((3, 2, 1, 1), False)]]
    return dict(status='PASS_COMPACT_LATE_CARRY_GUARD', source_pins=source_count,
                domains=domains, total_states=sum(d['states'] for d in domains),
                transition_checks=transitions, controls=controls,
                physical_comparisons=physical_comparisons(),
                headline=dict(n=2, K=6, G=2, good_fraction=str(density(2, 6, 2)),
                              previous_fraction='1971/4096', gain='1201/16384'),
                scope='All-n sufficient invariant guard and density by written proof; exact maximality only for n=1. Finite checks support the proof. No new kappa.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', type=Path, help='Export receipt to a new external path')
    args = ap.parse_args()
    result = json.loads(json.dumps(verify()))
    if args.write:
        destination = args.write.resolve()
        need(not destination.exists() and not destination.is_relative_to(ROOT), 'Use a fresh external receipt path')
        destination.write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(result == json.loads((HERE / 'RESULT.json').read_text()), 'Committed receipt drift')
    print(f"{result['status']} states={result['total_states']} physical={result['physical_comparisons']['states']} "
          f"controls={len(result['controls'])} headline=9085/16384 no_new_kappa")


if __name__ == '__main__':
    main()

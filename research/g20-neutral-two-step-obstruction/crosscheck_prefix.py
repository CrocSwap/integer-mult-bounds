"""Independent tiny-domain audit of unchanged-prefix invoice reuse.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The interval scan and set-valued full replay below are independent of the
indexed candidate enumerator, bit-row invoice and prefix implementation.
"""
from collections import Counter
from itertools import product
from pathlib import Path
from types import ModuleType
import argparse
import json


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def load(path, name):
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def candidates(records):
    for left, first in enumerate(records):
        if first[0] != 'ADD':
            continue
        _, a, b, _ = first
        for right in range(left + 1, len(records)):
            if records[right][:3] != ('ADD', a, b):
                continue
            corrections = {}
            for index in range(left + 1, right):
                event = records[index]
                if event[0] != 'ADD':
                    if event[1] in (a, b):
                        break
                elif event[1:3] == (b, a):
                    break
                elif event[1] == b:
                    corrections[index] = ('ADD', a, event[2], event[3])
                elif event[2] == a:
                    corrections[index] = ('ADD', event[1], b, event[3])
            else:
                yield left, right, a, b, corrections


def rewrite(records, candidate):
    left, right, _, _, corrections = candidate
    result = []
    for index, event in enumerate(records):
        if index not in (left, right):
            result.append(event)
            if index in corrections:
                result.append(corrections[index])
    return result


def independent_full(records, start, final, owned, distances, direct):
    rows, frames = [{i} for i in range(len(start))], list(start)
    paid, new = Counter(), set()

    def route(role, target):
        source = frames[role]
        if source != target:
            if source is None:
                need(role in owned and not rows[role], 'role in owned and not rows[role]')
            elif rows[role]:
                paid[distances[source][target]] += 1
                if (source, target) not in direct:
                    new.add((source, target))
            else:
                need(distances[source][target] > 0, 'distances[source][target] > 0')
            frames[role] = target

    for event in records:
        op, destination = event[:2]
        if op == 'ERASE':
            need(destination in owned, 'destination in owned')
            rows[destination] = set()
            frames[destination] = event[2]
        else:
            need(op == 'ADD', "op == 'ADD'")
            source, frame = event[2:]
            if rows[source]:
                route(destination, frame)
                route(source, frame)
                rows[destination] ^= rows[source]
    endpoint = [sum(1 << i for i in row) for row in rows]
    for role, target in enumerate(final):
        if role in owned:
            need(not rows[role], 'not rows[role]')
        else:
            route(role, target)
    return paid, new, endpoint


def fingerprint(saved):
    return {index: (tuple(state.rows), tuple(state.frames), tuple(sorted(state.paid.items())),
                    frozenset(state.new_paid)) for index, state in saved.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, default=Path(__file__).with_name('prefix_invoice.py'))
    parser.add_argument('--full', type=Path, default=Path(__file__).with_name('native_floor.py'))
    args = parser.parse_args()
    prefix = load(args.prefix, 'prefix_review_subject')
    full = load(args.full, 'full_review_subject')
    distances = {a: {b: abs([0, 1, 3][a] - [0, 1, 3][b]) for b in range(3)}
                 for a in range(3)}
    direct = {(0, 1), (1, 0), (1, 2), (2, 1)}
    alphabet = [('ADD', a, b, (a + 2*b) % 3) for a in range(3) for b in range(3) if a != b]
    alphabet += [('ERASE', 2, 0), ('ERASE', 2, None)]
    start, final, owned = [0, 1, None], [2, 0, 2], {2}
    words = intervals = zero_contacts = 0
    for length in range(6):
        for middle in product(alphabet, repeat=length):
            records = [('ERASE', 2, None), *middle, ('ERASE', 2, 2)]
            recipes = list(candidates(records))
            saved = prefix.snapshots(records, recipes, start, owned, distances, direct)
            before = fingerprint(saved)
            endpoint = independent_full(records, start, final, owned, distances, direct)[2]
            for recipe in recipes:
                changed = rewrite(records, recipe)
                paid, new, changed_endpoint = independent_full(changed, start, final, owned, distances, direct)
                need(changed_endpoint == endpoint, 'changed_endpoint == endpoint')
                ordinary = full.invoice(changed, start, final, owned, distances, direct)
                need(ordinary[0] == paid and ordinary[2] == new, 'ordinary[0] == paid and ordinary[2] == new')
                need(prefix.changed_invoice(records, recipe, saved, final, endpoint) == (paid, new), 'prefix.changed_invoice(records, recipe, saved, final, endpoint) == (paid, new)')
                need(fingerprint(saved) == before, 'fingerprint(saved) == before')
                intervals += 1
                zero_contacts += not recipe[4]
            words += 1
    records = [('ADD', 0, 1, 0), ('ADD', 0, 1, 1)]
    recipe = next(candidates(records))
    start2, final2 = [0, 0], [2, 1]
    saved = prefix.snapshots(records, [recipe], start2, set(), distances, direct)
    controls = 0
    for bad_saved, endpoint in (({}, [1, 2]), (saved, [3, 2])):
        try:
            prefix.changed_invoice(records, recipe, bad_saved, final2, endpoint)
        except ValueError:
            controls += 1
        else:
            raise AssertionError('prefix rejection control accepted')
    # Final returns are deliberately nonempty, and a snapshot must precede deletion.
    need(prefix.changed_invoice(records, recipe, saved, final2, [1, 2])[0] == Counter({3: 1, 1: 1}), 'prefix.changed_invoice(records, recipe, saved, final2, [1, 2])[0] == Counter({3: 1, 1: 1})')
    print(json.dumps({'words': words, 'legal_intervals': intervals, 'zero_contact_intervals': zero_contacts,
                      'saved_state_isolation': 'pass', 'rejection_controls': controls,
                      'nonempty_final_return_control': 'pass'}, sort_keys=True))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Extract the retained helper paths and check their full local contract."""

from collections import Counter
from copy import deepcopy
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
SOURCE = LANES / 'history-encoding/independent-skeleton-20261018'
PAYLOAD_PIN = '8fe1147e5cb80d9f1d9ef309b0ee6f42b1a64cc5ebabd19b818623c246c9fd64'
NATIVE = LANES / 'new-native-recipes-20261017'


def need(test, message):
    if not test:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def helper_events(events):
    out = []
    for event in events:
        tag = event[0]
        if tag in ('phase', 'zero_buffer'):
            out.append(event)
        elif tag in ('climb', 'adapter'):
            if event[2] >= 224:
                out.append(event)
        elif tag == 'warp':
            need(event[1][0] == 'L', 'Native warp uses a live role')
            if event[1][1] >= 224:
                out.append(event)
        elif tag == 'residual_adapter':
            need(event[2] >= 224, 'Residual wrapper uses a helper')
            out.append(event)
        elif tag == 'scalar':
            if event[1][0] == 'clear':
                need(event[1][1] == ['C', 0], 'Only owned C0 is cleared')
                out.append(event)
            else:
                need(event[1][0] == 'add', 'Only the data transfer is removed')
        else:
            need(tag == 'monomial_view', 'Known source event')
    return deepcopy(out)


def replay(events, canonical, original):
    frames = list(canonical['start'])
    words = [[] for _ in frames]
    active = set()
    allocated = set()
    peak = 0
    c0 = 0
    for event in events:
        tag = event[0]
        if tag == 'climb':
            _, _, wire, old, new, rank = event
            need(224 <= wire < 632 and frames[wire] == old, 'Helper child input')
            need(len(canonical['frames'][new]) - len(canonical['frames'][old]) == rank > 0,
                 'Helper child rank')
            frames[wire] = new
        elif tag == 'warp':
            _, token, symbol, old, new = event
            need(token[0] == 'L' and 224 <= token[1] < 632, 'Helper warp role')
            wire = token[1]
            need(frames[wire] == old, 'Helper warp input')
            frames[wire] = new
            if words[wire] and words[wire][-1] == -symbol:
                words[wire].pop()
            else:
                words[wire].append(symbol)
        elif tag == 'adapter':
            _, side, wire, frame = event
            need(224 <= wire < 632 and frames[wire] == frame, 'Helper endpoint adapter')
            expected = canonical['start'] if side == 'old_to_new' else canonical['final']
            need(side in ('old_to_new', 'new_to_old') and expected[wire] == frame,
                 'Helper adapter endpoint')
        elif tag == 'residual_adapter':
            _, side, wire, start, *tail = event
            final = tail[0] if tail else 1
            need(224 <= wire < 632 and side in ('pre', 'post'), 'Residual helper role')
            need((start, final) == (canonical['start'][wire], canonical['final'][wire]),
                 'Residual helper endpoint pair')
            need(frames[wire] == (start if side == 'pre' else final), 'Residual wrapper cut')
        elif tag == 'zero_buffer':
            _, op, owner = event
            need(224 <= owner < 632, 'Retained private buffer owner')
            if op == 'alloc':
                need(owner not in active and owner not in allocated, 'Single zero allocation')
                active.add(owner)
                allocated.add(owner)
                peak = max(peak, len(active))
            else:
                need(op == 'free' and owner in active, 'Retained zero return')
                active.remove(owner)
        elif tag == 'scalar':
            need(event[1] == ['clear', ['C', 0]] and event[2] == 0, 'Owned zero clear only')
            c0 = 0
        else:
            need(tag == 'phase', 'No data access or helper scalar transfer')
    need(not active and len(allocated) == 91 and c0 == 0, 'All private roles return zero')
    need(all(not w for w in words), 'Every helper logical warp word cancels')
    need(frames[:224] == canonical['start'][:224], 'All data roles are untouched')
    need(frames[224:] == canonical['final'][224:], 'Every helper endpoint is retained')
    # This comparison includes event order, all signed warps, and every wrapper.
    need(events == helper_events(original), 'Exact retained helper subsequence')
    return peak


def native_binding(provider, item, events):
    directory = NATIVE / provider
    dependencies = item['native_dependencies']
    for name, pin in dependencies['recipe_sha256'].items():
        need(digest(directory / name) == pin, 'Pinned native recipe: ' + name)
    need(digest(directory / 'GENERATION-RECEIPT.json') == dependencies['generation_receipt_sha256'],
         'Pinned generation receipt')
    recipe_file = json.loads((directory / 'CLIFFORD-RECIPES.json').read_text())
    residual_file = json.loads((directory / 'RESIDUAL-ADAPTERS.json').read_text())
    children = {(r['old'], r['new']): r for r in recipe_file['children']}
    warps = {(r['sign'], r['op'], r['old'], r['new']): r for r in recipe_file['warps']}
    used_children, used_warps, used_residuals = set(), set(), set()
    monomial_keys = {'matrix_rows', 'offset', 'quadratic_rows', 'linear_Z4', 'phase'}
    for event in events:
        if event[0] == 'climb':
            key = tuple(event[3:5])
            recipe = children[key]
            need(recipe['rank'] == event[5], 'Serialized helper child rank')
            need(set(recipe) == {'old', 'new', 'rank', 'left', 'right'}, 'One-array child schema')
            need(set(recipe['left']) == set(recipe['right']) == monomial_keys,
                 'No second live array in a child recipe')
            used_children.add(key)
        elif event[0] == 'warp':
            symbol, old, new = event[2:]
            key = (1 if symbol > 0 else -1, abs(symbol), old, new)
            recipe = warps[key]
            need(recipe['rank'] == 0 and recipe['right'] is None, 'One-array monomial warp')
            need(set(recipe['left']) == monomial_keys, 'No second live array in a warp')
            used_warps.add(key)
        elif event[0] == 'residual_adapter':
            entry, *tail = event[3:]
            final = tail[0] if tail else 1
            key = f'{entry}:{final}' if final != 1 else str(entry)
            recipe = residual_file['recipes'][key]
            need(set(recipe['left']) == set(recipe['right']) == monomial_keys,
                 'One-array residual wrappers')
            used_residuals.add(key)
    return {
        'children': [children[k] for k in sorted(used_children)],
        'warps': [warps[k] for k in sorted(used_warps)],
        'residuals': {k: residual_file['recipes'][k] for k in sorted(used_residuals)},
        'source_dependencies': dependencies,
    }


def main():
    raw = gzip.decompress((SOURCE / 'INDEPENDENT-SKELETON-PROGRAMS.json.gz').read_bytes())
    need(sha256(raw).hexdigest() == PAYLOAD_PIN, 'Frozen independent-skeleton payload')
    source = json.loads(raw)
    output = {'schema': 'retained-helper-completion-v1', 'source_payload_decompressed_sha256': PAYLOAD_PIN,
              'providers': {}}
    checks = {'status': 'PASS_RETAINED_HELPER_COMPLETION', 'providers': {}}
    for provider, item in source['providers'].items():
        canonical = item['canonical']
        events = helper_events(item['programs']['forward'])
        need(events == helper_events(item['programs']['backward']), 'Both orientations use the same helper word')
        peak = replay(events, canonical, item['programs']['forward'])
        recipes = native_binding(provider, item, events)
        tags = Counter(e[0] for e in events)
        profile = Counter(e[5] for e in events if e[0] == 'climb')
        need(dict(profile) == {1: 1609, 2: 512, 3: 172, 4: 33}, 'Exact helper profile')
        need(sum(profile.values()) == 2326 and sum(k * v for k, v in profile.items()) == 3281,
             'Helper child count and rank mass')
        expected_widths = Counter(len(canonical['frames'][canonical['final'][p]])
                                  - len(canonical['frames'][canonical['start'][p]])
                                  for p in range(224, 632))
        need(sum(k * v for k, v in expected_widths.items()) == 3281, 'All retained productive helper progress')
        controls = []
        bad = deepcopy(events)
        bad.pop(next(i for i, e in enumerate(bad) if e[0] == 'warp'))
        for name, mutation in [('missing helper warp', bad),
                               ('data read', events + [['scalar', ['add', ['L', 224], ['L', 0], 1, 1], 1]]),
                               ('missing residual wrapper', [e for e in events if e[0] != 'residual_adapter'])]:
            try:
                replay(mutation, canonical, item['programs']['forward'])
            except ValueError:
                controls.append(name)
            else:
                raise ValueError('Negative control accepted: ' + name)
        output['providers'][provider] = {
            'canonical': {k: canonical[k] for k in ('h', 'v', 'frames', 'start', 'final', 'warps', 'zero_buffers')},
            'events': events, 'native_recipes': recipes,
            'touched_live_roles': list(range(224, 632)),
            'untouched_live_roles': list(range(224)),
        }
        checks['providers'][provider] = {
            'arbitrary_helper_columns': 408, 'untouched_data_columns': 224,
            'native_profile': dict(sorted(profile.items())), 'native_children': 2326, 'native_rank_mass': 3281,
            'productive_helper_widths': dict(sorted(expected_widths.items())),
            'events': dict(sorted(tags.items())), 'private_zero_allocations': 91, 'private_zero_peak': peak,
            'owned_C_roles_reserved': 8, 'top_level_real_scalar_bound': 2 * tags['scalar'],
            'monomial_map_bound_including_child_sides': 2 * tags['climb'] + tags['warp'] + tags['adapter'] + tags['residual_adapter'],
            'same_signed_native_subsequence_as_both_source_words': True,
            'helper_data_scalar_couplings': 0, 'all_net_helper_warp_words_empty': True,
            'new_native_phase_recipes': 0, 'negative_controls': controls,
        }
        print(provider, checks['providers'][provider], flush=True)
    payload = encoded(output)
    (HERE / 'HELPER-COMPLETION-PROGRAMS.json.gz').write_bytes(gzip.compress(payload, mtime=0))
    checks['payload_decompressed_sha256'] = sha256(payload).hexdigest()
    checks['checker_sha256'] = digest(Path(__file__))
    checks['source_payload_decompressed_sha256'] = PAYLOAD_PIN
    checks['scope'] = ('Exact local helper completion. The supplied native recipes are pinned predecessor recipes. '
                       'No new data response, global owner schedule, or complete kappa calculation is claimed.')
    (HERE / 'CHECKS.json').write_text(json.dumps(checks, sort_keys=True, indent=2) + '\n')
    print('PASS_RETAINED_HELPER_COMPLETION', checks['payload_decompressed_sha256'])


if __name__ == '__main__':
    main()

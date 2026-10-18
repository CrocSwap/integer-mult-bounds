#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Literal T74 owners, 86-buffer private stock, rejection controls and exact moment of the new allocation.

Adapted from Mason Hale's PR2917 check_allocation.py, which retains Tekalign's independent integer
chronology/mask checker (allocation/vendor/independent_owners.py) and Jeremy Diviney's PR2908 integration.
The provider words are this package's data/WORD-*.json.gz (PR2917's words plus four paired extractions);
the per-helper widths and local profiles are re-derived from them and must equal allocation/PROVIDERS.json.
The exact dyadic moment auditor is PR2917's with its authenticated baseline re-pinned to the PR2930 headline.
Marius-Paul Dumitrean, with substantial AI assistance (Claude Code). Native/global/outer admission is separate.
"""
import argparse, gzip, hashlib, json, sys, types
from pathlib import Path
P = Path(__file__).resolve().parent
BUFFERS, PHYSICAL = 86, 66808

def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    if not __debug__:
        raise SystemExit('refusing python -O: this checker relies on assertions')
    out = args.work.resolve()
    assert not out.exists() and not out.is_relative_to(P)
    allocation_pins = read(P / 'ALLOCATION-PINS.json')
    actual_pins = {p.relative_to(P).as_posix(): sha(p) for p in (P / 'allocation').rglob('*') if p.is_file()}
    assert actual_pins == allocation_pins, 'complete allocation inventory binding'
    word_pins = read(P / 'PINS.json')
    assert all(sha(P / name) == digest for name, digest in word_pins.items()), 'source word/code pins'
    out.mkdir(parents=True)
    owners = load('normal45_owners', P / 'allocation/vendor/independent_owners.py')
    moment = load('normal45_moment', P / 'tools/audit_allocation_moment.py')
    frames = load('normal45_frames', P / 'vendor/preload_move.py')
    providers, word_records, private_counts = {}, {}, set()
    for tag, provider in [('base', 'gauge44'), ('extra', 'extra')]:
        path = P / f'data/WORD-{tag}.json.gz'
        word = read(path)
        profile, inventory = frames.frame_report(word)
        assert profile == word['report']['local_profile'] and inventory == word['report']['width_inventory']
        helpers = sorted(set(range(224, 704)) - set(word['removed']))
        widths = [len(word['helper_final'].get(str(h), [0] * 9)) - len(word['start_extra'].get(str(h), [])) for h in helpers]
        assert len(helpers) == 408 and len(word['centers']) == 8
        buffers = {r for gate in word['cleanup'] for r in (gate[1:3] if gate[0] == 'add' else gate[1:2]) if r >= 704}
        assert buffers == {704 + int(h) for h in word['helper_final']}, 'actual cleanup buffer/end-point bijection'
        assert len(buffers) == BUFFERS, 'all 86 private buffers charged'
        private_counts.add(len(buffers))
        providers[provider] = {'widths': widths, 'actual_paid_profile': {int(k): v for k, v in profile.items()}}
        word_records[tag] = {'sha256': sha(path), 'local_profile': profile, 'width_inventory': inventory, 'private_buffers': len(buffers)}
    assert len(private_counts) == 1
    registry = read(P / 'allocation/PROVIDERS.json')
    assert {k: {'widths': v['widths'], 'actual_paid_profile': {int(r): n for r, n in v['actual_paid_profile'].items()}} for k, v in registry.items()} == providers
    base = P / 'allocation'
    order, fill = read(base / 'ORDER.json'), read(base / 'FILL.json.gz')
    raw_dispatch = read(base / 'DISPATCH.json')
    dispatch = {(s, r): provider for s, r, provider in raw_dispatch}
    assert len(dispatch) == len(raw_dispatch), 'unique actual call/provider binding'
    profile = read(base / 'PROFILE.json')
    plan, template = read(base / 'vendor/PLAN.json.gz'), read(base / 'vendor/TEMPLATE.json.gz')
    T = len(order) // 9
    def check(candidate=fill, claimed=profile):
        return owners.check(T, order, candidate, dispatch, claimed, plan, template, providers)
    result, _, _ = check()
    assert T == 74 and result['roles'] == 271728
    result['physical'] = result['live'] + len(helpers) + len(word['centers']) + next(iter(private_counts)) + 2
    assert result['physical'] == PHYSICAL
    result['physical_source'] = 'Actual 86-register private cleanup namespace, 408 live helpers, eight centres and two guards; global stock checked separately.'
    controls = {}
    def reject(name, candidate=fill, claimed=profile):
        try:
            check(candidate, claimed)
        except ValueError as error:
            controls[name] = str(error)
        else:
            raise AssertionError('owner corruption accepted: ' + name)
    reject('missing_role', {**fill, 'rows': fill['rows'][:-1]})
    first = fill['rows'][0]
    j = next(i for i, r in enumerate(fill['rows'][1:], 1) if r[0] == first[0])
    def mutate(index, row):
        rows = list(fill['rows']); rows[index] = row
        return {**fill, 'rows': rows}
    duplicate = list(fill['rows'][j]); duplicate[1] = first[1]
    reject('duplicate_helper', mutate(j, duplicate))
    collision = list(fill['rows'][j]); collision[2:5] = first[2:5]
    reject('same_call_family_collision', mutate(j, collision))
    overflow = list(first); overflow[5] = 49
    reject('capacity_overflow', mutate(0, overflow))
    wrong = dict(profile); wrong['1'] = wrong.get('1', 0) + 1
    reject('changed_paid_profile', claimed=wrong)
    exact = moment.run(base, base / 'baseline')
    claim = read(P / 'CLAIM.json')
    assert {str(k): v for k, v in profile.items()} == {str(k): v for k, v in claim['profile'].items()}, 'claimed complete profile'
    assert all(sha(P / name) == digest for name, digest in {**word_pins, **allocation_pins}.items()), 'input drift'
    result.update(status='PASS_NORMAL45_LITERAL_OWNERS_AND_EXACT_MOMENT', providers=word_records,
                  controls=controls, moment=exact, allocation_sha256=allocation_pins,
                  scope='Recounted local frames, exact whole-owner geometry and directed moment; algebra/native/global/outer admission remains separately required.')
    (out / 'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'], exact['target_decimal'], exact['gain_decimal'])

if __name__ == '__main__':
    main()

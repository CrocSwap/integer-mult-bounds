# SPDX-License-Identifier: Apache-2.0
"""Semantic and packaging controls for verify.py: every mutation must be rejected by its named check.

Run: python3 -I -B -m unittest discover -s research/frontier1094-emitted-ledger-seed78 -p test_package.py -v
(about 10 s; the selected frontier1094 capsule is decoded once and copied per control)
"""
import gzip
import io
import json
import pickle
import random
import shutil
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as v  # noqa: E402

BASE, _ = v.load('frontier1094')
BLOB = pickle.dumps(BASE, protocol=5)


def fresh():
    return pickle.loads(BLOB)


def rehash(d):
    # a consistent forgery: the template's embedded programs and every call hash follow the edit
    d['template']['local_providers']['gauge44']['local_programs'] = pickle.loads(pickle.dumps(d['programs']))
    hashes = {o: v.sha(v.compact(p)) for o, p in d['programs'].items()}
    for c in d['template']['calls']:
        c['local_program_sha256'] = hashes[c['orientation']]


def dim(vectors):
    return len(v.basis(vectors))


def odd_orthogonal(rows, n):
    """A vector of odd weight orthogonal (mod 2) to every row, or None."""
    pivots = {}                                      # pivot column -> fully reduced row
    for r in rows:
        for c, p in pivots.items():
            if r >> c & 1:
                r ^= p
        if r:
            c = r.bit_length() - 1
            for k in list(pivots):
                if pivots[k] >> c & 1:
                    pivots[k] ^= r
            pivots[c] = r
    for f in range(n):
        if f in pivots:
            continue
        x = 1 << f
        for c, p in pivots.items():
            if p >> f & 1:
                x |= 1 << c
        if x.bit_count() & 1:
            return x
    return None


class Controls(unittest.TestCase):
    def rejects(self, d, label):
        with self.assertRaises(v.Reject) as ctx:
            v.check(d)
        self.assertTrue(str(ctx.exception).startswith(label), 'rejected by %r, expected %r' % (str(ctx.exception), label))

    # --- positives
    def test_selected_positive_and_order_invariance(self):
        self.assertEqual(v.check(fresh())['ledger'], {int(k): n for k, n in BASE['assembly']['complex_profile'].items()})
        d = fresh()
        random.Random(78).shuffle(d['template']['idle_children'])
        random.Random(79).shuffle(d['frames'])
        self.assertEqual(v.check(d)['deficit'], 5120)

    # --- the local programs
    def test_climb_rank_relabel(self):
        d = fresh()
        e = next(e for e in d['programs']['forward'] if e[0] == 'climb' and e[5] == 1)
        e[5] = 2
        rehash(d)
        self.rejects(d, 'L6')

    def test_non_nested_climb_same_rank(self):
        d = fresh()
        F = d['word']['frames']
        for e in d['programs']['forward']:
            if e[0] == 'climb' and dim(F[e[3]]) > 0:
                alt = next((j for j, f in enumerate(F) if dim(f) == dim(F[e[4]]) and not v.nested(F[e[3]], f)), None)
                if alt is not None:
                    e[4] = alt                     # same dimension difference, frames no longer nested
                    break
        rehash(d)
        self.rejects(d, 'L5')

    def test_unknown_program_event(self):
        d = fresh()
        d['programs']['backward'].append(['child', 1])
        rehash(d)
        self.rejects(d, 'L4 closed program vocabulary')

    def test_unknown_schedule_event(self):
        d = fresh()
        d['template']['execution_schedule'].append({'kind': 'recursive_child', 'replica': 0})
        self.rejects(d, 'L4 closed schedule vocabulary')

    def test_climb_moved_to_another_register(self):
        # same rank, same histogram and mass: the frame replay sees the register's chain break
        d = fresh()
        e = next(e for e in d['programs']['forward'] if e[0] == 'climb' and e[2] < 224 and e[5] == 1)
        e[2] = (e[2] + 1) % 224
        rehash(d)
        self.rejects(d, 'L5')

    def test_descending_climb(self):
        d = fresh()
        e = next(e for e in d['programs']['forward'] if e[0] == 'climb' and e[5] == 1)
        e[3], e[4] = e[4], e[3]
        rehash(d)
        self.rejects(d, 'L5')

    def test_broken_chain_same_dimension_nested(self):
        # from-frame replaced by a different frame of the same dimension that still lies in the to-frame
        d = fresh()
        F = d['word']['frames']
        done = False
        for e in d['programs']['forward']:
            if e[0] == 'climb' and dim(F[e[3]]) > 0:
                for j, f in enumerate(F):
                    if j != e[3] and dim(f) == dim(F[e[3]]) and v.nested(f, F[e[4]]):
                        e[3] = j
                        done = True
                        break
            if done:
                break
        self.assertTrue(done)
        rehash(d)
        self.rejects(d, 'L5 climb leaves its register')

    def test_centre_direction_flipped(self):
        d = fresh()
        e = next(e for e in d['programs']['forward'] if e[0] == 'center')
        e[2], e[3] = e[3], e[2]
        rehash(d)
        self.rejects(d, 'L7')

    def test_whole_local_stage_dropped_consistently(self):
        # recipe, calls and local sweeps of one pair-0 stage removed together: coverage and dispatch stay
        # consistent; the dropped calls' owner-map slots are now executed by no route (conservation,
        # mass and the certificate comparison reject it as well)
        d = fresh()
        T = d['template']
        stage = next(x['stage'] for x in T['recipe'] if x['kind'] == 'local' and x['pair'] == 0)
        T['recipe'] = [x for x in T['recipe'] if not (x['kind'] == 'local' and x['stage'] == stage)]
        T['calls'] = [c for c in T['calls'] if c['stage'] != stage]
        T['execution_schedule'] = [e for e in T['execution_schedule']
                                   if not (e['kind'] == 'local_cover_sweep' and e.get('stage') == stage)]
        self.rejects(d, 'L11 every owner-map slot')

    def test_data_route_family_duplicated(self):
        d = fresh()
        owners = d['template']['calls'][0]['owners']
        owners[0][0] = owners[1][0]
        self.rejects(d, 'L10')

    def test_embedded_programs_differ(self):
        d = fresh()
        d['template']['local_providers']['gauge44']['local_programs']['forward'].append(['scalar'])
        self.rejects(d, 'L3 dispatched programs')

    def test_adapter_at_wrong_frame(self):
        d = fresh()
        e = next(e for e in d['programs']['forward'] if e[0] == 'adapter' and e[1] == 'old_to_new')
        e[3] = 1 if e[3] != 1 else 2
        rehash(d)
        self.rejects(d, 'L5 adapter')

    def test_scalar_at_wrong_frame(self):
        d = fresh()
        e = next(e for e in d['programs']['forward'] if e[0] == 'scalar' and e[1][0] == 'add')
        e[2] = e[2] + 1
        rehash(d)
        self.rejects(d, 'L5 scalar')

    def test_extra_phase_marker(self):
        d = fresh()
        d['programs']['forward'].insert(5, ['phase', 'extra_child_rank_48'])
        rehash(d)
        self.rejects(d, 'L4 phase sequence')

    # --- schedule
    def test_local_sweep_repointed(self):
        # no program edit: one call is dispatched twice and another never
        d = fresh()
        e = next(e for e in d['template']['execution_schedule']
                 if e['kind'] == 'local_cover_sweep' and e['stage'] == 3 and e['replica'] == 0)
        e['stage'] = 0
        self.rejects(d, 'L9 local sweeps dispatch')

    def test_foreign_provider(self):
        d = fresh()
        T = d['template']
        T['local_providers']['evil'] = pickle.loads(pickle.dumps(T['local_providers']['gauge44']))
        self.rejects(d, 'L9 one local provider')

    def test_multi_replica_sweep(self):
        d = fresh()
        e = next(e for e in d['template']['execution_schedule'] if e['kind'] == 'local_cover_sweep')
        e['replicas'] = [e['replica'], (e['replica'] + 1) % 16]
        self.rejects(d, 'L9 schedule events act on one replica')

    def test_bank_sweep_reads_idle_children(self):
        d = fresh()
        e = next(e for e in d['template']['execution_schedule'] if e['kind'] == 'bank_padding_cover_sweep')
        e['children_source'] = 'idle_children'
        self.rejects(d, 'L8')

    def test_slot_parked_in_phantom_replica(self):
        # one slot moved to a nonexistent replica (route follows), with a ghost copy of the original left
        # in the owner map: the idle recount would subtract slices that no call executes
        d = fresh()
        idx, z = next((i, z) for i, z in enumerate(d['owners']) if z['stage'] == 0 and z['replica'] == 0 and z['helper'] == 0)
        ghost = dict(z, stage=99)
        for slots in (d['owners'], d['template']['hosting']['pooled_slots']):
            slots[idx] = dict(slots[idx], owner_replica=16, family=z['family'] + 16 * 896 - z['owner_replica'] * 896)
            slots.append(dict(ghost))
        call = next(c for c in d['template']['calls'] if (c['stage'], c['replica']) == (0, 0))
        call['owners'][224][0] = d['owners'][idx]['family']
        self.rejects(d, 'L11 every owner-map slot')

    # --- calls
    def test_program_hash_swapped(self):
        d = fresh()
        c = d['template']['calls'][0]
        c['local_program_sha256'] = v.sha(v.compact(d['programs']['backward' if c['orientation'] == 'forward' else 'forward']))
        self.rejects(d, 'L3')

    def test_orientation_swap_rehashed(self):
        d = fresh()
        c = d['template']['calls'][0]
        c['orientation'] = 'backward' if c['orientation'] == 'forward' else 'forward'
        rehash(d)
        self.rejects(d, 'L2')

    def test_duplicate_call(self):
        d = fresh()
        d['template']['calls'][-1] = pickle.loads(pickle.dumps(d['template']['calls'][-2]))
        self.rejects(d, 'L1')

    def test_live_families_changed(self):
        d = fresh()
        d['template']['cover_final_correction']['charged_calls_per_cover'] -= 1
        self.rejects(d, 'L9')

    def test_extra_bank_padding_child(self):
        d = fresh()
        d['template']['bank_padding']['children'].append({'rank': 1})
        self.rejects(d, 'L8')

    def test_helper_route_moved_to_another_family(self):
        d = fresh()
        d['template']['calls'][0]['owners'][224][0] += 1
        self.rejects(d, 'L11')

    def test_short_spectators(self):
        d = fresh()
        for c in d['template']['calls']:
            route = next((desc for _, desc in c['owners'] if desc[0] == 4), None)
            if route:
                route[4] = route[4][:-1]
                break
        self.rejects(d, 'L12')

    # --- pending children and hosting
    def test_dependent_pending_axis_with_fresh_label(self):
        # label-disjoint (a new integer) but F2-dependent on a sibling child's axes
        d = fresh()
        place = {}
        for e in d['template']['execution_schedule']:
            if e['kind'] == 'idle_cover_sweep':
                for side, ch in enumerate(e['child_indices']):
                    place[ch] = (e['pair'], side)
        rec = d['phases']['recipes'][0]
        groups = {}
        for ch, ps in place.items():
            if rec['idle_children'][ch]['rank'] >= 2:
                groups.setdefault(ps, []).append(ch)
        a, b = next(g[:2] for g in groups.values() if len(g) >= 2)
        axes_a, axes_b = rec['idle_children'][a]['orthogonal_axes'], rec['idle_children'][b]['orthogonal_axes']
        new = axes_b[0] ^ axes_b[1]
        self.assertNotIn(new, axes_a + axes_b)
        self.assertEqual(dim(axes_a[1:] + [new]), len(axes_a))   # child a alone stays full rank
        axes_a[0] = new
        self.rejects(d, 'L15')

    def test_rank0_child_made_pending(self):
        # a consistent forgery of DATA-PHASES: a rank-0 child gets one axis that keeps every sibling
        # union F2-orthonormal, so only the recount against the emitted remainders sees it
        d = fresh()
        place = {}
        for e in d['template']['execution_schedule']:
            if e['kind'] == 'idle_cover_sweep':
                for side, ch in enumerate(e['child_indices']):
                    place[ch] = (e['pair'], side)
        recipes = d['phases']['recipes']
        zero = next(ch for ch in place if all(r['idle_children'][ch]['rank'] == 0 for r in recipes))
        for rec in recipes:
            union = [x for ch, ps in place.items() if ps == place[zero] for x in rec['idle_children'][ch]['orthogonal_axes']]
            axis = odd_orthogonal(union, 73)
            self.assertIsNotNone(axis)
            rec['idle_children'][zero] = dict(rec['idle_children'][zero], rank=1, orthogonal_axes=[axis])
        self.rejects(d, 'L19')

    def test_slot_gap_kept_consistent(self):
        d = fresh()
        z = next(z for z in d['owners'] if z['offset'] > 0)
        idx = d['owners'].index(z)
        z['offset'] += 1
        d['template']['hosting']['pooled_slots'][idx]['offset'] += 1
        for c in d['template']['calls']:
            if (c['stage'], c['replica']) == (z['stage'], z['replica']):
                c['owners'][224 + z['helper']][1][2] += 1
        self.rejects(d, 'L18')

    def test_owner_map_differs_from_template(self):
        d = fresh()
        d['owners'][0]['copy'] += 1          # a field no other check reads: only the identity sees it
        self.rejects(d, 'L16')

    def test_drop_idle_child(self):
        d = fresh()
        x = d['template']['idle_children'].pop()
        d['frames'] = [f for f in d['frames'] if (f['family'], f['child']) != (x['family'], x['child'])]
        self.rejects(d, 'L19')

    def test_idle_hosted_inflated(self):
        d = fresh()
        x = next(x for x in d['template']['idle_children'] if x['rank'] == 3)
        x['hosted'] += 1
        x['pending_offset'] += 1
        x['rank'] -= 1
        self.rejects(d, 'L19')

    def test_duplicate_remainder_frame(self):
        d = fresh()
        one = next(i for i, f in enumerate(d['frames']) if len(f['orthogonal_axes']) == 1)
        big = next(f for f in d['frames'] if len(f['orthogonal_axes']) == 48)
        d['frames'][one] = pickle.loads(pickle.dumps(big))
        self.rejects(d, 'L20')

    def test_dependent_remainder_frame(self):
        d = fresh()
        f = next(f for f in d['frames'] if len(f['orthogonal_axes']) == 3)
        f['orthogonal_axes'][2] = f['orthogonal_axes'][0] ^ f['orthogonal_axes'][1]
        self.rejects(d, 'L20')

    # --- the certificate
    def test_assembly_profile_tamper(self):
        d = fresh()
        p = d['assembly']['complex_profile']
        p['48'] -= 1
        p['47'] = 1
        self.rejects(d, 'L23')

    def test_independent_profile_tamper(self):
        d = fresh()
        d['independent']['1'] += 1
        self.rejects(d, 'L23 ledger equals INDEPENDENT1094')


class Packaging(unittest.TestCase):
    def rejects(self, label, **kw):
        with self.assertRaises(v.Reject) as ctx:
            v.load('frontier1094', **kw)
        self.assertTrue(str(ctx.exception).startswith(label), str(ctx.exception))

    def test_decoy_local_programs(self):
        self.rejects('B6', members={'local_programs': 'global/base/split-centres/LOCAL-PROGRAMS.json.gz'})

    def test_decoy_template(self):
        self.rejects('B4', members={'template': 'global/base/split-centres/GLOBAL-TEMPLATE.json.gz'})

    def test_foreign_local_replay_receipt(self):
        self.rejects('B6', members={'local_replay': 'global/base/split-centres/INDEPENDENT-LOCAL-REPLAY.json'})

    def test_other_owner_map(self):
        self.rejects('B7', overrides={'owners': 'research/gauge44-slots-t16/data/OWNERS.json.gz'})

    def test_flipped_archive_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / 'capsule.tar.gz'
            raw = bytearray((v.ROOT / v.SOURCES['cases']['frontier1094']['archive']['path']).read_bytes())
            raw[len(raw) // 2] ^= 1
            bad.write_bytes(bytes(raw))
            self.rejects('B1', archive_path=bad)

    def test_unsafe_tar_members(self):
        for names in (['a.json', 'a.json'], ['../escape.json']):
            buf = io.BytesIO()
            with tarfile.open(fileobj=buf, mode='w:gz') as tar:
                for n in names:
                    info = tarfile.TarInfo(n)
                    info.size = 2
                    tar.addfile(info, io.BytesIO(b'{}'))
            buf.seek(0)
            with tarfile.open(fileobj=buf, mode='r:gz') as tar, self.assertRaises(v.Reject) as ctx:
                v.safe_members(tar)
            self.assertTrue(str(ctx.exception).startswith('B2'))


if __name__ == '__main__':
    unittest.main()

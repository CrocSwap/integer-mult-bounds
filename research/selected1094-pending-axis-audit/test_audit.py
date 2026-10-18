# SPDX-License-Identifier: Apache-2.0
"""Mathematical and temporal failure controls for the independent audit."""
from collections import defaultdict
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('pending_axis_audit', Path(__file__).with_name('verify.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class PendingAxisAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins, cls.data = audit.pinned_inputs()
        cls.geo = audit.source_geometry(cls.data['template'], cls.data['phases'])
        cls.widths = audit.helper_widths(cls.data['word'])
        cls.roles = cls.data['owners']
        cls.plan = dict(cls.data['plan'], _expected_idle=cls.data['spec']['expected']['idle_remainder_profile'])
        cls.events = audit.chronological_events(cls.geo, cls.plan['order'])

    def run_sweep(self, roles=None, events=None):
        return audit.sweep(self.geo, self.widths, self.roles if roles is None else roles,
                           self.plan['order'], self.events if events is None else events)

    def replace_role(self, index, **changes):
        roles = self.roles.copy()
        roles[index] = dict(roles[index], **changes)
        return roles

    def test_selected_positive_fixture(self):
        result = audit.audit(self.geo, self.widths, self.roles, self.plan)
        self.assertEqual(result['roles'], 69120)
        self.assertEqual(result['cuts'], 481)
        self.assertEqual(result['idle_profile'], self.plan['_expected_idle'])

    def test_distinct_locally_orthonormal_sets_can_share_a_span(self):
        left, right = [7], [1, 2, 4]
        self.assertTrue(audit.orthonormal(left))
        self.assertTrue(audit.orthonormal(right))
        self.assertTrue(set(left).isdisjoint(right))
        self.assertEqual(audit.rank(left + right), 3)
        self.assertFalse(audit.orthonormal(left + right))
        self.assertEqual(left[0], right[0] ^ right[1] ^ right[2])

    def test_source_distinct_but_dependent_cross_child_axes(self):
        phases = deepcopy(self.data['phases'])
        recipe = phases['recipes'][0]
        left = recipe['idle_children'][0]['orthogonal_axes']
        right = recipe['idle_children'][14]['orthogonal_axes']
        left[0] = right[0] ^ right[1] ^ right[2]
        self.assertTrue(audit.orthonormal(left))
        self.assertEqual(audit.rank(left), len(left))
        children = [0, 1, 14]
        combined = [v for child in children for v in recipe['idle_children'][child]['orthogonal_axes']]
        self.assertEqual(len(set(combined)), len(combined))
        self.assertEqual(audit.rank(combined), len(combined) - 1)
        with self.assertRaisesRegex(audit.Rejected, '^CROSS_CHILD_GRAM$'):
            audit.source_geometry(self.data['template'], phases)

    def test_false_child_rank(self):
        phases = deepcopy(self.data['phases'])
        phases['recipes'][0]['idle_children'][0]['rank'] += 1
        with self.assertRaisesRegex(audit.Rejected, '^CHILD_RANK$'):
            audit.source_geometry(self.data['template'], phases)

    def test_changed_source_pin(self):
        pins = deepcopy(self.pins)
        pins['inputs']['owners']['sha256'] = '0' * 64
        with self.assertRaisesRegex(audit.Rejected, '^SOURCE_PIN_owners$'):
            audit.pinned_inputs(pins)

    def test_wrong_replica_source_projection(self):
        order = deepcopy(self.plan['order'])
        first = next(i for i, key in enumerate(order) if key == [0, 0])
        second = next(i for i, key in enumerate(order) if key == [1, 0])
        order[first], order[second] = order[second], order[first]
        with self.assertRaisesRegex(audit.Rejected, '^SOURCE_PROJECTION$'):
            audit.chronological_events(self.geo, order)

    def test_intervening_bridge_touch(self):
        role = self.roles[0]
        pair, _ = self.geo['placement'][role['child']]
        events = self.events.copy()
        call = next(i for i, (time, replica, event) in enumerate(events)
                    if time == role['time'] and event['kind'] == 'local_cover_sweep')
        events.insert(call + 1, (role['time'], role['owner_replica'],
                                dict(kind='bridge', src=pair, dst=(pair + 1) % 4)))
        with self.assertRaisesRegex(audit.Rejected, '^SOURCE_TOUCH_WITH_RESERVATION$'):
            self.run_sweep(events=events)

    def test_deadline_before_call(self):
        role = self.roles[0]
        events = self.events.copy()
        deadline = next(i for i, (_, replica, event) in enumerate(events)
                        if replica == role['owner_replica'] and event['kind'] == 'idle_cover_sweep'
                        and role['child'] in event['child_indices'])
        events.insert(0, events.pop(deadline))
        with self.assertRaisesRegex(audit.Rejected, '^ROLE_AFTER_IDLE_SWEEP$'):
            self.run_sweep(events=events)

    def test_cross_call_coordinate_collision(self):
        buckets = defaultdict(list)
        for i, role in enumerate(self.roles):
            key = role['owner_replica'], role['child'], role['port']
            buckets[key].append(i)
        first, second = next((indices[0], indices[1]) for indices in buckets.values()
                             if len(indices) > 1 and self.roles[indices[0]]['time'] != self.roles[indices[1]]['time'])
        roles = self.replace_role(second, offset=self.roles[first]['offset'])
        with self.assertRaisesRegex(audit.Rejected, '^RESERVATION_COLLISION$'):
            self.run_sweep(roles=roles)

    def test_gap_in_reserved_prefix(self):
        last = {}
        for i, role in enumerate(self.roles):
            key = role['owner_replica'], role['child'], role['port']
            if key not in last or role['offset'] > self.roles[last[key]]['offset']:
                last[key] = i
        index = next(i for i in last.values()
                     if self.roles[i]['offset'] + self.roles[i]['width'] <
                     len(self.geo['axes'][self.roles[i]['child'], self.roles[i]['port']]))
        roles = self.replace_role(index, offset=self.roles[index]['offset'] + 1)
        with self.assertRaisesRegex(audit.Rejected, '^OCCUPIED_PREFIX_GAP$'):
            self.run_sweep(roles=roles)

    def test_missing_role(self):
        with self.assertRaisesRegex(audit.Rejected, '^ROLE_COUNT$'):
            self.run_sweep(roles=self.roles[1:])

    def test_duplicate_helper(self):
        index = next(i for i, r in enumerate(self.roles) if r['time'] == self.roles[0]['time'] and i != 0)
        with self.assertRaisesRegex(audit.Rejected, '^ROLE_HELPER_INVENTORY$'):
            self.run_sweep(roles=self.replace_role(index, helper=self.roles[0]['helper']))

    def test_wrong_helper_width(self):
        with self.assertRaisesRegex(audit.Rejected, '^ROLE_WIDTH$'):
            self.run_sweep(roles=self.replace_role(0, width=self.roles[0]['width'] - 1))

    def test_family_binding(self):
        with self.assertRaisesRegex(audit.Rejected, '^ROLE_FAMILY_BINDING$'):
            self.run_sweep(roles=self.replace_role(0, family=self.roles[0]['family'] + 1))

    def test_noninteger_role(self):
        with self.assertRaisesRegex(audit.Rejected, '^ROLE_INTEGER_DOMAIN$'):
            self.run_sweep(roles=self.replace_role(0, owner_replica=float(self.roles[0]['owner_replica'])))

    def test_false_idle_profile(self):
        plan = deepcopy(self.plan)
        plan['_expected_idle']['1'] += 1
        with self.assertRaisesRegex(audit.Rejected, '^IDLE_PROFILE_BINDING$'):
            audit.audit(self.geo, self.widths, self.roles, plan)


if __name__ == '__main__':
    unittest.main()

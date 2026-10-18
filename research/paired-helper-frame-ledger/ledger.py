# SPDX-License-Identifier: Apache-2.0
"""Finite frame and cleanup-structure audit using literal GF(2)^9 sets.

No predecessor implementation is imported.  Scalar/operator endpoint identities,
zero-buffer restoration, native phases, allocation and moment certification are
outside this module.  A frame is its complete set of at most 512 vectors; no
Gaussian elimination or pivot representation is used.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
import hashlib
import json


DIMENSION = 9
VECTORS = frozenset(range(1 << DIMENSION))
ZERO = frozenset({0})
FIRST_TARGET, FIRST_HELPER, ORDINARY_ROLES = 112, 224, 704
HELPERS = (424, 428, 412, 331, 299, 320, 511, 304, 499)
NORMALS = (52, 76, 127, 30, 51, 75, 85, 102, 120)
PARENT_PROFILE = {1: 2407, 2: 640, 3: 262, 4: 128, 5: 26, 8: 8}
FRAME_SECTIONS = (
    'A', 'B', 'restore', 'helper_final', 'start_extra', 'centers',
    'center_frames', 'target_levels', 'cut', 'warps', 'ports', 'removed',
    'prelude_events',
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, message):
    require(type(value) is int, message)
    return value


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


@lru_cache(maxsize=8192)
def _span(generators):
    result = {0}
    for generator in generators:
        result.update(x ^ generator for x in tuple(result))
    return frozenset(result)


def span(generators):
    require(type(generators) is list, 'frame must be a vector list')
    require(all(type(x) is int and 0 <= x < 512 for x in generators),
            'frame vector outside GF(2)^9')
    return _span(tuple(generators))


def dimension(space):
    size = len(space)
    require(size > 0 and size & (size - 1) == 0, 'non-subspace cardinality')
    return size.bit_length() - 1


def frame_basis(generators):
    result = span(generators)
    require(dimension(result) == len(generators), 'dependent frame generators')
    return result


def parity(a, b):
    return (a & b).bit_count() & 1


@lru_cache(maxsize=8192)
def perpendicular(space):
    return frozenset(x for x in VECTORS if all(not parity(x, u) for u in space))


def hyperplane(normal):
    require(type(normal) is int and 0 < normal < 512, 'invalid hyperplane normal')
    return frozenset(x for x in VECTORS if not parity(x, normal))


@lru_cache(maxsize=512)
def linear_table(columns):
    require(len(columns) == 9 and all(type(x) is int and 0 <= x < 512
                                     for x in columns), 'warp column shape')
    images = [0] * 512
    for x in range(1, 512):
        bit = x & -x
        images[x] = images[x ^ bit] ^ columns[bit.bit_length() - 1]
    require(len(set(images)) == 512, 'singular warp map')
    return tuple(images)


@lru_cache(maxsize=2048)
def check_map(columns, source, target):
    """Full 512-point permutation, dual-perpendicular and frame-lift checks."""
    image = linear_table(columns)
    require(frozenset(image[x] for x in source) == target, 'warp image frame mismatch')
    inverse = [0] * 512
    for x, y in enumerate(image):
        inverse[y] = x
    # G^-T(z) is characterized directly by dot(G^-T z, e_i)=dot(z,G^-1 e_i).
    dual = tuple(sum(parity(z, inverse[1 << i]) << i for i in range(9))
                 for z in range(512))
    require(frozenset(dual[z] for z in perpendicular(source)) == perpendicular(target),
            'dual warp perpendicular mismatch')

    def lifted(point):
        x, z = point & 511, point >> 9
        gx = image[x]
        return gx | ((gx ^ dual[x] ^ dual[z]) << 9)

    def lagrangian(space):
        return {x | ((x ^ p) << 9) for x in space for p in perpendicular(space)}

    require({lifted(x) for x in lagrangian(source)} == lagrangian(target),
            'lifted warp frame mismatch')
    require({lifted(x) for x in lagrangian(ZERO)} == lagrangian(ZERO),
            'warp does not fix zero frame')
    require({lifted(x) for x in lagrangian(VECTORS)} == lagrangian(VECTORS),
            'warp does not fix full frame')
    generators = [1 << i for i in range(18)]
    def symplectic(a, b):
        return parity(a & 511, b >> 9) ^ parity(a >> 9, b & 511)
    require(all(symplectic(lifted(a), lifted(b)) == symplectic(a, b)
                for a in generators for b in generators), 'warp symplectic mismatch')
    return True


def role_map(value, live, label):
    require(type(value) is dict, label + ' must be an object')
    result = {}
    for key, generators in value.items():
        require(type(key) is str and key.isascii() and key.isdecimal()
                and str(int(key)) == key, label + ' role key')
        role = int(key)
        require(role in live and role >= FIRST_HELPER, label + ' removed or invalid helper')
        result[role] = frame_basis(generators)
    return result


def target_role(role):
    return FIRST_TARGET <= role < FIRST_HELPER


def scalar_gate(gate, allowed, frame_required=True):
    require(type(gate) is list and gate and gate[0] in ('add', 'scale'),
            'unknown scalar gate')
    require(len(gate) == (6 if gate[0] == 'add' else 5), 'scalar gate shape')
    roles = gate[1:3] if gate[0] == 'add' else gate[1:2]
    require(all(type(r) is int and r in allowed for r in roles),
            'gate references removed or invalid role')
    if gate[0] == 'add':
        require(roles[0] != roles[1], 'self addition')
        numerator, denominator = gate[3:5]
    else:
        numerator, denominator = gate[2:4]
    require(type(numerator) is int and type(denominator) is int and denominator != 0,
            'invalid scalar rational')
    coefficient = Fraction(numerator, denominator)
    require(coefficient.denominator & (coefficient.denominator - 1) == 0,
            'non-dyadic gate')
    if gate[0] == 'scale':
        numerator_abs = abs(coefficient.numerator)
        require(numerator_abs and numerator_abs & (numerator_abs - 1) == 0,
                'noninvertible dyadic scaling')
    if frame_required:
        frame_basis(gate[-1])
    else:
        require(gate[-1] is None, 'cut must have unframed gate')
    return tuple(roles)


def _histogram(counter):
    return {str(k): v for k, v in sorted(counter.items()) if v}


def _claimed_histogram(value, label):
    require(type(value) is dict, label + ' must be an object')
    result = {}
    for k, v in value.items():
        require(type(k) is str and k.isascii() and k.isdecimal()
                and str(int(k)) == k and int(k) > 0, label + ' rank key')
        require(type(v) is int and v > 0, label + ' count')
        result[k] = v
    return result


def cleanup_projection(word):
    """Expected inverse-reverse syntax; does not prove its semantic endpoint."""
    restored = {int(r) for r in word['helper_final']}
    forward = list(word['A'][word['prelude_events']:])
    scheduled = defaultdict(list)
    for identity, record in enumerate(word['warps'], 1):
        scheduled[record[0]].append(['warp', record[1], identity])
    for index in range(len(word['B']) + 1):
        forward.extend(scheduled[index])
        if index < len(word['B']):
            forward.append(word['B'][index])
    forward.extend(word['restore'])
    forward = [g for g in forward if g[0] == 'warp' or not target_role(g[1])]
    result = []
    full = [1 << i for i in reversed(range(9))]
    def buffer(role):
        return role + ORDINARY_ROLES if role in restored else role
    for gate in reversed(forward):
        if gate[0] == 'warp':
            result.append(['warp', buffer(gate[1]), -gate[2], full])
        elif gate[0] == 'add':
            result.append(['add', buffer(gate[1]), buffer(gate[2]),
                           -gate[3], gate[4], full])
        else:
            result.append(['scale', buffer(gate[1]), gate[3], gate[2], full])
    return result


def _audit(word, check_report, check_cleanup):
    require(type(word) is dict, 'word must be an object')
    for key in FRAME_SECTIONS + ('report', 'cleanup'):
        require(key in word, 'missing word section ' + key)
    report = word['report']
    require(type(report) is dict and all(type(report.get(k)) is int
            for k in ('v', 'h', 'R')), 'integer source geometry')
    require((report['v'], report['h'], report['R']) == (112, 9, 480),
            'unsupported source geometry')
    removed_list = word['removed']
    require(type(removed_list) is list and all(type(r) is int and 224 <= r < 704
            for r in removed_list) and len(set(removed_list)) == len(removed_list),
            'removed helper inventory')
    live = set(range(704)) - set(removed_list)
    require(len(live) == 632, 'expected 632 independent ordinary roles')
    helpers = sorted(live - set(range(224)))
    restored = role_map(word['helper_final'], live, 'helper_final')
    entering = role_map(word['start_extra'], live, 'start_extra')
    ports = word['ports']
    require(type(ports) is list and len(ports) == 112 and len(set(ports)) == 112,
            'port inventory')
    require(all(type(p) is int and 0 < p < 512 for p in ports), 'port vector')
    start = {r: ZERO for r in live}
    finish = {r: VECTORS for r in live}
    for r, port in enumerate(ports):
        start[r] = span([port])
        finish[r + 112] = hyperplane(port)
    start.update(entering)
    finish.update(restored)
    current = dict(start)
    charges = []
    warp_events = []
    paid, by_section = Counter(), defaultdict(Counter)
    by_role = defaultdict(Counter)

    def charge(section, index, role, old, new, descending=False):
        amount = dimension(old) - dimension(new) if descending else dimension(new) - dimension(old)
        if amount:
            require(amount > 0, 'negative paid rank')
            paid[amount] += 1
            by_section[section][amount] += 1
            by_role[role][amount] += 1
            charges.append([section, index, role, dimension(old), dimension(new), amount,
                            canonical_hash(sorted(old)), canonical_hash(sorted(new))])

    def climb(section, index, role, destination):
        old = current[role]
        require(old <= destination, f'nonmonotone frame at {section}:{index} role {role}')
        charge(section, index, role, old, destination)
        current[role] = destination

    warps = word['warps']
    require(type(warps) is list, 'warp records')
    schedules = defaultdict(list)
    for identity, record in enumerate(warps, 1):
        require(type(record) is list and len(record) == 5, 'warp record shape')
        position, role, columns, raw_source, raw_target = record
        require(type(position) is int and 0 <= position <= len(word['B']), 'warp position')
        require(type(role) is int and role in live and not target_role(role), 'warp role')
        require(type(columns) is list, 'warp columns')
        source, target = frame_basis(raw_source), frame_basis(raw_target)
        require(dimension(source) == dimension(target), 'warp changes dimension')
        check_map(tuple(columns), source, target)
        schedules[position].append(identity)

    def warp(section, index, role, identity, source, destination):
        require(type(identity) is int and identity != 0 and abs(identity) <= len(warps),
                'warp identity')
        record = warps[abs(identity) - 1]
        require(role == record[1], 'warp lender mismatch')
        columns = tuple(record[2])
        check_map(columns, source if identity > 0 else destination,
                  destination if identity > 0 else source)
        require(current[role] == source, f'warp source frame mismatch at {section}:{index}')
        current[role] = destination
        warp_events.append([section, index, role, identity, dimension(source),
                            canonical_hash(sorted(source)), canonical_hash(sorted(destination))])

    npre = integer(word['prelude_events'], 'prelude count')
    require(0 <= npre <= len(word['A']), 'prelude bounds')
    for section in ('A', 'B', 'restore'):
        require(type(word[section]) is list, section + ' gate list')

    def scalar(section, index, gate):
        roles = scalar_gate(gate, live)
        if not target_role(gate[1]):
            require(all(not target_role(r) for r in roles), 'nontarget reads target')
        if section == 'restore':
            require(not target_role(gate[1]), 'restore writes target')
        destination = span(gate[-1])
        for role in roles:
            climb(section, index, role, destination)

    for index, gate in enumerate(word['A']):
        require(type(gate) is list and len(gate) >= 2, 'A gate shape')
        if gate[0] == 'warp':
            require(index < npre and len(gate) == 5, 'warp outside A prelude')
            role, identity = gate[1:3]
            require(type(role) is int and role in live, 'A warp role')
            warp('A', index, role, identity, frame_basis(gate[3]), frame_basis(gate[4]))
        else:
            if index < npre:
                require(target_role(gate[1]), 'prelude scalar must write target')
            scalar('A', index, gate)

    levels = word['target_levels']
    require(type(levels) is dict, 'target levels')
    target_frames = {}
    for key, value in levels.items():
        require(type(key) is str and key.isascii() and key.isdecimal()
                and str(int(key)) == key and 0 <= int(key) < 112, 'target level key')
        target_frames[int(key)] = frame_basis(value)
    require(all(current[112 + t] == target_frames.get(t, ZERO) for t in range(112)),
            'cut target frame unavailable')
    centers, center_frames = word['centers'], word['center_frames']
    require(type(centers) is list and type(center_frames) is list
            and len(centers) == len(center_frames) == 8 and len(set(centers)) == 8,
            'centre inventory')
    require(all(type(r) is int and r in live and not target_role(r) for r in centers),
            'centre role')
    served = defaultdict(set)
    require(type(word['cut']) is list, 'cut gate list')
    for gate in word['cut']:
        roles = scalar_gate(gate, live, frame_required=False)
        require(gate[0] == 'add' and target_role(roles[0]) and roles[1] in centers,
                'cut gate must read a declared centre into target')
        served[roles[1]].add(target_frames.get(roles[0] - 112, ZERO))
    for center_index, (role, raw) in enumerate(zip(centers, center_frames)):
        cursor = frame_basis(raw)
        require(current[role] == cursor, 'centre entrance frame mismatch')
        destinations = sorted(served[role], key=lambda s: (-len(s), tuple(sorted(s))))
        for descent_index, destination in enumerate(destinations):
            require(destination <= cursor, 'centre descent is not nested')
            charge('centre', center_index * 112 + descent_index, role, cursor,
                   destination, descending=True)
            cursor = destination
        # The centre path is a separately charged readout; its main-word frame
        # remains the entrance frame for subsequent B operations.

    for index in range(len(word['B']) + 1):
        for identity in schedules[index]:
            _, role, _, raw_source, raw_target = warps[identity - 1]
            warp('B-warp', index, role, identity,
                 frame_basis(raw_source), frame_basis(raw_target))
        if index < len(word['B']):
            scalar('B', index, word['B'][index])
    for index, gate in enumerate(word['restore']):
        scalar('restore', index, gate)
    for role in sorted(live):
        climb('endpoint', role, role, finish[role])

    widths = {str(role): dimension(finish[role]) - dimension(start[role]) for role in helpers}
    require(all(value > 0 for value in widths.values()), 'nonpositive helper width')
    inventory = Counter(widths.values())
    profile = _histogram(paid)
    if check_report:
        require(_claimed_histogram(report.get('local_profile'), 'local_profile') == profile,
                'declared paid profile mismatch')
        require(_claimed_histogram(report.get('width_inventory'), 'width_inventory') == _histogram(inventory),
                'declared helper inventory mismatch')
    expected_cleanup = cleanup_projection(word)
    cleanup = word['cleanup']
    require(type(cleanup) is list, 'cleanup gate list')
    buffers = {704 + role for role in restored}
    if check_cleanup:
        require(len(cleanup) == len(expected_cleanup), 'cleanup length mismatch')
        seen_buffers = set()
        for index, (actual, expected) in enumerate(zip(cleanup, expected_cleanup)):
            require(type(actual) is list and actual, 'cleanup gate shape')
            if actual[0] == 'warp':
                require(len(actual) == 4 and type(actual[1]) is int
                        and type(actual[2]) is int, 'cleanup warp shape')
            else:
                scalar_gate(actual, live | buffers)
            require(actual[:-1] == expected[:-1] and frame_basis(actual[-1]) == VECTORS,
                    f'inverse-reverse cleanup mismatch at {index}')
            roles = actual[1:2] if actual[0] != 'add' else actual[1:3]
            require(all(type(r) is int and r in live | buffers for r in roles), 'cleanup role')
            require(all(r not in restored for r in roles), 'cleanup touches restored helper')
            seen_buffers.update(r for r in roles if r >= 704)
        require(seen_buffers == buffers, 'private buffer namespace mismatch')
    for role in live:
        if not target_role(role) and role not in restored:
            require(finish[role] == VECTORS, 'cleanup unbuffered low endpoint')
    mass = sum(rank * count for rank, count in paid.items())
    endpoint_mass = sum(dimension(finish[role]) - dimension(start[role]) for role in live)
    centre_mass = sum(rank * count for rank, count in by_section['centre'].items())
    require(mass == endpoint_mass + centre_mass,
            'telescoping frame-mass identity mismatch')
    return {
        'profile': profile,
        'rank_mass': mass,
        'mass_identity': {'endpoint_increase': endpoint_mass,
                          'helper_endpoint_increase': sum(widths.values()),
                          'centre_descent': centre_mass, 'paid_total': mass},
        'width_inventory': _histogram(inventory),
        'helper_widths': widths,
        'independent_roles': len(live),
        'live_helpers': len(helpers),
        'restored_helpers': sorted(restored),
        'private_buffers': sorted(buffers),
        'buffer_count': len(buffers),
        'section_profiles': {key: _histogram(value) for key, value in sorted(by_section.items())},
        'role_profiles': {str(key): _histogram(value) for key, value in sorted(by_role.items())},
        'charge_columns': ['section', 'event', 'role', 'from_dimension', 'to_dimension',
                           'rank', 'from_span_sha256', 'to_span_sha256'],
        'charges': charges,
        'warp_event_columns': ['section', 'event', 'role', 'signed_id', 'dimension',
                               'from_span_sha256', 'to_span_sha256'],
        'warp_events': warp_events,
        'warp_records': len(warps),
        'cleanup_events': len(expected_cleanup),
        'cleanup_structure_sha256': canonical_hash(expected_cleanup),
        'frame_projection_sha256': canonical_hash({key: word[key] for key in FRAME_SECTIONS}),
        'scope': 'Exact frame sets, event-derived ranks, helper widths and inverse-reverse cleanup syntax; no scalar/operator endpoint or buffer-zero theorem.',
    }


def audit_word(word):
    """Audit one frozen word, including its declared reports and cleanup syntax."""
    return _audit(word, check_report=True, check_cleanup=True)


def audit_chain(parent, final, transforms):
    """Reconstruct only frame-bearing sections of the nine sequential stages."""
    require(type(transforms) is list and len(transforms) == 9, 'nine declared transforms required')
    before = audit_word(parent)
    after = audit_word(final)
    require(before['profile'] == _histogram(PARENT_PROFILE), 'unexpected parent profile')
    require(before['buffer_count'] == 73, 'expected 73 parent buffers')
    current = deepcopy(parent)
    records, edits = [], []
    expected_profile = Counter(PARENT_PROFILE)
    parent_restored = set(before['restored_helpers'])
    for step, (helper, normal, transform) in enumerate(zip(HELPERS, NORMALS, transforms), 1):
        require(type(transform) is dict and type(transform.get('helper')) is int
                and transform['helper'] == helper and transform.get('normal') == normal,
                'transform order/helper/normal mismatch')
        require(str(helper) not in current['helper_final']
                and str(helper) not in current['start_extra'] and helper not in current['removed'],
                'extraction helper is not fresh zero-entry helper')
        initial = current.get('initial_corrections')
        require(type(initial) is list and all(type(item) is dict and type(item.get('source')) is int
                                             for item in initial), 'initial correction source inventory')
        protected = set(map(int, current['helper_final'])) | set(map(int, current['start_extra']))
        protected.update(item['source'] for item in initial)
        allowed = set(range(224, 704)) - set(current['removed']) - protected
        input_gates, output_gates = transform.get('before'), transform.get('after')
        require(type(input_gates) is list and input_gates and type(output_gates) is list
                and output_gates, 'transform gate lists')
        for gate in input_gates:
            scalar_gate(gate, allowed)
            require(span(gate[-1]) == ZERO, 'input gate is not at zero frame')
        plane = hyperplane(normal)
        for gate in output_gates:
            scalar_gate(gate, set(range(704)) - set(current['removed']))
            require(not target_role(gate[1]) and span(gate[-1]) == plane,
                    'output gate must use exact declared hyperplane')
            roles = gate[1:3] if gate[0] == 'add' else gate[1:2]
            require(not (set(roles) & set(map(int, current['helper_final']))),
                    'output gate touches previously restored endpoint')
        seen = set()
        changes = transform.get('frame_changes', [])
        require(type(changes) is list, 'frame changes list')
        require(len(changes) == (0 if step <= 3 else 3 if step == 9 else 2),
                'unexpected stage frame edit count')
        for edit in changes:
            require(type(edit) is dict, 'frame edit record')
            section, index = edit.get('section'), edit.get('parent_index')
            require(section in ('A', 'restore') and type(index) is int
                    and 0 <= index < len(current[section]) and (section, index) not in seen,
                    'frame edit index/duplicate')
            require(section != 'A' or index >= current['prelude_events'], 'frame edit inside prelude')
            seen.add((section, index))
            gate = current[section][index]
            require(gate[:-1] == edit.get('gate') and gate[-1] == edit.get('old_frame'),
                    'frame edit exact preimage mismatch')
            require(gate[0] in ('add', 'scale') and not target_role(gate[1]), 'frame edit gate kind')
            old_frame, new_frame = frame_basis(edit['old_frame']), frame_basis(edit['new_frame'])
            require(new_frame < old_frame and dimension(old_frame) - dimension(new_frame) == 1,
                    'frame edit must lower by one within old span')
            require(new_frame == old_frame & plane,
                    'frame edit is not intersection with extraction hyperplane')
            expected_candidate_index = index + (len(input_gates) if section == 'A' else 0)
            require(type(edit.get('candidate_index')) is int
                    and edit['candidate_index'] == expected_candidate_index,
                    'frame edit candidate index mismatch')
            gate[-1] = deepcopy(edit['new_frame'])
            edits.append({'step': step, 'helper': helper, 'section': section,
                          'parent_index': index, 'candidate_index': expected_candidate_index,
                          'from_dimension': dimension(old_frame), 'to_dimension': dimension(new_frame),
                          'old_span_sha256': canonical_hash(sorted(old_frame)),
                          'new_span_sha256': canonical_hash(sorted(new_frame))})
        npre = current['prelude_events']
        current['A'][npre:npre] = deepcopy(input_gates)
        current['restore'].extend(deepcopy(output_gates))
        current['helper_final'][str(helper)] = deepcopy(output_gates[0][-1])
        projected = _audit(current, check_report=False, check_cleanup=False)
        delta = {1: 3, 2: -2} if step <= 3 else {2: 1, 3: 3, 4: -3}
        expected_profile.update(delta)
        require(projected['profile'] == _histogram(expected_profile), 'stage paid profile delta mismatch')
        require(projected['buffer_count'] == 73 + step, 'stage private buffer count')
        require(set(projected['restored_helpers']) == parent_restored | set(HELPERS[:step]),
                'previously restored helper disappeared')
        stage_inventory = Counter({int(k): v for k, v in before['width_inventory'].items()})
        stage_inventory[8] += step
        stage_inventory[9] -= step
        require(projected['width_inventory'] == _histogram(stage_inventory), 'stage helper inventory delta mismatch')
        require(all(projected['helper_widths'][role] == width - (int(role) in HELPERS[:step])
                    for role, width in before['helper_widths'].items()),
                'stage width changes outside extracted helpers')
        records.append({'step': step, 'helper': helper, 'normal': normal,
                        'input_gates': len(input_gates), 'output_gates': len(output_gates),
                        'frame_edits': len(changes), 'profile': projected['profile'],
                        'rank_mass': projected['rank_mass'], 'width_inventory': projected['width_inventory'],
                        'buffer_count': projected['buffer_count'],
                        'section_profiles': projected['section_profiles'],
                        'event_ledger_sha256': canonical_hash(projected['charges']),
                        'frame_projection_sha256': projected['frame_projection_sha256']})
    require(len(edits) == 13, 'thirteen frame edits required')
    for section in FRAME_SECTIONS:
        require(current[section] == final[section], 'final frame-bearing section mismatch: ' + section)
    require(cleanup_projection(current) == cleanup_projection(final), 'final cleanup projection mismatch')
    changed_widths = [int(role) for role, width in before['helper_widths'].items()
                      if after['helper_widths'][role] != width]
    require(set(changed_widths) == set(HELPERS), 'unexpected changed helper widths')
    require(all(before['helper_widths'][str(h)] == 9 and after['helper_widths'][str(h)] == 8
                for h in HELPERS), 'extracted helper width not 9 to 8')
    require(after['rank_mass'] - before['rank_mass'] == -9, 'local rank mass delta')
    return {'stages': records, 'frame_edits': edits,
            'changed_helpers': sorted(changed_widths), 'rank_mass_delta': -9,
            'profile_delta': {'1': 9, '3': 18, '4': -18},
            'buffer_count_before': before['buffer_count'], 'buffer_count_after': after['buffer_count'],
            'parent_event_ledger_sha256': canonical_hash(before['charges']),
            'final_event_ledger_sha256': canonical_hash(after['charges']),
            'frame_sections_checked': list(FRAME_SECTIONS),
            'scope': 'Sequential frame projection and cleanup syntax only; compensation algebra and paired scalar/free-operator identities are inherited, not replayed.'}

"""Independent raw-word rank ledger for the pinned PR2312/PR2322 comparison.

Every subspace is the explicit set of its at most 512 vectors.  No producer,
emitter, Gaussian-elimination routine, native checker or moment engine is
imported.  This checks the raw paid-frame interface, not scalar correctness,
physical Clifford phases, emitted cleanup, global hosting or an outer theorem.

The source construction is credited to Jeremy Kothe (PR2312), and the four-role
change to Vlado-V (PR2322), retaining their documented predecessor credits.
Independent implementation prepared with substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""

from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import json


class LedgerError(ValueError):
    """A raw source word violates the audited frame/pricing interface."""


def require(condition, message):
    if not condition:
        raise LedgerError(message)


def _integer(value, low, high, label):
    require(type(value) is int and low <= value <= high, label)
    return value


@lru_cache(maxsize=None)
def _enumerate_span(generators):
    vectors = {0}
    for generator in generators:
        vectors.update(vector ^ generator for vector in tuple(vectors))
    return frozenset(vectors)


def span(generators, h=9):
    """Enumerate all binary sums; redundant generators are representation only."""
    require(isinstance(generators, (list, tuple)), 'frame must be a list or tuple')
    for vector in generators:
        _integer(vector, 0, (1 << h)-1, 'frame vector outside the ambient space')
    return _enumerate_span(tuple(sorted(set(generators))))


def rank(space):
    size = len(space)
    require(size > 0 and size & (size-1) == 0, 'subspace cardinality is not a power of two')
    return size.bit_length()-1


def _hist(counter):
    return {str(key): value for key, value in sorted(counter.items()) if value}


def _delta(left, right):
    return _hist({int(k): right.get(k, 0)-left.get(k, 0)
                  for k in left.keys() | right.keys()})


def _digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def audit_word(word):
    """Reconstruct the paid histogram, then check the word's reported values.

    A, B, restoration and terminal climbs ascend by set inclusion.  The private
    cut is a separate nested descending copy chain for each center.  Rank-zero
    handoffs must be bijections on all 512 vectors and carry the actual current
    source subspace onto the declared destination.  The zero-frame scalar
    sections are schema-checked but their algebra and cleanup are out of scope.
    """
    require(isinstance(word, dict), 'word must be an object')
    report = word.get('report')
    require(isinstance(report, dict), 'missing report geometry')
    require(all(type(report.get(k)) is int for k in ('v', 'h', 'R')),
            'geometry must consist of integers')
    v, h, raw_helpers = (report[k] for k in ('v', 'h', 'R'))
    require((v, h, raw_helpers) == (112, 9, 480), 'outside the pinned raw-word geometry')
    n = 2*v + raw_helpers
    full = frozenset(range(1 << h))
    zero = frozenset({0})
    removed_list = word.get('removed')
    require(isinstance(removed_list, list), 'removed inventory must be a list')
    for role in removed_list:
        _integer(role, 2*v, n-1, 'removed role is not a raw helper')
    removed = set(removed_list)
    require(len(removed) == len(removed_list), 'duplicate removed role')
    live = set(range(n))-removed
    helpers = sorted(live-set(range(2*v)))

    def live_role(value):
        _integer(value, 0, n-1, 'role outside raw namespace')
        require(value in live, 'removed role referenced by the raw word')
        return value

    ports = word.get('ports')
    require(isinstance(ports, list) and len(ports) == v, 'wrong port count')
    for port in ports:
        _integer(port, 1, (1 << h)-1, 'port outside nonzero ambient vectors')
    require(len(set(ports)) == v, 'duplicate port')
    starts = [frozenset({0, port}) for port in ports] + [zero]*(v+raw_helpers)
    ends = [full]*v + [frozenset(x for x in full if (x & port).bit_count() % 2 == 0)
                       for port in ports] + [full]*raw_helpers

    def keyed_spaces(name, low, high):
        values = word.get(name)
        require(isinstance(values, dict), name+' must be an object')
        result = {}
        for key, generators in values.items():
            require(isinstance(key, str) and key.isdecimal() and str(int(key)) == key,
                    name+' uses a noncanonical role key')
            role = int(key)
            _integer(role, low, high, name+' role outside its domain')
            result[role] = span(generators, h)
        return result

    entrance = keyed_spaces('start_extra', 2*v, n-1)
    terminal = keyed_spaces('helper_final', 2*v, n-1)
    require(not removed.intersection(entrance) and not removed.intersection(terminal),
            'removed helper has an entrance or terminal frame')
    for role, space in entrance.items():
        starts[role] = space
    for role, space in terminal.items():
        ends[role] = space
    for role in helpers:
        require(starts[role] <= ends[role], 'helper entrance not contained in terminal frame')
    widths = {str(role): rank(ends[role])-rank(starts[role]) for role in helpers}
    require(all(width > 0 for width in widths.values()), 'nonpositive retained helper width')

    centers = word.get('centers')
    center_frames = word.get('center_frames')
    require(isinstance(centers, list) and len(centers) == 8 and
            len(set(centers)) == 8, 'wrong or duplicate center inventory')
    require(isinstance(center_frames, list) and len(center_frames) == len(centers),
            'center/frame count mismatch')
    for center in centers:
        live_role(center)
        require(not v <= center < 2*v, 'private producer is a target role')
    center_spaces = {role: span(frame, h) for role, frame in zip(centers, center_frames)}
    target_spaces = keyed_spaces('target_levels', 0, v-1)
    require(word.get('initial_corrections') == [], 'initial corrections outside audited interface')

    def scalar(event, cut=False):
        require(isinstance(event, list) and event, 'scalar event must be a nonempty list')
        kind = event[0]
        require(kind in ('add', 'scale'), 'unsupported scalar event')
        require(len(event) == (6 if kind == 'add' else 5), 'scalar event arity')
        roles = [live_role(event[1])]
        if kind == 'add':
            roles.append(live_role(event[2]))
            numerator, denominator = event[3:5]
        else:
            numerator, denominator = event[2:4]
        require(type(numerator) is int and type(denominator) is int and denominator > 0,
                'invalid scalar rational')
        require(kind != 'scale' or numerator != 0, 'noninvertible scalar scale')
        if cut:
            require(kind == 'add' and event[-1] is None, 'invalid private-cut scalar')
            require(v <= roles[0] < 2*v and roles[1] in center_spaces,
                    'private cut must copy a center into a target')
            return roles, None
        return roles, span(event[-1], h)

    sections = ('A', 'private-cut', 'B', 'restore', 'end')
    by_section = {section: Counter() for section in sections}
    by_role = defaultdict(Counter)
    by_role_section = defaultdict(lambda: {section: Counter() for section in sections})
    charged = []
    current = list(starts)

    def charge(section, index, role, before, after, direction='up'):
        amount = rank(after)-rank(before) if direction == 'up' else rank(before)-rank(after)
        require(amount >= 0, 'negative paid rank')
        if amount:
            by_section[section][amount] += 1
            by_role[role][amount] += 1
            by_role_section[role][section][amount] += 1
            charged.append({'section': section, 'index': index, 'role': role,
                            'from_rank': rank(before), 'to_rank': rank(after), 'charge': amount})

    def climb(section, index, role, after):
        before = current[role]
        require(before <= after, f'noncontaining frame at {section}[{index}], role {role}')
        charge(section, index, role, before, after)
        current[role] = after

    for name in ('A', 'cut', 'B', 'restore', 'precondition', 'compensation'):
        require(isinstance(word.get(name), list), name+' must be a list')
    for name in ('precondition', 'compensation'):
        for event in word[name]:
            _, space = scalar(event)
            require(space == zero, name+' has a nonzero frame outside this pricing interface')
    for index, event in enumerate(word['A']):
        roles, space = scalar(event)
        for role in roles:
            climb('A', index, role, space)
    for target in range(v):
        require(current[v+target] == target_spaces.get(target, zero), 'target frame at cut')

    readers = defaultdict(set)
    for event in word['cut']:
        roles, _ = scalar(event, cut=True)
        readers[roles[1]].add(target_spaces.get(roles[0]-v, zero))
    for role in centers:
        before = center_spaces[role]
        require(current[role] == before, 'producer frame at cut')
        # Equal-dimensional distinct spaces fail inclusion regardless of tie order.
        ordered = sorted(readers[role], key=lambda space: (-len(space), tuple(sorted(space))))
        for index, after in enumerate(ordered):
            require(after <= before, 'private readers do not form a nested copy chain')
            charge('private-cut', index, role, before, after, direction='down')
            before = after

    warps = word.get('warps')
    require(isinstance(warps, list), 'warps must be a list')
    at_position = defaultdict(list)
    for ordinal, event in enumerate(warps):
        require(isinstance(event, list) and len(event) == 5, 'warp record arity')
        position, role, columns, old, new = event
        _integer(position, 0, len(word['B']), 'warp position outside B chronology')
        live_role(role)
        require(isinstance(columns, list) and len(columns) == h, 'warp map column count')
        for column in columns:
            _integer(column, 0, (1 << h)-1, 'warp column outside ambient space')
        at_position[position].append((ordinal, role, columns, span(old, h), span(new, h)))
    map_checks = []
    for position in range(len(word['B'])+1):
        for ordinal, role, columns, old, new in at_position[position]:
            require(current[role] == old, 'handoff does not start at the current source frame')
            images = []
            for vector in range(1 << h):
                image = 0
                for bit in range(h):
                    if vector & (1 << bit):
                        image ^= columns[bit]
                images.append(image)
            require(len(set(images)) == 1 << h, 'handoff map is not an ambient bijection')
            require(frozenset(images[x] for x in old) == new, 'handoff map carries the wrong subspace')
            require(rank(old) == rank(new), 'handoff changed rank')
            current[role] = new
            map_checks.append({'ordinal': ordinal, 'B_position': position, 'role': role,
                               'rank': rank(old), 'ambient_images_checked': 1 << h,
                               'image_table_sha256': _digest(images)})
        if position < len(word['B']):
            roles, space = scalar(word['B'][position])
            for role in roles:
                climb('B', position, role, space)
    for index, event in enumerate(word['restore']):
        roles, space = scalar(event)
        for role in roles:
            climb('restore', index, role, space)
    for role in sorted(live):
        climb('end', role, role, ends[role])

    profile = sum(by_section.values(), Counter())
    width_inventory = Counter(widths.values())
    allowed_ranks = {str(value) for value in range(1, h+1)}
    for name in ('local_profile', 'width_inventory'):
        declared = report.get(name)
        require(type(declared) is dict, 'reported '+name+' must be an object')
        require(all(type(key) is str and key in allowed_ranks for key in declared),
                'reported '+name+' has a noncanonical rank key')
        require(all(type(count) is int and count > 0 for count in declared.values()),
                'reported '+name+' counts must be positive integers')
    require(report.get('local_profile') == _hist(profile), 'reported local profile differs from raw frame ledger')
    require(report.get('width_inventory') == _hist(width_inventory),
            'reported helper-width inventory differs from actual entrances/endpoints')
    return {
        'local_profile': _hist(profile),
        'rank_mass': sum(k*v for k, v in profile.items()),
        'section_profiles': {name: _hist(hist) for name, hist in by_section.items()},
        'role_profiles': {str(role): _hist(hist) for role, hist in sorted(by_role.items())},
        'role_section_profiles': {str(role): {name: _hist(hist) for name, hist in values.items()}
                                  for role, values in sorted(by_role_section.items())},
        'helper_widths': widths,
        'helper_width_inventory': _hist(width_inventory),
        'helper_width_mass': sum(widths.values()),
        'raw_helpers': raw_helpers,
        'live_helpers': len(helpers),
        'removed_roles': sorted(removed),
        'charged_events': charged,
        'charged_events_sha256': _digest(charged),
        'map_checks': map_checks,
        'scalar_event_counts': {name: len(word[name]) for name in ('A', 'cut', 'B', 'restore', 'precondition', 'compensation')},
        'scope': 'Raw paid-frame ledger only; scalar identities, cleanup, physical phases, hosting and outer admission remain separate.',
    }


def compare_words(source, candidate):
    """Return a compact source-to-candidate delta witness with both full ledgers."""
    before, after = audit_word(source), audit_word(candidate)
    require(set(before['removed_roles']) <= set(after['removed_roles']), 'candidate resurrects a removed role')
    removed = sorted(set(after['removed_roles'])-set(before['removed_roles']))
    widths_before, widths_after = before['helper_widths'], after['helper_widths']
    require(set(widths_after) == set(widths_before)-set(map(str, removed)), 'retained helper identity mismatch')
    require(all(widths_before[role] == width for role, width in widths_after.items()),
            'candidate changes a retained helper width')
    require(candidate['start_extra'] == {role: frame for role, frame in source['start_extra'].items()
                                         if int(role) not in removed},
            'retained helper entrance changed beyond removed-role deletion')
    changed_roles = {}
    all_roles = before['role_profiles'].keys() | after['role_profiles'].keys()
    for role in sorted(all_roles, key=int):
        old = before['role_profiles'].get(role, {})
        new = after['role_profiles'].get(role, {})
        delta = _delta(old, new)
        if delta:
            old_sections = before['role_section_profiles'].get(role, {})
            new_sections = after['role_section_profiles'].get(role, {})
            changed_roles[role] = {
                'before': old, 'after': new, 'delta': delta,
                'section_deltas': {name: _delta(old_sections.get(name, {}), new_sections.get(name, {}))
                                   for name in before['section_profiles']},
            }
    unchanged_sections = ('ports', 'centers', 'center_frames', 'target_levels', 'A', 'cut',
                          'restore', 'precondition', 'compensation', 'initial_corrections', 'helper_final')
    require(all(source[name] == candidate[name] for name in unchanged_sections),
            'change outside the scoped B/handoff/helper-removal comparison')
    old_helper_order = list(map(int, before['helper_widths']))
    return {
        'source': before, 'candidate': after,
        'local_profile_delta': _delta(before['local_profile'], after['local_profile']),
        'section_deltas': {name: _delta(before['section_profiles'][name], after['section_profiles'][name])
                           for name in before['section_profiles']},
        'changed_roles': changed_roles,
        'newly_removed_raw_roles': removed,
        'removed_source_compact_indices': [old_helper_order.index(role) for role in removed],
        'removed_widths': {str(role): widths_before[str(role)] for role in removed},
        'rank_mass_delta': after['rank_mass']-before['rank_mass'],
        'helper_width_mass_delta': after['helper_width_mass']-before['helper_width_mass'],
        'unchanged_raw_sections': list(unchanged_sections),
        'cleanup_checked': False,
    }

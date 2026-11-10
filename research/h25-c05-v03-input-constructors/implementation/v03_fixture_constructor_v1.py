"""Pure V03 fixtures for the selected genuine-Root input-prefix driver.

This file creates DATA, never files, imports, subprocesses or admissions.
Its baseline parameter must come from the independently reviewed C05/stage
constructor. Shape or equality checks here do not establish C05 completeness.
The future fixture installer writes each case BEFORE sealing its own stage.
The outer stage pins describe the actual mutant; the child oracle stays fixed.
"""
import hashlib

ROLES = ('pyinit_failure', 'exec_failure')
NAMES = ('dict_probe_fields_v1.c', 'field_service_v1.h',
         'field_loader_snapshot_v1.h')
C_PIN = ('e0188999d41a9ab26e8d3d5c37b18b2238b3af21b1db90895f01f7be76d50b65', 17806)
L_PIN = ('bf7ab049cea89c0a882b279e35b1383ac8f99b66aa4b9b8e1ca22eb9c24c5a8d', 19495)
PINS = (C_PIN,
        ('7656cd37503986459c4133643372fec13d3e5ad5553881f0bf0343a9a3e11abd', 17354),
        L_PIN, C_PIN,
        ('f5066831bd812e7e88fb971ba0e7ca86dbef91fc40a1a68c17b040ce474cd880', 17040),
        L_PIN)
FIELDS = ('sha256', 'bytes', 'mode')
LITERAL = 'Variant reviewed source/header differs'
CUSTODY = 'Variant current source closure differs'
INVENTORY = 'Variant role file omitted from closure'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def _copy(value, depth=0, budget=None):
    if budget is None:
        budget = [0, 0]
    budget[0] += 1
    need(depth <= 24 and budget[0] <= 65536, 'fixture input tree bound')
    kind = type(value)
    if value is None or kind is bool:
        return value
    if kind is int:
        need(-(1 << 64) <= value < (1 << 64), 'fixture integer bound')
        return value
    if kind is str:
        budget[1] += len(value)
        need(len(value) <= 8192 and budget[1] <= 524288, 'fixture text bound')
        return value
    if kind is list or kind is tuple:
        need(len(value) <= 1024, 'fixture input sequence bound')
        return [_copy(item, depth + 1, budget) for item in value]
    if kind is dict:
        need(len(value) <= 1024 and all(type(k) is str for k in value),
             'fixture input mapping domain')
        for key in value:
            _copy(key, depth + 1, budget)
        return {k: _copy(value[k], depth + 1, budget) for k in value}
    raise ValueError('fixture input must be an exact native plain tree')


def _relative(index):
    return 'areas/field-negative-variants-v1/' + ROLES[index // 3] + '/' + NAMES[index % 3]


def _metadata(configuration, index):
    role = configuration['roles'][index // 3]
    return role['source'] if index % 3 == 0 else role['source_headers'][NAMES[index % 3]]


def _changed(field, value):
    if field == 'sha256':
        return ('0' if value[0] != '0' else '1') + value[1:]
    if field == 'bytes':
        return value + 1
    return 0o400


def case_specs():
    """A conservative, explicitly proposed finite interpretation of V03.

    Both Python profiles apply to every returned case. These generated counts
    are not asserted to have appeared in the original one-sentence recipe.
    """
    rows = [('intact', -1, -1, '')]
    for index in range(6):
        rows += [('physical-byte', index, -1, ''),
                 ('physical-mode', index, -1, '')]
        for field in FIELDS:
            rows += [('literal-metadata', index, -1, field),
                     ('inventory-metadata', index, -1, field)]
    for left in range(6):
        for right in range(left + 1, 6):
            rows += [('physical-swap', left, right, ''),
                     ('equal-mode-swap', left, right, '')]
    rows += [('role-order', -1, -1, ''),
             ('role-path', 0, 3, ''), ('role-path', 3, 0, ''),
             ('header-label-swap', 1, 2, ''),
             ('header-label-swap', 4, 5, ''),
             ('equal-c-metadata-swap', 0, 3, ''),
             ('equal-loader-metadata-swap', 2, 5, ''),
             ('service-metadata-swap', 1, 4, ''),
             ('literal-before-physical', 0, 4, 'sha256'),
             ('earlier-preflight-before-physical', 0, -1, '')]
    return tuple(rows)


def construct_case(baseline_configuration, payloads, stage, spec):
    """Return the exact child plan, six physical payloads and parent oracle.

    `payloads` is the six original occurrences in P(C,H,L), E(C,H,L) order.
    This verifies their original byte pins, without executing their contents.
    `baseline_configuration` is the complete independent C05 successor input;
    this function neither constructs missing C05 facts nor approves any gate.
    """
    need(type(stage) is str and 1 < len(stage) <= 4096 and stage.startswith('/') and
         all(32 <= ord(c) < 127 for c in stage) and
         all(p not in ('', '.', '..') for p in stage.split('/')[1:]),
         'canonical absolute stage required')
    need(type(payloads) is tuple and len(payloads) == 6, 'six payload occurrences required')
    for raw, (digest, size) in zip(payloads, PINS):
        need(type(raw) is bytes and len(raw) == size and
             hashlib.sha256(raw).hexdigest() == digest, 'original fixture bytes differ')
    need(type(spec) is tuple and len(spec) == 4 and type(spec[0]) is str and
         type(spec[1]) is int and type(spec[2]) is int and type(spec[3]) is str and
         spec in case_specs(), 'unknown finite V03 case')
    plan = _copy(baseline_configuration)
    need(type(plan) is dict and type(plan.get('roles')) is list and
         len(plan['roles']) == 2 and
         [r['role'] for r in plan['roles']] == list(ROLES), 'baseline role order differs')
    inventory = plan['source_files']
    need(type(inventory) is list and 1 <= len(inventory) <= 512,
         'original source_files count differs')
    by_path, declared_total = {}, 0
    for row in inventory:
        need(type(row) is dict and set(row) == {'path', 'sha256', 'bytes', 'mode'} and
             type(row['path']) is str and row['path'] not in by_path,
             'baseline source row or duplicate path differs')
        need(type(row['sha256']) is str and len(row['sha256']) == 64 and
             all(c in '0123456789abcdef' for c in row['sha256']) and
             type(row['bytes']) is int and 0 <= row['bytes'] <= 67108864 and
             type(row['mode']) is int and 0 <= row['mode'] <= 0o7777,
             'baseline source pin domain differs')
        declared_total += row['bytes']
        need(declared_total <= 268435456, 'baseline declared custody byte bound')
        by_path[row['path']] = row
    preflight = plan['expected_preflight']
    need(type(preflight) is dict and set(preflight) == {
        'schema', 'authenticated_files', 'native_private_access', 'cached_admission'} and
        type(preflight['schema']) is str and
        preflight['schema'] == 'h25-public-runtime-preflight-v2' and
        type(preflight['authenticated_files']) is int and
        preflight['authenticated_files'] == 217 and
        preflight['native_private_access'] is False and
        preflight['cached_admission'] is False,
        'independent original preflight expectation differs')
    for index, (digest, size) in enumerate(PINS):
        role = plan['roles'][index // 3]
        need(role['source_path'] == stage + '/' + _relative(3 * (index // 3)),
             'baseline role source path differs')
        expected = {'sha256': digest, 'bytes': size, 'mode': 0o444}
        need(_metadata(plan, index) == expected, 'baseline literal metadata differs')
        need(by_path.get(stage + '/' + _relative(index)) ==
             {'path': stage + '/' + _relative(index), **expected},
             'baseline source_files literal differs')
    bodies, modes = list(payloads), [0o444] * 6
    kind, left, right, field = spec
    message, terminal, is_v03 = None, None, True
    if kind == 'physical-byte':
        bodies[left] = bytes((bodies[left][0] ^ 1,)) + bodies[left][1:]
        message, terminal = CUSTODY, '_vcheck_custody'
    elif kind == 'physical-mode':
        modes[left] = 0o400
        message, terminal = CUSTODY, '_vcheck_custody'
    elif kind == 'literal-metadata':
        row = _metadata(plan, left)
        row[field] = _changed(field, row[field])
        message, terminal = LITERAL, '_vcheck_literal_sources'
    elif kind == 'inventory-metadata':
        row = by_path[stage + '/' + _relative(left)]
        row[field] = _changed(field, row[field])
        message, terminal = INVENTORY, '_vcheck_literal_sources'
    elif kind == 'physical-swap':
        bodies[left], bodies[right] = bodies[right], bodies[left]
        # Derived from independent original pins, never child return values.
        if PINS[left] != PINS[right]:
            message, terminal = CUSTODY, '_vcheck_custody'
    elif kind == 'equal-mode-swap':
        modes[left], modes[right] = modes[right], modes[left]
    elif kind == 'role-order':
        plan['roles'].reverse()
        message, terminal = 'Variant literal configuration differs', '_v03_original_input_prefix'
    elif kind == 'role-path':
        plan['roles'][left // 3]['source_path'] = stage + '/' + _relative(right)
        message, terminal = 'Variant source role path differs', '_vcheck_literal_sources'
    elif kind in ('header-label-swap', 'equal-c-metadata-swap',
                  'equal-loader-metadata-swap', 'service-metadata-swap'):
        first, second = _metadata(plan, left), _metadata(plan, right)
        old_first, old_second = dict(first), dict(second)
        first.clear()
        first.update(old_second)
        second.clear()
        second.update(old_first)
        if PINS[left] != PINS[right]:
            message, terminal = LITERAL, '_vcheck_literal_sources'
    elif kind == 'literal-before-physical':
        row = _metadata(plan, left)
        row[field] = _changed(field, row[field])
        bodies[right] = bytes((bodies[right][0] ^ 1,)) + bodies[right][1:]
        message, terminal = LITERAL, '_vcheck_literal_sources'
    elif kind == 'earlier-preflight-before-physical':
        plan['expected_preflight']['authenticated_files'] = 216
        bodies[left] = bytes((bodies[left][0] ^ 1,)) + bodies[left][1:]
        message, terminal = 'Variant original preflight differs', '_v03_original_input_prefix'
        is_v03 = False  # Deliberate earlier refusal must NOT earn V03 credit.
    else:
        need(kind == 'intact', 'unimplemented finite V03 case')
    return {
        'case': spec,
        'child_configuration': plan,
        'physical_files': tuple((stage + '/' + _relative(i), bodies[i], modes[i])
                                for i in range(6)),
        'parent_expectation': {
            'outcome': 'PREFIX_RETURN' if message is None else 'EXACT_SOURCE_REFUSAL',
            'exception_type': None if message is None else 'RuntimeError',
            'message': message, 'terminal_function': terminal,
            'v03_discriminator': is_v03,
            'compiler_launches': 0, 'candidate_image_loads': 0,
            'complete_raw_and_owned_terminal_required': True,
        },
        'c05_completeness_established_here': False,
        'source_admitted': False, 'execution_admitted': False,
    }

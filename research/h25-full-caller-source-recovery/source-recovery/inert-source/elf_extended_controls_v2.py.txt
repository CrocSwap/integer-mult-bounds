"""Additional independent input families for all previously missing pure rows.

SOURCE ONLY. A rejection does not prove a particular internal branch was hit;
compound obligations and production-specific bindings remain independently
reviewed. Root-only source/custody obligations are deliberately not simulated.
"""
from copy import deepcopy
from hashlib import sha256
from struct import pack_into, unpack_from
from types import SimpleNamespace
from elf_literal_fixture_v1 import SHOFF
from elf_literal_fixture_v2 import (make_fixture, make_import_fixture, make_versioned_fixture,
    make_data_link_fixture, make_page_crossing_dynamic_fixture, make_notype_plt_fixture,
    add_section, elf_hash, runtime_policy_v2)
from provider_controls_v1 import fixtures as initial_provider_fixtures
from receipt_contract_v1 import need, record, finish, validate

STATIC_CASES = (
 ('extended-section-numbering', 'base'), ('extended-table-header-overlap', 'base'),
 ('extended-allocated-mapping-mismatch', 'base'), ('extended-bad-alignment', 'base'),
 ('extended-unknown-program-header', 'base'), ('extended-load-file-overlap', 'base'),
 ('extended-wrong-header-mapping', 'base'), ('extended-missing-rx', 'base'),
 ('extended-missing-stack', 'base'), ('extended-missing-relro', 'base'),
 ('extended-dynamic-outside-relro', 'base'), ('extended-unknown-note', 'base'),
 ('extended-duplicate-dynamic-name', 'base'), ('extended-duplicate-full-initializer', 'base'),
 ('extended-initializer-outside-rx', 'base'), ('extended-interposable-internal-object', 'base'),
 ('extended-versioned-full-name-mismatch', 'versioned'), ('extended-sysv-bad-bucket', 'base'),
 ('extended-sysv-bad-chain-index', 'base'), ('extended-gnu-unterminated-chain', 'base'),
 ('extended-gnu-wrong-bucket', 'base'), ('extended-hash-pointer-mismatch', 'base'),
 ('extended-verneed-dependency-mismatch', 'versioned'), ('extended-verneed-hash', 'versioned'),
 ('extended-verneed-next', 'versioned'), ('extended-unused-version-record', 'versioned'),
 ('extended-df-textrel', 'base'), ('extended-unknown-tag', 'base'),
 ('extended-unknown-flags', 'base'), ('extended-dynamic-after-null', 'base'),
 ('extended-duplicate-dynamic-tag', 'base'), ('extended-relr', 'base'),
 ('extended-unsupported-relocation', 'base'), ('extended-readonly-relocation', 'base'),
 ('extended-unaligned-relocation', 'base'), ('extended-relocation-symbol-range', 'imports'),
 ('extended-external-nonzero-addend', 'imports'), ('extended-relative-nonzero-symbol', 'base'),
 ('extended-relative-target-outside', 'base'), ('extended-relacount', 'base'),
 ('extended-unadvertised-rela', 'base'), ('extended-defined-symbol-relocation', 'base'),
 ('extended-plt-without-got', 'imports'), ('extended-method-table-extent', 'base'),
 ('extended-method-name', 'base'), ('extended-method-padding', 'base'),
 ('extended-method-doc', 'base'), ('extended-external-method-pointer', 'imports'),
 ('extended-method-interior-pointer', 'base'), ('extended-unlisted-code-pointer', 'imports'),
 ('extended-missing-helper', 'base'), ('extended-nonhidden-helper', 'base'),
 ('extended-pointer-slot-outside-object', 'imports'), ('extended-dynamic-count-bound', 'base'),
 ('extended-symbol-count-bound', 'base'), ('extended-relocation-count-bound', 'base'),
 ('extended-string-bound', 'base'), ('extended-hash-bloom-bound', 'base'),
 ('extended-method-table-count-bound', 'base'), ('extended-pointer-slot-count-bound', 'base'),
 ('extended-relro-no-effective-page', 'base'), ('extended-relro-straddles-effective-end', 'base'),
 ('extended-wrong-page-profile', 'base'), ('extended-data-link-retargeted', 'data-link'),
 ('extended-data-link-relocation-missing', 'data-link'))
DATA_CASES = ('extended-dict-nonstring-key', 'extended-sequence-list', 'extended-bool-integer',
 'extended-foreign-equality', 'extended-cyclic-record', 'extended-aggregate-record-bound',
 'extended-extra-policy-key', 'extended-missing-digest', 'extended-static-receipt-digest')
PROVIDER_CASES = ('extended-wrong-snapshot-scope', 'extended-map-phdr-drift',
 'extended-duplicate-map-name', 'extended-map-segment-overlap', 'extended-vdso-fake-file',
 'extended-vdso-provider', 'extended-omitted-search-row', 'extended-local-dependency-fallback',
 'extended-unknown-needed-alias', 'extended-dependency-alias-ambiguity',
 'extended-unresolved-strong', 'extended-resolved-zero', 'extended-weak-zero-owner',
 'extended-wrong-symbol-version', 'extended-ifunc-unknown-family',
 'extended-ifunc-overlapping-families', 'extended-ifunc-vdso-family',
 'extended-import-count-bound', 'extended-map-count-bound', 'extended-segment-count-bound',
 'extended-required-version-missing-despite-interposer', 'extended-version-node-hash',
 'extended-duplicate-version-node', 'extended-jump-slot-notype-object-winner',
 'extended-jump-slot-notype-data-winner')
POSITIVE_CASES = ('extended-positive-versioned-elf', 'extended-positive-data-link',
 'extended-positive-relocation-results', 'extended-positive-os-ifunc',
 'extended-positive-vdso-inventory', 'extended-positive-local-project',
 'extended-positive-sysv-only', 'extended-positive-gnu-only',
 'extended-positive-versioned-provider', 'extended-positive-page-crossing-dynamic',
 'extended-positive-jump-slot-notype-function')
CASE_IDS = tuple(row[0] for row in STATIC_CASES) + DATA_CASES + PROVIDER_CASES + POSITIVE_CASES
NORMAL_CASE_COUNT = 110
OPTIMIZED_CASE_COUNT = 110


def expectations():
    rows = {}
    for name in CASE_IDS[:-len(POSITIVE_CASES)]:
        rows[name] = {'accepted': False, 'exception': 'ELFAdmissionError', 'foreign_callbacks': 0}
    for name in POSITIVE_CASES:
        rows[name] = {'accepted': True, 'independent_literal_checks': True}
    need(len(rows) == 110 and len(CASE_IDS) == 110, 'extended literal inventory')
    return rows


def _pack(raw, offset, fmt, value):
    pack_into(fmt, raw, offset, value)


def _fixture(kind):
    if kind == 'versioned': return make_versioned_fixture()
    if kind == 'imports': raw, profile = make_import_fixture()
    elif kind == 'data-link': raw, profile = make_data_link_fixture()
    else: raw, profile = make_fixture()
    return raw, profile, {}


def _static_input(name, kind):
    raw0, policy, positions = _fixture(kind)
    raw = bytearray(raw0)
    if name == 'extended-section-numbering': _pack(raw, 60, '<H', 0)
    elif name == 'extended-table-header-overlap': _pack(raw, 40, '<Q', 64)
    elif name == 'extended-allocated-mapping-mismatch': _pack(raw, SHOFF+64+16, '<Q', 0x501)
    elif name == 'extended-bad-alignment': _pack(raw, SHOFF+64+48, '<Q', 3)
    elif name == 'extended-unknown-program-header': _pack(raw, 64+5*56, '<I', 0x70000001)
    elif name == 'extended-load-file-overlap': _pack(raw, 64+56+8, '<Q', 0)
    elif name == 'extended-wrong-header-mapping': _pack(raw, 64+4, '<I', 6)
    elif name == 'extended-missing-rx': _pack(raw, 64+56+4, '<I', 4)
    elif name in ('extended-missing-stack', 'extended-missing-relro'):
        offset = 64 + (4 if name == 'extended-missing-stack' else 5) * 56
        raw[offset:offset+56] = bytes(56)
    elif name == 'extended-dynamic-outside-relro':
        _pack(raw, 64+5*56+32, '<Q', 128); _pack(raw, 64+5*56+40, '<Q', 128)
    elif name == 'extended-unknown-note':
        raw = add_section(raw, '.note.unknown', 7, 2, 0xB00, bytes(16), align=4)
        _pack(raw, 56, '<H', 7)
        pack_into('<IIQQQQQQ', raw, 64+6*56, 4, 4, 0xB00, 0xB00, 0xB00, 16, 16, 4)
    elif name == 'extended-duplicate-dynamic-name':
        raw[0x730:0x748] = raw[0x718:0x730]; _pack(raw, SHOFF+4*64+32, '<Q', 72)
    elif name == 'extended-duplicate-full-initializer':
        raw[0x3360:0x3378] = raw[0x3348:0x3360]; _pack(raw, SHOFF+12*64+32, '<Q', 120)
    elif name == 'extended-initializer-outside-rx':
        _pack(raw, 0x720, '<Q', 0x2000); _pack(raw, 0x3350, '<Q', 0x2000)
    elif name == 'extended-interposable-internal-object':
        _pack(raw, 0x3334, '<B', 0x11); _pack(raw, SHOFF+12*64+44, '<I', 2)
    elif name == 'extended-versioned-full-name-mismatch':
        start = 0x3200 + positions['full_versioned_offset'] + len(b'__h25_fixture_symbol@')
        raw[start:start+5] = b'BAD_1'
    elif name == 'extended-sysv-bad-bucket':
        right = elf_hash('PyInit__h25_field_service_v1') % 2
        buckets = [0, 0]; buckets[1-right] = 1
        pack_into('<IIIIII', raw, 0x600, 2, 2, buckets[0], buckets[1], 0, 0)
        _pack(raw, SHOFF+2*64+32, '<Q', 24)
    elif name == 'extended-sysv-bad-chain-index': _pack(raw, 0x610, '<I', 2)
    elif name == 'extended-gnu-unterminated-chain':
        _pack(raw, 0x63C, '<I', unpack_from('<I', raw, 0x63C)[0] & ~1)
    elif name == 'extended-gnu-wrong-bucket':
        h = 5381
        for byte in b'PyInit__h25_field_service_v1': h = (33*h+byte) & 0xFFFFFFFF
        buckets = [0, 0]; buckets[1-h%2] = 1
        _pack(raw, 0x620, '<I', 2)
        pack_into('<III', raw, 0x638, buckets[0], buckets[1], h|1)
        _pack(raw, SHOFF+3*64+32, '<Q', 36)
    elif name == 'extended-hash-pointer-mismatch': _pack(raw, 0x2148, '<Q', 0x608)
    elif name == 'extended-verneed-dependency-mismatch': _pack(raw, 0xB04, '<I', positions['weak_dynstr_offset'])
    elif name == 'extended-verneed-hash': _pack(raw, 0xB10, '<I', 0)
    elif name == 'extended-verneed-next': _pack(raw, 0xB1C, '<I', 16)
    elif name == 'extended-unused-version-record':
        _pack(raw, 0x902, '<H', 1); _pack(raw, 0x3348, '<I', positions['full_base_strong_offset'])
    elif name in ('extended-df-textrel', 'extended-unknown-tag', 'extended-unknown-flags', 'extended-relr'):
        tag, value = {'extended-df-textrel': (30, 4), 'extended-unknown-tag': (0x60000001, 0),
                      'extended-unknown-flags': (30, 1 << 31), 'extended-relr': (36, 0xA00)}[name]
        pack_into('<qQ', raw, 0x21A0, tag, value)
    elif name == 'extended-dynamic-after-null':
        pack_into('<qQ', raw, 0x21A0, 0, 0); pack_into('<qQ', raw, 0x21B0, 24, 0)
    elif name == 'extended-duplicate-dynamic-tag': pack_into('<qQ', raw, 0x21A0, 5, 0x800)
    elif name == 'extended-unsupported-relocation': _pack(raw, 0xA08, '<Q', 255)
    elif name == 'extended-readonly-relocation': _pack(raw, 0xA00, '<Q', 0x500)
    elif name == 'extended-unaligned-relocation': _pack(raw, 0xA00, '<Q', 0x2001)
    elif name == 'extended-relocation-symbol-range': _pack(raw, 0xA38, '<Q', (99 << 32) | 6)
    elif name == 'extended-external-nonzero-addend': _pack(raw, 0xA40, '<q', 1)
    elif name == 'extended-relative-nonzero-symbol': _pack(raw, 0xA08, '<Q', (1 << 32) | 8)
    elif name == 'extended-relative-target-outside': _pack(raw, 0xA10, '<q', 0x1000000)
    elif name == 'extended-relacount': _pack(raw, 0x21A8, '<Q', 1)
    elif name == 'extended-unadvertised-rela':
        data = bytearray(24); pack_into('<QQq', data, 0, 0x2000, 8, 0x500)
        raw = add_section(raw, '.rela.extra', 4, 2, 0xB00, data, 4, 9, 8, 24)
    elif name == 'extended-defined-symbol-relocation': _pack(raw, 0xA08, '<Q', (1 << 32) | 6); _pack(raw, 0xA10, '<q', 0)
    elif name == 'extended-plt-without-got':
        pack_into('<qQ', raw, 0x2170, 23, 0xA00); pack_into('<qQ', raw, 0x2180, 2, 48)
        pack_into('<qQ', raw, 0x2190, 20, 7); pack_into('<qQ', raw, 0x21A0, 0, 0)
        pack_into('<QQq', raw, 0xA00, 0x2040, (1 << 32)|7, 0)
        pack_into('<QQq', raw, 0xA18, 0x2048, (2 << 32)|7, 0)
        _pack(raw, SHOFF+7*64+32, '<Q', 48)
    elif name == 'extended-method-table-extent': _pack(raw, 0x3340, '<Q', 32)
    elif name == 'extended-method-name': raw[0x500] = ord('x')
    elif name == 'extended-method-padding': _pack(raw, 0x2014, '<I', 1)
    elif name == 'extended-method-doc': _pack(raw, 0x2018, '<Q', 1)
    elif name == 'extended-external-method-pointer':
        _pack(raw, 0xA20, '<Q', (1 << 32)|6); _pack(raw, 0xA28, '<q', 0)
        _pack(raw, 0x21A8, '<Q', 1)
    elif name == 'extended-method-interior-pointer': _pack(raw, 0xA28, '<q', 0x1011)
    elif name == 'extended-unlisted-code-pointer':
        _pack(raw, 0xA38, '<Q', 8); _pack(raw, 0xA40, '<q', 0x1010); _pack(raw, 0x21A8, '<Q', 3)
    elif name == 'extended-missing-helper':
        policy['required_local_functions'] = ('absent',)
        policy['method_tables'] = ({'symbol': 'h25_fixture_methods', 'entries': (('field_id', 'absent', 1, None),)},)
    elif name == 'extended-nonhidden-helper':
        _pack(raw, 0x331C, '<B', 0x12); _pack(raw, 0x3334, '<B', 0x11)
        _pack(raw, 0x3335, '<B', 2); _pack(raw, SHOFF+12*64+44, '<I', 1)
    elif name == 'extended-pointer-slot-outside-object': policy['pointer_slots'] = (('h25_fixture_methods', 64, 'h25_fixture_target'),)
    elif name == 'extended-dynamic-count-bound':
        # Independently bounded metadata overrun, rejected before allocating or iterating 1025 entries.
        _pack(raw, SHOFF+10*64+32, '<Q', 1025*16)
    elif name == 'extended-symbol-count-bound': _pack(raw, SHOFF+4*64+32, '<Q', 4097*24)
    elif name == 'extended-relocation-count-bound': _pack(raw, SHOFF+7*64+32, '<Q', 16385*24)
    elif name == 'extended-string-bound': policy['required_local_functions'] = ('x'*4097,)
    elif name == 'extended-hash-bloom-bound': _pack(raw, 0x628, '<I', 256)
    elif name == 'extended-method-table-count-bound': policy['method_tables'] = policy['method_tables']*33
    elif name == 'extended-pointer-slot-count-bound': policy['pointer_slots'] = (('h25_fixture_methods', 0, 'h25_fixture_target'),)*513
    elif name == 'extended-relro-no-effective-page':
        _pack(raw, 64+5*56+32, '<Q', 0x1C0); _pack(raw, 64+5*56+40, '<Q', 0x1C0)
    elif name == 'extended-relro-straddles-effective-end':
        return make_page_crossing_dynamic_fixture(False)
    elif name == 'extended-wrong-page-profile': policy['page_profile']['page_size'] = 8192
    elif name == 'extended-data-link-retargeted': _pack(raw, 0xA40, '<q', 0x2060)
    elif name == 'extended-data-link-relocation-missing':
        # Keep five legitimate data relocations but move the module link away from its fixed field.
        _pack(raw, 0xA30, '<Q', 0x2058)
    else: raise RuntimeError('unknown extended static fixture')
    return bytes(raw), policy


def _provider_state(candidate, versioned=False, plt=False):
    if versioned:
        raw, static, _ = make_versioned_fixture()
    elif plt:
        raw, static = make_notype_plt_fixture()
    else:
        raw, static = make_import_fixture()
    parsed = candidate.admit_service_elf(raw, sha256(raw).hexdigest(), static)
    policy0, maps, resolved = initial_provider_fixtures(parsed)
    policy = runtime_policy_v2(policy0)
    if plt:
        policy['symbols'][0]['symbol_type'] = 0
        _set_result(resolved, 0, type=0)
    if versioned:
        policy['maps'][1]['aliases'] += ('libfixture.so',)
        policy['needed'] = (('libfixture.so', 'system'),)
        policy['maps'][0]['version_definitions'] = ((2, 'H25_1', elf_hash('H25_1'), 0),)
        policy['maps'][1]['version_definitions'] = ((2, 'H25_1', elf_hash('H25_1'), 0),)
        policy['symbols'][0]['version'] = 'H25_1'
        policy['symbols'][0]['search'][0][1]['version'] = 'H25_1'
        result = list(resolved['symbol_results'][0]); result[1] = 'H25_1'
        resolved['symbol_results'] = (tuple(result),) + resolved['symbol_results'][1:]
    return parsed, policy, maps, resolved


def _set_result(resolved, index, **changes):
    fields = ('name', 'version', 'weak', 'type', 'address', 'base', 'owner', 'nearest_type', 'nearest_address')
    row = list(resolved['symbol_results'][index])
    for name, value in changes.items(): row[fields.index(name)] = value
    results = list(resolved['symbol_results']); results[index] = tuple(row)
    resolved['symbol_results'] = tuple(results)


def _vdso(policy, maps, resolved):
    row = {'id': 'vdso', 'name': 'linux-vdso.so.1', 'kind': 'os', 'identity_kind': 'kernel_vdso',
       'sha256': policy['launch_tcb_sha256'], 'phdr_offset': 64,
       'segments': ((0, 4096, 4), (4096, 8192, 5)), 'aliases': ('linux-vdso.so.1',),
       'dependencies': (), 'global': False, 'retained': True, 'relocated': True,
       'initialized': True, 'version_definitions': ()}
    policy['maps'] += (row,)
    native = (0x300000, 0x300040, 'linux-vdso.so.1', ((0x300000, 0x301000, 4), (0x301000, 0x302000, 5)))
    for value in (maps, resolved):
        value['maps_before'] += (native,); value['maps_after'] += (native,)


def _ifunc(policy, resolved):
    policy['maps'][0]['kind'] = 'os'
    definition = policy['symbols'][0]['search'][0][1]
    definition['type'] = 10
    definition['ifunc_families'] = (('main', 0x1100, 0x1120),)
    _set_result(resolved, 0, address=0x101108, nearest_type=2, nearest_address=0x101108)


def _provider_input(candidate, name):
    versioned = name in ('extended-required-version-missing-despite-interposer',
                         'extended-version-node-hash', 'extended-duplicate-version-node')
    parsed, policy, maps, resolved = _provider_state(candidate, versioned,
        name in ('extended-jump-slot-notype-object-winner', 'extended-jump-slot-notype-data-winner'))
    phase = 'maps'
    if name == 'extended-wrong-snapshot-scope': maps['scope'] = 'RTLD_LOCAL-is-not-proof'
    elif name == 'extended-map-phdr-drift':
        row = list(maps['maps_before'][0]); row[1] += 8
        maps['maps_before'] = maps['maps_after'] = (tuple(row),) + maps['maps_before'][1:]
    elif name == 'extended-duplicate-map-name':
        row = list(maps['maps_before'][1]); row[2] = maps['maps_before'][0][2]
        maps['maps_before'] = maps['maps_after'] = maps['maps_before'][:1] + (tuple(row),)
    elif name == 'extended-map-segment-overlap':
        row = list(maps['maps_before'][0]); row[3] = ((0x100000, 0x101100, 4), (0x101000, 0x102000, 5), (0x102000, 0x103000, 6))
        maps['maps_before'] = maps['maps_after'] = (tuple(row),) + maps['maps_before'][1:]
    elif name == 'extended-vdso-fake-file':
        policy['maps'][0]['name'] = 'linux-vdso.so.1'; policy['maps'][0]['aliases'] = ('linux-vdso.so.1',)
    elif name == 'extended-vdso-provider':
        first = policy['maps'][0]
        first.update(name='linux-vdso.so.1', aliases=('linux-vdso.so.1',), identity_kind='kernel_vdso',
                     kind='os', sha256=policy['launch_tcb_sha256'])
    elif name == 'extended-omitted-search-row': policy['symbols'][0]['search'] = policy['symbols'][0]['search'][:1]
    elif name == 'extended-local-dependency-fallback':
        policy['maps'][1]['global'] = False; policy['global_scope'] = ('main',)
        policy['maps'][1]['aliases'] += ('libfixture.so',); policy['needed'] = (('libfixture.so', 'system'),)
        for symbol in policy['symbols']: symbol['search'] = symbol['search'][:1]
    elif name == 'extended-unknown-needed-alias': policy['needed'] = (('missing.so', 'system'),)
    elif name == 'extended-dependency-alias-ambiguity': policy['maps'][0]['aliases'] += ('/fixture/libsystem.so',)
    elif name == 'extended-unresolved-strong': policy['symbols'][0]['search'] = (('main', None), ('system', None))
    elif name == 'extended-resolved-zero':
        _set_result(resolved, 0, address=0, base=0, owner='', nearest_type=None, nearest_address=None); phase = 'results'
    elif name == 'extended-weak-zero-owner':
        _set_result(resolved, 1, base=0x100000, owner='/fixture/python'); phase = 'results'
    elif name == 'extended-wrong-symbol-version': _set_result(resolved, 0, version='OTHER'); phase = 'results'
    elif name in ('extended-ifunc-unknown-family', 'extended-ifunc-overlapping-families', 'extended-ifunc-vdso-family'):
        _ifunc(policy, resolved)
        if name == 'extended-ifunc-unknown-family':
            _set_result(resolved, 0, address=0x101120, nearest_address=0x101120); phase = 'results'
        elif name == 'extended-ifunc-overlapping-families':
            policy['symbols'][0]['search'][0][1]['ifunc_families'] = (('main', 0x1100, 0x1120), ('main', 0x1108, 0x1128))
            _set_result(resolved, 0, address=0x101110, nearest_address=0x101110); phase = 'results'
        else:
            _vdso(policy, maps, resolved)
            policy['symbols'][0]['search'][0][1]['ifunc_families'] = (('vdso', 0x1100, 0x1120),)
    elif name == 'extended-import-count-bound': policy['symbols'] = policy['symbols'][:1]*513
    elif name == 'extended-map-count-bound': policy['maps'] = policy['maps'][:1]*257
    elif name == 'extended-segment-count-bound': policy['maps'][0]['segments'] = policy['maps'][0]['segments'][:1]*65
    elif name == 'extended-required-version-missing-despite-interposer':
        # Named DT_NEEDED dependency lacks the requirement; global winner still
        # advertises and supplies H25_1. These are independent loader obligations.
        policy['maps'][1]['version_definitions'] = (); phase = 'requests'
    elif name == 'extended-version-node-hash': policy['maps'][1]['version_definitions'] = ((2, 'H25_1', 0, 0),)
    elif name == 'extended-duplicate-version-node': policy['maps'][1]['version_definitions'] *= 2
    elif name in ('extended-jump-slot-notype-object-winner', 'extended-jump-slot-notype-data-winner'):
        definition = policy['symbols'][0]['search'][0][1]
        definition['type'] = 1 if name.endswith('object-winner') else 0
        definition['value'] = 0x2100
        phase = 'requests'
    else: raise RuntimeError('unknown extended provider fixture')
    return parsed, policy, maps, resolved, phase


def _remove_hash(raw0, tag, section_index):
    raw = bytearray(raw0)
    entries = [unpack_from('<qQ', raw, 0x2100 + 16*i) for i in range(12)]
    entries = [item for item in entries if item[0] != tag]
    entries += [(0, 0)] * (12-len(entries))
    for index, values in enumerate(entries): pack_into('<qQ', raw, 0x2100+16*index, *values)
    _pack(raw, SHOFF+section_index*64+4, '<I', 1)
    _pack(raw, SHOFF+section_index*64+40, '<I', 0)
    _pack(raw, SHOFF+section_index*64+56, '<Q', 0)
    return bytes(raw)


def run_extended(candidate, mode):
    expected, rows = expectations(), []
    def rejection(name, operation, callbacks):
        error = message = None
        try: operation()
        except BaseException as exc:
            need(type(exc) is candidate.ELFAdmissionError, 'extended exact rejection type: '+name)
            error, message = type(exc).__name__, str(exc)
            if name == 'extended-relro-no-effective-page':
                need(message == 'RELRO protects no complete pages', 'exact no-effective-page rejection')
            elif name == 'extended-relro-straddles-effective-end':
                need(message == 'dynamic table outside effective RELRO', 'exact partial-effective-page rejection')
            elif name == 'extended-required-version-missing-despite-interposer':
                need(message == 'named dependency missing/ambiguous required version', 'exact named dependency version rejection')
            elif name == 'extended-data-link-retargeted':
                need(message == 'source pointer slot mismatch', 'exact own-data link target rejection')
            elif name == 'extended-data-link-relocation-missing':
                need(message == 'nonlocal/missing source pointer relocation', 'exact own-data link omission rejection')
            elif name in ('extended-jump-slot-notype-object-winner', 'extended-jump-slot-notype-data-winner'):
                need(message == 'resolved PLT relocation requires function provider', 'exact PLT provider type rejection')
        rows.append(record(name, {'accepted': error is None, 'exception': error,
                                  'foreign_callbacks': len(callbacks)}, expected[name],
                           {'exception_message': message}))
    for name, kind in STATIC_CASES:
        raw, policy = _static_input(name, kind)
        need(type(raw) is bytes and len(raw) <= 32768, 'extended fixture byte bound')
        rejection(name, lambda: candidate.admit_service_elf(raw, sha256(raw).hexdigest(), policy), [])
    for name in DATA_CASES:
        raw, policy = make_fixture()
        digest, callbacks = sha256(raw).hexdigest(), []
        class Foreign:
            def __eq__(self, other): callbacks.append('eq'); raise RuntimeError('foreign equality forbidden')
            def __hash__(self): callbacks.append('hash'); raise RuntimeError('foreign hash forbidden')
        if name == 'extended-dict-nonstring-key': policy[3] = None
        elif name == 'extended-sequence-list': policy['expected_exports'] = list(policy['expected_exports'])
        elif name == 'extended-bool-integer':
            policy['method_tables'] = ({'symbol': 'h25_fixture_methods', 'entries': (('field_id', 'h25_fixture_target', True, None),)},)
        elif name == 'extended-foreign-equality': policy['schema'] = Foreign()
        elif name == 'extended-cyclic-record': policy['cycle'] = policy
        elif name == 'extended-aggregate-record-bound': policy['large'] = {str(i): (None,)*64 for i in range(3500)}
        elif name == 'extended-extra-policy-key': policy['extra'] = None
        elif name == 'extended-missing-digest': digest = None
        elif name == 'extended-static-receipt-digest':
            parsed, runtime, maps, resolved = _provider_state(candidate)
            parsed['receipt_sha256'] = '0'*64
            rejection(name, lambda: candidate.provider_requests(parsed, runtime), callbacks)
            continue
        rejection(name, lambda: candidate.admit_service_elf(raw, digest, policy), callbacks)
        if name == 'extended-cyclic-record': policy.pop('cycle')
    for name in PROVIDER_CASES:
        parsed, policy, maps, resolved, phase = _provider_input(candidate, name)
        if phase == 'maps': operation = lambda: candidate.admit_loaded_maps(maps, policy)
        elif phase == 'requests': operation = lambda: candidate.provider_requests(parsed, policy)
        else:
            admitted = candidate.admit_loaded_maps(maps, policy)
            operation = lambda: candidate.admit_runtime_provider_map(parsed, resolved, policy, admitted)
        rejection(name, operation, [])
    for name in POSITIVE_CASES:
        details = {}
        if name in ('extended-positive-versioned-elf', 'extended-positive-data-link',
                    'extended-positive-sysv-only', 'extended-positive-gnu-only',
                    'extended-positive-page-crossing-dynamic'):
            if name == 'extended-positive-versioned-elf': raw, policy, _ = make_versioned_fixture()
            elif name == 'extended-positive-data-link': raw, policy = make_data_link_fixture()
            elif name == 'extended-positive-page-crossing-dynamic': raw, policy = make_page_crossing_dynamic_fixture(True)
            else:
                raw, policy = make_fixture()
                raw = _remove_hash(raw, 0x6FFFFEF5, 3) if name.endswith('sysv-only') else _remove_hash(raw, 4, 2)
            parsed = candidate.admit_service_elf(raw, sha256(raw).hexdigest(), policy)
            need(parsed['initializer'] == ('PyInit__h25_field_service_v1', 0x1000, 1) and
                 parsed['page_size'] == 4096 and parsed['effective_relro'] == ((0x2000, 0x4000) if name == 'extended-positive-page-crossing-dynamic' else (0x2000, 0x3000)),
                 'extended independent initializer/effective RELRO')
            if name == 'extended-positive-versioned-elf':
                need(parsed['imports'][0]['name'] == '__h25_fixture_symbol' and
                     parsed['imports'][0]['version'] == 'H25_1' and
                     parsed['imports'][0]['version_file'] == 'libfixture.so', 'extended literal version binding')
            details = {'initializer': list(parsed['initializer']), 'effective_relro': list(parsed['effective_relro'])}
        else:
            versioned = name == 'extended-positive-versioned-provider'
            plt = name == 'extended-positive-jump-slot-notype-function'
            parsed, policy, maps, resolved = _provider_state(candidate, versioned, plt)
            expected_strong = 0x101100
            expected_kind = 'ordinary-definition'
            if name == 'extended-positive-os-ifunc':
                _ifunc(policy, resolved); expected_strong = 0x101108; expected_kind = 'trusted-os-ifunc-family'
            elif name == 'extended-positive-vdso-inventory': _vdso(policy, maps, resolved)
            elif name == 'extended-positive-local-project':
                row = deepcopy(policy['maps'][1])
                row.update(id='local-project', name='/fixture/project.so', aliases=('/fixture/project.so',), kind='ordinary_project', global_=False)
                row.pop('global_'); row['global'] = False
                policy['maps'] += (row,)
                native = (0x300000, 0x300040, '/fixture/project.so',
                          ((0x300000, 0x301000, 4), (0x301000, 0x302000, 5), (0x302000, 0x303000, 6)))
                for snapshot in (maps, resolved):
                    snapshot['maps_before'] += (native,); snapshot['maps_after'] += (native,)
            admitted = candidate.admit_loaded_maps(maps, policy)
            receipt = candidate.admit_runtime_provider_map(parsed, resolved, policy, admitted)
            expected_version = 'H25_1' if versioned else None
            literal_relocations = ((0x2098 if plt else 0x2040, 7 if plt else 6, '__h25_fixture_symbol', expected_version, expected_strong),
                                   (0x2048, 6, '__h25_fixture_weak', None, 0))
            need(receipt['relocation_results'] == literal_relocations and
                 receipt['symbols'][0][2] == expected_kind and receipt['symbols'][1][2] == 'unresolved-weak-zero',
                 'extended exact complete relocation-result oracle')
            if versioned:
                need(candidate.provider_requests(parsed, policy) == (('__h25_fixture_symbol', 'H25_1', False, 2), ('__h25_fixture_weak', None, True, 2)),
                     'literal versioned request')
                need(receipt['version_requirement_results'] == (('libfixture.so', 'system', 'H25_1', 2, 0x4B5B21, 2),),
                     'literal named dependency version-node result')
            details = {'relocation_results': [list(row) for row in receipt['relocation_results']]}
            if versioned: details['version_requirement_results'] = [list(row) for row in receipt['version_requirement_results']]
        rows.append(record(name, {'accepted': True, 'independent_literal_checks': True}, expected[name], details))
    return finish(rows, CASE_IDS, NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT, expected, mode)


def validate_extended(receipt, mode):
    validate(receipt, CASE_IDS, NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT, expectations(), mode)
    by_name = {row['case_id']: row for row in receipt['records']}
    exact_errors = {
        'extended-relro-no-effective-page': 'RELRO protects no complete pages',
        'extended-relro-straddles-effective-end': 'dynamic table outside effective RELRO',
        'extended-required-version-missing-despite-interposer': 'named dependency missing/ambiguous required version',
        'extended-data-link-retargeted': 'source pointer slot mismatch',
        'extended-data-link-relocation-missing': 'nonlocal/missing source pointer relocation',
        'extended-jump-slot-notype-object-winner': 'resolved PLT relocation requires function provider',
        'extended-jump-slot-notype-data-winner': 'resolved PLT relocation requires function provider'}
    for name, message in exact_errors.items():
        need(by_name[name]['details'] == {'exception_message': message}, 'extended repaired-predicate exact error evidence')
    need(by_name['extended-positive-page-crossing-dynamic']['details'] == {
        'initializer': ['PyInit__h25_field_service_v1', 0x1000, 1], 'effective_relro': [0x2000, 0x4000]},
        'extended paired effective-page positive evidence')
    for name in ('extended-positive-relocation-results', 'extended-positive-os-ifunc',
                 'extended-positive-vdso-inventory', 'extended-positive-local-project',
                 'extended-positive-versioned-provider', 'extended-positive-jump-slot-notype-function'):
        version = 'H25_1' if name == 'extended-positive-versioned-provider' else None
        plt = name == 'extended-positive-jump-slot-notype-function'
        address = 0x101108 if name == 'extended-positive-os-ifunc' else 0x101100
        literal = [[0x2098 if plt else 0x2040, 7 if plt else 6, '__h25_fixture_symbol', version, address],
                   [0x2048, 6, '__h25_fixture_weak', None, 0]]
        details = by_name[name]['details']
        need(details.get('relocation_results') == literal, 'extended literal relocation receipt evidence')
        if version is not None:
            need(details.get('version_requirement_results') == [['libfixture.so', 'system', 'H25_1', 2, 0x4B5B21, 2]],
                 'extended literal named-version receipt evidence')
    return receipt

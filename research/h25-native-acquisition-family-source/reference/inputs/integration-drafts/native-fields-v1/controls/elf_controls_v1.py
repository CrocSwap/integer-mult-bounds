"""Pure-parser controls with independent literal bytes. Never performs loading."""
from hashlib import sha256
from struct import pack_into
from elf_literal_fixture_v1 import make_fixture, SHOFF, INITIALIZER, SIZE
from receipt_contract_v1 import need, record, finish

# All offsets belong to the independent fixed fixture, never candidate output.
# Each mutation encodes an independently forbidden ELF property. Rejection
# messages may reflect an earlier violated invariant; exact class is mandatory.
MUTATIONS = (
 ('bad-magic', 0, '<I', 0), ('elf32', 4, '<B', 1), ('big-endian', 5, '<B', 2),
 ('wrong-machine', 18, '<H', 183), ('wrong-etype', 16, '<H', 2),
 ('entry-present', 24, '<Q', 0x1000), ('ph-table-overflow', 32, '<Q', (1 << 64)-8),
 ('sh-table-overflow', 40, '<Q', (1 << 64)-8), ('ph-entry-size', 54, '<H', 55),
 ('sh-entry-size', 58, '<H', 63), ('zero-programs', 56, '<H', 0),
 ('oversized-sections', 60, '<H', 257), ('load-file-overflow', 64+32, '<Q', 1 << 63),
 ('load-page-overlap', 64+56+16, '<Q', 0), ('writable-executable', 64+56+4, '<I', 7),
 ('executable-zero-fill', 64+56+40, '<Q', 33), ('executable-stack', 64+4*56+4, '<I', 7),
 ('section-outside-file', SHOFF+64+24, '<Q', SIZE),
 ('section-overlap', SHOFF+2*64+24, '<Q', 0x500),
 ('bad-dynamic-link', SHOFF+10*64+40, '<I', 11),
 ('sysv-hash-unreachable', 0x608, '<I', 0), ('sysv-hash-cycle', 0x610, '<I', 1),
 ('gnu-hash-unreachable', 0x638, '<I', 0), ('gnu-hash-bloom', 0x630, '<Q', 0),
 ('gnu-hash-chain', 0x63C, '<I', 0), ('dynstr-unterminated', 0x81D, '<B', 65),
 ('initializer-weak', 0x71C, '<B', 0x22), ('initializer-ifunc', 0x71C, '<B', 0x1A),
 ('initializer-hidden', 0x71D, '<B', 2), ('initializer-undefined', 0x71E, '<H', 0),
 ('initializer-absolute', 0x71E, '<H', 0xFFF1), ('initializer-empty', 0x728, '<Q', 0),
 ('initializer-wrong-name', 0x801, '<B', 88), ('initializer-versioned', 0x902, '<H', 2),
 ('initializer-hidden-version', 0x902, '<H', 0x8001),
 ('irelative', 0xA08, '<Q', 37), ('copy-relocation', 0xA08, '<Q', 5),
 ('text-relocation', 0xA00, '<Q', 0x1000), ('metadata-relocation', 0xA00, '<Q', 0x700),
 ('duplicate-relocation', 0xA18, '<Q', 0x2000), ('wrong-method-target', 0xA28, '<q', 0x1000),
 ('method-terminator', 0x2020, '<Q', 1), ('method-flags', 0x2010, '<I', 2),
 ('ctor-init', 0x21A0, '<q', 12), ('ctor-array', 0x21A0, '<q', 25),
 ('ctor-preinit', 0x21A0, '<q', 32), ('fini', 0x21A0, '<q', 13),
 ('fini-array', 0x21A0, '<q', 26), ('soname', 0x21A0, '<q', 14),
 ('filter', 0x21A0, '<q', 0x7FFFFFFF), ('auxiliary', 0x21A0, '<q', 0x7FFFFFFD),
 ('audit', 0x21A0, '<q', 0x6FFFFEFC), ('depaudit', 0x21A0, '<q', 0x6FFFFEFB),
 ('rpath', 0x21A0, '<q', 15), ('runpath', 0x21A0, '<q', 29),
 ('symbolic', 0x21A0, '<q', 16), ('textrel-tag', 0x21A0, '<q', 22),
 ('new-needed', 0x21A0, '<q', 1), ('initfirst-flags', 0x21A0, '<q', 0x6FFFFFFB))
CASE_IDS = ('literal-valid-both-hashes',) + tuple('elf-' + row[0] for row in MUTATIONS) + (
    'elf-digest-mismatch', 'elf-bytes-subclass', 'elf-truncated', 'elf-oversized', 'elf-policy-subclass')
NORMAL_CASE_COUNT = 65
OPTIMIZED_CASE_COUNT = 65


def expectations():
    result = {CASE_IDS[0]: {'accepted': True, 'static_only': True,
                          'initializer': INITIALIZER, 'bytes': SIZE}}
    for name in CASE_IDS[1:]:
        result[name] = {'accepted': False, 'exception': 'ELFAdmissionError', 'entry': 'pure-admit_service_elf'}
    need(len(CASE_IDS) == 65 and len(result) == 65, 'ELF literal inventory')
    return result


def run_static_elf_controls(admit_service_elf, admission_error_type, mode):
    raw, policy = make_fixture()
    need(type(raw) is bytes and len(raw) == SIZE and SIZE < 8 * 1024 * 1024, 'literal ELF fixture bound')
    expected = expectations()
    rows = []
    parsed = admit_service_elf(raw, sha256(raw).hexdigest(), policy)
    need(type(parsed) is dict and parsed.get('initializer') == (INITIALIZER, 0x1000, 1), 'literal initializer extent')
    need(parsed.get('sha256') == sha256(raw).hexdigest(), 'literal ELF digest')
    rows.append(record(CASE_IDS[0], {'accepted': True, 'static_only': parsed.get('static_only'),
                                    'initializer': parsed['initializer'][0], 'bytes': parsed.get('bytes')}, expected[CASE_IDS[0]]))
    def reject(name, value, digest, profile):
        exception = None
        error_text = None
        try:
            admit_service_elf(value, digest, profile)
        except BaseException as exc:
            need(type(exc) is admission_error_type, 'ELF rejection exact exception: ' + name)
            need(type(str(exc)) is str and bool(str(exc)), 'ELF rejection preserves error')
            exception = type(exc).__name__
            error_text = str(exc)
        # Pure-parser entry has no loader capability; passing a loading wrapper
        # is forbidden by parent source admission. No malicious code executes.
        rows.append(record(name, {'accepted': exception is None, 'exception': exception,
                                  'entry': 'pure-admit_service_elf'}, expected[name], {'exception_message': error_text}))
    for name, offset, fmt, value in MUTATIONS:
        mutated = bytearray(raw)
        pack_into(fmt, mutated, offset, value)
        if name == 'initfirst-flags':
            pack_into('<Q', mutated, 0x21A8, 0x20)
        if name == 'load-page-overlap':
            pack_into('<Q', mutated, 64 + 56 + 24, 0)
        mutated = bytes(mutated)
        need(mutated != raw and len(mutated) == SIZE, 'literal ELF mutation effective')
        reject('elf-' + name, mutated, sha256(mutated).hexdigest(), policy)
    reject('elf-digest-mismatch', raw, '0' * 64, policy)
    class BytesSubclass(bytes):
        pass
    class DictSubclass(dict):
        pass
    reject('elf-bytes-subclass', BytesSubclass(raw), sha256(raw).hexdigest(), policy)
    reject('elf-truncated', raw[:63], sha256(raw[:63]).hexdigest(), policy)
    # Production profile bound is 8 MiB; this test allocates at most 8 MiB + 1.
    oversized = bytes(8 * 1024 * 1024 + 1)
    reject('elf-oversized', oversized, sha256(oversized).hexdigest(), policy)
    reject('elf-policy-subclass', raw, sha256(raw).hexdigest(), DictSubclass(policy))
    count = NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT
    return finish(rows, CASE_IDS, count, expected, mode)

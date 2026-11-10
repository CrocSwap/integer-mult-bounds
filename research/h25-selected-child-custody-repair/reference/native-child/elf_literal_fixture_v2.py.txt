"""Append-only v2 fixture/profile additions; never load these synthetic bytes."""
from struct import pack_into, unpack_from
from elf_literal_fixture_v1 import make_fixture as base_v1, make_import_fixture as imports_v1, SHOFF

PAGE_PROFILE = {'schema': 'h25-amd64-page-profile-v1', 'page_size': 4096}


def profile_v2(profile):
    if type(profile) is not dict:
        return profile  # preserve exact-type adverse controls
    result = dict(profile)
    result['schema'] = 'h25-static-elf-policy-v2'
    result['page_profile'] = dict(PAGE_PROFILE)
    return result


def make_fixture():
    raw, profile = base_v1()
    return raw, profile_v2(profile)


def make_import_fixture():
    raw, profile = imports_v1()
    return raw, profile_v2(profile)


def elf_hash(text):
    # Fixture encoding from the ELF string-hash algorithm, never target output.
    value = 0
    for byte in text.encode('ascii'):
        value = (value << 4) + byte
        high = value & 0xF0000000
        if high: value ^= high >> 24
        value &= ~high
    return value & 0xFFFFFFFF


def add_section(raw, name, typ, flags, address, data, link=0, info=0, align=8, entsize=0):
    """Bounded fixture writer, not an ELF validator or parser oracle."""
    raw = bytearray(raw)
    count = unpack_from('<H', raw, 60)[0]
    new_end = SHOFF + (count + 1) * 64
    if len(raw) < new_end: raw.extend(bytes(new_end - len(raw)))
    shstr_size = unpack_from('<Q', raw, SHOFF + 13 * 64 + 32)[0]
    encoded_name = name.encode('ascii') + b'\0'
    if shstr_size + len(encoded_name) >= 0x200: raise RuntimeError('fixture section names bound')
    raw[0x3000 + shstr_size:0x3000 + shstr_size + len(encoded_name)] = encoded_name
    pack_into('<Q', raw, SHOFF + 13 * 64 + 32, shstr_size + len(encoded_name))
    raw[address:address + len(data)] = data
    pack_into('<IIQQQQIIQQ', raw, SHOFF + count * 64, shstr_size, typ, flags,
              address if flags & 2 else 0, address, len(data), link, info, align, entsize)
    pack_into('<H', raw, 60, count + 1)
    if flags & 2 and address < 0x1000:
        pack_into('<Q', raw, 64 + 32, 0xC00)
        pack_into('<Q', raw, 64 + 40, 0xC00)
    return raw


def make_versioned_fixture():
    raw0, profile = make_import_fixture()
    raw = bytearray(raw0)
    dyn_size = unpack_from('<Q', raw, SHOFF + 5 * 64 + 32)[0]
    library_offset = dyn_size
    version_offset = library_offset + len(b'libfixture.so\0')
    appended = b'libfixture.so\0H25_1\0'
    raw[0x800 + dyn_size:0x800 + dyn_size + len(appended)] = appended
    pack_into('<Q', raw, SHOFF + 5 * 64 + 32, dyn_size + len(appended))
    pack_into('<Q', raw, 0x2128, dyn_size + len(appended))
    pack_into('<H', raw, 0x902, 2)
    full_size = unpack_from('<Q', raw, SHOFF + 11 * 64 + 32)[0]
    full_versioned = b'__h25_fixture_symbol@H25_1\0'
    raw[0x3200 + full_size:0x3200 + full_size + len(full_versioned)] = full_versioned
    pack_into('<Q', raw, SHOFF + 11 * 64 + 32, full_size + len(full_versioned))
    pack_into('<I', raw, 0x3348, full_size)
    verneed = bytearray(32)
    pack_into('<HHIII', verneed, 0, 1, 1, library_offset, 16, 0)
    pack_into('<IHHII', verneed, 16, elf_hash('H25_1'), 0, 2, version_offset, 0)
    raw = add_section(raw, '.gnu.version_r', 0x6FFFFFFE, 2, 0xB00, verneed, 5, 1, 8, 0)
    for index, values in enumerate(((1, library_offset), (0x6FFFFFFE, 0xB00),
                                    (0x6FFFFFFF, 1), (0, 0))):
        pack_into('<qQ', raw, 0x21B0 + index * 16, *values)
    pack_into('<Q', raw, SHOFF + 10 * 64 + 32, 240)
    pack_into('<Q', raw, 64 + 3 * 56 + 32, 240)
    pack_into('<Q', raw, 64 + 3 * 56 + 40, 240)
    profile['needed'] = ('libfixture.so',)
    positions = {'library_offset': library_offset, 'version_offset': version_offset,
                 'full_versioned_offset': full_size, 'full_base_strong_offset': 69,
                 'weak_dynstr_offset': 51}
    return bytes(raw), profile, positions


def runtime_policy_v2(policy):
    if type(policy) is not dict: return policy
    result = dict(policy)
    result['schema'] = 'h25-runtime-provider-policy-v2'
    rows = []
    for item in policy['maps']:
        item = dict(item)
        item['version_definitions'] = ()
        rows.append(item)
    result['maps'] = tuple(rows)
    return result


def initial_v1_adapter(candidate):
    """Explicit source-owned adapter for frozen initial91 inputs under v2.

    Only required literal schema/page/version-inventory fields are added;
    malformed raw bytes, wrong exact policy types, maps/results and mutations
    remain intact. This is not a parser fallback or an execution permission.
    """
    class Adapter:
        ELFAdmissionError = candidate.ELFAdmissionError
        @staticmethod
        def admit_service_elf(raw, digest, profile):
            return candidate.admit_service_elf(raw, digest, profile_v2(profile))
        @staticmethod
        def admit_loaded_maps(snapshot, policy):
            return candidate.admit_loaded_maps(snapshot, runtime_policy_v2(policy))
        @staticmethod
        def provider_requests(parsed, policy):
            return candidate.provider_requests(parsed, runtime_policy_v2(policy))
        @staticmethod
        def admit_runtime_provider_map(parsed, snapshot, policy, maps):
            return candidate.admit_runtime_provider_map(parsed, snapshot, runtime_policy_v2(policy), maps)
    return Adapter


def make_data_link_fixture():
    """Independent own-data dispatch link plus two valid own method arrays."""
    raw0, profile = make_fixture()
    raw = bytearray(raw0)
    strings = b'\0h25_fixture_target\0h25_fixture_methods\0'
    initializer_offset = len(strings)
    strings += b'PyInit__h25_field_service_v1\0'
    module_offset = len(strings); strings += b'h25_fixture_module\0'
    alternate_offset = len(strings); strings += b'h25_fixture_methods_alt\0'
    raw[0x3200:0x3200 + len(strings)] = strings
    pack_into('<Q', raw, SHOFF + 11 * 64 + 32, len(strings))
    raw[0x3348:0x3390] = bytes(72)
    pack_into('<IBBHQQ', raw, 0x3348, module_offset, 0x01, 0, 9, 0x2050, 16)
    pack_into('<IBBHQQ', raw, 0x3360, alternate_offset, 0x01, 0, 9, 0x2060, 64)
    pack_into('<IBBHQQ', raw, 0x3378, initializer_offset, 0x12, 0, 8, 0x1000, 1)
    pack_into('<Q', raw, SHOFF + 12 * 64 + 32, 144)
    pack_into('<I', raw, SHOFF + 12 * 64 + 44, 5)
    pack_into('<Q', raw, SHOFF + 9 * 64 + 32, 160)
    pack_into('<I', raw, 0x2070, 1)
    for offset, destination, target in ((0xA30, 0x2050, 0x2000), (0xA48, 0x2060, 0x500), (0xA60, 0x2068, 0x1010)):
        pack_into('<QQq', raw, offset, destination, 8, target)
    pack_into('<Q', raw, SHOFF + 7 * 64 + 32, 120)
    pack_into('<Q', raw, 0x2188, 120)
    pack_into('<Q', raw, 0x21A8, 5)
    profile['required_local_objects'] += ('h25_fixture_module', 'h25_fixture_methods_alt')
    profile['method_tables'] += ({'symbol': 'h25_fixture_methods_alt',
          'entries': (('field_id', 'h25_fixture_target', 1, None),)},)
    profile['pointer_slots'] = (('h25_fixture_module', 0, 'h25_fixture_methods'),)
    return bytes(raw), profile


def make_page_crossing_dynamic_fixture(covered):
    """Nonempty effective RELRO with .dynamic across its last page boundary.

    Both variants use RW[0x2000,0x4000) and dynamic[0x2f80,0x3040).
    covered=True protects through0x4000; False has nominal end0x3040 and
    effective end0x3000. All nonallocated metadata is shifted by one page.
    """
    old, profile = make_fixture()
    raw = bytearray(len(old) + 4096)
    raw[:0x3000] = old[:0x3000]
    raw[0x4000:] = old[0x3000:]
    new_shoff = SHOFF + 4096
    _dynamic = old[0x2100:0x21C0]
    raw[0x2100:0x21C0] = bytes(192)
    raw[0x2F80:0x3040] = _dynamic
    pack_into('<Q', raw, 40, new_shoff)
    for section in (11, 12, 13):
        off = unpack_from('<Q', raw, new_shoff+64*section+24)[0]
        pack_into('<Q', raw, new_shoff+64*section+24, off+4096)
    for offset in (new_shoff+10*64+16, new_shoff+10*64+24): pack_into('<Q', raw, offset, 0x2F80)
    for offset in (64+3*56+8, 64+3*56+16, 64+3*56+24): pack_into('<Q', raw, offset, 0x2F80)
    for offset in (64+2*56+32, 64+2*56+40): pack_into('<Q', raw, offset, 0x2000)
    relro_size = 0x2000 if covered else 0x1040
    for offset in (64+5*56+32, 64+5*56+40): pack_into('<Q', raw, offset, relro_size)
    return bytes(raw), profile


def make_notype_plt_fixture():
    """Valid literal PLT/GOT baseline with STT_NOTYPE strong JUMP_SLOT import."""
    old, profile = make_import_fixture()
    raw = bytearray(old)
    pack_into('<B', raw, 0x71C, 0x10)
    pack_into('<B', raw, 0x334C, 0x10)
    raw[0xA30:0xA48] = old[0xA48:0xA60]
    pack_into('<Q', raw, SHOFF+7*64+32, 72)
    pack_into('<Q', raw, 0x2188, 72)
    raw = add_section(raw, '.got.plt', 1, 3, 0x2080, bytes(32), align=8)
    relocation = bytearray(24)
    pack_into('<QQq', relocation, 0, 0x2098, (1 << 32)|7, 0)
    raw = add_section(raw, '.rela.plt', 4, 2, 0xB00, relocation, 4, 14, 8, 24)
    for index, values in enumerate(((3, 0x2080), (23, 0xB00), (2, 24), (20, 7), (0, 0))):
        pack_into('<qQ', raw, 0x21B0+16*index, *values)
    pack_into('<Q', raw, SHOFF+10*64+32, 256)
    for offset in (64+3*56+32, 64+3*56+40): pack_into('<Q', raw, offset, 256)
    return bytes(raw), profile

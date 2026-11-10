"""Independent ELF64 little-endian test bytes, NEVER a loadable test request.

Literal layout follows ELF64 gABI: three nonoverlapping PT_LOAD ranges; one
strong unversioned initializer; one local one-byte helper; a two-entry method
array (one method plus zero terminator); two RELATIVE pointer relocations.
Both hash tables and versym are present so negative tests cannot silently skip.
The bytes MUST ONLY reach the pure parser. They are not authenticated code and
must never be passed to dlopen/create_dynamic or written to a production image.
"""
from struct import pack_into

INITIALIZER = 'PyInit__h25_field_service_v1'
SIZE = 0x3780
SHOFF = 0x3400
SECTIONS = (
    ('', 0, 0, 0, 0, 0, 0, 0, 0, 0),
    ('.rodata', 1, 2, 0x500, 0x500, 9, 0, 0, 1, 0),
    ('.hash', 5, 2, 0x600, 0x600, 20, 4, 0, 8, 4),
    ('.gnu.hash', 0x6FFFFFF6, 2, 0x620, 0x620, 32, 4, 0, 8, 0),
    ('.dynsym', 11, 2, 0x700, 0x700, 48, 5, 1, 8, 24),
    ('.dynstr', 3, 2, 0x800, 0x800, 30, 0, 0, 1, 0),
    ('.gnu.version', 0x6FFFFFFF, 2, 0x900, 0x900, 4, 4, 0, 2, 2),
    ('.rela.dyn', 4, 2, 0xA00, 0xA00, 48, 4, 9, 8, 24),
    ('.text', 1, 6, 0x1000, 0x1000, 32, 0, 0, 16, 0),
    ('.data', 1, 3, 0x2000, 0x2000, 64, 0, 0, 8, 0),
    ('.dynamic', 6, 3, 0x2100, 0x2100, 192, 5, 0, 8, 16),
    ('.strtab', 3, 0, 0, 0x3200, 0, 0, 0, 1, 0),
    ('.symtab', 2, 0, 0, 0x3300, 96, 11, 3, 8, 24),
    ('.shstrtab', 3, 0, 0, 0x3000, 0, 0, 0, 1, 0))


def make_fixture():
    raw = bytearray(SIZE)
    raw[:16] = b'\x7fELF\x02\x01\x01\x00' + b'\x00' * 8
    pack_into('<HHIQQQIHHHHHH', raw, 16, 3, 62, 1, 0, 64, SHOFF, 0, 64, 56, 6, 64, 14, 13)
    programs = ((1, 4, 0, 0, 0, 0xB00, 0xB00, 4096),
                (1, 5, 0x1000, 0x1000, 0x1000, 32, 32, 4096),
                (1, 6, 0x2000, 0x2000, 0x2000, 0x1000, 0x1000, 4096),
                (2, 6, 0x2100, 0x2100, 0x2100, 192, 192, 8),
                (0x6474E551, 6, 0, 0, 0, 0, 0, 16),
                (0x6474E552, 4, 0x2000, 0x2000, 0x2000, 0x1000, 0x1000, 1))
    for index, values in enumerate(programs):
        pack_into('<IIQQQQQQ', raw, 64 + 56 * index, *values)
    raw[0x500:0x509] = b'field_id\x00'
    pack_into('<IIIII', raw, 0x600, 1, 2, 1, 0, 0)
    # GNU ELF hash fixture encoder, independent of the candidate parser.
    h = 5381
    for char in INITIALIZER.encode('ascii'):
        h = (33 * h + char) & 0xFFFFFFFF
    bloom = (1 << (h % 64)) | (1 << ((h >> 5) % 64))
    pack_into('<IIIIQII', raw, 0x620, 1, 1, 1, 5, bloom, 1, h | 1)
    dynstr = b'\x00' + INITIALIZER.encode('ascii') + b'\x00'
    raw[0x800:0x800 + len(dynstr)] = dynstr
    pack_into('<IBBHQQ', raw, 0x718, 1, 0x12, 0, 8, 0x1000, 1)
    pack_into('<HH', raw, 0x900, 0, 1)
    pack_into('<QQq', raw, 0xA00, 0x2000, 8, 0x500)
    pack_into('<QQq', raw, 0xA18, 0x2008, 8, 0x1010)
    raw[0x1000] = raw[0x1010] = 0xC3
    pack_into('<I', raw, 0x2010, 1)
    dynamic = ((5, 0x800), (6, 0x700), (10, len(dynstr)), (11, 24), (4, 0x600),
               (0x6FFFFEF5, 0x620), (0x6FFFFFF0, 0x900), (7, 0xA00),
               (8, 48), (9, 24), (0x6FFFFFF9, 2), (0, 0))
    for index, values in enumerate(dynamic):
        pack_into('<qQ', raw, 0x2100 + 16 * index, *values)
    strings = b'\x00h25_fixture_target\x00h25_fixture_methods\x00' + INITIALIZER.encode('ascii') + b'\x00'
    raw[0x3200:0x3200 + len(strings)] = strings
    pack_into('<IBBHQQ', raw, 0x3318, 1, 0x02, 0, 8, 0x1010, 1)
    pack_into('<IBBHQQ', raw, 0x3330, 20, 0x01, 0, 9, 0x2000, 64)
    pack_into('<IBBHQQ', raw, 0x3348, 40, 0x12, 0, 8, 0x1000, 1)
    shstrings = b'\x00'
    offsets = {'': 0}
    for section in SECTIONS[1:]:
        offsets[section[0]] = len(shstrings)
        shstrings += section[0].encode('ascii') + b'\x00'
    raw[0x3000:0x3000 + len(shstrings)] = shstrings
    for index, section in enumerate(SECTIONS):
        name, typ, flags, addr, off, size, link, info, align, entsize = section
        if name == '.dynstr': size = len(dynstr)
        if name == '.strtab': size = len(strings)
        if name == '.shstrtab': size = len(shstrings)
        pack_into('<IIQQQQIIQQ', raw, SHOFF + 64 * index, offsets[name], typ, flags, addr, off, size, link, info, align, entsize)
    profile = {'schema': 'h25-static-elf-policy-v1', 'source_closure_sha256': '1' * 64,
               'compiler_closure_sha256': '2' * 64, 'link_profile_sha256': '3' * 64,
               'build_receipt_sha256': '4' * 64, 'expected_exports': (INITIALIZER,),
               'needed': (), 'required_local_functions': ('h25_fixture_target',),
               'required_local_objects': ('h25_fixture_methods',),
               'method_tables': ({'symbol': 'h25_fixture_methods',
                 'entries': (('field_id', 'h25_fixture_target', 1, None),)},),
               'pointer_slots': ()}
    return bytes(raw), profile


def make_import_fixture():
    """Second literal fixture: one strong + one unresolved weak function import.

    No imported target is executed. Extra GLOB_DAT writes are two data slots
    beyond the method table terminator. GNU hash excludes undefined symbols;
    SysV hash includes every dynamic symbol. Both are independently encoded.
    """
    initial, profile = make_fixture()
    raw = bytearray(initial)
    strong, weak = b'__h25_fixture_symbol', b'__h25_fixture_weak'
    dynstr = b'\0' + INITIALIZER.encode('ascii') + b'\0' + strong + b'\0' + weak + b'\0'
    strong_offset = 30
    weak_offset = strong_offset + len(strong) + 1
    raw[0x800:0x800 + len(dynstr)] = dynstr
    raw[0x700:0x760] = bytes(96)
    pack_into('<IBBHQQ', raw, 0x718, strong_offset, 0x12, 0, 0, 0, 0)
    pack_into('<IBBHQQ', raw, 0x730, weak_offset, 0x22, 0, 0, 0, 0)
    pack_into('<IBBHQQ', raw, 0x748, 1, 0x12, 0, 8, 0x1000, 1)
    pack_into('<IIIIIII', raw, 0x600, 1, 4, 1, 0, 2, 3, 0)
    pack_into('<I', raw, 0x624, 3)
    pack_into('<I', raw, 0x638, 3)
    pack_into('<HHHH', raw, 0x900, 0, 1, 1, 1)
    pack_into('<QQq', raw, 0xA30, 0x2040, (1 << 32) | 6, 0)
    pack_into('<QQq', raw, 0xA48, 0x2048, (2 << 32) | 6, 0)
    strings = b'\0h25_fixture_target\0h25_fixture_methods\0' + INITIALIZER.encode('ascii') + b'\0'
    full_strong = len(strings)
    strings += strong + b'\0'
    full_weak = len(strings)
    strings += weak + b'\0'
    raw[0x3200:0x3200 + len(strings)] = strings
    raw[0x3348:0x3390] = bytes(72)
    pack_into('<IBBHQQ', raw, 0x3348, full_strong, 0x12, 0, 0, 0, 0)
    pack_into('<IBBHQQ', raw, 0x3360, full_weak, 0x22, 0, 0, 0, 0)
    pack_into('<IBBHQQ', raw, 0x3378, 40, 0x12, 0, 8, 0x1000, 1)
    for index, size in ((2, 28), (4, 96), (5, len(dynstr)), (6, 8),
                        (7, 96), (9, 80), (11, len(strings)), (12, 144)):
        pack_into('<Q', raw, SHOFF + 64 * index + 32, size)
    pack_into('<Q', raw, 0x2128, len(dynstr))
    pack_into('<Q', raw, 0x2188, 96)
    return bytes(raw), profile

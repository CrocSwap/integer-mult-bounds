"""Strict data-only ELF profiles for nine source-fixed harmless fixture roles.

This is not the production service parser. It does not import/load an ELF,
execute constructors or code, learn golden offsets, or issue an authority token.
Actual source, compiler, process, startup and copy authority remain external.
"""
import hashlib
import struct
import json

SOURCE_REVIEW = None
RUNTIME_ADMISSION = None
FUNDING = None
EXECUTION_APPROVAL = None
MAX_FILE = 8388608
MAX_LOAD_BYTES = 16777216
U64 = (1 << 64) - 1
_SCHEMA = 'h25-history-fixture-elf-profile-v2'
_PAGE_SIZE = 4096  # Separate actual loader/page/runtime admission remains required.
_ROLES = {
    '09-procfd-alias': ('history_alias_v1.c', 'h25_history_alias_v1', None, (), None, None),
    '09-soname-leaf': ('history_leaf_v1.c', 'h25_history_value_v1', 'libh25_history_leaf_v1.so', (), None, None),
    '09-soname-middle': ('history_middle_v1.c', 'h25_history_middle_v1', 'libh25_history_middle_v1.so', ('libh25_history_leaf_v1.so',), '$ORIGIN', 'h25_history_value_v1'),
    '10-global-definition': ('history_global_v1.c', 'h25_history_value_v1', None, (), None, None),
    '10-global-leaf': ('history_leaf_v1.c', 'h25_history_value_v1', 'libh25_history_leaf_v1.so', (), None, None),
    '10-global-middle': ('history_middle_v1.c', 'h25_history_middle_v1', 'libh25_history_middle_v1.so', ('libh25_history_leaf_v1.so',), '$ORIGIN', 'h25_history_value_v1'),
    '11-dependency-leaf': ('history_leaf_v1.c', 'h25_history_value_v1', 'libh25_history_leaf_v1.so', (), None, None),
    '11-dependency-middle': ('history_middle_v1.c', 'h25_history_middle_v1', 'libh25_history_middle_v1.so', ('libh25_history_leaf_v1.so',), '$ORIGIN', 'h25_history_value_v1'),
    '11-dependency-root': ('history_root_v1.c', 'h25_history_root_v1', 'libh25_history_root_v1.so', ('libh25_history_middle_v1.so',), '$ORIGIN', 'h25_history_middle_v1'),
}
# Section types, exact flags, entry width (0 means not a fixed-entry table).
_SECTIONS = {
    '.dynstr': (3, 2, 0), '.dynsym': (11, 2, 24), '.gnu.hash': (0x6ffffff6, 2, 0),
    '.text': (1, 6, 0), '.dynamic': (6, 3, 16), '.got': (1, 3, 8),
    '.got.plt': (1, 3, 8), '.plt': (1, 6, 16), '.plt.got': (1, 6, 8),
    '.plt.sec': (1, 6, 16), '.rela.plt': (4, 66, 24), '.rela.dyn': (4, 2, 24),
    '.eh_frame': (1, 2, 0), '.eh_frame_hdr': (1, 2, 0),
    '.symtab': (2, 0, 24), '.strtab': (3, 0, 0), '.shstrtab': (3, 0, 0),
    '.comment': (1, 48, 1), '.data': (1, 3, 0), '.bss': (8, 3, 0),
}
_DYNAMIC_ALLOWED = {0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 14, 20, 23, 24, 29, 30,
                    0x6ffffef5, 0x6ffffffb}


class FixtureELFError(ValueError):
    """Finite source-fixed data rejection, never a native/runtime result."""


def _need(condition, reason):
    if condition is not True:
        raise FixtureELFError(reason)


def _end(start, count):
    _need(type(start) is int and type(count) is int and
          0 <= start <= U64 and 0 <= count <= U64 - start, 'range integer/overflow')
    return start + count


def _bounds(raw, start, count):
    end = _end(start, count)
    _need(end <= len(raw), 'range outside file')
    return end


def _range(raw, start, count):
    return raw[start:_bounds(raw, start, count)]


def _unpack(raw, fmt, offset):
    # Formats are literals supplied only by this source, never by the caller.
    count = struct.calcsize(fmt)
    _bounds(raw, offset, count)
    return struct.unpack_from(fmt, raw, offset)


def _power(value):
    return type(value) is int and value > 0 and value & (value - 1) == 0


def _disjoint(ranges, reason):
    ordered = sorted((a, b) for a, b in ranges if b > a)
    for previous, current in zip(ordered, ordered[1:]):
        _need(previous[1] <= current[0], reason)


def _text(raw, offset, limit=512):
    _need(type(offset) is int and 0 <= offset < len(raw), 'string offset')
    stop = raw.find(b'\0', offset, min(len(raw), offset + limit + 1))
    _need(stop >= offset, 'unterminated/bounded string')
    value = raw[offset:stop]
    _need(all(32 <= c < 127 for c in value), 'non-ASCII ELF name')
    return value.decode('ascii')


def _contains(segment, address, size):
    return segment['vaddr'] <= address and _end(address, size) <= _end(segment['vaddr'], segment['memsz'])


def _mapped(loads, address, size, writable=False, executable=False):
    matches = [p for p in loads if _contains(p, address, size)]
    _need(len(matches) == 1, 'virtual range absent/aliased')
    p = matches[0]
    _need(not writable or p['flags'] == 6, 'relocation destination not writable')
    _need(not executable or p['flags'] == 5, 'function outside executable LOAD')
    delta = address - p['vaddr']
    _need(_end(delta, size) <= p['filesz'], 'virtual range in BSS/unbacked tail')
    return p['offset'] + delta


def _effective_contains(relro, address, size):
    lo, hi = relro['effective']
    return lo <= address and _end(address, size) <= hi


def _header(raw):
    _need(type(raw) is bytes and 64 <= len(raw) <= MAX_FILE, 'bounded exact ELF bytes')
    values = _unpack(raw, '<16sHHIQQQIHHHHHH', 0)
    ident, typ, machine, version, entry, phoff, shoff, flags, ehsize, phentsize, phnum, shentsize, shnum, shstrndx = values
    _need(ident == b'\x7fELF\x02\x01\x01' + b'\0' * 9, 'ELF identification profile')
    _need((typ, machine, version, entry, flags, ehsize, phentsize, shentsize) ==
          (3, 62, 1, 0, 0, 64, 56, 64), 'ELF architecture/type/header/entry')
    _need(1 <= phnum <= 32 and 2 <= shnum <= 96 and 0 < shstrndx < shnum,
          'ELF table counts/extended numbering')
    _need(phoff >= 64 and phoff % 8 == 0 and shoff >= 64 and shoff % 8 == 0,
          'ELF table offsets/alignment')
    _bounds(raw, phoff, 56 * phnum)
    _bounds(raw, shoff, 64 * shnum)
    _disjoint(((0, 64), (phoff, phoff + phnum * 56), (shoff, shoff + shnum * 64)),
              'ELF header/table overlap')
    return {'phoff': phoff, 'phnum': phnum, 'shoff': shoff, 'shnum': shnum, 'shstrndx': shstrndx}


def _segments(raw, header):
    phdrs, by_type, loads = [], {}, []
    allowed = {1, 2, 6, 0x6474e550, 0x6474e551, 0x6474e552}
    for index in range(header['phnum']):
        typ, flags, offset, vaddr, paddr, filesz, memsz, align = _unpack(raw, '<IIQQQQQQ', header['phoff'] + index * 56)
        _need(typ in allowed, 'unsupported program header/implicit initializer')
        _need(paddr == vaddr and filesz <= memsz, 'segment physical address/size')
        _bounds(raw, offset, filesz)
        _end(vaddr, memsz)
        _need(align in (0, 1) or _power(align) and align <= 2097152, 'segment alignment')
        p = dict(type=typ, flags=flags, offset=offset, vaddr=vaddr, filesz=filesz, memsz=memsz, align=align)
        phdrs.append(p)
        by_type.setdefault(typ, []).append(p)
        if typ == 1:
            _need(flags in (4, 5, 6) and filesz == memsz and 0 < memsz <= MAX_FILE,
                  'LOAD flags/zero span/BSS')
            _need(4096 <= align <= 2097152 and vaddr % align == offset % align,
                  'LOAD page congruence/alignment')
            loads.append(p)
    _need(2 <= len(loads) <= 8 and sum(p['memsz'] for p in loads) <= MAX_LOAD_BYTES,
          'LOAD count/aggregate span')
    # Compare the source order itself before any normalized evidence is returned.
    _need(tuple(p['vaddr'] for p in loads) == tuple(sorted(p['vaddr'] for p in loads)),
          'PT_LOAD ordering')
    first = loads[0]
    _need(first['vaddr'] == first['offset'] == 0 and first['flags'] == 4 and
          first['filesz'] >= header['phoff'] + header['phnum'] * 56, 'header LOAD mapping')
    _need(min(p['vaddr'] for p in loads) == 0 and
          max(p['vaddr'] + p['memsz'] for p in loads) <= MAX_LOAD_BYTES, 'LOAD virtual envelope')
    _need(sum(p['flags'] == 5 for p in loads) == 1 and sum(p['flags'] == 6 for p in loads) == 1,
          'LOAD executable/writable uniqueness')
    _disjoint([(p['vaddr'], p['vaddr'] + p['memsz']) for p in loads], 'LOAD virtual overlap')
    _disjoint([(p['offset'], p['offset'] + p['filesz']) for p in loads], 'LOAD file overlap')
    _disjoint([(p['offset'], p['offset'] + p['filesz']) for p in loads] +
              [(header['shoff'], header['shoff'] + header['shnum'] * 64)],
              'section headers mapped inside LOAD')
    _disjoint([(p['vaddr'] & ~4095, (p['vaddr'] + p['memsz'] + 4095) & ~4095) for p in loads],
              'LOAD page alias/permission overlap')
    _need(_mapped(loads, 0, 64) == 0 and
          _mapped(loads, header['phoff'], header['phnum'] * 56) == header['phoff'],
          'ELF/PHDR not in original first LOAD')
    for typ in (2, 0x6474e551, 0x6474e552):
        _need(len(by_type.get(typ, [])) == 1, 'mandatory unique dynamic/stack/RELRO')
    for typ in (6, 0x6474e550):
        _need(len(by_type.get(typ, [])) <= 1, 'duplicate auxiliary program header')
    stack = by_type[0x6474e551][0]
    _need((stack['flags'], stack['offset'], stack['vaddr'], stack['filesz'], stack['memsz']) == (6, 0, 0, 0, 0),
          'executable/nonempty GNU stack')
    dynamic = by_type[2][0]
    _need(dynamic['flags'] == 6 and dynamic['filesz'] == dynamic['memsz'] and
          16 <= dynamic['filesz'] <= 1024 and dynamic['filesz'] % 16 == 0 and
          _mapped(loads, dynamic['vaddr'], dynamic['filesz'], writable=True) == dynamic['offset'],
          'PT_DYNAMIC file/memory range')
    relro = by_type[0x6474e552][0]
    _need(relro['flags'] == 4 and relro['filesz'] == relro['memsz'] and relro['memsz'] > 0 and
          _mapped(loads, relro['vaddr'], relro['memsz'], writable=True) == relro['offset'],
          'PT_GNU_RELRO file/memory range')
    # Pinned production rule348: glibc floors BOTH endpoints; no end rounding up.
    relro_end = _end(relro['vaddr'], relro['memsz'])
    relro['nominal'] = (relro['vaddr'], relro_end)
    relro['effective'] = (relro['vaddr'] // _PAGE_SIZE * _PAGE_SIZE,
                          relro_end // _PAGE_SIZE * _PAGE_SIZE)
    _need(relro['effective'][0] < relro['effective'][1], 'RELRO protects no complete pages')
    _need(_contains(relro, dynamic['vaddr'], dynamic['filesz']), 'dynamic outside RELRO')
    _need(_effective_contains(relro, dynamic['vaddr'], dynamic['filesz']),
          'dynamic outside effective RELRO')
    if by_type.get(6):
        p = by_type[6][0]
        _need((p['flags'], p['offset'], p['vaddr'], p['filesz'], p['memsz']) ==
              (4, header['phoff'], header['phoff'], header['phnum'] * 56, header['phnum'] * 56),
              'PT_PHDR mismatch')
    return phdrs, loads, dynamic, relro


def _sections(raw, header, loads, dynamic, relro, phdrs):
    rows = []
    for index in range(header['shnum']):
        values = _unpack(raw, '<IIQQQQIIQQ', header['shoff'] + index * 64)
        name, typ, flags, address, offset, size, link, info, align, entsize = values
        rows.append(dict(index=index, name_offset=name, type=typ, flags=flags, address=address,
                         offset=offset, size=size, link=link, info=info, align=align, entsize=entsize))
    _need(all(value == 0 for key, value in rows[0].items() if key != 'index'), 'section zero entry')
    names = rows[header['shstrndx']]
    _need(names['type'] == 3 and names['flags'] == 0 and 1 <= names['size'] <= 8192,
          'section-name string table profile')
    name_bytes = _range(raw, names['offset'], names['size'])
    _need(name_bytes[:1] == name_bytes[-1:] == b'\0', 'section string-table boundaries')
    sections, file_ranges = {}, []
    for s in rows[1:]:
        name = _text(name_bytes, s['name_offset'], 128)
        _need(name in _SECTIONS and name not in sections, 'unexpected/duplicate section')
        typ, flags, entsize = _SECTIONS[name]
        _need((s['type'], s['flags']) == (typ, flags), 'section type/flags')
        # GNU ld may use zero or8 as the descriptive GOT entry width.
        _need(s['entsize'] == entsize or name in ('.got', '.got.plt') and s['entsize'] == 0,
              'section entry width')
        _need(s['entsize'] == 0 or s['size'] % s['entsize'] == 0, 'section partial entry')
        _need(name not in ('.text', '.eh_frame') or s['size'] <= 65536, 'code/unwind section byte bound')
        _need(name not in ('.plt', '.plt.got', '.plt.sec', '.eh_frame_hdr', '.comment') or
              s['size'] <= 4096, 'auxiliary section byte bound')
        _need(s['align'] in (0, 1) or _power(s['align']) and s['align'] <= 4096,
              'section alignment')
        _need(s['align'] <= 1 or s['offset'] % s['align'] == 0 and
              (s['address'] == 0 or s['address'] % s['align'] == 0), 'section aligned range')
        _need(s['link'] < header['shnum'], 'section link index')
        if name in ('.data', '.bss'):
            _need(s['size'] == 0, 'fixture source has no ordinary data/BSS')
        if s['type'] != 8:
            _bounds(raw, s['offset'], s['size'])
            if s['size']:
                file_ranges.append((s['offset'], s['offset'] + s['size']))
        if s['flags'] & 2 and s['size']:
            _need(_mapped(loads, s['address'], s['size'], bool(s['flags'] & 1), bool(s['flags'] & 4)) == s['offset'],
                  'allocated section virtual/file alias')
            expected_flags = 6 if s['flags'] & 1 else 5 if s['flags'] & 4 else 4
            _need(any(p['flags'] == expected_flags and _contains(p, s['address'], s['size']) for p in loads),
                  'allocated section/LOAD permission disagreement')
            if s['flags'] & 1:
                _need(_contains(relro, s['address'], s['size']), 'writable fixture section outside RELRO')
                _need(_effective_contains(relro, s['address'], s['size']),
                      'writable fixture section outside effective RELRO')
        elif not s['flags'] & 2:
            _need(s['address'] == 0, 'nonallocated section virtual address')
            if s['size']:
                _disjoint([(p['offset'], p['offset'] + p['filesz']) for p in loads] +
                          [(s['offset'], s['offset'] + s['size'])], 'nonallocated section inside LOAD')
        s['name'] = name
        sections[name] = s
    _disjoint(file_ranges + [(0, 64), (header['phoff'], header['phoff'] + header['phnum'] * 56),
                            (header['shoff'], header['shoff'] + header['shnum'] * 64)],
              'section/header/table range overlap')
    _need(all(name in sections for name in ('.dynstr', '.dynsym', '.gnu.hash', '.text', '.dynamic',
                                           '.symtab', '.strtab', '.shstrtab')), 'mandatory section missing')
    _need(sections['.shstrtab']['index'] == header['shstrndx'], 'section-name index/name mismatch')
    dyn = sections['.dynamic']
    _need((dyn['address'], dyn['offset'], dyn['size']) ==
          (dynamic['vaddr'], dynamic['offset'], dynamic['filesz']) and
          dyn['link'] == sections['.dynstr']['index'] and dyn['info'] == 0,
          'dynamic section/segment/string linkage')
    for name in ('.dynstr', '.strtab', '.shstrtab'):
        s = sections[name]
        _need(1 <= s['size'] <= 65536, 'string table byte bound')
        table = _range(raw, s['offset'], s['size'])
        _need(1 <= len(table) <= 65536 and table[:1] == table[-1:] == b'\0' and
              s['link'] == 0 and s['info'] == 0, 'string table extent/linkage')
    for name in ('.text', '.plt', '.plt.got', '.plt.sec', '.got', '.got.plt', '.eh_frame',
                 '.eh_frame_hdr', '.comment', '.data', '.bss'):
        if name in sections:
            _need(sections[name]['link'] == 0 and sections[name]['info'] == 0,
                  'ordinary section unexpected linkage')
    eh = [s for s in phdrs if s['type'] == 0x6474e550]
    _need(bool(eh) == ('.eh_frame_hdr' in sections), 'GNU_EH_FRAME segment/section presence')
    if eh:
        s = sections['.eh_frame_hdr']; e = eh[0]
        _need((e['flags'], e['offset'], e['vaddr'], e['filesz'], e['memsz']) ==
              (4, s['offset'], s['address'], s['size'], s['size']) and '.eh_frame' in sections,
              'GNU_EH_FRAME range')
    _need(sections['.text']['size'] > 0, 'empty fixture text')
    return rows, sections


def _dynamic(raw, sections, role):
    s = sections['.dynamic']
    tags, terminated = {}, False
    for offset in range(s['offset'], s['offset'] + s['size'], 16):
        tag, value = _unpack(raw, '<qQ', offset)
        _need(tag in _DYNAMIC_ALLOWED, 'forbidden/unsupported dynamic tag')
        if terminated:
            _need((tag, value) == (0, 0), 'nonzero dynamic tail after NULL')
            continue
        if tag == 0:
            _need(value == 0, 'dynamic NULL value')
            terminated = True
        else:
            _need(tag == 1 or tag not in tags, 'duplicate dynamic tag')
            tags.setdefault(tag, []).append(value)
    _need(terminated, 'dynamic NULL terminator absent')
    _need(all(tag in tags for tag in (5, 6, 10, 11, 0x6ffffef5)), 'mandatory dynamic tables')
    one = {tag: values[0] for tag, values in tags.items() if tag != 1}
    _need(one[5] == sections['.dynstr']['address'] and one[10] == sections['.dynstr']['size'] and
          one[6] == sections['.dynsym']['address'] and one[11] == 24 and
          one[0x6ffffef5] == sections['.gnu.hash']['address'], 'dynamic section pointers/widths')
    _need(one.get(30, 0) in (0, 8) and one.get(0x6ffffffb, 0) in (0, 1) and
          (one.get(30) == 8 or one.get(0x6ffffffb) == 1 or 24 in one) and
          (24 not in one or one[24] == 0), 'exact NOW-only dynamic flags')
    strings = _range(raw, sections['.dynstr']['offset'], sections['.dynstr']['size'])
    soname = _text(strings, one[14]) if 14 in one else None
    needed = tuple(_text(strings, value) for value in tags.get(1, []))
    runpath = _text(strings, one[29]) if 29 in one else None
    _need((soname, needed, runpath) == (role[2], role[3], role[4]), 'source-fixed SONAME/NEEDED/RUNPATH')
    return one, strings, soname, needed, runpath


def _symbols(raw, rows, sections, loads, strings, role):
    dyn = sections['.dynsym']
    _need(dyn['size'] % 24 == 0 and 2 <= dyn['size'] // 24 <= 16 and
          dyn['link'] == sections['.dynstr']['index'] and dyn['info'] == 1, 'dynamic symbol table bounds/linkage')
    symbols, seen = [], set()
    for index in range(dyn['size'] // 24):
        nameoff, info, other, shndx, value, size = _unpack(raw, '<IBBHQQ', dyn['offset'] + index * 24)
        if index == 0:
            _need((nameoff, info, other, shndx, value, size) == (0, 0, 0, 0, 0, 0), 'dynamic symbol zero')
            symbols.append(dict(name='', binding=0, type=0, section=0, value=0, size=0))
            continue
        name = _text(strings, nameoff)
        _need(name and name not in seen and info >> 4 == 1 and other == 0,
              'dynamic symbol duplicate/binding/visibility')
        seen.add(name)
        typ = info & 15
        if shndx == 0:
            _need(name == role[5] and typ in (0, 2) and value == size == 0,
                  'unexpected/weak/versioned fixture import')
        else:
            _need(name == role[1] and typ == 2 and 0 < shndx < len(rows) and
                  rows[shndx]['name'] == '.text' and 0 < size <= 65536,
                  'unexpected export/IFUNC/section/type/size')
            s = rows[shndx]
            _need(s['address'] <= value and _end(value, size) <= s['address'] + s['size'],
                  'export beyond defining section')
            _mapped(loads, value, size, executable=True)
        symbols.append(dict(name=name, binding=1, type=typ, section=shndx, value=value, size=size))
    _need(len(symbols) == (3 if role[5] is not None else 2) and
          sum(s['section'] != 0 for s in symbols) == 1 and
          {s['name'] for s in symbols[1:]} == {name for name in (role[1], role[5]) if name is not None},
          'exact fixture import/export set')
    full = sections['.symtab']; string_section = sections['.strtab']
    _need(full['size'] % 24 == 0 and 2 <= full['size'] // 24 <= 128 and
          full['link'] == string_section['index'] and 1 <= full['info'] <= full['size'] // 24,
          'full symbol table bounds/linkage')
    names = _range(raw, string_section['offset'], string_section['size'])
    full_globals, local_names = [], set()
    for index in range(full['size'] // 24):
        noff, info, other, shndx, value, size = _unpack(raw, '<IBBHQQ', full['offset'] + index * 24)
        if index == 0:
            _need((noff, info, other, shndx, value, size) == (0, 0, 0, 0, 0, 0), 'full symbol zero')
            continue
        name, binding, typ = _text(names, noff), info >> 4, info & 15
        _need(other == 0 and binding in (0, 1) and (binding == 0) == (index < full['info']),
              'full symbol visibility/local partition')
        if binding == 1:
            full_globals.append(dict(name=name, binding=binding, type=typ, section=shndx, value=value, size=size))
            continue
        if typ == 4:
            _need(name == role[0] and shndx == 0xfff1 and value == size == 0 and name not in local_names,
                  'source file symbol')
        elif typ == 3:
            _need(name == '' and 0 < shndx < len(rows) and value == rows[shndx]['address'] and size == 0,
                  'section symbol range')
        else:
            expected = {'_DYNAMIC': (1, '.dynamic'), '_GLOBAL_OFFSET_TABLE_': (1, None),
                        '__GNU_EH_FRAME_HDR': (0, '.eh_frame_hdr')}
            _need(name in expected and name not in local_names and 0 < shndx < len(rows) and size == 0,
                  'unexpected local code/data symbol')
            etype, section_name = expected[name]
            _need(typ == etype and
                  (rows[shndx]['name'] == section_name if section_name is not None else
                   rows[shndx]['name'] in ('.got', '.got.plt')) and value == rows[shndx]['address'],
                  'linker infrastructure symbol range')
        if name:
            local_names.add(name)
    _need(sorted(full_globals, key=lambda s: s['name']) == sorted(symbols[1:], key=lambda s: s['name']),
          'dynamic/full symbol definitions disagree')
    return symbols


def _gnu_hash_value(name):
    value = 5381
    for byte in name.encode('ascii'):
        value = ((value << 5) + value + byte) & 0xffffffff
    return value


def _gnu_hash(raw, sections, symbols):
    s = sections['.gnu.hash']
    _need(s['link'] == sections['.dynsym']['index'] and s['info'] == 0 and 28 <= s['size'] <= 272,
          'GNU hash section linkage/range')
    data = _range(raw, s['offset'], s['size'])
    nbucket, first, nword, shift = _unpack(data, '<IIII', 0)
    _need(1 <= nbucket <= 16 and 1 <= nword <= 16 and _power(nword) and 0 < shift < 32 and
          1 <= first < len(symbols), 'GNU hash parameters')
    count = len(symbols) - first
    _need(len(data) == 16 + nword * 8 + nbucket * 4 + count * 4,
          'GNU hash exact extent')
    _need(all(s['section'] == 0 for s in symbols[1:first]) and
          all(s['section'] != 0 for s in symbols[first:]), 'GNU hash symbol partition')
    words = tuple(_unpack(data, '<Q', 16 + i * 8)[0] for i in range(nword))
    bucket_offset = 16 + nword * 8
    buckets = tuple(_unpack(data, '<I', bucket_offset + i * 4)[0] for i in range(nbucket))
    chain_offset = bucket_offset + nbucket * 4
    chains = tuple(_unpack(data, '<I', chain_offset + i * 4)[0] for i in range(count))
    expected_words = [0] * nword
    reached = set()
    for bucket_index, start in enumerate(buckets):
        if start == 0:
            continue
        _need(first <= start < len(symbols), 'GNU hash bucket index')
        index = start
        while True:
            _need(index < len(symbols) and index not in reached, 'GNU hash chain overflow/alias')
            reached.add(index)
            hv = _gnu_hash_value(symbols[index]['name'])
            _need(hv % nbucket == bucket_index and chains[index - first] & 0xfffffffe == hv & 0xfffffffe,
                  'GNU hash bucket/chain value')
            word = (hv // 64) % nword
            expected_words[word] |= (1 << (hv % 64)) | (1 << ((hv >> shift) % 64))
            if chains[index - first] & 1:
                break
            index += 1
    _need(reached == set(range(first, len(symbols))) and words == tuple(expected_words),
          'GNU hash reachability/bloom mismatch')


def _relocations(raw, sections, loads, relro, tags, symbols, role):
    tables = []
    regular = 7 in tags or 8 in tags
    plt = any(tag in tags for tag in (2, 20, 23))
    if regular:
        _need(all(tag in tags for tag in (7, 8, 9)) and tags[9] == 24 and '.rela.dyn' in sections,
              'regular RELA tag triple')
        tables.append(('.rela.dyn', tags[7], tags[8], 6))
    else:
        _need(7 not in tags and 8 not in tags and (9 not in tags or plt and tags[9] == 24),
              'orphan regular RELA metadata')
        _need('.rela.dyn' not in sections, 'unreferenced regular relocation section')
    if plt:
        _need(all(tag in tags for tag in (2, 3, 20, 23)) and tags[20] == 7 and '.rela.plt' in sections,
              'PLT RELA tag closure')
        tables.append(('.rela.plt', tags[23], tags[2], 7))
        _need('.plt' in sections and sections['.plt']['size'] > 0, 'PLT relocation without PLT code')
    else:
        _need(all(tag not in tags for tag in (2, 3, 20, 23)) and '.rela.plt' not in sections,
              'orphan PLT metadata')
        _need(all(name not in sections for name in ('.plt', '.plt.got', '.plt.sec')),
              'unrequested PLT code')
    relocations, destinations = [], []
    got_sections = [sections[name] for name in ('.got', '.got.plt') if name in sections]
    _need(len(got_sections) <= 1, 'ambiguous fixture GOT')
    if plt:
        _need(len(got_sections) == 1 and tags[3] == got_sections[0]['address'] and got_sections[0]['size'] >= 32,
              'PLTGOT exact range')
        got = got_sections[0]
        _need(_effective_contains(relro, got['address'], 24),
              'GOT reserved words outside effective RELRO')
        initial = _unpack(raw, '<QQQ', got['offset'])
        _need(initial == (sections['.dynamic']['address'], 0, 0), 'GOT reserved words')
    for name, address, size, kind in tables:
        s = sections[name]
        _need((s['address'], s['size']) == (address, size) and 0 < size <= 16 * 24 and size % 24 == 0 and
              s['link'] == sections['.dynsym']['index'], 'relocation section extent/symbol linkage')
        if name == '.rela.plt':
            _need(len(got_sections) == 1 and s['info'] == got_sections[0]['index'], 'PLT relocation destination linkage')
        else:
            _need(s['info'] == 0, 'regular relocation info')
        for offset in range(s['offset'], s['offset'] + s['size'], 24):
            destination, info, addend = _unpack(raw, '<QQq', offset)
            symbol_index, actual_kind = info >> 32, info & 0xffffffff
            _need(actual_kind == kind and addend == 0 and 0 < symbol_index < len(symbols),
                  'unsupported relocation type/addend/symbol')
            symbol = symbols[symbol_index]
            _need(role[5] is not None and symbol['section'] == 0 and symbol['name'] == role[5],
                  'relocation not exact external fixture function')
            _need(destination % 8 == 0 and _contains(relro, destination, 8), 'relocation alignment/RELRO')
            _need(_effective_contains(relro, destination, 8), 'relocation outside effective RELRO')
            file_offset = _mapped(loads, destination, 8, writable=True)
            matches = [got for got in got_sections if got['address'] <= destination and
                       destination + 8 <= got['address'] + got['size']]
            _need(len(matches) == 1, 'relocation outside exact GOT')
            if plt:
                _need(destination >= matches[0]['address'] + 24, 'relocation aliases GOT reserved words')
            initial = _unpack(raw, '<Q', file_offset)[0]
            if kind == 6:
                _need(initial == 0, 'GLOB_DAT initial value')
            elif initial != 0:
                _mapped(loads, initial, 1, executable=True)
            destinations.append((destination, destination + 8))
            relocations.append((destination, kind, symbol['name'], addend))
    _disjoint(destinations, 'relocation destination alias')
    _need(len(relocations) == (1 if role[5] is not None else 0), 'exact external relocation count')
    if role[5] is None:
        _need(not got_sections, 'unexpected fixture GOT/data')
    else:
        _need(len(got_sections) == 1 and got_sections[0]['size'] == (32 if plt else 8),
              'extra writable GOT cells')
    return tuple(relocations)


def inspect_fixture(role, image):
    """Parse exact immutable bytes into raw unadmitted fixture-profile DATA.

    Source semantics are not inferred from arbitrary code bytes. The authenticated
    compiler/command/source premise remains separate even after every check here.
    No serializable return value is an admission or copy/claim capability.
    """
    _need(type(role) is str and role in _ROLES, 'unknown exact fixture role')
    expected = _ROLES[role]
    header = _header(image)
    phdrs, loads, dynamic, relro = _segments(image, header)
    rows, sections = _sections(image, header, loads, dynamic, relro, phdrs)
    tags, strings, soname, needed, runpath = _dynamic(image, sections, expected)
    symbols = _symbols(image, rows, sections, loads, strings, expected)
    _gnu_hash(image, sections, symbols)
    relocs = _relocations(image, sections, loads, relro, tags, symbols, expected)
    export = next(s for s in symbols if s['section'] != 0)
    imports = tuple((s['name'], s['type'], s['binding']) for s in symbols[1:] if s['section'] == 0)
    return {'schema': _SCHEMA, 'status': 'RAW_STATIC_PROFILE_UNADMITTED', 'role': role,
            'sha256': hashlib.sha256(image).hexdigest(), 'bytes': len(image),
            'elf_class': 64, 'endianness': 'little', 'elf_type': 3, 'machine': 62,
            'entry': 0, 'soname': soname, 'needed': needed, 'runpath': runpath,
            'exports': ((export['name'], export['value'], export['size'], 2, 1, 0),),
            'imports': imports, 'relocations': relocs,
            'loads': tuple((p['offset'], p['vaddr'], p['filesz'], p['memsz'], p['flags'], p['align'])
                           for p in loads),
            'sections': tuple((s['name'], s['type'], s['flags'], s['offset'], s['address'], s['size'])
                              for s in rows[1:]),
            'relro': (relro['vaddr'], relro['memsz']),
            'nominal_relro': relro['nominal'], 'effective_relro': relro['effective'],
            'page_profile': {'schema': 'h25-amd64-page-profile-v1', 'page_size': _PAGE_SIZE,
                             'runtime_admission': None},
            'dynamic_tags': tuple(sorted(tags)), 'implicit_initializers': (),
            'constructor_free_fixture_profile': True, 'source_semantics_proven_from_code': False,
            'compiler_source_execution_premise': None, 'actual_native_dependencies_admitted': None,
            'actual_runtime_admission': None, 'parent_authority': None}


_REVIEWED_PRODUCER_SHA256 = '675dfb8636a44424d06c4f7df448dc722c7bd7c8cf85b197d473af59f251ccaf'
_ORIGINAL_ROOT_SHA256 = 'f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0'
_ORIGINAL_HELPER_SHA256 = 'aa0a315110e031e19291970c9611fe5e0f91465fa20eaec51e81186099563f78'
_SOURCE_PINS = {'history_alias_v1.c': {'bytes': 166, 'mode': 292, 'sha256': 'a27c38d66a926642a7149edcbfa4f40a40854aca46273a9172e9b71d441faa00'}, 'history_global_v1.c': {'bytes': 168, 'mode': 292, 'sha256': '9220fbbf3c5b5a794c2261966c5229e87d24056c9aa6e52aecfce68658846b91'}, 'history_leaf_v1.c': {'bytes': 168, 'mode': 292, 'sha256': '87db5356c5c5ee8c409bde01d38fa783c3357e42b570892c5b7a9f6e1b827b5f'}, 'history_middle_v1.c': {'bytes': 224, 'mode': 292, 'sha256': '95117568eca200c245784a356b973e0214d586be3f9cc53e4412f7672785ef54'}, 'history_root_v1.c': {'bytes': 226, 'mode': 292, 'sha256': 'd29e0da2ef808b9970e8bf786169180fc46dc4cf3df5e1b75f96752629289d96'}}
_BUILD_ROLES = (('09-procfd-alias', '09-procfd', 'history_alias_v1.c', 'history-alias-object.so', None, None), ('09-soname-leaf', '09-soname', 'history_leaf_v1.c', 'leaf-history-object.so', 'libh25_history_leaf_v1.so', None), ('09-soname-middle', '09-soname', 'history_middle_v1.c', 'libh25_history_middle_v1.so', 'libh25_history_middle_v1.so', 'leaf-history-object.so'), ('10-global-definition', '10-global', 'history_global_v1.c', 'global-history-object.so', None, None), ('10-global-leaf', '10-global', 'history_leaf_v1.c', 'libh25_history_leaf_v1.so', 'libh25_history_leaf_v1.so', None), ('10-global-middle', '10-global', 'history_middle_v1.c', 'libh25_history_middle_v1.so', 'libh25_history_middle_v1.so', 'libh25_history_leaf_v1.so'), ('11-dependency-leaf', '11-dependency', 'history_leaf_v1.c', 'libh25_history_leaf_v1.so', 'libh25_history_leaf_v1.so', None), ('11-dependency-middle', '11-dependency', 'history_middle_v1.c', 'libh25_history_middle_v1.so', 'libh25_history_middle_v1.so', 'libh25_history_leaf_v1.so'), ('11-dependency-root', '11-dependency', 'history_root_v1.c', 'libh25_history_root_v1.so', 'libh25_history_root_v1.so', 'libh25_history_middle_v1.so'))
_BUILD_FLAGS = ('-nostdlib', '-nodefaultlibs', '-nostartfiles', '-shared', '-fPIC', '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fno-stack-protector', '-fno-builtin', '-Wl,-z,defs', '-Wl,-z,now', '-Wl,-z,relro', '-Wl,--build-id=none', '-Wl,--hash-style=gnu')
_IDENTITY_KEYS = ('device', 'inode', 'mode', 'links', 'uid', 'gid', 'size', 'mtime_ns', 'ctime_ns')
_BINDING_KEYS = ('mode', 'generation', 'launch_nonce', 'process_id', 'process_start_time',
                 'root_source_sha256', 'producer_source_sha256', 'producer_command_sha256',
                 'terminal_receipt_sha256', 'producer_output', 'stage_root',
                 'fixture_profile_admission_sha256')
_ROOT_COUNTERS = ('load_calls', 'native_creations', 'native_execs', 'activation_attempts',
                  'successful_bindings', 'deactivation_attempts', 'cleanup_failures',
                  'control_module_creations')


class FixtureReceiptError(ValueError):
    """Bounded data inconsistency; never an original process/native failure."""


def _rneed(condition, reason):
    if condition is not True:
        raise FixtureReceiptError(reason)


def _exact(value, keys):
    _rneed(type(value) is dict and len(value) <= 64, 'exact bounded receipt object')
    _rneed(all(type(k) is str and len(k) <= 128 for k in value), 'receipt key type')
    _rneed(set(value) == set(keys), 'exact receipt key set')


def _digest(value):
    _rneed(type(value) is str and len(value) == 64 and
           all(c in '0123456789abcdef' for c in value), 'exact lowercase digest')


def _path(value):
    _rneed(type(value) is str and 1 < len(value) <= 4096 and value.startswith('/') and
           all(32 <= ord(c) < 127 for c in value) and
           all(part not in ('', '.', '..') for part in value.split('/')[1:]), 'exact absolute path')


def _integer(value, lower=0, upper=U64):
    _rneed(type(value) is int and lower <= value <= upper, 'bounded exact receipt integer')


def _identity(value, private):
    _exact(value, _IDENTITY_KEYS)
    for key in _IDENTITY_KEYS:
        _integer(value[key])
    _rneed(value['mode'] & 0o170000 == 0o100000 and value['mode'] & 0o7000 == 0 and
           value['links'] >= 1 and (not private or value['links'] == 1),
           'regular file/private single-link identity')


def _file_row(value, path=True, private=False):
    _exact(value, ('path', 'sha256', 'bytes', 'mode', 'identity') if path else
           ('sha256', 'bytes', 'mode', 'identity'))
    if path:
        _path(value['path'])
    _digest(value['sha256'])
    _integer(value['bytes'], 1 if private else 0, 67108864)
    _integer(value['mode'], 0, 0o777)
    _identity(value['identity'], private)
    _rneed(value['identity']['size'] == value['bytes'] and
           value['identity']['mode'] & 0o777 == value['mode'], 'file row size/mode disagreement')


def _json_pairs(pairs):
    _rneed(len(pairs) <= 64, 'JSON object bound')
    result = {}
    for key, value in pairs:
        _rneed(type(key) is str and len(key) <= 128 and key not in result, 'duplicate/invalid JSON key')
        result[key] = value
    return result


def _json_number(text):
    raise FixtureReceiptError('floating/nonfinite JSON number forbidden')


def _json_integer(text):
    _rneed(len(text) <= 21, 'JSON integer lexical bound')
    value = int(text)
    _rneed(-(1 << 63) <= value <= U64, 'JSON integer magnitude')
    return value


def _json_bytes(raw):
    _rneed(type(raw) is bytes and 1 <= len(raw) <= 1048576 and
           all(byte in (9, 10, 13) or 32 <= byte < 127 for byte in raw), 'bounded ASCII receipt bytes')
    # Bound nesting before handing bytes to the fixed standard-library decoder.
    depth, quoted, escaped = 0, False, False
    for byte in raw:
        if quoted:
            if escaped:
                escaped = False
            elif byte == 92:
                escaped = True
            elif byte == 34:
                quoted = False
        elif byte == 34:
            quoted = True
        elif byte in (91, 123):
            depth += 1
            _rneed(depth <= 24, 'JSON nesting bound')
        elif byte in (93, 125):
            depth -= 1
            _rneed(depth >= 0, 'JSON unmatched closing delimiter')
    _rneed(not quoted and depth == 0, 'JSON unterminated nesting/string')
    try:
        value = json.loads(raw, object_pairs_hook=_json_pairs, parse_int=_json_integer,
                           parse_float=_json_number, parse_constant=_json_number)
    except json.JSONDecodeError as error:
        raise FixtureReceiptError('JSON receipt syntax') from error
    todo, nodes, text_bytes = [(value, 0)], 0, 0
    while todo:
        item, level = todo.pop()
        nodes += 1
        _rneed(nodes <= 8192 and level <= 24 and len(todo) <= 8192, 'receipt tree bound')
        kind = type(item)
        if kind is dict:
            todo.extend((v, level + 1) for v in item.values())
        elif kind is list:
            _rneed(len(item) <= 256, 'receipt sequence bound')
            todo.extend((v, level + 1) for v in item)
        elif kind is str:
            text_bytes += len(item)
            _rneed(len(item) <= 8192 and text_bytes <= 524288 and
                   all(32 <= ord(c) < 127 for c in item), 'receipt text bound/alphabet')
        else:
            _rneed(item is None or kind in (bool, int), 'receipt primitive type')
    return value


def _command(stage, output, row):
    role, scenario, source, target, soname, dependency = row
    source_path = stage + '/areas/field-native-history-fixtures-v1/' + source
    directory = output + '/images/' + scenario
    command = ['/usr/bin/x86_64-linux-gnu-gcc-13', *_BUILD_FLAGS, source_path]
    if soname is not None:
        command.append('-Wl,-soname,' + soname)
    if dependency is not None:
        command.extend(['-Wl,--no-as-needed', directory + '/' + dependency,
                        '-Wl,--enable-new-dtags', '-Wl,-rpath,$ORIGIN'])
    command.extend(['-o', directory + '/' + target])
    return command, source_path, directory + '/' + target


def compare_fixture_receipts(role, image, build_raw, producer_raw, expected_binding,
                             current_source_rows, current_binary_row):
    """Return unadmitted consistency DATA after the parent's actual completion.

    expected_binding must be derived by the fixed parent from its private live
    owned_root/terminal owner and admitted launch, not from child receipt fields.
    This pure function cannot prove an input dictionary came from that owner.
    Parent source/closure review must establish that origin before a one-shot
    capability is issued. Call before chmod/export, then retain the separate
    actual freeze/export/copy identities. No saved PASS is accepted or returned.
    """
    profile = inspect_fixture(role, image)
    _exact(expected_binding, _BINDING_KEYS)
    binding = expected_binding
    _rneed(type(binding['mode']) is str and binding['mode'] in ('normal', 'optimized'),
           'producer execution mode')
    _rneed(type(binding['generation']) is str and 1 <= len(binding['generation']) <= 96 and
           all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in binding['generation']),
           'predeclared producer generation')
    for name in ('launch_nonce', 'root_source_sha256', 'producer_source_sha256',
                 'producer_command_sha256', 'terminal_receipt_sha256', 'fixture_profile_admission_sha256'):
        _digest(binding[name])
    _rneed(binding['root_source_sha256'] == _ORIGINAL_ROOT_SHA256, 'original Root source lineage')
    _integer(binding['process_id'], 1, (1 << 31) - 1)
    _integer(binding['process_start_time'], 1)
    _path(binding['producer_output']); _path(binding['stage_root'])
    _rneed(binding['producer_output'] != binding['stage_root'] and
           not binding['producer_output'].startswith(binding['stage_root'] + '/'), 'output inside stage')
    _rneed(type(current_source_rows) is tuple and 7 <= len(current_source_rows) <= 512,
           'complete current source row collection')
    sources = {}
    for row in current_source_rows:
        _file_row(row)
        _rneed(row['path'] not in sources, 'duplicate source custody path')
        sources[row['path']] = row
    stage, output = binding['stage_root'], binding['producer_output']
    for name, pin in _SOURCE_PINS.items():
        path = stage + '/areas/field-native-history-fixtures-v1/' + name
        _rneed(path in sources, 'fixture C source absent from current custody')
        row = sources[path]
        _rneed(all(row[key] == pin[key] for key in ('sha256', 'bytes', 'mode')),
               'current fixture C source differs from frozen literal')
    producer_path = stage + '/integration/fixture_producer_v1.py'
    helper_path = stage + '/integration/cold_build_evidence.py'
    _rneed(producer_path in sources and sources[producer_path]['sha256'] == binding['producer_source_sha256'] and
           sources[producer_path]['mode'] == 0o444, 'configured producer current source differs')
    _rneed(helper_path in sources and sources[helper_path]['sha256'] == _ORIGINAL_HELPER_SHA256 and
           sources[helper_path]['mode'] == 0o444, 'original helper current source differs')
    _file_row(current_binary_row, private=True)
    build, producer = _json_bytes(build_raw), _json_bytes(producer_raw)
    _exact(build, ('schema', 'role', 'status', 'command', 'context', 'path', 'binary',
                   'original_helper_sha256', 'negative_only', 'loaded'))
    _exact(producer, ('schema', 'status', 'producer_role', 'binding', 'process_id', 'builds',
                      'helper_names', 'consumed_roles', 'root_before', 'root_after',
                      'negative_only', 'candidate_loads', 'parent_completion', 'domain_closed', 'elf_admission'))
    _rneed(producer['schema'] == 'h25-native-history-producer-v1' and
           producer['status'] == 'NINE_BUILDS_RAW_AND_SOURCE_CAPTURED' and
           producer['producer_role'] == 'history_fixtures_v1' and
           producer['negative_only'] is True and type(producer['candidate_loads']) is int and
           producer['candidate_loads'] == 0 and
           producer['parent_completion'] is producer['domain_closed'] is producer['elf_admission'] is None,
           'producer literal schema/status/native boundary')
    _exact(producer['binding'], ('mode', 'generation', 'launch_nonce'))
    _rneed(all(producer['binding'][key] == binding[key] for key in ('mode', 'generation', 'launch_nonce')) and
           type(producer['process_id']) is int and producer['process_id'] == binding['process_id'],
           'producer binding differs from actual owned process')
    _rneed(type(producer['helper_names']) is list and producer['helper_names'] == ['control'] * 9 and
           type(producer['consumed_roles']) is list and len(producer['consumed_roles']) == 9 and
           all(value is True for value in producer['consumed_roles']), 'producer exact helper/consumption census')
    for name in ('root_before', 'root_after'):
        _exact(producer[name], _ROOT_COUNTERS)
        _rneed(all(type(value) is int and value == 0 for value in producer[name].values()),
               'producer native lifecycle not zero')
    _rneed(type(producer['builds']) is list and len(producer['builds']) == 9, 'producer nine build rows')
    selected = None
    for definition, summary in zip(_BUILD_ROLES, producer['builds']):
        _exact(summary, ('role', 'path', 'build_receipt_sha256', 'output_sha256', 'output_bytes', 'elf_admission'))
        command, source_path, target = _command(stage, output, definition)
        _rneed(summary['role'] == definition[0] and summary['path'] == target and
               summary['elf_admission'] is None, 'producer role order/path/profile boundary')
        _digest(summary['build_receipt_sha256']); _digest(summary['output_sha256'])
        _integer(summary['output_bytes'], 64, MAX_FILE)
        if definition[0] == role:
            selected = summary, definition, command, source_path, target
    _rneed(selected is not None, 'selected fixture role absent')
    summary, definition, command, source_path, target = selected
    _rneed(build['schema'] == 'h25-native-history-build-v1' and build['role'] == role and
           build['status'] == 'RAW_BUILD_PENDING_PARENT_COMPLETION_AND_ELF' and
           build['negative_only'] is True and build['loaded'] is False and
           build['original_helper_sha256'] == _ORIGINAL_HELPER_SHA256 and build['command'] == command and
           build['path'] == current_binary_row['path'] == target,
           'actual build command/role/output contract')
    context = build['context']
    _exact(context, ('source', 'source_name', 'source_path', 'no_cached_binary', 'target',
                     'fixture_role', 'fixture_profile_admission_sha256', 'system_header_count', 'project_header_count'))
    _exact(context['source'], ('sha256', 'bytes', 'mode'))
    _rneed(context['source'] == _SOURCE_PINS[definition[2]] and context['source_name'] == definition[2] and
           context['source_path'] == source_path and context['target'] == target and
           context['fixture_role'] == role and context['no_cached_binary'] is True and
           context['fixture_profile_admission_sha256'] == binding['fixture_profile_admission_sha256'] and
           type(context['system_header_count']) is type(context['project_header_count']) is int and
           context['system_header_count'] == context['project_header_count'] == 0,
           'build source/header/profile context')
    _file_row(build['binary'], False, True)
    _rneed(all(current_binary_row[key] == build['binary'][key] for key in ('sha256', 'bytes', 'mode', 'identity')),
           'actual retained binary changed before freeze/export')
    _rneed(profile['sha256'] == current_binary_row['sha256'] == summary['output_sha256'] and
           profile['bytes'] == current_binary_row['bytes'] == summary['output_bytes'] and
           hashlib.sha256(build_raw).hexdigest() == summary['build_receipt_sha256'],
           'actual image/build receipt bytes differ')
    canonical = json.dumps(profile, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')
    return {'schema': 'h25-history-fixture-receipt-consistency-v2',
            'status': 'CONSISTENCY_ONLY_UNADMITTED', 'role': role, 'profile': profile,
            'profile_sha256': hashlib.sha256(canonical).hexdigest(),
            'build_receipt_sha256': hashlib.sha256(build_raw).hexdigest(),
            'producer_receipt_sha256': hashlib.sha256(producer_raw).hexdigest(),
            'process_id': binding['process_id'], 'process_start_time': binding['process_start_time'],
            'producer_command_sha256': binding['producer_command_sha256'],
            'terminal_receipt_sha256': binding['terminal_receipt_sha256'],
            'configured_producer_source_sha256': binding['producer_source_sha256'],
            'reviewed_unconfigured_producer_sha256': _REVIEWED_PRODUCER_SHA256,
            'configuration_inverse_admission': None,
            'actual_parent_owner_authenticated': None, 'original_helper_process_receipts_admitted': None,
            'frozen_export_copy_admission': None, 'native_startup_admission': None,
            'actual_runtime_admission': None, 'claim_authority': None}

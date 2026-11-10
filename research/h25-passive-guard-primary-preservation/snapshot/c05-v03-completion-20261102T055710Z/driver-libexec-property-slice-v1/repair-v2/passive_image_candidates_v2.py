"""SOURCE ONLY: bounded image/reference candidate discovery, never a proof.

No subprocess, disassembler, target execution, original-module import or image
copy. Main authenticates the entire nominated image before interpreting ELF.
Inspection returns candidate data ONLY; it validates no instruction boundary,
operand role, callee ABI, reachability, relocation effect or runtime frame.
"""
import hashlib
import json
import os
import stat
import struct
import sys

EXPECTED_PATH = '/usr/bin/x86_64-linux-gnu-gcc-13'
EXPECTED_SIZE = 1023032
EXPECTED_SHA = '1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26'
LITERAL = b'/usr/libexec/gcc/\0'
LITERAL_OFFSET = 702226
MAX_INPUT = 2097152
MAX_CANDIDATES = 8


class Stop(ValueError):
    pass


def need(value, reason):
    if not value:
        raise Stop(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def span(offset, size, length):
    need(type(offset) is int and type(size) is int and
         0 <= offset <= length and 0 <= size <= length - offset,
         'file span outside image')


def inspect(data, literal_offset=LITERAL_OFFSET):
    """Pure synthetic-test interface. Main supplies only fully pinned actual B."""
    need(type(data) is bytes and 64 <= len(data) <= MAX_INPUT, 'image byte bound')
    h = struct.unpack_from('<16sHHIQQQIHHHHHH', data, 0)
    ident, typ, machine, version, entry, phoff, shoff, flags, ehsize, phent, phnum, shent, shnum, shstr = h
    need(ident[:4] == b'\x7fELF' and ident[4:7] == b'\x02\x01\x01', 'unsupported ELF class/data/version')
    need(machine == 62 and version == 1 and typ in (2, 3), 'unsupported machine/type')
    need(ehsize == 64 and phent == 56 and 1 <= phnum <= 128 and phnum != 65535,
         'unsupported/extended program headers')
    span(phoff, phent * phnum, len(data))
    loads, dynamic = [], []
    for index in range(phnum):
        t, f, off, va, pa, filesz, memsz, align = struct.unpack_from('<IIQQQQQQ', data, phoff+index*56)
        if t not in (1, 2):
            continue
        span(off, filesz, len(data))
        need(filesz <= memsz and va + memsz <= 2**64, 'segment memory overflow')
        need(align in (0, 1) or (align & (align-1) == 0 and va % align == off % align),
             'segment alignment invalid')
        row = {'index': index, 'type': t, 'flags': f, 'offset': off,
               'vaddr': va, 'filesz': filesz, 'memsz': memsz}
        (loads if t == 1 else dynamic).append(row)
    need(loads, 'no PT_LOAD')
    def map_file(off, size):
        return [x for x in loads if x['offset'] <= off and off+size <= x['offset']+x['filesz']]
    def unique_va(off, size):
        rows = map_file(off, size)
        need(len(rows) == 1, 'ambiguous/unmapped file span')
        va = rows[0]['vaddr'] + off - rows[0]['offset']
        need(map_va(va, size) == off, 'file/virtual reverse mapping differs')
        return va
    def map_va(va, size):
        rows = [x for x in loads if x['vaddr'] <= va and va+size <= x['vaddr']+x['filesz']]
        need(len(rows) == 1, 'ambiguous/zero-fill/unmapped virtual span')
        row = rows[0]
        # Reject even partial competing memory mappings, including zero-fill.
        # A distinct file span mapping over any requested VA is not unique.
        need(not any(x is not row and max(va, x['vaddr']) <
                     min(va+size, x['vaddr']+x['memsz']) for x in loads),
             'overlapping virtual mapping')
        return row['offset'] + va - row['vaddr']
    if entry:
        map_va(entry, 1)
        entry_rows = [x for x in loads if x['vaddr'] <= entry < x['vaddr']+x['filesz']]
        need(len(entry_rows) == 1 and entry_rows[0]['flags'] & 1,
             'entry outside exact executable VA mapping')
    span(literal_offset, len(LITERAL), len(data))
    need(data[literal_offset:literal_offset+len(LITERAL)] == LITERAL, 'literal bytes differ')
    L = unique_va(literal_offset, len(LITERAL))
    # Section structures are corroboration only; names do not prove table kinds.
    sections = []
    if shoff:
        need(shent == 64 and 1 <= shnum <= 512 and shstr < shnum,
             'unsupported/extended section headers')
        span(shoff, shnum*64, len(data))
        for index in range(shnum):
            n, t, f, va, off, size, link, info, align, ent = struct.unpack_from('<IIQQQQIIQQ', data, shoff+64*index)
            if t != 8:
                span(off, size, len(data))
            if t in (2, 11):
                need(ent == 24 and size % 24 == 0 and link < shnum, 'invalid symbol table shape')
            if t in (4, 9, 19):
                expected = {4:24, 9:16, 19:8}[t]
                need(ent == expected and size % expected == 0, 'relocation section shape')
            sections.append({'index':index, 'type':t, 'flags':f, 'addr':va,
                             'offset':off, 'size':size, 'link':link, 'entsize':ent})
    else:
        need(shnum == 0, 'section count without table')
    # Actual dynamic table descriptors, not semantic relocation interpretation.
    tags = {}
    dynamic_tags_observed = []
    need(len(dynamic) <= 1, 'multiple PT_DYNAMIC')
    for d in dynamic:
        need(d['filesz'] % 16 == 0 and d['filesz'] <= 4096, 'dynamic table bound')
        ended = False
        for off in range(d['offset'], d['offset']+d['filesz'], 16):
            tag, value = struct.unpack_from('<qQ', data, off)
            if tag == 0:
                ended = True; break
            dynamic_tags_observed.append({'tag':tag,'value':value,'file_offset':off})
            if tag in (7,8,9,17,18,19,20,23,2,35,36,37):
                need(tag not in tags, 'duplicate relevant dynamic scalar tag')
                tags[tag] = value
        need(ended, 'DT_NULL absent within declared dynamic span')
    relocation_tables = []
    for name, address_tag, size_tag, ent_tag, width in (
            ('RELA',7,8,9,24), ('REL',17,18,19,16), ('RELR',36,35,37,8)):
        if address_tag in tags or size_tag in tags:
            need(all(t in tags for t in (address_tag,size_tag,ent_tag)), 'partial relocation descriptor')
            size = tags[size_tag]
            need(tags[ent_tag] == width and size % width == 0 and size <= 196608,
                 'relocation table bound/entry size')
            off = map_va(tags[address_tag],size)
            relocation_tables.append({'kind':name,'vaddr':tags[address_tag],
                'offset':off,'bytes':size,'sha256':sha(data[off:off+size])})
    if 23 in tags or 2 in tags:
        need(all(t in tags for t in (23,2,20)) and tags[20] in (7,17), 'unsupported JMPREL descriptor')
        width = 24 if tags[20] == 7 else 16
        size = tags[2]; need(size % width == 0 and size <= 196608,'JMPREL bound')
        off = map_va(tags[23],size)
        relocation_tables.append({'kind':'JMPREL','vaddr':tags[23],'offset':off,
            'bytes':size,'sha256':sha(data[off:off+size])})
    refs, overflow, seen = [], False, set()
    def add(kind, off, width, target):
        nonlocal overflow
        key = (kind,off)
        if key in seen:
            return
        seen.add(key)
        if len(refs) == MAX_CANDIDATES:
            overflow = True; return
        refs.append({'kind':kind,'file_offset':off,'link_pc_or_slot':unique_va(off,width),
                     'span_bytes':width,'raw_hex':data[off:off+width].hex(),
                     'candidate_target':target,'instruction_boundary_validated':False})
    # Raw pointer slots include possible tables/immediates: never typed as pointers.
    needle = struct.pack('<Q',L)
    for seg in loads:
        if seg['flags'] & 1:
            continue
        off = seg['offset']; end = off + seg['filesz']
        while True:
            off = data.find(needle,off,end)
            if off < 0:
                break
            add('RAW_LE64_LITERAL_ADDRESS',off,8,L); off += 1
            if overflow:
                break
    slots = [r['link_pc_or_slot'] for r in refs if r['kind']=='RAW_LE64_LITERAL_ADDRESS']
    for seg in loads:
        if overflow:
            break
        if not seg['flags'] & 1:
            continue
        start,end = seg['offset'],seg['offset']+seg['filesz']
        for off in range(start,end):
            if overflow:
                break
            pc = seg['vaddr'] + off-start
            b = data[off]
            # Candidate shapes only: preceding prefixes/interior boundaries UNKNOWN.
            if off+7 <= end and 0x48 <= b <= 0x4f and data[off+1] in (0x8d,0x8b):
                modrm = data[off+2]
                if modrm & 0xc7 == 0x05:
                    target = pc+7+struct.unpack_from('<i',data,off+3)[0]
                    if data[off+1] == 0x8d and target == L:
                        add('CANDIDATE_REXW_LEA_RIP_DISP32',off,7,L)
                    if data[off+1] == 0x8b and target in slots:
                        add('CANDIDATE_REXW_MOV_FROM_RIP_SLOT',off,7,target)
            if off+10 <= end and 0x48 <= b <= 0x4f and 0xb8 <= data[off+1] <= 0xbf:
                if struct.unpack_from('<Q',data,off+2)[0] == L:
                    add('CANDIDATE_REXW_MOV_IMM64',off,10,L)
            if off+5 <= end and 0xb8 <= b <= 0xbf and struct.unpack_from('<I',data,off+1)[0] == L:
                add('CANDIDATE_MOV_R32_IMM32_ZEROEXT',off,5,L)
            if off+7 <= end and 0x48 <= b <= 0x4f and data[off+1] == 0xc7 and data[off+2]&0xf8 == 0xc0:
                value = struct.unpack_from('<i',data,off+3)[0] % 2**64
                if value == L:
                    add('CANDIDATE_REXW_MOV_IMM32_SIGNEXT',off,7,L)
    return {'status':'STOP_CANDIDATE_CAP' if overflow else 'PARTIAL_LOCALISATION_DATA_ONLY',
            'ELF_type':typ,'machine':machine,'entry':entry,'load_bias':'0 under ET_EXEC loader premise' if typ==2 else 'symbolic beta',
            'literal_offset':literal_offset,'literal_link_address':L,'literal_bytes':LITERAL.hex(),
            'loads':loads,'sections':sections,'dynamic_tags_observed':dynamic_tags_observed,
            'relocation_table_descriptors':relocation_tables,
            'references':refs,'candidate_overflow':overflow,'reference_count_retained':len(refs),
            'relocation_effects_audited':False,'instruction_boundaries_validated':False,
            'source_role_qualified':False,'D_applicability_qualified':False,
            'certificate_feasible':False,'full_C05':False,'full_V03':False}


def main():
    fd = os.open(EXPECTED_PATH,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_size == EXPECTED_SIZE, 'wrong input size/type')
        chunks,total = [],0
        while True:
            block = os.read(fd,min(65536,MAX_INPUT+1-total))
            if not block:
                break
            total += len(block); need(total <= MAX_INPUT,'image cap')
            chunks.append(block)
        after = os.fstat(fd)
        need((before.st_dev,before.st_ino,before.st_mode,before.st_size,before.st_mtime_ns,before.st_ctime_ns) ==
             (after.st_dev,after.st_ino,after.st_mode,after.st_size,after.st_mtime_ns,after.st_ctime_ns), 'input descriptor changed')
        data = b''.join(chunks)
        need(len(data)==EXPECTED_SIZE and sha(data)==EXPECTED_SHA,'whole-image pin mismatch')
        result = inspect(data)
        result.update(image_sha256=EXPECTED_SHA,image_bytes=len(data),target_executed=False)
        raw = json.dumps(result,sort_keys=True).encode()+b'\n'
        need(len(raw)<=65536,'candidate report cap')
        sys.stdout.buffer.write(raw);sys.stdout.buffer.flush()
    finally:
        os.close(fd)


if __name__ == '__main__':
    try:
        main()
    except (Stop,OSError,ValueError,struct.error) as exc:
        print('STOP: '+type(exc).__name__+': '+str(exc),file=sys.stderr)
        raise SystemExit(2)

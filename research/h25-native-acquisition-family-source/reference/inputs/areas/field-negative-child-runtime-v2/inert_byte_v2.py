"""Independent ELF64 file-layout proof for one same-size unloaded comment byte.

This is deliberately separate from sealed_elf_profile_v2 and never loads ELF.
Only a nonallocated SHT_PROGBITS .comment payload outside every load segment,
ELF/program/section header, and every other section can supply the byte. No
append, truncate, section-header change, or assumed padding is permitted.
"""
import struct
from hashlib import sha256


def need(value, message):
    if value is not True:
        raise RuntimeError(message)


def derive(raw, expected_sha256):
    need(type(raw) is bytes and 64 <= len(raw) <= 8388608 and type(expected_sha256) is str and
         sha256(raw).hexdigest() == expected_sha256, 'inert exact original image/hash')
    need(raw[:16] == b'\x7fELF\x02\x01\x01\x00' + b'\x00'*8, 'inert ELF64 little-endian identity')
    kind,machine,version,entry,phoff,shoff,flags,ehsize,phsize,phnum,shsize,shnum,shstr = struct.unpack_from('<HHIQQQIHHHHHH',raw,16)
    need((kind,machine,version,entry,flags,ehsize,phsize,shsize) == (3,62,1,0,0,64,56,64) and
         1 <= phnum <= 16 and 1 <= shnum <= 128 and 0 < shstr < shnum and
         64 <= phoff and phoff+phnum*56 <= len(raw) and 64 <= shoff and shoff+shnum*64 <= len(raw),
         'inert complete ELF header layout')
    protected = [(0,64),(phoff,phoff+phnum*56),(shoff,shoff+shnum*64)]
    loads = []
    for index in range(phnum):
        ptype,pflags,offset,vaddr,paddr,filesz,memsz,align = struct.unpack_from('<IIQQQQQQ',raw,phoff+56*index)
        need(offset+filesz <= len(raw), 'inert program file range')
        if ptype == 1:
            need(filesz <= memsz, 'inert PT_LOAD size')
            loads.append((offset,offset+filesz))
    need(1 <= len(loads) <= 8,'inert PT_LOAD census')
    rows = tuple(struct.unpack_from('<IIQQQQIIQQ',raw,shoff+64*index) for index in range(shnum))
    strings = rows[shstr]
    need(strings[1] == 3 and strings[4]+strings[5] <= len(raw),'inert section string table')
    names = raw[strings[4]:strings[4]+strings[5]]
    comments = []
    for index,row in enumerate(rows):
        name,stype,sflags,address,offset,size,link,info,alignment,entsize = row
        need(0 <= name < len(names),'inert bounded section name')
        end = names.find(b'\x00',name)
        need(end >= name,'inert terminated section name')
        if stype != 8:
            need(offset+size <= len(raw),'inert section file range')
        if names[name:end] == b'.comment':
            comments.append((index,row))
    need(len(comments) == 1,'inert unique comment section')
    selected,row = comments[0]
    name,stype,sflags,address,offset,size,link,info,alignment,entsize = row
    need((stype,sflags,address,link,info,entsize) == (1,0,0,0,0,0) and alignment in (0,1) and 1 <= size <= 4096,
         'inert comment must be nonallocated passive bytes')
    interval = (offset,offset+size)
    protected.extend(loads)
    protected.extend((other[4],other[4]+other[5]) for index,other in enumerate(rows)
                     if index != selected and other[1] != 8 and other[5])
    need(all(interval[1] <= start or end <= interval[0] for start,end in protected),
         'inert comment overlaps loaded image or ELF metadata')
    payload = raw[offset:offset+size]
    candidates = tuple(index for index,value in enumerate(payload) if 65 <= value <= 90)
    need(bool(candidates),'inert comment needs existing uppercase ASCII byte')
    position = offset+candidates[0]
    original = raw[position:position+1]
    replacement = b'Y' if original == b'Z' else bytes((original[0]+1,))
    return {'schema':'h25-inert-comment-proof-v2','source_sha256':expected_sha256,'file_bytes':len(raw),
            'offset':position,'original_byte':original,'replacement_byte':replacement,
            'section_index':selected,'section_interval':interval,'pt_load_ranges':tuple(loads),
            'protected_ranges':tuple(protected),'size_delta':0,'writes':1}


def verify_changed(original, changed, proof):
    need(type(changed) is bytes and len(original) == len(changed) == proof['file_bytes'],
         'inert mutation changed file length')
    position = proof['offset']
    need(original[:position] == changed[:position] and original[position+1:] == changed[position+1:] and
         original[position:position+1] == proof['original_byte'] and
         changed[position:position+1] == proof['replacement_byte'], 'inert mutation is not exactly the proved byte')
    return None

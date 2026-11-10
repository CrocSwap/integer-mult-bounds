"""NEW literal synthetic ELF buffers only. No extractor-derived oracle or I/O."""
import struct

LITERAL = bytes.fromhex('2f7573722f6c6962657865632f6763632f00')
CODE = {
    'S01': '488d3d790000004889fec3',
    'S02': '48be8001400000000000c3',
    'S03': 'be80014000c3',
    'S04': '48b8488d3d7700000000c3',
    'S05': 'c3',
    'S06': '488d3d790000004889fe31f6c3',
    'X01': '48c7c680014000c3',
}


def segment(data, index, offset, address, filesz, memsz, flags, align):
    struct.pack_into('<IIQQQQQQ', data, 64 + index * 56,
                     1, flags, offset, address, 0, filesz, memsz, align)


def base(code=CODE['S01'], elf_type=2):
    data = bytearray(1024)
    struct.pack_into('<16sHHIQQQIHHHHHH', data, 0,
                     bytes.fromhex('7f454c46020101000000000000000000'),
                     elf_type, 62, 1, 0x400100, 64, 0, 0, 64, 56, 1, 0, 0, 0)
    segment(data, 0, 256, 0x400000, 768, 768, 5, 256)
    raw = bytes.fromhex(code)
    data[512:512+len(raw)] = raw
    data[640:658] = LITERAL
    return data


def fixtures():
    out = {name: bytes(base(code)) for name, code in CODE.items()}
    data = base(); segment(data, 0, 256, 0x400000, 384, 768, 5, 256)
    out['S07'] = bytes(data)
    data = base(); struct.pack_into('<H', data, 56, 2)
    segment(data, 1, 256, 0x500000, 768, 768, 5, 256)
    out['S08'] = bytes(data)
    data = base(); data[640] = 0
    out['S09'] = bytes(data)
    data = base('')
    for i, displacement in enumerate((121, 114, 107, 100, 93, 86, 79, 72, 65)):
        off = 512 + 7 * i
        data[off:off+7] = b'\x48\x8d\x3d' + struct.pack('<i', displacement)
    out['S10'] = bytes(data)
    out['S14'] = bytes(base(elf_type=3))
    # Independent reviewer C01: file-unique literal, ambiguous virtual address.
    data = base(); struct.pack_into('<H', data, 56, 2)
    segment(data, 1, 768, 0x400180, 18, 18, 4, 1)
    data[768:786] = b'X' * 18
    out['C01'] = bytes(data)
    # C02: entry maps non-X; same file byte has executable alias at OTHER VA.
    data = base(); struct.pack_into('<H', data, 56, 2)
    segment(data, 0, 256, 0x400000, 768, 768, 4, 256)
    segment(data, 1, 512, 0x500000, 1, 1, 5, 1)
    out['C02'] = bytes(data)
    data = base(); struct.pack_into('<Q', data, 32, 1000)
    out['TRUNC_PHDR'] = bytes(data)
    out['SHORT_HEADER'] = bytes(base()[:63])
    data = base(); struct.pack_into('<Q', data, 64+16, 2**64-16)
    out['SEGMENT_WRAP'] = bytes(data)
    data = base(); data[5] = 2
    out['WRONG_ENDIAN'] = bytes(data)
    data = base(); struct.pack_into('<H', data, 18, 183)
    out['WRONG_MACHINE'] = bytes(data)
    # Two different file spans, one code and one data, with literal-address slot.
    data = base('488b3539ff0f00c3'); struct.pack_into('<H', data, 56, 2)
    segment(data, 0, 256, 0x400000, 384, 384, 5, 256)
    segment(data, 1, 640, 0x500000, 384, 384, 4, 128)
    data[640:658] = bytes(18)
    data[768:786] = LITERAL
    struct.pack_into('<Q', data, 704, 0x500080)
    out['X02_SLOT'] = bytes(data)
    return out

"""Deterministic gzip transport using stored DEFLATE blocks, no zlib encoder.

Fixed empty metadata and literal blocks make bytes independent of Python,
operating-system gzip headers and compression-library versions. Apache-2.0.
"""
from binascii import crc32
from struct import pack


def deterministic_gzip(raw):
    assert isinstance(raw,bytes)
    pieces=[raw[i:i+65535]for i in range(0,len(raw),65535)] or [b'']
    body=b''.join(bytes([int(i==len(pieces)-1)])+pack('<HH',len(p),65535^len(p))+p
                  for i,p in enumerate(pieces))
    return b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\xff'+body+pack('<II',crc32(raw)&0xffffffff,len(raw)&0xffffffff)

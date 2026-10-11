"""Exact gzip transport header used by the pinned macOS PR431 witnesses.

Activated only by this package's verifier child environment. For mtime=0,
normalize the gzip OS header byte to19. Deflate payload, CRC, size, JSON,
upstream program bytes and upstream hash assertions remain unchanged.
Python3.12 platform zlib and Python3.13 otherwise choose different OS bytes.
"""
import gzip
import os


def normalize_zero_mtime_header(blob, mtime):
    if mtime != 0:
        return blob
    assert len(blob) >= 18 and blob[:3] == b'\x1f\x8b\x08'
    assert blob[3] == 0 and blob[4:8] == b'\x00\x00\x00\x00'
    return blob[:9] + b'\x13' + blob[10:]


if os.environ.get('E8_HAMMING_GZIP_OS19') == '1':
    _original_compress = gzip.compress

    def _source_bound_compress(data, compresslevel=9, *, mtime=None):
        return normalize_zero_mtime_header(
            _original_compress(data, compresslevel=compresslevel, mtime=mtime),
            mtime)

    gzip.compress = _source_bound_compress

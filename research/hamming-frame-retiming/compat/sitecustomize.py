"""Retain the published supplier gzip metadata on every supported Python/OS.

Python 3.11/3.12 may expose zlib's OS byte; 3.13+ emits 255. Normalize
only this non-payload metadata field. Never alter DEFLATE data or its CRC.
"""
from pathlib import Path
import gzip,json
_policy=json.loads((Path(__file__).with_name('GZIP-POLICY.json')).read_text())
if not getattr(gzip,'_hamming_canonical_metadata',False):
 _compress=gzip.compress
 def _canonical_compress(data,compresslevel=9,*,mtime=0):
  raw=_compress(data,compresslevel=compresslevel,mtime=mtime)
  if mtime==_policy['mtime']:
   assert raw[:3]==bytes.fromhex('1f8b08')
   raw=raw[:9]+bytes([_policy['canonical_os_byte']])+raw[10:]
  return raw
 gzip.compress=_canonical_compress
 gzip._hamming_canonical_metadata=True

"""Byte-pinned new 70-pivot witness, rechecked against immutable upstream data."""
from pathlib import Path
import hashlib,json
PATH=Path(__file__).resolve().parent/'kernel70-witness.json'
SHA256='8b99bb2f0e9f352c303d251009058cc30e7ad4c20b8e32e863afb0ebcc3388b7'
def load():
    raw=PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA256:
        raise ValueError('70-pivot witness bytes changed')
    return json.loads(raw)

"""Frozen new relation witnesses; equations are rechecked against pinned data."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
PATH=HERE/'kernel-witness.json'
SHA256='ff2539ed56c790545c33a03ce185e49a8132ca9db26c007686deb6a4009b06d6'

def load():
    data=PATH.read_bytes()
    if hashlib.sha256(data).hexdigest()!=SHA256:
        raise ValueError('Kernel witness bytes changed')
    return json.loads(data)

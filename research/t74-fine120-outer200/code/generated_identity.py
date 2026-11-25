"""Proof-relevant identities for generated artifacts, independent of gzip streams.

Immutable source archives retain their exact byte hashes. For freshly emitted
artifacts, gzip identity is the exact decompressed payload and JSON identity
retains every field. Only CLIFFORD-REVIEW's root timing field is excluded.
Literal receipt references are checked against actual files before replacing
the three gzip references (and the phase recipe reference) with content hashes.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
import copy
import gzip
import hashlib
import json
import math

if not __debug__:
    raise RuntimeError('Assertions must remain enabled')

FILES=('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json',
       'INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-RECIPES.json',
       'CLIFFORD-REVIEW.json','RESIDUAL-ADAPTERS.json')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def json_identity(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')).hexdigest()

def payload_identity(path):
    return hashlib.sha256(gzip.decompress(Path(path).read_bytes())).hexdigest()

def phase_value(directory,value=None):
    directory=Path(directory)
    value=copy.deepcopy(json.loads((directory/'CLIFFORD-REVIEW.json').read_bytes())if value is None else value)
    assert value['canonical_word_sha256']==sha(directory/'CANONICAL-WORD.json.gz'),'stale phase canonical word reference'
    assert value['recipe_sha256']==sha(directory/'CLIFFORD-RECIPES.json'),'stale phase recipe reference'
    seconds=value.pop('seconds')
    assert type(seconds)in(int,float) and math.isfinite(seconds) and seconds>=0,'invalid phase timing metadata'
    value['canonical_word_sha256']=payload_identity(directory/'CANONICAL-WORD.json.gz')
    value['recipe_sha256']=json_identity(json.loads((directory/'CLIFFORD-RECIPES.json').read_bytes()))
    return value

def native_value(directory,value=None):
    directory=Path(directory)
    value=copy.deepcopy(json.loads((directory/'INDEPENDENT-LOCAL-REPLAY.json').read_bytes())if value is None else value)
    for field,name in [('canonical_word_sha256','CANONICAL-WORD.json.gz'),('local_programs_sha256','LOCAL-PROGRAMS.json.gz')]:
        assert value[field]==sha(directory/name),'stale native artifact reference: '+field
        value[field]=payload_identity(directory/name)
    return value

def artifact_identities(directory):
    directory=Path(directory)
    result={}
    for name in FILES:
        path=directory/name
        if name.endswith('.gz'):
            result[name]=payload_identity(path)
        else:
            value=phase_value(directory)if name=='CLIFFORD-REVIEW.json'else native_value(directory)if name=='INDEPENDENT-LOCAL-REPLAY.json'else json.loads(path.read_bytes())
            result[name]=json_identity(value)
    return result

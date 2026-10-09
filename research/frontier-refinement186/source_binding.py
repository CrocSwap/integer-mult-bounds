"""Exact additive source closure; guards remain active under optimized Python."""
from pathlib import Path
from hashlib import sha256
import json,sys
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(100000)
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PIN='166a34d75e853e933855f0f7e940fe77c4bb6b8d'
BASE='f5ab0230f0db0a98df7e99ce4169d15fad6c74c7'
DEPENDENCY_CLOSURE_PIN='49e38a7cc609be712743e51417bb62b7849d09fd829860864ae07d9b32da74ee'
OWN_FILES={'arithmetic.py','verify.py','scalar.py','check_banks.py','source_binding.py','test_refinement.py','test_source.py','README.md','PROOF.md','NOTICE','LICENSE','inputs/logical.json','inputs/physical-sinks.json','inputs/scaled-bank.json'}
def require(c,m):
    if not c:raise ValueError(m)
def canonical(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def check_manifest(manifest,read_dependency=None,read_owned=None):
    require(type(manifest)is dict and manifest.get('upstream_commit')==PIN and manifest.get('preserved_base_commit')==BASE,'wrong source revision label')
    deps=manifest['dependency_sha256'];own=manifest['source_sha256']
    require(type(deps)is dict and canonical(deps)==DEPENDENCY_CLOSURE_PIN,'wrong frozen dependency closure')
    require(type(own)is dict and set(own)==OWN_FILES,'incomplete own source closure')
    read_dependency=read_dependency or (lambda p:(ROOT/p).read_bytes())
    read_owned=read_owned or (lambda p:(HERE/p).read_bytes())
    for path,expected in deps.items():require(sha256(read_dependency(path)).hexdigest()==expected,'dependency bytes changed: '+path)
    for path,expected in own.items():require(sha256(read_owned(path)).hexdigest()==expected,'own source bytes changed: '+path)
    return manifest
def check_sources():return check_manifest(json.loads((HERE/'SOURCE.json').read_bytes()))

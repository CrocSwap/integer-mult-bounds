"""Load the frozen derived storage compiler from its exact PR84 predecessor.

Prepared for Thomas DiFiore with OpenAI Codex assistance. Apache-2.0.
The complete readable change is preserved in ENGINE-PATCH.diff. All inherited
authors, licenses and notices remain applicable to storage_engine.py.
"""
from pathlib import Path
from hashlib import sha256
import difflib

HERE=Path(__file__).resolve().parent
ORIGINAL_SHA256='a4a582339430662e13c905d5a4701f4e488ff1830a72dc1c71da57066ad2ea38'
DERIVED_SHA256='3d2a664cfb0175fffeb90d75dd9be4602becc7dd56d65df8837cb1f4b9c2ef6f'


def apply(source):
    assert sha256(source.encode()).hexdigest()==ORIGINAL_SHA256,'Changed PR84 compiler'
    result=(HERE/'storage_engine.py').read_text()
    assert sha256(result.encode()).hexdigest()==DERIVED_SHA256,'Changed storage compiler'
    patch=''.join(difflib.unified_diff(source.splitlines(True),result.splitlines(True),
        fromfile='references/frame-compiler/pr84/scripts/experiments/indexed_cycle_engine.py',
        tofile='research/deferred-span-frames/storage_engine.py'))
    assert patch==(HERE/'ENGINE-PATCH.diff').read_text(),'Derived-source patch differs'
    return result

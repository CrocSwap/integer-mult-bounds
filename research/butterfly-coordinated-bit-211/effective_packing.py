"""Actual V6 emitted graph/word/frame inputs for retained packing verification."""
from common import *
import candidate,check_packed,json,hashlib
def run(bit_root,fresh):
    word,emitted,metadata=candidate.candidate(bit_root)
    assert metadata['emitted_sha256']==fresh['metadata']['emitted_sha256']
    original=check_packed.read
    prefix=Path(bit_root)/'research/paired-cube-diagonal-bit-168/selected/bit'
    data={'graph_p12.json':emitted['graph_p12.json'],'word_p12.json.gz':emitted['word_p12.json'],'frames_p12.json.gz':emitted['frames_p12.json']}
    observed={}
    def effective(path):
        if path.parent==prefix and path.name in data:
            value=data[path.name];observed[path.name]=hashlib.sha256(value).hexdigest()
            return json.loads(value)
        return original(path)
    check_packed.read=effective
    try:result=check_packed.run(bit_root,fresh)
    finally:check_packed.read=original
    assert observed=={name:metadata['emitted_sha256'][name.removesuffix('.gz')] for name in data}
    result['effective_input_sha256']=observed
    result['source_head']=metadata['source_head']
    result['limitations']=['Completed-core weighted, separated-residual and restored-row interfaces remain inherited conditions.']
    return result

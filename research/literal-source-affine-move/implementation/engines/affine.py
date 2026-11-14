"""Literal fixed-offset native XOR translation in the Gamma6/HOME ABI.

Apache-2.0; prepared with substantial OpenAI assistance. The retained
first-slot reversal/CNOT instructions are unchanged. Offset and pivot are
fixed template data; no encoded input controls runtime table generation.
"""
from pathlib import Path
from hashlib import sha256
import atexit
import importlib.util
import json
import sys
import tempfile

HERE=Path(__file__).resolve().parent
_cache=tempfile.TemporaryDirectory(prefix='affine-source-')
atexit.register(_cache.cleanup)
sys.dont_write_bytecode=True
sys.pycache_prefix=str(Path(_cache.name)/'required-absent')


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
    raw=(HERE/pin['local']).read_bytes()
    if len(raw)!=pin['bytes'] or sha256(raw).hexdigest()!=pin['sha256']:
        raise ValueError('frozen source drift: '+pin['local'])
P=load('affine_parent',HERE/'reference/rank2/rank2.py')
T=load('affine_first_slot',HERE/'reference/translation/translate.py')
Builder=P.Builder
BLANK,ONE,MARK,BITS=P.BLANK,P.ONE,P.MARK,P.BITS
HEADER,DATA,WORK,TRACE,TAPES=P.HEADER,P.DATA,P.WORK,P.TRACE,P.TAPES


def fixed_offset(offset):
    if type(offset) is not int or not 0<=offset<512:
        raise ValueError('construction-time nine-bit offset')
    return offset


def conjugator(offset):
    """Fixed chronological CNOT word G with G e0=b, for nonzero b."""
    offset=fixed_offset(offset)
    if not offset:
        return ()
    pivot=(offset&-offset).bit_length()-1
    word=[] if pivot==0 else [(0,pivot),(pivot,0),(0,pivot)]
    word.extend((slot,pivot) for slot in range(9) if slot!=pivot and (offset>>slot)&1)
    return tuple(word)


def components(offset,mutation=None):
    offset=fixed_offset(offset)
    if offset==0:
        return []
    word=conjugator(offset)
    if mutation=='omit_last_conjugator_gate' and word:
        word=word[:-1]
    flip=('X0_',T.compile_translation())
    if not word:
        return [flip]
    before=('G_inverse_',P.compile_word(tuple(reversed(word))))
    after=('G_',P.compile_word(word))
    return [before,after,flip] if mutation=='wrong_conjugation_order' else [before,flip,after]


def compile_translation(offset,mutation=None):
    """One complete original-owner transaction for a fixed offset, even zero."""
    factors,a=components(offset,mutation),Builder()
    for tape in (WORK,TRACE):
        a.op('move',tape,-1);a.op('write',tape,MARK);a.op('move',tape,1)
    a.mark('clone')
    a.op('read',DATA,{'0':'clone0',ONE:'clone1',BLANK:'cloned'})
    for bit in BITS:
        a.mark('clone'+bit)
        a.op('write',WORK,bit);a.op('move',WORK,1);a.op('move',DATA,1)
        a.op('write',TRACE,ONE);a.op('move',TRACE,1);a.op('goto','clone')
    a.mark('cloned');P.return_source(a);a.rewind(WORK,BITS)
    entries={}
    for index,(name,(code,alphabet)) in enumerate(factors):
        entries[name]=len(a.code)
        after=factors[index+1][0]+'0' if index+1<len(factors) else 'commit'
        P.insert(a,name,code,alphabet,after)
    a.mark('commit');entries['commit']=len(a.code)
    a.op('read',WORK,{'0':'commit0',ONE:'commit1',BLANK:'committed'})
    for bit in BITS:
        a.mark('commit'+bit)
        a.op('write',DATA,bit);a.op('write',WORK,BLANK)
        a.op('move',WORK,1);a.op('move',DATA,1)
        a.op('write',TRACE,ONE);a.op('move',TRACE,1);a.op('goto','commit')
    a.mark('committed');P.return_source(a);a.rewind(WORK,(BLANK,))
    for tape in (WORK,TRACE):
        a.op('move',tape,-1);a.op('write',tape,BLANK);a.op('move',tape,1)
    a.op('halt')
    code,alphabet=a.finish((BLANK,'0',ONE,MARK))
    return code,alphabet,entries

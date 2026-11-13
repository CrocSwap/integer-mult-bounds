"""Generic fixed monomial and actual MOVE24476 literal Gamma6 join.

Apache-2.0; substantial OpenAI assistance. All source/recipe processing is
offline. Runtime is only the emitted local instruction table.
"""
from pathlib import Path
from hashlib import sha256
import atexit
import copy
import importlib.util
import json
import sys
import tempfile

HERE=Path(__file__).resolve().parent
_cache=tempfile.TemporaryDirectory(prefix='affine-move-source-')
atexit.register(_cache.cleanup)
sys.dont_write_bytecode=True;sys.pycache_prefix=str(Path(_cache.name)/'absent')


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module);return module


manifest=json.loads((HERE/'SOURCES.json').read_text())
for pin in manifest['files']:
    raw=(HERE/pin['local']).read_bytes()
    if len(raw)!=pin['bytes'] or sha256(raw).hexdigest()!=pin['sha256']:
        raise ValueError('frozen source drift: '+pin['local'])
if sha256((HERE/'RECIPE.json').read_bytes()).hexdigest()!=manifest['recipe_sha256']:
    raise ValueError('bound source recipe drift')
CENT=load('source_move_center',HERE/'engines/join.py')
AFF=load('source_move_affine',HERE/'engines/affine.py')
P=CENT.P
Builder=P.Builder
BLANK,ONE,MARK,BITS=P.BLANK,P.ONE,P.MARK,P.BITS
HEADER,DATA,WORK,TRACE,TAPES=P.HEADER,P.DATA,P.WORK,P.TRACE,P.TAPES
SOURCE=json.loads((HERE/'RECIPE.json').read_text())


def monomial_components(recipe,prefix='monomial_'):
    """One fixed D_(q+a*f), binary G, output X_b, without outer staging."""
    if set(recipe)!=set(('matrix_rows','offset','quadratic_rows','linear_Z4','phase')):
        raise ValueError('fixed monomial schema')
    if len(recipe['matrix_rows'])!=9 or len(recipe['linear_Z4'])!=9 or len(recipe['quadratic_rows'])!=9:
        raise ValueError('fixed nine-coordinate monomial')
    word=P.LINEAR.cnot_word(tuple(recipe['matrix_rows']))
    result=[(prefix+'phase_',P.PHASE.compile_phase(tuple(recipe['linear_Z4']),
                tuple(recipe['quadratic_rows']),recipe['phase']))]
    if word:result.append((prefix+'binary_',P.compile_word(word)))
    result.extend((prefix+name,code) for name,code in AFF.components(recipe['offset']))
    return result


def transaction(factors):
    a=Builder()
    for tape in (WORK,TRACE):
        a.op('move',tape,-1);a.op('write',tape,MARK);a.op('move',tape,1)
    a.mark('clone');a.op('read',DATA,{'0':'clone0',ONE:'clone1',BLANK:'cloned'})
    for bit in BITS:
        a.mark('clone'+bit);a.op('write',WORK,bit);a.op('move',WORK,1);a.op('move',DATA,1)
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
        a.mark('commit'+bit);a.op('write',DATA,bit);a.op('write',WORK,BLANK)
        a.op('move',WORK,1);a.op('move',DATA,1);a.op('write',TRACE,ONE)
        a.op('move',TRACE,1);a.op('goto','commit')
    a.mark('committed');P.return_source(a);a.rewind(WORK,(BLANK,))
    for tape in (WORK,TRACE):
        a.op('move',tape,-1);a.op('write',tape,BLANK);a.op('move',tape,1)
    a.op('halt');code,alphabet=a.finish((BLANK,'0',ONE,MARK))
    return code,alphabet,entries


def compile_monomial(recipe):
    return transaction(monomial_components(recipe))


def compile_move(mutation=None):
    if SOURCE['event_index']!=24476 or SOURCE['event']!=['MOVE',727,3,470,False]:
        raise ValueError('actual selected event binding')
    recipe=copy.deepcopy(SOURCE['recipe']);rank=recipe['rank']
    if mutation=='wrong_phase':recipe['right']['phase']=(recipe['right']['phase']+1)%4
    if mutation=='wrong_offset':recipe['right']['offset']^=4
    factors=[('joint_guard_',CENT.compile_guard(rank,weak=mutation=='weak_cutoff'))]
    factors.extend(monomial_components(recipe['right'],'right_'))
    center=CENT.components(rank)[1:]
    if mutation=='omit_last_C':center=[p for p in center if p[0]!='C'+str(rank-1)+'_']
    factors.extend(('center_'+name,code) for name,code in center)
    factors.extend(monomial_components(recipe['left'],'left_'))
    return transaction(factors)

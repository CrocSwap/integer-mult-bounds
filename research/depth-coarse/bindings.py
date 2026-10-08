"""Pinned dependency adapters; mathematical/compiler bodies remain unchanged.

PR71 Chafik Boukhalfa: split/anchor/next-use composition; PR65/67 Rohan Arun:
schedule, directed arithmetic and profile cost; PR68 Dominik Scholz: live
controls; PR69 eumemic: coarse columns. Earlier notices are in vendor/.
Prepared with substantial OpenAI Codex assistance, Apache-2.0.
"""
import sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from pathlib import Path
import ast,hashlib,json,types,subprocess,tempfile,shlex,os
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
VENDOR=HERE/'vendor'
_previous_import_path=list(sys.path)
sys.path.insert(0,str(ROOT/'scripts/experiments'))
INHERITED=ROOT/'references/frame-compiler/pr48'
alias_paths={'partial_swap.paired':'scripts/partial_swap/paired.py',
             'partial_swap.shared':'scripts/partial_swap/shared.py',
             'exclusion_circuit':'scripts/exclusion_circuit.py'}
def check_aliases():
    manifest=json.loads((INHERITED/'SOURCE.json').read_text())['files']
    for name,relative in alias_paths.items():
        expected=manifest[relative]
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==expected,'Changed root library: '+relative
        if name in sys.modules:
            module=sys.modules[name]
            assert hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()==expected,'Unexpected imported library: '+name
check_aliases()

def checked_source(name):
    pins=json.loads((VENDOR/'SOURCE.json').read_text())
    raw=(VENDOR/name).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==pins[name]['sha256'],name
    return raw.decode()

def original_definition(name,function):
    source=checked_source(name);tree=ast.parse(source)
    node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==function)
    return '\n'.join(source.splitlines()[node.lineno-1:node.end_lineno])+'\n'

import binary_frame_math as arithmetic
refine=types.ModuleType('balanced_split_refine');refine.__file__=str(VENDOR/'pr65-refine.py')
refine.INJECTED_ROOT=ROOT
source=checked_source('pr65-refine.py')
needle='ROOT = Path(__file__).resolve().parents[3]';assert source.count(needle)==1
exec(compile(source.replace(needle,'ROOT = INJECTED_ROOT'),refine.__file__,'exec'),refine.__dict__)
previous=sys.modules.get('refine');sys.modules['refine']=refine
try:
    audit=types.ModuleType('balanced_split_audit');audit.__file__=str(VENDOR/'pr65-audit.py')
    exec(compile(checked_source('pr65-audit.py'),audit.__file__,'exec'),audit.__dict__)
finally:
    if previous is None:sys.modules.pop('refine',None)
    else:sys.modules['refine']=previous

compiler=types.ModuleType('balanced_split_engine');compiler.__file__=str(VENDOR/'pr71-engine.py')
compiler.INJECTED_REFERENCE=ROOT/'references/frame-compiler/pr48'
source=checked_source('pr71-engine.py')
needle="ROOT=Path(__file__).resolve().parents[2]/'references/frame-compiler/pr48'"
assert source.count(needle)==1
exec(compile(source.replace(needle,'ROOT=INJECTED_REFERENCE'),compiler.__file__,'exec'),compiler.__dict__)

pair=types.ModuleType('balanced_split_original_pair');pair.__file__=str(ROOT/'research/pair-assembly/pair_graph.py')
raw=Path(pair.__file__).read_bytes()
assert hashlib.sha256(raw).hexdigest()=='3d47e89d2649c90800a276bdd0480131def50e0bdf92c122a19494b55bf17420'
exec(compile(raw,pair.__file__,'exec'),pair.__dict__)
check_aliases()
definitions={}
exec(original_definition('pr71-split-graph.py','split_class'),definitions)
exec(original_definition('pr65-schedule.py','reordered_build'),definitions)
split_class=definitions['split_class'];reordered_build=definitions['reordered_build']
producer=types.SimpleNamespace(_graph=pair)

def graph(h):
    assert h in (23,25)
    module=producer._graph;original=module.circuit_class;original_points=module.alternating_points
    try:
        module.circuit_class=lambda dimension:split_class(original(dimension),[1,1,2])
        def anchored_points(dimension,common):
            points=original_points(dimension,common)
            pairs=[(a,a+1) for a in range(0,dimension-1,2) if common not in (a,a+1)]
            chosen=min(pairs)
            result=list(chosen)+[x for x in points if x not in chosen]
            assert sorted(result)==[x for x in range(dimension) if x!=common]
            return result
        module.alternating_points=anchored_points
        return module.graph(h)
    finally:module.circuit_class=original;module.alternating_points=original_points
producer.graph=graph

def compile_axis(h):
    compiler.graph=graph
    original_build=compiler.build
    compiler.build=reordered_build(original_build,'cover-core' if h==23 else 'reverse-node')
    compiler.PENDING_COST=True
    try:
        with tempfile.TemporaryDirectory(prefix='balanced-split-') as directory:
            work=Path(directory);oracle=work/'oracle'
            subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(VENDOR/'pr67-profile-oracle.cpp'),'-o',str(oracle)],check=True)
            compiler.oracles=[];compiler.ORACLE_EXE=str(oracle);compiler.ORACLE_INPUT=str(work/'oracle-input.bin')
            try:result,word=compiler.compile_(h,matching=True,reclaim=True,dirty=True)
            finally:
                for process in compiler.oracles:
                    process.stdin.close();assert process.wait(timeout=10)==0
    finally:compiler.build=original_build
    result.pop('seconds',None)
    result['scalar']=graph(h).verify()
    return result,word

# Imported definitions retain their private module globals. Deferred math
# import is already bound in sys.modules; do not leak reference search paths.
sys.path[:]=_previous_import_path

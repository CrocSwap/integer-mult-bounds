"""Conformance and invalidation checks for the compact prefix-key construction."""
from pathlib import Path
import ast
import hashlib
import json
import os
import shutil
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def expect_value_error(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError('Expected rejection did not occur')


def structure_checks():
    original = ast.parse((HERE/'vendor/prefix_clifford.py').read_bytes())
    candidate = ast.parse((HERE/'indexed_clifford.py').read_bytes())
    def relevant(tree):
        return ast.dump(ast.Module(body=[n for n in tree.body
            if not isinstance(n,(ast.ImportFrom,ast.Expr))],type_ignores=[]),include_attributes=False)
    need(relevant(original) == relevant(candidate),'The compiler body is unchanged')
    old = ast.parse((HERE/'vendor/state.py').read_bytes())
    new = ast.parse((HERE/'compact_state.py').read_bytes())
    prefix = next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='prefix')
    step = next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='step')
    old_if = next(n for n in prefix.body if isinstance(n,ast.If) and
                  isinstance(n.test,ast.Compare) and isinstance(n.test.left,ast.Name) and n.test.left.id=='tag')
    new_if = next(n for n in step.body if isinstance(n,ast.If))
    need(ast.dump(old_if,include_attributes=False) == ast.dump(new_if,include_attributes=False),
         'Every gate branch is retained literally as an AST')
    return 2


def state_checks(R, candidate):
    old = R.load(HERE/'vendor/inputs/clifford_exact.py','dense_state_reference')
    count = 0
    for n in range(1,7):
        for sign in (-1,1):
            for phase in range(4):
                rows = tuple(1 << ((i+1)%n) for i in range(n))
                diagonal = tuple(1 << i for i in range(n))
                gates = [('P',rows),('C',(1<<n)-1,sign),('D',diagonal,(1,)*n),('X',1),('phase',phase)]
                for basis in range(1<<n):
                    a = old.Op(n,old.identity(n),gates).zero_state(basis)
                    b = candidate.Op(n,candidate.identity(n),gates).zero_state(basis)
                    need(a == b,'Every exact Gaussian state amplitude and denominator')
                    count += 1
    gates = [('C',255,1),('C',511,-1),('phase',1),('X',131)]
    for basis in range(512):
        a = old.Op(9,old.identity(9),gates).zero_state(basis)
        b = candidate.Op(9,candidate.identity(9),gates).zero_state(basis)
        need(a == b,'All nine-bit input basis columns')
        count += 1
    for n in range(1,6):
        for length in (0,1,7,31,127,512):
            gates = [('C',(i%(2**n-1))+1,(-1)**i) if i%3 else ('phase',i%4)
                     for i in range(length)]
            for basis in (0,(1<<n)-1):
                a = old.Op(n,old.identity(n),gates).zero_state(basis)
                b = candidate.Op(n,candidate.identity(n),gates).zero_state(basis)
                need(a == b,'Deep iterative preparation and sparse normalization')
                count += 1
    return count


def cache_checks(C, S):
    S.clear()
    op = C.Op(2,C.identity(2),[('C',1,1)])
    before = op.zero_state()
    returned = op.zero_state()
    returned[0][0] = (999,999)
    need(op.zero_state() == before,'Returned lists do not alias cached tuples')
    op.circuit.append(('phase',1))
    need(op.zero_state() != before,'Phase changes invalidate both cache levels')
    op.circuit[-1] = ('phase',0)
    need(op.zero_state() == before,'Equivalent phase-zero return')
    # Repeated new keys must leave both fixed-capacity stores bounded.
    for phase in range(S.NODE_CAP+2):
        result = C.Op(2,C.identity(2),[('phase',phase)]).zero_state(1)
        need(result[1] == 0 and result[0][1] == ((1,0),(0,1),(-1,0),(0,-1))[phase%4],
             'Node and state eviction preserve the actual phase')
    need(len(S._nodes) == S.NODE_CAP and len(S._states) == S.STATE_CAP,'Both stores reach their bounds')
    need(S.route.cache_info().currsize == 512,'Prepared-path cache reaches its bound')
    S.clear()
    original = op.zero_state()
    old_nodes = tuple(S._nodes.values())
    for phase in range(S.NODE_CAP+1):
        S.node(0,('phase',phase+10000))
    need(not set(old_nodes).intersection(S._nodes.values()),'Ancestors can be evicted while routes survive')
    need(op.zero_state() == original,'Surviving routes keep stable nonrecycled IDs')
    S._next = 2**63-S.MAX_GATES-1
    need(op.zero_state() == original and S._next < 2**63-S.MAX_GATES-1,
         'ID rollover clears all dependent caches together')
    for n,basis,gates in ((0,0,[]),(10,0,[]),(2,4,[]),(2,0,[('phase',0)]*513)):
        expect_value_error(lambda: C.Op(n,(),gates).zero_state(basis))
    expect_value_error(lambda: C.Op(2,(),[('unknown',)]).zero_state())
    S.clear()
    return {'eviction_phases':S.NODE_CAP+2,'ancestor_eviction_keys':S.NODE_CAP+1,
            'boundary_rejections':5,'path_capacity':512,'node_capacity':S.NODE_CAP,'state_capacity':S.STATE_CAP}


def source_control(R):
    original = R.HERE
    with tempfile.TemporaryDirectory(prefix='source-control-',dir=os.environ.get('IMB_SCRATCH_ROOT')) as tmp:
        copy = Path(tmp)
        shutil.copyfile(HERE/'ORIGINS.json',copy/'ORIGINS.json')
        for pin in json.loads((HERE/'ORIGINS.json').read_bytes())['files']:
            path = copy/pin['path']
            path.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(HERE/pin['path'],path)
        broken = copy/'vendor/state.py'
        raw = broken.read_bytes()
        broken.write_bytes(bytes([raw[0]^1])+raw[1:])
        try:
            R.HERE = copy
            expect_value_error(R.authenticate)
        finally:
            R.HERE = original
    return 1


def main():
    need(len(sys.argv)==1,'No verifier arguments')
    sys.dont_write_bytecode = True
    sys.path.insert(0,str(HERE))
    with tempfile.TemporaryDirectory(prefix='key-index-bytecode-',dir=os.environ.get('IMB_SCRATCH_ROOT')) as cache:
        sys.pycache_prefix = cache
        import run as R
        R.authenticate()
        C = R.load(HERE/'indexed_clifford.py','indexed_test_compiler')
        import compact_state as S
        structure = structure_checks()
        states = state_checks(R,C)
        controls = cache_checks(C,S)
        corruption = source_control(R)
        S.clear()
        native = R.native('candidate')['native']
    result = {'status':'PASS_CLIFFORD_PREFIX_KEY_INDEX','state_comparisons':states,
              'structural_preservation_checks':structure,'cache_checks':controls,
              'source_corruption_rejections':corruption,'complete_native':native,
              'scope':'Implementation-preservation proof and exact conformance; no new kappa.'}
    files = ['compact_state.py','indexed_clifford.py','run.py','benchmark.py','verify.py','PROOF.md','ORIGINS.json']
    result['source_sha256'] = {name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in files}
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':
    main()

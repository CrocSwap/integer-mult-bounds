"""Check state preservation and every current native map.

Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import ast
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            path = HERE/'inputs'/Path(pin['path']).name
            need(sha256(path.read_bytes()).hexdigest() == pin['sha256'], 'Native source hash: '+path.name)


def check_edits():
    original = ast.parse((HERE/'inputs/clifford_exact.py').read_text())
    def normalized(tree):
        out = deepcopy(tree)
        out.body = [n for n in out.body if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str))
                    and not (isinstance(n,ast.ImportFrom) and n.module == 'state')]
        for n in out.body:
            if isinstance(n,ast.ClassDef) and n.name == 'Op':
                n.body = [f for f in n.body if not (isinstance(f,ast.FunctionDef) and f.name == 'zero_state')]
        return ast.dump(out,include_attributes=False)
    for name in ('prefix_clifford','gated_clifford'):
        need(normalized(ast.parse((HERE/(name+'.py')).read_text())) == normalized(original),
             'Only Op.zero_state changes in '+name)
    old = ast.parse((HERE/'inputs/local.py').read_text())
    actual = ast.parse((HERE/'native.py').read_text())
    for name in ('need','span','native'):
        a = next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name == name)
        b = next(n for n in actual.body if isinstance(n,ast.FunctionDef) and n.name == name)
        if name == 'native':
            a.args.args.extend([ast.arg(arg='C'),ast.arg(arg='V')])
            a.body = [n for n in a.body if not (isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('C','V'))]
        need(ast.dump(a,include_attributes=False) == ast.dump(b,include_attributes=False),
             'The native driver keeps every source check: '+name)



def gray_checks():
    from run import load
    import random
    old = load(HERE/'inputs/native_verify.py','reference_gray')
    new = load(HERE/'native_gray.py','candidate_gray')
    rng = random.Random(6453)
    gates = []
    for _ in range(32):
        rows = [1 << i for i in range(9)]
        for _ in range(24):
            a,b = rng.sample(range(9),2)
            rows[a] ^= rows[b]
        gates.append(('P',tuple(rows)))
        q = [0]*9
        for i in range(9):
            for j in range(i,9):
                if rng.randrange(2):
                    q[i] |= 1 << j
                    q[j] |= 1 << i
        linear = tuple(((q[i] >> i) & 1)+2*rng.randrange(2) for i in range(9))
        gates.append(('D',tuple(q),linear))
    for gate in gates:
        need(old.action(gate) == new.action(gate),'Every Gray-table value')
    # The fork retains all other scientific checks and gate semantics.
    def normalized(path, reference):
        tree = ast.parse(path.read_text())
        tree.body = [n for n in tree.body if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str))]
        for n in tree.body:
            if isinstance(n,ast.FunctionDef) and n.name == 'action':
                n.body = [ast.Pass()]
            if reference and isinstance(n,ast.FunctionDef) and n.name == 'state':
                for sub in ast.walk(n):
                    if isinstance(sub,ast.Assign) and isinstance(sub.value,ast.Call) and isinstance(sub.value.func,ast.Name) and sub.value.func.id == 'mul':
                        sub.value = ast.parse('action(gate)[address]',mode='eval').body
        return ast.dump(tree,include_attributes=False)
    need(normalized(HERE/'inputs/native_verify.py',True) == normalized(HERE/'native_gray.py',False),
         'Only the independent state action and P lookup change')
    return 512*len(gates)

def state_checks():
    from run import load
    import state
    old = load(HERE/'inputs/clifford_exact.py','reference_states')
    new = load(HERE/'prefix_clifford.py','prefix_states')
    count = 0
    for n in range(1,7):
        # All basis states, both C signs and all scalar phases.
        for sign in (-1,1):
            for phase in range(4):
                rows = tuple(1 << ((i+1)%n) for i in range(n))
                diagonal = tuple(1 << i for i in range(n))
                circuit = [('P',rows),('C',(1<<n)-1,sign),('D',diagonal,(1,)*n),('X',1),('phase',phase)]
                for basis in range(1<<n):
                    a = old.Op(n,old.identity(n),circuit).zero_state(basis)
                    b = new.Op(n,new.identity(n),circuit).zero_state(basis)
                    need(a == b,'Every exact state amplitude and denominator')
                    count += 1
    n = 9
    circuit = [('C',255,1),('C',511,-1),('phase',1),('X',131)]
    for basis in range(512):
        need(old.Op(n,old.identity(n),circuit).zero_state(basis) == new.Op(n,new.identity(n),circuit).zero_state(basis),
             'Every nine-bit basis state')
        count += 1
    op = new.Op(2,new.identity(2),[('C',1,1)])
    before = op.zero_state()
    returned = op.zero_state(); returned[0][0] = (999,999)
    need(op.zero_state() == before,'Returned state cannot corrupt the cache')
    op.circuit.append(('phase',1))
    need(op.zero_state() != before,'Changed phase cannot reuse the old state')
    op.circuit[-1] = ('phase',0)
    need(op.zero_state() == before,'The full circuit key binds the changed value')
    state.clear()
    for phase in range(540):
        c = [('phase',phase)]
        need(new.Op(2,new.identity(2),c).zero_state(1) == old.Op(2,old.identity(2),c).zero_state(1),
             'Eviction preserves state values')
    need(state.prefix.cache_info().currsize == 512,'The prefix cache has a fixed bound')
    state.clear()
    return count


def main():
    authenticate()
    check_edits()
    cases = state_checks()
    gray_entries = gray_checks()
    from run import run
    native,_ = run('prefix')
    result = {'status':'PASS_P104_NATIVE_PREFIX_REPLAY','state_comparisons':cases,'gray_table_entries':gray_entries,
              'complete_native':native,'cache_entries':512,
              'controls':['all basis indices','both C signs','all scalar phases','dimension key',
                          'returned-list mutation','circuit mutation','cache eviction','wrong native phase'],
              'scope':'Exact native verification speed only; no new kappa or full compiler replay.'}
    text = json.dumps(result,sort_keys=True,indent=2)+'\n'
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(text)
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == json.loads(text),'Exact complete result receipt')
    print(text,end='')


if __name__ == '__main__':
    main()

"""Check the fused grid map, retained ports and exact matrix errors."""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import ast
import json
import random
import sys

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
sys.path.insert(0, str(P))
from kernel import block, call, parity, baseline, retained, need


def authenticate():
    for pin in json.loads((P/'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            path = Path(pin['path']).relative_to('research/fused-gaussian-rounding')
            need(sha256((P/path).read_bytes()).hexdigest() == pin['sha256'], 'Source hash: '+str(path))


# These unchanged oracle functions come from the retained PR6509 checker.
# They use direct matrix convolution, not the fused kernel.
def oracle():
    names = {'add', 'sub', 'mul', 'rotate', 'ideal_pair', 'norm2', 'fiber_sums',
             'ideal_call', 'base_map', 'ideal_monomial', 'ideal_port'}
    tree = ast.parse((P/'inputs/oracle.py').read_text())
    tree.body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    need(len(tree.body) == len(names), 'Exact retained oracle functions')
    scope = {'F': Q}
    exec(compile(tree, 'retained matrix oracle', 'exec'), scope)
    return scope


def rejects(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError('Negative control accepted')


def main():
    authenticate()
    o = oracle()
    norm = lambda v: sum(a*a+b*b for a, b in v)
    error = lambda x, y: norm([(a-c, b-d) for (a,b),(c,d) in zip(x,y)])
    rotate = o['rotate']
    matrix = ((1j,1,1,-1j),(1,1j,-1j,1),(1,-1j,1j,1),(-1j,1,1,1j))
    def twice_ideal(x, sign):
        out = []
        for row in matrix:
            real = imag = 0
            for c, (a,b) in zip(row, x):
                u,v = int(complex(c).real), sign*int(complex(c).imag)
                real += u*a-v*b
                imag += u*b+v*a
            out.append((real,imag))
        return out
    cases = 0
    old_max = new_max = 0
    witness = None
    trace = {}
    for coords in product(range(-2,2), repeat=8):
        x = tuple(zip(coords[::2],coords[1::2]))
        a,b = parity(x)
        for sign in (-1,1):
            y = block(x, 16, sign, trace)
            need(block(y,16,-sign) == x, 'Exact inverse')
            need(parity(y) == (b,a), 'Coset exchange')
            need(tuple(map(sum,zip(*x))) == tuple(map(sum,zip(*y))), 'Conserved sum')
            exact = twice_ideal(x,sign)
            residual = [(2*u-r,2*v-s) for (u,v),(r,s) in zip(y,exact)]
            need(all(abs(n) <= 1 for z in residual for n in z), 'Nearest Gaussian output')
            need(norm(residual) == 4*(a+b), 'Sharp squared error')
            if all(n in (0,1) for n in coords):
                z = x
                for _ in range(4): z = block(z,16,sign)
                need(z == x, 'Fourth power')
            old = list(x)
            baseline.layer(old,0,16,sign)
            baseline.layer(old,1,16,sign)
            old_error = norm([(2*u-r,2*v-s) for (u,v),(r,s) in zip(old,exact)])
            if old_error > old_max:
                old_max = old_error
                witness = dict(input=list(map(list,x)), sign=sign, output=list(map(list,old)))
            new_max = max(new_max,norm(residual))
            cases += 1
    need(trace['data_additions'] == 20*cases and trace['checked_values'] == 42*cases,
         'Literal block work')
    old_trace = {}
    z = [(1,0),(0,1),(-1,0),(0,-1)]
    baseline.layer(z,0,16,1,old_trace);baseline.layer(z,1,16,1,old_trace)
    need(old_trace['data_additions'] == 40 and old_trace['data_half_shifts'] == 8,
         'Actual predecessor work')
    rng = random.Random(7046509)
    call_cases = port_cases = fibers = 0
    port_work = {}
    source = retained('rounded')
    port = retained('ports').port
    for f in (1,2,3):
        n = 8**f
        for axis, adj in product((0,2),(False,True)):
            values = [(rng.randrange(-15,16),rng.randrange(-15,16)) for _ in range(n)]
            actual = list(values);t = {}
            call(actual,f,axis,32,adj,t)
            ideal = o['ideal_call'](values,f,axis,adj)
            need(error(actual,ideal) <= ((f+1)//2)**2*n//2, 'Whole-call error bound')
            need(o['fiber_sums'](actual,f,axis) == o['fiber_sums'](values,f,axis), 'All spectator sums')
            need(t['data_additions'] == 5*n*((f+1)//2) and t['data_half_shifts'] == n*f,
                 'All call arithmetic')
            call(actual,f,axis,32,not adj)
            need(actual == values, 'Whole-call inverse')
            fibers += 4**f;call_cases += 1
        for kind, reverse in product((2,3),(False,True)):
            x = [(rng.randrange(-7,8),rng.randrange(-7,8)) for _ in range(n)]
            y = [(rng.randrange(-7,8),rng.randrange(-7,8)) for _ in range(n)]
            xx,yy = list(x),list(y)
            ax,ay,t,cuts = port(xx,yy,f,kind,reverse,40,call,source,True)
            need(len(cuts) == kind, 'Every paid cut')
            for axis,adj,before,after in cuts:
                need(error(after,o['ideal_call'](before,f,axis,adj)) <= ((f+1)//2)**2*n//2,
                     'Actual-input cut bound')
            exact = o['ideal_port'](x,y,f,kind,reverse)
            # The mix has norm at most three. Each bank receives at most five call errors.
            need(max(error(ax,exact[0]),error(ay,exact[1])) <= 25*((f+1)//2)**2*n//2,
                 'Complete port error')
            bx,by,_,empty = port(xx,yy,f,kind,reverse,40,call,source)
            need(bx is xx and by is yy and (bx,by) == (ax,ay) and empty == [], 'In-place complete port')
            rx,ry,_,_ = port(bx,by,f,kind,not reverse,40,call,source)
            need((rx,ry) == (x,y), 'Exact dirty-bank return')
            for key in ('data_additions','data_half_shifts','checked_values'):
                port_work[key] = port_work.get(key,0)+t[key]
            port_cases += 1
    e = ((1,0),(0,0),(0,0),(0,0))
    out = block(e,16)
    need(block(tuple(rotate(z,1) for z in e),16) != tuple(rotate(z,1) for z in out),
         'Global phase covariance is absent')
    need(block(out,16) != tuple(reversed(e)), 'Ideal square rewrite is absent')
    rejects(lambda:block(((1,1),)*4,2))
    rejects(lambda:block(((Q(1,2),0),*e[1:]),16))
    rejects(lambda:call([(0,0)]*8,1,1,16))
    rejects(lambda:call([(0,0)]*7,1,0,16))
    rejects(lambda:block(e,16,0))
    same = [(0,0)]*8
    rejects(lambda:port(same,same,1,2,False,16,call,source))
    result = dict(status='PASS_FUSED_GAUSSIAN_ROUNDING', signed_block_cases=cases,
                  maximum_fused_error_squared=Q(new_max,4).__str__(),
                  maximum_source_error_squared=Q(old_max,4).__str__(), source_error_witness=witness,
                  block_work=trace, completed_calls=call_cases, spectator_sums=fibers,
                  complete_ports=port_cases, exact_dirty_returns=port_cases, port_work=port_work,
                  negative_controls=8, scope='Indexed grid kernel and retained ports; no native tariff or kappa')
    if '--write' in sys.argv:
        (P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(result == json.loads((P/'RESULT.json').read_text()), 'Exact result receipt')
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()

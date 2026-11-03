"""Check the optimal fixed-coset table and full retained port calls."""
from collections import Counter
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
sys.path.insert(0,str(P))
from kernel import matrix,multiply,reversed_pairs,block,plan,Table,make_call,retained,need
from optimize import optimize


def authenticate():
    for pin in json.loads((P/'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            path = Path(pin['path']).relative_to('research/three-axis-coset-rounding')
            need(sha256((P/path).read_bytes()).hexdigest() == pin['sha256'], 'Source hash: '+str(path))


def oracle():
    names = {'add','sub','mul','rotate','ideal_pair','norm2','fiber_sums','ideal_call',
             'base_map','ideal_monomial','ideal_port'}
    tree = ast.parse((P/'inputs/oracle.py').read_text())
    tree.body = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    need(len(tree.body) == len(names), 'Exact retained oracle')
    scope = {'F':Q}
    exec(compile(tree,'retained direct matrix oracle','exec'),scope)
    return scope


def rejects(action):
    try: action()
    except ValueError: return
    raise ValueError('Negative control accepted')


def main():
    authenticate();o = oracle();rows = matrix()
    census,blob = optimize()
    if '--write' in sys.argv:
        (P/'CENTERS.json').write_text(json.dumps(census,sort_keys=True,indent=2)+'\n')
        (P/'TABLE.bin').write_bytes(blob)
    else:
        need(json.loads(json.dumps(census)) == json.loads((P/'CENTERS.json').read_text()),'Exact optimal centre census')
        need(blob == (P/'TABLE.bin').read_bytes(),'Exact runtime table')
    table = Table(blob)
    # Check the two algebraic identities over the real integer matrix.
    square = [[sum(rows[i][k]*rows[k][j] for k in range(16)) for j in range(16)] for i in range(16)]
    gram = [[sum(rows[k][i]*rows[k][j] for k in range(16)) for j in range(16)] for i in range(16)]
    need(all(gram[i][j] == 16*(i == j) for i in range(16) for j in range(16)), 'Exact unitarity')
    need(all(square[i][j] == 16*(j == 2*(7-i//2)+i%2) for i in range(16) for j in range(16)), 'Exact permutation square')
    need(all(sum(rows[i][j] for i in range(parity,16,2)) == 4*(j%2 == parity)
             for j in range(16) for parity in (0,1)), 'Exact complex sum')
    counts = Counter();trace = {};rng = random.Random(8036534);worst = 0
    for index,item in enumerate(census['centers']):
        center = item['center']
        # Four times every integer vector lies in K. These large shifts test
        # signed word arithmetic outside the small centre search.
        for trial in range(8):
            x = tuple(a+4*rng.randrange(-10**12,10**12) for a in center)
            values = tuple(zip(x[::2],x[1::2]))
            for sign in (-1,1):
                out = block(values,64,table,sign,trace)
                need(block(out,64,table,-sign) == values,'Exact inverse on every coset')
                out_flat = tuple(v for z in out for v in z)
                target = census['permutation' if sign == 1 else 'inverse'][index]
                need(tuple(v%4 for v in multiply(rows,out_flat)) == tuple(census['centers'][target]['key']), 'Correct output coset')
                image = multiply(rows,x)
                if sign == -1: image = reversed_pairs(image)
                cost = sum((4*a-b)**2 for a,b in zip(out_flat,image))
                expected = table.offset(tuple(item['key']),sign)
                need(cost == sum(v*v for v in expected) <= 64,'Constant all-coset error')
                need(sum(out_flat[::2]) == sum(x[::2]) and sum(out_flat[1::2]) == sum(x[1::2]),'Complex sum')
                worst = max(worst,cost);counts['signed_coset_cases'] += 1
        z = tuple(zip(center[::2],center[1::2]));start = z
        for _ in range(4): z = block(z,16,table)
        need(z == start,'Fourth power')
    need(worst == 64 and trace['data_additions'] == 80*counts['signed_coset_cases']
         and trace['checked_values'] == 144*counts['signed_coset_cases'],'Sharp error and literal work')
    # A separate generating function counts the complete integer search ball.
    coefficients = [1]+[0]*6
    for _ in range(16):
        coefficients = [sum(coefficients[n-k]*weight for k,weight in ((0,1),(1,2),(4,2)) if k<=n)
                        for n in range(7)]
    need(sum(coefficients) == census['enumerated_vectors'] == 700833,'Independent sphere count')
    call = make_call(table);source = retained('rounded');port = retained('ports').port
    norm = lambda v: sum(a*a+b*b for a,b in v)
    error = lambda a,b: norm([(u-x,v-y) for (u,v),(x,y) in zip(a,b)])
    # This rational bound is exact for the tested all-three or all-two plans.
    for f in (1,2,3,4):
        n = 8**f;p = plan(f)
        bound2 = Q(((f+2)//3)**2*n,2)
        for axis,adj in product((0,2),(False,True)):
            values = [(rng.randrange(-9,10),rng.randrange(-9,10)) for _ in range(n)]
            actual = list(values);call(actual,f,axis,40,adj)
            need(error(actual,o['ideal_call'](values,f,axis,adj)) <= bound2,'Whole-call bound')
            need(o['fiber_sums'](actual,f,axis) == o['fiber_sums'](values,f,axis),'Every spectator sum')
            call(actual,f,axis,40,not adj);need(actual == values,'Whole-call inverse')
            counts['complete_calls'] += 1
        if f == 4: continue
        for kind,reverse in product((2,3),(False,True)):
            x = [(rng.randrange(-9,10),rng.randrange(-9,10)) for _ in range(n)]
            y = [(rng.randrange(-9,10),rng.randrange(-9,10)) for _ in range(n)]
            xx,yy = list(x),list(y)
            ax,ay,t,cuts = port(xx,yy,f,kind,reverse,40,call,source,True)
            need(len(cuts) == kind,'Every paid cut')
            for axis,adj,before,after in cuts:
                need(error(after,o['ideal_call'](before,f,axis,adj)) <= bound2,'Actual-input cut bound')
            exact = o['ideal_port'](x,y,f,kind,reverse)
            need(max(error(ax,exact[0]),error(ay,exact[1])) <= 25*bound2,'Complete port bound')
            bx,by,_,empty = port(xx,yy,f,kind,reverse,40,call,source)
            need((bx,by) == (ax,ay) and bx is xx and by is yy and empty == [],'In-place complete port')
            rx,ry,_,_ = port(bx,by,f,kind,not reverse,40,call,source)
            need((rx,ry) == (x,y),'Exact dirty-bank return')
            counts['complete_ports'] += 1
    # Minimise the number of equal-error groups, then their data additions.
    for f in range(1,129):
        p = plan(f);cost = (len(p),5*(p.count(1)+p.count(2))+10*p.count(3))
        for three in range(f//3+1):
            for two in range((f-3*three)//2+1):
                one = f-3*three-2*two
                need((one+two+three,5*(one+two)+10*three) >= cost,'Minimum group count then additions')
    unit = (1,)+(0,)*15
    image = multiply(rows,unit)
    need(all(abs(v) == 1 for v in image),'Unique-nearest collapse witness')
    witness = next(c for c in census['centers'] if c['key'] == [2]*16 or tuple(c['key']) == (2,)*16)
    need(all(v%4 == 2 for v in multiply(rows,witness['center'])), 'Global minimax half-grid witness')
    zero = ((0,0),)*8
    need(block(zero,16,table) == zero,'Zero fixed')
    rejects(lambda:block(((1,1),)*8,2,table))
    rejects(lambda:block(((Q(1,2),0),)+zero[1:],16,table))
    rejects(lambda:Table(blob[:-1]))
    rejects(lambda:table.offset((4,)*16,1))
    rejects(lambda:call([(0,0)]*8,1,1,16))
    result = dict(status='PASS_THREE_AXIS_COSET_ROUNDING',counts=dict(counts),table_bytes=len(blob),
                  complete_center_search=census['enumerated_vectors'],center_costs16=census['center_costs16'],
                  sharp_fixed_coset_error_squared=5,sharp_all_integer_output_error_squared=4,
                  permuted_costs16=census['permuted_costs16'],table_sha256=sha256(blob).hexdigest(),block_work=trace,
                  group_plans_checked=128,negative_controls=5,
                  scope='Sharp uniform eight-point grid error with exact inverse; no native tariff or kappa')
    if '--write' in sys.argv: (P/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else: need(json.loads(json.dumps(result)) == json.loads((P/'RESULT.json').read_text()),'Exact result receipt')
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__': main()

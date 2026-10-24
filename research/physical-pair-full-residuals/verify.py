"""Check the full local residual transfer. Apache-2.0.
Ali Romman with substantial OpenAI Codex assistance.
Source identities retain JoyboyBrian and Dillon's credit.
"""
from fractions import Fraction as F
from pathlib import Path
from hashlib import sha256
from collections import defaultdict
from types import SimpleNamespace
import argparse
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, why):
    if not ok:
        raise ValueError(why)

for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
    if pin['usage'] == 'input':
        need(sha256((ROOT/pin['path']).read_bytes()).hexdigest() == pin['sha256'], 'Source pin')
a = [[F(v) for v in row] for row in json.loads((ROOT/'research/native-center-free-code/CODE.json').read_text())['A']]
normal = json.loads((ROOT/'research/coded-native-caller/NORMALIZERS.json').read_text())
ports, modes = normal['ports'], normal['mode_columns']
sparse = [[(j, v) for j, v in enumerate(row) if v] for row in a]
need(all(sum(abs(v) for _, v in row) == 26 for row in sparse), 'Code row norm')
need(all(a[i][j] == int(i == j)-F(sum(m[i]*m[j] for m in modes), 4)
         for i in range(112) for j in range(112)), 'Actual mode factorization')
need(all(sum(x*y for x,y in zip(m,n)) == 56*(i == j)
         for i,m in enumerate(modes) for j,n in enumerate(modes)), 'Mode Gram')

def add(x, y, sign=1):
    return [(r+sign*u, i+sign*v) for (r,i),(u,v) in zip(x,y)]

def scale(x, c):
    return [(c*r,c*i) for r,i in x]

def phase(x, exponents):
    return [((r,i),(-i,r),(-r,-i),(i,-r))[e%4] for (r,i),e in zip(x,exponents)]

def code(x, inverse=False):
    y = [(sum(v*x[j][0] for j,v in row),sum(v*x[j][1] for j,v in row)) for row in sparse]
    return scale(add(y,scale(x,12)),F(1,13)) if inverse else y

def mv(rows, u):
    return sum(((r&u).bit_count()%2) << i for i,r in enumerate(rows))

def trans(rows):
    return [sum(((r>>i)&1)<<j for j,r in enumerate(rows)) for i in range(9)]

# Independent residuals are inserted after their exact operations.
fibers = [(0,), (1,), (19,), (511,), (0,1), (1,19,256), (17,256,3,98,511)]
zero = [(F(0),F(0))]*112
fixtures = [[(F((j*j+3*s)%29,7+s), F((7*j+s)%19,11+s)) for j in range(112)] for s in range(1,11)]
x,y = fixtures[:2]
controls = {'omit_full_Y': False, 'omit_exit_Q': False, 'wrong_thin_order': False}
cases = 0
for us in fibers:
    chart = [[mv(trans(p['G_rows']), u^p['Z_mask']) for u in us] for p in ports]
    q = [sum(v&1 for v in row) for row in chart]
    d = [sum((v>>1).bit_count() for v in row) for row in chart]
    qi = [-v for v in q]
    need(all((u+v-sum(w.bit_count() for w in us))%4 == 0 for u,v in zip(q,d)), 'Signed DQ phase')
    def terminal(z):
        return phase(code(phase(z,q)),qi)
    for active in range(9):
        e0,bx,by,e1,et,eQ,eC,eL = [v if active == 8 or j == active else zero for j,v in enumerate(fixtures[2:])]
        y1 = add(code(y,True), e0)
        x2 = add(phase(add(x,phase(code(y1),q),-1),d),bx)
        y2 = add(phase(y1,d),by)
        thin = add(phase(add(code(x2,True),e1),qi),et)
        y3 = add(y2,thin)
        out = add(phase(add(code(add(phase(y3,q),eQ)),eC),qi),eL)
        idealx = phase(add(x,phase(y,q),-1),d)
        idealy = phase(phase(x,qi),d)
        dx = add(scale(phase(phase(code(e0),q),d),-1),bx)
        dy = phase(bx,qi)
        for term in (terminal(by), phase(code(e1),qi), terminal(et), phase(code(eQ),qi), phase(eC,qi), eL):
            dy = add(dy,term)
        need(x2 == add(idealx,dx) and out == add(idealy,dy), 'Chronological residual identity')
        controls['omit_full_Y'] |= out != add(idealy,add(dy,terminal(by),-1))
        controls['omit_exit_Q'] |= out != add(idealy,add(dy,phase(code(eQ),qi),-1))
        wrong_thin = add(add(code(phase(x2,qi),True),phase(e1,qi)),et)
        wrong = add(phase(add(code(add(phase(add(y2,wrong_thin),q),eQ)),eC),qi),eL)
        controls['wrong_thin_order'] |= wrong != out
        cases += 1
need(all(controls.values()), 'Semantic controls')

# All actual nonzero blocks satisfy the distinct-port premise.
need(len({p['q'] for p in ports}) == 112, 'Distinct source ports')
for p in ports:
    g = p['G_rows']
    need(mv(g,1) == p['q'], 'Central source port')
    need(all(((r&s).bit_count()%2) == int(i == j) for i,r in enumerate(g) for j,s in enumerate(g)), 'Orthogonal normalizer')
blocks = [(i,j) for i,row in enumerate(a) for j,v in enumerate(row) if v]
for i,j in blocks:
    need(i != j and abs(a[i][j]) == F(1,2), 'Off-diagonal source coefficient')
    need(mv(trans(ports[i]['G_rows']),ports[j]['q']) not in (0,1), 'Four distinct support points')

# Expand the literal four-point formula, including signs, at every address.
def terminal_columns(i,j):
    left,right = ports[i],ports[j]
    out=[]
    for x in range(512):
        u=mv(right['G_rows'],x);v=mv(right['G_rows'],x^1)
        gx=mv(trans(left['G_rows']),u);gy=mv(trans(left['G_rows']),v)
        sign=lambda z: 1-2*(((left['Z_mask']^right['Z_mask'])&z).bit_count()%2)
        sx,sy=sign(u),sign(v)
        column=defaultdict(lambda:(0,0))
        for dst,value in [(gx,(sx,0)),(gy,(0,-sy)),(gx^1,(0,sx)),(gy^1,(sy,0))]:
            old=column[dst];column[dst]=(old[0]+value[0],old[1]+value[1])
        out.append({k:v for k,v in column.items() if v != (0,0)})
    return out
for i,j in (blocks[0],blocks[len(blocks)//2],blocks[-1]):
    columns=terminal_columns(i,j)
    rows=[[] for _ in range(512)]
    for x,col in enumerate(columns):
        need(len(col)==4 and all(abs(r)+abs(v)==1 for r,v in col.values()), 'Literal column norm')
        for dst,z in col.items():rows[dst].append(z)
    need(all(len(row)==4 and sum(abs(r)+abs(v) for r,v in row)==4 for row in rows), 'Literal row norm')
need(all(len(c)==1 for c in terminal_columns(0,0)), 'Diagonal control loses four-point support')
for f in range(1,501):
    B1,B9=2**((f+1)//2),2**((9*f+1)//2)
    need(26*B9+1 < 32*B9, 'X guard')
    need(54*B1+52*2**f+1 < 32*B9, 'Y guard')
    need(2**f <= B9//16, 'All-width comparison control')

# The actual source kernel returns the required error subspace.
path=ROOT/'research/coded-inverse-fixed-grid/kernel.py'
ns={'__name__':'source_kernel','__file__':str(path)}
exec(compile(path.read_bytes(),str(path),'exec'),ns)
kernel=SimpleNamespace(**ns)
for seed in range(1,13):
    values=[((j*j+seed*11)%103)-51 for j in range(112)]
    width=kernel.word_width(51)
    words=[kernel.encode(v,width) for v in values]
    scratch=[[1]*width for _ in range(9)]
    kernel.recode(words,modes,51,scratch)
    err=add([(F(kernel.decode(w)),F(0)) for w in words],code([(F(v),F(0)) for v in values],True),-1)
    need(code(err)==scale(err,-13) and max(abs(r) for r,i in err)<=2, 'Actual inverse residual contract')
    need(all(not any(w) for w in scratch), 'Source scratch return')
result={'status':'PASS_FULL_PAIR_RESIDUAL_TRANSFER','chronological_cases':cases,
        'actual_terminal_blocks':len(blocks),'literal_row_and_column_checks':3*512*2,
        'source_kernel_vectors':12,'guard_widths':500,'controls':controls,
        'terminal_component_norm':'26*2^f','guard':'P=p+ceil(9f/2)+5',
        'provider_accuracy_verified':False,'complete_caller_run':False}
parser=argparse.ArgumentParser();parser.add_argument('--write-result',action='store_true');args=parser.parse_args()
if args.write_result:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
else:need(json.loads((HERE/'RESULT.json').read_text())==result,'Receipt mismatch')
print(json.dumps(result,sort_keys=True))

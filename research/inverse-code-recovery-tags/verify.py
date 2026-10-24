"""Exact inverse tags for the source rounded code.
Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
from types import SimpleNamespace
import json
import argparse

def need(ok, why):
    if not ok: raise ValueError(why)

HERE = Path(__file__).resolve().parent
root = HERE.parents[1]
for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
    if pin['usage'] == 'input':
        need(sha256((root/pin['path']).read_bytes()).hexdigest() == pin['sha256'], 'Declared source pin')

p = root/'research/coded-native-caller/NORMALIZERS.json'
need(sha256(p.read_bytes()).hexdigest() == 'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da', 'Mode source pin')
m = json.loads(p.read_text())['mode_columns']
need(all(sum(a*b for a,b in zip(c,d)) == 56*(i==j)
         for i,c in enumerate(m) for j,d in enumerate(m)), 'Gram')

def rnd(t):
    return (1 if t>=0 else -1)*((abs(t)+26)//52)

def expand(v):
    return [sum(c[i]*z for c,z in zip(m,v)) for i in range(112)]

def forward(x):
    q = [rnd(sum(a*b for a,b in zip(c,x))) for c in m]
    z = expand(q)
    return [a-b for a,b in zip(x,z)], [z%13 for z in q]

def recover_mode(s, tag):
    lo = -((26+s)//4)
    hi = (26-s)//4
    qs = [q for q in range(lo,hi+1) if q%13 == tag and rnd(s+56*q) == q]
    need(len(qs)==1, 'Unique valid quotient')
    return qs[0]

def inverse(y,tags):
    need(len(tags)==8 and all(type(t) is int and 0<=t<13 for t in tags), 'Tags')
    q = [recover_mode(sum(a*b for a,b in zip(c,y)),tag) for c,tag in zip(m,tags)]
    z = expand(q)
    return [a+b for a,b in zip(y,z)]

scalar = 0
for q in range(-200,201):
    for r in range(-26,27):
        t = 52*q+r
        if rnd(t) != q: continue
        need(recover_mode(t-56*q,q%13)==q, 'Scalar inverse')
        scalar += 1
need(sha256((root/'research/coded-inverse-fixed-grid/kernel.py').read_bytes()).hexdigest() == 'bc0e9f705665d6981c0f9176dad0f2d71471735e866c44643cb6835423435303', 'Kernel source pin')
namespace = {'__name__': 'source_kernel', '__file__': str(root/'research/coded-inverse-fixed-grid/kernel.py')}
exec(compile((root/'research/coded-inverse-fixed-grid/kernel.py').read_bytes(), namespace['__file__'], 'exec'), namespace)
kernel = SimpleNamespace(**namespace)
for seed in range(1,41):
    x = [((i*i*seed+7*i+31*seed)%501)-250 for i in range(112)]
    y,tags = forward(x)
    need(inverse(y,tags)==x, 'Whole inverse')
    width=kernel.word_width(250)
    words=[kernel.encode(v,width) for v in x]; scratch=[[0]*width for _ in range(9)]
    kernel.recode(words,m,250,scratch)
    need([kernel.decode(w) for w in words]==y, 'Source kernel agreement')
for v in [-6,-1,0,1,6]:
    for mode in range(8):
        z=[0]*8;z[mode]=v
        x=expand(z);y,tags=forward(x)
        need(y==[0]*112 and inverse(y,tags)==x, 'Zero fiber')
# The scalar condition proves all 13^8 combinations, without a large enumeration.
need(all(rnd(56*v)==v for v in range(-6,7)), 'All zero-fiber scalar choices')
need(2**29 < 13**8 <= 2**30, 'Sharp packed bit count')
# Twelve residue states cannot distinguish the two zero-fiber endpoints.
need((-6)%12==6%12 and rnd(56*-6)==-6 and rnd(56*6)==6, 'Too few states control')
result = {'status':'PASS_SHARP_INVERSE_KERNEL_TAGS','scalar_cases':scalar,
 'actual_kernel_vectors':40,'zero_fiber_size':13**8,'minimum_packed_bits':30,
 'simple_separate_tag_bits':32,'scope':'one scalar coordinate of 112 owners'}
parser = argparse.ArgumentParser()
parser.add_argument('--write-result', action='store_true')
args = parser.parse_args()
if args.write_result:
    (HERE/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
else:
    need(json.loads((HERE/'RESULT.json').read_text()) == result, 'Receipt mismatch')
print(json.dumps(result, sort_keys=True))

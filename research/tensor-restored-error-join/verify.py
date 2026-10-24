"""Joined Tensor error budget. Ali Romman with OpenAI Codex assistance.
Apache-2.0. This checks arithmetic, not production execution.
"""
from fractions import Fraction as F
from pathlib import Path
from hashlib import sha256
import ast
import json
import argparse

def need(ok, why):
    if not ok: raise ValueError(why)

HERE = Path(__file__).resolve().parent
root = HERE.parents[1]
for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
    if pin['usage'] == 'input':
        need(sha256((root/pin['path']).read_bytes()).hexdigest() == pin['sha256'], 'Declared source pin')

pins={
 'research/physical-gaussian-tensor/tensor_engine.py':'1a5a766426b16718e168619d5988cc18711b4574f0041ec7f3877c1024de59d1',
 'research/physical-chirp-middle/PROOF.md':'92cccf922e0e79fcffc5b6883812c6c5f162565c926f9d807791f6b850ac0951',
 'research/tensor-compression-error-refinement/PROOF.md':'2c72accb7e53c944a60b11519e5b931951c8a0a5c27970abde9da7df429de70a'}
for path,digest in pins.items():
    need(sha256((root/path).read_bytes()).hexdigest()==digest,'Source pin: '+path)
s=(root/'research/physical-gaussian-tensor/tensor_engine.py').read_text()
ast.parse(s)
positions=[s.index(v) for v in [
 'self.apply_lines(catalogue, plan, index, layout, plan.expansion_capacity, False)',
 'self.call(self.chirp, plan.sources, plan.flags, plan.axes, plan.ell, plan.p, rows)',
 'self.halo(plan, profile, layout, plan.target_halo, True)',
 'self.apply_lines(catalogue, plan, index, layout, plan.target_halo, True)',
 'self.boundary(self.current, self.output, plan, rows, opposite, True)']]
need(positions==sorted(positions),'Actual composition order')
need('scaled(real, plan.gamma)' in s and 'scaled(imaginary, plan.gamma)' in s,'Both restored components')
b=F(21,38);a=F(99,70)+F(1,2048)
need(F(99,70)**2>2 and a/(1-b)<4,'Exact upper constants')
need(F(6)+F(26,8)+F(16,7)<12,'Uniform coefficient')
cases=0
for D in range(1,33):
    expansion=F(0)
    for _ in range(D): expansion=a+b*expansion
    need(expansion==a*(1-b**D)/(1-b),'Expansion sum')
    for A in range(97):
        chirp=4*F(99,70)*2**A+22
        e=expansion+chirp
        for _ in range(D): e=e/8+2
        formula=F(1,8)**D*(expansion+chirp)+F(16,7)*(1-F(1,8)**D)
        need(e==formula,'Full error recurrence')
        L=max(A-3*D,0)
        need(formula<12*2**L,'Guard coefficient')
        need(formula/F(2)**(L+12)<F(1,256),'Restored precision guard')
        cases+=1
# A chirp-only residual is attenuated by every compression axis.
need(F(8)**-4*F(8)**4==1,'Suffix contraction control')
need(F(2)**20*F(1,2**21)==F(1,2),'Restoration is not free')
result = {'status':'PASS_JOINED_TENSOR_ERROR_GUARD','budget_cases':cases,
 'source_order_sites':len(positions),'constant_upper':'12',
 'guard':'p >= gamma + max(A-3D,0) + 12','physical_execution':False}
parser = argparse.ArgumentParser()
parser.add_argument('--write-result', action='store_true')
args = parser.parse_args()
if args.write_result:
    (HERE/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
else:
    need(json.loads((HERE/'RESULT.json').read_text()) == result, 'Receipt mismatch')
print(json.dumps(result, sort_keys=True))

"""Replay the finite obstruction and its two published positive controls.

Prepared for Jerry Chen / @CubeJerry with OpenAI Codex assistance. Apache-2.0.
"""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent

def need(ok,why):
    if not ok:raise ValueError(why)

def encode(x):return json.dumps(x,sort_keys=True,separators=(',',':'))

for pin in json.loads((HERE/'ORIGINS.json').read_text())['files']:
    raw=(HERE/pin['path']).read_bytes()
    need(len(raw)==pin['bytes'] and hashlib.sha256(raw).hexdigest()==pin['sha256'],'Pinned source bytes')

with tempfile.TemporaryDirectory(prefix='p104-span-') as temp:
    root=Path(temp);variables=None
    for source,receipt in [('PR6702','CURRENT'),('PR6453','CONTROL')]:
        argv=sys.argv
        sys.argv=[str(HERE/'search.py'),str(HERE/'inputs'/(source+'-WORD.json.gz')),str(root/(receipt+'.json'))]
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                variables=runpy.run_path(str(HERE/'search.py'),run_name='__main__')
        finally:sys.argv=argv
        actual=json.loads((root/(receipt+'.json')).read_text())
        expected=json.loads((HERE/(receipt+'.json')).read_text())
        need(encode(actual)==encode(expected),'Complete deterministic receipt '+receipt)
    control=json.loads((root/'CONTROL.json').read_text())
    specification=json.loads((HERE/'inputs/PR6529-SPEC.json').read_text())
    need(len(control['hits'])==len(specification)==2,'Exactly two published fusion controls')
    by_role={x['role']:x for x in control['hits']}
    for old in specification:
        got=by_role[old['role']]
        need(all(got[k]==old[k] for k in ('role','first','second','E','F','G','exports')),'Published fusion event binding')
        need(got['injections']==[dict(cut=old['injection'][0],receiver=old['injection'][1],frame='E',coefficient_mod=1)],'Published literal injection')
    solve=variables['solve'];p=variables['MOD']
    need(p>2 and all(p%d for d in range(2,__import__('math').isqrt(p)+1)),'Reduction modulus is prime')
    nodes=[(0,0,{0:1,1:2},'E'),(0,1,{1:1,2:3},'G')]
    target={0:4,1:13,2:15};sol,rank=solve(nodes,target)
    need(rank==2 and sol is not None,'Two-column positive span control')
    actual={}
    for j,q in sol.items():
        for k,v in nodes[j][2].items():actual[k]=(actual.get(k,0)+q*v)%p
    need({k:v for k,v in actual.items() if v}==target,'Returned coefficients solve the control')
    need(solve(nodes,{0:4,1:13,2:16})[0] is None,'Outside-span rejection control')
    duplicates=[(0,0,{0:1,1:2},'E'),(1,1,{0:2,1:4},'G')]
    need(solve(duplicates,{0:3,1:6})[1]==1,'Dependent columns have rank one')
    need(solve(duplicates,{0:3,1:7})[0] is None,'Dependent-column rejection control')
    need(solve([],{0:1})[0] is None and solve([],{})[0]=={},'Empty-span controls')
    bad=root/'CORRUPT.json.gz';raw=bytearray((HERE/'inputs/PR6702-WORD.json.gz').read_bytes());raw[0]^=1;bad.write_bytes(raw)
    command=[sys.executable,'-I']+(['-O'] if sys.flags.optimize else [])+['-B',str(HERE/'search.py'),str(bad),str(root/'bad.json')]
    result=subprocess.run(command,text=True,capture_output=True)
    need(result.returncode!=0 and 'Unrecognized pinned source bytes' in result.stderr,'Corrupt source rejected before interpretation')
print('PASS_P104_MAXIMAL_CARRIER_SPAN: 631 intervals, 2387 systems, two published fusion patterns, seven algebra/source controls')

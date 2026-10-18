"""Concurrent private-library regression and independent stored-witness audit.
Full declared censuses remain separate required checks.
"""
from pathlib import Path
import hashlib, json, os, platform, random, subprocess, sys, time
P=Path('/tmp/pr-efficient1800'); REPO=Path('/tmp/integer-mult-efficient1100-20261015')
def need(ok,msg):
    if not ok: raise ValueError(msg)
def dp(slots):
    d={(0,0):0}
    for v in slots:
        nxt=dict(d)
        for (m,p),c in d.items():
            k=(m^v,1-p);nxt[k]=min(nxt.get(k,99),c+1)
        d=nxt
    return [d.get((m,0),99) for m in range(32)]
def convolution(a,b):
    d={}
    for x,c in enumerate(a):
        if c>=99: continue
        for y,e in enumerate(b):
            if e<99:d[x^y]=min(d.get(x^y,99),c+e)
    return sum(d[m] for m in range(1,32)) if all(m in d for m in range(1,32)) else None
if len(sys.argv)>1 and sys.argv[1]=='--worker':
    pkg=Path(sys.argv[2]);sys.path.insert(0,str(pkg))
    import dual_lib, independent
    rng=random.Random(int(sys.argv[3]));count=0
    for _ in range(256):
        a=[rng.choice([0,2,4,6,8,99]) for _ in range(32)]
        b=[rng.choice([0,2,4,6,8,99]) for _ in range(32)]
        expected=convolution(a,b)
        need(dual_lib.dual_sum_c(a,b)==expected,'primary C kernel drift')
        need(independent.dual(a,b)==expected,'separate C load drift')
        count+=1
    # Force an uncovered case, which must return None through both wrappers.
    a=[0]+[99]*31
    need(dual_lib.dual_sum_c(a,a) is None and independent.dual(a,a) is None,'uncovered')
    need(dual_lib._dual_c is not None and independent._SO is not None,'unexpected Python fallback')
    print(json.dumps(dict(pid=os.getpid(),cases=count+1,paths=[dual_lib._dual_c._name,independent._SO._name])))
    raise SystemExit
for number in map(int,sys.argv[1:]):
    started=time.monotonic();root=P/'sources'/str(number)
    pkg=next((root/'research').glob('transfer-coupled*'))
    commands=[[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(pkg),str(seed)] for seed in range(4)]
    processes=[subprocess.Popen(c,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for c in commands]
    outputs=[]
    try:
        for child in processes:
            out,err=child.communicate(timeout=40);need(child.returncode==0,err+out);outputs.append(json.loads(out))
    finally:
        for child in processes:
            if child.poll() is None:child.kill();child.wait()
    need(len({r['pid'] for r in outputs})==4,'four separate workers')
    paths=[path for r in outputs for path in r['paths']];need(len(set(paths))==8,'shared build path')
    need(not (pkg/'dual.so').exists(),'package tree build output')
    source=json.loads((pkg/'SOURCES.json').read_text());bindings=0
    for rec in source['files']:
        if rec['usage']!='input':continue
        spec=source['base_commit']+':'+rec['path'];raw=subprocess.check_output(['git','show',spec],cwd=REPO)
        need(raw==(root/rec['path']).read_bytes(),'original input mismatch')
        need(hashlib.sha256(raw).hexdigest()==rec['sha256'],'input SHA')
        need(subprocess.check_output(['git','rev-parse',spec],cwd=REPO,text=True).strip()==rec['git_blob'],'input blob');bindings+=1
    cert=json.loads((pkg/'CERTIFICATE.json').read_text());count=[0]
    def visit(node):
        if isinstance(node,dict):
            if all(k in node for k in ('prefix','suf_a','suf_b','R')):
                pref=node['prefix'];a=node['suf_a'];b=node['suf_b']
                need(convolution(dp(pref+a),dp(pref+b))==node['R'],'stored dual witness')
                count[0]+=1
            for v in node.values():visit(v)
        elif isinstance(node,list):
            for v in node:visit(v)
    visit(cert)
    need(cert['claim']['no_new_kappa'] is True,'scope')
    detail=dict(concurrent_workers=outputs,unique_library_paths=8,original_git_bindings=bindings,stored_witnesses=count[0])
    log=P/f'check-{number}-supplement.log';log.write_text(json.dumps(dict(status='PASS',**detail),sort_keys=True)+'\n')
    receipt=dict(number=number,head=json.loads((P/f'{number}.json').read_text())['headRefOid'],status='passed',seconds=time.monotonic()-started,commands=[dict(argv=c,exit_code=0) for c in commands],input_sha256={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),pkg/'dual.c',pkg/'dual_lib.py',pkg/'independent.py',pkg/'CERTIFICATE.json',pkg/'SOURCES.json']},log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),environment=dict(python=sys.version,platform=platform.platform()),details=detail,scope='Concurrent unique-path builds of unchanged C kernel; independent convolution regression and DP of stored champions; does not replace exhaustive census.')
    (P/f'check-{number}-supplement.json').write_text(json.dumps(receipt,indent=2)+'\n');print(number,'PASS',count[0],'stored witnesses',flush=True)

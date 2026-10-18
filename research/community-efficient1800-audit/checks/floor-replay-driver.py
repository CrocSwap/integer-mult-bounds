import itertools,os,pathlib,subprocess,sys,time,json,hashlib,importlib.metadata
root=pathlib.Path(__file__).resolve().parent
pkg=root/'research/two-sided-ten-term-floor'
logs=root/'maintainer-logs';logs.mkdir(exist_ok=True)
os.environ.update(OMP_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
steps=[('manifest',[str(pkg/'checks/manifest_check.py')]),('clique',['clique.py']),('w16',['witness16.py']),('d9',['diag9.py'])]
steps += [('cb4_'+str(k),['caseb4.py',str(k),'3']) for k in range(3)]
sets=[c for k in range(4) for c in itertools.combinations(range(8),k)]
steps += [('c2_'+str(k),['clique2.py','5',';'.join(','.join(map(str,c)) for i,c in enumerate(sets) if i%4==k)]) for k in range(4)]
steps += [('c24',['clique2.py','4','0,1,2,4']),('d4A',['d4A.py','found_0_1_2_4.pkl']),('d4A2',['d4A2.py']),('d4A3',['d4A3.py']),('vcl_none',['verify_cl.py','']),('vcl_0_1_2',['verify_cl.py','0,1,2']),('vcl_0',['verify_cl.py','0']),('vcl_0_1',['verify_cl.py','0,1']),('sym',['sym.py']),('stab',['stab.py']),('summary',[str(pkg/'checks/check_logs.py'),str(logs)])]
records=[]
print('Dependencies',json.dumps({n:importlib.metadata.version(n) for n in ['numpy','sympy','networkx']}),flush=True)
for name,args in steps:
    start=time.monotonic()
    with (logs/(name+'.log')).open('wb') as out:
        try:r=subprocess.run([sys.executable,'-B',*args],cwd=root,stdout=out,stderr=subprocess.STDOUT,timeout=1200)
        except subprocess.TimeoutExpired:
            print('TIMEOUT',name,'1200s',flush=True);raise SystemExit(124)
    records.append(dict(name=name,argv=[sys.executable,'-B',*args],exit_code=r.returncode,seconds=time.monotonic()-start,timeout_seconds=1200,log_sha256=hashlib.sha256((logs/(name+'.log')).read_bytes()).hexdigest()))
    (root/'maintainer-replay-receipt.json').write_text(json.dumps(records,indent=2)+'\n')
    print(name,'exit',r.returncode,'seconds',round(time.monotonic()-start,3),flush=True)
    if r.returncode:print((logs/(name+'.log')).read_text()[-6000:],flush=True);raise SystemExit(r.returncode)
print((logs/'summary.log').read_text(),flush=True)
print('PASS_COMPLETE_TWO_SIDED_TEN_TERM_FLOOR_REPLAY steps='+str(len(steps)),flush=True)

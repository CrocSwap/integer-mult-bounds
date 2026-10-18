import json,pathlib,subprocess,sys,hashlib,gzip
P=pathlib.Path('/tmp/integer-mult-family588');pk=json.load(open('/tmp/im-k492-packages.json'));n=sys.argv[1];q=pathlib.Path(pk[n]);spec=json.load(open(q/'data/SPEC.json'))
base=pathlib.Path('/tmp/im-k492-replay/pr622') if int(n)>=623 else pathlib.Path('/tmp/im-cold617-replay/pr617')
assert (base/'RECEIPT.json').exists(), 'completed baseline replay required'
localsbase=pathlib.Path('/tmp/im-cold617-replay/pr604') if n=='618' else pathlib.Path('/tmp/im-cold617-replay/pr615') if n=='619' else base
sources={'multicold':P/'research/complex-multicold','structural_gain':P/'research/structural-gain','larger_gain':P/'research/promoted-kernel-coalescing/vendor/larger_gain','joint_prefix':P/'research/complex-joint-prefix','frame_coalescing':P/'research/kernel-frame-coalescing','direct_delivery':P/'research/direct-delivery504-global'}
cmd=[sys.executable,'-B',str(q/'verify.py'),'--work',f'/tmp/im-k492-replay/pr{n}','--jobs','2','--reuse-baseline',str(base/'baseline558')]
for pid,d in spec['providers'].items():
 l=localsbase/(pid+'-local');got=hashlib.sha256(json.dumps(json.loads(gzip.decompress((l/'CANONICAL-WORD.json.gz').read_bytes())),sort_keys=True,separators=(',',':')).encode()).hexdigest();assert got==d['artifact_semantic_sha256']['CANONICAL-WORD.json.gz'],(n,pid,got,d)
 cmd+=['--reuse-local',f'{pid}={l}']
for k in spec['build']['sources']:cmd+=['--source',f'{k}={sources[k]}']
print('RUN',cmd,flush=True);subprocess.run(cmd,check=True)

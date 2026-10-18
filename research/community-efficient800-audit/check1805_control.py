import importlib.util,json,pathlib,hashlib
p=pathlib.Path('/tmp/pr-efficient800/sources/1805/research/h2sem-copyshare-priced/verify.py')
s=importlib.util.spec_from_file_location('reviewed1805',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.check_pins();w=m.load_word();pairs,_=m.nominate_d(w,m.SEED);mut=m.construct_d(w,pairs[:2]);del mut['D'][-1]
try:
 m.semantic_n(mut['D'],w['v'],w['R'])
except ValueError as e:
 if 'helper restoration' not in str(e):raise
 print(json.dumps({'status':'PASS_INDEPENDENT_PARTIAL_RESTORE_REJECTION','exception':str(e),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'The submitted partial-matching control catches its own sentinel ValueError; this independent try/except/else checks that semantic_n itself rejects the mutation.'}))
else:
 raise RuntimeError('Unrestored partial matching accepted')

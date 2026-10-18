import pathlib,subprocess,hashlib,json,time,importlib.util,tempfile,sys
P=pathlib.Path('/tmp/pr-efficient1000');R=pathlib.Path('/tmp/integer-mult-efficient600-20261014');C=P/'combined-tooling';PY='/tmp/pr-efficient200-venv/bin/python'
for path in ['scripts/find_overlap.py','tests/test_research_onboarding.py','research/overlap-path-index/verify.py']:
 f=C/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(subprocess.check_output(['git','show',(':'+path if path=='scripts/find_overlap.py' else 'HEAD:'+path)],cwd=R))
probe=C/'probe_overlap_paths.py';probe.write_text('''import importlib.util,pathlib,tempfile
p=pathlib.Path(__file__).parent/'research/overlap-path-index/verify.py'
s=importlib.util.spec_from_file_location('v',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
with tempfile.TemporaryDirectory() as d:
 cache=pathlib.Path(d)/'cache.json';v.fixture_cache(cache)
 for pattern in ['docs/research/current-status.md','current-status.md','docs/*']:
  r=v.run_cli(cache,['--path',pattern]);assert [x['number'] for x in r['path_matches']]==[4242]
 assert v.run_cli(cache,['--path','no-such-path'])['path_matches_total']==0
 assert [x['number'] for x in v.run_cli(cache,['--path','current-status.md','status rewrite'])['matches']]==[4242]
 assert v.run_cli(cache,['--path','current-status.md','no-such-term'])['matches']==[]
 v.fixture_cache(cache,mutated=True);assert v.run_cli(cache,['--path','current-status.md'])['path_matches_total']==0
 v.fixture_cache(cache,drop_index=True);r=v.run_cli(cache,['--path','current-status.md']);assert r['path_matches_total']==0 and any('pr_files' in w for w in r['warnings'])
print('PASS combined path-index positive, glob, substring, AND, rejection, mutation and missing-index fixtures')
''')
commands=[[PY,'-I','-B','-m','unittest','discover','-s','tests','-p','test_research_overlap_pagination.py','-v'],[PY,'-I','-B','-m','unittest','discover','-s','tests','-p','test_research_onboarding.py','-k','Overlap','-v'],[PY,'-I','-B',str(probe)]]
start=time.time();codes=[]
with (P/'combined1970.log').open('w') as out:
 for cmd in commands:
  out.write(repr(cmd)+'\n');out.flush();q=subprocess.run(cmd,cwd=C,stdout=out,stderr=subprocess.STDOUT);codes.append(q.returncode)
  if q.returncode:break
rec=dict(status='passed' if len(codes)==len(commands) and not any(codes) else 'failed',seconds=time.time()-start,commands=commands,exit_codes=codes,input_sha256={s:hashlib.sha256((C/s).read_bytes()).hexdigest()for s in ['scripts/find_overlap.py','tests/test_research_onboarding.py','research/overlap-path-index/verify.py','probe_overlap_paths.py']},log_sha256=hashlib.sha256((P/'combined1970.log').read_bytes()).hexdigest(),scope='Three-way merged pagination fix retains newer path-index and Unicode work. New and existing Overlap tests plus explicit historical CLI fixture helpers; not the unchanged frozen-source historical verifier.')
(P/'combined1970.json').write_text(json.dumps(rec,indent=2)+'\n');print(rec['status']);assert rec['status']=='passed'

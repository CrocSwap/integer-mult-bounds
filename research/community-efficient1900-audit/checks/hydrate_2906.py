from pathlib import Path
import subprocess,importlib.util,hashlib,json
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'combined-2906'
spec=importlib.util.spec_from_file_location('h',D/'scripts/replay_historical_check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
names={'research/skip-clones/SOURCE.json'}
for route in ['skip-clones-tests',*['legacy-test-'+s for s in ('copied-fixed','copied-fixed-reversed','skip-strips','skip-suffix','pair-assembly','split-skip')]]:
 c=m.CONFIG[route]
 for e in [c,*c.get('additional_inputs',[])]:names.update([e['path'],e['manifest'],e['input'] if e.get('input_from_root') else 'scripts/historical-ci-inputs/'+e['input']])
rows=[]
for rel in sorted(names):
 raw=subprocess.check_output(['git','show','HEAD:'+rel],cwd=R);f=D/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw);rows.append(dict(path=rel,sha256=hashlib.sha256(raw).hexdigest()))
(P/'provenance-2906-hydration.json').write_text(json.dumps(dict(scope='Only missing unchanged current-tree dependencies for all seven historical test routes; no source-pin relaxation.',files=rows),indent=2)+'\n')
for ext in ['json','log']:(P/f'check-2906.{ext}').rename(P/f'check-2906-initial.{ext}')
s=(P/'run_2906.py').read_text();start=s.index('q=[');end=s.index('\nwith (P/',start);s=s[:start]+'''q=[(D,[py,'-I','-O','-B','tests/test_isolated_historical_completion.py','-v'],120,'All seven actual historical overlay tests, including six additional routes'),
(D,[py,'-I','-O','-B','tests/test_isolated_test_cancellation.py','-v'],120,'Current cancellation regressions; native Linux tests skip explicitly'),
(D,[py,'-I','-B',str(P/'baseline_2906.py')],120,'Independent unchanged-baseline falsification: exactly four lifetime assertions must fail')]
'''+s[end:];(P/'run_2906_supplement.py').write_text(s.replace('check-2906.','check-2906-supplement.'))

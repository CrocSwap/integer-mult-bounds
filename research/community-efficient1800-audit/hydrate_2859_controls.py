from pathlib import Path
import subprocess,importlib.util,hashlib,json
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'combined-2859'
def put(rel):
 f=D/rel
 if not f.exists():f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(subprocess.check_output(['git','show','HEAD:'+rel],cwd=R))
for rel in ['tests/test_isolated_historical_completion.py','scripts/run_parallel.py','Makefile','research/partial-swap-digest/verify.py']:
 put(rel)
f=D/'tests/test_isolated_historical_completion.py';s=f.read_text();s=s.replace('def run_case(self, body, *, corrupt=False, fake_wrapper=False):','def run_case(self, body, *, corrupt=False, fake_wrapper=False, route="skip-clones-tests"):\n        pattern = "test_skip_clones.py" if route == "skip-clones-tests" else "test_" + route.removeprefix("legacy-test-").replace("-", "_") + ".py"')
s=s.replace("config = history.CONFIG['skip-clones-tests']\n        with tempfile", "config = history.CONFIG[route]\n        with tempfile")
s=s.replace("config['input'], config['path'], config['manifest']]", "config['input'], config['path'], config['manifest']]\n            for entry in config.get('additional_inputs', []):\n                names.extend([entry['path'], entry['manifest'], entry['input'] if entry.get('input_from_root') else 'scripts/historical-ci-inputs/' + entry['input']])\n            names = list(dict.fromkeys(names))")
s=s.replace("(root/'tests/test_skip_clones.py').write_text(body, encoding='utf-8')", "(root/'tests'/pattern).write_text(body, encoding='utf-8')")
needle='    def test_wrapper_zero_exit_without_child_receipt_rejects(self):'
extra='''    def test_all_new_routes_require_actual_test_completion(self):
        for slug in ('copied-fixed', 'copied-fixed-reversed', 'skip-strips',
                     'skip-suffix', 'pair-assembly', 'split-skip'):
            route = 'legacy-test-' + slug
            with self.subTest(route=route, outcome='complete'):
                r = self.run_case('import unittest\\n', route=route)
                self.assertEqual(r.returncode, 0, r.stderr.decode())
                self.assertIn(('PASS_HISTORICAL_CHECK ' + route).encode(), r.stdout)
            with self.subTest(route=route, outcome='early-exit'):
                r = self.run_case('def load_tests(loader, tests, pattern):\\n raise SystemExit(0)\\n', route=route)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(b'Incomplete unittest run', r.stderr)
                self.assertNotIn(b'PASS all', r.stdout)

'''
assert needle in s;s=s.replace(needle,extra+needle);f.write_text(s)
spec=importlib.util.spec_from_file_location('h',D/'scripts/replay_historical_check.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
for config in h.CONFIG.values():
 for e in [config,*config.get('additional_inputs',[])]:
  for rel in [e['manifest'],e['path'],e['input'] if e.get('input_from_root') else 'scripts/historical-ci-inputs/'+e['input']]:put(rel)
# Exact source guard inspection on working candidate; don't loosen failures.
issues=[]
for key,c in h.CONFIG.items():
 for e in [c,*c.get('additional_inputs',[])]:
  try:h.authenticated_input(D,e,D/'scripts/historical-ci-inputs')
  except Exception as exc:issues.append(dict(package=key,path=e['path'],error=str(exc)))
(P/'finding-2859-candidate-source-gates.json').write_text(json.dumps(dict(scope='Actual candidate historical authentication gates; complete scientific/make replay still separate.',failures=issues),indent=2)+'\n');print('Source-gate issues',issues)
# Track a bounded candidate fixture for actual CLI and published-byte tests.
subprocess.run(['git','init','-q'],cwd=D,check=True)
objects=subprocess.check_output(['git','rev-parse','--git-path','objects'],cwd=R,text=True).strip();obj=(R/objects).resolve() if not Path(objects).is_absolute() else Path(objects)
(D/'.git/objects/info/alternates').write_text(str(obj)+'\n')
subprocess.run(['git','add','.'],cwd=D,check=True);subprocess.run(['git','-c','core.hooksPath=/dev/null','-c','user.name=Review fixture','-c','user.email=fixture@example.invalid','commit','-q','--no-gpg-sign','-m','Unpublished PR2859 compatibility fixture'],cwd=D,check=True)

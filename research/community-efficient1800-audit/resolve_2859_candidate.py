from pathlib import Path
import re,subprocess,json,hashlib
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'combined-2859'
def resolve(text,choice):
 pattern=r'^<<<<<<< [^\n]*\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n'
 out,n=re.subn(pattern,lambda m:choice(m.group(1),m.group(2)),text,flags=re.S|re.M);assert n==1,n;return out
f=D/'scripts/run_isolated_tests.py';s=resolve(f.read_text(),lambda a,b:"                       legacy[path.name], '--completion-receipt', str(receipt)]\n");f.write_text(s)
f=D/'scripts/replay_historical_check.py';s=resolve(f.read_text(),lambda a,b:a+"        if config.get('make_target'):\n            subprocess.run(['make', config['make_target']], cwd=snapshot, env=env, check=True)\n")
s=s.replace('private isolated-runner receipt; skip-clones-tests only','private isolated-runner receipt; historical unittest routes only')
s=s.replace('require(args.completion_receipt is None or args.package == "skip-clones-tests",\n            "completion receipt applies only to skip-clones-tests")','completion_patterns = {"skip-clones-tests": "test_skip_clones.py",\n        **{"legacy-test-" + slug: "test_" + slug.replace("-", "_") + ".py"\n           for slug in ("copied-fixed", "copied-fixed-reversed", "skip-strips",\n                        "skip-suffix", "pair-assembly", "split-skip")}}\n    require(args.completion_receipt is None or args.package in completion_patterns,\n            "completion receipt applies only to historical unittest routes")')
s=s.replace('"-p", "test_skip_clones.py", "-v"]','"-p", completion_patterns[args.package], "-v"]')
s=s.replace('module_command(sys.executable, "tests", "test_skip_clones.py",','module_command(sys.executable, "tests", completion_patterns[args.package],')
f.write_text(s)
f=D/'scripts/verify_pr_reconciliation.py';s=resolve(f.read_text(),lambda a,b:b);s=s.replace("root / 'research/community-efficient1700-audit/DISPOSITIONS.json')","root / 'research/community-efficient1700-audit/DISPOSITIONS.json',\n            root / 'research/community-efficient1800-audit/DISPOSITIONS.json')");f.write_text(s)
# Exact source-context guards must recognize both committed current main and
# the reviewed composed successor; no wildcard or provenance demotion.
for rel,anchor in [('scripts/run_isolated_tests.py','f569b1c287252c698b4d59bc1bd0f013159e772cc3be64e26c4eab8eb99d0478'),('tests/test_isolated_test_runner.py','5c2a715a66c0c87fd672ce46889cb878dd7017a8bfa0c44395b340306b1b5382')]:
 current=subprocess.check_output(['git','show','HEAD:'+rel],cwd=R);candidate=(D/rel).read_bytes();hashes=[hashlib.sha256(b).hexdigest()for b in [current,candidate]]
 for target in ['scripts/replay_historical_check.py','scripts/verify_pr_reconciliation.py']:
  f=D/target;s=f.read_text();assert anchor in s;replacement="', '".join([anchor,*dict.fromkeys(hashes)]);s=s.replace(anchor,replacement);f.write_text(s)
for f in D.rglob('*.py'):
 assert '<<<<<<< ' not in f.read_text();compile(f.read_bytes(),str(f),'exec')
print('Resolved three conflicts preserving completion receipts and round1800 ledger')

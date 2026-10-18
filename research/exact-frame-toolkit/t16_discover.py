"""t16_discover: discovery run of the T16 two-bank chain (same stage commands as gauge44-slots-t16/verify_t16.py) for a
package whose T8 data (data/SPEC-T8.json, data/T8/PLAN.json) is already frozen for a new local word.  T8 stages run strict;
data/PLAN.json is replaced by the lifted PLAN (owners unchanged); SPEC.json is stripped (word-dependent provider keys,
expected block except gain_baseline_kappa) and re-pinned to the new PLAN; bind/emit/audit/invoice/assembly then run with
WITNESS_DISCOVER=1, writing WORK/WITNESS-RECORD.jsonl and WORK/ASSEMBLY.json for unpin + freeze_spec.
usage: python -B t16_discover.py PKG MAIN LOCAL WORK"""
import gzip, hashlib, json, os, shutil, subprocess, sys, time
from pathlib import Path
from rebind import strip_spec
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
rd = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())
PKG, main, local, work = (Path(x).resolve() for x in sys.argv[1:5])
assert not work.exists(); work.mkdir(parents=True)
source = main / 'research/complex-k492-owner-repair/vendor/multicold'; baseline = main / 'research/community-k492-audit/pr622/replay/baseline558'
vendor = source / 'vendor/pr558/vendor/pr552/complex-global/vendor531'
env0 = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0', MULTICOLD_SOURCE=str(source), GAIN_PR564_SOURCE=str(source))
for k in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'): env0.pop(k, None)
SPEC8, SPEC16 = PKG / 'data/SPEC-T8.json', PKG / 'data/SPEC.json'; PLAN8, OWN8 = PKG / 'data/T8/PLAN.json', PKG / 'data/T8/OWNERS.json.gz'
def run(name, script, *args, spec=SPEC16, discover=False):
    t0 = time.monotonic(); log = work / (name + '.log'); env = dict(env0, WITNESS_SPEC=str(spec))
    if discover: env.update(WITNESS_DISCOVER='1', WITNESS_RECORD=str(work / 'WITNESS-RECORD.jsonl'))
    with log.open('w') as s:
        rc = subprocess.run([sys.executable, '-B', str(source / 'code/run_portable.py'), str(script), *map(str, args)], env=env, stdout=s, stderr=subprocess.STDOUT).returncode
    if rc: raise RuntimeError(name + ' failed:\n' + log.read_text(encoding='utf-8', errors='replace')[-6000:])
    print('PASS', name, 'discover' if discover else 'strict', round(time.monotonic() - t0, 2), flush=True)
code, t16 = PKG / 'code', PKG / 't16'
run('restore-parent', code / 'restore_parent.py', '--source', source, '--baseline', baseline, '--out', work / 'parent558', spec=SPEC8)
run('bind8', code / 'bind_providers_portable.py', '--baseline', work / 'parent558', '--provider', 'gauge44=' + str(local), '--plan', PLAN8, '--out', work / 'global8', spec=SPEC8)
run('lift16', t16 / 'lift16.py', work / 'global8/base', PLAN8, OWN8, PKG / 'data/OWNERS.json.gz', work / 'lift', spec=SPEC8)
old = rd(PKG / 'data/PLAN.json'); new = rd(work / 'lift/PLAN.json')
diff = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k)); print('lifted PLAN differs from the old data/PLAN.json in:', diff)
shutil.copyfile(work / 'lift/PLAN.json', PKG / 'data/PLAN.json'); strip_spec(SPEC16, PKG / 'data/PLAN.json')
parent16 = work / 'parent16'; shutil.copytree(work / 'parent558', parent16)
shutil.copyfile(work / 'lift/GLOBAL-TEMPLATE.json.gz', parent16 / 'complex-global/base/split-centres/GLOBAL-TEMPLATE.json.gz')
g = work / 'global'
run('bind', code / 'bind_providers_portable.py', '--baseline', parent16, '--provider', 'gauge44=' + str(local), '--plan', PKG / 'data/PLAN.json', '--out', g, discover=True)
run('emit', code / 'emit_allcold.py', '--base', g / 'base', '--owners', PKG / 'data/OWNERS.json.gz', '--plan', g / 'PLAN.json', '--out', g / 'hosted', discover=True)
run('audit', code / 'audit_allcold.py', g / 'base', g / 'hosted', g / 'audit/ASYNC-AUDIT.json', '--mutation-controls', discover=True)
run('invoice', code / 'invoice_allcold.py', '--base', g / 'base', '--hosted', g / 'hosted', '--audit', g / 'audit', '--out', g / 'audit',
    '--retained-invoice', vendor / 'evidence/audit/PREFIX-AND-INVOICE.json', discover=True)
run('assembly', code / 'assemble.py', source, g, work / 'ASSEMBLY.json', discover=True)
a = rd(work / 'ASSEMBLY.json'); print(a['status'], a['kappa_decimal'], 'profile', a['complex_profile'])

#!/usr/bin/env python3
"""Verify from scratch: PR2260's supplier (vendored at its head commit) + certified fine endpoint + PR1673 capped phase-cell
fusion outer with retuned strict slacks (the PR2220 retune method).

Steps
 1. MANIFEST.json: every package file's SHA-256.
 2. Supplier replay = the steps of vendor/pr2260-selective-borrowing-kappa/verify.py (local natives, owners, independent
    family audit, finite invoice, exact arithmetic incl. PR2260's own 47-row outer), run unmodified from the vendored copy.
    One deviation, stated: PR2260's independent receipt pins the SHA-256 of a gzip.compress(...) byte stream, which depends on
    the zlib build; here every other receipt key must equal PR2260's EXPECTED.json and the UNCOMPRESSED payload is pinned
    (SUPPLIER-BINDING.json).
 3. Binding: PR2260's recounted global profile, live stock and bit endpoint equal this package's SPEC.json.
 4. certify_endpoint.py: complex endpoint C to 10^-200 (native and conservative moments < 1 at C; conservative > 1 at C+10^-200).
 5. outer/run_outer.py: regenerates LEDGER.json / INDEPENDENT.json byte-identically and replays the supplier-independent
    PR1673 / PR2220 outer evidence (needs numpy and SymPy, as PR2220).
usage: python3 -B verify.py [--skip-supplier]   (assertions must be enabled)
"""
import gzip, hashlib, json, subprocess, sys, tempfile
from fractions import Fraction as Q
from pathlib import Path
sys.set_int_max_str_digits(0)
if not __debug__: raise RuntimeError('Assertions must be enabled')
HERE = Path(__file__).resolve().parent
SUP = HERE / 'vendor/pr2260-selective-borrowing-kappa'
def need(ok, why):
    if not ok: raise SystemExit('FAIL: ' + why)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p): return json.loads(Path(p).read_bytes())

man = rd(HERE / 'MANIFEST.json')['sha256']
files = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
need(files == set(man) | {'MANIFEST.json'}, 'package contains missing or undeclared files')
need(all(sha(HERE / k) == v for k, v in man.items()), 'package file SHA-256 differs')
print('PASS_MANIFEST', len(man))

spec = rd(HERE / 'SPEC.json'); bind = rd(HERE / 'SUPPLIER-BINDING.json')
need(sha(SUP / 'MANIFEST.json') == bind['pr2260_manifest_sha256'], 'vendored PR2260 manifest differs')
with tempfile.TemporaryDirectory(prefix='pr2260-retune-') as d:
    work = Path(d)
    if '--skip-supplier' not in sys.argv[1:]:
        def command(script, *args):
            subprocess.run([sys.executable, '-I', '-O', '-B', str(SUP / script), *map(str, args)], check=True, timeout=900)
        command('local/verify.py', '--out', work / 'LOCAL.json')
        command('owners/verify.py', '--out', work / 'owners')
        # PR2260 independent family audit, run through its own audit.audit with its own arguments
        sys.path.insert(0, str(SUP / 'independent'))
        import importlib.util, types
        for rel, pin in rd(SUP / 'independent/SOURCES.json').items():
            need(sha(SUP / rel) == pin, 'PR2260 independent source differs: ' + rel)
        spec_a = importlib.util.spec_from_file_location('pr2260_independent_audit', SUP / 'independent/audit.py')
        audit = importlib.util.module_from_spec(spec_a); sys.modules[spec_a.name] = audit; spec_a.loader.exec_module(audit)
        R = SUP
        args = types.SimpleNamespace(parent=R / 'independent/inputs/T8-PARENT.json.gz',
            parent_sha256='025448abdf2012d327e50a009084e1501690d05e650300d2982836aa0350ae00',
            phases=R / 'owners/inputs/DATA-PHASES.json', plan=R / 'owners/inputs/PLAN.json', owners=R / 'owners/OWNERS.json.gz',
            forward_trace=R / 'local/data/forward.json', backward_trace=R / 'local/data/backward.json',
            forward_native=R / 'local/data/native-forward.json.gz', backward_native=R / 'local/data/native-backward.json.gz',
            forward_wrapper=R / 'local/data/wrappers-forward.json', backward_wrapper=R / 'local/data/wrappers-backward.json',
            engine=R / 'local/vendor/native_verify.py', out=work / 'independent')
        audit.audit(args)
        actual = rd(work / 'independent/RESULT.json'); expected = rd(SUP / 'independent/EXPECTED.json')
        for k, v in expected.items():
            if k == 'actual_factors_sha256': continue
            need(actual.get(k) == v, 'PR2260 independent receipt differs: ' + k)
        payload = hashlib.sha256(gzip.decompress((work / 'independent/ACTUAL-FAMILY-FACTORS.json.gz').read_bytes())).hexdigest()
        need(payload == bind['independent_actual_factors_uncompressed_sha256'], 'PR2260 family-factor payload differs')
        print('PASS_PR2260_INDEPENDENT (all receipt keys; uncompressed factor payload pinned)')
        command('local/invoice.py', '--variant', SUP / 'local/data', '--owners', SUP / 'owners/OWNERS.json.gz', '--out', work / 'INVOICE.json')
        need(rd(work / 'INVOICE.json') == rd(SUP / 'local/data/finite-invoice.json'), 'fresh finite invoice differs')
        command('arithmetic/verify.py', '--out', work / 'ARITHMETIC.json')
        local = rd(work / 'LOCAL.json'); owner = rd(work / 'owners/OWNERS-RECEIPT.json'); inv = rd(work / 'INVOICE.json'); ar = rd(work / 'ARITHMETIC.json')
        need(local['source_hashes']['forward_trace'] == owner['source_trace_sha256'], 'local and owner word differ')
        need(owner['owners_sha256'] == inv['owner_table_sha256'], 'owner and finite invoice differ')
        need(ar['source_sha256']['owners/OWNERS.json.gz'] == owner['owners_sha256'], 'arithmetic owner differs')
        need(ar['profile'] == owner['profile'] == actual['complete_profile'], 'complete paid profiles differ')
        need(ar['kappa'] == '3361/2000000', 'PR2260 supplier kappa differs')
        # 3. binding to this package
        need({str(k): v for k, v in ar['profile'].items()} == spec['expected']['global_profile'], 'SPEC profile is not PR2260 recount')
        need(Q(ar['inherited_bit_saving']) == Q(spec['supplier']['bit_lower']), 'bit endpoint differs')
        print('PASS_PR2260_SUPPLIER_REPLAY_AND_BINDING')
    else:
        print('SKIPPED supplier replay (--skip-supplier)')
    need(rd(SUP / 'arithmetic/EXPECTED.json')['profile'] == spec['expected']['global_profile'], 'SPEC profile differs from PR2260 EXPECTED')
    subprocess.run([sys.executable, '-B', str(HERE / 'certify_endpoint.py')], check=True)
    subprocess.run([sys.executable, '-B', str(HERE / 'outer/run_outer.py'), str(work / 'outer')], check=True)
led = rd(HERE / 'outer/LEDGER.json')
row = led['rows']['struct_boundary_radix_union']
k = row['kappa']['decimal']
kq = Q(row['kappa']['rational'])
need(kq == Q(rd(HERE / 'ENDPOINT.json')['complex_lower']) - Q(1, 10 ** 246) - Q(1, 10 ** 222), 'kappa is not C - 1/F - B')
print('PASS_COMPLETE  kappa =', k[:60], '...')
print('  over PR2260 (3361/2000000): +%.6f%%' % float((kq / Q(3361, 2000000) - 1) * 100))
print('  over PR2220: +%.6f%%' % float((kq / Q('0.0016797549561255445213356709939207025769983114385025802954603275201628645482603256388263') - 1) * 100))

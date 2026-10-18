"""Reproduce inherited global acceptance of a semantically invalid overlay.

No WITNESS_DISCOVER mode; the only runtime edits are fully specified and
before/after hashed in LEGACY-PATCHES.json. Frozen inputs stay untouched.
"""
import gzip
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
import core as C
import overlay


def extract(path, out):
    out.mkdir()
    with tarfile.open(path) as archive:
        seen = set()
        for member in archive.getmembers():
            p = Path(member.name)
            C.need(not p.is_absolute() and '..' not in p.parts and member.name not in seen,
                   'unsafe or duplicate archive path')
            C.need(member.isfile() or member.isdir(), 'nonregular archive entry')
            seen.add(member.name)
        archive.extractall(out, filter='data')


def apply_patches(source):
    records = C.read(C.PACKAGE/'LEGACY-PATCHES.json')['patches']
    C.need({r['path'] for r in records} == {'code/audit_allcold.py', 'code/assemble.py'}, 'patch inventory')
    for record in records:
        path = source/record['path']
        C.need(C.sha(path) == record['before_sha256'], 'unexpected inherited source')
        text = path.read_text()
        for old, new in record['replacements']:
            C.need(text.count(old) == 1, 'patch hunk absent or ambiguous')
            text = text.replace(old, new)
        C.need(hashlib.sha256(text.encode()).hexdigest() == record['after_sha256'], 'patch result digest')
        path.write_text(text)
    return {r['path']: r['after_sha256'] for r in records}


def run(work, frames, profile, prices):
    C.need(__debug__, 'full inherited checks require assertions')
    C.need(not work.exists(), 'full work directory already exists')
    work.mkdir(parents=True)
    source, replay = work/'source', work/'replay'
    extract(C.ROOT/C.SOURCE, source)
    extract(C.ROOT/C.REPLAY, replay)
    (source/'engines').mkdir(exist_ok=True)
    for name in ('moment', 'base_two_moment', 'outer'):
        shutil.copyfile(C.ROOT/(C.ENGINES+name+'.py'), source/'engines'/(name+'.py'))
    shutil.copyfile(C.ROOT/C.OLD_BIT, source/'inputs/PR543-EXPECTED.json')
    global_base = replay/'candidate/strict/global'
    base = global_base/'base'
    for name in ('SPEC.json', 'PLAN.json', 'OWNERS.json.gz'):
        shutil.copyfile(C.ROOT/(C.DATA+name), source/'data'/name)
    C.need(C.sha(source/'inputs/PR589-EXPECTED.json') == C.sha(C.ROOT/C.BIT), 'archived bit input mismatch')
    env = dict(os.environ)
    for key in ('WITNESS_DISCOVER', 'WITNESS_RECORD', 'PYTHONOPTIMIZE'):
        env.pop(key, None)
    env['WITNESS_SPEC'] = str(source/'data/SPEC.json')
    env['GAIN_PR564_SOURCE'] = str(source)
    timings = []

    def command(name, script, *args):
        start = time.monotonic()
        log = work/(name+'.log')
        with log.open('w') as f:
            r = subprocess.run([sys.executable, '-B', str(script), *map(str, args)],
                               cwd=work, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=300)
        timings.append(dict(stage=name, seconds=time.monotonic()-start, exit_code=r.returncode))
        C.write(work/'TIMINGS.json', timings)
        if r.returncode:
            raise ValueError(name+' failed:\n'+'\n'.join(log.read_text().splitlines()[-25:]))
        print('PASS_FULL_STAGE '+name, flush=True)

    baseline = work/'baseline-hosted'
    command('baseline-emission', source/'code/emit_allcold.py', '--base', base,
            '--owners', source/'data/OWNERS.json.gz', '--plan', global_base/'PLAN.json', '--out', baseline)
    (work/'baseline-audit').mkdir()
    command('baseline-controller', source/'code/audit_allcold.py', base, baseline,
            work/'baseline-audit/ASYNC-AUDIT.json')
    baseline_checks = {}
    for name in overlay.NAMES:
        a, b = C.read(baseline/name), C.read(global_base/'hosted'/name)
        C.need(C.canonical(a) == C.canonical(b), 'fresh baseline semantic mismatch: '+name)
        baseline_checks[name] = C.digest(a)
    C.write(work/'BASELINE-REPLAY.json', baseline_checks)
    candidate = work/'candidate'
    candidate.mkdir()
    hosted, audit = candidate/'hosted', candidate/'audit'
    audit.mkdir()
    phases = base/'work/complex-nine-native/DATA-PHASES.json'
    own = source/'data/OWNERS.json.gz'
    independent = overlay.emit(baseline, hosted, frames, profile, phases, own)
    C.write(work/'OVERLAY-AUDIT.json', independent)
    spec = C.read(source/'data/SPEC.json')
    spec['name'] += ' + exact simultaneous idle reassignment'
    x = spec['expected']
    x['global_profile'] = {str(r): n for r, n in profile.items()}
    from collections import Counter
    x['idle_remainder_profile'] = {str(r): n for r, n in sorted(Counter(r['rank'] for r in frames).items())}
    x.update(complex_lower=prices['native']['endpoint'], conservative_complex_lower=prices['conservative']['endpoint'],
             kappa=prices['native']['kappa'], kappa_decimal=prices['native']['kappa_decimal'].rstrip('0'),
             conservative_kappa_decimal=prices['conservative']['kappa_decimal'].rstrip('0'))
    C.write(source/'data/SPEC.json', spec)
    C.write(work/'CANDIDATE-SPEC.json', spec)
    patched = apply_patches(source)
    env.update(T16_BASE_HOSTED=str(baseline), IDLE_VERIFY_SCRIPT=str(C.PACKAGE/'overlay.py'),
               IDLE_OWNERS_PATH=str(own))
    command('candidate-controller-controls', source/'code/audit_allcold.py', base, hosted,
            audit/'ASYNC-AUDIT.json', '--mutation-controls')
    command('fresh-invoice', source/'code/invoice_allcold.py', '--base', base, '--hosted', hosted,
            '--audit', audit, '--out', audit,
            '--retained-invoice', source/'evidence/audit/PREFIX-AND-INVOICE.json')
    command('strict-assembly', source/'code/assemble.py', source, candidate, candidate/'ASSEMBLY.json')
    for script, name in (('assembly_controls.py', 'assembly-controls'), ('bit_supplier_controls.py', 'bit-controls')):
        command(name, source/'code'/script, '--source-package', source, '--owner', audit/'OWNERS-AND-PROFILE.json',
                '--invoice', audit/'PREFIX-AND-INVOICE.json', '--out', work/(name+'.json'))
    # Recheck serialized artifacts after legacy checks; none may drift between checks.
    C.need(independent == overlay.check(baseline, hosted, phases, own), 'overlay drift during legacy checks')
    assembled = C.read(candidate/'ASSEMBLY.json')
    from fractions import Fraction as Q
    C.need(Q(assembled['kappa']) == Q(prices['native']['kappa']) and
           Q(assembled['conservative_kappa']) == Q(prices['conservative']['kappa']), 'assembly/pricing disagreement')
    controller = C.read(audit/'ASYNC-AUDIT.json')
    assembly_controls = C.read(work/'assembly-controls.json')
    bit_controls = C.read(work/'bit-controls.json')
    invoice = C.read(audit/'PREFIX-AND-INVOICE.json')
    receipt = dict(status='PASS_LEGACY_CHECKS_ACCEPT_INVALID_OVERLAY', admitted=False,
        baseline_semantic_hashes=baseline_checks, overlay=independent,
        patched_source_sha256=patched, spec_sha256=C.digest(spec),
        kappa=assembled['kappa'], conservative_kappa=assembled['conservative_kappa'],
        controller_controls=len(controller['mutations_rejected']),
        assembly_controls=len(assembly_controls['rejected_controls']),
        bit_controls=len(bit_controls['rejected_controls']),
        outer_constraints=len(assembled['outer']), conservative_outer_constraints=len(assembled['conservative_outer']),
        finite=invoice['finite'], global_prefix_bits=invoice['global_prefix_bits'],
        charged_prefix_bits=invoice['charged_prefix_bits'], strict_checks=invoice['strict_checks'],
        reused='Pinned selected local/native/bit source artifacts; no fresh local native or bit circuit rebuild')
    C.need(receipt['controller_controls'] == 15 and receipt['assembly_controls'] == 69 and receipt['bit_controls'] == 12,
           'inherited control coverage changed')
    C.write(work/'RECEIPT.json', receipt)
    return receipt

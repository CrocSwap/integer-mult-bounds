"""Reconstruct the T16 owner map from the selected PR1094 map and DIFF-vs-selected.json, run the
unchanged strict T16 admission, then the independent seed67 owner audit, exact pricing and PR1069 sweep,
and finally the proved packing ceiling (ceiling_bound.py)."""
from decimal import Decimal
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile

if not __debug__:
    raise RuntimeError('Assertions must remain enabled')
P = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
CONTROLS = dict(admission=69, bit_supplier=12, independent_t16=6, controller_mutations=15)
KAPPA_DECIMAL = '0.001673614205725695'
SIGMAS = 10011


def run(main, work):
    pins = json.loads((P/'INPUTS.json').read_text())
    for name, h in pins.items():
        assert sha(main/name) == h, 'Changed dependency: '+name
    package_pins = json.loads((P/'MANIFEST.json').read_text())
    actual = {f.relative_to(P).as_posix(): sha(f) for f in P.rglob('*')
              if f.is_file() and f != P/'MANIFEST.json' and '__pycache__' not in f.parts}
    assert actual == package_pins, 'Package inventory mismatch'

    # 1. Byte-exact PLAN/SPEC and content-exact OWNERS from selected PR1094 + DIFF.
    modspec = importlib.util.spec_from_file_location('t16_owner_build', P/'build.py')
    mod = importlib.util.module_from_spec(modspec)
    modspec.loader.exec_module(mod)
    blobs = mod.derive(main)
    for name, b in zip(('OWNERS.json.gz', 'PLAN.json', 'SPEC.json'), blobs):
        assert b == (P/'data'/name).read_bytes(), 'Reconstruction mismatch: '+name

    # 2. Unchanged PR1087 strict verifier on the overlaid data.
    source = work/'source'
    source.mkdir(parents=True)
    archive = main/'research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz'
    with tarfile.open(archive) as t:
        for m in t.getmembers():
            assert m.isfile() and (source/m.name).resolve().is_relative_to(source.resolve())
        t.extractall(source, filter='data')
    original = json.loads((source/'MANIFEST.json').read_text())
    assert {f.relative_to(source).as_posix(): sha(f) for f in source.rglob('*')
            if f.is_file() and f != source/'MANIFEST.json'} == original
    for name in ('OWNERS.json.gz', 'PLAN.json', 'SPEC.json'):
        shutil.copyfile(P/'data'/name, source/'data'/name)
    local = work/'local'
    local.mkdir()
    local_pins = json.loads((P/'LOCAL-PINS.json').read_text())
    with tarfile.open(main/'research/community-frontier1094-audit/selected-replay.tar.gz') as t:
        prefix = 'candidate/strict/global/base/providers/gauge44/'
        for name, h in local_pins.items():
            member = t.getmember(prefix+name)
            assert member.isfile()
            b = t.extractfile(member).read()
            assert hashlib.sha256(b).hexdigest() == h
            (local/name).write_bytes(b)
    # No discovery, source reconstruction, optimizer, credential environment,
    # or native cold rebuild. The full controller and invoice are regenerated.
    env = {k: os.environ[k] for k in ('PATH', 'SYSTEMROOT', 'WINDIR', 'TMPDIR', 'TEMP', 'TMP') if k in os.environ}
    env.update(PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    subprocess.run([sys.executable, '-E', '-S', '-B', str(source/'verify_t16.py'),
                    '--main', str(main), '--local', str(local), '--work', str(work/'strict')], env=env, check=True)
    result = json.loads((work/'strict/REPLAY.json').read_text())
    target = json.loads((P/'CANDIDATE.json').read_text())
    assert result['status'] == 'PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY'
    assert result['kappa'] == target['expected_updates']['kappa']
    # Decimal comparisons throughout: the native assembler and the SPEC may differ only in trailing zeros.
    assert Decimal(result['conservative_kappa_decimal']) == Decimal(target['expected_updates']['conservative_kappa_decimal'])
    assert result['complex_profile'] == target['expected_updates']['global_profile']
    assert result['idle_remainder_profile'] == target['expected_updates']['idle_remainder_profile']
    assert result['actual_73_axis_charts'] == target['expected_updates']['actual_73column_sigmas'] == SIGMAS
    assert result['controls'] == CONTROLS

    # 3. Independent seed67 owner audit, pinned-engine pricing and PR1069 sweep.
    subprocess.run([sys.executable, '-I', '-B', str(P/'check.py'), '--main', str(main),
                    '--replay', str(work/'strict'), '--out', str(work/'CHECK.json')], env=env, check=True)
    check = json.loads((work/'CHECK.json').read_text())
    assert Decimal(check['price_new']['kappa_decimal']) == Decimal(result['kappa_decimal']) == Decimal(KAPPA_DECIMAL)
    assert check['majorization']['candidate_majorizes_selected'] is True
    assert check['changed_rows'] == mod.CHANGED_ROWS and len(check['relocated_rows']) == mod.RELOCATED_ROWS

    # 4. Proved packing ceiling (PROOF.md): exact integer checks, standard library only.
    subprocess.run([sys.executable, '-I', '-B', str(P/'ceiling_bound.py'), '--data', str(P/'data'),
                    '--out', str(work/'CEILING.json')], env=env, check=True)
    ceiling = json.loads((work/'CEILING.json').read_text())
    assert ceiling['theorem1']['slack_total'] == 180832 and ceiling['theorem1']['max_empty_cap48'] == 4887
    assert Decimal(ceiling['theorem3']['bound_decimal']) == Decimal('908139.013')
    assert ceiling['this_map']['empty_cap48'] == check['candidate']['idle'].get('48', check['candidate']['idle'].get(48))
    for name, h in pins.items():
        assert sha(main/name) == h
    print('PASS_T16_OWNER_MAP', result['kappa_decimal'], result['idle_remainder_profile'],
          'changed', check['changed_rows'], 'relocated', len(check['relocated_rows']),
          'ceiling: empty cap-48 <=', ceiling['theorem1']['max_empty_cap48'], 'E <=', ceiling['theorem3']['bound_decimal'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, default=P.parents[1])
    ap.add_argument('--work', type=Path)
    args = ap.parse_args()
    if args.work:
        args.work.mkdir(parents=True, exist_ok=False)
        run(args.main.resolve(), args.work.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='two-stage-cycles-') as d:
            run(args.main.resolve(), Path(d))

"""Reconstruct #8073's source and apply the Gaussian envelope successor.

The bundled #8073 source/peer archive is not modified.  This script only
creates its own candidate tree and updates SHA-256 image checks for the
changed terminal profile and proof files.
"""

from hashlib import sha256
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SOURCE, DEST = ROOT / 'source8073', ROOT / 'combined'
OVERLAY = ROOT / 'overlay'
OLD = 'TERMINAL = Profile((8192, 117168, 524288), 501831, Q(".003898219753506"))'
NEW = 'TERMINAL = Profile((8192, 121057, 524288), 496174, Q(".003898221247474783"))'


def replace(path, before, after):
    data = path.read_text()
    if data.count(before) != 1:
        raise ValueError(f'{path.name}: expected exactly one {before!r}')
    path.write_text(data.replace(before, after))


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    if DEST.exists():
        raise RuntimeError(f'Candidate already exists at {DEST}; preserve it or remove it explicitly')
    DEST.mkdir()
    source = runpy.run_path(str(SOURCE / 'verify.py'))
    peer = source['restore'](DEST)
    runpy.run_path(str(SOURCE / 'prepare.py'))['materialize'](peer)
    for name in ('check_cutoff.py', 'check_stage_seam.py', 'check_ordinary_floor.py'):
        shutil.copyfile(SOURCE / name, peer / name)

    # Bootstrap the exact predecessor once, before changing the new profile,
    # to authenticate and derive the expected post-installation image hash.
    baseline = DEST / 'baseline-runtime'
    subprocess.run([sys.executable, '-IB', str(peer/'bootstrap.py'), str(baseline)], check=True)
    baseline_image = (baseline/'installations.py').read_text()
    assert baseline_image.count(OLD) == 1
    new_image_hash = sha256(baseline_image.replace(OLD, NEW).encode()).hexdigest()
    replace(peer/'runtime.patch', OLD, NEW)
    for name in ('weighted_suffix.py', 'independent_gaussian.py', 'check_combined_seams.py'):
        shutil.copyfile(OVERLAY/name, peer/name)

    positive = peer/'positive_debit.py'
    replace(positive, 'POSITIVE_DEBIT = Q(64939, 524288)',
            'POSITIVE_DEBIT = Q(130699669, 2**30)')
    replace(positive, 'from grades import UPPER_DIVISOR',
            'from grades import UPPER_DIVISOR\nfrom weighted_suffix import upper_numerator')
    replace(positive, 'fringe = 10 * target_axes / (t * psi)',
            'fringe = upper_numerator(recipe, lower, intervals) / (t * psi)')
    replace(positive, 'assert fringe < Q("7.335168")',
            'assert Q("4.550681") < fringe < Q("4.550682")')

    receipt = peer/'receipt.py'
    for old,new in (
        ('DEBIT = Q(64939, 2**19)', 'DEBIT = Q(130699669, 2**30)'),
        ('assert cost == 318291911 and premium == 517',
         'assert cost == 318291851 and premium == 516'),
        ('(516570, 501831)', '(516861, 496173)'),
        ('older = Q(".003898214283192")', 'older = Q(".003898219753506")'),
        ('assert gain == Q(2735157, 500000000000000)',
         'assert gain == Q(1493968783, 1000000000000000000)'),
    ):
        replace(receipt, old, new)

    independent = peer/'independent_price.py'
    text = independent.read_text()
    first, last = text.index('def weighted():'), text.index('def ordinary_debit():')
    text = (text[:first] + 'def weighted():\n'
            '    sys.path.insert(0, str(Path(__file__).resolve().parent))\n'
            '    from independent_gaussian import verify\n'
            '    verify(prepare_native(TERMINAL)[-1], powers)\n\n\n' + text[last:])
    independent.write_text(text)
    replace(independent, 'TERMINAL.kappa - peer == Q("0.000000018139806")',
            'TERMINAL.kappa - peer == Q(19633774783, 1000000000000000000)')
    replace(peer/'check_cutoff.py', 'assert heights == (1024, 501831)',
            'assert heights == (1024, 496174)')
    for old,new in (
        ('TERMINAL.rank_logs==(8192,117168,524288) and TERMINAL.complex_log==501831',
         'TERMINAL.rank_logs==(8192,121057,524288) and TERMINAL.complex_log==496174'),
        ('(a[-1].rank_log,b[-1].rank_log)==(1024,501831)',
         '(a[-1].rank_log,b[-1].rank_log)==(1024,496174)'),
    ):
        replace(peer/'check_ordinary_floor.py', old, new)
    replace(peer/'verify.py', '"check_stage_seam.py"', '"check_combined_seams.py"')
    # The appendix rebuild does not run product; it retains the upstream verifier.

    manifest = json.loads((peer/'SOURCES.json').read_bytes())
    manifest['runtime_images']['installations.py']['after'] = new_image_hash
    for name in ('runtime.patch', 'positive_debit.py', 'receipt.py', 'independent_price.py',
                 'weighted_suffix.py', 'independent_gaussian.py', 'check_combined_seams.py',
                 'check_cutoff.py', 'check_ordinary_floor.py', 'check_stage_seam.py', 'verify.py'):
        manifest['local_sources'][name] = sha(peer/name)
    (peer/'SOURCES.json').write_text(json.dumps(manifest, indent=2)+'\n')

    runtime = DEST/'runtime'
    subprocess.run([sys.executable, '-IB', str(peer/'bootstrap.py'), str(runtime)], check=True)
    receipt = subprocess.run([sys.executable, '-IB', str(peer/'receipt.py'), str(runtime)],
                             check=True, capture_output=True, text=True)
    result = json.loads(receipt.stdout)
    (peer/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    (ROOT/'RESULT-8073.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS_SOURCE_RECONSTRUCTION', peer, 'profile_sha256', new_image_hash)
    print('PASS_COMBINED_RECEIPT', result['terminal']['kappa'], result['complete_log2_C'])


if __name__ == '__main__':
    main()

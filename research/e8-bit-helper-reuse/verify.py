"""Fresh source-bound E8 retiming, helper reuse and exact assembly replay.

Usage: python3 -B verify.py /fresh/output [--parent ../e8-bit-seven-stage]
Requires Python 3.11+, numpy, sympy, mpmath, bash, GNU g++ C++17/Boost, sha256sum.
Prepared with OpenAI Codex assistance. Apache-2.0. No network is needed.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction
import argparse
import gzip
import json
import os
import subprocess
import sys
import frame_replay
import reuse_replay

assert __debug__, 'Assertions are required; do not use -O'
HERE = Path(__file__).resolve().parent


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def manifest(directory):
    entries = []
    for line in (directory / 'MANIFEST.sha256').read_text().splitlines():
        want, relative = line.split(None, 1)
        relative = relative.strip().removeprefix('./')
        target = directory / relative
        assert target.resolve().is_relative_to(directory.resolve())
        assert digest(target) == want, ('manifest mismatch', relative)
        entries.append(relative)
    assert len(entries) == len(set(entries))
    return len(entries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--parent', type=Path, default=HERE.parent / 'e8-bit-seven-stage')
    args = parser.parse_args()
    parent, out = args.parent.resolve(), args.output.resolve()
    for path in (parent, out, Path(sys.executable).resolve()):
        assert not any(c.isspace() for c in str(path)), 'Inherited parent requires paths without whitespace'
    assert not out.exists(), 'Use a fresh output directory'
    assert not out.is_relative_to(HERE) and not out.is_relative_to(parent)
    manifest(HERE)
    source, expected = read(HERE / 'SOURCE.json'), read(HERE / 'EXPECTED.json')
    frames, reuse = read(HERE / 'frame-selection.json'), read(HERE / 'reuse-selection.json')
    assert digest(parent / 'MANIFEST.sha256') == source['parent']['manifest_sha256']
    manifest(parent)
    for relative, want in source['parent']['files'].items():
        assert digest(parent / relative) == want, ('pinned parent file', relative)
    assert digest(HERE / 'frame-selection.json') == source['frame_selection_sha256']
    assert digest(HERE / 'reuse-selection.json') == source['reuse_selection_sha256']
    word_source = parent / source['word']
    assert digest(word_source) == frames['input_sha256']
    out.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    for key in ('PYTHONOPTIMIZE', 'PR315', 'CX_SOURCE_PINS', 'CX_PINS', 'CX_RECORD', 'CX_RECEIPT', 'B3_OUT'):
        env.pop(key, None)
    env['PATH'] = str(Path(sys.executable).parent) + os.pathsep + env.get('PATH', '')
    checks = []

    def run(name, command):
        print('CHECK', name, flush=True)
        with (out / (name + '.log')).open('w') as log:
            subprocess.run([str(x) for x in command], env=env, stdout=log,
                           stderr=subprocess.STDOUT, check=True)
        checks.append(name)

    def py(name, script, *arguments):
        run(name, [sys.executable, '-B', script, *arguments])

    run('parent373', ['bash', parent / 'verify.sh', out / 'parent'])
    b3 = read(out / 'parent/b3.json')
    guard = read(out / 'parent/complex-guard-b3.json')
    assert digest(out / 'parent/b3.json') == expected['complex_b3_receipt_sha256']
    assert b3['b'] == expected['pricing']['complex_coarse']
    assert b3['histogram'] == guard['ledger']['histogram'] == guard['five_stage_histogram']
    pg = guard['precision_guard']
    assert b3['m'] == pg['m'] and b3['W'] == pg['live_per_vertex']
    assert b3['m'] * b3['W'] - guard['ledger']['rank_mass'] == b3['deficit']
    assert (pg['G_exponent'], pg['E_exponent'], pg['C0_exponent'], pg['retained_row_coefficient']) == (30000, 100000, 210000, 20161)

    retimed = frame_replay.reconstruct(word_source.read_bytes(), frames)
    candidate = reuse_replay.reconstruct(retimed, reuse)
    (out / 'retimed.json').write_bytes(retimed)
    (out / 'word.json').write_bytes(candidate)
    (out / 'word.json.gz').write_bytes(gzip.compress(candidate, mtime=0))
    controls = frame_replay.negative_controls(word_source.read_bytes(), frames)
    controls += reuse_replay.negative_controls(retimed, reuse)
    assert sha256(candidate).hexdigest() == expected['word_sha256']
    word, rec = out / 'word.json.gz', out / 'records'
    B, CK = parent / 'code/bit', parent / 'code/bit/checkers'
    py('export', B / 'export_records.py', word, rec)
    record_hashes = {name: digest(rec / name) for name in expected['records']}
    assert record_hashes == expected['records']
    py('word', B / 'independent/checkword.py', word, parent / 'code/pricing')
    py('word-mutations', B / 'independent/mutate.py', word, parent / 'code/pricing')
    py('stage', B / 'regression/stage_cohort.py', rec, rec, out / 'cin', out / 'cout')
    binary = out / 'parent/bin'
    columns_binary = out / 'columns-k3-r822'
    run('compile-columns', ['g++', '-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9', '-DVPORTS=120', '-DRHELP=822', '-DKPAIRS=3', '-I' + str(CK), '-o', columns_binary, CK / 'columns_k.cpp'])
    run('legality', [binary / 'legality', out / 'cin', out / 'cout', out / 'cout/legality.json'])
    run('columns', [columns_binary, out / 'cout/COHORT249-RECORDS.bin', out / 'cout/columns.json'])
    py('record-mutations', B / 'mutate_records.py', rec, out / 'cin', out / 'cout', binary / 'legality', columns_binary, binary / 'legality_ncopy_h')
    py('gram', CK / 'gram_frames.py', rec, '--gram', 'e8ham', '--h', '8', '--positive')
    py('geometry', CK / 'geometry_k.py', '3', word)
    py('banks', CK / 'tile_k.py', rec, '3', '8', '7')
    py('pricing', CK / 'certify_bit_k.py', rec, b3['b'], '3', '8', '7', out / 'kappa.json')
    py('finite-input', B / 'receipts_k.py', word, rec, out / 'cout/legality.json', out / 'cout/columns.json', out / 'kappa.json', out / 'finite-input.json')
    py('finite', CK / 'finite_k.py', 'e8', out / 'finite-input.json', out / 'finite.json')
    price = read(out / 'kappa.json')
    price.pop('word')
    before = read(out / 'parent/kappa.json')
    assert before['kappa'] == expected['parent_kappa'] == price['kappa']
    assert before['bit_coarse'] == expected['parent_bit_coarse']
    assert Fraction(price['bit_coarse']) > Fraction(before['bit_coarse'])
    assert price == expected['pricing']
    legality = read(out / 'cout/legality.json')
    columns = read(out / 'cout/columns.json')
    columns.pop('seconds')
    columns.pop('local_scalar_stream')
    finite = read(out / 'finite.json')
    assert legality == expected['legality'] and columns == expected['columns']
    assert finite == expected['finite']

    py('assembly', HERE / 'assembly.py', parent, out / 'kappa.json', out / 'finite.json', out / 'assembly.json')
    py('parent-assembly', HERE / 'assembly.py', parent, out / 'parent/kappa.json', out / 'parent/finite.json', out / 'parent-assembly.json')
    assembly = read(out / 'assembly.json')
    assert assembly['kappa'] == read(out / 'parent-assembly.json')['kappa'] == expected['tight_kappa']
    assert digest(out / 'assembly.json') == expected['tight_assembly_sha256']
    assert Fraction(assembly['kappa']) > Fraction(price['kappa'])
    summary = dict(status='PASS_SOURCE_BOUND_CONDITIONAL_E8_HELPER_REUSE_AND_ASSEMBLY',
                   source_commit=source['parent']['commit'], parent_manifest_sha256=source['parent']['manifest_sha256'],
                   extension_manifest_sha256=digest(HERE / 'MANIFEST.sha256'), source_map_sha256=digest(HERE / 'SOURCE.json'),
                   expected_sha256=digest(HERE / 'EXPECTED.json'), frame_changes=128, helper_reuses=43,
                   word_sha256=sha256(candidate).hexdigest(), records=record_hashes, pricing=price,
                   finite=finite, assembly=assembly, parent_bit_coarse=before['bit_coarse'], checks=checks,
                   witness_negative_controls=controls,
                   headline_gain_scope='Assembly parameters only; applying the same refinement to the original PR373 word gives the same kappa. The improved R822 bit saving is a separate nonbinding component gain.',
                   obligations='All PR373/PR370/PR363 E8 routing/bank, nine-centre, B3/header-level exchange and source-owner admissions, and inherited compiler/chart/rows/routing/prime/precision/recovery/analytic interfaces remain conditional.')
    (out / 'RECEIPT.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print('PASS conditional kappa =', assembly['kappa'], '=', float(Fraction(assembly['kappa'])), flush=True)


if __name__ == '__main__':
    main()

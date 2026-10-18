"""Fast offline finite replay of the frozen Round20 global construction.

Default: exact changed scalar word, actual global owner/controller audit,
fresh primitive/prefix invoice, two rational moments and strict outer bounds.
The byte-pinned completed phase, data-controller and unchanged bit certificates
are reused. No solver, predecessor cold replay, or all-edge phase pass runs.
Optional --delta-phases lowers only edges absent from the pinned PR523 cache.
"""
import argparse
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


def read(path):
    b = path.read_bytes()
    return json.loads(gzip.decompress(b) if path.suffix == '.gz' else b)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if not __debug__:
        raise SystemExit('Assertions must be enabled; do not use -O.')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--rebuild-local', action='store_true', help='Also rebuild the scalar factory and frozen rational selection, without a search.')
    ap.add_argument('--delta-phases', action='store_true', help='Also freshly lower only changed phase edges; requires NumPy.')
    a = ap.parse_args()
    root = Path(__file__).resolve().parent
    a.work = a.work.resolve()
    assert not a.work.exists(), 'Use a new output directory.'
    assert root not in a.work.parents, 'Place outputs outside the package.'
    started = time.monotonic()
    manifest = read(root/'MANIFEST.json')
    for rel, digest in manifest['sha256'].items():
        assert sha(root/rel) == digest, ('input hash', rel)
    expected = read(root/'EXPECTED.json')
    local = root/'evidence/local'
    can = read(local/'CANONICAL-WORD.json.gz')
    review = read(local/'CLIFFORD-REVIEW.json')
    replay = read(local/'INDEPENDENT-LOCAL-REPLAY.json')
    programs = read(local/'LOCAL-PROGRAMS.json.gz')
    checks = read(local/'LOCAL-CHECKS.json')
    assert review['canonical_word_sha256'] == replay['canonical_word_sha256'] == sha(local/'CANONICAL-WORD.json.gz')
    assert replay['local_programs_sha256'] == sha(local/'LOCAL-PROGRAMS.json.gz')
    assert review['recipe_sha256'] == sha(local/'CLIFFORD-RECIPES.json')
    assert review['compiler_sha256'] == sha(root/'vendor/clifford/clifford_exact.py')
    assert review['all_child_equalities_include_global_phase']
    assert review['baseline_recipe_sha256'] == sha(root/'inputs/phase-baseline/CLIFFORD-RECIPES.json')
    for orientation, events in programs.items():
        encoded = json.dumps(events, sort_keys=True, separators=(',',':')).encode()
        assert hashlib.sha256(encoded).hexdigest() == checks[orientation]['sha256']
    adapters = read(local/'RESIDUAL-ADAPTERS.json')['recipes']
    starts = {f for f in can['start'][2*can['v']:] if f}
    assert set(map(int, adapters)) == starts
    for f in starts:
        r = adapters[str(f)]
        assert r['vectors'] == can['frames'][f] and r['rank'] == 9-len(can['frames'][f])

    a.work.mkdir(parents=True)
    steps = []
    def run(name, script, *args):
        t = time.monotonic()
        command = [sys.executable, '-B', str(root/'code'/script), *map(str,args)]
        log = a.work/(name+'.log')
        with log.open('w') as f:
            result = subprocess.run(command, stdout=f, stderr=subprocess.STDOUT)
        if result.returncode:
            print(log.read_text(), file=sys.stderr)
            raise SystemExit(f'{name} failed; see {log}')
        steps.append(dict(name=name, seconds=time.monotonic()-t, log=log.name))
        print('PASS', name, f'{steps[-1]["seconds"]:.2f}s', flush=True)

    raw = local/'FULL-WORD.json.gz'
    if a.rebuild_local:
        run('rebuild-selected', 'build_selected.py', '--work', a.work/'reconstructed')
        raw = a.work/'reconstructed/coalesced/FULL-WORD.json.gz'
    run('changed-scalar-and-frames', 'audit_and_transport.py', '--raw', raw,
        '--routing', root/'inputs/data-base/split-centres/CANONICAL-WORD.json.gz',
        '--out', a.work/'scalar')
    assert read(a.work/'scalar/CANONICAL-WORD.json.gz') == can
    if a.delta_phases:
        phase = a.work/'delta-phases'
        phase.mkdir()
        shutil.copyfile(local/'CANONICAL-WORD.json.gz', phase/'CANONICAL-WORD.json.gz')
        run('changed-phase-edges', 'phases_delta.py', '--local', phase,
            '--baseline', root/'inputs/phase-baseline', '--compiler', root/'vendor/clifford')
        assert read(phase/'CLIFFORD-RECIPES.json') == read(local/'CLIFFORD-RECIPES.json')

    run('new-local-controller-binding', 'prepare_supplier_base.py',
        '--data-base', root/'inputs/data-base', '--local', local, '--out', a.work/'base')
    run('emit-actual-owners', 'emit_supplier_hosted.py', '--base', a.work/'base',
        '--owners', root/'inputs/OWNERS.json.gz', '--plan', root/'inputs/OWNER-PLAN.json',
        '--out', a.work/'hosted')
    audit = a.work/'audit'; audit.mkdir()
    run('independent-whole-owners', 'audit_supplier_hosted.py', a.work/'base',
        a.work/'hosted', audit/'ASYNC-AUDIT.json')
    run('fresh-prefix-and-invoice', 'invoice_final.py', '--base', a.work/'base',
        '--hosted', a.work/'hosted', '--audit', audit, '--out', audit,
        '--retained-invoice', root/'inputs/PR523-PREFIX-AND-INVOICE.json')
    run('two-moments-and-outer', 'assemble.py', audit, a.work/'base',
        a.work/'hosted', root/'inputs/PR493-EXPECTED.json')
    answer = read(audit/'EXACT-ASSEMBLY.json')
    owners = read(audit/'OWNERS-AND-PROFILE.json')
    invoice = read(audit/'PREFIX-AND-INVOICE.json')
    assert answer['kappa'] == expected['kappa']
    assert answer['complex_lower'] == expected['complex_lower']
    assert answer['complex_template_sha256'] == expected['global_template_content_sha256']
    assert owners['paid_profile'] == expected['global_profile']
    assert invoice['global_prefix_bits'] == expected['global_prefix_bits']
    assert len(answer['strict_outer_constraints']) == 47
    result = dict(status='PASS_FAST_OFFLINE_FINITE_REPLAY', kappa=answer['kappa'],
        kappa_decimal=answer['kappa_decimal'], complex_lower=answer['complex_lower'],
        binding_component=answer['binding_component'], elapsed_seconds=time.monotonic()-started,
        predecessor_cold_replay=False, unchanged_bit_operator_rebuilt=False,
        changed_phase_edges_replayed=a.delta_phases, scalar_factory_rebuilt=a.rebuild_local,
        steps=steps,
        scope='Fresh changed-word and actual-host finite checks; byte-pinned completed phase/data/bit dependencies reused by default. All-size realization and analytic-transfer interfaces remain conditional.')
    (a.work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','kappa_decimal','elapsed_seconds')},sort_keys=True),flush=True)


if __name__ == '__main__':
    main()

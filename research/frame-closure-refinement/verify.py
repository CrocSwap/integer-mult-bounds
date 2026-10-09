#!/usr/bin/env python3
"""Replay a complex frame refinement against the immutable PR186 source.

Apache-2.0. Prepared with OpenAI Codex assistance. Scalar construction,
physical replay, terminal compiler, interval engine and balanced assembly
are the unchanged credited predecessor implementations, imported at runtime.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'research/coordinated-frames-and-entrance-banks'
sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def packed(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def write_packed(path, value):
    path.write_bytes(gzip.compress(json.dumps(value, sort_keys=True).encode(), mtime=0))


def pins():
    files = read(HERE / 'FILES.json')['files']
    actual = {p.relative_to(HERE).as_posix(): digest(p)
              for p in HERE.rglob('*') if p.is_file() and p.name != 'FILES.json'}
    require(files == actual, 'Refinement source inventory or bytes changed')
    return actual


def dependency_pins():
    for name, expected in read(HERE / 'PARENT.json')['files'].items():
        require(digest(ROOT / name) == expected, 'Predecessor source changed: ' + name)


def run(command, label):
    print(label, file=sys.stderr, flush=True)
    result = subprocess.run(command, text=True, capture_output=True)
    require(result.returncode == 0, label + '\n' + result.stdout + result.stderr)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def unpack(root):
    baseline = read(PARENT / 'BASELINE.json')
    chunks = []
    for part in baseline['parts']:
        raw = (PARENT / part['file']).read_bytes()
        require(len(raw) == part['bytes'] and sha256(raw).hexdigest() == part['sha256'],
                'Prerequisite archive part changed')
        chunks.append(raw)
    archive = b''.join(chunks)
    require(sha256(archive).hexdigest() == baseline['archive_sha256'], 'Archive hash changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        for entry in source.infolist():
            require((root / entry.filename).resolve().is_relative_to(root.resolve()),
                    'Unsafe archive path')
        source.extractall(root)
    staged_parent = root / PARENT.relative_to(ROOT)
    staged_parent.mkdir(parents=True)
    parts = {part['file'] for part in baseline['parts']}
    for path in PARENT.rglob('*'):
        if path.is_file() and path.name not in parts:
            target = staged_parent / path.relative_to(PARENT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    return staged_parent


def normalize_receipt(value):
    for key in ('seconds', 'maxrss', 'rss_kib'):
        value.pop(key, None)
    return value


def derive(root, parent, write):
    candidate = parent / 'selected/complex'
    new_frames = packed(HERE / 'physical-frames.json.gz')
    old_frames = packed(candidate / 'physical-frames.json.gz')
    sys.path.insert(0, str(root / 'scripts'))
    from paired_cube.frames import perp, contained
    from paired_cube_physical import physical
    graph, witness, word, oldrow = [packed(candidate / (n + '.json.gz'))
        for n in ('graph', 'frames', 'word', 'profile-before')]
    compiler = [perp(witness['annihilators'][n], graph['h']) for a, b, n in word['ops']]
    before = compiler[:]
    after = compiler[:]
    for i, frame in old_frames:
        before[i] = tuple(frame)
    for i, frame in new_frames:
        after[i] = tuple(frame)
    require(all(contained(a, b) for a, b in zip(after, before)),
            'Refinement must descend from the selected PR186 frames')
    changed = [i for i, (a, b) in enumerate(zip(after, before)) if a != b]
    require(changed, 'Empty frame refinement')
    shutil.copyfile(HERE / 'physical-frames.json.gz', candidate / 'physical-frames.json.gz')
    if write:
        profile = physical(graph, witness, word, oldrow, new_frames,
                           packed(candidate / 'physical-pairs.json.gz'))
        write_packed(HERE / 'profile.json.gz', profile)
    shutil.copyfile(HERE / 'profile.json.gz', candidate / 'profile.json.gz')
    inventory = read(candidate / 'result.json')
    inventory['pins'] = {p.name: digest(p) for p in candidate.glob('*.json.gz')}
    write_json(candidate / 'result.json', inventory)
    complex_dir = parent / 'complex'
    output = root / 'physical-receipt.json'
    run([sys.executable, '-B', str(complex_dir / 'physical.py'), '--candidate',
         str(candidate), '--source', str(root), '--out', str(output)],
        'Replaying exact scalar word, value containment, physical chains and all formal columns.')
    physical_result = normalize_receipt(read(output))
    physical_result['source_sha256'] = {
        Path(k).relative_to(root).as_posix(): v
        for k, v in physical_result['source_sha256'].items()}
    selection_path = candidate / 'sinks.json'
    run([sys.executable, '-B', str(complex_dir / 'check_sinks.py'), '--candidate',
         str(candidate), '--output', str(selection_path)],
        'Recounting simultaneous terminal sinks and every target-frame event.')
    selection = normalize_receipt(read(selection_path))
    write_json(selection_path, selection)
    if write:
        shutil.copyfile(selection_path, HERE / 'sinks.json')
    else:
        require(selection == read(HERE / 'sinks.json'), 'Terminal compiler receipt changed')
    formal_path = root / 'terminal-formal.json'
    run([sys.executable, '-B', str(complex_dir / 'formal_sinks.py'), '--candidate',
         str(candidate), '--selection', str(selection_path), '--formal-helper',
         str(complex_dir / 'physical.py'), '--output', str(formal_path)],
        'Replaying the terminal-modified word on every formal column in both signs.')
    formal = normalize_receipt(read(formal_path))
    paid = dict(physical_result['physical'])
    paid.update(physical_R=selection['new_physical_R'], W_per_vertex=selection['new_W'],
                rank_per_vertex=selection['new_rank'], child_histogram=selection['child_histogram'],
                local_histogram=selection['local_histogram'],
                target_data_histogram=selection['target_histogram'],
                terminal_sinks=selection['eligible_count'])
    require(all(z['dirty'] == paid['physical_R'] and z['columns'] == paid['W_per_vertex']
                for z in formal['columns']), 'Formal-column inventory differs from paid stock')
    row = {k: oldrow[k] for k in ('h', 'v', 'c', 'q', 'matched', 'total_M_operations', 'loss')}
    row.update({k: paid[k] for k in ('m', 'W_per_vertex', 'rank_per_vertex',
                                   'deficit_per_vertex', 'child_histogram')})
    row.update(R=paid['physical_R'], scalar_role_reserve=oldrow['R'],
               reuse_pairs=paid['pairs'], terminal_sinks=paid['terminal_sinks'],
               maxchild=max(map(int, paid['child_histogram'])))
    sys.path.insert(0, str(parent / 'arithmetic'))
    from interval_moment import saving_grid, moment
    from certificate import price, js, AC, COARSE, BETA, ETA, WEAKENING, normalized_body_check
    from balanced_shared import assembly
    normalized_body_check()
    moment_profile = dict(m=row['m'], W=row['W_per_vertex'], N=row['deficit_per_vertex'],
                          L=0, total_rank=row['rank_per_vertex'], maxchild=row['maxchild'],
                          child_multiplicities=row['child_histogram'])
    certified_moment = saving_grid(moment_profile, 10**18)
    saving = certified_moment['accepted']['saving']
    require(saving > AC, 'No improvement in complex saving')
    final = price(row, saving, COARSE, BETA, ETA, WEAKENING, 'balanced')
    old_kappa = Q(read(PARENT / 'certificate.json')['kappa'])
    require(final['kappa'] > old_kappa, 'No improvement in the final exponent')
    require(physical_result['scalar_bound']['local_group_upper'] ==
            final['finite_bridge']['complex']['local_group_upper'], 'Detached scalar bill')
    controls = []
    def reject(name, action):
        try:
            action()
        except (ValueError, AssertionError):
            controls.append(name)
        else:
            raise ValueError('Adverse control accepted: ' + name)
    reject('next final kappa grid point', lambda: assembly(final['finite_bridge'], row,
        final['a'], final['kappa'] + Q(1, 10**18), beta=BETA, h=ETA, a_complex=saving))
    reject('unpaid old nonlinear scalar guard', lambda: assembly(final['finite_bridge'], row,
        final['a'], final['kappa'], beta=BETA, h=ETA, a_complex=saving, old_guard=True))
    reject('unpaid old prefix layout', lambda: assembly(final['finite_bridge'], row,
        final['a'], final['kappa'], beta=BETA, h=ETA, a_complex=saving, original_prefix=True))
    bad = dict(moment_profile, total_rank=moment_profile['total_rank'] - 1)
    reject('detached rank mass', lambda: moment(bad, saving))
    original_profile = read(PARENT / 'certificate.json')['complex']['profile']
    oldmoment = dict(m=original_profile['m'], W=original_profile['W_per_vertex'],
        N=original_profile['deficit_per_vertex'], L=0,
        total_rank=original_profile['rank_per_vertex'], maxchild=original_profile['maxchild'],
        child_multiplicities=original_profile['child_histogram'])
    require(moment(oldmoment, saving)['lower'] > 1,
            'Original frames do not exclude the new complex saving')
    # A nonempty required source span cannot fit an empty operation frame.
    corrupt = [list(z) for z in new_frames]
    operation = changed[0]
    corrupt = [z for z in corrupt if z[0] != operation] + [[operation, []]]
    reject('empty operation frame loses required value', lambda: physical(
        graph, witness, word, oldrow, corrupt, packed(candidate / 'physical-pairs.json.gz')))
    return js(dict(status='PASS conditional frame-refinement candidate',
        kappa=final['kappa'], previous_kappa=old_kappa,
        relative_improvement=(final['kappa'] - old_kappa) / old_kappa,
        complex_saving=saving, changed_operation_count=len(changed),
        changed_operations=changed, profile=row, moment=certified_moment,
        assembly=final, physical=physical_result, terminal_formal=formal,
        adverse_controls=controls, original_frames_reject_new_complex_saving=True,
        scope='Conditional on the unchanged PR186 all-size interfaces; finite replay is not a formal multiplication theorem.'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Authoring: regenerate derived receipts')
    args = parser.parse_args()
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    before = None if args.write else pins()
    dependency_pins()
    run([sys.executable, '-B', str(PARENT / 'verify.py')],
        'Replaying the immutable predecessor, including its complete bit supplier and 47 constraints.')
    run([sys.executable, '-B', str(ROOT / 'research/community-round8-audit/bank_schedule.py')],
        'Replaying the inherited entrance-bank scheduling supplement.')
    with tempfile.TemporaryDirectory(prefix='frame-closure-refinement-') as tmp:
        root = Path(tmp)
        parent = unpack(root)
        result = derive(root, parent, args.write)
    if args.write:
        write_json(HERE / 'certificate.json', result)
    else:
        require(result == read(HERE / 'certificate.json'), 'Derived certificate differs')
        require(pins() == before, 'Refinement source changed during verification')
    dependency_pins()
    print('PASS frame-closure-refinement kappa=' + result['kappa'] +
          '; ' + str(result['changed_operation_count']) + ' descended operation frames; '
          'complete formal columns, strict rational moment and 47 assembly constraints.')


if __name__ == '__main__':
    main()

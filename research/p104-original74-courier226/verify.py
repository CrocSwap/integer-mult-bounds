#!/usr/bin/env python3
"""Offline, staged #7644-to-main46 reconstruction and application replay."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import secrets
import shutil
import subprocess
import sys
import tarfile
import tempfile

PACKAGE = Path(__file__).resolve().parent
DATA = PACKAGE / 'data'
SOURCE_SHA = 'a1bbe4897942e6e22ae947d39803e7db821e2774e25b3164b470ade7406f9835'
BASELINE_SHA = '6c52b2fba7c20343a50cb92ed4b997aa9921c78f212ac6428d13fff2bcd014cf'
CANDIDATE_SHA = '450c7e544efb5258c4b8b4858b49cbd7482d14f206cdda1a71833fc73343ac66'
CLAIM = '0.0036524238117'
EXTERNAL = {
    'retained/pr7605/retained/role902/upstream/inputs/pr7480/inputs/pr7334.tar.gz':
        ('pr7334.tar.gz', '721f839cc48605cccd3629d11456e1fcbb3810a624803ad27e99a1bfd6246211'),
    'retained/pr7605/retained/two-contractions/published/replay.zip':
        ('replay.zip', '0bf0082cab9b6d2bb6657903a4169a3d04c380927982fc4672a6a44edda79a2a'),
}
SOURCE_PINS = {'build_candidate.py': 'd01c8a66b787b5203b4eaea2a0d9fb7b485466bd73471622dd121bcae5c8f712', 'combined.py': '02bf9ae9aabf50a894fa841d8d6177edac743999ef1fca1b9d705003067f4a9b', 'generate.py': 'f3cd924e6fc0a4a24ebb26cd42e42d9199a3b34e1c68ade3ab075bc4c3e87cce', 'compose_edits.py': '47c935668585e888729ec19594461fd70b488a22fd781939e57dbe2d26f0d537', 'paired.py': '82762c73e49dbb95ca5c3b20a33fb4e15fe94889c65b328e971e014c06abcab5', 'word_checks.py': '91c98e69926c6e2c3d285e3a2116a6919c7b12746c845f36770ea2ebfad071a9', 'run.py': 'df989c97e7d566929388f4e9cdb31958a83a3171e771a776bcd17df095f7ab3e'}
IDENTITY = hashlib.sha256(str(PACKAGE).encode()).hexdigest()[:16]
POINTER = Path(tempfile.gettempdir()) / ('p104-courier226-%s-%s.json' % (os.getuid(), IDENTITY))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def execute(script, *arguments):
    command = [sys.executable, '-I', '-B', str(script), *map(str, arguments)]
    subprocess.run(command, check=True)


def workspace():
    require(POINTER.is_file() and not POINTER.is_symlink(), 'missing or unsafe replay pointer')
    require(POINTER.stat().st_uid == os.getuid(), 'unsafe replay pointer owner')
    record = json.loads(POINTER.read_text())
    root = Path(record['workspace'])
    require(root.is_dir() and not root.is_symlink() and root.parent == Path(tempfile.gettempdir()).resolve(), 'unsafe workspace')
    require(root.name.startswith('p104-original74-work-') and root.stat().st_uid == os.getuid(), 'workspace ownership')
    marker = root / '.replay-owner.json'
    require(marker.is_file() and not marker.is_symlink() and marker.stat().st_uid == os.getuid(), 'unsafe workspace marker')
    require(json.loads(marker.read_text()) == {'token': record['token'], 'package': str(PACKAGE)}, 'workspace identity mismatch')
    return root


def extract_source(root):
    archive = DATA / 'source7644-remainder.tar.gz'
    manifest = json.loads((DATA / 'source-manifest.json').read_text())
    require(digest(archive.read_bytes()) == SOURCE_SHA == manifest['archive_sha256'], 'source archive pin')
    files = manifest['files']
    require(len(files) == 156 and manifest['retained_7605_closure_files'] == 138, 'source inventory')
    target = root / 'source7644'
    target.mkdir(mode=0o700)
    seen = set()
    with tarfile.open(archive, mode='r:gz') as bundle:
        for member in bundle:
            name = member.name
            parts = PurePosixPath(name)
            require(member.isfile() and not parts.is_absolute() and '..' not in parts.parts and name in files and name not in seen, 'unexpected archive member')
            payload = bundle.extractfile(member).read()
            require(digest(payload) == files[name], 'source file hash: ' + name)
            path = target.joinpath(*parts.parts)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(payload)
            seen.add(name)
    external = manifest['external_blobs']
    require(external == {name: item[0] for name, item in EXTERNAL.items()} and not (seen & set(external)), 'external source inventory')
    for name, local_name in external.items():
        parts = PurePosixPath(name)
        require(not parts.is_absolute() and '..' not in parts.parts and name in files, 'external destination')
        require(local_name in ('pr7334.tar.gz', 'replay.zip'), 'external filename')
        payload = (DATA / local_name).read_bytes()
        require(digest(payload) == files[name] == EXTERNAL[name][1], 'external source hash: ' + name)
        path = target.joinpath(*parts.parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(payload)
        seen.add(name)
    require(seen == set(files), 'incomplete source archive')


def create_workspace():
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(POINTER, flags, 0o600)
    root = Path(tempfile.mkdtemp(prefix='p104-original74-work-')).resolve()
    token = secrets.token_hex(32)
    (root / '.replay-owner.json').write_text(json.dumps({'token': token, 'package': str(PACKAGE)}))
    with os.fdopen(descriptor, 'w') as stream:
        json.dump({'workspace': str(root), 'token': token}, stream)
    return root


def check_package_sources():
    for name, pin in SOURCE_PINS.items():
        require(digest((PACKAGE / 'src' / name).read_bytes()) == pin, 'package source pin: ' + name)


def prepare():
    check_package_sources()
    execute(PACKAGE / 'controls.py')
    root = create_workspace()
    print('REPLAY_WORKSPACE', root, flush=True)
    extract_source(root)
    for name in ('build_candidate.py', 'combined.py', 'generate.py', 'compose_edits.py', 'paired.py', 'word_checks.py'):
        shutil.copyfile(PACKAGE / 'src' / name, root / name)
    application = root / 'application'
    application.mkdir()
    shutil.copyfile(PACKAGE / 'src' / 'word_checks.py', application / 'word_checks.py')
    source = (PACKAGE / 'src' / 'run.py').read_text()
    runtime_edits = [('start_new_session=True', 'start_new_session=False'),
                     ('os.killpg(proc.pid,signal.SIGTERM)', 'proc.terminate()'),
                     ('os.killpg(proc.pid,signal.SIGKILL)', 'proc.kill()'),
                     ('os.killpg(proc.pid, signal.SIGKILL)', 'proc.kill()')]
    for before, after in runtime_edits:
        require(source.count(before) == 1, 'runtime adapter anchor: ' + before)
        source = source.replace(before, after)
    compile(source, str(application / 'run.py'), 'exec')
    (application / 'run.py').write_text(source)
    execute(root / 'source7644' / 'build.py')
    execute(root / 'build_candidate.py')
    execute(root / 'combined.py')
    import gzip
    require(digest(gzip.decompress((root / 'candidate.json.gz').read_bytes())) == BASELINE_SHA, 'baseline word')
    (root / 'candidate.json.gz').rename(root / 'baseline.json.gz')
    (root / 'combined-edits.json').rename(root / 'baseline-edits.json')
    (root / 'candidate-invoice.json').rename(root / 'baseline-invoice.json')
    require(digest((root / 'baseline-invoice.json').read_bytes()) == '7d54c1ec036d4c096526dd95e06892ca99210812d51a503b22f6d78243330ca9', 'baseline invoice')
    execute(root / 'generate.py')
    require(digest(gzip.decompress((root / 'candidate.json.gz').read_bytes())) == CANDIDATE_SHA, 'candidate word')
    execute(root / 'compose_edits.py')
    invoice = json.loads((root / 'baseline-invoice.json').read_text())
    for rank, delta in {'1': -17, '2': -17, '3': 17}.items():
        invoice['paid'][rank] += delta
    (root / 'candidate-invoice.json').write_text(json.dumps(invoice, indent=2, sort_keys=True) + '\n')
    require(digest((root / 'candidate-invoice.json').read_bytes()) == 'fa0c37a9e67d0a82850c4fcfd5cbdb3bd88e1f8db329176e5669da6c7788f6a2', 'candidate invoice')
    execute(application / 'run.py', 'prepare', '--work', application / 'work',
            '--package', root / 'source7644' / 'retained' / 'pr7605',
            '--word', root / 'candidate.json.gz', '--sha', CANDIDATE_SHA,
            '--edits', root / 'combined-edits.json', '--invoice', root / 'candidate-invoice.json',
            '--incumbent', root / 'baseline-invoice.json', '--claim', CLAIM)
    print('PASS_STRICT74_PREPARE', CANDIDATE_SHA, flush=True)


def run_stage(stage):
    check_package_sources()
    root = workspace()
    for name in ('paired.py', 'word_checks.py'):
        require(digest((root / name).read_bytes()) == SOURCE_PINS[name], 'workspace source pin: ' + name)
    application = root / 'application'
    if stage == 'native':
        execute(root / 'paired.py')
        result = json.loads((root / 'paired.json').read_text())
        require(result['status'] == 'PASS_PAIRED_EXACT_STRICT74' and result['source_sha256'] == BASELINE_SHA and result['candidate_sha256'] == CANDIDATE_SHA and result['observations'] == 630 and result['ordered_clears'] == 74 and result['copies'] == 1, 'strict original interface')
        controls = json.loads((root / 'controls.json').read_text())
        require(all(controls[name]['rejected'] for name in ('wrong_encode_sign', 'decode_before_990_arrives')), 'negative controls')
    # The registered hook enforces the stage process-group limit. Its
    # group-wide termination includes the attached scientific child.
    timeout = 1800
    execute(application / 'run.py', stage, '--work', application / 'work',
            '--package', root / 'source7644' / 'retained' / 'pr7605', '--timeout', timeout)
    if stage == 'signed':
        final = json.loads((application / 'work' / 'FINAL.json').read_text())
        require(final['status'] == 'PASS_CHART1062_FINAL_APPLICATION' and final['candidate_canonical_sha256'] == CANDIDATE_SHA and final['claim'] == CLAIM and final['paid_calls'] == 110281 and final['productive_calls'] == 22461 and final['tape']['native_invocations'] == 17 and final['outer']['BIT_just_below_effective_rejected'] and final['outer']['strict_count'] == 54, 'full final receipt')
        require((application / 'work' / 'DIRECTED-PRICE.json').is_file(), 'directed price')
        print('PASS_STRICT74_COMPLETE', CANDIDATE_SHA, flush=True)
        shutil.rmtree(root)
        POINTER.unlink()
    else:
        print('PASS_STRICT74_NATIVE', CANDIDATE_SHA, flush=True)


def main():
    require(sys.version_info[:2] == (3, 12) and sys.dont_write_bytecode and __debug__, 'use Python 3.12 -I -B')
    require(len(sys.argv) == 2 and sys.argv[1] in ('prepare', 'native', 'signed', 'cleanup'), 'expected prepare, native, signed or cleanup')
    stage = sys.argv[1]
    if stage == 'prepare':
        prepare()
    elif stage == 'cleanup':
        root = workspace()
        shutil.rmtree(root)
        POINTER.unlink()
    else:
        run_stage(stage)


if __name__ == '__main__':
    main()

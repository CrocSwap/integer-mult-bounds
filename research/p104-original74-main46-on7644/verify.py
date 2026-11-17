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
CANDIDATE_SHA = '6c52b2fba7c20343a50cb92ed4b997aa9921c78f212ac6428d13fff2bcd014cf'
CLAIM = '0.0036521182092'
EXTERNAL = {
    'retained/pr7605/retained/role902/upstream/inputs/pr7480/inputs/pr7334.tar.gz':
        ('pr7334.tar.gz', '721f839cc48605cccd3629d11456e1fcbb3810a624803ad27e99a1bfd6246211'),
    'retained/pr7605/retained/two-contractions/published/replay.zip':
        ('replay.zip', '0bf0082cab9b6d2bb6657903a4169a3d04c380927982fc4672a6a44edda79a2a'),
}
IDENTITY = hashlib.sha256(str(PACKAGE).encode()).hexdigest()[:16]
POINTER = Path(tempfile.gettempdir()) / ('p104-original74-%s-%s.json' % (os.getuid(), IDENTITY))


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


def prepare():
    execute(PACKAGE / 'controls.py')
    root = create_workspace()
    print('REPLAY_WORKSPACE', root, flush=True)
    extract_source(root)
    for name in ('build_candidate.py', 'combined.py', 'strict_replay.py', 'price_check.py'):
        shutil.copyfile(PACKAGE / 'src' / name, root / name)
    application = root / 'application'
    application.mkdir()
    shutil.copyfile(PACKAGE / 'src' / 'word_checks.py', application / 'word_checks.py')
    source = (PACKAGE / 'src' / 'run.py').read_text()
    require(digest(source.encode()) == '1265cffbf08653f06b3f0c6515a67c366a40647d42a1cfb9c2e8f76d92323dff', 'application source pin')
    # The package hook owns the whole process group. Keep child processes in
    # that group so a hook timeout cannot strand a detached native/signed job.
    runtime_edits = [('start_new_session=True', 'start_new_session=False'),
                     ('os.killpg(proc.pid,signal.SIGTERM)', 'proc.terminate()'),
                     ('os.killpg(proc.pid,signal.SIGKILL)', 'proc.kill()')]
    for before, after in runtime_edits:
        require(source.count(before) == 1, 'runtime adapter anchor: ' + before)
        source = source.replace(before, after)
    compile(source, str(application / 'run.py'), 'exec')
    (application / 'run.py').write_text(source)
    # Reconstruct the public #7644 source and then the candidate on fresh inputs.
    execute(root / 'source7644' / 'build.py')
    execute(root / 'build_candidate.py')
    execute(root / 'combined.py')
    import gzip
    require(digest(gzip.decompress((root / 'candidate.json.gz').read_bytes())) == CANDIDATE_SHA, 'candidate hash')
    execute(application / 'run.py', 'prepare', '--work', application / 'work',
            '--package', root / 'source7644' / 'retained' / 'pr7605',
            '--word', root / 'candidate.json.gz', '--sha', CANDIDATE_SHA,
            '--edits', root / 'combined-edits.json', '--invoice', root / 'candidate-invoice.json',
            '--incumbent', root / 'source7644' / 'data' / 'invoice.json', '--claim', CLAIM)
    print('PASS_STRICT74_PREPARE', CANDIDATE_SHA, flush=True)


def run_stage(stage):
    root = workspace()
    application = root / 'application'
    if stage == 'native':
        execute(root / 'strict_replay.py')
        result = json.loads((root / 'STRICT-REPLAY.json').read_text())
        require(result['status'] == 'PASS_PAIRED_EXACT_STRICT74' and result['candidate_sha256'] == CANDIDATE_SHA and result['private_observation_events'] == 630 and result['ordered_clears'] == 74 and result['copies'] == 1, 'strict original interface')
        execute(root / 'price_check.py')
    # The generic hook's 580-second process-group limit fires first. Its
    # group-wide termination includes the attached scientific child.
    timeout = 1800
    execute(application / 'run.py', stage, '--work', application / 'work',
            '--package', root / 'source7644' / 'retained' / 'pr7605', '--timeout', timeout)
    if stage == 'signed':
        final = json.loads((application / 'work' / 'FINAL.json').read_text())
        require(final['candidate_canonical_sha256'] == CANDIDATE_SHA, 'final candidate')
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

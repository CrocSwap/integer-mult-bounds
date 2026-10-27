#!/usr/bin/env python3
"""Small cache-policy controls; fixture bytes are not Lean proof artifacts."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('source_replay', ROOT / 'replay.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


def main():
    checks = []

    def check(label, assertion):
        assert assertion, label
        checks.append(label)

    def rejects(label, action):
        try:
            action()
        except RuntimeError:
            checks.append(label)
        else:
            raise AssertionError(label)

    with tempfile.TemporaryDirectory(prefix='reuse-policy-fixture-') as directory:
        build = Path(directory)
        source = b'def fixture := True\n'
        source_copy = build / 'Fixture.lean'
        source_copy.write_bytes(source)
        artifact = build / 'Fixture.olean'
        artifact.write_bytes(b'cache-policy fixture, not a Lean artifact')
        sha = hashlib.sha256(source).hexdigest()
        artifact_sha = replay.sha256_file(artifact)
        deps = {'Earlier': 'a' * 64}
        dep_artifacts = {'Earlier': {'.olean': 'a' * 64}}
        dep_sources = {'Earlier': 'b' * 64}
        old = {'sha256': sha, 'dependency_hashes': deps,
               'olean_sha256': artifact_sha, 'seconds': 1.0, 'output': ''}
        args = dict(source=source, expected_sha=sha, source_copy=source_copy,
                    artifacts={'.olean': artifact_sha}, dependencies=deps,
                    dependency_artifacts=dep_artifacts,
                    dependency_sources=dep_sources, environment_sha='current')
        anchor = {'fixture': True}
        check('unchanged legacy cache matches before policy gate', replay.cache_matches(old, **args))
        rejects('legacy reuse without explicit flag rejected',
                lambda: replay.legacy_reuse_record('Fixture', old, old, anchor, 'current', False))
        reused = replay.legacy_reuse_record('Fixture', old, old, anchor, 'current', True)
        check('explicit legacy keeps historical environment unrecorded',
              reused['historical_external_environment'] == 'unrecorded' and
              'environment_sha256' not in reused)
        rejects('mutable progress cannot override committed artifact receipt',
                lambda: replay.legacy_reuse_record('Fixture', dict(old, olean_sha256='altered'),
                                                  old, anchor, 'current', True))
        source_copy.write_bytes(source + b'-- changed\n')
        check('changed copied source rejected', not replay.cache_matches(old, **args))
        source_copy.write_bytes(source)
        artifact.write_bytes(b'altered fixture')
        changed = dict(args, artifacts=replay.module_artifacts(build, 'Fixture'))
        check('changed compiled bytes rejected', not replay.cache_matches(old, **changed))
        check('changed dependency hash rejected', not replay.cache_matches(
            old, **dict(args, dependencies={'Earlier': 'changed'})))
        check('unrecorded legacy companion rejected', not replay.cache_matches(
            old, **dict(args, artifacts={'.olean': artifact_sha, '.olean.private': 'extra'})))
        fresh = dict(old, environment_sha256='current', artifacts=args['artifacts'],
                     dependency_artifacts=dep_artifacts, dependency_source_sha256=dep_sources)
        check('matching environment-bound cache accepted', replay.cache_matches(fresh, **args))
        check('changed external environment invalidates new cache', not replay.cache_matches(
            fresh, **dict(args, environment_sha='changed')))
        check('changed dependency companion invalidates new cache', not replay.cache_matches(
            fresh, **dict(args, dependency_artifacts={'Earlier': {'.olean': 'a' * 64, '.ir': 'new'}})))
        check('changed dependency source invalidates new cache', not replay.cache_matches(
            fresh, **dict(args, dependency_sources={'Earlier': 'changed'})))
        repeated = replay.legacy_reuse_record('Fixture', reused, old, anchor, 'current', True)
        check('subsequent legacy resume stays historically unrecorded',
              repeated['historical_external_environment'] == 'unrecorded' and
              'environment_sha256' not in repeated)
        check('previously observed changed environment invalidates legacy cache',
              not replay.cache_matches(reused, **dict(args, environment_sha='changed')))
        before = replay.footprint(build)
        artifact.write_bytes(b'another fixture')
        check('footprint hashes actual bytes', replay.footprint(build) != before)
        replay.validate_build_artifact_inventory(build, ['Fixture'])
        checks.append('manifested artifact inventory accepted')
        for name in ['Std.olean', 'Mathlib/Algebra/Group/Defs.olean',
                     'Extra.olean.private', 'Extra.ir.sig', 'libInjected.so']:
            extra = build / name
            extra.parent.mkdir(parents=True, exist_ok=True)
            extra.write_bytes(b'fixture')
            rejects('unmanifested shadow artifact rejected: ' + name,
                    lambda: replay.validate_build_artifact_inventory(build, ['Fixture']))
            extra.unlink()
        (build / 'Shadow').symlink_to(build.parent, target_is_directory=True)
        rejects('symlinked search subtree rejected',
                lambda: replay.validate_build_artifact_inventory(build, ['Fixture']))
    print(json.dumps({'status': 'PASS', 'checks': checks, 'count': len(checks),
                      'scope': 'Policy fixtures only; no Lean compilation.'}, indent=2))


if __name__ == '__main__':
    main()

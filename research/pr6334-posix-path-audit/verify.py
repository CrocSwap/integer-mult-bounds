#!/usr/bin/env python3
"""Independent materialized-path differential audit of PR6334 on POSIX.

Hao Yan (@FanPUYen), with substantial OpenAI Codex assistance. Apache-2.0.
The repair and retained tests are josecarlosgonzalezroque-design's work;
the original tools retain Douglas Colkitt and their other contributors' credit.
"""
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PINS = {
    'retained/main/scripts/find_overlap.py': '41a2796868b5122f568b126726cd04d98f9b5fea78d399c449c1d2e2a69aa0f4',
    'retained/pr6334/scripts/find_overlap.py': 'cff8509bf54b19cfb174ba0b3878ed5ddf350cd7f18e40bf359d9cbbf67f8b29',
    'retained/pr6334/scripts/research_package.py': 'e1256016e7f51827d04fa2179255989f639ae1d97afaa9c16265f85a0c6abd70',
    'retained/pr6334/tests/test_research_overlap_git_paths.py': '85c99372b916a2cce45e4513252e9d64b24aeab293a7ab5d829d91e7c15749e1',
    'retained/pr6334/tests/test_research_overlap_local.py': '51360d84b55792a55a1ff9a34ec02cf87086e43a0eb5144cf0e630a982d5d7b5',
}
NAMES = ['research/line\rbreak/README.md', 'research/line\nbreak/README.md',
         'research/line\r\nbreak/README.md']
EXTRA = ['research/plain/TASK.json', 'docs/research/pr-ledger.md']
EXPECTED = sorted(NAMES + EXTRA)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_bytes(base=HERE):
    result = {}
    for name, digest in PINS.items():
        raw = (base / name).read_bytes()
        require(sha256(raw).hexdigest() == digest, 'source hash mismatch: ' + name)
        result[name] = raw
    return result


def environment():
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
               GIT_AUTHOR_NAME='Path fixture', GIT_COMMITTER_NAME='Path fixture',
               GIT_AUTHOR_EMAIL='fixture@example.invalid',
               GIT_COMMITTER_EMAIL='fixture@example.invalid')
    return env


def run(args, root, env):
    return subprocess.run(args, cwd=root, env=env, capture_output=True,
                          check=True, timeout=30)


def git(root, env, *args):
    return run(['git', '-c', 'core.hooksPath=' + os.devnull,
                '-c', 'commit.gpgsign=false', *args], root, env).stdout


def write(root, name, raw=b'needle\n'):
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    return target


def fixture(root, env):
    root.mkdir()
    for name in EXPECTED:
        write(root, name)
    (root / EXTRA[0]).chmod(0o755)
    # Deliberately outside the inventory of regular top-level notes.
    write(root, 'research/plain/vendor/README.md')
    link = root / 'research/tracked-link/README.md'
    link.parent.mkdir()
    link.symlink_to('../line\nbreak/README.md')
    git(root, env, 'init', '-q')
    git(root, env, 'add', '.')
    git(root, env, 'commit', '-qm', 'materialized POSIX path fixture')
    return git(root, env, 'rev-parse', 'HEAD').decode('ascii').strip()


def cli(root, env, cache, files, variant):
    write(root, 'scripts/find_overlap.py', files[f'retained/{variant}/scripts/find_overlap.py'])
    write(root, 'scripts/research_package.py', files['retained/pr6334/scripts/research_package.py'])
    flags = ['-I', '-B', '-W', 'error']
    if sys.flags.optimize:
        flags += ['-O']  # Propagate optimization into every independent CLI child.
    args = [sys.executable, *flags, str(root / 'scripts/find_overlap.py'),
            'needle', '--offline', '--json', '--limit', '1', '--cache', str(cache)]
    before = cache.read_bytes()
    report = json.loads(run(args, root, env).stdout)
    require(cache.read_bytes() == before, 'offline command changed cache')
    return report


def check_report(report, head, missing, records, variant):
    coverage = report['coverage']['local']
    # The oracle comes from declared fixture paths, not the tool/Git decoder.
    # The baseline's normalization is an expected negative control.
    expected_missing = sorted(missing) if variant == 'pr6334' else []
    require(coverage['head'] == head, 'HEAD binding changed')
    require(coverage['head_records'] == (5 if variant == 'pr6334' else 3),
            'unexpected HEAD path count')
    require(coverage['unsearched_head_paths'] == expected_missing, 'wrong missing paths')
    require(coverage['complete_head_inventory'] == (not expected_missing),
            'incorrect completeness flag')
    require(coverage['records'] == records, 'wrong searched record count')
    require(report['matches_total'] == records, 'search lost a materialized note')
    require(len(report['matches']) == 1, '--limit did not limit displayed results')
    if expected_missing:
        require(any(f'{len(expected_missing)} HEAD note paths were not searched' in w
                    for w in report['warnings']), 'missing coverage warning')
    return {k: coverage[k] for k in ('records', 'head_records',
                                    'complete_head_inventory', 'unsearched_head_paths')}


def differential(files):
    results = []
    env = environment()
    with tempfile.TemporaryDirectory(prefix='pr6334-posix-') as directory:
        base = Path(directory)
        root = base / 'repo'
        head = fixture(root, env)
        cache = base / 'overlap.json'
        cache.write_text(json.dumps({'schema_version': 1,
                                    'repository': 'CrocSwap/integer-mult-bounds',
                                    'sources': {}}), encoding='utf-8')
        omitted = [NAMES[0], NAMES[2]]

        def probe(name, missing, records):
            row = {'case': name}
            for variant in ('main', 'pr6334'):
                row[variant] = check_report(cli(root, env, cache, files, variant),
                                            head, missing, records, variant)
            results.append(row)

        probe('all_materialized_executable_and_tracked_symlink', [], 5)
        for name in omitted:
            (root / name).unlink()
        probe('only_lf_materialized', omitted, 3)
        for name in omitted:
            (root / name).symlink_to(root / NAMES[1])
        probe('leaf_symlinks_to_lf_cannot_fill_gap', omitted, 3)
        for name in omitted:
            (root / name).unlink()
            (root / name).parent.rmdir()
            (root / name).parent.symlink_to((root / NAMES[1]).parent,
                                          target_is_directory=True)
        probe('parent_symlinks_to_lf_cannot_fill_gap', omitted, 3)
        for name in omitted:
            (root / name).parent.unlink()
            (root / name).parent.mkdir()
            (root / name).symlink_to(base / 'nonexistent')
        probe('dangling_symlinks_cannot_fill_gap', omitted, 3)
        write(root, 'research/untracked/README.md')
        probe('untracked_note_cannot_fill_gap', omitted, 4)
        for name in omitted:
            (root / name).unlink()
            write(root, name)
        probe('restored_real_notes_complete_inventory', [], 6)
    return results


def retained_suites(files):
    """Run the two unchanged predecessor suites in an offline source export."""
    results = []
    with tempfile.TemporaryDirectory(prefix='pr6334-tests-') as directory:
        root = Path(directory)
        prefix = 'retained/pr6334/'
        for name, raw in files.items():
            if name.startswith(prefix):
                write(root, name[len(prefix):], raw)
        for test, count in [('test_research_overlap_git_paths.py', 7),
                            ('test_research_overlap_local.py', 6)]:
            flags = ['-I', '-B', '-W', 'error'] + (['-O'] if sys.flags.optimize else [])
            result = run([sys.executable, *flags, str(root / 'tests' / test), '-v'],
                         root, environment())
            log = result.stderr.decode('utf-8')
            require(f'Ran {count} tests' in log and '\nOK\n' in log,
                    'unexpected retained suite outcome: ' + test)
            # A skipped suite ends in "OK (skipped=N)", not the exact OK
            # checked above. Test names themselves may contain "skipped".
            results.append({'module': test, 'tests': count, 'skips': 0})
    return results


def main():
    require(os.name == 'posix', 'this audit requires a POSIX filesystem and symlinks')
    require(shutil.which('git') is not None, 'Git is required')
    files = source_bytes()
    results = differential(files)
    suites = retained_suites(files)
    print(json.dumps({'status': 'PASS_PR6334_POSIX_PATH_AUDIT',
                      'python': platform.python_version(), 'platform': platform.platform(),
                      'optimized_cli_children': bool(sys.flags.optimize),
                      'differential_cases': results, 'retained_suites': suites,
                      'source_sha256': PINS,
                      'scope': 'Pinned local path/coverage behavior only; no network, '
                               'current-main repair, supplier replay or theorem proof.'}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({'status': 'FAIL_PR6334_POSIX_PATH_AUDIT', 'error': str(exc)}),
              file=sys.stderr)
        raise SystemExit(1)

#!/usr/bin/env python3
"""Fresh unchanged PR193 six-stage proof with explicit strict portability adapter."""
import sys
if sys.flags.optimize:
    raise SystemExit('Assertions required')
sys.dont_write_bytecode = True
sys.set_int_max_str_digits(0)
import argparse, subprocess, time, types
from common import *


def run(repo, output):
    repo = repo.resolve()
    pkg = repo / 'research/source-assisted-v4'
    work = pkg / '.work'
    assert not work.exists() and not work.is_symlink(), 'Existing complex work'
    before = check_source(repo, 'complex')
    verifier = module('public_pinned193_verify', pkg / 'verify.py')
    assert verifier.pins() == read(pkg / 'SOURCE.json')['files']
    commands = []

    def stage(*args):
        started = time.monotonic()
        label = 'complex-stage-' + str(len(commands) + 1)
        completed = subprocess.run([sys.executable, '-B', *map(str, args)],
                                   cwd=repo, capture_output=True, text=True)
        log = output / (label + '.log')
        log.write_text(completed.stdout + completed.stderr)
        relative_args = []
        for arg in args:
            value = str(arg)
            if Path(value).is_absolute():
                value = Path(value).resolve().relative_to(repo).as_posix()
            relative_args.append(value)
        commands.append(dict(stage=label, arguments=relative_args,
                             exit_code=completed.returncode,
                             seconds=time.monotonic()-started,
                             log=log.name, log_sha256=sha(log)))
        (output / 'complex-commands.json').write_text(json.dumps(commands, indent=2)+'\n')
        assert completed.returncode == 0, 'PR193 stage failed; see ' + label
        return completed.stdout

    def preserve(path, **kwargs):
        assert Path(path) == work and kwargs == {'ignore_errors': True}

    verifier.run = stage
    # Upstream's finally block discards the proof; preserve this new run's evidence.
    verifier.shutil = types.SimpleNamespace(rmtree=preserve)
    actual = verifier.build()
    assert len(commands) == 6 and all(x['exit_code'] == 0 for x in commands)
    assert check_source(repo, 'complex') == before
    write(work / 'canonical-result.json', actual)
    adapter = module('public193_semantic', HERE / 'adapter193/semantic_v2.py')
    published = read(pkg / 'certificate.json')
    semantic = adapter.validate(actual, published, repo)
    write(output / 'complex-acceptance.json', dict(
        status='PASS freshly executed six-stage PR193 proof',
        stages_executed=6, source_pins=before, semantic=semantic,
        direct_upstream_canonical_equality=(actual == published),
        outer_default_entrypoint_executed=False,
        comparison='Explicit exact two-diagnostic and gzip normalization; no historical logs used'))
    return actual


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    run(a.repo, a.output)

#!/usr/bin/env python3
"""Bounded whole-check equality and rejection controls for both exp engines.

Only the twelve pinned inputs and adapter files are copied to a temporary
repository. Mathematical mutation controls deliberately bypass the adapter's
source admission in a child process, so they exercise the unchanged checker.
Normal, source-admission and output controls use the public command directly.
"""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = Path('research/complex-k492-owner-repair')
FIXTURE = Path('research/community-k492-audit/pr622/replay')
ENGINES = ('reference', 'integer')

# This override exists only in the test process for intentionally changed inputs.
# The checker and the adapter's exp substitution still execute unchanged.
MUTATION_DRIVER = '''\
from pathlib import Path
import runpy
import sys
sys.path.insert(0, str(Path(sys.argv[1]).parent))
namespace = runpy.run_path(sys.argv[1])
namespace['replay'].__globals__['check_sources'] = lambda: None
namespace['replay'](sys.argv[2], Path(sys.argv[3]))
'''


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def dump(path, value):
    raw = (json.dumps(value, indent=2) + '\n').encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == '.gz' else raw)


def run_controls():
    started = time.perf_counter()
    source = load(HERE / 'SOURCE.json')
    checks = 0
    with tempfile.TemporaryDirectory(prefix='exact-exp-replay-controls-') as name:
        temporary = Path(name)
        stage = temporary / 'repository'
        adapter = stage / 'research/exact-exp-performance/run.py'
        output_dir = temporary / 'outputs'
        output_dir.mkdir()

        def restore_inputs():
            for relative in source['files']:
                target = stage / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)

        restore_inputs()
        for filename in ('run.py', 'fast_exp.py', 'SOURCE.json'):
            adapter.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / filename, adapter.parent / filename)

        def run(case, engine, *, rejection=None, mutate=False, optimized=True,
                output=None):
            nonlocal checks
            output = output or output_dir / f'{case}-{engine}.json'
            command = [sys.executable, '-B']
            if optimized:
                command.append('-O')
            if mutate:
                command += ['-c', MUTATION_DRIVER, str(adapter), engine, str(output)]
            else:
                command += [str(adapter), '--engine', engine, '--out', str(output)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            if rejection is None:
                need(result.returncode == 0, f'{case}/{engine}: {result.stderr}')
                need('PASS independent map and exact moments' in result.stdout,
                     f'{case}/{engine}: checker did not finish')
                need(hashlib.sha256(output.read_bytes()).hexdigest()
                     == source['owner_receipt_sha256'],
                     f'{case}/{engine}: receipt differs from frozen reference')
            else:
                need(result.returncode != 0 and rejection in result.stderr,
                     f'{case}/{engine}: expected {rejection!r}, got '
                     f'{result.returncode}, {result.stderr!r}')
            checks += 1
            return output

        reports = []
        for optimized in (False, True):
            for engine in ENGINES:
                reports.append(run('positive-O' if optimized else 'positive', engine,
                                   optimized=optimized).read_bytes())
        need(all(report == reports[0] for report in reports),
             'Whole reports differ between engines or under -O')

        reused = output_dir / 'existing.json'
        sentinel = b'existing output must survive\n'
        reused.write_bytes(sentinel)
        for engine in ENGINES:
            run('output-reuse', engine, output=reused,
                rejection='Use a fresh output path outside the repository')
            need(reused.read_bytes() == sentinel, 'Existing output was overwritten')
            inside = stage / f'forbidden-{engine}.json'
            run('output-in-repository', engine, output=inside,
                rejection='Use a fresh output path outside the repository')
            need(not inside.exists(), 'Output was written inside the repository')

        spec_path = stage / PACKAGE / 'data/SPEC.json'
        spec_path.write_bytes(spec_path.read_bytes() + b'\n')
        for engine in ENGINES:
            run('source-tamper', engine, rejection='Pinned input changed:')
        restore_inputs()
        missing = stage / FIXTURE / 'jp8-local/LOCAL-PROGRAMS.json.gz'
        missing.unlink()
        for engine in ENGINES:
            run('source-missing', engine, rejection='FileNotFoundError')
        restore_inputs()

        manifest_path = adapter.parent / 'SOURCE.json'
        changed_manifest = load(manifest_path)
        changed_manifest['owner_receipt_sha256'] = '0' * 64
        dump(manifest_path, changed_manifest)
        for engine in ENGINES:
            run('receipt-tamper', engine, rejection='Owner receipt differs from pinned reference')
        shutil.copyfile(HERE / 'SOURCE.json', manifest_path)

        def reject_mutation(case, reason):
            for engine in ENGINES:
                output = output_dir / f'{case}-{engine}.json'
                run(case, engine, rejection='ValueError: ' + reason, mutate=True,
                    output=output)
                need(not output.exists(), f'{case}/{engine}: rejected checker wrote a receipt')
            restore_inputs()

        for label, relative in (('candidate', 'data/SPEC.json'),
                                ('PR623', 'comparison/PR623-SPEC.json')):
            path = stage / PACKAGE / relative
            spec = load(path)
            spec['expected']['complex_lower'] = '1/100'
            dump(path, spec)
            reject_mutation('moment-' + label, 'strict exact moment ' + label)

        for case, field, value, reason in (
                ('owner-width', 'width', None, 'actual width'),
                ('owner-family', 'family', None, 'physical family'),
                ('owner-call', 'stage', None, 'ordered complete call'),
                ('owner-footprint', 'offset', 1000000, 'window and footprint')):
            path = stage / PACKAGE / 'data/OWNERS.json.gz'
            roles = load(path)
            roles[0][field] = roles[0][field] + 1 if value is None else value
            dump(path, roles)
            spec = load(spec_path)
            spec['data']['owners_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            dump(spec_path, spec)
            reject_mutation(case, reason)

        plan_path = stage / PACKAGE / 'data/PLAN.json'
        plan = load(plan_path)
        plan['provider_calls'][0]['time'] = plan['provider_calls'][1]['time']
        dump(plan_path, plan)
        spec = load(spec_path)
        spec['data']['plan_sha256'] = hashlib.sha256(plan_path.read_bytes()).hexdigest()
        dump(spec_path, spec)
        reject_mutation('plan-chronology', 'complete chronology')

        canonical_path = stage / FIXTURE / 'jp8-local/CANONICAL-WORD.json.gz'
        canonical = load(canonical_path)
        canonical['test_only_metadata'] = True
        dump(canonical_path, canonical)
        reject_mutation('native-hash', 'unchanged PR622 native word and program')

        programs_path = stage / FIXTURE / 'jp8-local/LOCAL-PROGRAMS.json.gz'
        programs = load(programs_path)
        paid_event = next(event for event in programs['forward']
                          if event[0] in ('climb', 'center'))
        paid_event[-1] += 1
        dump(programs_path, programs)
        native_hashes_path = stage / PACKAGE / 'comparison/PR622-NATIVE-HASHES.json'
        native_hashes = load(native_hashes_path)
        native_hashes['jp8/LOCAL-PROGRAMS.json.gz'] = hashlib.sha256(
            programs_path.read_bytes()).hexdigest()
        dump(native_hashes_path, native_hashes)
        reject_mutation('native-orientation', 'both actual orientations')

    print(f'PASS {checks} whole-check subprocess controls; exact receipt equality, '
          f'both engines, and -O ({time.perf_counter() - started:.3f}s)')


class ReplayTests(unittest.TestCase):
    def test_full_replay(self):
        run_controls()


if __name__ == '__main__':
    unittest.main()

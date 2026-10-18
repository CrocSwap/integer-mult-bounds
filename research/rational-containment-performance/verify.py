"""Reproduce exact customer equivalence, arithmetic controls and one paired timing."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from adapter import check_sources
from benchmark import benchmark, EXPECTED
from kernel import Containment

EXPECTED_TRACE = '26d55e53c7e9f7ae83b3f3d3c4e9c91735e57f11a1f0db54bb02e895bc867157'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(command, *, failure=None):
    result = subprocess.run(command, capture_output=True, text=True, timeout=120, cwd=ROOT)
    if failure is None:
        require(result.returncode == 0, result.stdout + result.stderr)
    else:
        require(result.returncode != 0 and failure in result.stdout + result.stderr,
                'Expected deliberate rejection: ' + failure)
    return result


def source_controls(work):
    inputs = [item for item in json.loads((PACKAGE / 'SOURCES.json').read_text())['files']
              if item['usage'] == 'input']
    copied = work / 'source-controls'
    for item in inputs:
        target = copied / item['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / item['path'], target)
    check_sources(copied)
    rejected = []
    for item in inputs:
        target = copied / item['path']
        original = target.read_bytes()
        target.write_bytes(original + b'\n# deliberate source mutation\n')
        try:
            check_sources(copied)
        except ValueError as error:
            require(str(error) == 'Changed pinned input: ' + item['path'], str(error))
            rejected.append(item['path'])
        else:
            raise ValueError('Source mutation accepted: ' + item['path'])
        finally:
            target.write_bytes(original)
    return rejected


def frame_controls():
    sys.path.insert(0, str(ROOT / 'scripts'))
    import rational_span_frames as frames
    from experiments.mixed_point_circuit import build, factored_transpose
    circuit, _ = factored_transpose(build(10, 3, 3, 1))
    source, target = frames.spans(circuit)
    dual = set()
    for node in circuit.active:
        if not frames.nondegenerate(source[node]) or (circuit.args[node] and
                any(parent in dual for parent in circuit.args[node])):
            dual.add(node)
    labels = {node: frames.orthogonal(target[node], circuit.n) if node in dual else source[node]
              for node in circuit.active}
    first_gate = next(node for node in circuit.active if circuit.args[node])
    empty = dict(labels)
    empty[first_gate] = ()
    full = tuple(tuple(int(i == j) for i in range(circuit.n)) for j in range(circuit.n))
    bad_injections = dict.fromkeys(circuit.active, full)
    reference = frames.contained
    outcomes = {}
    try:
        for name, changed, expected in (('decreasing_side_frame', empty, 'Decreasing forward side edge'),
                                       ('wrong_injection_frame', bad_injections, 'Wrong forward injection frame')):
            receipts = []
            for engine in (reference, Containment()):
                frames.contained = engine
                frames.compiled_frames(circuit, labels)
                try:
                    frames.compiled_frames(circuit, changed)
                except ValueError as error:
                    require(str(error) == expected, str(error))
                    receipts.append(str(error))
                else:
                    raise ValueError('Mutated frame accepted: ' + name)
            require(receipts[0] == receipts[1], 'Frame rejection mismatch')
            outcomes[name] = receipts
    finally:
        frames.contained = reference
    return outcomes


def verify(work):
    check_sources()
    kernels = {}
    for optimized in (False, True):
        command = [sys.executable, '-I', '-B'] + (['-O'] if optimized else [])
        command += [str(PACKAGE / 'test_kernel.py')] + ([] if optimized else ['--mutations'])
        result = run(command)
        kernels['optimized' if optimized else 'normal'] = json.loads(result.stdout.strip().splitlines()[-1])
        (work / ('kernel-optimized.log' if optimized else 'kernel.log')).write_text(result.stdout + result.stderr)
    rejected_sources = source_controls(work)
    rejected_frames = frame_controls()
    adapter = [sys.executable, '-I', '-B', str(PACKAGE / 'adapter.py')]
    outputs = {}
    for engine in ('reference', 'annihilator', 'compare'):
        output = work / (engine + '.json')
        command = adapter + ['--engine', engine, '--output', str(output)]
        if engine == 'compare':
            command += ['--trace', str(work / 'trace.json')]
        run(command)
        outputs[engine] = json.loads(output.read_text())
    for record in outputs.values():
        require(record['result'] == outputs['reference']['result'], 'Full audit output differs')
        digest = hashlib.sha256(json.dumps(record['result'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        require(digest == EXPECTED == record['result_sha256'], 'Wrong complete payload hash')
    trace = json.loads((work / 'trace.json').read_text())
    require(trace['compared_calls'] == 42860 and trace['distinct_targets'] == 7614
            and trace['transcript_sha256'] == EXPECTED_TRACE, 'Containment coverage drift')
    # Guard controls are actual adapter processes, not merely kernel simulations.
    run(adapter + ['--engine', 'annihilator', '--output', str(work / 'reference.json')],
        failure='Use fresh output paths')
    run([sys.executable, '-I', '-B', '-O', str(PACKAGE / 'adapter.py'), '--engine', 'annihilator',
         '--output', str(work / 'optimized-must-not-exist.json')], failure='inherited checker assertions')
    require(not (work / 'optimized-must-not-exist.json').exists(), 'Optimized adapter wrote output')
    measured = benchmark(1)
    (work / 'benchmark.json').write_text(json.dumps(measured, indent=2) + '\n')
    result = dict(status='PASS_RATIONAL_CONTAINMENT', kernel_tests=kernels,
                  source_mutations_rejected=rejected_sources, frame_mutations_rejected=rejected_frames,
                  adapter_controls=['existing_output_rejected', 'optimized_python_rejected'],
                  compared_calls=trace['compared_calls'], distinct_targets=trace['distinct_targets'],
                  transcript_sha256=EXPECTED_TRACE, result_sha256=EXPECTED,
                  benchmark_process_wall_ratio=measured['process_wall_ratio'])
    (work / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional fresh evidence directory')
    args = parser.parse_args()
    if sys.flags.optimize:
        raise SystemExit('Run without -O: inherited checker assertions must remain enabled')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        result = verify(args.output.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='rational-containment-') as temporary:
            result = verify(Path(temporary))
    print(result['status'], 'calls=' + str(result['compared_calls']),
          'kernel_mutants=4', 'source_mutants=6', 'frame_mutants=2', 'adapter_controls=2')

#!/usr/bin/env python3
"""Mutate literal inputs after hash admission; require semantic Lean rejection.

Each case first compiles its unmutated control. Failures due to imports or a
broken test harness do not count as rejected mutations. No package file changes.
"""
import json
from pathlib import Path
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
PRELUDE = '''import LevelFrameJoins
import LevelSchedule
open PR442LevelModel
set_option maxHeartbeats 0
set_option maxRecDepth 100000
'''
CASES = [
    ('entrance_frame_id', '2', '0', '''
def candidate : Fin 944 := VALUE
example : FrameGeometry.scaled candidate 0 0 = rootVector 0 0 * rootVector 0 0 := by decide
'''),
    ('root_coordinate', '2', '3', '''
def candidate : Int := VALUE
example : FrameGeometry.scaled (sourceEntrance 0) 0 0 = candidate * candidate := by decide
'''),
    ('stage2_axis', '15', '14', '''
def candidate := (routeAxes 0 2).set 8 VALUE
example : candidate = List.range 8 ++ List.range' 15 7 := by decide
'''),
    ('reflected_call_orientation', 'true', 'false', '''
def candidate := schedulePrefix.set 1 (.local 1 0 VALUE)
def observed := (replay candidate initialOrigins []).bind
  (fun s => s.2.find? (fun o => o.idx == 1))
example : observed = some
  ⟨1, 1, 7, 2, 3, .localExit 1 true, .localExit 2 false⟩ := by decide
'''),
    ('recorded_source_level', '2', '1', '''
def candidate := schedulePrefix.set 5 (.idle 1 1 7 VALUE 3)
def consistent := (replay candidate initialOrigins []).map
  (fun s => s.2.all (fun o => o.recordedSource == levelTag o.before &&
    o.recordedTarget == levelTag o.after))
example : consistent = some true := by decide
'''),
]


def run(lake):
    results = []
    for name, original, changed, source in CASES:
        record = {'name': name}
        for kind, value in [('positive', original), ('mutated', changed)]:
            with tempfile.TemporaryDirectory(prefix='level-control-', dir=HERE / '.lake') as tmp:
                path = Path(tmp) / 'Control.lean'
                path.write_text(PRELUDE + source.replace('VALUE', value))
                start = time.monotonic()
                result = subprocess.run([lake, 'env', 'lean', str(path)], cwd=HERE,
                                        text=True, capture_output=True, timeout=120)
                output = result.stdout + result.stderr
                if kind == 'positive':
                    if result.returncode:
                        raise RuntimeError(f'Broken positive control {name}:\n{output}')
                elif not (result.returncode and "tactic 'decide' proved that" in output
                          and 'is false' in output):
                    raise RuntimeError(f'Mutation not rejected semantically {name}:\n{output}')
                record[kind] = {'exit_code': result.returncode,
                                'seconds': round(time.monotonic() - start, 3),
                                'diagnostic': output.replace(str(path), 'Control.lean').strip()}
        results.append(record)
        print('PASS_CONTROL ' + name, flush=True)
    return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lake', default='lake')
    print(json.dumps(run(parser.parse_args().lake), indent=2))

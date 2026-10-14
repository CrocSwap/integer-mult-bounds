#!/usr/bin/env python3
"""Compile positive witnesses and require semantic rejection of input mutations.

Every candidate proposition is first checked by `#check`, separately from its
attempted proof. Import, syntax, typing, missing-instance and resource-limit
failures never count as successful rejection. No package source is mutated.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
PRELUDE = '''import IdleOperators
open PR442LevelModel PR442LevelModel.Phase2
open scoped Matrix BigOperators
'''

# (name, original input, mutant input, declarations, closed proposition).
# These inputs are changed only after the verifier admits their source hashes.
CASES = [
    ('entrance_frame_id', '2', '0',
     'def candidate : Fin 944 := VALUE\n',
     'FrameGeometry.scaled candidate 0 0 = rootVector 0 0 * rootVector 0 0'),
    ('root_coordinate', '2', '3',
     'def candidate : Int := VALUE\n',
     'FrameGeometry.scaled (sourceEntrance 0) 0 0 = candidate * candidate'),
    ('stage2_axis', '15', '14',
     'def candidate := (routeAxes 0 2).set 8 VALUE\n',
     "candidate = List.range 8 ++ List.range' 15 7"),
    ('reflected_call_orientation', 'true', 'false',
     '''def candidate := schedulePrefix.set 1 (.local 1 0 VALUE)
def observed := (replay candidate initialOrigins []).bind
  (fun s => s.2.find? (fun o => o.idx == 1))
''',
     'observed = some ⟨1, 1, 7, 2, 3, .localExit 1 true, .localExit 2 false⟩'),
    ('reflection_side_swap', '!false', 'false',
     '''def candidateSide : Bool := VALUE
def candidateFrame := if candidateSide then targetEntrance 0 else sourceEntrance 0
''',
     'candidateFrame = (localEndpoint 0 1 true true false).frame'),
    ('bridge_partner', '1', '2',
     '''def candidate := schedulePrefix.set 6 (.bridge 0 VALUE (-1))
def observed := (replay candidate initialOrigins []).bind
  (fun s => s.2.find? (fun o => o.idx == 1))
''',
     'observed = some ⟨1, 1, 7, 2, 3, .localExit 1 true, .localExit 2 false⟩'),
    ('cumulative_exterior', 'exteriorAxes 0 3', '(routeAxes 0 3).drop 8',
     '''def candidateExterior : List Nat := VALUE
def literal := localEndpoint 0 3 true true false
def candidate := { literal with exterior := candidateExterior }
def retainedExterior : Fin 64 → ℚ := fun i => if i = 8 then 1 else 0
''',
     'endpointOperator ℚ 0 candidate retainedExterior 8 = 1'),
    ('local8_complement_before_extension', 'true', 'false',
     '''def chooseLocal8 : Bool := VALUE
def reflected := localEndpoint 0 1 true true false
def outside : Fin 64 → ℚ := fun i => if i = 63 then 1 else 0
def candidate : Fin 64 → ℚ :=
  if chooseLocal8 then endpointOperator ℚ 0 reflected outside
  else outside - endpointOperator ℚ 0 { reflected with complemented := false } outside
''',
     'candidate 63 = 0'),
]


def run(lake):
    results = []
    for name, original, changed, declarations, proposition in CASES:
        record = {'name': name, 'originalInput': original, 'mutatedInput': changed}
        for kind, value in [('positive', original), ('mutated', changed)]:
            admitted = PRELUDE + declarations.replace('VALUE', value) + '\n#check (' + proposition + ')\n'
            attempted = admitted + '\nexample : ' + proposition + ' := by decide\n'
            with tempfile.TemporaryDirectory(prefix='phase2-control-', dir=HERE / '.lake') as tmp:
                directory = Path(tmp)
                typed = directory / 'Typed.lean'
                typed.write_text(admitted)
                proof = directory / 'Control.lean'
                proof.write_text(attempted)
                tick = time.monotonic()
                typecheck = subprocess.run([lake, 'env', 'lean', str(typed)], cwd=HERE,
                                           text=True, capture_output=True, timeout=120)
                typed_output = typecheck.stdout + typecheck.stderr
                if typecheck.returncode:
                    raise RuntimeError(f'Ill-typed control {name}/{kind}:\n{typed_output}')
                result = subprocess.run([lake, 'env', 'lean', str(proof)], cwd=HERE,
                                        text=True, capture_output=True, timeout=120)
                output = result.stdout + result.stderr
                if kind == 'positive':
                    if result.returncode:
                        raise RuntimeError(f'Broken positive control {name}:\n{output}')
                elif not (result.returncode and "tactic 'decide' proved that" in output
                          and 'is false' in output):
                    raise RuntimeError(f'Mutation not rejected semantically {name}:\n{output}')
                record[kind] = {'exitCode': result.returncode, 'typecheckExitCode': typecheck.returncode,
                                'seconds': round(time.monotonic() - tick, 3),
                                'sourceSha256': hashlib.sha256(attempted.encode()).hexdigest(),
                                'diagnostic': output.replace(str(directory) + '/', '').strip()}
        results.append(record)
        print('PASS_CONTROL ' + name, flush=True)
    return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lake', default='lake')
    print(json.dumps(run(parser.parse_args().lake), indent=2))

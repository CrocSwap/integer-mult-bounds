#!/usr/bin/env python3
"""Compile positive witnesses and require semantic rejection of input mutations.

Every candidate proposition is first checked by `#check`, separately from its
attempted proof. Import, syntax, typing, missing-instance and resource-limit
failures never count as successful rejection. No package source is mutated.
Large tables are rewritten through kernel-certified joins before residual
`decide`; the literal root-coordinate certificate uses `decide +kernel`.
Both paths retain default settings and never invoke native evaluation.
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

# Rewrite the large certified frame table through its checked joins before
# computing a small residual proposition. The same proof body is used for
# each admitted original input and its mutant, under default Lean options.
PROOFS = {
    'entrance_frame_id': '''  have hframe : sourceEntrance (0 : Port) = (2 : Fin 944) := by
    apply Fin.ext
    simpa only [Fin.val_zero, Nat.zero_add] using (endpoint_label_values (0 : Port)).1
  have hroot : rootVector 0 0 = (2 : Int) := by decide +kernel
  have hscaled : FrameGeometry.scaled (2 : Fin 944) 0 0 = 4 := by
    rw [← hframe, entrance_scaled, hroot]
    decide
  simp only [candidate, hscaled, FrameGeometry.scaled_zero_entries, hroot]
  all_goals decide
''',
    'root_coordinate': '''  have hroot : rootVector 0 0 = (2 : Int) := by decide +kernel
  rw [entrance_scaled, hroot]
  simp only [candidate]
  all_goals decide
''',
    'stage2_axis': '''  unfold candidate
  have haxes : routeAxes 0 2 = blockAxes (⟨1, by decide⟩ : Fin 3) :=
    route_axes_positive 0 ⟨1, by decide⟩
  rw [haxes]
  decide
''',
    'reflection_side_swap': '''  have hs : sourceEntrance (0 : Port) = (2 : Fin 944) := by
    apply Fin.ext
    simpa only [Fin.val_zero, Nat.zero_add] using (endpoint_label_values (0 : Port)).1
  have ht : targetEntrance (0 : Port) = (0 : Fin 944) :=
    (endpoint_label_values (0 : Port)).2.1
  change (if candidateSide then targetEntrance 0 else sourceEntrance 0) = targetEntrance 0
  rw [hs, ht]
  unfold candidateSide
  decide
''',
    'cumulative_exterior': '''  have houtside (e : Endpoint) (v : Fin 64 → ℚ) (i : Fin 64)
      (hi : ¬i.val < 8) (hlen : e.axes.length ≠ 8)
      (hidx : ¬e.axes.idxOf i.val < 15) :
      endpointOperator ℚ 0 e v i = if e.exterior.contains i.val then v i else 0 := by
    simp only [endpointOperator, axisRoute, if_neg hlen, dif_neg hidx,
      liftedOperator, dif_neg hi]
  have haxes : routeAxes 0 3 = blockAxes (⟨2, by decide⟩ : Fin 3) :=
    route_axes_positive 0 ⟨2, by decide⟩
  have ha : candidate.axes = blockAxes (⟨2, by decide⟩ : Fin 3) := by
    simpa only [candidate, literal, localEndpoint_axes] using haxes
  have hlen : candidate.axes.length ≠ 8 := by rw [ha, blockAxes_length]; decide
  have hidx : ¬candidate.axes.idxOf (8 : Fin 64).val < 15 := by rw [ha]; decide
  rw [houtside candidate retainedExterior 8 (by decide) hlen hidx]
  have update_exterior (e : Endpoint) (ext : List Nat) :
      ({ e with exterior := ext } : Endpoint).exterior = ext := by rfl
  have hv : retainedExterior 8 = 1 := by decide
  delta candidate
  rw [update_exterior, hv]
  have hext : (exteriorAxes 0 3).contains 8 = true := by
    simpa using exterior_axes_contains 0 (⟨3, by decide⟩ : Fin 4) (⟨8, by decide⟩ : Fin 64)
  simp only [show (8 : Fin 64).val = 8 from rfl, candidateExterior, hext, haxes]
  all_goals decide
''',
    'local8_complement_before_extension': '''  have houtside (e : Endpoint) (v : Fin 64 → ℚ) (i : Fin 64)
      (hi : ¬i.val < 8) (hlen : e.axes.length ≠ 8)
      (hidx : ¬e.axes.idxOf i.val < 15) :
      endpointOperator ℚ 0 e v i = if e.exterior.contains i.val then v i else 0 := by
    simp only [endpointOperator, axisRoute, if_neg hlen, dif_neg hidx,
      liftedOperator, dif_neg hi]
  have haxes : routeAxes 0 1 = blockAxes (⟨0, by decide⟩ : Fin 3) :=
    route_axes_positive 0 ⟨0, by decide⟩
  have ha : reflected.axes = blockAxes (⟨0, by decide⟩ : Fin 3) := by
    simpa only [reflected, localEndpoint_axes] using haxes
  have hlen : reflected.axes.length ≠ 8 := by rw [ha, blockAxes_length]; decide
  have hidx : ¬reflected.axes.idxOf (63 : Fin 64).val < 15 := by rw [ha]; decide
  have hext : reflected.exterior.contains 63 = false := by
    have h : (exteriorAxes 0 1).contains 63 = false := by
      simpa using exterior_axes_contains 0 (⟨1, by decide⟩ : Fin 4) (⟨63, by decide⟩ : Fin 64)
    simpa only [reflected, localEndpoint_exterior] using h
  have hlocal : endpointOperator ℚ 0 reflected outside 63 = 0 := by
    rw [houtside reflected outside 63 (by decide) hlen hidx]
    simp only [show (63 : Fin 64).val = 63 from rfl, hext, Bool.false_eq_true, if_false]
  have update_axes (e : Endpoint) (b : Bool) :
      ({ e with complemented := b } : Endpoint).axes = e.axes := rfl
  have update_exterior (e : Endpoint) (b : Bool) :
      ({ e with complemented := b } : Endpoint).exterior = e.exterior := rfl
  have hambientBase : endpointOperator ℚ 0 { reflected with complemented := false } outside 63 = 0 := by
    have hlen' : ({ reflected with complemented := false } : Endpoint).axes.length ≠ 8 := by
      rw [update_axes]
      exact hlen
    have hidx' : ¬({ reflected with complemented := false } : Endpoint).axes.idxOf (63 : Fin 64).val < 15 := by
      rw [update_axes]
      exact hidx
    rw [houtside { reflected with complemented := false } outside 63 (by decide) hlen' hidx', update_exterior]
    simp only [show (63 : Fin 64).val = 63 from rfl, hext, Bool.false_eq_true, if_false]
  simp only [candidate, chooseLocal8, Bool.true_eq, Bool.false_eq_true, if_true,
    if_false, Pi.sub_apply, hlocal, hambientBase, outside, sub_zero]
  all_goals decide
''',
}


def run(lake):
    results = []
    for name, original, changed, declarations, proposition in CASES:
        record = {'name': name, 'originalInput': original, 'mutatedInput': changed}
        for kind, value in [('positive', original), ('mutated', changed)]:
            admitted = PRELUDE + declarations.replace('VALUE', value) + '\n#check (' + proposition + ')\n'
            attempted = admitted + '\nexample : ' + proposition + ' := by\n' + PROOFS.get(name, '  decide\n')
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

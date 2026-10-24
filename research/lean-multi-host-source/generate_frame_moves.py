#!/usr/bin/env python3
"""Bind each literal MOVE to FrameData's certified source transition.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def search(pairs, start=0):
    if len(pairs) == 1:
        return str(start)
    half = len(pairs) // 2
    old, new = pairs[half]
    return (f'(if n < {944 * old + new} then {search(pairs[:half], start)} '
            f'else {search(pairs[half:], start + half)})')


def render(template):
    raw = template.read_bytes()
    if template.suffix == '.gz':
        raw = gzip.decompress(raw)
    assert hashlib.sha256(raw).hexdigest() == 'dd7833dcaff8c84b258847f4c4d65b6402c702700ae37d2c464083ee37b24126'
    events = json.loads(raw)['local_programs']['forward']
    pairs = sorted({(e[2], e[3]) for e in events if e[0] == 0})
    assert len(events) == 19002 and len(pairs) == 3357
    assert sum(e[0] == 0 for e in events) == 4291
    assert all(0 <= a < 944 and 0 <= b < 944 for a, b in pairs)
    return '''import FrameData
import FrameTraceLiterals

/-!
Each of the actual4291 MOVE events selects one of FrameData's3357 certified
transition pairs. The balanced index is only an untrusted search aid; the
kernel checks the selected pair against the literal old/new frame labels.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
-/
namespace SourceFrameMoves
set_option maxRecDepth 100000
set_option maxHeartbeats 0

''' + f'def pairSearch (n : Nat) : Nat :=\n  {search(pairs)}\n\n' + '''def moveIndex (e : FrameTrace.Entry) : Fin 3357 :=
  ⟨pairSearch (944 * e.oldFrame + e.newFrame) % 3357, Nat.mod_lt _ (by decide)⟩

def moveCheck (e : FrameTrace.Entry) : Bool :=
  decide (e.scalar.op = 0 →
    (FrameGeometry.transition (moveIndex e)).1.val = e.oldFrame ∧
    (FrameGeometry.transition (moveIndex e)).2.val = e.newFrame)

theorem moves_checked : SourceFrameTrace.forward.all moveCheck = true := by decide +kernel

theorem move_pair (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward)
    (hop : e.scalar.op = 0) :
    (FrameGeometry.transition (moveIndex e)).1.val = e.oldFrame ∧
    (FrameGeometry.transition (moveIndex e)).2.val = e.newFrame := by
  have h := List.all_eq_true.mp moves_checked e he
  exact of_decide_eq_true h hop

theorem move_range (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward)
    (hop : e.scalar.op = 0) : e.oldFrame < 944 ∧ e.newFrame < 944 := by
  obtain ⟨ha, hb⟩ := move_pair e he hop
  exact ⟨ha ▸ (FrameGeometry.transition (moveIndex e)).1.isLt,
    hb ▸ (FrameGeometry.transition (moveIndex e)).2.isLt⟩

def oldIndex (e : FrameTrace.Entry) : Fin 944 :=
  ⟨e.oldFrame % 944, Nat.mod_lt _ (by decide)⟩

def newIndex (e : FrameTrace.Entry) : Fin 944 :=
  ⟨e.newFrame % 944, Nat.mod_lt _ (by decide)⟩

theorem move_transition (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward)
    (hop : e.scalar.op = 0) :
    FrameGeometry.transition (moveIndex e) = (oldIndex e, newIndex e) := by
  obtain ⟨ha, hb⟩ := move_pair e he hop
  obtain ⟨hra, hrb⟩ := move_range e he hop
  apply Prod.ext
  · apply Fin.ext
    simpa only [oldIndex, Nat.mod_eq_of_lt hra] using ha
  · apply Fin.ext
    simpa only [newIndex, Nat.mod_eq_of_lt hrb] using hb

/-- Every actual source MOVE satisfies the checked nested-projector identity. -/
theorem move_absorbs (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward)
    (hop : e.scalar.op = 0) : FrameGeometry.Absorbs (oldIndex e) (newIndex e) := by
  have h := FrameGeometry.transition_absorbs (moveIndex e)
  rw [move_transition e he hop] at h
  exact h

end SourceFrameMoves
#print axioms SourceFrameMoves.moves_checked
#print axioms SourceFrameMoves.move_range
#print axioms SourceFrameMoves.move_transition
#print axioms SourceFrameMoves.move_absorbs
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    source = render(args.template)
    if args.check:
        assert args.out.read_text() == source, 'FrameMoveData.lean changed'
    else:
        args.out.write_text(source)
    print(f'PASS: 4291 literal MOVE events, 3357 certified pairs; {len(source)} source characters')


if __name__ == '__main__':
    main()

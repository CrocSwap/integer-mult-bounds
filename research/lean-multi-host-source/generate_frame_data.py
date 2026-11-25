#!/usr/bin/env python3
"""Emit untrusted witnesses; Lean checks every integer matrix identity.

The source frame rows are literal. SymPy computes witnesses only: projectors
and an inverse of [B; A]. No SymPy answer is a trusted proof. --check rerenders
every generated module, including source hashes and the MOVE transition set.
Independent certificate batches let Lake check them in parallel. Splitting
changes imports and declaration locations only, preserving declaration text.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import sympy as sp


def array(rows):
    return '#[' + ', '.join('#[' + ', '.join(map(str, row)) + ']' for row in rows) + ']'


def branch(names, start=0):
    if len(names) == 1:
        return names[0]
    half = len(names) // 2
    return f'(if n < {start + half} then {branch(names[:half], start)} else {branch(names[half:], start + half)})'


def render_monolith(frames_path, template_path):
    raw = frames_path.read_bytes()
    template_raw = template_path.read_bytes()
    frames = json.loads(raw)['frames']
    template = json.loads(gzip.decompress(template_raw))
    assert sorted(map(int, frames)) == list(range(944))
    matrices = []
    lines = ['''import Std

/-!
Literal PR442 inherited frame rows, with independently checked integer
witnesses. Apache-2.0. Prepared with substantial OpenAI Codex assistance.
The balanced lookup stores proofs alongside each frame; no native_decide,
external solver axiom, or sampled field arithmetic is used.
''', f'frames.json SHA-256: {hashlib.sha256(raw).hexdigest()}',
        f'GLOBAL-TEMPLATE.json.gz SHA-256: {hashlib.sha256(template_raw).hexdigest()}',
        '''-/
namespace FrameGeometry
set_option maxRecDepth 100000
set_option maxHeartbeats 0

abbrev IntMatrix8 := Fin 8 → Fin 8 → Int
def entry (a : Array (Array Int)) : IntMatrix8 :=
  fun i j => (a.getD i.val #[]).getD j.val 0

def dot8 (a b : IntMatrix8) (i j : Fin 8) : Int :=
  a i 0 * b 0 j + (a i 1 * b 1 j + (a i 2 * b 2 j +
  (a i 3 * b 3 j + (a i 4 * b 4 j + (a i 5 * b 5 j +
  (a i 6 * b 6 j + (a i 7 * b 7 j + 0)))))))

structure FrameDatum where
  dimension : Nat
  scaled : Array (Array Int)
  /-- Exactly the source's B rows followed by its A rows. -/
  stack : Array (Array Int)
  /-- Untrusted witness for 256 times the inverse of stack. -/
  inverse256 : Array (Array Int)

def ValidFrame (d : FrameDatum) : Prop :=
  d.dimension ≤ 8 ∧
  (∀ i j : Fin 8, dot8 (entry d.scaled) (entry d.scaled) i j = 4 * entry d.scaled i j) ∧
  (∀ i j : Fin 8, entry d.scaled i j = entry d.scaled j i) ∧
  (∀ i j : Fin 8, dot8 (entry d.scaled) (fun a b => entry d.stack b a) i j =
    if j.val < d.dimension then 4 * entry d.stack j i else 0) ∧
  (∀ i j : Fin 8, dot8 (entry d.stack) (entry d.inverse256) i j =
    if i = j then 256 else 0) ∧
  (∀ i j : Fin 8, dot8 (entry d.inverse256) (entry d.stack) i j =
    if i = j then 256 else 0)

instance (d : FrameDatum) : Decidable (ValidFrame d) := by
  unfold ValidFrame
  infer_instance

abbrev CertifiedFrame := { d : FrameDatum // ValidFrame d }
''']
    for n in range(944):
        f = frames[str(n)]
        rows = f['B'] + f['A']
        assert len(rows) == 8 and all(len(r) == 8 for r in rows)
        assert len(f['B']) == f['dim']
        stack = sp.Matrix(rows)
        inv = 256 * stack.inv()
        b = sp.Matrix(f['B']) if f['B'] else sp.zeros(0, 8)
        p = b.T * (b * b.T).inv() * b if f['B'] else sp.zeros(8)
        scaled = 4 * p
        assert all(x.q == 1 for x in inv) and all(x.q == 1 for x in scaled)
        matrices.append(scaled)
        lines.append(f'def certified{n} : CertifiedFrame :=\n  ⟨{{ dimension := {f["dim"]}, scaled := {array(scaled.tolist())},\n'
                     f'     stack := {array(rows)},\n     inverse256 := {array(inv.tolist())} }}, by decide⟩\n')
    lines.append('def lookup (n : Nat) : CertifiedFrame :=\n  ' + branch([f'certified{n}' for n in range(944)]))
    lines.append('''
def frame (f : Fin 944) : FrameDatum := (lookup f.val).val
def scaled (f : Fin 944) : IntMatrix8 := entry (frame f).scaled
def stack (f : Fin 944) : IntMatrix8 := entry (frame f).stack
def inverse256 (f : Fin 944) : IntMatrix8 := entry (frame f).inverse256

theorem frame_valid (f : Fin 944) : ValidFrame (frame f) := (lookup f.val).property
theorem scaled_idempotent_entries (f : Fin 944) (i j : Fin 8) :
    dot8 (scaled f) (scaled f) i j = 4 * scaled f i j := (frame_valid f).2.1 i j
theorem scaled_symmetric_entries (f : Fin 944) (i j : Fin 8) :
    scaled f i j = scaled f j i := (frame_valid f).2.2.1 i j
theorem scaled_stack_entries (f : Fin 944) (i j : Fin 8) :
    dot8 (scaled f) (fun a b => stack f b a) i j =
      if j.val < (frame f).dimension then 4 * stack f j i else 0 :=
  (frame_valid f).2.2.2.1 i j
theorem stack_inverse_entries (f : Fin 944) (i j : Fin 8) :
    dot8 (stack f) (inverse256 f) i j = if i = j then 256 else 0 :=
  (frame_valid f).2.2.2.2.1 i j
theorem inverse_stack_entries (f : Fin 944) (i j : Fin 8) :
    dot8 (inverse256 f) (stack f) i j = if i = j then 256 else 0 :=
  (frame_valid f).2.2.2.2.2 i j

def Absorbs (small large : Fin 944) : Prop :=
  (∀ i j : Fin 8, dot8 (scaled small) (scaled large) i j = 4 * scaled small i j) ∧
  (∀ i j : Fin 8, dot8 (scaled large) (scaled small) i j = 4 * scaled small i j)
''')
    lines.append('instance (small large : Fin 944) : Decidable (Absorbs small large) := by\n  unfold Absorbs\n  infer_instance\n')
    pairs = sorted({(e[2], e[3]) for e in template['local_programs']['forward'] if e[0] == 0})
    for k, (a, b) in enumerate(pairs):
        assert matrices[a] * matrices[b] == 4 * matrices[a]
        assert matrices[b] * matrices[a] == 4 * matrices[a]
        lines.append(f'def transition{k} : {{ p : Fin 944 × Fin 944 // Absorbs p.1 p.2 }} :=\n  ⟨({a}, {b}), by decide⟩')
    lines.append(f'def transitionLookup (n : Nat) : {{ p : Fin 944 × Fin 944 // Absorbs p.1 p.2 }} :=\n  ' + branch([f'transition{k}' for k in range(len(pairs))]))
    lines.append(f'''def transition (n : Fin {len(pairs)}) : Fin 944 × Fin 944 := (transitionLookup n.val).val
theorem transition_absorbs (n : Fin {len(pairs)}) : Absorbs (transition n).1 (transition n).2 :=
  (transitionLookup n.val).property
end FrameGeometry
#print axioms FrameGeometry.frame_valid
#print axioms FrameGeometry.scaled_idempotent_entries
#print axioms FrameGeometry.scaled_symmetric_entries
#print axioms FrameGeometry.scaled_stack_entries
#print axioms FrameGeometry.stack_inverse_entries
#print axioms FrameGeometry.inverse_stack_entries
#print axioms FrameGeometry.transition_absorbs
''')
    return '\n'.join(lines)


FRAME_BATCH_SIZE = 64
TRANSITION_BATCH_SIZE = 128
GENERATED_PATTERNS = (
    'FrameData.lean', 'FrameDatumCore.lean', 'FrameLookup.lean',
    'FrameCertificateBatch*.lean', 'FrameTransitionBatch*.lean',
)


def split_rendered(monolith):
    """Move declarations into independent modules, preserving types and data.

    Each frame batch imports only the shared definitions. Each transition
    batch imports only the common frame lookup, never another transition
    batch. The final facade preserves the existing FrameData import path.
    Certificate proofs use Lean's kernel reduction directly, avoiding the
    duplicate elaborator reduction performed by plain `decide`. This changes
    only proof bodies; it introduces no native-code trust or external setting.
    """
    frame_start = monolith.index('def certified0 : CertifiedFrame :=')
    lookup_start = monolith.index('def lookup (n : Nat) : CertifiedFrame :=')
    transition_start = monolith.index('def transition0 : ')
    transition_lookup_start = monolith.index('def transitionLookup (n : Nat) : ')
    end = monolith.index('end FrameGeometry\n')

    def declarations(text, prefix):
        pieces = re.findall(r'^def ' + prefix + r'\d+\b[\s\S]*?(?=^def |\Z)', text, re.M)
        assert ''.join(pieces) == text
        assert [re.match(r'def (\w+)', item).group(1) for item in pieces] == [
            prefix + str(i) for i in range(len(pieces))]
        return pieces

    frames = declarations(monolith[frame_start:lookup_start], 'certified')
    transitions = declarations(monolith[transition_start:transition_lookup_start], 'transition')
    assert len(frames) == 944

    def module(imports, body):
        return ('\n'.join('import ' + name for name in imports) + '\n\n'
                '/-! Literal PR442 certificate partition. Apache-2.0.\n'
                'Prepared with substantial OpenAI Codex assistance.\n'
                'Generated by generate_frame_data.py; types and literal data are unchanged. -/\n'
                'namespace FrameGeometry\n'
                'set_option maxRecDepth 100000\n'
                'set_option maxHeartbeats 0\n\n'
                + body + '\nend FrameGeometry\n')

    files = {'FrameDatumCore.lean': monolith[:frame_start] + 'end FrameGeometry\n'}

    def batches(items, size, prefix, dependency):
        names = []
        for i, offset in enumerate(range(0, len(items), size)):
            name = f'{prefix}{i:02d}'
            body = ''.join(items[offset:offset + size]).replace('by decide⟩', 'by decide +kernel⟩')
            files[name + '.lean'] = module([dependency], body)
            names.append(name)
        return names

    frame_modules = batches(frames, FRAME_BATCH_SIZE, 'FrameCertificateBatch', 'FrameDatumCore')
    files['FrameLookup.lean'] = module(frame_modules, monolith[lookup_start:transition_start])
    transition_modules = batches(transitions, TRANSITION_BATCH_SIZE,
                                 'FrameTransitionBatch', 'FrameLookup')
    files['FrameData.lean'] = (module(transition_modules, monolith[transition_lookup_start:end])
                             + monolith[end + len('end FrameGeometry\n'):])
    return files


def render_files(frames_path, template_path):
    """Return the complete filename-to-source mapping for this certificate."""
    return split_rendered(render_monolith(frames_path, template_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('frames', type=Path)
    parser.add_argument('template', type=Path)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('FrameData.lean'))
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    assert args.output.name == 'FrameData.lean', '--output must name the FrameData.lean facade'
    expected = render_files(args.frames, args.template)
    existing = {path.name for pattern in GENERATED_PATTERNS
                for path in args.output.parent.glob(pattern)}
    if args.check:
        assert existing == set(expected), 'Frame certificate module inventory differs'
        for name, text in expected.items():
            assert (args.output.parent / name).read_text() == text, name + ' differs from the supplied source'
    else:
        assert not existing - set(expected), 'Remove obsolete frame certificate modules before regeneration'
        args.output.parent.mkdir(parents=True, exist_ok=True)
        for name, text in expected.items():
            (args.output.parent / name).write_text(text)


if __name__ == '__main__':
    main()

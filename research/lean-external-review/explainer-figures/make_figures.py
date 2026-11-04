#!/usr/bin/env python3
"""Render the explainer's fixed toy trace; optionally recheck it with Lean.

No proof-package files or receipts are written. --check-lean builds the
existing FramedReplay target through ordinary Lake, writes a scratch .lean
file outside the checkout, and compares its #eval output with TRACE.
The scratch also checks FramedReplay.ValidTrace for this one example.
PNGs have fixed dimensions, colors, bundled font, and metadata; no timestamps.
Reproduce with the versions in requirements.txt. --check compares bytes
without overwriting the committed figures.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1] / "lean-multi-host-source"

# Each row: physical bits at (false,true), decoded bits at (false,true),
# gauge tag (0 = identity I, 1 = address reversal J).
# Source: LEAN_EXAMPLE below, FramedReplay.physicalStep/decodeRow, Tree.get.
TRACE = [
    [[1, 0, 1, 0, 0], [1, 1, 1, 1, 1], [0, 1, 0, 1, 0], [0, 0, 0, 0, 0]],
    [[1, 0, 1, 0, 0], [1, 1, 1, 1, 1], [1, 0, 0, 1, 1], [0, 0, 0, 0, 0]],
    [[1, 0, 1, 0, 0], [0, 1, 1, 0, 1], [1, 0, 0, 1, 1], [0, 0, 0, 0, 0]],
    [[1, 0, 1, 0, 0], [0, 1, 1, 0, 1], [1, 0, 0, 1, 1], [0, 1, 1, 0, 1]],
    [[1, 0, 1, 0, 0], [0, 1, 1, 0, 1], [1, 1, 1, 1, 1], [0, 1, 1, 0, 1]],
    [[1, 0, 1, 0, 0], [1, 0, 0, 1, 1], [1, 1, 1, 1, 1], [0, 1, 1, 0, 1]],
    [[1, 0, 1, 0, 0], [1, 0, 0, 1, 1], [1, 0, 0, 1, 1], [0, 1, 1, 0, 1]],
    [[1, 0, 1, 0, 0], [1, 0, 0, 1, 1], [1, 0, 0, 1, 1], [0, 0, 0, 0, 0]],
]
ROW_NAMES = ["S  source", "T  target", "H  dirty helper", "P  private temporary"]
STEPS = ["Initial state", "1  MOVE H to J", "2  ADD T, H", "3  COPY S to P in J",
         "4  ADD H, P", "5  ADD T, H", "6  ADD H, P", "7  ERASE P using S"]

LEAN_EXAMPLE = r'''import FramedReplay
open FramedReplay TreeReplay

-- Signature checks ground the explainer's glosses of the admitted axioms.
universe u
example {p q : Prop} : (p ↔ q) → p = q := propext
noncomputable example {α : Sort u} : Nonempty α → α := Classical.choice
example {α : Sort u} {r : α → α → Prop} {a b : α} :
    r a b → Quot.mk r a = Quot.mk r b := Quot.sound

def I : Gauge Bool := ⟨id, id, fun _ => rfl, fun _ => rfl⟩
def J : Gauge Bool := ⟨Bool.not, Bool.not,
  by intro b; cases b <;> rfl, by intro b; cases b <;> rfl⟩
def bits (a b : Bool) : Bool → Bool := fun x => if x then b else a
-- Row indices: 0 source, 1 target, 2 dirty helper, 3 clean private temporary.
def initial : Store Bool := Tree.tabulate 2 fun i =>
  match i with
  | 0 => (I, bits true false)
  | 1 => (J, bits true true)
  | 2 => (I, bits false true)
  | _ => (I, bits false false)
def events : List (Event Bool) := [
  ⟨⟨0, 2, 0, false⟩, J⟩,
  ⟨⟨1, 1, 2, true⟩, J⟩,
  ⟨⟨2, 0, 3, false⟩, J⟩,
  ⟨⟨1, 2, 3, true⟩, J⟩,
  ⟨⟨1, 1, 2, true⟩, J⟩,
  ⟨⟨1, 2, 3, true⟩, J⟩,
  ⟨⟨3, 0, 3, false⟩, I⟩]
-- The real chronological guard predicate, for this toy only.
example : ValidTrace events initial := by
  refine ⟨True.intro, rfl, ?_, rfl, rfl, rfl, ?_, True.intro⟩
  · funext b; cases b <;> rfl
  · funext b; cases b <;> rfl

def states : List (Event Bool) → Store Bool → List (Store Bool)
  | [], s => [s]
  | e :: es, s => s :: states es (physicalStep s e)
def bit (b : Bool) : Nat := if b then 1 else 0
def view (r : Row Bool) : List Nat :=
  [bit (r.2 false), bit (r.2 true),
   bit (decodeRow r false), bit (decodeRow r true), bit (r.1.forward false)]
#eval (states events initial).map fun s => (List.range 4).map fun i => view (s.get i)
'''


def check_lean(project: Path, lake: str) -> None:
    version = subprocess.check_output([lake, "env", "lean", "--version"], cwd=project, text=True)
    if not version.startswith("Lean (version 4.21.0,"):
        raise RuntimeError("The illustration must be checked on the project's Lean 4.21.0")
    subprocess.run([lake, "build", "FramedReplay"], cwd=project, check=True)
    with tempfile.TemporaryDirectory(prefix="pr442-explainer-") as temporary:
        source = Path(temporary) / "Example.lean"
        source.write_text(LEAN_EXAMPLE)
        result = subprocess.run([lake, "env", "lean", str(source)], cwd=project,
                                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError("Scratch Lean check failed:\n" + result.stdout)
    if json.loads(result.stdout) != TRACE:
        raise RuntimeError("The Lean-computed trace differs from the figure data")
    print("PASS: Lean 4.21.0 evaluated every toy state and checked its chronological guards.")


def figures() -> dict[str, bytes]:
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.font_manager import FontProperties
    from matplotlib.patches import Rectangle
    import PIL

    if matplotlib.__version__ != "3.10.8" or PIL.__version__ != "12.3.0":
        raise RuntimeError("Install the rendering versions in requirements.txt for byte-stable PNGs")
    plt.rcdefaults()
    plt.rcParams.update({"figure.facecolor": "white", "savefig.facecolor": "white",
                         "text.color": "#152b3b", "font.size": 12})
    font = FontProperties(fname=str(Path(matplotlib.get_data_path()) /
                                   "fonts/ttf/DejaVuSans.ttf"))
    colors = {0: "#edf2f5", 1: "#146a83"}

    def label(ax, x, y, text, size=12, **kw):
        ax.text(x, y, text, fontproperties=font, fontsize=size, **kw)

    def bits(ax, x, y, values, width=.40, height=.38):
        for j, value in enumerate(values):
            ax.add_patch(Rectangle((x + j * width, y), width, height,
                                   facecolor=colors[value], edgecolor="white", linewidth=1.5))
            label(ax, x + (j + .5) * width, y + height / 2, str(value), 12,
                  ha="center", va="center", color="white" if value else "#152b3b")

    def png(fig):
        stream = io.BytesIO()
        fig.savefig(stream, format="png", dpi=160, metadata={"Software": "PR442 explainer"})
        plt.close(fig)
        return stream.getvalue()

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.subplots_adjust(left=.025, right=.995, bottom=.025, top=.98)
    ax.set(xlim=(0, 10), ylim=(0, 5)); ax.axis("off")
    label(ax, .2, 4.58, "Same logical helper, different physical addresses", 18)
    for x, state, title in [(0.2, TRACE[0], "BEFORE"), (5.2, TRACE[-1], "AFTER")]:
        label(ax, x, 4.04, title, 14)
        label(ax, x + 2.05, 3.62, "Frame", 11)
        label(ax, x + 2.82, 3.62, "Physical", 11)
        label(ax, x + 3.9, 3.62, "Decoded", 11)
        for i, row in enumerate(state):
            y = 2.91 - i * .58
            label(ax, x, y + .19, ROW_NAMES[i], 11, va="center")
            label(ax, x + 2.25, y + .19, "J" if row[4] else "I", 12, ha="center", va="center")
            bits(ax, x + 2.82, y, row[:2])
            bits(ax, x + 3.9, y, row[2:4])
    label(ax, .2, .58, "I reads addresses in order.  J reads them in reverse.", 12)
    label(ax, .2, .22, "T becomes T XOR S; H retains its decoded bits; P returns blank.", 12)
    result = {"before-after.png": png(fig)}

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.subplots_adjust(left=.025, right=.995, bottom=.025, top=.98)
    ax.set(xlim=(0, 10), ylim=(0, 7)); ax.axis("off")
    label(ax, .2, 6.55, "Seven operations, with every intermediate state", 18)
    label(ax, .2, 6.15, "Physical bits shown; the letter records the row's frame.", 12)
    names = ["S / source", "T / target", "H / helper", "P / private"]
    positions = [3.35, 4.98, 6.61, 8.24]
    for x, name in zip(positions, names):
        label(ax, x, 5.65, name, 11)
    for i, (step, state) in enumerate(zip(STEPS, TRACE)):
        y = 5.02 - .57 * i
        label(ax, .2, y + .19, step, 11, va="center")
        for x, row in zip(positions, state):
            bits(ax, x, y, row[:2])
            label(ax, x + .92, y + .19, "J" if row[4] else "I", 11, va="center")
    label(ax, .2, .56, "Before ERASE: S is 10 in I, P is 01 in J; both decode to 10.", 12)
    label(ax, .2, .19, "Toy semantics illustration only; this is not a fragment of the R747 word.", 11)
    result["operation-trace.png"] = png(fig)
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true", help="compare PNG bytes without writing")
    p.add_argument("--check-lean", action="store_true", help="also rerun the optional scratch example")
    p.add_argument("--lean-project", type=Path, default=PROJECT)
    p.add_argument("--lake", default="lake", help="Lake executable; no compiler flags or environment overrides")
    args = p.parse_args()
    if args.check_lean:
        check_lean(args.lean_project.resolve(), args.lake)
    for name, data in figures().items():
        path = HERE / name
        if args.check:
            if path.read_bytes() != data:
                raise RuntimeError("Figure differs: " + name)
        else:
            path.write_bytes(data)
    print("PASS: deterministic figures " + ("match committed bytes." if args.check else "generated."))


if __name__ == "__main__":
    main()

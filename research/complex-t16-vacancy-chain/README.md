# Four whole-helper placements improve the selected T16 packing

The unchanged PR1094 supplier admits conditional
**κ = 0.001672664045494084**, up from **0.001672660197076918**
(**+0.000230077643548%**). Four of 69,120 helper placements change. The local
word, helper widths, 144-call order, physical stock, native supplier and bit
supplier stay fixed. Complete strict supplier replay passes.

This improves the selected PR1094 benchmark, but is not the best known packing
of that supplier. [PR1407](https://github.com/CrocSwap/integer-mult-bounds/pull/1407)
already reports **κ = 0.001672680818492982** for the same unchanged PR1094
supplier. This package provides a compact four-row alternative. PR1992 and
PR2044 report still larger conditional values for the different T74 supplier
and fine-prime transfer. No global packing optimum, practical speedup, or
unconditional multiplication theorem is claimed.

## Construction and exact saving

The moves below are packing assignments, not new chronological scalar gates.
All source and destination slices are suffixes; other placements stay fixed.
The exact before/after rows are in `MOVES.json`.

Each assignment reserves a disjoint slice of its owner's pending prefix for
the whole schedule. Prefix coverage is checked over the union of those slices;
offsets need not increase with call time. For example, calls at times4 and9 use
offsets40 and44. The unchanged 144-call chronology and strict owner windows,
not the order of the move list below, govern execution.

| Helper, call (stage, replica), time | Old owner bin and offset | New owner bin and offset |
|---|---|---|
| 228, (6,3), 96 | (1,15,86), 25 | (13,15,14), 25 |
| 226, (1,15), 71 | (11,8,103), 40 | (1,15,86), 25 |
| 90, (1,0), 4 | (0,0,102), 9 | (11,8,103), 40 |
| 154, (1,9), 9 | (2,0,22), 9 | (11,8,103), 44 |

First, helper228 fills a seven-slot vacancy. Helper226 fills its vacated slice,
leaving an eight-slot suffix. Two width-four helpers from distinct calls fill
that suffix. Their old bins each become seven-slot residuals.

The idle histogram changes from `{1:2276,3:377,7:7,48:4866}` to
`{1:2275,3:375,7:8,48:4866}`. Thus the whole-profile change is
`Δ = H7 - 2 H3 - H1`, where `Hr = r^p` and `0 < p < 1`.
Strict subadditivity gives `7^p = (3+3+1)^p < 2*3^p+1`.
Rank mass remains 1,041,408 and the deficit remains 5,120. This is an actual
paid-profile improvement, not a scalar-only saving or a parameter-only backoff.

The final profile is
`{1:349603,2:60192,3:62583,4:20448,5:11808,7:8,8:1152,48:4866}`.
The native complex lower endpoint is
`1675466538131846067921/10^24`; the bit lower endpoint is unchanged.

## Reproduce

Python 3.12+, standard library only, from a complete repository checkout:

```sh
python3 -I -B research/complex-t16-vacancy-chain/verify.py --work /absolute/fresh/output
python3 scripts/research_package.py --package research/complex-t16-vacancy-chain --check-only
```

`--main /path/to/pinned-dependency-checkout` can supply the explicitly hashed
inputs. `INPUTS.json` declares the full retained dependency subtrees, original
PR1094 data and archive, and the selected replay archive. The package hook lists
the same files for CI invalidation. `build.py` reconstructs all four changes and
the derived data bindings; it compares compressed owner data by its complete
decoded payload and retains immutable container hashes for source binding.

The verifier preserves all 179 archived predecessor files, overlays only
`OWNERS.json.gz`, `PLAN.json`, and `SPEC.json`, and executes the unchanged
`verify_t16.py`. It extracts the actual selected R480 native provider from the
pinned selected replay archive. The older archive's historical R492
`evidence/local` is not the selected provider.

## Validation and scope

All eleven strict stages pass: parent restoration, T8 binding, literal T16
windows, selected binding, controller emission, audit, finite invoice,
assembly, admission controls, bit controls, and independent owner replay.
This includes 69 admission controls, 12 bit controls, 15 controller mutations,
six independent owner controls, two exact moment engines, and 47 strict outer
inequalities for each native/conservative assembly. The unchanged native
local receipts are source-bound reuse, not a fresh cold rebuild of all ancestry.

The independent checker also reconstructs all 73-axis owner charts, actual
bridge-aware windows, whole-helper slices and active-data exclusion. Its
historical R504 stock upper bound is conservative; the strict controller and
invoice retain the actual R480 physical stock of 14,826. Prefix397 remains below
the charged512 reserve, and the physical row coefficient16469 stays below20161.

The all-size compiler, common-label/mutable-source realization, whole-call
hosting, precision/tape, exact recovery, analytic transfer and PR589 bit H1-H5
assumptions remain. Finite replay does not establish them. `VALIDATION.json`
records local evidence; hosted CI and maintainer acceptance are separate.

## Attribution and overlap

Prepared for George Lydakis with substantial OpenAI Codex assistance, including
coordination with Ody. No independent human review is claimed. New material is
Apache-2.0. Retained predecessor archives, notices and attribution are unchanged.

Builds directly on Rohan Arun's PR1094 and the PR1087 packing work, Jeremy
Kothe's owner-packing lineage, Hao Yan / FanPUYen's PR858 T16 controller,
PR1018 including PR987, PR1005, NewBArch's PR869, and PR799/741/685/645/589.
The exact arithmetic engines retain their original authors and source notices.

[philippeVV's independent review](https://github.com/CrocSwap/integer-mult-bounds/pull/2077#issuecomment-6176996271)
reports a full CPython3.12 strict replay, registered replay and metadata-check
pass, plus a separate seed67 owner audit with eleven rejection controls. The
review discloses substantial Claude assistance. It identifies the stronger
same-supplier PR1407 result and overlapping owner rows2010 and34306 and bins;
the two patches cannot be composed as written. Any combined candidate needs a
new owner assignment and complete replay.

The changed hypothesis is vacancy propagation through an occupied full bin,
followed by filling the new eight-slot suffix. Direct relocation and a single
blocking-role swap miss the first path. This is a bounded witness, not a claim
that broader packing searches or other suppliers are exhausted. See
`OVERLAP.json` for the dated search coverage and known higher pending claims.

## Open next questions

Can a vacancy path improve the stronger PR1407 owner map without undoing its
existing gains? A first step is to freeze that exact map and a bounded path
grammar, check the overlapping rows and bins, then apply exact family/window
constraints and the complete invoice. This witness does not establish that
such a path exists or that either packing is optimal. Larger gains likely
require a changed local supplier or interface.

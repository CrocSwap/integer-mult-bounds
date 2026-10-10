# complex-p10

**The complex supplier at cube size p = 10 (no new κ).** PR #304 compiled the source-assisted complex word of PR
#184/#194 at p = 11 (h = 22, 1,320 ports) on re-annealed query modules, and PR #315 ships a centre-sharing version of
it. This package compiles the same word with the same frozen recipe one cube size down, at **p = 10 (h = 20, 960
ports)**, on query modules cut from p = 11 module files and re-annealed at p = 10. Each word is one explicit gcert/1
program that Jacob Sussman's reference checker `gx.check1` (exact scalar identity) and his Python mirror of the two
Lean checks (`gxcore.py`), both vendored unchanged, accept. Priced in his bridged five-stage layout at h = 20
(m = 5h = 100, W = 4v + R; see "The layout at h = 20") with exact rational bounds:

**centre-sharing modules (PR #233 pairs): a = 7795/10⁷ (7796/10⁷ rejected), against 7727/10⁷ for PR #315's p = 11
centre-sharing program: +0.88%.**
**PR #304's recipe on annealed p = 10 modules (PR #233 pairs): a = 7737/10⁷ (7738/10⁷ rejected), against 7635/10⁷
for PR #304 at p = 11: +1.34%.**

Both claims also hold with the five-stage packages' 10⁻¹⁶ bad-class fallback envelope included; the fallback-inclusive
coarse savings that a five-stage package would consume are b = 779597612622781/10¹⁸ (centre-sharing) and
773718577669358/10¹⁸ (PR #304's recipe), each certified by two independent rational moment engines with the next
10⁻¹⁸ point rejected.

**No new κ by itself.** On the open frontier (community stacks on PR #315's p = 10 bit word, best PR #320 at
κ 7.69199e-4; cited, not checked here) the bit side binds: it lies below PR #315's complex supplier (7727/10⁷) and
below both prices here. If a κ package adopts this supplier, the complex cap rises from 7.727e-4 to 7.796e-4
(+0.89%), so that the bit side could pass 7.727e-4 without the complex supplier capping κ there. A κ package must first
generalize or re-pin the five places where PR #315's package pins its p = 11 complex program (listed in PROOF.md §5);
this package does not do that.

| program (gcert/1, five-stage layout m = 100, W = 4v + R) | modules | pairs | R | registers | blocks | N | gx.check1 and gxcore | saving a |
|---|---|---|---|---|---|---|---|---|
| control, parity recipe | PR #168 v4 cut to p = 10 | PR #193 recipe | 7,121 | 9,041 | 49,631 | 179,260 | accepted | 7322/10⁷ |
| control, mw recipe | PR #168 v4 cut to p = 10 | PR #233 recipe | 7,125 | 9,045 | 49,282 | 179,340 | accepted | 7375/10⁷ |
| PR #304 recipe, parity | annealed at p = 10 | PR #193 recipe | 6,515 | 8,435 | 48,602 | 167,140 | accepted | 7689/10⁷ |
| **PR #304 recipe, mw** | **annealed at p = 10** | PR #233 recipe | **6,515** | 8,435 | 48,299 | 167,140 | accepted | **7737/10⁷** |
| centre-sharing, parity | annealed, centre pair module | PR #193 recipe | 6,455 | 8,375 | 48,278 | 165,940 | accepted | 7747/10⁷ |
| **centre-sharing, mw** | **annealed, centre pair module** | PR #233 recipe | **6,455** | 8,375 | 47,979 | 165,940 | accepted | **7795/10⁷** |

Against the same-recipe control the annealed modules gain +4.91% (mw) and +5.01% (parity), the centre-sharing set
+5.69% and +5.80% on the certified grid points. Against the p = 11 programs: PR #304's recipe at p = 10 beats PR
#304 (7635 and 7586/10⁷) by +1.34% and +1.36%; the centre-sharing word beats PR #315's (7727/10⁷) by +0.88%, and
even PR #304's recipe at p = 10 passes it (+0.13%). [PROOF.md](PROOF.md) states the claim and the chain of checks.

## The layout at h = 20

The price uses Sussman's bridged five-stage word B₂ with the h-dependent idle climbs written out:
H₅ = 5·H_inv + 2v·(e_{2h−2} + e_{h−1} + e_{2h+2} + e₄), m = 5h, W = 4v + R. At h = 22 these are PR #304's literals
(e₄₂, e₂₁, e₄₆, e₄); here they are **e₃₈, e₁₉, e₄₂, e₄**, m = 100, and the deficit is 4v − 5·cst = 3,840 − 5·360 =
2,040 for every program (20 scratch copies of 18 moves, cst = h(h − 2)). This is the generic formula applied at a new
h: PR #304's price, PR #315's complex supplier and Sussman's Lean build of #193 are all at h = 22. In his
repository the layout is stated for every h (`bankPrice h`
in `Work/BridgeGeom/B2.lean`, `bridge2_gcert` and `GX.wht_of_halves` parametric in the label dimension; `gxunit.unit`
builds the unit from `BANK['B2']` as functions of h). Both mw programs here were kernel-checked at h = 20 with his
unchanged generator (below). `verify.py` re-derives the h = 22 literals from the same formula on its PR #194 anchor.

## Verify

    python -m pip install numpy==2.3.5 scipy==1.17.0        # for the pinned regeneration and the checkers
    python3 -B research/complex-p10/verify.py                # about 12 minutes; -O is refused

The script checks every pin of `SOURCE.json`, rebuilds the 308 pinned files of PR #202 from the vendored PR #233
package and regenerates the producer word and the source-aligned word at p = 11 (PR #194's pipeline). Four anchors
follow: `aligned_word_p.py` at its default p = 11 reproduces the seven output files of `source_aligned_local_v4.py`
byte for byte; PR #194's word through this package's chain is PR #256's certificate (same sha256) with Sussman's #193
histogram; the control modules are re-derived from PR #168 v4's module files byte for byte (`module_cut.py`); and PR
#315's 10-line `Graph.finish` patch, applied to the rebuilt `graph.py`, builds the same graph as `centre46.py`. Then,
for each module set and pair recipe, it installs the modules and the frozen layer, builds the word with
`aligned_word_p.py --p 10`, re-checks the pairs with `paircheck.py` (five mutation controls), recomputes PR #168's
`physical()` profile and admits the layer with PR #200's complete complex checker, runs PR #184's flow and exact lift
and PR #194's contract, emits the gcert/1 program with PR #256's `gcert_emit.py` (unchanged), runs `gx.check1` and
the `gxcore` mirror on the emitted program, checks the ledger, writes the scatter as the star rule with
`normalize_scatter.py`, runs `gx.check1` and `gxcore` again, requires both to reject a flipped scalar sign (E5),
prices the five-stage word at h = 20 at the claim of `SOURCE.json` with and without the fallback envelope (next 10⁻⁷
point rejected by an exact lower bound) and certifies the fallback-inclusive coarse saving on the 10⁻¹⁸ grid with
both engines, and compares the six committed programs byte for byte (uncompressed JSON) with `certificates/` and the
run with `certificate/expected.json`. `--temp-root` chooses scratch storage.

All six programs come out of the emitter in star form (every retained-total unit is +1), so at p = 10
`normalize_scatter.py` changes nothing; the step stays as a check. The committed files are the emitted programs in
canonical JSON (sorted keys).

To check a certificate with Sussman's other tools (not run for this package):

    python3 -B tools/gx/refcheck.py <this package>/certificates/gcert1-p10-centre-mw-flow.json.gz   # in his repository
    python3 -B tools/gx/gxdry.py    <this package>/certificates/gcert1-p10-centre-mw-flow.json.gz   # mirror and price

and to build it in Lean with his unchanged generator (about 10 minutes of kernel time per program at h = 20):

    GX_OUT=<empty dir> python3 -B tools/gx/regen_check.py <abs path>/gcert1-p10-centre-mw-flow.json.gz CC95 B2Gcc95 --keep <empty dir>
    cp -R <empty dir>/Work/GCert/Data/. Work/GCert/Data/          # then lake build each module in the printed build order
    lake env lean --run tools/Compare.lean Work.GCert.Data.ChallengeB2Gcc95x Work.GCert.Data.SolutionB2Gcc95x OAI.PowerSaving.WHT.wht_main_block_B2Gcc95x

A dry run of the Python half of that generator (`regen_check.py --keep` into a scratch directory; not part of
`verify.py`) accepts both mw programs at h = 20 (its `gxcore` mirror of both Lean checks; 6 data segments, 4 replay
segments, 2 scalar batches) and states the whole-block rates 1 − 7795973/10¹⁰ (centre-sharing) and
1 − 7737183/10¹⁰ (PR #304's recipe) for the theorems it emits.

**Lean (run locally; not pinned in this package).** Both mw programs were compiled with Sussman's unchanged
generator (`tools/gx/regen_check.py`, wht-power-saving-lean at f010392, Lean v4.34.1, Mathlib d13f23b) and
kernel-checked, one module at a time (31 of 31 built modules each, 0 errors):

| program | theorem | exponent | gcert sha256 (uncompressed) |
| --- | --- | --- | --- |
| centre-sharing mw | `OAI.PowerSaving.WHT.wht_main_block_B2Gcc95x` | 1 − 7795973/10¹⁰ | `370fae73…23ff` |
| PR #304's recipe mw | `OAI.PowerSaving.WHT.wht_main_block_B2Gcp37x` | 1 − 7737183/10¹⁰ | `433848305e…16e5` |

The hashes equal the `certificate_sha256` values pinned in `certificate/expected.json`. `tools/Compare.lean`
passed for both, against challenge files that differ from his ChallengeB2Gp193x only in the module and theorem
names and the exponent. `#print axioms` gives `propext`, `Classical.choice` and `Quot.sound`. Nothing h-specific
broke at h = 20 (the generator emits 6 data and 4 replay segments). The official comparator and a clean build
from nothing were not run. This covers the Walsh–Hadamard power-saving theorem at these exponents, not any
integer-multiplication κ assembly.

## Modules

| set | triple module (p = 10) | pair module (n = 9) | all-but-one module (n = 8) |
|---|---|---|---|
| `pr168-v4-cut` (control) | PR #168 v4's, point 6 dropped (1,220 additions) | PR #168 v4's, point 4 dropped (256) | PR #168 v4's, point 1 dropped (24) |
| `anneal` (PR #304 recipe) | `tmod_t2_p10.json` (1,322) | `pmod_p3_p10.json` (269) | `qmod_sa1_p10.json` (24) |
| `centre` | `tmod_t2_p10.json` | `pmod46_pc1_p10.json` (291, 37 roots) | `qmod_sa1_p10.json` |

Every module is a zero restriction of a p = 11 module file followed (except the control's) by simulated annealing at
p = 10 against a closed-form evaluator of the aligned word's compile ledger: the triple and all-but-one modules from
PR #304's `tmod_cmod_v2.json` and `qmod_cmod.json`; the pair module of the PR #304-recipe set from PR #168 v4's pair
module (the control's cut); the centre-sharing pair module from PR #304's `pmod_cmod_dropin.json`, annealed, given a
37th root (the sum of all its inputs) and annealed again with it. [discovery/README.md](discovery/README.md) has the
cut points, chains and energies. The annealing code is research code and is not included; the module files are inputs,
checked by the rebuilt tree's contract loaders (`load_pmod46` for the 37-root module) and priced by the chain.

**The centre-sharing graph.** In PR #144's `Graph.finish` every star centre S(2i + e) is a separate sum of the
inputs of the pair module (i, e). The centre-sharing pair module returns that sum as its 37th root, and the graph uses
it as the centre: PR #315's 10-line patch (`references/centre46_graph.diff`, icekylinx's `graph.py`) does this inside
`Graph.finish`; `centre46.py` (`finish_centre46`, `load_pmod46`) does it without editing the tree. `verify.py` applies
the patch to the rebuilt `graph.py` and requires the two graphs to agree in every field except the status string,
and the patch to leave the graph of an ordinary 36-root pair module unchanged.

## Two latent bugs, fixed for p ≠ 11

- **PR #233's `pairs_mw.py` hard-codes the gauge rank f = 18**, which is h − 4 only at h = 22. At h = 18 (p = 9)
  every donor weight is then 0 and the maximum-weight pairing returns no pairs. `discovery/pairs_mw_p.py` reads
  f = h − 4 (one line; identical at h = 22). The weights only choose pairs, which `verify.py` checks independently; on
  this package's layers the literal happens to give the same pairs (discovery/README.md).
- **`source_aligned_local_v4.py` keeps the births of dropped gauges in its record.** The script keeps only the
  selected gauges of rank h − 4 that are paired, but its record (`selected_roles`, `selected_rank_histogram`,
  `remaining_internal_histogram`) still counts every gauge `select()` chose. On every p = 11 module set and on the
  annealed p = 10 modules `select()` chooses only rank-(h − 4) gauges, so the record is exact; on the control's cut
  modules it also chooses 8 gauges of ranks 14 and 13, and PR #200's complex checker (which recounts the record)
  rejects the word. `aligned_word_p.py` reverses the births of dropped gauges in those three fields (and changes
  nothing when none is dropped, which anchor (a) confirms byte for byte at p = 11). Only the verifiers read these fields; the
  programs are unaffected.

## Re-pinning after a module changes

    python3 -B research/complex-p10/discovery/make_layer_p.py --set anneal --tmod <new tmod.json>   # ~90 s
    python3 -B research/complex-p10/verify.py --write
    python3 -B research/complex-p10/verify.py

`--write` re-pins `modules/` and `layers/` (no other pin), sets every claim to the largest 10⁻⁷ grid point its exact
bounds certify, and rewrites `certificates/` and `certificate/expected.json`; the numbers in this file and in
PROOF.md are then updated by hand.

## Files

`verify.py`; `aligned_word_p.py` (PR #304's `aligned_word.py` with the cube size, the centre-sharing option and the
record correction); `centre46.py`; `module_cut.py` (zero restriction; re-derives the control modules); `paircheck.py`
and `normalize_scatter.py` (PR #304's, unchanged); `modules/` (seven module files); `layers/{pr168-v4-cut,anneal,
centre}/` (frozen carrier arcs, operation frames, reuse pairs of both recipes, kernel pairs);
`certificates/gcert1-p10-{pr168-v4-cut,anneal,centre}-{parity,mw}-flow.json.gz` (the six programs, star form, about
0.32 MB each); `certificate/expected.json`; `gcert_emit.py`, `gx/gx.py`, `scripts/moment.py` and `references/`
(`pr233-layer/`, `sussman/`) vendored byte for byte from PR #256 via PR #304; `gx/gxcore.py` (Sussman's, unchanged);
`scripts/source527/` (eumemic's two moment engines, unchanged); `references/centre46_graph.diff` (PR #315's);
`discovery/` (how the layers and modules were found; not run by `verify.py`); `SOURCE.json`, `PROOF.md`, `NOTICE`.
`.github/workflows/complex-p10.yml` runs the verifier on Python 3.12 and 3.14.

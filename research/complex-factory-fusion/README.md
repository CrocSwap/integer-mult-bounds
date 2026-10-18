# Unit-add lowering of the exact complex factory

This construction implements the complete PR924 eight-register factory with
**37 real-component primitives, plus one charged work clear**. It uses 26 unit
additions, nine binary shifts and two sign changes. It has no new helper.
Temporary source scales are restored at the exact factory boundary.

A source-scale certificate gives a nine-shift minimum in the stated fixed
unit-add class. This is a compiler refinement of a 32-macro block. It is not
a 37-macro replacement under a per-macro adapter invoice.

The verifier installs the circuit in all fourteen raw PR622 factory windows
and their inverse cleanups. It checks both complete orientations, all 725
input columns, the native frames and all repeated calls in the existing
conservative dedicated-bank host.

| Complete raw program | PR696 / PR999 | Persistent cache | Strong comparison | New circuit | Extra saving |
|---|---:|---:|---:|---:|---:|
| Forward | 123,320 | 121,808 | 121,392 | 121,056 | 336 |
| Inverse transpose | 123,336 | 121,936 | 121,408 | 121,072 | 336 |
| 40 forward + 32 inverse-transpose calls | 8,879,552 | 8,774,272 | 8,740,736 | 8,716,544 | **24,192** |

Counts include both real components. They are instruction counts, not measured
runtime gains. The strong comparison combines persistent coefficient work,
small-integer accumulation and source scales restored at each macro boundary.
It costs **44 per component in all four factory orientations**, versus 38 for
the new circuit. Both complete programs also use the small-integer routes
outside the factories. Their 304-operation saving per call is credited to
the elementary routes used in PR1036, and is excluded from the extra saving.

The historical cache column uses PR999 outside each factory. It reproduces
PR1032's local costs of 46/46/48/48. PR999 itself ties PR696 on these complete
raw words; its gains on other CK/JP8 words are not claimed here. The package
also checks all 39,424 one-scale magnitude placements per orientation under
a source-version cache policy with the added direct routes. The minimum is
44 in this finite class. No global circuit minimum is claimed.

## Reproduce

Use Python 3.11 or later with NumPy installed. Run from the repository root:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python3 -I -B research/complex-factory-fusion/verify.py
```

The command generates the raw word with the pinned constructor, runs the
unchanged native and emitted-word checks, checks the phase recipes, then
checks all ten complete primitive programs and five complete invoices.
It compares the result with `EXPECTED.json`. Expected final line:

```text
PASS_EXACT_COMPLEX_FACTORY_FUSION primitives=44->38 columns=725 calls=72 extra_vs_strong=24192 no_new_kappa
```

The default command uses a temporary directory. `--out NEW_DIRECTORY` retains
all complete primitive streams, factory bindings, native/phase artifacts and
host schedules. `--write NEW_FILE` writes a new development receipt. Existing
output paths are refused. No solver, network access or source regeneration
outside the output directory is required.

The proof and limits are in [PROOF.md](PROOF.md). Source pins are in
[SOURCES.json](SOURCES.json), the integer witness in [CIRCUIT.json](CIRCUIT.json),
and executed checks in [VALIDATION.md](VALIDATION.md).

## Mechanism and physical boundary

Normalize the original scales to the outputs. At each addition, choose the
scale of its target and source so that its coefficient is `+1` or `-1`.
Keep these scales between additions and pay each actual change. The circuit
never copies a source into coefficient work. It clears that work at exit,
including an arbitrary incoming work column.

The emitted factory has some climbs between scalar operations. Each such
climb acts on a register that has not yet been used in that factory. The
verifier checks this condition before moving the climb to the block entry.
All eight registers then have one common frame. The new circuit runs in this
frame. It has no internal frame change or external consumer. At exit its
complete eight-register map equals PR924, including the complementary basis.
Every later consumer therefore receives the same value.

This is the changed assumption relative to the scale-placement floor in
`complex-factory-scale-frontier27`: that result fixes a clear after every ADD
and prices each extra SCALE as another logical macro. This construction
instead lowers the entire admitted block. Its extra unary primitive scales
need no coordinate alignment. The original 32 logical interface slots and
all their adapter reserves remain paid. [PROOF.md](PROOF.md) gives the
common-frame and adapter argument; it does not price a Fourier conversion
as a monomial adapter.

## Complete charge and limits

The fixed host has 72 literal calls, 4,428 width-nine helper banks, 11,596 live
families and 12,098 physical families. It pays all 35,424 helper roles, all
72 bridge sweeps, all idle children, and one rank-one complement per bank.
No owner or replica arrangement is optimized.

The paid rank mass is 843,948. Its deficit is `73*11596 - 843948 = 2560`.
The local adapter reserve remains 319,104. The candidate's complete bound
per cover vertex is 635,470,496,860,108, which is 24,192 below the strong
comparison. All ten retained finite guards pass. The global prefix allowance
is 512 bits; the recomputed requirement is 206 bits.

Exact complete-program row-l1 peaks are 124 forward and 64 backward. Their
positive bounds remain 39,090 and 1,301,331. The fractional depth remains two.
The phase check verifies 1,879 new edge recipes and reuses 1,231 pinned edge
certificates and 224 endpoint adapters. It includes exact global phase.

This result applies to the reconstructed **raw 492-helper PR622 supplier**.
It does not claim transport to the current T37 supplier, PR1004/1005's changed
mutable-leaver inventories, or a new conditional exponent. It does not alter
`certificates/selected-result.json` or `upstream/`.

All-size compilation, the common-label mutable-source realization, physical
hosting, precision/tape recovery and analytic transfer remain inherited
conditions. This is a finite construction with written proofs and exact
checks. It is not a Lean proof or a full integer-multiplication theorem.

## Prior work and attribution

Prepared for **Ali Romman (@aliromman)** with substantial **OpenAI Codex**
assistance in the circuit, proof, code, verification and text. Apache-2.0;
see the repository [LICENSE](../../LICENSE). No independent human review is
claimed. All predecessor files and notices remain unchanged.

- **Alluri / alluri-ritual, PR681**: the exact eight-register boundary,
  fourteen-window extraction and complete raw native replay.
- **CubeJerry, PR922 and PR924**: the 32-macro contraction and scale placement
  used as the input circuit.
- **Ross Richardson, scale-frontier27**: the fixed per-ADD-lowering floor,
  which states the restriction changed here.
- **Sagar Thakrar / thakrarsagar, PR696**: the copy-Horner/unit lowerer.
- **woklerx, PR1032**: the persistent-work factory comparison and its exact
  fixed-gauge floors. The historical cache figures are credited to this work.
- **Hanson Sun / bbMisk, PR1036**: the two-register coefficient frontier and
  its complete application of the elementary small-integer routes.
- **Seb / ZK-Snarky, PR999**: the bounded target-accumulation lowerer. Its exact
  source and notice are retained in `sources/pr999-lower.py` for comparison.
- **Jeremy Kothe / jeremykothe2, PR622**, and **Chafik Boukhalfa / chafreaky,
  PR626**: the constructor, retained native checks and host lineage.
- **icekylinx, PR425/433/531**: the common-frame scalar interface, phase
  compiler, original banked host and finite invoice.
- **DreamingOfClouds**, **Dugongue** and the earlier contributors retain the
  credits in the [predecessor notice](../complex-k492-owner-repair/NOTICE.md).

Related PR839/755/793/811/830 remove or reuse work in other words. The strong
comparison includes block-wide clear removal, exact scaled-work reuse and
PR1036's direct routes. PR1032 retains one magnitude scale per nonunit wire;
this circuit permits more scales and retains their effects across macros.
PR1033 checks short macro sections under a fixed per-ADD lowering. It does
not cover this complete joint primitive lowering.
PR975/1011 concern X4 target panels. PR1004/1005 change all-K delivery cells,
helper stock and frames. Those are different construction boundaries; their
claimed global exponents are not used as evidence for this local result.
PR1027 is a bit-supplier R480 quad12 result on six wires. Its arithmetic and
factory boundary are different. [OVERLAP.json](OVERLAP.json) records the heads.

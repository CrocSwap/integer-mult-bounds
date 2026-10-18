# Selected monomial: coordinate and word refinement

This package takes [PR2341's second handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2253#discussioncomment-18941667):
connect one actual PR2250 directed monomial adapter to the full-array tensor
semantics. The selected recipe is residual `0:1000.right`, with affine
offset 245 and constant phase 2.

The contribution is a **conditional formal refinement of the source-faithful
staged model**, plus separately authenticated execution tests of the unchanged
Python implementation. The physical Compact/digit-permutation endpoint
contract remains explicit. Python execution and the complete tape algorithm
are not formally verified. No selected frontier or exponent changes.

## Exact proposition and hypotheses

Write an address as `(s,x)`, where s contains every spectator/dirty compact
field and x is an f-tuple of nine-bit columns. Let sigma(x)=Lx XOR245,
with binary matrix rows

```
[1,73,4,67,16,32,128,256,75].
```

The strict-upper phase polynomial is

```
q(x) = x0 + 3x1 + 2x2 + 3x3 + 2x4 + 2x5 + 2x7 + 2x8
       + 2x0*x6 + 2x1*x3    (mod 4).
```

Assume an address equivalence `decode : P ≃ S × (Fin f → Fin512)`.
For each elementary ADD/FLIP operation in the literal compiled word, assume
its **completed** physical address step has exactly the corresponding
columnwise bit action and restores all spectators. This is
`CompletedPrimitive`, not an assumption of the entire word's endpoint.
The finite recipe theorem checks that all 22 literal gates implement the
displayed affine map, on every one of its 512 inputs; reversal is its inverse.

For every f and every full coefficient array h, the staged forward action
scatters the coefficient at `(s,x)` to `(s,sigma(x))` and multiplies it by

```
zeta^(2*f + sum_j q(x_j)),
```

where zeta is a unit. For zeta^4=1 the exponent reduces modulo4, matching the
source convention; complex i is the intended instance. The source execution
domain is f>=1; the formal coordinate identity also permits the empty tensor.
The inverse undoes the affine address action before applying inverse phase at
the recovered input. Both composition orders are identities.

`physical_tensor_refinement` identifies this action with
`coordinates ∘ PiTensorProduct.map(unary) ∘ coordinates.symm`,
using PR2341's unchanged coordinate equivalence, for each unchanged spectator.
It quantifies over all coefficient arrays, including arrays correlated across
columns and spectators. No pure-tensor or clean-input assumption appears.

The phase word model is separate. For every bit width b>=1, its literal
LSB-first carry loop implements negation modulo2^b. Under exact signed
headroom it implements Gaussian-integer unit multiplication:
the most-negative component `-2^(b-1)` must be excluded **only when that
component is negated**. Thus phase0 has no exclusion, phase1 excludes that
imaginary component, phase2 excludes both, and phase3 excludes the real one.
The source supports b>=2. The symmetric sufficient guard
`|real|,|imag| < 2^(b-1)` is convenient but stronger than these exact guards.

The theorem names and source locations are in the Lean modules:

| Module | Principal claims |
|---|---|
| `SelectedRecipe.lean` | Literal word/matrix equality, reverse-word identities, strict-upper polynomial, wrong phase-location witnesses |
| `MonomialRefinement.lean` | Completed-primitive induction; full-array tensor equality; phase exponent; spectator preservation; physical forward/inverse identities |
| `PhaseWords.lean` | Carry conservation; all-width modular negation; guarded signed refinement; Gaussian coefficient action; most-negative boundary |

## Source and model binding

PR2250 is pinned at `d404b48a1e7b147556b309497d55089c837dddb2`.
Its unchanged `monomial.py`, `compact.py` and `streams.py` are the
implementation under test, with original proof and notice retained.
The actual recipe is extracted from the complete immutable
`slots/local/RESIDUAL-ADAPTERS.json` member used by that package,
SHA256 `383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c`.
Its archive/commit lineage is recorded in `SOURCES.json`.
This retains PR2250's selected-source provenance rather than claiming a new
whole-supplier cold replay.

PR2341 is pinned at `f448ce821ba32001bf1ec13f7088450d2edcd112`.
`TensorLift.lean` and `LemmaG/Stream.lean` are unchanged dependencies, with
their notices. Their general stream lifting theorem is credited, not reproved
as new work. PR2250 already supplies 3,474 monomial/single-column checks,
physical small fixtures, and a written full-array argument. The addition here
is kernel-checked concrete word/phase staging and the arithmetic refinement.

The finite replay authenticates all14 copied source files before importing
the three Python implementation modules. It compares the Lean literal
matrix, phase data and 22-gate word to the actual recipe and compiler output.
Lean proves its finite facts directly from those literals, not from a
Python-generated image table. The translation of Python control flow into
Lean is reviewed and tested; it is **not** itself a formally verified importer.

## Evidence and meaningful controls

Use both evidence layers. `FINITE.json` intentionally says
`kernel_checked=false`; it records implementation/model binding, not an
all-width proof. `KERNEL.json` records the explicit Lean run on the published
source hashes, toolchain, dependencies, axioms and false-theorem probes.

The local fresh build passed on Lean4.33.0-rc1 under Ubuntu/WSL. All31 named
theorem axiom reports passed the allowlist; all3 false theorems were rejected
for mathematical reasons. The finite package replay passed normally and under
optimized CPython3.12.11 on Windows. These are local receipts, not a hosted-CI
or maintainer acceptance claim.

The finite replay checks:

- all512 affine addresses and reverse actions, all512 strict-upper phases;
- 508 actual negation bit words across widths2–8;
- 10,880 actual phase-pass coefficient pairs across widths2–5, all four phases
  and both directions: 10,408 satisfy the precise signed guard, 472 expose
  its boundary while retaining correct modular execution;
- 4,096 tensor-phase cases at column counts f=1,2,3,7 and two bit spacings;
- the actual selected directed monomial on a complete4,096-record address
  rectangle, all8 dirty spectator combinations, two Gaussian coefficients
  per record, at coefficient widths2 and5, with inverse restoration.

The last two full-array runtime fixtures use specified correlated coefficient
patterns; they do not enumerate every possible coefficient payload. Arbitrary
payload/column conclusions come from the conditional formal model.

Nineteen controls comprise fourteen source corruptions and five semantic
boundaries: one's-complement carry, inverse phase at the wrong address,
affine offset before the linear word, missing the repeated constant phase,
and most-negative signed overflow. For example, at b=5, phase2 sends encoded
`(-16,0)` back to encoded `(-16,0)`, although integer negation requires
`(16,0)`. Byte roundtrip still passes. This illustrates the headroom
condition already stated in PR2250 section5; it is not a newly alleged defect.

## Reproduce

From the repository root, with standard-library Python3.12:

```sh
python3.12 scripts/research_package.py --package research/selected-monomial-coordinate-refinement
```

This runs finite replay normally and under `-O`. To intentionally regenerate
the finite receipt, use `verify.py --write-result`.

For the formal layer use Lean4.33.0-rc1, commit
`62eed1db4d67327ec8120be05f1a1b0847d74561`, and the exact nine dependency
revisions in `lean/lake-manifest.json`, including Mathlib
`55b7917b472489c7c56a0fa6393af05cfd536599`. Prepare those package checkouts
and their official compiled cache, then run:

```sh
python3 kernel.py --lake /absolute/lean-4.33.0-rc1-linux/bin/lake \
  --work-dir /fresh/monomial-build --packages /pinned/.lake/packages \
  --out /fresh/monomial-kernel.json
```

Run that command from this package directory. The build directory and receipt
must not already exist. The harness checks Lean's version/commit, each
dependency's revision and tracked-source cleanliness, and copies only source
files into the fresh build. It rebuilds the local proofs, checks named theorem
axioms against `propext, Classical.choice, Quot.sound`, and requires actual
mathematical rejection of three false statements. No `sorry`, custom axiom,
`native_decide` or externally evaluated proof admission is used.

Dependency compiled caches are reused after source/revision checks; their
compiled bytes are not independently rebuilt or authenticated. The receipt
states this trust boundary. Hosted CI is separate from the local kernel
receipt. The dedicated workflow contains the complete cache-preparation and
fresh-build commands.

## Limits

The formal model retains completed Compact/digit-permutation and address
decode contracts; it does not prove the sequential repair algorithm, work
bound, scratch closure or physical tape runtime. The per-coefficient word
proof does not formalize Python allocation or record enumeration. The phase
word model and generic tensor theorem are separate checked bridges, joined by
source binding and the written interpretation, not a verified Python-to-Lean
compiler.

No other selected monomial, whole serialized native word, ownership chronology,
all-size recursive caller, numerical precision/error transfer or integer
packing theorem is admitted by this package. No source/frontier file is
modified. A separate AI review is not human or maintainer acceptance.

## Open next questions

**Discharge the completed primitive premise for one actual Compact branch.**
This would connect the arbitrary-column-count endpoint theorem to sequential
repair and dirty-field restoration. Start with a source-faithful formal model
of one earlier-source compact operation, including exceptional-record
extraction, key inversion and reinsertion. The blocker is that physical
algorithm and its layout contract; another single-column tensor identity does
not discharge it. Coordinate with the ongoing complete-caller/dispatcher work
before extending the scope.

**Compose coefficient encoding with the address interpreter.** The present
word arithmetic and tensor coordinate proofs have explicit matching contracts.
A formally verified record traversal/encoding relation would remove the
remaining manual bridge. Start with a fixed record layout and prove the scan
preserves record boundaries while applying `phase_pass_coefficient` to every
coefficient. This requires a tape semantics, not additional random samples.
Structured questions are in `TASK.json`.

## Credit

Prepared by AAAmirinu with substantial OpenAI Codex assistance, including
separate formalization, execution-harness and review agents. Apache-2.0.

Jose Manuel / jmbarrancoml supplied PR2250's compiler, tape interpreter, source
binding and written argument; Gareth Davidson / bitplane supplied PR2341's
general tensor theorem and fresh-build pattern. PR2287's argument, Douglas
Colkitt's construction, DreamingOfClouds' LemmaG semantics and its documented
predecessors remain credited in the copied notices. Mathlib supplies the
tensor, algebra and arithmetic libraries. Original source bytes and notices
are preserved.

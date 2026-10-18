# PR2979 cleanup fixes arbitrary dirty private arrays

For the original PR #2979 cleanup, all 91 private arrays return to their own
entrance values, even when those values are dirty. No private entrance value
leaks into a live output. This holds for arbitrary live entrance arrays, in
both providers and both orientations, without a reachable-state premise from
the prefix.

This closes the explicit unrun arbitrary-cleanup-entrance question in
[PR #3238](https://github.com/CrocSwap/integer-mult-bounds/pull/3238). It also
strengthens zero-return to a dirty-private identity. It is a finite algebraic
certificate, not a complete native, physical or multiplication theorem audit.
There is no new kappa, supplier admission or selected-frontier change.

## Exact statement

Let `V` be any vector space over the rationals. The 632 live arrays and 91
private arrays are distinct and disjoint copies of `V`. Run the literal
5,207 cleanup gates under their FULL-frame scalar/linear-map interpretation.
For either orientation, the cleanup operator has block form

```text
                live entrance    private entrance
live output          A                  0
private output       0                 I_91
```

The live block `A` is not asserted to be identity. All 112 target arrays are
unchanged. Each private array equals its own arbitrary entrance at its last
literal cleanup touch, including a final read rather than a final write.
Zero entrance therefore implies zero at every corresponding return boundary,
provided the native schedule binds that boundary to this last touch.

The 72 cleanup warp sites may be arbitrary linear maps, independently. No
commutation, phase normalization, inverse identity or native Clifford recipe
is used in this statement. For the physical dual interpretation, instantiate
them with the appropriate inverse-transpose maps. The literal dual scalar
rules are `s -= q*t` for `t += q*s`, and reciprocal scaling.

The two providers have byte-identical cleanup lists but different warp
recipes. Their canonical cleanup SHA256, using JSON with separators `,` and
`:`, is `af0fd40c22a5fa100525f68e16228ea2ebcc1ae4e5ca1f0e7564f277fe299c79`.
Checking both source files authenticates both assignments; it is not two
independent cleanup constructions.

## Proof and certificate

Work in the free associative algebra over the rationals on the signed warp
names. A polynomial term is an entrance-array symbol preceded by an ordered
word of map symbols. The two symbols `i` and `-i` are independent. The checker
never cancels inverse pairs and never exchanges operators.

Initialize all 723 rows as independent entrance symbols, including the 91
private rows. For each gate:

- ADD replaces its target row by the target plus the rational coefficient
  times the source row.
- SCALE multiplies its row by the exact rational coefficient.
- WARP prepends its formal map symbol to every term in its row.

Induction over the ordered gate list proves that each row is the literal
cleanup's linear expression in all entrance arrays. The source-bound replay
then checks that each private row is exactly its own symbol, every live row
has zero coefficients on all private symbols, and every target row is its
own symbol. These are exact polynomial identities, not sampled numerical
agreements. Substitution of arbitrary linear maps preserves each identity.
The last-touch assertions follow because no later gate reads or writes the
returned private array.

`verify.py` performs that full forward row propagation. `RESULT.json` binds
the complete formal matrix with deterministic hashes and records every private
last touch. The maximum intermediate row has 112 terms forward and 120 dual.
The live block changes 429 rows forward and 397 dual, so this certificate must
not be read as a proof of the complete invocation's live endpoint.

`backward.py` is a separately implemented check with no import of the forward
interpreter or any predecessor verifier. It pulls 91 private output covectors
back through the reversed gate list, multiplying map symbols on the right.
It also pulls them through the transposed program, independently checking the
91 private input columns. Formal transpose reverses operator words; it assumes
no symmetry of a map. All 728 row/column checks across the two providers and
two orientations give unit vectors. The peak covector support is recorded in
`BACKWARD.json`. This is algorithmic cross-checking by the same contributor,
not independent human review or formal-kernel verification.

## A control that clean-only replay misses

The last touch of private array 1003 is cleanup gate 4844, zero-indexed:

```text
live[302] -= private[1003] / 4
```

Doubling that coefficient leaves the complete cleanup map unchanged whenever
all private entrances are zero. The clean-only replay therefore accepts this
mutant. With arbitrary dirty private entrances, its exact difference from the
original is

```text
live[302]      -= private_entrance[1003] / 4
private[930]   += private_entrance[1003] / 8
private[934]   += private_entrance[1003] / 8
```

Setting only private entrance 1003 to one gives an explicit witness, with no
warp assignment needed. The dirty-identity check rejects it. This establishes
new failure coverage beyond zero-return under clean allocation.

Other controls reject a dropped closing gate, a changed closing coefficient,
a premature return, private leakage and private scaling, malformed geometry,
non-FULL frames, removed-register access, invalid scalars/operators, source
corruption, duplicate JSON keys and a changed receipt. Noncommuting toy words
check both interpreters' multiplication order and transpose handling.
A changed live-only warp can preserve the private contract while changing
the live matrix hash. That control explicitly prevents treating private
success as certification of all native/live semantics.

## Sources, overlap and scope

Base canonical main is `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority
revision 6. Both live inputs match PR #2979 head
`be191346391661f4d35fc0d1508d0a6029572576` byte for byte. `SOURCES.json` pins
the compressed inputs with Git blobs and SHA256, plus catalogue and selected
record provenance. Frozen inputs and existing packages are unchanged.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19002977)
identifies this refinement of `independent-moment`. Its first working baseline
command passed. The complete overlap snapshot at entry covered 284 open PRs
at 2026-10-17 18:59:06 UTC and 2,059 Discussion records at 18:59:36 UTC.
The searches included the task, `arbitrary cleanup entrance`, `rank7 cleanup`
and `3238`; they do not cover every diff or unpublished work. The pre-submission
fetch at 2026-10-17 19:08 UTC found canonical main unchanged, with no guidance,
selected-record or relevant source delta. Refreshed complete snapshots covered
288 open PRs at 19:08:36 UTC and 2,067 Discussion records at 19:09:05 UTC;
no new overlapping arbitrary-dirty-cleanup result was found.

Nearest predecessor coverage:

- PR #3238, head `3c689aac34ff240f82e27dcc7f0247b96b8676af`, proves the
  original words' clean zero returns at actual native frees, relative to the
  original inputs and their expanded prefix dependency cone. It explicitly
  leaves arbitrary cleanup entrance unrun. No executable from it is imported.
- PR #3208, head `87d63a82defff1ffeea173743106fb97903cbbd6`, proves arbitrary
  live entrance with clean private buffers for PR #3044's different R2
  cleanup. Its 5,208 gates are not this 5,207-gate cleanup; it independently
  checks native recipes, which this package does not. No code is copied.
- PR #2979's existing auditor checks a whole invocation with clean private
  buffers and derives cleanup from the preceding word. This package checks
  the isolated cleanup and arbitrary dirty private inputs directly.

A possible consumer may borrow dirty arrays instead of supplying clean ones
under this scalar/linear contract. That is only an interface corollary. The
unchanged schedule still requires 91 distinct arrays disjoint from live
storage, and their intermediate values need not equal their entrances.
Acquisition, backing ownership, movement, finite precision and native
allocation/free legality are unpriced. No stock, role or recursive-rank
saving follows here. Prefix/native phases, complete supplier/outer replay,
all-size/compiler/analytic obligations and hosted CI are not checked.

## Reproduce

Python 3.12 standard library, no third-party dependencies:

```sh
python3.12 -I -O -Werror -B research/rank7-cleanup-dirty-identity/verify.py
python3.12 -I -O -Werror -B research/rank7-cleanup-dirty-identity/backward.py
python3.12 -I -O -Werror -B research/rank7-cleanup-dirty-identity/test_verify.py
python3.12 -B scripts/research_package.py --package research/rank7-cleanup-dirty-identity
ruff check research/rank7-cleanup-dirty-identity
```

`--emit` on either interpreter reconstructs its JSON receipt on stdout.
Normal replay is read-only. Local checks pass on CPython 3.12.15 and 3.13.5,
Linux 6.6.87.2-microsoft-standard-WSL2 x86_64; Ruff 0.17.1 passes. Tests use
explicit exceptions for acceptance, including under `-O`.

## Open next questions

1. Can one of these dirty-private arrays be acquired, kept disjoint and returned
   under an actual paid native owner contract? Start with one literal private
   interval from PR #3238 and price its physical backing and arithmetic range.
   The current block identity does not supply that contract or a cost saving.
2. Can the 91-array boundary contract simplify the original native dependency
   cone? Compose it with the already checked native event/warp bindings and
   compare the exact required premises with PR #3238. A rechecked native
   schedule and its linear-map conventions are prerequisites; do not infer
   correctness of the live prefix from this isolated cleanup.

## Credit and engineering limits

Nick Petalas. Apache-2.0. Credit Marius-Paul Dumitrean for PR #2979/#2942's
words; Jeremy Kothe for the inverse cleanup, frame and rewrite lineage;
Mason Hale and Jeremy Diviney for PR #2917/#2908's paired extraction chain;
commdata2338 for PR #3238's explicit arbitrary-entrance handoff and original
private-free audit; 24kHandsome1201 for PR #3208's separate R2 result and
method context; ToikY for PR #3038's source/native machinery; and the retained
source geometry, compiler and owner contributors credited in PR #2979.
New code imports no predecessor implementation. Research, implementation and
checking used substantial automated assistance; no independent human review
is claimed.

Build the Lever led to the retained full-matrix and reverse-covector tools.
Prove It Works required literal source replay and the clean-only blind-spot
control. Power-of-Ten constraints bound source payloads to 4 MB, gates to 6,000,
registers to 800, terms per polynomial to 4,096, word length to 256, and rational
numerator/denominator sizes to 4,096 bits. Capacity failures raise errors;
functions remain below 60 physical lines. Registered commands have finite
timeouts. The Python managed-runtime deviation from fixed post-initialization
allocation is restricted to these bounded polynomials and fixtures. Python's
ordinary dynamic dispatch and unittest framework are the corresponding
rules 8/9 deviations, with only the two named local interpreters as test
imports and no dynamic predecessor loading. Reassess these capacities and
resource contracts before enlarging the domain or adopting a physical caller.

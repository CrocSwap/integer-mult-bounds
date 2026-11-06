# Two frame relations cannot share rank, at any register count

**Scoped universal lower bound. No new κ.** In the formal binary
scalar-idempotent model, a word with at most two independent integral
relations among its address frames cannot save paid rank, regardless
of its number of scalar registers or diagonal auxiliary outputs.

More precisely, every target address in a diagonal monomial endpoint
is a sum of a disjoint subset of the paid addresses. For rational
matrix frames this gives

\[
\sum_i \operatorname{rank}_{\mathbb Q} C_i
\le \sum_j \operatorname{rank}_{\mathbb Q} A_j.
\]

Thus rank-one calls need **at least three independent frame relations**
to beat total target rank. In particular, eight calls for three
invertible `3 x 3` targets cannot have frame span six, even with
arbitrarily many dirty auxiliaries and arbitrary diagonal monomial
auxiliary outputs. Combined with earlier results, frame span five is
the remaining eight-call case in this formal alphabet.

## What is new relative to the archive

The result extends David Govea's three-register disjoint-subset theorem
in CrocSwap/integer-mult-bounds#720 and woklerx's arbitrary-register
one-relation bound in CrocSwap/integer-mult-bounds#1456. It resolves
their missing width/two-relation combination by three compatible steps:

1. A common cyclic pattern reduces to an odd all-ones core. The
   quadratic prefix argument is extended to **every odd core size**,
   proving that its noncoordinate calls cancel at a diagonal endpoint.
2. A two-pattern noncoordinate pool has joint image dimension at most
   **three**, except the four lifts of two disjoint single edges,
   which are coordinate triangular. This is a written classification
   for every width. Its sharp maximum image dimension four improves
   the bound five obtained from the pool-cardinality theorem in
   CrocSwap/integer-mult-bounds#5921; that predecessor's sharp
   cardinality theorem remains unchanged.
3. A saturated cube-valued relation basis separates intervening
   coordinate calls as free exponent generators. Restrict the remaining
   word to its small image, apply the inherited three-register theorem,
   then reconstruct every original target, including repeated values.

[PROOF.md](PROOF.md) supplies each step and its exact inherited hypotheses.
The final analytic proof does not depend on a new finite scalar census.
[REVIEW.md](REVIEW.md) records a separate written mathematical review and
an alternate target-label argument. It checks the precise inherited
CrocSwap/integer-mult-bounds#720 scope without claiming a new proof of that
three-register theorem or a replay of its unrelated address search.
We credit and independently replay woklerx's **existing** 4,964-plane
classification in CrocSwap/integer-mult-bounds#1846 as corroboration.

Several narrower results were already established and are not claimed
as new here. JoyboyBrian's CrocSwap/integer-mult-bounds#5481 excluded
five calls for three invertible `2 x 2` targets with arbitrary diagonal
auxiliaries, closing the span-four handoff in
CrocSwap/integer-mult-bounds#4118. Josie Elliston's
CrocSwap/integer-mult-bounds#6055 independently enumerated the five-call
case through five registers. The **four-register** span-six case was
closed by CrocSwap/integer-mult-bounds#4119,
CrocSwap/integer-mult-bounds#5075, CrocSwap/integer-mult-bounds#5231 and
CrocSwap/integer-mult-bounds#5552. The new theorem is at arbitrary
width, arbitrary word length, and arbitrary address dimension.

## Exact evidence and verification boundary

The universal proof is written. Its central inherited dependency is
CrocSwap/integer-mult-bounds#720's three-register relation theorem, not
that package's later address-dimension-three search. That theorem is
**inherited, not newly formally verified here**. Nick Petalas's
CrocSwap/integer-mult-bounds#5921 off-diagonal fiber lemma is credited
and recalled in the proof. No unmerged source or network fetch is
needed to run the standalone checker.

The finite tests corroborate precise parts of the argument:

| Check | Executed domain |
| --- | --- |
| Historical four-register alphabet | All 65,536 binary matrices; exactly 120 rank-one idempotents |
| Historical pattern-plane replay | All 104 nonzero patterns and 4,964 generated planes |
| Certificate coverage | Every plane once; every projector preserves its explicit proper-subspace witness |
| Invariant block reduction | All 3,600 invariant projector/subspace pairs on four registers |
| Sharp joint-image classification | Every generated pattern plane at widths 2, 3, 4, 5: 1, 129, 4,964, 108,165 planes |
| Equality cases | Exactly 12 image-dimension-four pools at width four and 60 at width five; all are disjoint-edge pools |
| Odd-core quadratic mechanism | 20,097 prefix-placement cases at core sizes 3, 5, 7 and J-call counts 2, 3, 4, one coordinate occurrence per role |
| Whole formal endpoints | Odd-core cancellation and noncancellation words; a six-call rational span-three fixture |
| Failure controls | Omitted plane, proper but noninvariant witness, deleted paid calls, missing helper cleanup, separated internal gaps |
| Scope controls | Irreducible odd-width common-J alphabet, nontriangular three-coordinate subblock, intervening coordinate gates, and repeated-target eigenspaces |

[CERTIFICATE.json](CERTIFICATE.json) records all 4,964 invariant-space
witnesses. [verify.py](verify.py) regenerates the complete domain and
checks each witness directly. Its structural census uses a separate
outer-product enumeration at widths through five. The universal proof
does not extrapolate those finite counts.

The six-call fixture has integer frames `2 E11, 2 E22`, then
`2 E11, 4 E22`, then `3 [[1,1],[1,1]], [[1,-1],[-1,1]]` on the three
data coordinates. These span the symmetric `2 x 2` space and produce
`2 I`, `diag(2,4)`, `[[4,2],[2,4]]`, while helpers remain identity.
Their target relatives have commutator determinant one, so no common
algebraic flag is silently assumed. This is a sharpness control,
not a new construction. Even address entries remain nonzero; only
scalar coefficients use characteristic two.

## Reproduce

From the repository root, Python 3.12 and its standard library suffice:

```sh
python3 -I -W error -B research/bit-two-relation-any-registers/verify.py
```

Expected first line:

```
PASS_TWO_RELATION_ANY_REGISTERS
```

The next JSON line gives every count above. The same complete check
is registered normally and with Python assertions disabled:

```sh
python3 -I -O -W error -B research/bit-two-relation-any-registers/verify.py
python3 -B scripts/research_package.py --package research/bit-two-relation-any-registers --check-only
python3 -B scripts/research_package.py --package research/bit-two-relation-any-registers
```

Regenerate certificate bytes without changing the tracked file:

```sh
python3 -I -B research/bit-two-relation-any-registers/verify.py --emit-certificate /tmp/two-relation-certificate.json
cmp research/bit-two-relation-any-registers/CERTIFICATE.json /tmp/two-relation-certificate.json
```

There is no random seed: domains are deterministic and fully exhausted
at the stated widths and prefix bounds. This is not a word search over
`120^5` cases. No native compiler, solver or third-party library is used.
Metadata validation authenticates the canonical provenance in
[SOURCES.json](SOURCES.json); the direct verifier is self-contained.
[VERIFY.json](VERIFY.json) declares no external live scientific inputs.

## Scope, assumptions and provenance

Base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`; catalogue revision 8;
seed 12, card `bit-new-register-model`. [TASK.json](TASK.json) retains
the full original card, the explicit scope change and stopping rule.
The original five-call question had already been solved; the contribution
addresses the remaining arbitrary-width two-relation question identified
across CrocSwap/integer-mult-bounds#1456,
CrocSwap/integer-mult-bounds#1846 and CrocSwap/integer-mult-bounds#5921.

The theorem requires a torsion-free exponent group, binary rank-one
idempotent scalar calls, and exact whole-matrix diagonal monomial
endpoints. Helpers may be arbitrary inputs and may return arbitrary
diagonal monomials; exact identity restoration is a special case.
Finite-address coincidences, approximate endpoints, discarded or
zero-initialized-only inputs, nondiagonal outputs, nonabelian address
operations and other scalar fields are outside the theorem.

The selected conditional κ remains `0.003125804` at the pinned base.
Native all-columns, owned erasure, compiler, precision/tape and analytic
recovery assumptions are unchanged. No complete supplier, physical
cost invoice or multiplication improvement follows from this obstruction.

## Open next questions

1. **Eight calls at frame span five.** This gives three independent
   relations and is the remaining formal three-target case after the
   older low-span results and this theorem. Begin with rank-three cube
   relation lattices and the associated three-dimensional spaces of scalar
   patterns. Unlike rank two, independent cube relations need not have a
   unit minor; the free-coordinate split requires new saturation work.
2. **Sharp joint-image dimension for three-dimensional pattern spaces.**
   Three disjoint edges give image dimension six, while
   CrocSwap/integer-mult-bounds#5921 gives the upper bound ten from
   cardinality. Extend the diagonal-difference argument before launching
   a large pool search. A better width reduction would help the span-five
   question, but does not itself prove a three-relation word theorem.

## Credit and license

Prepared for **@CubeJerry** with substantial OpenAI Codex assistance
for mathematical development, exact checking and separately assigned
adversarial review. No independent human acceptance or proof-assistant
certification is claimed. New files are **Apache-2.0**.

Credit eumemic's CrocSwap/integer-mult-bounds#288 model; Ali Romman's
CrocSwap/integer-mult-bounds#468 scalar/relation framework; David Govea's
CrocSwap/integer-mult-bounds#720 theorem and common-J proof; woklerx's
CrocSwap/integer-mult-bounds#1456 and CrocSwap/integer-mult-bounds#1846;
Nick Petalas's CrocSwap/integer-mult-bounds#5921 fiber/cardinality theorem;
and the predecessors identified above. @CubeJerry's
CrocSwap/integer-mult-bounds#6760 compression motivated the original
assignment but is not a dependency of the final theorem.

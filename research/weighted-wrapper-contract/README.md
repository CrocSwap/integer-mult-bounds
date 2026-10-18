# Exact weighted-callee contract for the ordinary wrapper

**Result: scoped interface theorem and independent exact checks; no new κ.**
The unchanged two-call ordinary wrapper works with additive maps `P,Q` exactly
when **`Q=P` and `P²=I`**. Replacing only the second callee cannot repair a
non-involutory first map. For finite address groups, using the same map twice
already maximizes the number of correctly exchanged address pairs among all
possible additive second maps.

This audits a possible substitution at Nick Petalas's [PR2808](https://github.com/CrocSwap/integer-mult-bounds/pull/2808)
callee boundary. That package already warns that an involutive **callee** is
insufficient and gives one modulo-3 counterexample. It correctly requires an
unweighted callee. Jose Manuel/jmbarrancoml's
[PR2899](https://github.com/CrocSwap/integer-mult-bounds/pull/2899) likewise
explicitly supplies unit root weight. **No defect in either stated construction
is alleged.** The new results are the two-distinct-callee necessity theorem,
optimal error-image bound, exact prime-power agreement count, and a failure
invisible at every lower precision. These help audit future callee substitutions.

## Exact statement and proof

Fix an abelian address group `G`. Fix two additive automorphisms `P,Q` of `G`,
independent of the current body addresses. They may be selected by spectators
that remain fixed throughout this word. Write

```
F_P(H,D) = (P D, P^-1 H),       F_Q(H,D) = (Q D, Q^-1 H).
J(H,D)   = (D,H).
```

Both `F_P` and `F_Q` are involutions for **every** such `P,Q`; that alone says
nothing about compatibility with the wrapper's additions. Composition is
ordered: `PQ` means apply `Q` then `P`. No commutation is assumed.

Execute the literal chronological body from `outer.body_ordinary`:

```
D -= H; F_P; D += H; F_Q; D = -D; D += H.
```

After the middle addition the banks are
`(P(D-H), P^-1 H + P(D-H))`. Therefore the final output is

```
H' = Q(P^-1-P) H + QP D,
D' = H' - Q^-1 P(D-H).                         (1)
```

**Theorem 1 (necessary and sufficient contract).** This word equals `J` on
all of `G x G` iff `P²=I` and `Q=P`.

*Proof.* If it is `J`, set `D=0` in the first line of (1). Invertibility of
`Q` gives `P^-1-P=0`, hence `P²=I`. Next set `H=0`; `QP=I`, so `Q=P^-1=P`.
Conversely these identities make the first output `D` and the second `H`.
The argument includes characteristic two and does not require a field. ∎

This distinguishes two requirements: each *callee* `F_P` is involutive
without restriction, while its *one-bank map* `P` must also be involutive.
Even two individually admissible one-bank involutions fail if they differ.

Let `A=P²-I`. When `Q=P`, (1) simplifies to the exact error identity

```
(H',D') = (D,H) + (A(D-H), A(D-H)).              (2)
```

Thus testing only `H'-D'=D-H` misses every error in this family.

**Theorem 2 (best possible second callee, finite G).** For the additive error
map `E_(P,Q)=W_(P,Q)-J`,

```
min_Q |im E_(P,Q)| = |im(P²-I)|,
max_Q #{(H,D): W_(P,Q)(H,D)=(D,H)} = |G| |ker(P²-I)|.  (3)
```

The extrema range over all additive automorphisms `Q`; `Q=P` attains both.

*Proof.* Restrict the first error coordinate to `D=0`. Its image is
`im(Q(P^-1-P))`, of size `|im A|`, since `P^-1-P=-P^-1 A` and the outside
maps are automorphisms. Projection cannot increase an image's size, so the
whole error has image size at least `|im A|`. For `Q=P`, (2) gives exactly
the diagonal image `{(Ax,Ax):x in G}`, since `D-H` is surjective onto `G`.
For every `Q`, the correct pairs form `ker E_(P,Q)`. The finite-group
kernel-image identity gives (3). ∎

For finite-dimensional vector spaces, when P and Q are linear over the field,
the same restriction/attainment proof
also gives `min_Q rank(E_(P,Q))=rank(P²-I)`. This is an endpoint-error bound,
**not** an operation-count or circuit lower bound.

## Weighted reversals and precision blindness

Put `G=(Z/MZ)^n`, `M>=2`, and let each `a_i` be a unit. Define the convention
`(P_a x)_i=a_i x_(n-1-i)`. Its inverse uses reciprocal weights in reversed
order. Consequently

```
P_a² = diag(a_i a_(n-1-i)),
P_a²=I iff a_i a_(n-1-i)=1 mod M for every i.     (4)
```

Theorem 1 says that the two weight lists must be identical modulo M and satisfy (4).
Nontrivial reciprocal pairs are permitted: `(4,7)` modulo 9 is valid.
At an odd-length middle coordinate, require `a_i²=1`; only for an odd prime
power does this reduce to `a_i=+1 or -1`. For example, 3 also squares to 1
modulo 8. No stronger restriction on general composite moduli is asserted.
For odd prime powers, the middle-coordinate assertion follows from
`(a-1)(a+1)=0`: the two factors cannot both be divisible by the odd prime,
so one factor must contain its full power.

For two equal weighted calls, each difference coordinate must solve
`(a_i a_(n-1-i)-1)(D_i-H_i)=0 mod M`. The kernel of multiplication by an
integer `c` on `Z/MZ` has `gcd(M,c)` elements: divide `M,c` by their gcd,
then the remaining coefficient is coprime to the remaining modulus. For each
allowed difference there are `M` choices of `H_i`. Hence the exact number of
correct address pairs is

```
M^n product_i gcd(M, a_i a_(n-1-i)-1).           (5)
```

By Theorem 2 no other additive second callee can improve that count while the
first callee and all surrounding additions remain fixed.

**All lower precisions can pass while the next one fails.** For any prime
`p` and integer `w>=2`, use two coordinates, modulus `M=p^w`, and
`a=(1+p^(w-1),1)`. Both weights are units and `P_a²-I=p^(w-1) I`.
Every reduction modulo `p^j`, `1<=j<w`, is the ordinary reversal and satisfies
the wrapper identity. At full precision (5) gives exactly `p^(4w-2)` correct
pairs out of `p^(4w)`: fraction `1/p²`. This is an algebraic family, not a
claim that these weights occur in the selected generated programme.

The explicit `p=3,w=2` example has 729 correct pairs and 5,832 failures among
6,561. At `H=(0,0),D=(1,0)`, the output is `((4,0),(3,0))`, not
`((1,0),(0,0))`. Both individual callees remain correct involutions, their
modulo-3 reductions pass, and the output difference is still correct.

## Reproduction and actual evidence

From the repository root, with standard-library CPython 3.12:

```sh
python3 -I -Werror -B scripts/research_package.py --package research/weighted-wrapper-contract
```

Expected command output includes `PASS_WEIGHTED_WRAPPER_CONTRACT no_new_kappa`
and ends with `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`.
`RESULT.json` is a deterministic, read-only receipt. The standalone verifier's
`--emit-to NEW_EXTERNAL_PATH` is an explicit, exclusive-create regeneration
option; ordinary verification never rewrites evidence.

The finite-map oracle enumerates matrices, tests their bijectivity directly,
and executes the six operations on every address pair. It does not call the
predecessor or decide acceptance by substituting the theorem's criterion.
It then compares observed endpoints, error images and agreement counts with
that criterion and the optimum (3):

| Address group | Automorphisms | Ordered callee pairs | Address-pair evaluations |
| --- | ---: | ---: | ---: |
| `(F2)^2` | 6 | 36 | 576 |
| `(F3)^2` | 48 | 2,304 | 186,624 |
| `(F2)^3` | 168 | 28,224 | 1,806,336 |
| `(Z/4Z)^2` | 96 | 9,216 | 2,359,296 |
| **Total** | | **39,780** | **4,352,832** |

A separate weighted census exhausts all 75 unit-weight lists for `(M,n)` in
`{(2,1),(3,1),(4,1),(8,1),(9,1),(3,2),(4,2),(8,2),(9,2)}`: 303,876 address-pair
evaluations, checking (2), (4) and (5). These are complete finite domains;
there is no randomized search or extrapolated impossibility claim.

The source check authenticates the unchanged PR2808 body and PR2786 padding,
whose loader authenticates the complete 84-file PR2753 export. It executes
literal native ADD, sign and padding operations using Boolean coordinate
bit planes, assigning nonzero codes 1 through V to original positions and
reserving zero for padding. Recovering each output's input-origin index checks the complete
permutation, not one convenient all-zero payload. No predecessor endpoint
checker is imported. Four fixtures cover 15,075 addresses across 41 bit-plane
runs: modulo-3 success with prefix/gap/suffix spectators and 3-to-4 row padding;
the modulo-9 failure above; the valid `(4,7)` modulo-9 pair; and different
one-coordinate involutions. Input bytes, heads, count tapes and live numerical
scratch are checked at return.

The source harness deliberately supplies weighted callees as finite
address-permutation oracles. It checks the **unchanged wrapper's response to
those exact endpoints**, not a physical implementation or cost of a weighted
callee. The input-independent native payload copies justify the bit-plane
method; it is not a test of every possible Boolean function. The all-group
proofs above are written mathematics, not proof-assistant results.

Semantic controls reject an involutive-callee-only rule, inverse-second
repair, a difference-only endpoint test, nonunit weights, and mutated operation
order/inverse handling. A reciprocal-weight positive control prevents a
blanket rejection of weighted calls. Source and typed-receipt corruption
controls are recorded by `test_verify.py`. Exact commands, environment and
verification status are in `TASK.json`.

## Scope, sources and credit

Scientific base: `9ee73fecdbae9f892a6496dbdfae872217cf4601`, priority revision 5.
Before publication the branch was fast-forwarded to canonical main
`95ff4e2dd396c505932a43ff7c1cdfdd94b8c867`; the guidance, selected record,
replay tools and every consumed input were unchanged. `TASK.json` records
the bounded overlap refresh and local-only claim.
`SOURCES.json` pins every consumed external file by SHA256 and Git blob.
PR2808 is pinned at `b00b58e0db823643364f705b530faac254e7b05b`; its unchanged
padding export pins PR2786 `80df2062cef303c05ffe89bb54b87b6b371d1253` and PR2753
`7dba5452a4071a856a0b11cebdcd2d3b6bcd7659`. The local review ledger records
PR2808, PR2786 and PR2899 as incorporated research. Selected construction,
frozen sources and `upstream/` are unchanged.

Credit Nick Petalas for PR2808's wrapper and original weighted counterexample,
PR2786 padding and retained ordinary identity; David Arias for PR2753's
logical caller and linear sign; Jose Manuel/jmbarrancoml for the retained
PR2697 numerical/stream lineage and PR2899 physical composition; and the
original authors credited in the unchanged source notices. This package does
not claim their constructions, identities, prior counterexample or prices
as new. Jerry Chen (@CubeJerry), with substantial OpenAI Codex assistance in
reasoning, code, verification and writing. Apache-2.0. No independent human
or formal-kernel review is claimed.

This is a fixed-word interface audit, not a new callee, supplier, improvement
to multiplication, or universal barrier. Changed surrounding shears, extra
normalization, affine/input-dependent maps and non-pointwise row contracts
are outside the theorem. It neither proves the selected all-size/compiler,
physical hosting, precision/tape and analytic assumptions nor reruns the full
selected cold replay. **No new κ.**

## Open next questions

Can one concrete weighted callee be normalized at an affordable complete cost?
Start by pinning its weights and charging every scale/inverse, source access,
frame change, copy and restoration needed to satisfy (4). The theorem supplies
an endpoint criterion, not that missing implementation or budget. A changed
wrapper could evade this fixed-word theorem, but would require its own proof
and complete invoice. The current unit-weight wrapper needs no such repair.

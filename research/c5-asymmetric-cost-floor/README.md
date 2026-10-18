# Sharp asymmetric cost 20 on the named physical C5

**Scoped proof with finite geometric and combinatorial premises.** On
PR2484's physical core `(13,23,35,16,34)`, every finite asymmetric rank-one
decomposition of the strict scalar endpoint costs at least **20** under the
inherited complete source/target plane tariff. Five terms attain 20. Factors
and coefficients may be rational, real or complex, with arbitrary signs,
denominators, supports and term counts. The fitting matrix need not be symmetric.

A weighted rank cover gives 18. Equality traces exclude cost 18, and exact
finite support-count enumeration excludes all ten possible cost-19 cases.
This is an exhaustive necessary-condition proof, not a failed coefficient
search or a solver timeout. It concerns this named core only.

## Exact object and price

Write the five planes in the stated cyclic order as `E_0,...,E_4`. Their
ordered binary-dot bases, reconstructed from the pinned PR2782 inputs, are:

```text
[(289,49), (194,134), (304,56), (50,193), (200,196)].
```

Each plane has Gram matrix `I2` over `F2`; adjacent planes are orthogonal,
and nonadjacent planes are not. This binary form is not alternating. Each
plane has two scalar ports. A fitting `10 x 10` matrix K has diagonal one,
off-diagonal entries within each plane zero, and all cross entries between
nonorthogonal planes zero. Adjacent-plane cross entries are free.

Consider `K = sum_t a_t u_t v_t^T` over `Q`, `R` or `C`, with ordinary
transpose. Omit zero coefficients and zero factors; absorb `a_t` into `u_t`.
Let A_t and B_t be the planes touched by the source and target factors.
The term costs

```text
c(A_t,B_t) = rank_F2 [(x dot y) : x in both basis labels of A_t,
                               y in both basis labels of B_t].
```

Touching one port charges its whole plane. The rectangular binary pairing
rank is independent of scalar coefficient magnitudes or signs. All tariffs
are nonnegative integers, including possible zero-cost nonzero terms.

## Weighted cover and exact slack budget

Use four forced principal identity blocks

```text
Q = {(0,2), (0,3), (1,3), (1,4)},
```

each of size four, and the two size-two singleton blocks at planes 2 and 4.
The remaining forced block `(2,4)` also has size four. For any such block H,
let `b_H(A,B)` be one exactly when both A and B meet H. Let n_H count the
terms with that property. Their restricted rank-one terms sum to `I_r`, so
rank subadditivity gives `n_H >= r`.

The first finite premise is checked for **all 1,024 ordered support pairs**:

```text
d(A,B) = 2c(A,B) - 2 sum_{H in Q} b_H(A,B) - b_{2}(A,B) - b_{4}(A,B) >= 0.
```

For total cost C, put `x_H=n_H-4`, `y_2=n_2-2`, `y_4=n_4-2`, and
`D=sum_t d(A_t,B_t)`. All are nonnegative integers, and exactly

```text
2C - 36 = 2 sum_{H in Q} x_H + y_2 + y_4 + D.
```

Hence C >= 18. At cost 18 every excess and D is zero. At cost 19 the
right-hand side is two, allowing precisely ten cases:

- One of the four x_H is one; both singleton excesses and D are zero.
- All x_H are zero, `(y_2,y_4)` is one of `(0,0),(1,0),(0,1),(2,0),(0,2),(1,1)`,
  and `D=2-y_2-y_4`.

## Traces forced by rank equality

If exactly r nonzero rank-one summands form `I_r`, assemble them as columns
of square matrices U and V. Then `UV^T=I_r`, so `V^TU=I_r`. Every individual
summand has trace one. This uses no positivity or conjugation.

For one term define `z_i=u_i^T v_i` on its two ports. Necessarily `z_i=0`
when plane i is absent from A or B. In a proposed slack case, impose

```text
sum_{i in H} z_i = b_H(A,B)
```

only for the six selected blocks whose count equals their rank. A block
with excess terms imposes no such termwise trace equation. These are rational
linear equations: consistency over Q is equivalent to consistency over R
or C. They are necessary conditions only; satisfying them is not an actual
factorization.

At cost 18, all six blocks are tight. Of 354 zero-defect support pairs,
208 pass these trace equations, including all 83 zero-cost pairs. Only four
survivors touch the missing `(2,4)` block on both sides, with masks
`(20,20),(20,28),(28,20),(28,28)`. All contain both planes 2 and 4 on both
sides. Therefore `n_(2,4)=n_2=n_4=2`, contradicting its required rank four.

## Exhausting cost 19

For each of the ten cases, retain every support pair satisfying that case's
trace equations. Its increment is

```text
(four Q-block hits, singleton-2 hit, singleton-4 hit, d, missing-block hit).
```

Enumerate additive states from zero, allowing **unbounded repeated use** of
each increment. Bound the first seven coordinates by the case's exact target
counts and D. Saturate the last coordinate at four, since the missing block
requires at least four terms. Identical increments may be combined; no
dominance pruning or factor-coefficient restriction is used.

All 83 zero-cost support pairs have entirely zero increments, including the
20 pairs with both supports nonempty. Their self-loops can be discarded
without bounding the number of free terms. Every positive-cost term advances
a bounded primary coordinate. Thus the state space is finite and contains
the count image of every possible finite decomposition in the case.

None of the ten target states is reachable. The complete replay visits
4,872 states across those cases. A separate implementation independently
reconstructs the dense binary ranks, uses general Fraction Gaussian
elimination for traces and enumerates states by total cost. It reaches the
same per-case results. The retained receipt gives all targets, pattern counts
and state counts. This excludes cost 19; integer tariffs now give C >= 20.

## Attainment and controls

For each cyclic i, take `u_i=v_i=e_(i,1)+e_(i+1,0)` with coefficient one.
The five vectors partition all ten ports, and their only off-diagonal
entries join free adjacent planes. Each term touches two orthogonal complete
planes on both sides and costs four. The full fitted matrix therefore costs
20; replay checks the matrix, tariffs and the corresponding support counts.

A five-term cost-19 support multiset passes all five forced-I4 and all five
singleton-I2 rank counts, but fails the trace equations. Its masks and tariffs
are `(28,28,5),(19,19,5),(7,7,5),(14,24,3),(1,4,1)`. It is retained as a
failure control, not as a decoder: no scalar factors fitting the endpoint
are supplied by these support counts. This demonstrates why the trace step
adds information beyond all those rank cuts. The explicit cost-20 fit
supplies a positive reachability control.

## Reproduce and scope

From the repository root, with standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/c5-asymmetric-cost-floor
```

[SOURCES.json](SOURCES.json) authenticates the two geometry inputs and pins
provenance. [RESULT.json](RESULT.json) is the complete deterministic receipt;
[VERIFY.json](VERIFY.json) declares primary, independent and behavioral checks.
No predecessor executable, external solver or proof kernel is needed.

The proof covers ordinary-transpose factors over Q, R and C on this physical
core. It gives no other-C5, global 112-port, native-word, dirty-restoration,
hosting, precision, all-size or complete multiplication theorem. Local bounds
cannot simply be added across overlapping cores. No selected cold-chain
replay, supplier admission, new kappa or independent human review is claimed.

## Open next questions

Do the other 22 physical C5s admit the same arbitrary-term cost floor? First
reconstruct their rectangular tariffs and find a valid weighted cover; the
present equality/case argument cannot be transferred just from the abstract
cycle graph. Compare with the separate all-cycle five-term result in PR3248.

Can a changed geometry or explicitly justified endpoint contract evade this
local floor? Produce a complete fitting identity and charge all source/target
spans; failing a lower-bound certificate alone is not a favorable decoder.
Any supplier expansion still needs native payload, source access, frame,
restoration, hosting and precision obligations paid.

## Credit and coordination

Tekalign (`tekuuu`), [PR2782](https://github.com/CrocSwap/integer-mult-bounds/pull/2782),
head `002a9983079a3244c10221b4e16d0cff7e70da40`, supplies the physical inputs,
tariff and asymmetric handoff. Arham Tahir/PR2879 supplies the related
principal-block rank method. Sagar Thakrar/PR2484 names the core; Cinna
Davis/PR1825 supplies the matching; Adam Gall/PR1889 supplies the strict
scalar mask. Retain ctoth, Philippe Van Velzen and the selected geometry's
full-space accounting and source attribution.

[PR3232](https://github.com/CrocSwap/integer-mult-bounds/pull/3232) proves the
all-cycle Gram floor. The complementary
[@petalas PR3248](https://github.com/CrocSwap/integer-mult-bounds/pull/3248),
head `96e3ccd00c62f73d30a23f8d774eea59bfe3b97c`, proves the all-cycle
five-term theorem; this arbitrary-term proof does not assume that result.
[Our canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19003119)
records scope and coordination. Base main is
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.

Prepared by thakrarsagar with substantial OpenAI Codex assistance in proof,
implementation, independent reconstruction, controls and review. Separate AI
executions are not independent human review. Apache-2.0.

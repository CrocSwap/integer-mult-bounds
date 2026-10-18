# Sharp cost 20 for signed Gram decoders on the physical C5s

**Scoped proof with exact finite premises; no new supplier or kappa.** On each
of the 23 induced C5s in PR1825's fixed paired-plane matching, every finite
Gram decomposition of the strict scalar endpoint costs at least **20** under
the inherited complete-plane tariff. Five terms attain 20. Coefficients may
be arbitrary rational, real or complex numbers; no positivity, denominator,
support-size or term-count restriction is needed.

This closes the signed-Gram part of
[PR2782's open question](../c5-dyadic-decoder-gate/README.md#open-next-questions).
That package proved a positive half-integral theorem and excluded a specified
quarter-integral E8 menu. Its signed-half search was inconclusive. Here five
overlapping identity blocks give a lower bound directly, without another
coefficient search. Unequal source/target factors remain outside this theorem.

## Object and tariff

The pinned selected labels lie in `F2^9`. Each matched plane `E_i` has an
ordered basis of two labels with binary Gram matrix `I2`. Order a physical
C5 as `E_0,...,E_4`, with adjacent planes orthogonal and all other distinct
plane pairs nonorthogonal. Each plane has two scalar ports `(i,0),(i,1)`.

A fitting `10 x 10` matrix `K` has diagonal one. Every off-diagonal entry
within one plane, or between nonorthogonal planes, must be zero. Entries
between adjacent orthogonal planes remain free. Consider any finite exact
decomposition

```text
K = sum_t a_t v_t v_t^T,       v_t in F^10,       F = Q, R or C.
```

The transpose is ordinary transpose. Omit zero coefficients and zero vectors.
Let `S_t` be the set of planes with at least one nonzero port in `v_t`.
The term's tariff is

```text
c(S_t) = rank_F2 Gram(all two basis labels of every plane in S_t).
```

Thus touching one port charges its complete two-dimensional plane. This is
the inherited binary-dot tariff, not scalar support size or scalar matrix
rank. The binary form is not alternating: odd tariffs occur. Coefficients do
not alter a term's support tariff.

## Proof

The five nonorthogonal plane pairs are

```text
P = {(0,2), (0,3), (1,3), (1,4), (2,4)}.
```

For each `p in P`, the principal block on its four scalar ports is exactly
`I4`. A rank-one term contributes rank at most one to that block, and zero
if its support misses both planes. If `n_p` counts terms touching `p`, rank
subadditivity therefore gives `n_p >= 4`, regardless of coefficient signs
or cancellations.

For a plane-support mask `S`, put

```text
h(S) = number of pairs p in P with S intersect p nonempty.
```

The finite geometric premise is **`c(S) >= h(S)` for every support mask**.
The verifier reconstructs the physical labels, matching and induced cycles,
then checks all 32 masks for each of the 23 cycles: 736 exact binary-rank
inequalities. It does not infer this premise from the abstract C5 graph.
Summing the inequalities proves

```text
total cost = sum_t c(S_t)
          >= sum_t h(S_t)
           = sum_{p in P} n_p
          >= 5 * 4 = 20.
```

The free orthogonal-plane entries are never constrained in this argument.
It uses five forced identity blocks rather than assuming the entire fitting
matrix is nonsingular.

**Attainment.** For each `i mod 5`, take
`v_i = e_(i,1) + e_(i+1,0)` with coefficient one. These five supports partition
the ten ports. Their only off-diagonal entries join adjacent orthogonal planes,
so the sum fits. Each term touches two orthogonal nondegenerate planes and
costs four. The verifier checks the complete fitted matrix and cost 20 on
every cycle.

## Boundary and evidence

The theorem does not price arbitrary asymmetric terms `u_t v_t^T` by their
Gram tariff. A concrete failure of that extension occurs on PR2484's core
`(13,23,35,16,34)`. Source plane `E_2` against target planes `E_0 + E_4` has
binary pairing matrix

```text
0 0 0 0
1 0 1 0
```

Its rank is one, but this source/target support pair can contribute to two
of the forced blocks, `(0,2)` and `(2,4)`. The analogous termwise tariff
inequality fails. The verifier retains this boundary control; it is not a
complete decoder or evidence of a cost saving.

The result combines a written rank argument with exhaustive checks of its
small finite geometric premises and sharp positive witnesses. It is not a
proof-assistant or formal-kernel verification. It makes no global cost-224
claim for the full paired-plane instance: overlapping local C5 bounds cannot
simply be added. No native word, dirty-state restoration, hosting, precision,
all-size recursion or selected cold-chain replay is supplied.

## Reproduce and sources

From the repository root, using standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/c5-gram-rank-cover
```

[SOURCES.json](SOURCES.json) pins the input bytes and historical provenance;
[VERIFY.json](VERIFY.json) declares the replay. No predecessor code is imported
or changed. The scientific base is `463113d675af7410ac91d53a4fed51ec6494eb9a`,
priority revision 6. [TASK.json](TASK.json) records the scope change from
`coverage-law-change`: test a missing local decoder implication before any
two-unpaid-coordinate supplier expansion. The
[canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19002632)
records the claim and handoff.

Nine controls pass on CPython 3.12.15 and 3.14.4. They independently enumerate
the cycles and compute binary ranks, check every positive witness, and reject
wrong masks, signed undercharging, invalid normalization and changed inputs.
The wrong-mask and signed-tariff mutations are each detected by their intended
control. A separate Codex review reconstructed the finite premises using
chordless walks and dense binary elimination; it is not human review.

## Open next questions

Can asymmetric factors with unequal complete source/target spans lower the
cost on one of these physical cycles? Start with an exact fitting identity
and independently price every full-space pairing, using the displayed
rank-one-versus-two boundary as a diagnostic. The present certificate fails
for that class, but no favorable identity follows from this failure.

Can changed plane geometry or a justified endpoint contract evade the rank
cover? First reconstruct its exact mask and support tariffs; a failed
inequality alone is not a construction. Any favorable local fit still needs
all native payloads, source access, frame changes, dirty restoration, hosting,
precision and compatible supplier costs charged before expansion.

## Credit

Tekalign (`tekuuu`), [PR2782](https://github.com/CrocSwap/integer-mult-bounds/pull/2782),
head `002a9983079a3244c10221b4e16d0cff7e70da40`, supplied the physical C5
instances, complete-plane tariff, positive-half theorem, quarter-E8 census and
signed-half handoff. Arham Tahir's
[PR2879](https://github.com/CrocSwap/integer-mult-bounds/pull/2879) supplies the
related rank-to-tariff method for nonsingular principal blocks. The new step
is the overlapping five-block certificate on these C5s.

Credit Sagar Thakrar's PR2484 for the named C5 core; Cinna Davis's PR1825 for
the matching; Adam Gall's PR1889 for the strict scalar mask; ctoth and Philippe
Van Velzen for the plane-port endpoint and full-space accounting; and the
selected PR1094/E8 geometry contributors retained by the predecessor sources.

Prepared by thakrarsagar with substantial OpenAI Codex assistance in source
inspection, proof development, implementation, controls and review. Apache-2.0.
No independent human or proof-assistant review is claimed.

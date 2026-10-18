# Exact packed-bit repair counts on fixed-source fibers

**Mathematical audit / research note; no new kappa.** The retained eight-rotation
packed-bit gadget has a source-dependent repair density. The complete-rectangle
average in [PR773](https://github.com/CrocSwap/integer-mult-bounds/pull/773) is
not a uniform upper bound after fixing the source. This is a quantified
extension of that audit's stated boundary, not a defect in its theorem or in
the retained manuscript.

Put `B=2^K`, `m=f-1`, and fix the complete source chunk `x`. Let
`c_i=x_(rho+iK)` for `0<=i<m`. If the positions of its `1` bits are
`j_1<...<j_w`, the exact forward disagreement fraction over the **complete
pair of dirty fields** `(y,z)` is

\[
 d(c)=1-\prod_{t=1}^{w-1}\left(1-\frac{2}{B^{j_{t+1}-j_t}}\right).
\]

An empty product is one. This is also the support density of the correction
permutation on that source fiber. The statement holds for all `K>=6`, `f>=1`,
and `0<=rho<K`. It needs no probability assumption on `x`, but does require
complete `y,z` ranges within each source fiber.

At `K=6,f=3`, source `x=65` has two adjacent used `1` bits and density
`1/32`, while the complete-rectangle average is `1/128`. At `K=6,f=4`, the
patterns `110` and `101`, written low bit first, have the same weight but
densities `1/32` and `1/2048`. Neither the average nor the source weight alone
determines the conditional count. PR735 already gives the fixed-source density
of its sufficient no-escape envelope, `1-(1-2/B)^(2w)`. The formula here counts
actual failures, including carries that cross zero-source segments and cancel;
it therefore depends on spacing as well as weight.

## Scope, pins and reproduction

Base: `49b3157d1d89adcef16df8be98445451672be5ba`. The selected record at that
base is conditional kappa `0.001672660197076918`, with complex supplier #1094
and bit supplier #589 on #555. The baseline binding check passed; the complete
selected supplier was not replayed. This package audits the original packed
primitive in `upstream/build/sections/05-layers.tex`, at
`lem:packed-selected-bit-rectangle`, `eq:eight-packed-additions`, and
`eq:packed-cyclic-shift`. It does not change the later compact-control
primitive, the selected supplier surcharge, or the frontier.

[SOURCES.json](SOURCES.json) pins the manuscript, its license, and the retained
full-word simulator with SHA256 and Git blob identities. The upstream source
commit is `adc7f1241b42e322a6451854ab7e4b4c146bf78a`. PR773 is pinned at
`dbd9da3eed9a0045b77de861099e869259f1ad13`; its code is not imported. The new
verifier uses explicit digit assignments and compares them with the unchanged
whole-word simulator. Its gap product is checked against a separate five-state
integer count. This is implementation separation, not independent human review.

From the repository root, using Python 3.10 or newer and the standard library:

```sh
python3 -I -O -B research/packed-source-fibers-seed62/verify.py
```

Expected:

```text
PASS_PACKED_SOURCE_FIBERS digit_cases=873760 full_fiber_states=541200 source_cases=49792 controls=6 no_new_kappa
```

Every evidence field
must equal [EXPECTED.json](EXPECTED.json); a completed process alone is not
acceptance. `--write NEW_PATH` regenerates a receipt and refuses to overwrite.
[VERIFY.json](VERIFY.json) registers the bounded Python 3.12 CI replay. The
stronger package check is `python3 -I -O -B
research/packed-source-fibers-seed62/test_package.py`: it repeats the audit in
a minimal relocated tree and rejects four mathematical mutations, source
drift, an incomplete input inventory, receipt drift, and receipt overwrite.
[TASK.json](TASK.json) and [CLAIM.json](CLAIM.json) record seed **62**, the three
candidate tasks, the scope refinement, finite domain and stopping rule.
The claim is [discussion #1233](https://github.com/CrocSwap/integer-mult-bounds/discussions/1233).

## Conditional transition proof

Write each used `y,z` segment as `u=2g+a`, `v=2h+b`. Reading segments from
low to high is a topological order for the eight gates: a gate reads earlier
gates at that segment and its own carry from the preceding segment. It never
reads a higher segment. Once a low segment differs from the ideal output,
higher segments cannot repair it.

A carry state records the gates crossing a segment boundary. Gate signs and
one-based numbers are those in the pinned manuscript. Matching prefixes have
only these states:

| State | Carry gates |
|---|---|
| 0 | none |
| 5 | 1 and 3, on y |
| 10 | 2 and 4, on z |
| 80 | 5 and 7, on z |
| 160 | 6 and 8, on y |

Here is the conditional transition table, counting choices of `(u,v)` out of
`B^2`. `E` is any one nonzero state; all omitted matching counts are zero.

| Source bit | Incoming | Outgoing | Count |
|---|---|---|---:|
| 0 | 0 | 0 | B^2 |
| 0 | E | 0 | B(B-1) |
| 0 | E | same E | B |
| 1 | 0 | 0 | B(B-2) |
| 1 | 0 | each E | B/2 |
| 1 | E | any matching state | 0 |

For `c=0`, the only changes are the two opposite incoming carries. They
restore the digit. A carry pair survives exactly when `u=0` for state 5,
`v=0` for 10, `v=B-1` for 80, or `u=B-1` for 160. Each boundary has B choices.

For `c=1` and incoming state 0, the scalar identity gives `(u XOR 1,v)`.
Tracing its four parity cases gives the following disjoint outgoing events:

| Outgoing state | Exact boundary event |
|---|---|
| 5 | u=0 and v even |
| 10 | v=0 and u odd |
| 80 | v=B-1 and u odd |
| 160 | u=B-2 and v odd |

Each has B/2 choices. All other inputs leave state 0. To see that these are
uniform statements, run the eight integer assignments from the four parity
pairs `(a,b)`. Every normalized intermediate coordinate lies in `[-2,3]`;
translation by `(2g,2h)` leaves parity tests unchanged. Quotients can therefore
change only at the listed boundary values. Reducing modulo the even B leaves
the parity tests unchanged as well.

For incoming `E` and `c=1`, the final unwrapped error in **z** is always
`+1` or `-1`. In parity order `00,01,10,11`, the signs are `-,+,+,-` for
state 5, and `+,-,-,+` for states 10, 80 and 160. Thus none of these inputs
matches the ideal map modulo B. This rejects target-only reasoning: for
`K=6,f=3,rho=0`, input `(x,y,z)=(65,65,0)` yields `(65,0,262080)` instead of
`(65,0,0)`; the target is right and the dirty temporary is wrong.

This proves closure of the five states by induction from state 0. Every
listed state has signed carry sum zero separately on y and z. In the unused
suffix above the last active segment there are no source increments, so both
suffixes are restored modulo `2^(K-rho)`. Bits below rho never move. The
separately paid highest-bit XOR is the same permutation after both maps and
preserves their agreement set. These facts include `m=0` and `m=1`.

## Product formula and sharp bounds

Let `A,E` denote the probabilities of a matching prefix in state 0 and in
any of the four nonzero states. The table gives

\[
 c=0:\quad (A,E)\mapsto(A+(1-1/B)E,E/B),
 \qquad
 c=1:\quad (A,E)\mapsto((1-2/B)A,2A/B).
\]

Leading zeros do nothing. Immediately after any `1`, conditional on a match,
the proportions are `(1-2/B,2/B)`. If the next `1` is distance d away, its
`d-1` preceding zeros leave nonzero-state mass `2/B^d`. That mass fails at the
next `1`; everything else survives. Trailing zeros preserve total matching
mass. Multiplying these survival factors proves the formula for every source
pattern, without assuming independent or unbiased source bits.

For `m>=2`, the maximum over all sources is

\[
 d_{\max}=1-(1-2/B)^{m-1}\le\min\{1,2(m-1)/B\},
\]

attained by all used source bits equal to one. The maximum is zero for `m<=1`.
For a fixed weight `w>=2`, the maximum is `1-(1-2/B)^(w-1)`, attained by a
contiguous run of ones. For the minimum, write
`m-1=(w-1)a+r`, `0<=r<w-1`. It is

\[
 d_{\min}=1-(1-2/B^a)^{w-1-r}(1-2/B^{a+1})^r.
\]

It is attained by placing the first and last ones at the two endpoints and
making the intervening distances differ by at most one. Each agreement factor
increases with its distance, so an optimum uses the full span. If distances
s,t satisfy `s+1<t`, replacing them by `s+1,t-1` increases their product by
`2(B-1)(B^(-(s+1))-B^(-t))>0`. Repeating this balancing step proves the stated
minimum. For weight zero or one both extrema are zero.

Averaging the conditional table over an unbiased source bit sends `(A,E)` to
`((1-1/B)A+(B-1)E/(2B), A/B+E/(2B))`. After the first bit the vector is
`(1-1/B,1/B)`, an eigenvector with eigenvalue `1-1/(2B)`. Thus the average
failure is `1-(1-1/(2B))^(m-1)` for `m>=1`, recovering PR773. At `m=2` the
worst fixed source has exactly four times that average. For every `m>=2`
the ratio is at most four, by concavity of `1-(1-t)^(m-1)`.

## Repair, accounting and limits

On each fixed-source fiber both the actual map S0 and the ideal T0 are
bijections. If `F_x={p:S0(p)!=T0(p)}`, then the support of
`R_x=T0 S0^-1` is `D_x=S0(F_x)`. Hence the support has the same density d(c),
and R_x permutes D_x. Extracting records at current addresses in D_x,
sorting by their R_x destination, and reinserting fills exactly the extracted
holes. This is the same correction mechanism as PR773, now counted fiberwise.
A forward-disagreement test at a current address is still not that predicate.

For a union of complete y,z fibers, the exact density is the weighted average
of d(c) over its source chunks. The worst-source envelope above is available
when that source distribution is unknown. Arbitrary restrictions on y or z,
or correlations between source and dirty fields, do not meet the hypothesis.

If a caller separately admits such a layout under the retained streaming
contracts, substituting its density delta into the existing repair accounting
retains the entire bill

\[
 O\bigl(V(L^\tau+1)+MA^3+\delta MA(R+A)\bigr),\qquad V=MR.
\]

All eight rotations, field swaps and restores, source reads, inverse masks,
rank/key calculations, full scans, payload copies, radix passes, reinsertion,
highest XOR, rewinds and cleanup remain charged. An irregular source subset
does not automatically inherit the manuscript's complete-rectangle movement
lemma. No new layout compiler or recursive call has been constructed here.
The exponential-in-K repair bound still has the same asymptotic order, so no
new supplier saving or multiplication exponent follows.

## Verification coverage

The deterministic receipt distinguishes a written quantified proof from its
finite corroboration:

- 40 normalized parity cases and every listed state's suffix cancellation.
- 873,760 literal digit cases at K=2 through 8, checking the exact boundary
  events and both conditional transition tables.
- Every source pattern of length 0 through 10 at B=4,8,64,128: gap product,
  independent state counting, complete-rectangle marginal and sharp extrema.
- All y,z values in each of the 15 source fibers at K=2, rho=0, f=1 through 4,
  including every suffix value. These small radices are diagnostic coverage.
- Actual K=6 prefixes realizing all five states, with exhaustive second digits
  and both controls; additional seeded uniform/boundary comparisons at every
  offset for K=6,7,10 and f=1,2,3,4,7,11.
- Complete extraction, sorting and payload reinsertion on the four K=2,f=3
  source fibers, plus six controls for false mathematical shortcuts.

The universal claim rests on the proof above; these finite enumerations are
not a Lean theorem. The selected cold replay, all-size supplier/compiler,
physical hosting, precision/tape and analytic-transfer obligations are outside
this contribution.

## Open next questions

A proposed source-restricted caller could use this count only after showing
that its row splitting preserves complete y,z fibers and admitting its layout
under the paid streaming interface. The first useful step is to name such a
caller and trace one complete invocation, including swaps and correction
access. This package has no proposed caller to discharge that obligation;
[TASK.json](TASK.json) records the precise question and blocker.

## Credit

Prepared by **Hanson Sun (@bbMisk)**, with substantial **OpenAI Codex** assistance
in the derivation, implementation, tests and writing. New work is Apache-2.0.
Credit OpenAI's retained manuscript and the repository's finite-identity
checker for the eight-operation source and simulator; Precious (@Kyu), PR773,
for the five-state matching-prefix method, complete-rectangle density and
support-repair argument; and Aryan Sudhir (@AryanSudhirDev), PR735 at
`8d36139e49add1e55795e283b3bfa45e1cfe1bf0`, for the invariant guard-envelope
audit and distinction between envelope, failure set and source fibers.
The new contribution is the exact source-pattern product, its sharp extrema
and the associated conditional-count audit. No predecessor sources are edited.

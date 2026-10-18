# Exact carry-state count for packed selected-bit repair

**Research audit; no new kappa.** For the eight packed additions in the
retained `lem:packed-selected-bit-rectangle`, the exact fraction of addresses
where the uncorrected map disagrees with the ideal map is

\[
 d_{K,f}=1-\left(1-2^{-(K+1)}\right)^{\max(f-2,0)}.
\]

This is an exact count on the lemma's **complete rectangle**, for every
`K >= 6`, `f >= 1`, and `0 <= rho < K`. It is also the density of the
support of the correction permutation. The written proof below uses a
five-state carry automaton and a finite symbolic partition valid at every
such radix. The executable checks corroborate that proof; they are not a
formal verification of the multiplication theorem.

Concurrent [PR #735](https://github.com/CrocSwap/integer-mult-bounds/pull/735),
by Aryan Sudhir (@AryanSudhirDev), gives the sufficient invariant guard
envelope of density
`1 - (1 - 2^(1-K) + 2^(1-2K))^(f-1)`. Its note explicitly distinguishes
that envelope from the actual failure set. This contribution answers the
latter question using carries that can escape a segment and later cancel.
It also implements extraction, sorting, and reinsertion on the exact
correction support, and exhibits a failure of testing the forward error
predicate at a *current* address. No defect in #735 or the retained proof
is asserted.

For `K=6, f=3`, the exact failure fraction is `1/128`, whereas #735's
sufficient envelope has density `254079/4194304`. For `f=2` there are no
failures at all, despite nonempty sufficient guard envelopes. These are
address counts, not runtime measurements or changes to a supplier exponent.

## Sources, reproducibility, and scope

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The retained OpenAI source is pinned at
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`; the precise anchors in
[`05-layers.tex`](../../upstream/build/sections/05-layers.tex) are
`eq:eight-packed-additions`, `eq:packed-cyclic-shift`, and
`lem:packed-selected-bit-rectangle`. [SOURCE.json](SOURCE.json) pins the
source bytes, license, previous finite checker, selected certificate, and
the concurrent #735 head `8d36139e49add1e55795e283b3bfa45e1cfe1bf0`.
No #735 code is imported or needed for replay.

From the repository root, with Python's standard library:

```sh
python3 -B research/packed-carry-automaton-audit/verify.py
```

Expected:

```text
PASS_PACKED_CARRY_AUTOMATON digit_cases=873760 prior_simulator_cases=40960 repair_states=114752 source_domain_samples=116736 negative_controls=8
```

The command checks source hashes and compares all generated evidence with
[RESULT.json](RESULT.json). `--write PATH` regenerates only that receipt.
The deterministic domain, assignment seed **70**, stopping rule, initial
candidate tasks, and the evidence-driven pivot after finding #735 are in
[CLAIM.json](CLAIM.json).

The selected #626/#543 conditional kappa remains
`51110230636731/31250000000000000`. This audits the original packed
primitive, not the different compact-control primitive or the selected
supplier's surcharge. All-size supplier compilation, physical hosting,
precision, tape implementation, and analytic transfer remain inherited
obligations. The exact address-map theorem below does not discharge them.

## 1. Carries at a segment boundary

Write `B=2^K`, `m=f-1`. The lowest `rho` bits of each chunk are fixed.
Above them lie `m` radix-`B` segments and a suffix of `K-rho` bits. The
top selected XOR is the separate operation already present in the source.
Let `S0` be the eight packed rotations and `T0` the XORs in the `m` used
segments only. The source chunk `x` is unchanged.

For one segment let `c` be its source bit, and `u,w` its initial `y,z`
digits. At gate `t`, the incoming carry is either zero or the sign of that
gate. Encode its presence by bit `t-1` of an eight-bit state `s`. The
local update is

\[
 v_{\rm target}\leftarrow
 v_{\rm target}+\epsilon_t
 \bigl(c[v_{\rm other}\bmod2=p_t]+s_{t-1}\bigr).
\]

Reduce the target modulo `B` and pass its signed quotient to the next
segment at the same gate. The gate targets, signs, and parity tests are
the eight literal source operations. An increment has the gate's sign
and magnitude at most two, so its outgoing carry again has presence bit
zero or one.

Processing whole segments from low to high is a valid topological order:
each gate depends only on earlier gates in that segment and the same gate
in the preceding segment. There is no dependency from a higher segment
back to a lower one. A final mismatch in a low segment cannot be repaired
by a higher segment, so count only prefixes that already match `T0`.

Exactly five states are reachable on these matching prefixes:

| State | Carry gates (one-based) | Interpretation |
| --- | --- | --- |
| `0` | none | No boundary crossings |
| `5` | 1, 3 | A negative and a positive `y` carry |
| `10` | 2, 4 | A negative and a positive `z` carry |
| `80` | 5, 7 | A positive and a negative `z` carry |
| `160` | 6, 8 | A positive and a negative `y` carry |

This is a statement about **matching** prefixes; other executions may
have other carry states. Every listed state's signed carries sum to zero
on each target. In the final suffix there are no selected-bit increments,
so these incoming carries restore both suffixes, modulo `2^(K-rho)`, for
every suffix value. Thus acceptance does not depend on `rho` or on suffix
bits. The separate highest XOR also preserves the agreement/failure count.

## 2. Exact transition table, uniformly in B

The alphabet of one segment is `(c,u,w)`, of size `2B^2`. Counting only
transitions whose final digits are `(u XOR c,w)` gives this matrix. `E`
denotes any of the four nonzero states; different `E` states do not
transition to each other along matching prefixes.

| Incoming | Outgoing | Multiplicity |
| --- | --- | ---: |
| `0` | `0` | `2B(B-1)` |
| `0` | each `E` | `B/2` |
| `E` | `0` | `B(B-1)` |
| `E` | the same `E` | `B` |

Here is a complete way to establish this table without inferring a
polynomial from numerical radices. Put `N=B/2` and write
`u=2g+a`, `w=2h+b`. For each of the five incoming states and eight Boolean
triples `(c,a,b)`, execute the unwrapped integer updates from `(a,b)`.
All intermediate normalized coordinates lie in `[-2,3]`. Reducing modulo
the even `B` never changes a parity predicate, so adding `(2g,2h)` gives
the unwrapped trajectory for every pair of guards.

Partition each guard into the three classes `0`, `[1,N-2]`, and `N-1`.
Their multiplicities are `1`, `N-2`, and `1`. For a normalized coordinate
`v` in `[-2,3]`, its quotient after adding the guard translation is:

| Guard class | Quotient on division by B |
| --- | --- |
| `0` | `-1` if `v<0`, otherwise `0` |
| `[1,N-2]` | `0` |
| `N-1` | `1` if `v>=2`, otherwise `0` |

For the middle class, `0 <= 2g+v <= B-1`; the other two rows follow
directly from `-2 <= v <= 3` and `B>=64`. Subtracting the preceding
quotient at each gate gives its outgoing carry. The terminal normalized
coordinates match exactly when they equal `(a XOR c,b)`: their difference
has absolute value less than `B`, so a nonzero difference cannot vanish
modulo `B`.

Sum the nine guard-class products for each of the 40 parity cases.
The resulting polynomials, in increasing powers of `N`, are respectively
`[0,-4,8]`, `[0,1,0]`, `[0,-2,4]`, and `[0,2,0]`, giving the table above.
The verifier performs this symbolic partition and checks closure of the
five states. A separate `divmod` implementation exhausts literal digits
at `K=2,...,8` and obtains the same matrices. The small radices are extra
diagnostics; the written theorem retains the source domain `K>=6`.

## 3. Closed-form disagreement count

Before any segment the only state is `0`. After the first segment the
state-count vector is

\[
 v_1=(2B(B-1),\ B/2,\ B/2,\ B/2,\ B/2).
\]

Its sum is `2B^2`, so every one-segment input agrees. Direct multiplication
by the table shows `v_1 M = B(2B-1) v_1`. Consequently the number of
matching alphabet words of length `m>=1` is

\[
 2B^2\,[B(2B-1)]^{m-1}.
\]

Divide by `(2B^2)^m` to obtain agreement fraction
`(1-1/(2B))^(m-1)`. For `m=0`, both maps are identities. This proves the
displayed formula for every `f>=1`.

The complete rectangle makes all segment controls and digits independent
and uniform. Unused `x` bits, low bits, suffixes, rows, spectators, and
payloads multiply numerator and denominator equally. The fraction is
**not** a bound for each fixed `x` fiber; for example `x=0` never fails.
Grouped rectangles with the same `K,f,rho` have the same fraction within
each complete group. No distributional claim is made for incomplete boxes.

## 4. Repair the support at current addresses

Let `F={p : S0(p) != T0(p)}` be the forward disagreement set, and let
`R=T0 S0^-1`. Its support is

\[
 D=\{q:R(q)\ne q\}=S0(F).
\]

Thus `|D|=|F|`. Since `R` is a permutation, its fixed-point complement
`D` is invariant under `R`. Compute `q'=R(q)` at **every current address**;
extract a record exactly when `q'!=q`, attach `rank(q')`, and mark its
hole. The destination keys are distinct and are exactly the marked holes.
Sorting and reinserting therefore realizes `R`, with exactly density
`d_{K,f}` in the extracted bank.

Testing `q in F` in that scan is incorrect. At `K=6,f=3,rho=0`, take
`q=(x,y,z)=(65,0,127)`. Then

```text
S0(q) = T0(q) = (65,65,127),
S0^-1(q)       = (65,65,191),
R(q)          = (65, 0,191) != q.
```

So a forward-error test at `q` would skip a necessary correction. It
also passes the naive test that its isolated forward segments never
escape. The seed-selected translation `rho=4` gives the same counterexample
with all three chunk values multiplied by 16. These are valid source
parameters, not counterexamples to its invariant-envelope repair.

## 5. Complete inherited cost and evidence

The membership test computes the same eight inverse rotations and direct
XOR already used by the original correction routine, now for every record.
The source already charges `O(A^3)` per full-scan record for rank decoding,
descriptor work, and arithmetic. Its argument bounds this inverse/XOR
calculation by `O(A^3)` too, so the full scan remains `O(M A^3)`.
This may increase its constant. With `V=MR`, the complete inherited bill is

\[
 O\bigl(V(L^\tau+1)+MA^3+d_{K,f}\,MA(R+A)\bigr).
\]

All eight forward rotations, their field swaps and restores, every
source read, rank/key computation, extraction, radix pass, reinsertion,
top XOR, rewind, and cleanup retain their source charges. There are no
new recursive children or clean helper assumptions. The finite program
models permutations and payload movement, not a fixed-tape machine, so
this is a substitution into the inherited accounting, not a new machine
implementation or a measured speedup. Since the original repair term was
already negligible in its asymptotic regime, no new kappa follows.

The deterministic receipt covers:

- 40 symbolic parity cases with exact guard-class polynomial weights;
- 873,760 literal digit transitions, including every state in the claimed
  matching-prefix automaton at `K=2,...,8`;
- exact recurrence checks through 64 segments at `K=6,7,10`;
- 40,960 comparisons with the unchanged, source-pinned repository simulator
  at `K=6,rho=4`, exhausting the next segment after witnesses of all five
  incoming states;
- 114,752 exhaustive small-radix whole-word states with distinct payloads,
  inverse checks, extraction, sorted keys, and reinsertion;
- 116,736 full-source-domain inputs at every offset for the declared
  `(K,f)` pairs, half uniform and half boundary-heavy, compared with a
  separate signed digit/carry implementation;
- eight controls: two current-address/forward-error confusions, four
  forbidden no-crossing endpoints, one primitive sign corruption, and
  omission of the separately required top XOR.

The exhaustive payload census uses fixed-`x` fibers ordered by
`rank=y*2^L+z`. Arbitrary spectator layouts are covered by the written
permutation argument, not by an exhaustive census of all layouts.

No finite replay is presented as a formal proof of the universal claim.
The proof's coverage comes from the parity/guard partition and the matrix
recurrence; sampled inputs test the independent implementation and boundary
plumbing. The checker uses explicit failures and also runs under `python -O`.

## Attribution

Prepared by Precious Oyetunji (@Kyu), with substantial OpenAI Codex assistance in
the derivation, implementation, verification, and writing. New material is
Apache-2.0. Credit OpenAI for the retained manuscript and gadget, Douglas
Colkitt for the existing dependency and finite-identity audits, and Aryan
Sudhir for concurrent #735's guard-envelope result, which prompted the
scoped pivot to exact carry-state counting. The historical packed-movement
and short-guard work remains credited to its existing authors. No priority
is claimed for the independently rediscovered guard envelope, and no human
peer review or proof-assistant verification is claimed here.

# Independent signed delivery review

Prepared with OpenAI Codex assistance. This review concerns the assigned signed
characteristic-zero extension of Adam Gall's PR #2060 correlated-source delivery
mechanism. The parent's source/provenance review owns the precise predecessor
pin. No predecessor implementation or primary-package implementation is imported
by `independent.py`.

The proposed query bill is correct in the stated fixed-word grammar. This is an
all-parameter written proof and a separate finite exact search, not a formal
kernel proof, general circuit lower bound, physical-machine optimum, recursive
caller admission, or new exponent-saving result.

## Model and written derivation

Let `k,d >= 1`, and let every row `M_i` of `M in Q^(k x d)` be nonzero. Independent
arbitrary vector inputs `v_j` determine the externally imposed current source
`x_i = sum_j M_ij v_j`. A single arbitrary dirty connector `z` and pairwise
distinct dirty outputs `y_i` are reserved. The fixed word must work uniformly
over arbitrary compatible exact linear maps `B,A_i` over Q or C. During epoch i,
only `B_i^s: z += s B x_i` and `A_i^s: y_i += s A_i z`, for `s in {-1,+1}`, are
allowed. The output is delivered before the next epoch; source mutations are
outside this grammar and fully paid. No source correction queries, observations
of z, feedback, aliases, rounding, or other data operations are allowed. The
connector must be restored at the end.

Prices `a_i,b_i > 0` are complete, sign-symmetric and state-independent. They
include each macro's source/coefficient access, preservation, update, cleanup,
actual volume, routing, frame adapters and head return. Any imposed source-path
cost and additional lifetime costs must be added separately and consistently.

At any prefix, write

```
z = z0 + B sum_j q_j v_j,
y_i = yi0 + alpha_i A_i z0 + A_i B sum_j r_ij v_j.
```

These coefficients fully describe the grammar even for nonscalar maps: every
source query adds a scalar multiple of one `B v_j`, and every output query
applies the same `A_i` to the connector. No higher ordered factor word occurs.
Taking scalar identity maps and independent scalar inputs proves the necessary
conditions `alpha_i=0`, `r_i=M_i` at delivery, and `q=0` at the end.

Every reader has sign +/-1. Cancelling the independent `A_i z0` coefficient
requires equal positive and negative reader counts. Zero readers cannot produce
the nonzero target row. Thus each epoch needs at least two readers. If there is
no source query during that epoch, q is constant, so `r_i=alpha_i q=0`, again
contradicting `M_i != 0`. Every epoch therefore has at least one source query.

Let `t_i` be its signed source count, and `n_i` its unsigned source count.
Always `n_i >= abs(t_i)` and `n_i` has the parity of `t_i`. In particular, for
`t_i=0`, positive `n_i` is at least two. Therefore

```
n_i >= phi(t_i),    phi(0)=2,    phi(t)=abs(t) for t != 0.
```

Terminal restoration imposes `sum_i t_i M_i=0`, equivalently `M^T t=0`. Adding
the necessary complete prices gives

```
Q >= 2 sum_i a_i + min_{t in Z^k, M^T t=0} sum_i b_i phi(t_i).
```

This lower bound applies to all multiplicities and interleavings in the grammar.
It does not assume paired source calls or that outputs use exactly two readers.

Conversely, fix any integer kernel vector t. For nonzero `t_i`, set
`s=sign(t_i)` and execute

```
A_i^(-s), B_i^s, A_i^s, then abs(t_i)-1 additional B_i^s.
```

The two readers contribute
`-s A_i z_before + s A_i(z_before+s B x_i) = A_i B x_i`, including cancellation
of all connector dirt and prior source history. The remaining source queries
are outside that readout pair and change no output. For `t_i=0`, execute
`A_i^-, B_i^+, A_i^+, B_i^-`. Thus each output is correct at its own delivery cut,
the source net is `t_i`, and source count is exactly `phi(t_i)`. The kernel
equation restores the connector. Every candidate in the minimization is
attainable, establishing equality.

The minimum exists for arbitrary fixed positive real prices: t=0 gives a finite
closed-echo bound, and any contender has bounded `abs(t_i)` for every coordinate.
The implementation tests rational prices exactly.

This theorem concerns one universal word. Specialized maps such as `A_i B=0`
can admit cheaper words and are not covered by its optimality assertion.

## Three-epoch mechanism

For rows `(1,0),(1,1),(1,2)`, the integer kernel is exactly
`t=q(1,-2,1)`, `q in Z`. The source bill is

```
min(2(b1+b2+b3), b1+2b2+b3) = b1+2b2+b3.
```

Indeed the nonzero branches have price `abs(q)(b1+2b2+b3)`, minimized at
`abs(q)=1`. The improvement over closed source echoes is always `b1+b3>0`.
The middle epoch retains two same-sign source calls. With unit macro prices,
the whole word costs ten queries: six readers and four sources, versus twelve.

Modulo two the first and third rows coincide, and `(1,0,1)` is a parity kernel
vector. Its characteristic-zero residual is `(2,2)`, so importing that binary
kernel would fail restoration. The signed word uses `(1,-2,1)` or its negative.

## Finite independent search

Reproduce with:

```
python3 -I -B research/signed-dependent-delivery/independent.py
python3 -I -O -B research/signed-dependent-delivery/independent.py
```

The Dijkstra state is `(epoch,q,alpha,r)`, representing the complete exact
connector source coefficients, current output dirt coefficient and current
output product coefficients. All four signed query edges are present. A
zero-price delivery edge exists only when `alpha=0,r=M_i`; old outputs cannot be
written again. The last delivery also requires `q=0`. Rational source rows use
one common denominator, with no reduction modulo a characteristic.

The closed-echo price bounds the search. Pruning uses only the necessary
two-reader/one-source cost of untouched future epochs and the readers required
to cancel the current alpha. Dijkstra's first accepted terminal state therefore
excludes every cheaper allowed word. It does not assume the proposed integer
kernel formula; that formula is compared afterward against independent finite
integer enumeration within the closed bound.

Exactly 130 cases pass:

* 117 cases comprise every ordered `k=1,2,3` tuple of rows `(1,s_i)` with
  `s_i in {0,1,2}`, crossed with three tariff families. Their reader/source
  sequences, truncated to k entries, are `(1,1,1)/(1,1,1)`,
  `(1,2,1)/(2,1,3)` and `(3/2,1,5/4)/(1/2,3/2,1)`.
* Ten named cases test one source, repeated/opposite/scaled sources, independent
  rows, a triangular dependence, the progression, a rational source scale,
  asymmetric middle source price and asymmetric reader prices.
* Three further rational matrices are the progression scaled uniformly by 1/2;
  rows `(1/2,0),(1,1),(1/2,1)`; and rows
  `(1/2,1/3),(1/2,2/3),(1/2,1)`. Their unit-price optima are 10, 9 and 10.

The run popped 182,597 states and generated 233,663 states in total, with at most
5,623 states for one case. The observed runtime was about 1.3 seconds. The
deterministic all-case result-record SHA256 is
`27f83bf984de0becd074564e93ce96b6e8a454a8bfe9d57ddc173514b174d5f3`.
These are explicitly enumerated finite instances, not a census of all rational
matrices or tariffs. Repeated matrices from different named cases remain
separate cases in these counts.

Both ordinary and optimized isolated replays execute all 130 comparisons and
five defect controls. Verification uses explicit `require` calls raising
exceptions; there are no Python `Assert` syntax nodes, so `-O` does not remove
the behavioral checks. Separate optimized harness injections forced the
inverse checker to return false and the literal-map checker to accept every
word: the run rejected them at `one inverse mismatch` and
`binary-only kernel defect survived`, respectively. Earlier optimized execution
of the assertion-based version did not establish those removed checks and is
superseded by these replays. The ordinary and optimized corrected runs have the
same deterministic case-record hash above; each took about 1.5 seconds.

For every case the checker propagates the attaining word on a full exact
coefficient basis and verifies its target and delivery cuts. It also checks
word followed by its reversed sign-negated inverse, including arbitrary
connector/output dirt. The inverse check assumes the same source values are
available in reverse order. It does not grant a reverse word permission under
an imposed forward-only source schedule. In the parent's physical pilot, the
entire inverse must also reverse the literal imposed source updates.

Five controls must fail: the false binary kernel, an omitted reader, a reversed
source sign, inversion of the second same-sign middle source call, and delaying
an earlier output reader beyond its delivery cut. The last control deliberately
has the correct final map; the strict delivery checker rejects it.

## Primary source review and remaining obligations

After completing the independent engine, the reviewer read the parent's
`model.py` without importing it. Its column-denominator scaling preserves the
integer kernel; its finite DP reserves a valid lower bound for future source
cost; its epoch construction agrees with the algebra above; and the pilot's
literal source updates and terminal source restoration implement the intended
progression. No material mathematical defect was found in those reviewed
components. The invoice is for its explicit fixed scalar-cell/ADD movement
model; it does not prove a finite-tape implementation or an all-size recursive
cost bound. The direct compiled comparator appropriately prevents a claim of
global optimality after opening the macro alphabet.

The reviewed `model.py` SHA256 was
`deae83903a6a0dcee6dc20f934f3646554714d47b174ecdbfd3b7208d5e04207`.
Changes to its mathematics or invoice after that review require an affected
review refresh. The tested `independent.py` SHA256 was
`6fb601a714b681b7e7d1f1109890ffdf47506d77dc7ffc600a09b2ed0f34fe76`.

The reviewer also read `PROOF.md`, `README.md` and `verify.py`. Their all-word
proof, complete-price comparison and finite-evidence scope agree with the
derivation here. The primary optimized verifier executed successfully, checking
117 optimizer cases, 81 endpoint coefficients per pilot, 19,683 dirty grid states
and 68 rejecting controls. Its primary checks use explicit exceptions.

As a separate source-level check, the reviewer propagated the primitive pilot
words with an independent 9-by-9 integer matrix loop. The forward maximum
row-L1 values are candidate/closed/direct = 9/8/7, and the reversed sign-negated
words give 8/9/7. Under one common coordinate magnitude bound, the forward
candidate requires four conservative extra magnitude bits versus the closed
word's three. A caller that reserves common capacity for both full directions
already needs maximum 9 for either program, so this does not prove a universal
noncommon precision increase. The current source invoice and accompanying
text disclose this direction-specific boundary. No physical or all-size gain
follows from the smaller scalar ADD invoice.

Before promoting this mechanism to a recursive saving, a caller must admit the
correlated source path at every required size and cut, pay its actual updates
and return, and provide exact additive sign-symmetric complete child interfaces.
It must pay connector reservation, source access, coefficient preparation,
dispatch, routing, frames, precision/range growth and cleanup. Arbitrary source
row dependencies alone do not provide such a caller. The finite optimizer is a
mathematical optimizer, with no efficient uniform-controller claim. The parent's
construction/cost proof owns these remaining admission and full-cost obligations.

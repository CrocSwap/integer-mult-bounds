# Actual producer admission for the first P104 collector

This note answers the producer question left by PR #3382. The actual source
path can supply its numerical entrance under an explicit stronger initial
contract. Admission from arbitrary initial lattice states is false: a single
initial coordinate gives a source-bound counterexample, even though all
arithmetic on that execution remains exact before the collector.

The result is a conditional producer theorem and one reachable counterexample.
It does not admit a complete P104 supplier, classify all possible final-cut
cancellations, or supply physical access to the numerical banks.

## 1. Exact source and dependency boundary

The word and native recipes are ywz65's PR #2586, head
`7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`, retained in
`research/p104-rounded-collector/inputs/WORD.json` and `NATIVE.json.gz`.
Their SHA256 digests are respectively
`cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50` and
`ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d`.
The referenced Gaussian model is the byte-identical PR #3382 `model.py`,
SHA256 `74c83367887dd885137b222155c86389fe0be9f1293a6f0e5fdb51d71f435fdd`.
This package retains it as [`inputs/pr3382_model.py`](inputs/pr3382_model.py),
alongside its credited [`inputs/PR3382_PROOF.md`](inputs/PR3382_PROOF.md).
The consolidated source manifest is `SOURCES.json`; source bytes are
authenticated before the model is executed. The word and native inputs
remain at their original repository paths in both the checkout and the
portable source export.

The collector starts at zero-based event 2025. An ADD record is
`["add", destination, source, coefficient, frame]`. This direction matters:
the appearances of Q7 at events 492–543 are reads into X targets, not writes
to Q7. Backward dataflow from D31, D30, D29, D28, D27 and Q7 produces exactly
257 events and 58 initial dependencies:

- The five initial D banks and initial Q7.
- Y22 through Y32 and Y63 through Y103: 52 initial Y banks.

All 58 start at frame `[]`. The slice contains 200 actual native transports,
of total native rank 354, and 57 ADDs: 52 positive quarter-source ADDs and
five unit subtractions into Q7. There is no X, G or N dependency in these
six numerical outputs.

| Produced bank | Quarter source count | First quarter event | Last write before the cut |
|---|---:|---:|---:|
| D31 | 3 | 1090 | 1233 |
| D30 | 7 | 1093 | 1395 |
| D29 | 7 | 1177 | 1461 |
| D28 | 11 | 1087 | 1643 |
| D27 | 24 | 1157 | 1831 |
| Q7 | 0 | — | 972 |

Every one of the 52 Y banks is used exactly once by these five D targets.
Each Y bank changes only by native transports before its required read.
The complete event lists and source names are derived from the frozen word
and retained in the receipt.

Q7 subtracts the five *initial* D values at 908, 910, 912, 914 and 916.
Each D bank's own initial transport follows its subtraction. Hence, writing
`q` and `d_j` for initial values, its cut value is exactly the event-972 map
applied to `q-sum(d_j)` whenever the stated admission condition holds.

The five D outputs reach frame `[256,136,64,40,16,4,2,1]`, and Q7 reaches
`[364]`. Frame checks establish the specified program boundary. They do not
construct physical ownership or read permissions. The initial D and Q banks
are mutable dirty inputs. The Y banks are also numerically transported; they
cannot be charged as immutable borrowed raw arrays without a separate copy
or representation contract.

Only the six target outputs of a minimal backward slice are actual cut
states. A sliced auxiliary Y bank stops at its last required read, even if
the original word transports it later. A downstream execution must use the
actual initial-to-cut Y transport, not that historical read state.

## 2. The exact conditional theorem

Put `pi=1+i` and use PR #3382's Gaussian Newton lattice

\[
 \mathcal B_9=\left\{f(x)=\sum_S a_Sx^S:
                      \pi^{|S|}\mid a_S\right\}.
\]

The earlier proof establishes that every actual affine/quadratic Gaussian
wrapper and every coordinate butterfly is a linear automorphism of this
lattice. The literal signed-floor butterfly equals the ideal one on it,
including negative integers. Thus each full literal native transport
restricts to an automorphism of `B9`, and of `4B9`.

**Producer theorem.** Assume the 58 initial numerical banks belong to
`2^-f B9`, and the 52 listed Y banks belong to the stronger module
`2^-f 4B9`. Keep their distinct program roles and declared frames. Then every
relevant native stage and ADD is exact on the retained grid, every tracked
bank remains in `2^-f B9`, and all six produced collector inputs meet
PR #3382's numerical entrance contract.

The initial D and Q values are arbitrary within the stated module; they
need not be zero, small, independent, or uncorrelated. To prove the theorem,
observe that each Y path preserves `4B9`, so its quarter is in `B9` at its
actual read. An ADD of two lattice elements stays in the lattice. All
native transports preserve it, and Q7's five initial subtractions preserve
it. Induction through the extracted source order proves the claim.

There is a sharp converse for this *prefix* invariant. Under the weaker
assumption that all 58 initial banks are in `B9`, every tracked complete
native stage and event remains in `B9` if and only if all 52 initial Y banks
are in `4B9`. A complete native stage here means a complete wrapper or all
disjoint butterflies on one coordinate. A physical permutation cycle's
intermediate partially rearranged array is not asserted to lie in `B9`;
its operations use Gaussian integers and contain no division.
For necessity, take any quarter event. Its destination before and after the
event is in `B9`, so their difference, the quarter source, must be in `B9`.
Its source is therefore in `4B9` at that read. The source's preceding native
path is an automorphism of both modules, so its initial value was in `4B9`.
Every listed Y is read, proving the necessity of all 52 conditions.

The 52 stronger source conditions are therefore sufficient for the six
final-cut inputs and necessary for the stated prefix invariant. They are
not asserted necessary for admission at only the final cut. Outside-lattice
contributions can cancel after earlier bad prefixes.
Neither such a cancellation domain nor arbitrary rounded executions are
classified here. The quarter operation in this theorem is the exact scalar
ADD appearing in the word; a componentwise rounded quarter is a different
operation and has not been substituted.

The encoder makes the positive contract constructive as a numerical
representation: initial D and Q may be `E9*c`, and initial Y may be
`4*E9*c`, for arbitrary Gaussian coefficient arrays. All conversion,
preservation and eventual inverse-conversion costs remain part of the
caller's bill. In particular the old six-field local codec does not prepare
these 52 stronger Y sources for free.

## 3. One-coordinate actual-source counterexample

Set the original persistent input `Y27[0]=64`, and set every other initial
component of all 358 persistent banks to zero. This is one explicit input
choice, not a zero assumption about general dirty state. Its initial Y27 is
`64*delta_0`. Every Newton coefficient of that impulse is `+64` or `-64`.
Since `v_pi(64)=12` and every degree is at most nine, all initial banks lie
in `B9`. But Y27 is not in `4B9`: the degree-nine condition would require
valuation at least thirteen.

The actual Y27 producer transports are events 131 and 1056, of ranks one
and two. Event 1090 adds one quarter of their output into D31. For this
fixture the division is componentwise integral, and every literal native
pair in the producer cone agrees exactly with its ideal pair. Nevertheless
the first lattice failure **in the 257-event producer cone** occurs at 1090:

\[
 S=349\quad(|S|=6),\qquad a_S=-4-4i,\qquad
 v_\pi(a_S)=5<6.
\]

D31 subsequently receives zero from Y26 and Y99 and executes the actual
transports 1092, 1131 and 1233. At the collector entrance its output has
256 nonzero entries, each a Gaussian unit. A two-address witness suffices:

\[
 D31[8]-D31[0]=-1.
\]

This is its degree-one Newton coefficient at address bit three. It is not
divisible by `1+i`, so D31 fails the entrance condition. The other four D
inputs and Q7 are zero and satisfy it.

There are two useful conceptual checks on this failure. First, an exact
native transport is an automorphism of `B9`; applying its inverse to an
admitted output would give an admitted input. Second, the unrestricted
literal signed-floor pair is a bijection, with the credited negative pair
as its inverse, and both restrict to lattice automorphisms. Consequently
even an outside-lattice *literal* native cannot move a state into `B9`.
The latter argument does not assume that unrestricted floors are linear.
For this particular fixture, the stronger direct literal/ideal comparison
also passes at every producer pair.

Multiplying the input amplitude by four, to `Y27[0]=256`, gives a positive
control. It starts in `4B9`; the whole producer cone remains admitted, and
its D31 cut output is four times the negative fixture's output. Amplitude
64 is a simple constructive witness, not a claimed minimum over all inputs.

## 4. Why this witness can reach the cut

A counterexample at a chosen read would not by itself show that the earlier
word can supply that read on the retained grid. Here a small Gaussian
valuation certificate establishes reachability for the explicit initial
point through events 0–2024.

If every component is divisible by `pi^k`, a Gaussian monomial wrapper
preserves this property. Each coordinate butterfly has coefficients equal
to Gaussian units divided by `pi`, so it loses at most one power. If the
available lower bound is at least the native rank, every ideal stage stays
Gaussian integral, and the literal floor implementation agrees with it at
each stage. A quarter coefficient loses four powers. Exact zero banks have
an infinite bound until a nonzero source is added; for additions take the
minimum of the two source bounds. This is a conservative valuation argument,
so cancellation can only improve it.

Starting from valuation twelve in Y27, exactly 20 native occurrences and
six quarter-source events are active before the cut. The latter are:

| Event | Destination | Y27 cumulative native rank | Valuation lower bound after quarter |
|---|---|---:|---:|
| 1090 | D31 | 3 | 5 |
| 1190 | D10 | 4 | 4 |
| 1303 | D20 | 5 | 3 |
| 1499 | D24 | 6 | 2 |
| 1763 | D1 | 7 | 1 |
| 1937 | D16 | 8 | 0 |

Each listed D branch spends at most that remaining valuation in its later
native stages and ends with a nonnegative lower bound. Y27's final native
stage leaves bound three. Every fractional source in the full prefix is
therefore exactly representable on this one execution; all other source
banks remain zero. The certificate binds all 20 active native occurrences
to their archived frames, ranks and actual wrapper alphabet, and checks
the coefficients and unit signs of the entire prefix.

This valuation certificate proves exact arithmetic and existence of this
one prefix execution. It does not by itself prove lattice membership at
the outside-cone events or a universal full-prefix admission theorem.

There is also a separate direct replay in [`independent.py`](independent.py).
It imports neither the producer or consumer checker nor the PR #3382 model.
Starting from all 358 original persistent banks, it executes every event
from 0 through 2024, authenticates all 883 native occurrences in that prefix,
and tracks the actual states and frames. Exact-zero native inputs remain
zero; the 20 active native occurrences require 6,144 independent literal
signed-floor versus ideal pair comparisons. All six active quarter ADDs
are checked componentwise integral, and every initial bank is independently
checked for Newton membership.

This replay passes and agrees with the producer on all six collector-input
frames and array hashes. In particular its D31 output is
`adde9450101abb38b9f2c225459b1068526a1fc6dede4957615e2b0ef5ed8a21`,
with the same degree-one failure at mask 8. Its earliest failure in the
**full 2,025-event prefix** is also event 1090, D31, coefficient `-4-4i`
at mask 349. Thus the stronger full-prefix location is established by this
separate replay; it is not inferred from the smaller producer slice.

The negative example is consequently reachable on the retained exact grid
from explicit admitted initial lattice states. This remains a one-point
result. It does not claim general membership throughout the full prefix,
execute the later events of the 5,398-event word, or establish a physical
implementation.

## 5. Reproduction, controls and limits

`producer.py` exposes
`verify_producer(word_path, native_path, model_path) -> deterministic JSON`.
It uses standard-library Python and the authenticated PR #3382 model; no
native compiler, Git, network, large search or predecessor test suite is
needed. From the repository root, or the same root in the portable source
export, run the package's dedicated verifier:

```sh
python3 -B research/p104-newton-interfaces/verify.py
```

The same obligations can be checked with assertions disabled:

```sh
python3 -O -B research/p104-newton-interfaces/verify.py
```

`VERIFY.json` records the package replay contract and `RECEIPT.json` records
the consolidated execution, source bindings, environment and controls.
This is a dedicated package workflow; it does not require registration in
the repository's shared verification suite. The caller supplies the exact
vendored model path to the producer API. `independent.py` supplies its separate
full-prefix and symbolic-port evidence to the same consolidated verifier.

The verifier extracts and checks the exact source order, frames and native
recipes. It compares 90,624 literal/ideal pair obligations per fixture:
one dense signed fixture with arbitrary dirty initial D/Q banks, the
one-coordinate counterexample, and the amplitude-256 positive control.
On admitted fixtures it also checks every native stage and event's lattice
membership. Written invariance and necessity arguments establish the
universal conditional theorem; those finite cases do not replace it.

Small controls reject corrupt source bytes, a changed quarter coefficient,
an omitted Y27 source, and swapped chronological source reads. Signed
exact quarters are accepted, while a negative nonintegral quarter is
rejected explicitly. All checks use exceptions and remain active with
Python optimization. The frozen all-rank model's original broad tests are
not repeated by this follow-up.

The producer's three-fixture replay passes in both ordinary and optimized
CPython 3.12.14, producing byte-identical proof-relevant child receipts. Each
mode checks 271,872 pair obligations in total. The independent full-prefix
replay supplies a different source-wide reachability check for the one
counterexample, while the universal conditional theorem relies on the
written invariant and its inherited all-rank lattice proof.

The substantive answer is that a real source path is now bound, but its
admission is a stronger input contract rather than a property of arbitrary
lattice inputs. A complete caller must supply the 52 `4B9` states with their
actual source access and prices, and a downstream consumer must preserve
the requested logical map. The actual downstream contract is developed in
[`CONSUMER.md`](CONSUMER.md), and the complete retained interface bill and
conditional outer stop test are in [`COMPARISON.md`](COMPARISON.md).
Any full physical or recursive improvement must include those obligations
and the literal restoration bill.

Prepared by Clear1nsight with substantial OpenAI assistance. Credit remains
with ywz65 and the P104 native lineage, Arham Tahir's retained rounded
collector archive, Tekalign's PR #3025 signed-floor bijection,
Ross Richardson's PR #3068 exactness-domain question, and
PR #3382's Gaussian Newton/Clifford proof and model. The new claims are the
actual producer binding, its quantified stronger entrance condition, and
the reachable one-coordinate counterexample. Apache-2.0.

# A sharp information bound for the 326 → 531 → 1 relay

## Result and scope

For the specific modified incidence schedule below, no causal binary-scalar
protocol can reproduce the native 630-output map on more than half of the
constant binary inputs. This remains true when every retained payload and
decoder is changed, when intermediate results are retained without limit,
and when the three chart-531 exports are completely recoded. An explicit
modified native word is correct on exactly half the inputs. Its exact domain
is a 629-dimensional hyperplane, so the bound is attained.

For `k ≥ 1` independent copies, permit fully joint causal coding among the
`k` bits in each corresponding transfer slot. If there are also `m ≥ 0`
additional input-dependent one-bit transmissions at fixed, input-independent
times, the exact best success probability under the uniform input distribution
is

```
2^(-max(0, k - m)).
```

The upper bound allows each side transmission to go to an arbitrary chart.
The matching construction grants up to one **specified residual bit as an
oracle** to chart 531 per corrected copy. Its delivery and physical cost are
not constructed. When `m = 0`, the construction is the literal, paid-slot
relay word itself. The statement does not establish a new κ bound.

Here a slot carries exactly one bit per copy, the transfer times and endpoints
are fixed independently of the input, and charts initially have only the
specified input fields. Local computations and fixed-length slot payloads may
be arbitrary deterministic, including nonlinear, functions of cocharted
history. In the original scalar word, cocharted XORs and the native chart
permutations preserve constant fields; this therefore yields an obstruction on
that constant-input restriction. The stronger nonlinear model is a binary
communication relaxation, **not** an assertion that unrestricted
address-dependent physical operations cannot pack several bits into a
nonconstant field. Preloaded input information, input-dependent control flow or
message timing, moved contacts other than the specified change, and changed
final chart bindings are outside the claim.

## Fixed native incidence

Use the #8027 graph at `fb9b6a7b0d27da1cf98430893a3016bf811e2aa4`, as pinned
in #8041 at `05f6172d4d9487090fa24c75137a7c60e6fcd67e`. The packed and
expanded graph SHA-256 values are checked by `information.py`. The graph contains
630 independent public inputs and 39,600 instructions. Indices are zero-based.
There is initially no public field at chart 1 or chart 531. The 505 public
outputs bound to chart 1 are independent binary linear forms. Every native
ingress to chart 1 is a MOVE and there are 505 such slots in total.

Change the native slot at clock 8075 from `326 → 1` to `531 → 1`, leaving all
other MOVE incidences and times unchanged. Charts 326, 531 and 1 are nested,
with dimensions 6, 7 and 8. Chart 531 has precisely two incoming MOVE slots
through clock 10141, at clocks 8072 and 8098. Under the changed schedule it
has three outgoing MOVE slots to chart 1 through that clock: 8075, 10138 and
10141. The remaining 502 chart-1 arrivals can originate anywhere and can
carry arbitrary codewords. Owner-renaming SWAPs do not transport a field to a
different chart.

## Lower bound, including joint copies and side bits

Fix `k` and `m`. Grant a decoder all of the following values:

1. the `2k` bits on the two hub ingress slots up to 10141;
2. the `502k` bits on the other chart-1 slots; and
3. all `m` side-message bits, wherever their actual destinations are.

Given this transcript, the complete cocharted history of chart 531 up to
10141 and hence the three batches of hub-to-chart-1 messages can be simulated
chronologically. The chart-1 history and final output can then also be
simulated. Cycles or feedback elsewhere, arbitrary nonlinear local encoding,
and cross-copy coding do not defeat this simulation: their effects are already
included in the actual bit values granted in the transcript. The side-message
times and destinations may be chosen freely in advance but cannot themselves
encode inputs.

Thus the 505k chart-1 target outputs realized by any such protocol assume at
most `2^(504k + m)` distinct values. The native target map has rank `505k` on
`630k` binary inputs, so each target value has exactly `2^(125k)` input
preimages. The set of inputs on which the protocol is fully correct therefore
has size at most

```
min(2^(630k), 2^(504k + m) * 2^(125k))
    = 2^(630k - max(0, k - m)).
```

In particular, zero side bits imply an exact full-map probability at most
`2^(-k)`. At least `k` extra one-bit channels are required for full success.
This is a finite cardinality proof; it does not assume linear encoders or
independence of transmitted messages.

## Matching literal word and side-information construction

The literal changed word makes only these local edits:

* Omit the two original XORs into owner 2326 at clocks 8070 and 8071.
* At 8073 and 8074, initialize owner 2327 at chart 531 and copy the current
  2326 into it; move 2327 from 531 to 1 at 8075.
* Keep every other original instruction, including all 3,433 private CLEARs.

The 8075 receipt is exactly the native one. Let `M` be the native 630-output
operator, `T` this altered word, and `r` the XOR of native owners 1857 and
2224 at clock 8068. On the 630 public binary inputs,

```
T x = M x + s (r x),
support(s) = {0, 11, 117, 223, 224, 230, 249, 250, 251},
support(r) = {3, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
              72, 230, 359, 362, 365, 367, 372, 375, 378, 386, 388,
              390, 522}.
```

Both `r` and `s` are nonzero, so **the complete public result agrees with the
native map if and only if `r x = 0`**. The private-clear values also agree on
this hyperplane. For `k` independent copies the `k` residuals are independent,
so the unassisted product construction is correct on exactly `2^(-k)` of all
inputs. This attains the universal upper bound, even against arbitrary joint
coding.

Immediately before clock 10137, the changed word has the same full live owner
locations and values as the original except that owner 2326 at chart 531
differs by `r x`. Granting `r x` at that time, and XORing it into 2326, restores
all 630 outputs and all 3,433 original private-clear values. With `m` granted
oracle bits, do this for `min(m,k)` copies. The unassisted copies are correct
exactly when their residuals vanish, giving success probability
`2^(-max(0,k-m))` and proving sharpness in the stated side-information model.
The checker tests a deliberately wrong injected observation as well.

The changed chart-1 output space has rank 504 and is contained in the rank-505
native chart-1 target space. It attains 504 independent target functions:
keep the 497 unaffected output rows and, for each of the seven other affected
chart-1 rows, XOR it with affected row 0. These seven pairwise XORs cancel
the common residual. The remaining affected output, 117, belongs to chart 531
and is part of the full-map condition above.

The modified paid histogram exchanges one rank-two MOVE for one rank-one MOVE
in one local word. The compressed checker confirms this count, but does not
prove a physical supplier on unrestricted fields, a 36-call invoice, owner
scheduling, a positive supplier, or a signed outer application. In particular,
the extra oracle is not priced. These omissions preclude a κ improvement.

## Replay and provenance

Run from this directory with Python 3.10 or later and only the standard library:

```sh
python3 -I -B information.py pinned/strong-bit.json.gz > /tmp/p104-information-result.json
```

`INFORMATION.json` is the captured local output. The independent forward replay
checks owner locations, both full 630-row maps, the altered receipt and the
exact live pre-reader state. An independently implemented reverse adjoint
reconstructs and compares both complete transposes. The script checks source
hashes, exact clock prefixes, the 504 independent target combinations, the
oracle and wrong-oracle controls, private CLEARs and paid histogram. The small
`k ≤ 8` exhaustive residual-bit controls are examples; the general multi-copy
claim follows from the proof above, not enumeration. The script does not
independently re-prove the predecessor's full physical application.

Ali Romman supplied the graph; [the package notice](NOTICE.md)
and [parent notice](PARENT-NOTICE) record its research lineage. The predecessor
notice describes the larger predecessor package, not every file in this small
standalone folder. The graph provenance and predecessor pins are retained in
[SOURCES.json](SOURCES.json). The source's Apache-2.0 license is
retained in [LICENSE](LICENSE). Computational replay is author-side evidence,
not independent human review.

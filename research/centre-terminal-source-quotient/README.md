# Eight-coordinate source-only terminal quotient for two selected centre ablations

The selected time-0 and time-10 forward calls have 88 common centre-scatter
destinations. Their centre histories are not their final output requirement.
This package computes an exact **terminal residual** through every intervening
local call and supplies a sharp eight-coordinate factorization when only the
first 112 source owners vary and target/helper dirt is held fixed.

This resolves a terminal-output version of the explicitly uncomputed
fixed-dirt, overlapping-panel question in
[PR2199, Open next question 2](https://github.com/CrocSwap/integer-mult-bounds/pull/2199),
at `30ec048eedcaca970f94bbec0fdd3c52eacf9fdc`.
It is a finite certificate in that work's **local-call-only scalar projection**.
It is not a native sharing construction, a change of centre charge, or a new
selected exponent.

## Exact boundary and result

Use the selected PR1094 480-helper program from the pinned selected replay
archive. There are 704 ordinary local roles per call. Execute all eleven local
calls, time 0 through time 10, in schedule order, using their actual physical
owner maps. This involves 4,490 distinct owners; aliases are the same variable.
The relevant replica-zero calls are forward stage 0 at time 0, backward stage 1
at time 4, and forward stage 2 at time 10. The other eight calls are retained.
The observation boundary is immediately after the complete time-10 call.

As in PR1918/PR2199, scalar CLEAR/COPY/ADD/SCALE operations are exact over Q;
climbs, adapters, residual adapters and centre frame operators act as identity.
The four bridge and four idle-cover events in this prefix are **omitted**, not
executed or certified as identity. Terminal, padding and translate events are
outside the prefix. The native address/chart maps are not modeled.

Let F be this complete projected prefix. Define A by changing exactly the
sixteen rank-eight `center` events in calls 0 and 10: immediately at each such
event, replace its private C_k value by zero. All source preparation, scalar
scatter operations, complete continuations, other calls and private clearing
remain. This is an algebraic ablation experiment; zeroing a value is not a
proposed free physical operation.

Let E=F-A. Partition the initial owners into D, the 112 roles 0..111 of call 0,
and H, the remaining 4,378 target/helper/other owners. For arbitrary fixed h,
the demanded **difference of residuals** is

```
E(d,h) - E(0,h) = E_D d.
```

| Exact quantity | Value |
|---|---:|
| rank_Q(E_D) | 8 |
| nonzero terminal output rows of E_D | 224 |
| rank with first source and target blocks both variable | 16 |
| rank with all 4,490 owner inputs variable | 16 |
| overlap of the two immediate scatter panels | 88 of 88 |

Write P for the eight **source-only parts** of the original first centre inputs.
The receipt gives every coefficient of P and of an explicit 224-by-8 matrix L,
and checks every entry of `E_D = L P`. The first-cut minor on columns
`0,1,2,3,4,5,6,12` has determinant 32. More importantly, the actual **terminal**
minor on those same input columns and output owners has determinant **1/64**.
That minor proves the rank-eight lower bound after all continuations.
[RESULT.json](RESULT.json) includes both minors, the full factorization and
canonical hashes of the complete residual matrices.

Thus a linear residual decoder whose only source-dependent input is a
d-coordinate transcript z=K d must have d>=8: `E_D=R K` implies
`rank(E_D)<=d`. At the level of linear information, P d attains eight.
This familiar rank lemma is inherited from PR1918; the new certificate is its
application to the **chronological terminal residual** with overlapping panels.
No bound on arbitrary native recursive children follows.

The qualifier “source-only” is essential. An actual saved first centre value
also contains fixed-dirt contributions. This package does not supply the
offset E(0,h), subtract that dirt for free, or show that the full dirty endpoint
can be recovered from eight saved values. When target values may vary as part
of the information demand, the explicit sixteen-by-sixteen minor in the
receipt proves rank 16. This does not contradict the fixed-dirt rank 8, nor
PR2199's formal centre-history rank 16.

## Why chronological propagation matters

The original time-10 centre inputs have zero D-part in this projection, after
the intervening backward call. That known source-cut fact alone gives no
terminal lower bound. In the ablated run the first error changes later inputs;
the second ablation and its continuation still matter. Both runs must be
composed before subtracting their endpoints.

Summing the two original instantaneous scatter increments is wrong. On the
basis input D-owner 0 = 1, the true terminal residual at owner 0 is **-1**,
whereas that summed-scatter calculation gives **0**. The literal output support
has spread to 224 owners. Omitting the time-4 backward call, ablating only the
first call, or changing a repair coefficient's sign also changes the endpoint.
These are effective controls, not merely different receipt hashes.

## Reproduce and validation

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -O -B research/centre-terminal-source-quotient/verify.py
python3.12 -I -O -B research/centre-terminal-source-quotient/check_events.py
python3.12 scripts/research_package.py --package research/centre-terminal-source-quotient
```

The primary authenticates the archive before loading three exact pinned
members, verifies call-to-program digests and both complete local ordinary
endpoints, propagates sparse rational maps, derives L, verifies every entry
and both nonsingular terminal minors, and compares the typed receipt. Normal
verification is read-only; `--write` explicitly regenerates the receipt.

The separate interpreter imports none of the primary code. It executes the
literal scalar events on all 112 source basis columns and all 16 columns of
the variable-target lower minor. Exact integer-grid division is checked at
every operation; insufficient divisibility fails rather than rounding. It
also replays arbitrary deterministic target/helper dirt and private scratch,
checking the paired affine difference and final private clearing. These are
two implementations by the same AI-assisted author, not human review.
The registered integrity command checks a Git-free export and rejects changed
archive bytes and a typed receipt alteration.

## Cost and scope limits

The unchanged literal two centre phases contain 16 rank-eight children,
16 COPY, 32 CLEAR and 352 ADD operations: recursive rank mass **128**. No child,
source access, routing, restoration, hosting or precision cost is removed.
There is no admissible changed profile to submit to `ceiling.ceiling`.
The card's first ceiling example passed as orientation only.

This is a conditional information statement for a precisely declared ablation
and residual-output contract. It neither admits a native supplier nor claims
the centre histories can be shared. The omitted owner-level events, native
512-coordinate charts, dirty offsets and physical invoice remain obligations.
No selected record, source archive or predecessor package is modified.

## Open next questions

Can this terminal quotient survive the actual owner-level bridges, idle sweeps
and native chart operators? First instantiate the same ablation and terminal
boundary with those events, then compute a source-only minor or kernel witness.
This matters because the scalar projection is not a proof of a native rank
bound; correct address and frame semantics are the blocker.

Can a legal residual decoder provide both L P d and the dirt-dependent offset
with a favorable complete invoice? First specify how P d is obtained from
dirty prepared carriers, and price every observation, transport and return.
The information factorization alone supplies neither that interface nor a
cost saving.

## Provenance, overlap and credit

Base main is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4;
picker seed `37212992d41e94ab286b7d40a39e3951`, card `centre-path-sharing`.
The changed scope and exact source pins are in [TASK.json](TASK.json) and
[SOURCES.json](SOURCES.json). The overlap record distinguishes fresh REST PR
coverage from the last complete Discussion snapshot: GraphQL refresh was
rate-limited, so the latter is explicitly stale. No absence-of-match novelty
guarantee is claimed.

Adam Gall's PR1918 supplies the scalar projection and transcript rank lemma;
thakrarsagar's PR2199 supplies the dependent-call census and explicit missing
fixed-dirt output question. PR2048 (commdata2338) provides a different native
lift for disjoint calls; PR2391 gives a native centre-history counterexample,
and PR2461 an owner-local observation floor. None is replaced by this projected
terminal calculation. The selected construction is Rohan Arun's PR1094 lineage,
with Jeremy Kothe, Hao Yan, icekylinx and all retained source contributors.
New terminal certificate, checker and exposition: ywz65, with substantial
OpenAI Codex assistance. Apache-2.0; separate AI review is not maintainer admission.

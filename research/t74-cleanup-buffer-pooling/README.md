# A 48-field private pool for the borrowed T74 cleanup

**The frozen PR2269 cleanup can use 48 private FULL-frame fields in place of
76 dedicated buffers.** The forward orientation needs 44 slots in the certified
interval schedule; the inverse-transpose orientation needs 48. A shared-capacity
bank therefore saves **28 fields**. No scalar operation is added: 151 and 409
proved zero operations, respectively, are omitted, and the remaining operations
keep their original order. All 661 ordinary entry arrays are arbitrary.

This is a finite allocation construction with a scoped proof, author-checked
with an independently represented dense cross-check. It is not an admitted
supplier, a new recursive profile, a new κ, or independent human review.

## Exact source and result

The claim is in [Discussion #2609](https://github.com/CrocSwap/integer-mult-bounds/discussions/2609).

The two `BORROW-WORD-43base/extra.json.gz` files are byte-for-byte copies from
Jeremy Kothe's [PR2269](https://github.com/CrocSwap/integer-mult-bounds/pull/2269),
head `b479fc5567bc09ab9185bffe89b62594f36d74e5`. Their serialized cleanup lists
are identical, although their enclosing words differ. We bind both files and
check both orientations; this is one common cleanup stream, not four different
constructions. [INPUTS.json](INPUTS.json) records original paths, commit, Git
blob IDs and SHA256 hashes. Source notices are retained unchanged.

[Sagar Thakrar's PR2315](https://github.com/CrocSwap/integer-mult-bounds/pull/2315),
head `4a2f20ea339e30348448096ca789d0efe55df9bb`, reproduced the words and found
that the 76 eagerly allocated buffers had not been charged. Later constructions
charge dedicated banks. This package addresses the distinct storage-reuse
question; it does not repair or endorse the rest of PR2269's record claim.

| Per enclosing word | Forward | Inverse transpose |
| --- | ---: | ---: |
| Original private buffers | 76 | 76 |
| Buffers ever formally nonzero | 76 | 58 |
| Maximal nonzero intervals | 81 | 65 |
| Optimal interval-pool slots | 44 | 48 |
| First maximum, after cleanup event (one-based) | 82 | 2686 |
| Zero ADDs omitted | 123 | 361 |
| Zero SCALEs omitted | 28 | 48 |
| WARP operations retained | 43 | 43 |
| Original / retained total operations | 4500 / 4349 | 4500 / 4091 |

[EXPECTED.json](EXPECTED.json) contains every nonzero interval, a **static
per-logical-buffer** slot assignment over the hull of its intervals, the exact
peak rows, the omitted event numbers, and the ordinary endpoint digest. The
static hull coloring already attains the same peak as splitting lifetimes;
no mid-lifetime copying, dynamic allocator, or value-dependent decision is
required. `pooled_replay` in [verify.py](verify.py) executes that allocation.

## Model and proof

Let `A = Q[F_43]` be the group algebra of the free group on the 43 invertible
warp symbols. Each of the 661 ordinary registers starts as a separate free
module generator `x_r`; every private buffer starts at zero. A scalar gate
adds a rational multiple of one row to another or scales one row. A warp
left-multiplies every term by its symbol; only adjacent inverse symbols cancel.
This is exact symbolic arithmetic, not numerical sampling. For the second
orientation, ADDs reverse source/destination and negate their coefficient,
SCALEs invert their coefficient, and symbol `j` denotes `K_j^(-T)`.
Applying inverse transpose to each chronological gate preserves gate order.

A reduced row is zero exactly when all its coefficients vanish. Trace each
buffer's maximal nonzero intervals. A zero source makes an ADD the identity;
a SCALE or WARP applied to a zero buffer is also the identity. Removing exactly
these events is valid for arbitrary ordinary inputs and for **any** invertible
substitution for the warp symbols. Both buffers and ordinary data are checked
as part of the final boundary. No caller-specific reachable-state restriction
is used: the proof checks all independent cleanup-entry arrays.

For each logical buffer, take the hull from its first nonzero write through
its last zero-return event. Color these inclusive integer intervals by the
usual earliest-available-slot rule. Each assigned field is zero at allocation,
contains the logical value while allocated, and is zero at release. An
induction over events proves that renamed execution equals the original
execution: skipped events are identities, and every retained source and target
is allocated or ordinary. The verifier checks the zero boundary at each
allocation/release and compares every ordinary endpoint coefficient. All pool
fields return to zero.

The 44 forward and 48 dual simultaneous-live intervals certify lower bounds
for **interval allocation with distinct storage for overlapping lifetimes**;
the displayed colorings attain them. This alone would not exclude equal-value
coalescing. Indeed, at the first forward peak two pairs of buffers carry equal
expressions, so we do not claim a forward minimum under that broader model.

There is a stronger certificate for the **common 48-field bank**. At dual cut
2686, all 48 private rows are distinct and nonzero, and every row is a plain
rational linear form: all warp symbols have canceled. The receipt gives an
explicit small input witness using SHA256-derived signed 16-bit integers
(seed 0, maximum absolute input 32736). Its 48 outputs are distinct and nonzero;
maximum absolute output is `707881/4`, and denominators divide 4. The witness
therefore survives the actual invertible warp specialization. On this input,
a field storing one literal buffer value cannot store another different
buffer value at the same cut. Thus 48 is also a sharp common capacity for
**direct literal storage**, even allowing equal-value coalescing, when ordinary
registers and the declared event boundaries are retained.

That lower bound does **not** allow encoding several values into a field,
address packing, borrowing ordinary/cold storage, recomputation, spilling,
changes to precision, or resynthesis/reordering of the cleanup. It is not an
information-theoretic scratch lower bound for arbitrary circuits.

## Cost and interface boundary

All original cleanup gates carry the FULL frame; preserved cold helpers are
never touched directly. The checker binds the private namespace to exactly
`704 + cold_helper` and confirms that no earlier section touches those buffers.
The new bank is used only in the same cleanup interval. Logical scalar work
decreases by the zero operations above, and the retained warp count is unchanged.
The construction adds no arithmetic, transport, copy, or recursive call.

Under a convention that clears each physical private field once at allocation
and once at release, the candidate uses 88 forward or 96 dual CLEARs instead of
152, or 96 for a common 48-field bank. These are conditional invoice counts,
not a checked native emitter patch. Static routing, array allocation, exact
native phase bindings, precision/tape constants, full hosted admission, and
integration with later 78-buffer words remain to be checked. A smaller private
bank by itself does not establish any change in κ.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/t74-cleanup-buffer-pooling
```

Equivalent direct commands:

```sh
python3 -I -O -B research/t74-cleanup-buffer-pooling/verify.py
python3 -I -B research/t74-cleanup-buffer-pooling/check_dense.py
```

Expected final markers are `PASS_T74_CLEANUP_BUFFER_POOLING` and
`PASS_DENSE_POOL_ORACLE cases=8 columns_per_case=1322 primes=65537,1000003 noncommuting=PASS`.
Replay is read-only. `verify.py --write FRESH_PATH` explicitly creates a fresh
receipt and refuses to overwrite an existing path. Default replay recomputes
and compares every stored certificate field, preserving JSON type distinctions.

The primary has six semantic controls per word/orientation: overlapping
allocation, release before zero, dirty pool entry, a wrong-sign closing ADD,
a re-enabled unallocated zero read, and an inverse-warp sign change that alters
the ordinary endpoint despite scratch cleanup. `check_dense.py` imports neither
the primary nor predecessor code. It separately interprets literal gates using
noncommuting determinant-one 2-by-2 matrices over each of two prime fields,
checks all 1322 scalar basis inputs, every zero/nonzero lifetime, the peak-row
certificate, the pooled boundary and scratch restoration. This finite-field
cross-check supports implementation confidence; the group-algebra derivation
and rational replay establish the exact identities.

## Open next questions

- **Native adoption on this pinned word.** Emit the static slot renaming and
  skipped identities in the native cleanup, then price allocation and routing.
  This would turn the logical pool into an admitted physical saving; the native
  stream and whole-call accounting are the missing artifacts.
- **Later borrowed words.** Apply the same independently derived lifetime test
  to a named 78-buffer successor, checking its exact cleanup instead of carrying
  forward the number 48. Changed kernels and source-partner lifetimes may change
  the intervals and peak; no such transfer is established here.
- **Forward equal-value coalescing.** At forward cut 82, `(1015,1202)` and
  `(1031,1214)` coincide. Examine their next writes before trying a smaller
  forward-only bank. Equal values at one cut do not authorize merging complete
  lifetimes, and cannot defeat the dual 48-value witness in the direct-storage
  model.

Structured questions and the changed task scope are in [TASK.json](TASK.json).

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Jeremy Kothe/PR2269 supplies the frozen T74 words. Sagar Thakrar/PR2315 supplies
the independent accounting finding. Cinna Davis (@1337isnot1337)/PR2226 supplies
the anticipatory dirty-borrowing mechanism, early restoration and private-zero
cleanup. Dugongue/PR2309 supplies dedicated private-stock accounting in the
successor line. Rohan Arun, Marius-Paul Dumitrean, icekylinx and the retained
T74/provider/compiler lineage keep the attribution in `source/` notices.
No predecessor code is imported, executed or copied into the new checkers.
The copied words and notices retain their original Apache-2.0 context.
No independent human review or hosted-CI success is claimed.

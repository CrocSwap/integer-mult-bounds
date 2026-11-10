# One classification per rank pair constructs the same mirror windows

This scoped algorithmic proof and implementation are produced by Nick
Petalas. Apache-2.0. Window semantics and the compiler context are zxv's
PR4483, retaining Ryanson Jonathan's corrected PR4459 mirror identity and
Jacob Alan Sussman's integer compiler. Endpoint sweeps are classical.

## Contract

Let `T[k]` and `P[r]` be finite nonempty positive integer rank histograms.
Form the sorted cuts `0`, `1/k` and `1/r`. The direct constructor visits each
elementary cell `(left,right]` and every ordered target/paid pair. At any
interior point `x`, that pair contributes `T[k]*P[r]` at product rank `kr`:

- to the exit histogram when `r>k` and `1/r < x <= 1/k`;
- to the source histogram when `k>r` and `1/k < x <= 1/r`.

Equal ranks contribute neither. Cells with no exits are omitted. A cell
with exits and no source histogram raises the funding error. The return
value is the ordered list of retained `(left,right,exits,sources)` tuples.

`windows.mirror_windows` preserves that complete return value and funding
error on its declared input domain: each histogram has at most 64 ranks,
and ranks and counts are positive integers at most `10^12`. Booleans are
rejected. The original compiler's stronger native-profile hypotheses are
unnecessary for this window-construction lemma.

## Sweep invariant

Each unequal pair has exactly one active interval
`(a,b]=(1/max(k,r),1/min(k,r)]` on exactly one side. Place a positive event
of weight `T[k]*P[r]` at `a` and its negative at `b`, using product rank `kr`
as the histogram key. Product collisions add, rather than deduplicate.

Immediately before emitting cell `(c_i,c_(i+1)]`, apply all events at its
left endpoint `c_i`. The resulting active histogram contains exactly the
pairs satisfying `a <= c_i < b`, equivalently `a < x <= b` for every
interior point `x` in that cell. Thus it equals the direct histogram.
Grouping all events before checking positivity preserves coincident starts
and stops, including collisions at the same product rank.

This proves the invariant by induction over the sorted cuts. The emission
and funding rules then give identical return values or the same funding
error at the same first offending cell. Applying the final closing events
leaves both active histograms empty, an executable postcondition.

The API copies each emitted histogram. Earlier cells cannot change when
the sweep advances or when a caller edits another cell. Inputs and separate
invocations share no mutable state.

## Work removed and work retained

Write `K=|supp(T)|`, `R=|supp(P)|`, `S` for the number of elementary cells,
and `U` for the number of unequal ordered rank pairs. The direct constructor
classifies `S*K*R` pairs. The sweep classifies `K*R` pairs and records exactly
`2U` endpoint updates. These are enumerated logical operation counts, not
elapsed-time or whole-caller complexity claims.

Sorting cuts, updating active counters and copying output histograms remain
payable. In particular, materializing all returned histograms can dominate
the cost. No claim that total work is merely `O(KR)` follows from the pair
classification reduction. Shared compiler code is not changed.

On the exact retained inventories, the checker enumerates:

| Inventory | Elementary / emitted cells | Direct classifications | Sweep classifications | Endpoint updates |
| --- | --- | --- | --- | --- |
| p7 | 16 / 9 | 1,296 | 81 | 158 |
| p16 | 25 / 19 | 4,550 | 182 | 360 |

The inventory files are cited inputs; no native supplier, root, invoice,
compiler theorem or predecessor scientific certificate is being audited.

## Evidence and limits

The checker compares complete lists and every histogram multiplicity on all
6,400 pairs of nonempty histograms on ranks 1–4 with counts 0–2. Exactly
3,688 return matching lists and 2,712 reject for missing source funding.
The written invariant, rather than extrapolation from that finite family,
supplies the general equivalence proof.

A literal boundary fixture gives one cell `(1/3,1/2]` with exit histogram
`{6:33}` and source histogram `{4:35}`. Other controls exercise equal ranks,
unfunded exits, colliding product ranks, malformed inputs, input preservation,
independent cell snapshots and isolation across calls. Both modes use explicit
exceptions and generate source/package-hash-bound receipts on stdout.

There is no runtime speedup claim, default adoption, new compiler admission,
native/caller implementation, κ improvement, selected-frontier change,
independent human review or formal proof-kernel acceptance. The source's
physical, chronological, ownership, precision, tape, stock and analytic
obligations remain separate. Full caller timing and an incremental consumer
are open questions.

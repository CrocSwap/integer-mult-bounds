## Change and mathematical scope

The published [Pascal occurrence codec](https://github.com/CubeJerry/integer-mult-bounds/tree/91246e5131152ccb1f64a969c36706360861f821/research/pascal-occurrence-codec)
left contiguous source indexing open. This adds exact rank/unrank between
fresh source occurrences and every integer in `[0,S_N)`, extending to all
replicated productive rows `[0,a*S_N)`. Owned banks receive no productive
source credit.

The subtree count depends only on depth, paid-rank product and last paid
rank. With q distinct paid ranks and d target ranks, at most
`1+q*binom(G+q-1,q)` states and `binom(G+d,d)` target multiindices suffice.
This avoids enumerating the chronological class tree or each multinomial
occurrence. The proof includes exact ordering, state/count bit sizes and
separately charged deterministic setup/query work. Sorted level lists and
binary-search count tables remove hash-dispersion assumptions. A separate
serialized-table construction charges metadata access on fixed tapes.

**No new kappa and no complete assumption discharge.** The selected
conditional value remains 0.00363005817.

## Why it matters and what is new

This supplies actual integer row names for the preceding symbolic owner
codec, resolving its first open question and advancing #6878's occurrence
emitter obligation. The inherited Pascal flow, live-role correctness and
rank descent are not new claims. Distinct paid positions retain separate
physical intervals even when their subtree statistics are identical.

## Verification

```sh
python3 -I -W error -B research/lockstep-source-row-index/verify.py
python3 -I -W error -O -B research/lockstep-source-row-index/verify.py
```

Both modes agree on 102 complete literal small flows and all 1,431 fresh
source ranks/inverses, including replicated row intervals, plus fourteen
rejecting controls. A height-64 fixture needs 4,161 states despite a class
tree exceeding 5*10^30 nodes. A different ordered-word-product counter
corroborates all 4,161 state totals using incoming-unit subtraction.
The exact source-count and interval samples are recorded in VALIDATION.json.

Independent review found and corrected a worst-case complexity defect in
the initial hash-table implementation. A fixed five-paid-rank rule makes
every same-depth state hash identically; the repaired checker verifies its
3,961 states at height 8. PROOF.md preserves the obstruction and explicitly
separates indexed arithmetic/comparison work from paid serialized scans.

The unchanged predecessor codec and literal oracle are source-hashed.
The ambient-property test adapter and source-aware comparison are disclosed.
Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Codec dependency: `91246e5131152ccb1f64a969c36706360861f821`.

Separate functional and cost-model reviewers passed the repaired snapshot.
The independent checker uses literal ordered role words instead of the
author's source-count recurrence and covers 16 cases, 314 sources and all
1,570 replicated rows; four exact collision families also pass. From this
package directory run `python3 -I -W error -B independent_check.py .`.
REVIEW.md and COST-MODEL-REVIEW.md preserve both the original objection and
the accepted correction; INDEPENDENT-RESULT.json pins the executed snapshot.

## Limitations and next obligations

The selected finite product's complete role/paid-owner manifest remains
required. This does not execute source-complement grouping, smaller-rank
substitution, owned allocation, payload access or the physical tape caller.
Its canonical row numbering need not equal incidental numeric IDs in an
older interpreter. Any layout conversion retains its actual movement bill.
All selected native, compiler, precision/tape and analytic conditions remain.
No practical winning-rank materialization, supplier admission, human proof
or formal-kernel acceptance is asserted.

## Credit

Prepared for Jerry Chen / **@CubeJerry** with substantial OpenAI assistance.
Credit the preceding occurrence-codec publication and separate root AI review,
Jacob Alan Sussman's lockstep/Pascal construction, zxv's compiler and literal
audit, Mark / Matarener's #4691 executor, and the #6878 geometry lineage.
Original dependency files and notices are unchanged. Apache-2.0.

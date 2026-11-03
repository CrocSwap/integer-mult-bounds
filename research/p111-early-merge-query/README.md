# Draft: P111 query interfaces; complete scatter and kappa pending

**No new kappa.** Exact local native forward and inverse-transpose checks now pass
for a retimed centre query with no incremental recursive calls relative to the
replaced copy and already-paid terminal centre moves. The existing scatter
cannot accept its new target endpoint, so the full decoder is still unadmitted.

For puncture 0, the query is half the sum of current centre values 61, 63, 31
and 256, with the omitted input specialized to zero. The checker recomputes
all clean and dirty coefficients from the pinned A word; the query has 62 dirty
columns whose compensation is a remaining obligation.

After the seven unchanged zero-endpoint copies, move these four centres from
their rank-eight frames to FULL. Those four rank-one moves were already needed
at their terminal endpoints, and none of the four centres is used in B or the
early cleanup. Form the weighted sum reversibly in one centre, copy FULL to the
chosen endpoint line E (rank eight), then undo the scalar mixing. The local
invoice is 4 H1 + H8 both before and after. The extra scalar work is six ADDs
and two SCALEs, with one temporary stream. Every logical centre is restored
at FULL. This changes the copy target interface and timing; it does not establish
unchanged whole-call owners or idle volume.

Exact signed Pauli and global phase checks cover every local native transition.
Two dense Gaussian fixtures per orientation exercise the complete block,
including dirty accumulator inputs and inverse transpose. The standalone checker
reconstructs the source-column identity and verifies chronological availability.
These are finite checks, not independent human review or a formal theorem.

The retained B/early-tail chronology is incompatible with the new line endpoint.
An independent incidence closure finds 23 or 40 incompatible target endpoints,
and 12 to 22 incompatible helper endpoints, depending on the replaced centre.
A separate local L/U screen rejects all 448 puncture/pivot instances. Only the
independent eight-centre incidence certificate is packaged here. This is a
necessary-frame obstruction for the retained chronology, not for new scatters,
changed contracts, paid descents or specialized zero-value implementations.

Reproduce with Python 3.10+ standard library and assertions enabled:

```sh
python3 -B research/p111-early-merge-query/verify.py
python3 -B research/p111-early-merge-query/native_query.py
python3 -B research/p111-early-merge-query/retimed_centre_query.py
python3 -B research/p111-early-merge-query/cut_reachability.py
```

The original early-merge witness and its checks remain unchanged: 16 A values,
transport 23 H1 + 6 H2 + H4 (rank 39 versus direct 86), four temporary streams in
each orientation. Their favorable volume screen grants deletion, compensation,
endpoint and storage credits that need not be jointly realizable. It is not an
admitted profile. The retimed-centre variant is a different local construction.

Next: synthesize a scatter with the new endpoint, then charge compensation,
temporary allocation/disposal, whole-call owners, precision/tape and complete
outer inequalities. Keep this PR draft until a complete admitted improvement
exists. All all-size/compiler, common-label/mutable-source, exact recovery,
analytic transfer, PR559 and PR589 H1-H5 caveats remain. No selected supplier,
unconditional multiplication theorem, or global packing optimum is claimed.

Credits and exact source pins are retained in NOTICE.md and SOURCES.json:
PR1297 current word, PR1134 arithmetic/context, PR1060 exact native compiler,
physical executor and transpose bridge, plus their retained lineage. Prepared
by Rohan Arun with substantial OpenAI Codex assistance. Local verification and
hosted CI are separate; no hosted CI success is claimed.

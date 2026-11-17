# Exact block minimum for the rounded tensor image

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written proof with exact finite corroboration.
There is no new kappa or selected-frontier change.

The original-coordinate rounded tensor image has an exact, sharp
contiguous block-copy count. This adds a layout invariant to CubeJerry's
[PR6995](https://github.com/CrocSwap/integer-mult-bounds/pull/6995),
whose physical extractor and reported invoices are cited predecessor work,
not replay targets. The question here is original local side work, not an
answer to its production-caller handoff.

For integer dyadic target periods `t_i=2^ell_i` and integer source periods
`s_i<t_i<2s_i`, define

```text
Q_i(j) = floor(t_i*j/s_i + 1/2),  0 <= j < s_i
d_i = t_i-s_i
b_i = 1 if 3*s_i > 2*t_i, otherwise 0
S_D = R_D = 1
S_i = s_i*S_(i+1)
R_i = d_i*S_(i+1) + b_i*R_(i+1)
```

Axis zero is fastest and the linear field begins at address zero. The
minimum number of intervals that copy exactly the selected records in
order, copying each once and copying no hole, is `R_0`. Formula (1) in
[PROOF.md](PROOF.md) gives its closed finite sum. Each `b_i` states whether
the scalar image touches its right target endpoint. The proof counts all
and only the carry boundaries at which two blocks join. Copying maximal
selected runs attains the lower bound for arbitrary record contents.

For target/source pairs `(4,3), (8,7), (8,5)` the sharp answer is
`1*7*5 + 1*5 + 3 = 43` blocks for 105 records in a 256-record target field.
This is a theorem about the layout and the stated interval-copy contract.
It is not a measured speedup or a native operation count.

## Evidence and reproduction

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/rounded-image-block-minimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/rounded-image-block-minimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rounded-image-block-minimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rounded-image-block-minimum --check-source-history --check-modes
```

Another host can substitute its CPython 3.12 path. Expected direct output
is `PASS_ROUNDED_IMAGE_BLOCK_MINIMUM` in a generated JSON receipt bound to
the six package files and three source texts. The verifier writes nothing
and imports no predecessor executable. The registered runner also checks
source Git blobs, pinned historical metadata and declared live inputs.
No receipt is hand-written or committed.

The census enumerates every ordered dyadic packet with `sum(ell_i)<=10`,
including every admissible source period for each axis. That is 4,180
packets, 3,270,652 target records, 1,831,047 selected records and 657,556
maximal blocks. One engine literally rounds source coordinates. A second
scans target coordinates and tests inverse half-open integer intervals.
Their complete ordered images agree. Both the backward recurrence and
the finite sum equal the literal run count. Executing the run intervals
copies exactly the selected addresses and no hole in every packet.

The named 256-record fixture additionally copies distinct nonzero record
values and preserves its source. Nine invalid packets reject. Five
boundary controls distinguish the fixed seam from a cyclic seam, a
trailing hole, the two axis orders of a mixed packet, and a larger
sixteen-axis formula evaluation. The last control does not enumerate its
large volume. The universal claim rests on the written proof.

## Limits and implementation

The exact count applies to interval copies with the stated seam and order.
It does not exclude a changed producer, paid reordering, copying holes
followed by filtering, noncontiguous native reads or a different service.
No bulk-copy tape operation or improved scan time is supplied. Source
delivery, movement, restoration, stock, precision, native cost and compiler
closure still require complete invoices. No selected cold replay, Lean,
Docker, full Gaussian transform or multiplier is run. All five selected
framework assumptions remain. Independent human and formal proof-kernel
review are unclaimed.

The formula evaluator permits at most sixteen axes with exponents at most
64; these executable caps do not restrict the written theorem. The literal
oracle enforces target volume at most 1,024. Its worklist has capacity
5,000, checks full exhaustion, and checks its packet coverage by a separate
composition-count recurrence. All loops have finite bounds; there is no
recursion, subprocess, network access or dynamic module loading. Functions
fit within sixty physical lines. Explicit checks remain enabled under `-O`.

Power of Ten rule 3 has a managed-runtime deviation in `verify.py`.
Python integers and collections allocate during computation. The sixteen
axis caps bound formula integers to at most 1,024 bits for the full volume;
the literal engines retain one packet of at most 1,024 addresses at a time.
The worklist retains fewer than 5,000 packets of at most five axes. Source
and package files are capped at 128 KiB each, and the manifest at eight
source rows. Hashing and JSON parsing use ordinary bounded Python
allocations; allocator internals are not instrumented. Warning-strict normal
and optimized executions plus AST/function-size inspection provide the
available diagnostics. Fixed-capacity storage would be a separate native
implementation if a real caller uses this formula.

## Open next questions

- What is the minimum over axis permutations that a real producer can
  legally deliver? Start with an adjacent-axis exchange inequality from
  recurrence (2), then price the complete physical permutation. The legal
  producer layout and its movement cost are blockers.
- Can a native extractor exploit maximal blocks with a complete setup,
  movement, copy and restoration invoice? Start with one literal producer
  packet and an encoded block iterator. A bulk-copy service, source delivery
  and ownership/precision/storage accounting remain blockers.

The structured questions are in [TASK.json](TASK.json). Neither is reserved.

## Sources and coordination

Base main is `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8,
selected #7000. The cheap source-binding orientation passed. The
complex-new-helper-inventory card is explicitly changed to this local
layout side result; no helper supplier or selected assumption is completed.
[SOURCES.json](SOURCES.json) pins the exact predecessor texts, task card
and selected record. Frozen files and predecessor credit are unchanged.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19541691)
followed live open/account PR, active Discussion, main and merged
general-form searches and local reservation checks. Those checks found
the credited scalar Beatty result, not the tensor carry formula. Their
coverage does not include every unpublished result or arbitrary unseen
diff. No global literature-priority claim is made.

Credit CubeJerry for #6995 and its original-q extraction boundary;
Dugongue / David Ganz for #5566's scalar Beatty runs and fixed-seam warning;
the canonical Gaussian and #3851 selection authors, the retained
Tape/Count contributors, and the normalized-recovery predecessor for the
inherited image and carrier. Elementary interval counting and tensor
flattening are classical methods. Only the fixed-seam tensor count and
its stated block-readout consequence are claimed as the new step.

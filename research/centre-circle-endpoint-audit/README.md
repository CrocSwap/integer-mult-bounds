# Centre-circle cancellation does not erase the full response

This independent audit checks the proposed centre reduction in
[dcharb78's PR3147][proposal] at `5cbc48b18cb05327a8dacab3f626412d3bc5e924`.
It supplies an exact input witness, rational minors and the late bridge response
of the **hosted scalar skeleton** in the selected replay archive.

- The F0/F2 demands have joint rank **16** on the original source and target
  inputs, even though the F2 demand vanishes on the original source alone.
- Each stage-8 call has **three later bridges** in the audited hosted schedule.
  Its eight independent centre responses survive on all four target panels.
  The sixteen replicas have direct-sum response rank **128**.

Consequently, source-only cancellation does not justify a common eight-scalar
linear observation of both demands without additional information. Absence of
later recursive calls does not justify deleting the late centre response under
the unchanged returned-data contract. A changed program or consumer may still
save work, but must supply and price that missing identity.

No smaller complete program was found here. There is no new kappa, supplier
admission, selected-record change or counterexample to integer multiplication.

## Exact model and sources

Runtime input is only the SHA256-pinned
`research/community-frontier1094-audit/selected-replay.tar.gz`, from main
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
The two compressed members and their exact hashes are in `verify.py`:

```
candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz
candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz
```

Execute every literal scalar operation on 704 local roles and eight initially
zero private C registers. Non-scalar climbs, adapters and recursive events act
as identities **in this specialization only**. At each named centre event,
record its current C input, then add a fresh formal increment. This is the
scalar specialization used by PR3147's
[`extract_local_cuts_and_responses` and chronological check][audited-code].
It is not an implementation or semantic proof of the actual recursive children.

The primary replay carries every local input column, including arbitrary
initial helper values. It checks the ordinary local endpoints
`Y += X` and `X -= Y`, with other roles unchanged and private C returned to zero.
It then composes the actual global owners and chronological bridge schedule.
Private C is clean scratch; the borrowed local helper inputs are not assumed
zero in this replay. The lower bounds already hold on the subspace where those
helpers start at zero.

PR3147 already reports joint rank 16 and local response rank eight. Those
observations are credited, not claimed as new. This package independently
certifies exact rational minors, supplies the target-only witness, derives the
full late bridge response and identifies the unproved cost implication.
PR3147's owner decoding, route census and braid theorem are outside this audit.
Its source files are not imported, executed, vendored or required for replay.
Their exact Git blobs and hashes are recorded as claim provenance in `TASK.json`.

## Original target data survives the circle

For replica zero, pair zero, let `D0 = 0..111` and `T0 = 112..223` denote
**original input columns**, not current role contents. The three calls have
`time` fields 0, 4 and 10 and orientations F0, B1 and F2.

Let R be the eight F0 demand rows restricted to D0. Exact propagation gives

```
                    original D0       original T0
F0 demands                 R                  0
F2 demands                 0                 -R
```

There can also be coefficients on other original input columns. They cannot
lower the rank of this restriction. On port columns
`0, 1, 2, 3, 4, 5, 6, 12`, the determinant of R is exactly **32**.
The corresponding sixteen-column joint minor is block diagonal with blocks
R and -R, so its determinant is **1024**. Sixteen rows give the matching upper
bound. A linear factorization of the joint pair through q scalar observations
with no additional information therefore needs `q >= 16`.
This does not exclude sequential reuse, new reads, recomputation, nonlinear
encodings or a changed endpoint.

A concrete witness sets original `T0[0] = 1` and every other input to zero:

```
F0 demand = [ 0,  0,  0,  0, 0, 0, 0, 0]
F2 demand = [-1, -1, -1, -1, 0, 0, 0, 0]
```

The source cancellation is real. The information moved to the original target
inputs rather than disappearing.

## The late response passes through the bridges

The audited hosted template has 482 schedule events. In replica zero, the
stage-8 call has `time = 88` at zero-based schedule index **224**, followed by
bridges **229, 230, 231** with source/destination pairs `2->3`, `1->2`, `0->1`.
Every other replica has the same three-bridge suffix. `RESULT.json` records all
sixteen call times and indices, for **48** bridges in total.

This corrects PR3147's hosted stage-8 text claiming no subsequent bridge events.
There is no later local-cover call on that replica. The local response also
has zero D/helper component, as PR3147 states. Neither fact makes its target
response zero.

Let U map the eight fresh centre increments to the local target output u.
The minor on target ports `0, 1, 2, 3, 4, 5, 6, 12` has determinant
**1/2048**, so U has rank eight. At local exit the increments affect only Y3.
The literal bridge rule is

```
X_dst += X_src
Y_src -= Y_dst
```

Following the three bridges, the target-panel differences are

```
(Y0, Y1, Y2, Y3) = (-u, +u, -u, +u).
```

This embedding is injective. Each replica retains rank eight, and their
returned-data supports are disjoint, giving rank `16 * 8 = 128`. The primary
checker verifies every coefficient, not only the rank or one endpoint port.
A single unit centre increment already has a nonzero returned target response.

This rank is measured after the bridges, before terminal translations/exchanges.
Fixed affine translations do not change a response matrix; any invertible
terminal state map preserves its rank. An actual projection onto fewer
observed roles needs a separate composition check and is not assumed here.
The 128 scalar response coordinates are not a newly certified native COPY bill.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/centre-circle-endpoint-audit
```

Direct read-only checks, also usable in a Git-free source export with the pinned
archive at its repository-relative path:

```sh
python3.12 -I -O -Werror -B research/centre-circle-endpoint-audit/verify.py
python3.12 -I -O -Werror -B research/centre-circle-endpoint-audit/independent.py
python3.12 -I -O -Werror -B research/centre-circle-endpoint-audit/test_verify.py
```

The primary marker is
`PASS_CENTRE_CIRCLE_ENDPOINT_AUDIT joint_rank=16 late_rank=128 late_bridges=48 no_new_kappa`.
`verify.py --emit` regenerates the whole receipt to stdout without writing files.

The independent implementation imports neither the primary checker nor any
predecessor implementation. It executes dense, one-input-at-a-time scalar
states through the actual local words and prefix schedule for all sixteen
minor columns. Integer Bareiss elimination independently gives determinants
1024 and 32. Eight separate centre impulses reconstruct the response minor and
its sixteen bridge suffixes.

Eight behavioral groups exercise optimized CLI/emission, the literal target
witness, missing centre, wrong fanout sign, omitted/reordered/sign-flipped
bridges, wrong owner-role mapping, deficient-rank controls, and a read-only
Git-free export. Receipt and archive corruptions must fail. The registered
replay runs both checkers and these controls. It does not run native compilation,
full supplier admission, the outer certificate or `make frontier1094-verify`.

## Open next questions

1. Can a changed F0/B1/F2 program preserve original-target and dirty-helper
   demands while eliminating paid work? First write the replacement and compare
   every input/response column, then charge its new reads and restoration.
   No such replacement or complete consumer bill is supplied here.
2. Does a different actual terminal consumer annihilate any late response?
   Pin that projection and compose it with U and the bridge suffix, retaining
   every required returned role. Native child semantics and that consumer
   remain unverified here.

Family decision: finish this audit and stop direct-elision expansion. The
reported reduced profiles remain conditional on a changed full-boundary
construction; this result does not exclude other sharing mechanisms.

## Credit and engineering notes

Nick Petalas. Apache-2.0. Substantial automated assistance was used. No
independent human or formal-kernel review is claimed.

Credit dcharb78/PR3147 for the centre-circle proposal and existing local rank
observations; Aaron Wang/PR3120 for the earlier demand audit and PR3075 for
charged sharing; Ross Richardson/PR3071, Gonzalo-Mier/PR3097, ywz65 and ToikY
for the related observation/return boundaries; Douglas Colkitt and Sagar
Thakrar for the ceiling/coverage framework. The frozen selected construction
retains Rohan Arun/PR1094, Jeremy Kothe, Hao Yan and the complete credited
geometry, decoder, compiler and ownership lineage. No predecessor bytes change.

Build the Lever changed the deliverable to a kept exact replay and explicit
minors. Prove It Works required literal schedule tracing and a second arithmetic
implementation. Test Behavior, Not Implementation required target/output
witnesses and semantic mutants rather than success-message checks alone.
Laziness Protocol kept this in one isolated package without changing the
selected verifier or adding a new global census.

Power of Ten inspection covers the three Python files. Functions fit within
60 physical lines. Iteration is bounded by the authenticated inputs: fewer than
30,000 events per local word, 704 local roles, eight centres, 144 calls,
482 schedule events, 14,336 global roles, sixteen replicas and minors of order
at most sixteen. The dense oracle performs sixteen prefix probes and eight
centre impulses. Subprocesses have 30-second timeouts. Explicit exceptions keep
invariants active under optimized Python.

Rule 3 deviation: Python and its standard library allocate managed objects.
Archive/member/payload bounds and a single synchronous replay bound live data;
there is no resident service, unbounded queue or concurrent worker. A service
accepting arbitrary circuits would need fixed-capacity storage and stronger
operand/size validation. The unittest loader has one fixed local module target;
no predecessor implementation is loaded by either arithmetic checker.
Rule 10 uses warnings-as-errors, source compilation and strict applicable Ruff checks. An exploratory all-rule scan also reported
inapplicable pytest-style rules for unittest and optional documentation/style
rules; no diagnostic suppressions were added. No shared lint configuration or
historical source is changed.

[proposal]: https://github.com/CrocSwap/integer-mult-bounds/pull/3147
[audited-code]: https://github.com/CrocSwap/integer-mult-bounds/blob/5cbc48b18cb05327a8dacab3f626412d3bc5e924/research/centre-sink-duality-and-braid-quotient/verify.py#L363-L395

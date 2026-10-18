# PR626 owner boundaries and the bridge-omission blind spot

**Adversarial mathematical audit; no new κ.** The selected whole-owner
allocation passes an independent event-state check. Its timing predicate
alone nevertheless cannot certify the presence of any of the 72 bridges:
deleting any one leaves all borrowing windows unchanged, while changing
the normalized scalar data map. The selected production audit separately
binds the full controller; this is **not** a reported acceptance bug in it.

Prepared for **Tekalign / tekuuu** with substantial OpenAI Codex assistance,
including a separate agent's review. Apache-2.0. This is not independent
human peer review.

## Reproduce

From the repository root, using only Python's standard library:

```sh
python3 -I -O -B research/owner-boundary-audit/verify.py
```

Expected status: `PASS_PR626_NEXT_TOUCH_BOUNDARY_AUDIT`. The deterministic
output must equal [EXPECTED.json](EXPECTED.json), including:

| Check | Completed coverage / result |
| --- | --- |
| Controller | All 240 replica events; 160 idle deadlines, including 16 zero-rank deadlines |
| Nonzero pending children | 144 owner-replica/child windows |
| Eligibility | All 10,368 window/call decisions; 2,958 admitted |
| Literal allocation | All 35,424 helpers; 28,404 cross-replica roles |
| Same-block deadlines | All 144 deadline-block calls admitted; 2,736 actual roles use them |
| Wrong-replica diagnostic | Using the borrower's replica rejects 12,614 valid roles |
| Rejection controls | 522 endpoint changes, 144 moved deadlines, 288 inserted bridges (both endpoints), whole-family aliasing, unknown event |
| Omitted literal bridges | All 72 single deletions leave eligibility unchanged |
| Scalar counterexamples | All nine source bridge deletions change the exact eight-wire map; each applies independently to all eight replicas |

The source pins are checked before any computation. Checks remain active
under `-O`. To regenerate a receipt after an intentional code change, use
`--write /absolute/path/to/receipt.json`, then inspect its difference from
the committed receipt. Normal verification writes no files.

## Precise statement and method

For the finite controller and owner table pinned below, every selected
helper role belongs to its owner's pending region strictly between that
region's last data touch and its idle deadline. No two helpers in one
complete invocation own the same physical family, no helper aliases the
active data pair, and their allocated pending coordinate sets are disjoint.

The existing source audit reconstructs last-touch intervals. This checker
instead scans the explicit event stream backward. For each physical
replica/pair it records whether the next relevant event is an idle deadline
or a blocking data touch. A local event blocks its active pair before
sampling admissibility. It then compares the complete Boolean matrix with
the stored windows, and checks every literal owner against that matrix.
It imports no emitter, allocator, original audit, or scalar replay module.
See [REVIEW.md](REVIEW.md) for the induction and conditional timing argument.

Strict event positions cannot be replaced by strict block times. For
owner replica 0, child 0 permits times `{0,1,2}`: its idle event follows the
local call of block 2. The same block's subsequent bridge releases child 1,
whose times are `{3,4,5}`. Actual selected roles exercise both closing
boundaries. The controls move deadlines before calls and insert physical
touches after formerly legal calls; they do not manufacture an impossible
call at the same event position as an idle or bridge.

The bridge-deletion experiment is a scoped counterexample to the inference
“the borrowing windows agree, therefore the scalar controller is correct.”
It is not a counterexample to the selected certificate. In the inherited
normalized eight-wire contract, the full recipe is the identity. Removing
source bridge 3 maps input `(1,0,0,0,0,0,0,0)` to
`(1,0,0,1,0,0,0,0)`. The receipt gives an exact input/output witness for
each of the nine source bridges. Each matrix factor is invertible and each
bridge is nonidentity, so deleting a single bridge from an identity product
cannot preserve that product. This explains why source projection and
scalar checks must accompany a timing certificate.

## Pins, selection and bounded coverage

- Exact main base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Selected at that base: #626 with #543,
  `κ = 51110230636731/31250000000000000 = 0.001635527380375392`.
- Reviewed #626 source: `660de893d27bb7abd1d5b01b1640207528a5c851`.
- All consumed artifacts and semantic reference code: [SOURCES.json](SOURCES.json).
  The inherited archived controller, phases, owner table and plan are bound
  to `research/community-k492-audit/SELECTED-SOURCE.json`. The checker also
  compares the archived controller's recipe, idle children and first 30
  events with the actual frozen558 input installed by `run_complex44.py`.
  It does not identify those full parent templates, whose final bank events
  differ, or pretend to cold-rebuild either supplier.
- Assignment seed **60**, drawn with OS-backed `secrets.randbelow(100)`:
  adversarial audit. It also chooses the legal call used for each inserted
  bridge control by index `60 % len(window)`.
- [CLAIM.json](CLAIM.json) records the three candidates and local claim.
  No pinned coordination issue or open sprint issue was available.
- Stopping rule: finish this finite table, all its window/call combinations,
  all single bridge deletions, and the stated controls; no parameter search,
  supplier optimization, or additional speculative investigation.

## Scope, credit and handoff

This audits a necessary finite interface. It inherits the source supplier
widths, phase/frame identities, exact normalized residual and spectator
restoration, atomic execution, common labels, mutable-basis realization,
full invoice, all-size compiler, precision/tape/exact recovery and analytic
assumptions. It does not re-prove native local programs, price a new
recurrence, establish global optimality, or formally verify multiplication.

Credit: chafreaky's #626 owner repair; jeremykothe2's #622/#623 constructions
and allocations; GamingPuzzled's #620 owner-map lead; DreamingOfClouds and
the earlier supplier lineage; icekylinx's inherited controller/scalar
replays, with their recorded AI assistance. Source notices remain intact.
Rohan Arun's open [#553](https://github.com/CrocSwap/integer-mult-bounds/pull/553)
at `0c3e5ee4719d705afd63fefd001091d70e55182b` already formalizes the historical
PR531 table's 144 strict windows. This contribution adds the current
492-helper data, a separate next-touch implementation, actual closing-block
usage counts, and the paired timing/scalar omission evidence. It claims no
priority for the strict-window principle or eight-wire identity.

All changes are confined to this research package. `upstream/`, the selected
frontier and predecessor implementations remain unchanged. Reviewers can
run the command above and inspect the nine short exact counterexamples;
no expensive supplier replay is needed for this scoped addition.

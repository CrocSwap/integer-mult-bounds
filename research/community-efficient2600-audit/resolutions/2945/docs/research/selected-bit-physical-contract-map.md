# Selected BIT physical caller and ordinary backend contracts

The [caller/storage map](selected-bit-caller-storage-map.md) is a dated logical
caller checkpoint. Later work addresses its physical-reuse, outer-wrapper and
reached-primitive handoffs. Use the contracts below before rebuilding those
components. This successor adds navigation, not a new implementation, proof,
supplier admission or exponent. The [selected record](../../certificates/selected-result.json)
still governs the conditional multiplication result.

Source checkpoint: main `9ee73fecdbae9f892a6496dbdfae872217cf4601`, priority
revision 5, checked 2026-10-16. The [round-1700](community-efficient1700-review.md)
and [round-1900](community-efficient1900-review.md) reviews incorporate
PR2808, PR2899 and PR2915 as scoped research. **PR2809 remains partially
reviewed.** Incorporating a downstream composition does not discharge its
inherited universal caller arguments. Follow the [PR ledger](pr-ledger.md)
for later dispositions and [Discussion 2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319)
for live coordination.

Maintainer update (2026-10-16): PR2809 is now merged as a source-only archive,
with its independent scientific review still open. The top-level
`research/selected-bit-physical-caller` package is available; archival publication
does not discharge the universal dependencies described below.

## Four contracts, not one completed theorem

| Source and author | Published contract | Boundary that remains |
| --- | --- | --- |
| [PR2808, Nick Petalas][2808] | Executable logical ordinary wrapper. Two separately padded calls to a **completed unweighted** reversed caller, with restriction between calls, residual/high exchanges and an added-work invoice. | It assumes that callee and the stock/fit/time contracts. It does not provide the fixed physical caller or stronger H2 primitives. An arbitrary weighted involution is not an interchangeable callee. |
| [PR2809, Jose Manuel / jmbarrancoml][2809] | Fixed-role lowering of David Arias's PR2753 baseline caller C0. Finite macrocode, explicit scratch leases, serialized parent state and CALL/RETURN, parked numerical banks and owned root cleanup. Under its named source/root-coupling arguments, the stated reserve is `O_q(V_root)+F_q`, with local toll `O_q(V(n+w))`. | Mechanism/proof and changed-code review remains pending. It retains baseline linear-in-w routing/leaves. Reduced GL2 programs and selected coefficient junctions are not selected GL64 payload execution or a complete transition-table refinement. |
| [PR2899, Jose Manuel / jmbarrancoml][2899] | Composes those two sources into ordinary backend B1. Encoded parameter selection and minimal templates, unit ROOT parsing, two-call ownership, successful-return erasure and binary rectangle completion. The stated time is `O_q(V E^(1-a1))`, space `O_q(V)+F_q`, where `a1=169711/10^8`. | The quantified statement inherits PR2753/2809 endpoint, chronology, refinement and cost arguments. It covers successful admitted execution, not interrupted-macro recovery. The successor header route was still missing here. |
| [PR2915, Jose Manuel / jmbarrancoml][2915] | Replaces **both** reached leaf/remainder swaps and decorated-key owner routes using B1 and PR2157 factor words. The stated C1 local toll is `O_q(V(n+w^(1-a1)))`; the existing wrapper gives B2 saving `1699995087/10^12`. | Named C0/B1 source arguments remain dependencies. Small complete C1 fixtures use B1's elementary branch; a separate reduced fitted handoff checks that junction. Neither the selected GL64 payload nor a universal formal refinement is executed. |

Here `V` counts the complete Boolean payload of the relevant call, `n` its
atom-pair count, `w` its atom width, and `E` the ordinary binary width. `q` is
fixed in the source-admissible large-prime domain. `F_q` is a fixed compilation
allowance, not fresh row stock. The small q=2/3 fixtures do not instantiate
that large-prime domain. Each source's own ownership and canonical-input
premises govern its bound.

The [PR2899 proof](../../research/physical-ordinary-interchange/PROOF.md) keeps
the elementary routine A0 inside C0 while constructing B1 around C0.
The [PR2915 proof](../../research/selected-bit-fast-primitives/PROOF.md) then
uses the dependency order `C1 -> B1 -> C0 -> A0`. It restores both preceding
primitive bindings during nested B1 calls. Substituting only a leaf or only
an older imported alias does not implement this composition. In particular,
PR2753's decorated-key route does not reach PR2399's older `ordinary_fields`
hook. The second reached replacement is necessary to remove that route's
`O(wV)` charge.

## Where the next implementation boundary moved

PR2915's [consumer comparison](../../research/selected-bit-fast-primitives/PROOF.md#8-evidence-selected-consumer-and-stopping-decision)
shows that B1 already exceeds the ordinary rate required by the selected
complex consumer. B2's stronger rate does not improve the present
complex-limited frontier. Do not substitute a1 into the convenience assembler's
`complex_above_bit` check, which expects the opposite ordering. Another
ordinary-stage speedup is not the missing current-consumer implication.

The [PR2250 compact adapters](../../research/selected-complex-compact-adapters/README.md)
need a completed binary interchange with preserved borrowed input, arbitrary
complete spectators, a distinct owned output and cleanup before port reuse.
A matching exponent alone does not bind those interfaces. Their original
implementation uses host-integer controls. The [encoded compact-operation
claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2238#discussioncomment-18971213)
addresses encoded controls, fixed roles, B1 output transfer and complete
outer-row repair. At this check it reports LOCAL-ONLY analysis, not a public
completed artifact. Recheck its status before taking that scope. A single
completed compact operation would still leave complex recursion, actual owner
packets/lifetimes, DATA-PHASES translations and numerical precision to compose.

The earlier storage map's separate backing/live-content results remain useful
for independent source audits. This page does not add their maxima to claim
a total physical reserve, or treat a downstream reserve assertion as their
independent verification.

## Exact sources and replay coverage

| PR | Pinned author/review head | Replay package under `research/` |
| --- | --- | --- |
| 2808 | `b00b58e0db823643364f705b530faac254e7b05b` | `selected-outer-borrowing-wrapper` |
| 2809 | `e7d93dd0de0bb81308bc3356f65eddeeb22fd712` | `selected-bit-physical-caller`, now available as a top-level source-only archive; authenticated predecessor archive in PR2899 |
| 2899 | `2f0911ad735643a069b9790302fbf179e49f74f8` | `physical-ordinary-interchange` |
| 2915 | `fecc5a87574df441ddc3dad44f99fca9bd7fdd92` | `selected-bit-fast-primitives` |

The source links identify the exact contracts. Main retains an explicit
catalogue-cache lifetime adaptation for PR2915, documented in its
[maintainer replay receipt](../../research/community-efficient1900-audit/checks/check-2915.json).
That receipt records all eight passing suites and preserves the original
[resource-limited attempt](../../research/community-efficient1900-audit/checks/check-2915-original-resource-stop.json)
separately. Do not describe main's adapted checker as byte-identical to the
author head, or replay success as closure of PR2809's pending review.

From this main checkpoint, use standard-library Python 3.12:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/physical-ordinary-interchange
python3.12 -Werror -B scripts/research_package.py --package research/selected-bit-fast-primitives
```

Contributor-reported checks on Linux x86_64 / WSL2, CPython 3.12.15
(retained as author evidence; the maintainer navigation review did not rerun these scientific workloads):

- Metadata/source-pin checks passed for PR2808, PR2899 and PR2915's installed
  packages. The four immutable README links and review-head/status bindings
  were checked against Git objects and the retained dispositions.
- PR2899's complete eight-command registered replay passed in 221.680 seconds,
  matching its saved typed receipts, including normal/optimized controls.
- PR2915's registered run passed `kernels`, `routes`, `catalogue`, `handoff`
  and `caller`, then timed out in `complete` at its unchanged 600-second
  limit. `outer` and optimized `controls` subsequently passed separately in
  fresh bytecode namespaces. A complete Linux replay is **not** claimed.
- All six existing current-status/navigation tests passed. All 33 local links
  across the three changed documents resolve, including the new section anchor.
  The earlier caller/storage snapshot from its dated marker onward and the
  selected record remain byte-identical.

These are source-bound finite replays and navigation checks, not independent
proofs of the parametric arguments. The retained maintainer pass and this
incomplete Linux run are different evidence. No full selected cold replay,
formal-kernel check, hosted CI result or new physical/theorem admission is
supplied here.

## Open next questions

1. Bind B1 to the actual complex compact operation, rather than repeating a
   rate substitution. Start with the linked encoded-operation claim and one
   complete earlier/later-source rectangle. Preserved borrowed inputs, output
   ownership/erasure, dirty fields, complete outer rows and paid preparation
   are the discriminating obligations. A completed operation does not supply
   the whole complex caller.
2. Independently audit PR2809's universal refinement dependency. Start with
   opcode/source correspondence, lease-end annotations and CALL invariants at
   its exact head. This matters because downstream scoped incorporation does
   not complete that pending review. Reduced fixtures cannot settle the
   selected GL64 or all-size claims.

## Scope and credit

Task `scope-navigation`, refined to this post-logical caller handoff; chooser
nonce `bf17c9e321658790056dc6892ca28931`, scope key `b18e0e173a4430a9564b`.
The historical caller/storage snapshot and all frozen sources are preserved.
No construction-family expansion is proposed. Initial overlap covered 473 open
PRs, 2,159 closed PRs and 1,634 Discussion records with complete pagination and
no warnings. The search does not cover every code diff or unpublished result.
The pre-submission refresh at 2026-10-16 13:33 UTC covered 473 open PRs, 2,162
closed PRs and 1,636 Discussion records, again complete with no warnings.
Canonical main was `95ff4e2dd396c505932a43ff7c1cdfdd94b8c867`. Guidance,
priority revision, selected record, both replay packages and the four scoped
dispositions were unchanged; unrelated review additions do not change these
source pins. The encoded-operation claim still reported LOCAL-ONLY analysis.

Jose Manuel/jmbarrancoml supplied PR2809/2899/2915 and the PR2250 compact
adapters. David Arias supplied PR2753. Nick Petalas supplied PR2808 and the
earlier caller/storage map. Retain ywz65's parking controller, commdata2338's
substitution algebra, Aakash Thakkar's stock-fit proof, Sagar Thakrar's stock
audit, PR2157's factor words and the selected PR589/PR555/source527 lineage
credited in the source packages. This contribution adds navigation and the
scoped replay record only. Nick Petalas. Apache-2.0.

[2808]: https://github.com/CrocSwap/integer-mult-bounds/blob/b00b58e0db823643364f705b530faac254e7b05b/research/selected-outer-borrowing-wrapper/README.md
[2809]: https://github.com/CrocSwap/integer-mult-bounds/blob/e7d93dd0de0bb81308bc3356f65eddeeb22fd712/research/selected-bit-physical-caller/README.md
[2899]: https://github.com/CrocSwap/integer-mult-bounds/blob/2f0911ad735643a069b9790302fbf179e49f74f8/research/physical-ordinary-interchange/README.md
[2915]: https://github.com/CrocSwap/integer-mult-bounds/blob/fecc5a87574df441ddc3dad44f99fca9bd7fdd92/research/selected-bit-fast-primitives/README.md

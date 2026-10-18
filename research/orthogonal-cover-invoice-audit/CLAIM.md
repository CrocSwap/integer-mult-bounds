# Sprint claim — seed 65

- Track: adversarial mathematical audit (60–74).
- OS-random assignment seed: **65**, from `secrets.randbelow(100)` at
  2026-10-13 05:09:06 UTC (2026-10-12 22:09 PDT).
- Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Branch: `codex/orthogonal-cover-invoice-seed65`.
- Budget: 60 minutes, with the final 15 minutes reserved for verification
  and handoff; expected finish 2026-10-13 06:09 UTC (October 12, 23:09 PDT).

## Three narrow candidates

0. Cold-helper compensation admission in the selected #626 source; deferred
   because #702 and #729 already cover related wrapper/frame obligations.
1. Arbitrary private-center restoration in a selected scalar orientation;
   deferred because #734/#745 already cover it by distinct forward/reverse methods.
2. The order of the binary dot-product isometry group used in #626's finite
   routing invoice, and the propagation of its multiplicity into finite guards.

The seed selects candidate `65 % 3 = 2`. The other candidates are already
crowded. The chosen mathematical object is the *bilinear* dot-product group,
not a quadratic-form orthogonal group; in odd dimension its characteristic
vector splits off and the complement is symplectic.

## Exact scope and method

Audit the group factor in `code/invoice_allcold.py` and `code/assemble.py`
of `research/complex-k492-owner-repair`, bound to the reviewed #626 invoice.
Derive the odd-dimensional order by counting symplectic bases; independently
count complete binary orthonormal bases in dimensions 1 through 7 without
using that formula. Recompute the group-dependent finite guards with integer
arithmetic, and supply controls for a wrong group family or missing cover
multiplicity. No new kappa, search for a new supplier, or selected-frontier
edit is planned. Expected deliverable: a scoped proof, exact certificate,
standalone verifier, source pins and meaningful negative controls.

## Coordination and overlap

GitHub reports no pinned issues; the sole open issue is #650 (Discussions),
so this is the local claim. No separate reservation issue was opened.
The full open queue was inspected (578 PRs), then latest arrivals through
#762 were checked immediately before this claim. #717 studies moment/invoice
sensitivity and pair-preserving program permutations, not the ambient cover
cardinality and finite routing guards. Its scope was inspected. The selected
review and prior negative-results index were read; no closed supplier search
is reopened here. No pending PR supplies code or inputs to this audit.

## Completed result and final overlap check

The group factor and all nine finite invoice guards are corroborated.
Exhaustive basis enumeration covers dimensions 1–7. Five wrong-order controls
are rejected explicitly; four undercounts still pass every upper-bound guard,
whereas using GL(73,2) violates the row cap. Exact cover-only inflation reaches
its first failed guard at a factor of 2^1847. No construction defect or new
kappa is claimed. See README.md, CERTIFICATE.json and VALIDATION.json.

The final full-queue check covered 586 open PRs through #767, followed by
an immediate pre-submission latest-arrival check through #769; no ambient
cover-cardinality audit was found. #717 remains distinct (moment/invoice
sensitivity and finite program permutations). Upstream main is still the
recorded base. No coordination issue exists, so the result is recorded locally.

Submitted: https://github.com/CrocSwap/integer-mult-bounds/pull/771
Completion recorded: 2026-10-13 05:24:47 UTC.
The contribution finished early; verification and packaging occupied the final
portion of the session. No work remains on the claimed mathematical scope.

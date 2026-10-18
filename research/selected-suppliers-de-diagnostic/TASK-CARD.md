# Local task card (autoresearch.md section 3)

Task ID / proposed scope key: `independent-moment` / `c6f2494b197df3bc3591`
(draw: track `independent-verification`, chooser seed
`9246ead964f301161b3d7eec63704082`, OS-random assignment; refined below to the
card's "certified enclosure with a different method" variation).

Base commit; exact predecessor and dependency heads:
`dadfea6e8a78ff6ba901705f87532a71c6f5bbb8` (origin/main at entry).
Selected record `certificates/selected-result.json`
(sha256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`);
selected assembly `research/community-frontier1094-audit/ASSEMBLY.json`
(sha256 `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`);
bit supplier pin `research/e8-bit-p111-tuned/tune/EXPECTED.json`
(git blob `e293ddc557742637f9f679f083a1a282d87b1b13`, as recorded inside the
selected assembly's `bit_supplier` block).

Concrete object and question:
The two supplier ledgers of the selected record: the complex k8/T16 gauge44
hosted profile (`complex_profile` in ASSEMBLY.json, width m = 73, live stock
W = 14,336, calls N = 144) and the bit PR589 p111-tuned nine-stage profile
(`nine.profile` / `nine.bit.live` in EXPECTED.json, width m = 64, W = 28,416,
bad-residue surcharge). Question: (1) can the recorded moment acceptance at the
two certified endpoints be reproduced by a genuinely independent exact
implementation; (2) what does the prescribed small-saving diagnostic
`a < D/E` give exactly for each ledger, and is the inequality actually implied
by the priced moment?

Scope status: refined. The card's question and method are unchanged
("certified moment inequalities through a different exact enclosure method");
the refinement names the two ledgers, the endpoints, the widths/stocks and the
diagnostic. The earlier note that the endpoint-moment card was already covered
by three code-disjoint engines (Mercator, base-two, atanh prime chain) is why
this session does not add a fourth series engine: the log enclosure here is by
rational square-root bisection, the new content is the `a < D/E` lemma and its
application, and the bit ledger is included (the packing ceiling of
https://github.com/CrocSwap/integer-mult-bounds/pull/1240 covers the complex
local word only).

Existing restriction being changed (or exact claim being audited):
None changed. Audited claims: the ASSEMBLY `moments` accept/reject decisions at
the complex and bit endpoints (and their next 1e-24 grid points), the ledger
aggregates `rank_mass`/deficit and their coverage identities, and the
`a < D/E` diagnostic asserted in autoresearch.md section 2 without an in-repo
proof.

Method; explicit parameter ranges/candidate alphabet:
Stdlib-only exact rationals plus outward-rounded dyadic interval arithmetic at
2^-320. ln by rational square-root bisection (x^(1/2^k) by squaring bisection,
ln(1+u) bracketed by u - u^2/2 <= ln(1+u) <= u); cross-checked against an
independent alternating Leibniz enclosure. exp by Taylor partial sums with an
explicit rational tail bound. Parameters are the fixed ledgers above; the only
free integer is the bisection depth (k = 32) and Taylor order (48), both
checked to move intervals by far less than 2^-200. No search domain.

Nearest overlapping PRs and why this adds something:
https://github.com/CrocSwap/integer-mult-bounds/pull/1240 (complex local-word
packing ceiling via idle-mass optimization; no bit side, no D/E lemma),
research/pending-claims-independent-pricing (atanh prime-chain endpoint
certification for pending claims) and
research/community-batch970-audit/submitted/957/.../audit_endpoint_reduction.py
(Mercator/base-two endpoint audit, PR957 lineage). None of them proves or
computes the `a < D/E` diagnostic or covers the bit ledger's D/E.

Optimistic full cost budget; required observable improvement:
Budget ~60 minutes total with the last quarter for verification and handoff;
no kappa change is possible or claimed (this is verification/diagnostic work).
Required observable: independent residual intervals agreeing with the recorded
ASSEMBLY residuals and the same accept/reject signs, certified D/E bounds on
both ledgers, and every semantic failure control rejected.

Success evidence; falsification test; time/compute cap:
Success = verify.py prints PASS with (i) both moment residuals negative at the
recorded endpoints and positive at the next grid point, (ii) exact ledger
identities reproduced, (iii) certified a* < D/E intervals containing decimal
cross-checks. Falsification = the smallest failing instance: the sign flip of
the residual at the next grid point, or any mutated ledger that is not
rejected. Compute cap: seconds per run, stdlib only.

Predecessor authors; intended artifact and reproduction command:
Predecessors: Douglas Colkitt (repository pricing model, autoresearch
diagnostic), Rohan Arun (#1094 complex ledger), the PR 589 by DreamingOfClouds /
PR 555 / PR 543 by eumemic bit supplier lineage (with their credited
predecessors, retained unchanged by the selected record), Sagar Thakrar and
Josie Elliston (independent audits), Jeremy Kothe (packing chain),
static44/PR525/PR643 and the author of
https://github.com/CrocSwap/integer-mult-bounds/pull/1240 (packing-ceiling
lineage). Artifact: `research/selected-suppliers-de-diagnostic/`.
Command: `python3 -B research/selected-suppliers-de-diagnostic/verify.py`.

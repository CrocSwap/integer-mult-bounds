# CLAIM — kappa-blocker KB3: the sharp singleton f(7) gap

Agent: **Aaron Wang**, with help from opencode (substantial AI assistance; no
independent human review claimed). Base main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; priority revision 4; catalogue
SHA-256 `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`;
selected-record SHA-256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. Posted
claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18947532

## Object and scope change

In the PR943 prefix-walk model (`research/universal-connector-boundary`), a
restored source word `w` over `n` singleton labels is universal when paired
readouts realize every mask, `D(w) = {q_s xor q_t} = F2^n`; `f(n)` is the
minimum word length. The pinned record is `f(5) = 12`, `f(6) = 16`,
`18 <= f(7) <= 24` (`research/universal-connector-six-source/README.md`: "The
exact value of `f(7)` is open"). This package decides or narrows that gap in
the singleton alphabet only.

**Scope status: changed** (authorized explicit-open-request scope change to the
assigned kappa-blocker KB3; drawn track `adversarial-audit`, chooser seed
`b859517b2b08394033ce4a4ab231ece8`). The drawn cards
(`selected-stock-envelope`, `uniform-transfer-audit`,
`supplier-boundary-audit`) are saturated or incremental at this base — the last
two were completed within hours (discussion 1166 comments 18939154/18939459 and
18939803/18940382). The distinct scopes of the DUO pair-source alphabet
(https://github.com/CrocSwap/integer-mult-bounds/pull/2396,
https://github.com/CrocSwap/integer-mult-bounds/pull/2128,
https://github.com/CrocSwap/integer-mult-bounds/pull/2156) and the 63-mask
weight-1/2/3 sparse family
(https://github.com/CrocSwap/integer-mult-bounds/pull/2229,
https://github.com/CrocSwap/integer-mult-bounds/pull/2236,
https://github.com/CrocSwap/integer-mult-bounds/pull/2397) are recorded as
concurrent scopes in `SOURCES.json`, not collisions.

## Method

Smallest falsifying instance first: the engine must reproduce the pinned
five-source length-10 census (945 words, max 31/32) and six-source
length-12/14 censuses (10,395 words, max 49/64; 945,945 words, max 59/64)
byte-for-byte, including records SHA-256, before any new number is trusted.

Then the length-18 census at `n = 7`, via the prefix vertex set `P = E union O`
(`E` even-weight prefixes, `O` odd-weight prefixes; universality is exactly
`P + P = F2^7`):

1. Position parity gives `|E|, |O| <= 9`; counting gives `|E||O| >= 64` and
   `C(|E|,2) + C(|O|,2) >= 63`.
2. **Lemma A (pair-representation identity).** Every surviving 17-point split
   `(9,8)` and `(8,9)` is contradictory: full odd coverage with 72 pairs forces
   `sum_x A_x B_x >= 4`, while full even coverage forces at most one shared
   nonzero pair-sum value, bounding the same sum by 1. Machine-checked rows are
   in `CERTIFICATE.json`; an independent multiset enumeration re-derives them.
   (The same lemma explains the community census fact that no nine-point set of
   `F2^5` covers, max 29.)
3. So a universal 18-word would walk a simple 18-cycle through an 18-point
   cover with the `(9,9)` split. The joint `(E,O)` search enumerates every such
   cover (increasing-order generation, exact 64-bit bitmasks, collision-budget
   and coverage-capacity pruning — each prune a proved necessary condition),
   and every cover found is tested for a Hamiltonian 18-cycle in the induced
   hypercube.

Controls and non-vacuity: the same joint search is validated at `n = 5` against
a brute-force census of all C(31,9) ten-point sets (exact agreement on the
number of covers) and reproduces the community nine-point result; `f(5) = 12`
is re-confirmed by showing no ten-point cover is cycle-realisable.

## Deliverable

Either an exact length-18 exclusion (`f(7) >= 20`) or a universal word of
length below 24 (`f(7) <= 22` or `20`), with exact coverage verification either
way. No kappa, supplier or selected-frontier claim. One bounded pivot maximum
(a length-20/22 construction screen on the same set engine) if the length-18
census completes negative inside the priced budget.

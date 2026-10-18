# Task card - KB3f: press the vanishing-character restriction against the four surviving 18-point splits

```text
Task ID / proposed scope key: kappa-blocker KB3f / scope key 4e44f2900cd2a6a3003d
  (deterministic: sha256("fc618722a84313d16975dd03a0d68449:kb3f-vanishing")[:20];
  chooser OS nonce fc618722a84313d16975dd03a0d68449, track recursive-interfaces)

Base commit; exact predecessor and dependency heads (verified with `gh pr view
NNN --json author,title` against current ground truth at entry, 2026-10-16):
  base commit f646a7fb75f7d854a881e07fefb13fdfe7631c86
  PR 2542 (Aaron Wang) head 3b6011d2400f50ab0ad9e105c7c55a18f3cef4cf
  PR 2634 (Aaron Wang) head e2f30d93efbef5658334072aa855aa95e795e394
  PR 2773 (Aaron Wang) head 6739c799799621878a9249c93e2b12cc799c1482
  PR 2870 (Aaron Wang) head 9f55f291e9e79e628fd98f1e4f4debfc1c2106e5 (MERGED)
  PR 2911 (Aaron Wang) head cfb813f883e61519deedcd84151dc0c68b9d19cc
  PR 2691 (Nicholas Stone) head 88dda3534071442773106e9c0b941b9d39a3cea8
  (recorded state only; concurrent L=20 WORD census, different object)

Concrete object and question:
  The set-level 18-point cover question for F2^7 (PR943 prefix-walk model:
  P + P = F2^7). PR 2911 narrowed it to four surviving parity splits
  (12,6), (11,7), (10,8), (9,9) (+ mirrors) and PROVED: any (12,6) or (10,8)
  cover must have a vanishing character off the all-ones hyperplane (the
  no-vanishing sub-case forces sum rho^2 = 46 at (12,6), unattainable; at
  (10,8) the parity/integrality fails). Question here: PRESS THAT RESTRICTION -
  classify the vanishing-character configurations (which characters can
  vanish, what half-decomposition structure that forces on A and B in the
  (A, D) reduction in E = F2^6, and whether coverage of the remaining masks
  survives), and try one exact contradiction per class to exclude (12,6) and
  (10,8); then, if those hold, extend the classification to (11,7)/(9,9)
  (where no character can vanish at all - both sides odd - so those splits
  need a different identity). Outcome sought: settle or further narrow the
  four splits; a covering 18-set in any split is a complete result.

Scope status: changed (authorized "explicit open request" scope change).
  Reason: the assignment takes the explicit open request from discussion 1166
  (PR 2911's open questions 1 and 2 - the vanishing-character route) instead
  of the drawn card. The chooser (seed fc618722a84313d16975dd03a0d68449,
  track recursive-interfaces) drew the card centre-path-sharing (scope key
  a55534776f5479f1686c) plus two neighbors (coverage-law-change,
  connector-alphabet-change); all three are saturated cards for this object
  (they target the selected word's centre path / coverage identity / connector
  alphabet, not the F2^7 cover question), which the assignment records as the
  reason for taking the assigned request.

Existing restriction being changed (or exact claim being audited):
  PR 2911's PROVEN vanishing-character restriction on (12,6)/(10,8) is being
  exploited, not changed; PR 2911's own open question 2 ("does combining the
  forced vanishings with the even-half multiplicities exclude (12,6) outright?")
  is the target. PR 2911's profile system's step cap and its feasible profile
  counts (16/22/50/31 spectra) are reproduced first.

Method; explicit parameter ranges/candidate alphabet:
  Exact integer arithmetic only (no floats). (1) Reproduce every recorded
  anchor before any new number (PR 2542/2634 REPRO tiers; PR 2542 L=18 census;
  PR 2870 OBSTRUCTION parseval=696 allowed=504 deficit=192; PR 2911 ROWS18
  808/501/251/196 and NOVANISH lines; PR 2773 k10 budget-3 = 149,990,400 and
  k11 levels 3-4 = 0/0 re-walked from EMPTY receipts in resumable sharded
  jobs). (2) Vanishing-classification layer: for splits (12,6)/(10,8) in the
  (A, D) reduction (A, D subsets of E = F2^6, |A| = s, |D| = t, A + D = E,
  (A+A) u (D+D) = E), classify configurations with a vanishing character psi
  (A-halves of size s/2 across ker(psi); D-halves d0/d1), derive the exact
  half-decomposition constraints per class (odd half excess 4+4 at (12,6),
  even half E1 coverage (A0+A1) u (D0+D1) = E1), and decide each class by
  exact enumeration where the class space is finite and small (halved
  F2^5 subproblems, profile shapes with zero columns plus the even-half
  multiplicity layer). Ground truth at the smallest instances: exhaustive
  classification of all covers of F2^4 and of the 99,200 recorded F2^5
  ten-point covers by vanishing type. (3) One bounded pivot max: structured
  seeded search restricted to one vanishing class ((12,6), A-split 6/6 across
  a fixed hyperplane) - the smallest falsifying instance for a class
  contradiction is a covering pair (A, D) in that class.

Nearest overlapping PRs and why this adds something:
  PR 2911 (Aaron Wang) - the immediate predecessor; narrows the question,
  proves the vanishing restriction; its open questions 1-2 name exactly this
  next step ("add the even-half multiplicity constraints as a second layer and
  enumerate the joint profiles"; "blocked by: nothing structural"). This
  package executes that named step and classifies the vanishings; it does not
  re-run PR 2911's search or row machinery as new results.
  PR 2870 (Aaron Wang) - the odd-coverage Fourier/Parseval identity (vendored
  byte-exact with SHA-256 pins, credited).
  PR 2773 (Aaron Wang) - pair-representation rows and the census floors whose
  anchors are re-walked here.
  PR 2691 (Nicholas Stone) - the (10,10) L=20 WORD census (recorded state
  only; different object - this package stays strictly on the SET level).

Declared milestone: local module (a scoped set-level obstruction or narrowed
  remainder; no supplier, tariff, certificate or selected-frontier change).

Optimistic full cost budget; required observable improvement:
  Budget ~210 minutes total; the required observable is a labelled
  split-by-split verdict (PROVEN / CHECKED / DEMOTED) with exact integers and
  machine-checked classification counts, i.e. either class contradictions
  excluding (12,6) and/or (10,8), or the exact surviving vanishing classes
  recorded as the narrowed remainder.

Unresolved consumer/restoration costs; family expansion decision if continuing:
  Not applicable: a finite set-level question in the PR943 query model; no
  consumer, restoration or physical interface is priced and no family
  expansion is claimed. The f(7) gap 20 <= f(7) <= 24 is unchanged unless an
  18-point cover is constructed (which keeps L = 22 alive) or all splits are
  excluded (which kills L = 22).

# Local task card — KB3e: the 18-point cover question for F2^7

Task ID / proposed scope key: `f7-18point-cover-question` (scope key drawn
`eee4a5467dd91c47ef45` etc. not used; see scope change).

Base commit; exact predecessor and dependency heads:
- Base commit: `ffbd90dd90dbe0055464f3a1411b25a3a4fdc6b8` (origin/main at draw).
- Predecessor PR 2542 (Aaron Wang) head `3b6011d2400f50ab0ad9e105c7c55a18f3cef4cf`,
  package `research/universal-f7-singleton-seedb859517b`.
- Predecessor PR 2634 (Aaron Wang) head `e2f30d93efbef5658334072aa855aa95e795e394`,
  package `research/universal-f7-singleton-l20-seed06704c39`.
- Predecessor PR 2773 (Aaron Wang) head `6739c799799621878a9249c93e2b12cc799c1482`,
  package `research/f7-17point-cover-audit-seedcfa215c2`.
- Predecessor PR 2870 (Aaron Wang) heads `88426cc42` + `9f55f291e9e79e628fd98f1e4f4debfc1c2106e5`,
  package `research/f7-17point-fourier-obstruction-seedb5e318fe`.
- PR 2691 (Nicholas Stone) recorded state only (the (10,10) word census).

Concrete object and question:
In the PR943 prefix-walk model, a prefix set `P` covers `F2^7` when
`P + P = F2^7` (pair-sums `a + b` of elements of the set, self-pairs covering
mask 0; every mask of F2^7 is a pair-sum or a self-sum). Question: does any
**18-point** set `S` cover `F2^7`? Parity splits `(|A|, |B|)` with `A` in the
even coset `E` and `B` in the odd coset `O`, `|A| + |B| = 18`: (12,6), (11,7),
(10,8), (9,9) and the mirror orders (6,12), (7,11), (8,10).

Scope status: **changed** — authorized explicit open request (kappa-blocker
KB3e), recorded in TASK.json. Reason: the drawn card (chooser OS nonce
`6d34356c3c96fdb981b4f20ddfa06b07`, track `adversarial-audit`, cards
`selected-stock-envelope` / `supplier-boundary-audit` / `uniform-transfer-audit`)
is saturated / off-object; the assignment is the immediate successor of the
now-complete 17-point question (KB3b/KB3c/KB3d chain, PR 2542 + PR 2634 +
PR 2773 + PR 2870) and the deciding set-level object for the f(7) L=22 route.

Existing restriction being changed (or exact claim being audited):
PR 2870's open question 1 ("Do 18-point or 19-point covers of F2^7 exist?"),
and PR 2773's open question 3 (tabulate the odd-coverage Fourier obstruction
over the counting-feasible splits).

Method; explicit parameter ranges/candidate alphabet:
1. Reproduce every recorded anchor before new numbers (PR 2870 OBSTRUCTION
   parseval=696 allowed=504 deficit=192; PR 2773 k10 budget-3 = 149,990,400 and
   k11 levels 3-4 = 0; PR 2542/2634 REPRO tiers 945/31, 10395/49, 945945/59 and
   the L18 census 15,775,992 / 312,064 / 0).
2. Re-derive the odd-coverage Fourier/Parseval identity for the four
   counting-feasible 18-point splits (12,6), (11,7), (10,8), (9,9) and track the
   deficit exactly (remainder vs allowed character squares per split).
3. Extend PR 2773's pair-representation row machinery (`sharp_rows`) to the
   four splits and demote rows with the reproduced census floors
   (floor(10) = 3, floor(11) = 5; counting floor(12) = 3; Sidon floors 6-9 = 0).
4. Smallest falsifying instance first: a bounded construction search for an
   18-point cover (search falsifying "no 18-point cover exists"), using the
   exact (A,D) reduction of each split to F2^6 and the vendored enumeration
   primitives; exact verification of any candidate; one bounded pivot maximum.
All arithmetic exact integers. Alphabet: F2^7 masks 0..127, sets up to
translation (WLOG 0 in S).

Nearest overlapping PRs and why this adds something:
PR 2542/2634/2773/2870 (Aaron Wang) close the 17-point question; none treats
18-point sets. PR 2691 (Nicholas Stone) is the word-level L=20 repeated-state
census with splits (10,9)/(10,8),(9,9) — his WORD object; this card stays on
the SET-level question (pair-collision check 2026-10-16 07:10 UTC: no CLAIM on
the 18-point set object in discussions 1317/1166).

Declared milestone: audit / scoped obstruction (set level; no words enumerated).

Optimistic full cost budget; required observable improvement:
Reproduction ~70 min of single-core census (sharded, resumable); new
computation bounded. Required observable: a decided split (excluded or
constructed) or a finite row remainder per split with exact obstructions.

Unresolved consumer/restoration costs; family expansion decision if continuing:
none at this level (set-level abstraction inside PR943's interface; word-level
walk realizability and L=22 consequences are separate obligations).

Success evidence; falsification test; time/compute cap:
Success = PROVEN exclusion of at least one 18-point split, or an explicit
verified 18-point cover, or outcome=partial with every surviving split's exact
obstruction recorded. Falsification of any new claim = the smallest exact
counterexample (a covering set for a claimed-impossible split). Cap: one
session; heavy anchors sharded to <=600 s blocking jobs with receipts.

Predecessor authors; intended artifact and reproduction command:
Predecessors PR 2542/2634/2773/2870 by Aaron Wang (navinor); PR 943 by Ross
Richardson (prefix-walk model); PR 1185 by Doug Colkitt (pinned f(5)=12,
f(6)=16 record). Artifact: `research/f7-18point-cover-question-seed6d34356c/`
with `verify.py` replay markers.

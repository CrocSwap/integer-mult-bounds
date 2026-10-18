# Local task card - KB3h (written before substantial computation)

Task ID / proposed scope key: kappa-blocker KB3h; drawn scope key c191650c0fa8d2fa514e
(independent-moment), refined object key f7-18point-avtail.

Base commit; exact predecessor and dependency heads:
- Base commit (frozen assignment pin): `1c1de259ec4313da3a3279fd84a748bcee2d2d25`
  (= origin/main of CrocSwap/integer-mult-bounds at worktree creation).
- Predecessor heads (verified at writing with `gh pr view NNN --json author,title`
  and `--json headRefOid`): PR 2961 head `df2eba6c6c3dcc88b49b3b9a9c9c2e710710d7fd`
  (OPEN, not merged), PR 2933 head `25ea0e94250444db9ab05c3c8f1a66ba68e737b6`,
  PR 2911 head `cfb813f883e61519deedcd84151dc0c68b9d19cc`,
  PR 2870 head `9f55f291e9e79e628fd98f1e4f4debfc1c2106e5`,
  PR 2773 head `6739c799799621878a9249c93e2b12cc799c1482`,
  PR 2542 head `3b6011d2400f50ab0ad9e105c7c55a18f3cef4cf`,
  PR 2634 head `e2f30d93efbef5658334072aa855aa95e795e394`,
  PR 2691 head `88dda3534071442773106e9c0b941b9d39a3cea8` (Nicholas Stone).

Concrete object and question:
The shrinking remainder of the 18-point cover question for F2^7 (PR943 prefix-walk
model: a restored seven-source singleton word is universal exactly when its prefix
set P covers, P + P = F2^7; PR 2911 reduction: with D = p + B inside E = F2^6 the
pair (A, D) covers iff A + D = E and (A+A) u (D+D) = E). PR 2961 PROVEN impossible:
(10,8) A-vanish (7,1), (10,8) D-vanish (8,2), (12,6) A-vanish (6,0); it recorded
the remainder this task takes. Questions, smallest first:
(a) kill or classify (12,6) A-vanish (5,1), (4,2), (3,3) - the classes PR 2933
    recorded at floors 41/44/45 >= 32, where (6,0)'s full-sumset rigidity
    (A0+A1 = F2^5) does not extend;
(b) sharpen the (11,7)/(9,9) identity gap (row remainders 501/196; both sides odd,
    no vanishing character; PR 2961's sum-rho^2 >= 17/19 conditions do not
    contradict) - the bounded pivot, only after (a) is decided or stalls;
(c) opportunistically: any covering 18-set in any surviving split (keeps the
    f(7) L = 22 route alive). Honest search limits; a failed search is not an
    exclusion.

Scope status: changed (authorized "explicit open request" scope change, recorded
in TASK.json with this reason). The chooser (OS seed
`010d26faeebc345503e833f0ed63d7bd`, track independent-verification) drew the cards
independent-moment / formal-interface-lemma; neither targets the F2^7 cover
question. The assignment explicitly authorizes taking discussion 1166's open
request instead - the recorded remainder of PR 2961 (KB3g). Pair-collision checks
(entry + refined, discussions 1317 and 1166 via agent_tools.py disc-comments
--grep incl. nested replies) found no claim on this object; Nicholas Stone's
active claim (discussion 1166 comment 18954844) is the f(7) L=20/repeated-state
WORD census and this task stays strictly on the SET level.

Existing restriction being changed (or exact claim being audited):
Extends PR 2961's decision of the three tightest classes to the surviving
non-tight (12,6) A-vanish classes; audits no prior claim negatively - every
predecessor number is reproduced before new numbers (anchors: PR 2870 OBSTRUCTION
696/504/192, PR 2911 ROWS18 808/501/251/196, PR 2933 CLASSIFY lines incl. the
32=32 TIGHT cases=6720, PR 2961 FOURIER (7,1) need=175 lower=239, CLASS82
checked=28,815,360 covering=0, CLASS60 d_checked=169,911 d_with_transversals=0).

Method; explicit parameter ranges/candidate alphabet:
Exact integer arithmetic only (Python int bitmasks over F2^5 = {0..31}; no floats).
Class (5,1): exact reduction to three F2^5 sets (U, V 6-sets, W 5-set, lines
(a) V u (U+W) = F2^5, (b) U u (V+W) = F2^5, (c) (U+V) u W = F2^5,
(d) selfsum(U) u selfsum(V) u selfsum(W) u {0} = F2^5; WLOG 0 in V, 0 in W by
half-translations), then a complete D-side walk over all C(31,4) = 31,465
normalized W, per W the complete near-transversal family
G(W) = {6-sets U : |U+W| >= 26} (branch-on-uncovered search, PR 2961's
transversals6 extended with slack), and exact pair tests over G(W) x G(W)_0.
Classes (4,2)/(3,3): the right per-class structure (same four L3 lines with
D1 = {0,1} resp. a 3-set), or an exact narrowed classification if the walk does
not close in budget. Positive controls before any m=5 number: the identical
reduction + walk machinery at m=4 against a direct complete census of the
analogue class (702,464 brute-force configurations), and branch-vs-brute
equality of G(W) on sampled m=5 W. Failure controls: line-checker mutants must
change census results (semantic failure control).

Nearest overlapping PRs and why this adds something:
PR 2961 (Aaron Wang) decided the tight classes and recorded this exact remainder
(its open question 1: "Decide the surviving non-tight classes of (12,6) and
(10,8)"; this task takes the (12,6) half, smallest class first). PR 2933
(Aaron Wang) classified the vanishing configurations and recorded the class
floors 41/44/45. PR 2911 (Aaron Wang) proved the forced-vanishing premise and
the row remainders. No other open PR works these classes (overlap survey
2026-10-16: 40 matches, all predecessor lineage or the distinct word-level
L=20 work).

Declared milestone: local module (a scoped set-level decision/classification
inside the PR943 abstract interface; no supplier, tariff or kappa).

Optimistic full cost budget; required observable improvement: see
TASK.json priced_budget_breakdown. Required observable: each named class
decided (PROVEN impossible / realized / exactly classified) or an exact
obstruction recorded per class.

Unresolved consumer/restoration costs; family expansion decision if continuing:
None at this level - the set-level question feeds the word-level L=22 route but
walk-realizability of any cover remains separate (and is Nicholas Stone's
word-level object at L = 20). No family expansion; no kappa change.

Success evidence; falsification test; time/compute cap:
Success = class-by-class verdict with PROVEN/CHECKED labels and exact numbers,
plus reproduced anchors. Falsification of "class (5,1) is empty" = one covering
(U, V, W) configuration (then record it as a witness - an 18-point cover in
class (5,1) would be outcome (c) and would decide the question the other way).
Cap: the priced budget in TASK.json; long walks are blocking foreground chunks
with per-shard receipts (one section per mode), complete/budget_hit flags, and
re-runs from EMPTY receipts to prove recomputation.

Predecessor authors; intended artifact and reproduction command:
All cited PR authors verified against current ground truth at writing:
PR 2542/2634/2773/2870/2911/2933/2961 Aaron Wang (navinor); PR 2691 Nicholas
Stone (NicholasStone); PR 943 Ross Richardson (prefix-walk model); PR 1185
Doug Colkitt (pinned f(5)=12, f(6)=16 record). PR 2961's engines (tight.py and
its vendor/) are vendored byte-exact with SHA-256 pins and credited. Intended
artifact: this package, replayed with
`python3 -I -B research/f7-18point-avtail-seed010d26fa/verify.py <mode>`.

# Task card (local) — reframed two-writer helper-star absorption

Task ID / proposed scope key: `bit-helper-contract` (drawn track `bit-mechanisms`,
chooser OS nonce `eceddf4aa200ce2301eb1f4de3d09ff1`, scope key `3475f46c8358c6a9211b`),
refined to one concrete object.

Base commit: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (priority revision 4;
selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`;
catalogue SHA-256 `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`).

Exact predecessor and dependency heads (all open PRs, rechecked before computation):

- PR #1868 `6b222d01fee072bcd3a680e6a96ae7d22e13bcac` (Sagar Thakrar): twisted
  helper contract H2-tw/H4-tw/K-tw, three single-writer absorptions, single-edge
  census; open question: multi-gate splits.
- PR #1913 `6cde2d14f0090f51672feae32a04f3145e70f595` (Adam Gall): two-writer
  single-donor completions on the pinned PR1062 11,500-ADD word; 314 exact
  arbitrary-dirty completions, 52 with one fewer ADD, all rejected at the
  *unchanged* gate frames; explicitly does not rule out changed gate
  frames/itineraries.
- PR #1937 `8b4a4d59eb5df9971d44587d9980c3dd0b18fc96` (Aaron Wang): complete
  multi-donor/multi-writer F2 linear system on three words in `same_path` and
  `monotone_all` modes, both with **fixed gate frames**; five solvable edges.

Concrete object and question: the 52 scalar-saving two-writer single-donor
completions of PR #1913 on
`research/r439-bsection-stars-seed01/candidate.json.gz` (zero-based registers:
sources 0-110, dirty targets 111-221, dirty helpers 222-660). When the receiving
A gates' frames may be **changed** (monotone-climb legal rational subspaces; the
one premise PR #1913 and PR #1937 both hold fixed), can any of those completions
become frame-legal while preserving the exact 661-column arbitrary-dirty boundary
and every register's original final frame? If so, what is the exact paid-profile
change of the cheapest legal reframing?

Smallest falsifying instance first: the lexicographically first saving completion
of PR #1913: omit D restoration `231 ^= 459`; A[9] donors `[4] -> [4,109]`;
A[527] donors `[459] -> []`; scalar criterion holds on all 661 columns.

Scope status: **refined** (card `bit-helper-contract`). Reason: the card's
generic replacement-interface question is covered for fixed gates by PR #1194
(semantic D), PR #1868 (twisted contract), PR #1913 (two-writer single-donor
exclusion) and PR #1937 (complete fixed-gate linear system). The narrowed object
changes exactly one named premise those results hold fixed: the receiving gates'
frame itinerary. This is not a claim about other words, other helpers, or other
correction classes.

Method; explicit parameter ranges: exact F2 linear algebra on 661-column rows
(Python ints), exact rational span containment in Q^8 via the pinned label lines;
the donor alphabet is PR #1913's (all original source/helper registers except the
centre, 549 choices); reframing candidates per gate are spans of label sets
containing the forced join, enumerated from the pinned 636-frame catalogue and
joins of the touched registers' original visit frames; the paid histogram is the
inherited rank-increment count of per-register frame paths plus the nine
rank-7 COPY rows. Whole construction priced: ADDs, F/B positive bounds, paid
histogram, moment comparison at p = 1 - a.

Nearest overlapping PRs and why this adds something: #1913 rejects the 52 at
fixed frames and names changed frames as open; #1937's `monotone_all` pool is
fixed-gate and its dual witnesses do not cover enlarged gates; #1868's census is
single-writer. No open PR found (find_overlap 2026-10-15 07:50-07:52Z, 612 open
PRs / 1138 discussion records, complete pagination) covers reframed two-writer
absorption.

Optimistic full cost budget; required observable improvement: stdlib-only, under
an hour of exact computation. Success = one legal reframed completion with full
boundary replay and exact profile, OR a per-completion exact obstruction/minimal
profile cost showing every legal reframing worsens the moment bill (scoped
negative). Unchanged scalar counts alone are insufficient: the paid profile is
always reported.

Success evidence; falsification test; time/compute cap: positive = the committed
word passes the 661-column forward/reverse literal COPY/ERASE boundary and an
independent recomputation of the paid histogram; falsification = dirty-column
failure, rational noncontainment witness, or profile/moment comparison. Cap:
this session; kill if the minimal instance alone exceeds the declared
reframing domain.

Predecessor authors; intended artifact: credited above (Thakrar, Gall, Wang,
woklerx/PR1194, Vagvala/PR967, Davidson/PR915-1122, Richardson/PR923,
DreamingOfClouds/PR589, eumemic/PR555 and xcheck_p.py). Artifact:
`research/r439-two-writer-reframing/` with verify.py, CERTIFICATE.json, README
with **Open next questions**. No kappa claim; bit side does not bind.

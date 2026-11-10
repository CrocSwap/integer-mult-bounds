# Independent complete contact and pairing review

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This supplements the original bounded independent review; it does not replace or
retroactively enlarge that review's 68-contact and single-Gram execution scope.
The initial target is the published `p104-two-channel-hub` package at remote
`057528d`, with exact mathematical input bytes pinned in `check_review.py`.

## Result and execution

`PASS_INDEPENDENT_FULL_HUB_REVIEW`: all 4,296 certified cuts in 30 non-skipped
boundary groups were checked. Every collection/delivery pure dimension matches
the certificate. Dense rational Gram elimination gives 4,292 rank-zero cuts and
four rank-one cuts. There is no rank-two cut in this certified domain.

The checker independently reconstructs 7,643 prefix contact vectors and 11,104
suffix contact vectors, representing 10,641 collection and 14,095 delivery
records across all 1,093 nontrivial stored frame IDs. Every vector retains the
full 801-axis space; zero coordinates are stored sparsely. The reconstruction
uses 5,507,762 exact scalar updates. It does not import the primary verifier or
call its `trace`, `pure_basis` or `pairing_rank` functions.

The first full run took 35.838 seconds. Subsequent read-only normal and optimized
runs passed in 34.036 and 40.864 seconds. The tests also cover 2,600 exhaustive
small nullspace fixtures, 32 comparisons of the accelerated propagation against
a full opposite-direction chronological loop, a rank-two Gram, dirty-axis
contamination, and exact cancellation recovering a second pure direction.
Actual compressed source-byte corruption was rejected before parsing in both
normal and optimized Python. These timings are observations, not fixed bounds.

## Opposite-direction reconstruction

The primary implementation propagates all prefix rows forward and all suffix
columns backward. This checker instead reconstructs each requested prefix
covector backward from its contact and each requested suffix vector forward
from its contact. In particular, for `destination += c*source`, backward
covector propagation adds `c*v[destination]` to the source coefficient, whereas
forward vector propagation adds `c*v[source]` to the destination coefficient.
COPY additionally removes the overwritten destination coefficient in the
backward direction, or overwrites it in the forward direction. SCALE multiplies
the relevant coefficient. INIT and CLEAR kill it. MOVE has identity scalar
action but contributes physical midpoint contacts.

An event-dependency heap skips only operations whose acting coordinate has zero
coefficient. The backward event lists index scalar destinations; forward lists
index ADD/COPY sources together with destinations of resets, SCALE and COPY.
When an event changes support, its affected role schedules are refreshed past
that exact event. Thus an omitted operation acts identically on the current
vector. Thirty-two full chronological opposite-direction walks independently
check the accelerated scheduler.

The contact enumerator uses the actual stored-frame chronology: public entrance
contacts, destination changes, relevant source changes in the adjoint direction,
public exit contacts, and every legal proper intermediate frame of every MOVE.
Zero vectors are excluded only after complete algebraic reconstruction. The
`time2` convention treats even times as event boundaries and odd times as a
MOVE midpoint. The global zero and full frames cannot be strict intermediate
frames for any helper boundary, so their contact histories are immaterial here.

## Different pure-space and rank calculation

For each frame and side, form an ordinary full-coordinate basis V of the
available vectors, with coordinate order 0 through 800 independent of the helper
group G. This stage preserves the entire span; it does not prioritize outside
coordinates and does not decide purity. Snapshots are reused when a certified
cut has not changed the full span.

Let M have rows indexed by coordinates outside G and columns indexed by basis
vectors of V: `M[j,i] = V[i][j]`. A basis-coefficient vector u gives a pure
combination exactly when `M*u = 0`. Dense rational forward elimination and
back-substitution compute a basis of this coefficient nullspace. Multiplying
its vectors back through V gives a basis of `span(V) intersect Q^G`. Independence
of V ensures that nonzero nullspace vectors do not collapse to zero. All dirty
public and owned coordinates are among the outside constraints.

Do this independently for collection and delivery. Construct their full rational
bilinear Gram matrix and determine its rank by dense Gaussian elimination. This
is separate from the primary outside-first row reduction and rank-at-most-one
cross-minor test. The run creates 7,444 full-span snapshots and computes 2,778
distinct coefficient nullspaces, reused across cuts with identical spaces.

## Exact dependence and limits

The pinned primary `RESULT.json` supplies the cut-domain list and the expected
pure dimensions and ranks. This checker does **not** independently enumerate the
physical pivot domain, prove that all intervening cuts are covered, or certify
the skipped boundary groups. It checks every listed cut without sampling or an
early stop. The separate lead physical-domain sweep addresses domain coverage;
that result must be stated and reviewed on its own terms.

The mathematical result remains the narrow source-bound retained-buffer hub
obstruction under the original scalar chronology, helper boundary matching and
separately specified S09 contract. Native realization, ordinary work, caller,
compiler, all-size and global-construction obligations remain inherited or
unrun. No new kappa, human scientific acceptance, or formal-kernel acceptance is
claimed.

## Portable replay

Place `check_review.py`, `REVIEW-RESULT.json`, and `CONTACT-TIMES.json` together
in an immediate subdirectory of the package, separate from the original review.
From the repository root, for an installation at `independent-full/`:

```sh
python3 -I -B research/p104-two-channel-hub/independent-full/check_review.py
python3 -I -B -O research/p104-two-channel-hub/independent-full/check_review.py
```

Expected marker: `PASS_INDEPENDENT_FULL_HUB_REVIEW`. Each command recomputes and
compares both receipts without writing files. `--package PATH` explicitly selects
the source package. `--emit` is the only receipt-writing mode and writes both
receipts beside the checker. For temp-only emission, copy the checker into a
temporary directory and pass `--package` pointing to the source package.

Frozen checker SHA256:
`2143fadcd6b7de592ad516174ff27e47377c1be0867b46bd418a620d81da3b24`.
Frozen review receipt SHA256:
`1a9aff019d6dd958995258d47fa69a040e13dcf5b6e3c4d569074d1b28bfee87`.
Frozen contact-times SHA256:
`a870454b329666ffc97658c2c9413fa7ab9ac6a7019ed035b483745f694a9173`.

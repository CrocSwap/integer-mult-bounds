# Proper endpoint arrivals in P104 transport-cost screens

The 208-helper floor inherited by Nick Petalas's pending [PR2640](https://github.com/CrocSwap/integer-mult-bounds/pull/2640)
requires **source-dependent proper arrivals at target hyperplanes**. Encoding
only 208 total lifetimes is a valid but weaker relaxation: its optimizer uses
134.875 unproductive 0->9 lifetimes to satisfy that count.

This source-bound cost audit binds the stronger arrival obligation to complete
helper histories and certifies both relaxations. At the selected exponent the
stronger transport lower bound increases by 1.339066098318; at p=98/99 it
increases by 7.979043055690. Exact brackets, source reconstruction and a control
distinguishing the two models make this an independently replayable handoff.
Even the stronger necessary constraints admit 208 integer lifetimes; neither
relaxation constructs a correction circuit or admits a supplier.

One integer witness for the necessary constraints is particularly simple:

```text
137 histories (1,7,1) + 71 histories (1,1,1,1,1,1,1,1,1)
208 source-dependent proper arrivals at dimension 8
capacity at each of the seven cuts = 137 + 71*64 = 4681
paid transport profile = 913 H1 + 137 H7; rank mass = 1872
```

Every cut needs at most 4680 entries. This is an integer **profile witness
for a relaxation**, not a correction circuit, attainable rectangle assignment,
208-helper upper bound for the real network, or favorable complete bill.

## Certified transport-cost optima

For each positive composition h of nine, let x_h be its nonnegative real
lifetime count. Let a_k(h) be PR2640's capacity at cut k: if the crossing
is a -> b with 1 <= a <= k < b <= 8, its capacity is 2^(7-(b-a)); otherwise
it is zero. Its positive transport charge is c_p(h) = sum(r^p) over its jumps.
For each of the 256 histories the checker enforces

```text
sum_h a_k(h) x_h >= (4656,4656,4672,4680,4672,4656,4656)_k
sum_h e(h) x_h >= 208
sum_h x_h <= 482
```

Here e(h)=1 only when the history enters dimension 8 from a positive proper
dimension; it is zero otherwise. This implements kumagi's [PR2353](https://github.com/CrocSwap/integer-mult-bounds/pull/2353)
requirement of two source-dependent proper arrivals at each of 104 distinct
target hyperplanes. A history 0 -> 9 cannot stand in for an endpoint arrival.
The finite rank-eight premises for all 104 targets are recomputed here.
The 482 upper cap is a hypothetical boundary from the preceding screen,
not a newly established necessary budget or feasibility assertion.

The objective is the unnormalized positive transport bill sum_h c_p(h)x_h:

| Exponent p | Total-count relaxation | Proper-arrival relaxation | Integer witness bill |
| --- | ---: | ---: | ---: |
| 1 | 1872 exactly | 1872 exactly | 1872 exactly |
| 1 minus selected complex saving | 1867.534416637517 | 1868.873482735835 | 1868.878463802756 |
| 98/99 | 1845.325338368350 | 1853.304381424040 | 1853.334268474880 |

The selected saving is pinned to ASSEMBLY.json as
67018507072324140917/40000000000000000000000. The last row uses a=1/99,
the retained balanced-transfer planning threshold for kappa=.01. Neither
evaluation is an exponent claim for P104. RESULT.json gives exact rational
enclosures of width less than 10^-40, not floating-point acceptance decisions.
Both nontrivial primal certificates use 208 lifetimes and the same six active
histories. The same certified brackets hold with or without the upper cap.
All noninteger table entries are approximate. No exact integer optimum is claimed.

## Why the certificates suffice

The replay enumerates all compositions by the eight possible internal stops.
It authenticates the original word/fixture, reconstructs the E8 port order,
recomputes every forced-entry set (including its complete hash), and checks the
affine-odd and endpoint-arrival finite premises. It imports no predecessor
executable or optimizer.

For each exponent, CERTIFICATES.json supplies nonnegative dual weights y and a
nonnegative fractional profile x. The checker tests all 256 inequalities
`a(h).y <= lower(c_p(h))`, all primal constraints, and the lifetime cap.
Weak duality proves `b.y <= optimum <= upper(c_p).x`. The dual relaxes the
upper cap, but the displayed primal respects it; hence the same bracket applies
with the cap. This is certificate checking, not trust in the simplex solver.

The independent power enclosure uses a positive atanh series for logarithms,
an explicit geometric tail, outward-rounded integer exp series at argument
at most 1/4, and four squarings. Tests independently check every 98/99 power
by raising integer bounds to the 99th power, and square-root powers by squaring.
No numeric library or floating-point value enters acceptance.

The written program-to-crossing implication remains credited to PR2640; the
proper-arrival implication remains credited to PR2353. This package checks
their finite inputs and adds the coupled cost relaxation, not a formal-kernel
proof or independent recertification of every universal predecessor argument.

## Reproduce

Python 3.12 or later, standard library only, from the repository root:

```sh
python -I -O -B research/p104-crossing-profile-screen/verify.py
python -B research/p104-crossing-profile-screen/test_verify.py
python -B scripts/research_package.py --package research/p104-crossing-profile-screen
```

Expected marker: `PASS_P104_CROSSING_PROFILE_SCREEN histories=256 cuts=7 exponents=3`.
Normal replay is read-only and works in a Git-free export containing the declared
inputs. `--emit` prints a recomputation. Optional `solve.py` regenerates
CERTIFICATES.json using a bounded exact-rational simplex; it is never imported
by replay. It rewrites CERTIFICATES.json and the weaker COUNT-ONLY.json intentionally.
RESULT.json can then
be regenerated with `verify.py --emit`. Its informational decimal output is
not an acceptance criterion.

Seven test groups cover independent powers/history enumeration, an all-cheap
profile, phantom 0->9 lifetimes that satisfy cuts but fail arrivals, false dual
weights, noncanonical masks, optimized read-only export, typed receipt and
certificate corruption, duplicate keys and source drift. Python uses dynamic
allocation and arbitrary-size integers; the experiment is bounded to 256
histories, eight constraints, three exponents and fixed 512-address geometry.

## Scope

The model retains the frozen X/Y paths, immutable X, unread Y, fixed rational
coefficients, no access to original helper/private values, and restored new
ZERO-to-FULL nested helper lifetimes. The pending predecessor proofs and those
hypotheses are material. The literal source never reads Y or writes X; both
facts are checked before applying the relaxation.

The objective omits ADDs, compatible geometric paths and chronology, native
adapters, ownership/idle/residual work, precision/tape and the consumer. It is
not recursive excess after displaced idle credit or a normalized full moment.
For any declared common width m and role normalization W, its transport-only
normalization would divide by W*m^p; that alone supplies no full invoice.
No native phases, full correction endpoint, selected cold replay, all-size
compiler or outer multiplication theorem is checked.

## Open next questions

Can actual source/target labels and chronological contacts
force a stronger bill than this relaxed profile? First bind one history's
simultaneously realizable contacts to the frozen labels, then add that valid
coupling to the screen. The blocker is compatible geometry/chronology, not
another evaluation of these same seven inequalities. Stop this audit here;
its feasible relaxation does not justify a construction campaign by itself.

## Provenance and credit

Started on canonical main b4560d9e7216f72b73c5aa940ac099c05e33ccf9, priority 5;
single picker nonce 4728c4f9f86527f76a705b5cbd76cfa0, independent verification.
TASK.json records the refined scope, source freshness, overlap and limitations.
SOURCES.json binds the unchanged live inputs. PREDECESSORS.json retains exact
PR2640 proof/receipt at 2a5b9d72371211eac1288b690bc2739a97132439 and
PR2353 README at 2704eadf6b5205d4b965e9c6fc6dce28b89783cf.

Final live overlap found a [concurrent broader cost claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18953694),
posted at 16:43 UTC after this session's entry snapshot. That investigation also
includes the channel/ideal-idle template. This contribution is narrowed to the
proper-arrival model distinction and code-disjoint transport certificates for
both models. It neither reviews unpublished code nor duplicates a full-budget
decision. The concurrent work retains independent credit; these results can be
used as a complementary source-bound regression or corroboration.

Credit Nick Petalas/PR2640 and PR2604 for crossing/contact pricing and its
arrival-shape correction; kumagi/PR2353 and Philippe Van Velzen for the
208-arrival argument and screen; ywz65/PR2614 for the later-read audit; Rohan
Arun/PR1972, Chafik Boukhalfa/PR1991, Adam Gall/PR1940, Josie Elliston/PR1071,
Ali Romman and the retained geometry/native lineage for the frozen inputs.
The atanh/Taylor bounds, weak duality and simplex algorithm are standard.

New cost certificates, source reconstruction, controls and prose prepared for
Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0. No independent
human review, separate-agent review, proof assistant or hosted CI is claimed.

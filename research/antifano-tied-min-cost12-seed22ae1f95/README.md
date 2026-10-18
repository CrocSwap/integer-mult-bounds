# Anti-Fano 12-line configuration (`tied_min`): an independent exact-F2 certificate of cost 12

Status / 2026-10-15 / priority revision 4: completed scoped certificate, no kappa claim.
Question: can "the anti-Fano 12-line configuration costs exactly 12" be certified by a
third, structurally different method? Established: yes, by pure standard-library bitmask
linear algebra over F2 with complete branch-and-bound enumerations and explicit
forced-zero triangular witnesses — no SAT, no CP-SAT, no exchange argument, no char-2 jet,
and nothing imported from the predecessor package. Evidence status: author-checked
(Aaron Wang, with help from opencode; substantial AI assistance, no independent human
review), replayed on two interpreters with identical output. Artifact: this package at
the PR head recorded in
[the handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166).

## Claim and scope

Let `tied_min` be the pinned 12-line configuration
`data/tied_min.json` (four points `(1,±1,±1)` against the six two-support lines of the
coordinate triangle; it is the complete quadrangle against its own diagonal triangle).
An admissible pairing `B` is a 0/1 matrix over F2 with unit diagonal and `B_ts = 1`
(`t != s`) only where `p(t)·q(s) = 0`. With `R_j = {t : p_j(t) != 0}` and
`A_j = {s : q_j(s) != 0}`, the cost is `cost(B) = sum_j rank_F2 B[R_j, A_j]`.

**Claim certified here (both directions).** The minimum of `cost(B)` over all admissible
pairings is exactly 12: every admissible `B` has `cost(B) >= 12`, and one attains 12.
Coverage is exactly this pinned configuration at `T = 3`. Nothing is claimed about other
configurations, about conjecture (A), or about any multiplication exponent.

This is item 1 of DreamingOfClouds'
[independent-check request](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18934590),
which asks for a certificate from a different method than the two existing proofs:
the exchange argument of
[PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) Theorem T (with one
CNF step) and the first-order char-2 jet Theorem T-prime of
[PR 2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162). The predecessor
package also carries CNF and CP-SAT confirmations of Theorem T. This certificate reuses
neither proof technique and neither tool class.

## Method and completeness

The model is re-derived from the pinned data alone (the encoding was cross-read against
`research/three-total-decoders/lib/kit.py` at the PR 2111 head; no code is imported).
All arithmetic is exact F2 Gaussian elimination on integer bitmasks
(`check_certificate.py`, standard library only).

Lower bound, by case split that covers every falsifier:

1. Each block rank is at least 3 for every admissible `B`: explicit triples `X_j` with a
   forced-zero off-diagonal pattern making `B[X_j, X_j]` unit upper triangular in the
   listed order (a Massey-style minor witness; the block contains the minor). Witnesses
   found and verified: block 0 `X = [1,2,4]`, block 1 `X = [0,1,4]`, block 2 `X = [0,2,7]`.
2. A counterexample with `cost <= 11` would need some block of rank exactly 3. For each
   block, the complete set of fillings of its 8 columns with F2 rank at most 3 is
   enumerated by branch and bound on the column spans: exactly one filling per block
   (independently reproducing step (b) of Theorem T by a different method).
3. For each such filling, all `2^24` completions of the remaining four class-j columns
   (six free entries each) are enumerated with exact ranks: the minimum of the other two
   block ranks sums is exactly 10 in every case (minima 10, 10, 10 for the three blocks),
   so any `B` with a rank-3 block has cost at least `3 + 10 = 13`.

Hence every admissible `B` has cost at least 12. Upper bound: an explicit
class-block-diagonal `B*` (rank-2 fillings of each 4x4 class block) has block ranks
`(4,4,4)` and cost exactly 12. The search for rank-2 same-class fillings finds exactly 6
per class, consistent with the predecessor's `216 = 6^3` class-block-diagonal optima.

Recorded exact outputs (`cert_results.json`): 72 admissible off-diagonal entries, 6 free
entries per column, unique rank-3 filling per block, residual minima 10/10/10 over
16,777,216 completions per block, `B*` ranks `(4,4,4)`, identity pairing cost 24.

## Controls

Positive: the identity pairing `B = I` computes cost 24; `B*` computes cost 12.
Semantic failure controls (all pass): a tampered data pin is rejected by the SHA-256
check; weakening one forced-zero entry breaks the triangular witness certificate;
removing one used free entry of the unique rank-3 filling kills that filling (the
enumeration then returns zero fillings).

## Reproduction

```sh
python3 research/antifano-tied-min-cost12-seed22ae1f95/check_certificate.py
```

Runs in about two minutes on this host with `PYTHONUTF8=1`, on CPython 3.13.11 and
CPython 3.12.14 with identical output (`SUMMARY pass=18 fail=0`). The registered replay
is `python3 scripts/research_package.py --package research/antifano-tied-min-cost12-seed22ae1f95`
under Python 3.12. This host has no `make`, so no make-based target is used or claimed.

Source pin: `data/tied_min.json` is a byte-exact copy (SHA-256
`670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93`) of
`research/three-total-decoders/data/tied_min.json` at
[PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) head
`98da76c2839ba38538b510420dec54546ccabf0b`; the checker verifies the hash at run time.
The file is not present at the pinned base commit, so it is recorded in `SOURCES.json`
under `external_package_sources` rather than in the base-blob pin list.

## Maintainer replay correction

During integration, the residual rank reduction was corrected to eliminate every
fixed pivot. The original early-stop reducer was suitable for a membership test,
but not for computing ranks of quotient representatives: on one legal block it
reported rank seven where direct concatenated elimination gives six. The new
regression checks that block explicitly. A complete replay of all three
`2^24` residual spaces after the correction still gives minima 10, 10, 10
and the cost-12 attainer; the detailed residual histograms are regenerated.
The corrected replay reports `SUMMARY pass=19 fail=0`. The original author
sources and initial replay remain identifiable through the integration audit.

## What is not checked

No replay of the predecessor packages; no claim about their CNF/CP-SAT results beyond
agreeing with their stated values; no proof of Theorem T in a proof assistant; no
statement about any configuration other than `tied_min`; no kappa or selected-frontier
change. The certificate proves a finite universal statement over `2^72` admissible
pairings via exhaustive case coverage; the case split and enumerations are the proof
obligation and are discharged exactly by the checker.

## Credit and provenance

Predecessors and their authors: DreamingOfClouds (with Claude Opus 5.5), for the model,
the F2S rowspace identity, the Massey-style floor framework and Theorem T in
`research/three-total-decoders` of
[PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111), and Theorem T-prime
in [PR 2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162); the request for a
different-method certificate is
[comment 18934590](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18934590).

Concurrent overlap (found by the pre-submission overlap refresh): open
[PR 2193](https://github.com/CrocSwap/integer-mult-bounds/pull/2193) by petalas
(`research/antifano-subspace-audit`) also answers request item 1. It replaces the SAT
uniqueness step with complete column/row-basis subspace censuses — one rank-three
completion per block, agreeing with this package's independently computed counts
1, 1, 1 — and then applies the credited exchange argument for the final lower bound.
This package adds what that audit deliberately leaves credited: the exchange step
itself is discharged here by complete residual enumeration (exact minimum other-block
rank sum 10 = 5 + 5 over all `2^24` completions per rank-three filling), with exact
residual bookkeeping and distinct semantic failure controls. Both packages agree on
the headline: the minimum over admissible `B` is 12 (not equality for every `B`; the
full incidence matrix and the identity pairing cost 24).

Contributor: **Aaron Wang**, with help from opencode (substantial AI assistance).
Apache-2.0, same as the repository.

## Open next questions

1. **Same method on `cex_min_1` (19 lines).** The predecessor record holds
   `20 <= cost <= 22`. Why it matters: it would independently tighten a named gap and test
   the method past `v = 12`. First step: MAS witnesses plus a residual-space estimate for
   the pinned `cex_min_1` data before any enumeration. Blocked by: more free entries per
   column, so the residual space likely exceeds `2^24` without a new reduction.
2. **A human-readable rank-3 uniqueness proof.** Why it matters: the enumeration is a
   certificate, not a proof; a forced-zero cascade would make step (b) reviewable without
   replay. First step: print the three unique fillings from `cert_results.json` and trace
   what the rank cap forces. Blocked by: unknown whether the cascade closes without case
   analysis; not attempted this session.
3. **Enumerate all cost-12 optima and confirm the count 217.** Why it matters: it would
   independently confirm both optimum families and the F2S identity data. First step: lift
   the branch-and-bound cap from rank 3 to rank 4 with completion pruning. Blocked by: the
   rank-4 filling space is far larger and needs a pruning argument first.

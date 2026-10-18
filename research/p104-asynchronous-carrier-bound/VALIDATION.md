# Validation and investigation record

## Scope and stopping rule

The research started at `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf` on
branch `codex/k9-p104-delivery`. The source checkout is sparse. Existing
research packages were added with `git sparse-checkout add`.

The completed census covers all 1260 frames disjoint from the coordinate
frame, all mixed dual bases on each union, and all 104 target supports of
each of the 7168 valid decoders. A reflection orbit covers all choices of
the first frame. The independent census visits every split of the two
frames by a different partition algorithm. No random search was used.
The stopping rule was complete enumeration of this domain.

Three approaches were considered: independent target orders, repeated
carrier drops, and an order-independent terminal-read bound. The third
approach gave a uniform result before a native delivery implementation
was justified. The bound admits paid target and carrier drops, so it
also addresses the second approach within the stated interface.

## Findings during development

- One explicit support poset had width 32. All 7168 decoders reduced to
  the same cube support family. Projection away from any one term had
  width 26. These values have exact lower and upper certificates.
- A first prose description incorrectly called the five-vertex supports
  complements of three-vertex paths. The explicit family-equality check
  rejected that description. The correct five-vertex supports are
  induced paths. The antichain widths did not use the incorrect rule.
- A first reflection check compared signed representative Gram entries.
  Reflections can change the chosen root signs. The check was corrected
  to compare absolute products, which preserve zero supports and the
  binary pairing. No mathematical result relied on the rejected check.
- Pricing two extra rank-one children failed the historical T37 budget.
  A stronger screen then gave each extra rank the lower price of one.
  Two ranks still failed. The calculation was repeated on the refreshed
  PR1042/T16 profile and gave the same conclusion.
- No construction search was claimed. A chain cover only bounds the
  terminal-support relaxation; it does not supply source access,
  temporal order, native phases, or restoration.

## Checks

[The execution receipt](VALIDATION.json) records the commands, source
hashes, exit status, elapsed time, and final output. Both scripts use the standard library. Runs use
one CPU process and no BLAS worker pool. No dependencies were installed.

The primary checker rebuilds the exact family census, the nine matching
antichain/chain-cover certificates, and both price screens. It checks
seven controls. Four reject a duplicated antichain element, a missing
chain element, a comparable antichain pair, and a false width. Each
rejection must come from its intended guard. One rejects a changed
support family. A chain and a three-set antichain provide sharp positive
controls.

The normal primary replay passed in 15.907 seconds. The independent
replay passed in 2.602 seconds. The optimized relocated replay passed
in 18.259 seconds. A byte change in a copied selected record was rejected
by the actual CLI in 0.111 seconds. The base selected-record check passed
in 0.489 seconds; it did not replay the full selected supplier. These
times describe this run only.

The second checker imports neither the producer nor PR968. It builds the
E8 lines independently, checks every frame partition, transports each
support family through graph isomorphisms, and verifies every explicit
certificate using set inclusion. Its different root and term order gives
16 ordered support families; the primary order gives 18. Both transport
every family to the same cube.

The full selected supplier replay, repository-wide `make verify`, hosted
CI, and Lean are outside this additive research change and were not run.
No selected or upstream file was changed. Finite replay does not certify
the all-size/compiler, common-label/mutable-source, hosting, precision,
tape, analytic, or bit H1-H5 obligations of either selected construction.

## Overlap refresh

The final metadata check on 2026-10-13 at 18:37 UTC covered 774 open
PRs through PR1120. The relevant heads for PR717, PR1071, PR1077, and
PR1060 were unchanged. A title and body scan found no other asynchronous
P104 delivery proof. This is a repository overlap check, not a claim of
literature priority.

PR1099 accelerates PR968's frame-pair enumeration with an exact mask
algorithm. This package does not use that code. Its separate partition
census is evidence for the new scheduling bound; no timing improvement
is claimed. PR1084 treats a different bit decoder. PR669's sequential
COPY obstruction has an odd-diagonal premise that excludes this E8
class; PR767 treats Gaussian E8 planar and incidence decoders.

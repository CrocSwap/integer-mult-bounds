# Three-shear cycles need exceptional products to escape the paired-root floor

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

Claim type: scoped written proof with exact finite corroboration. For every
finite simple graph, retain both roots e_i+e_j and e_i-e_j on each edge.
Let R contain those rows, and change the Gram factor basis by

    M=(I+t E_ab)(I+s E_bc)(I+u E_ca),
    P=R M, Q=R M^(-T), with distinct a,b,c and rational t,s,u.

Whenever tsu is neither 1 nor -1, every common directed fitting binary
pairing B has the complete algebraic COPY bill

    sum_j rank_F2 B[supp(P_j),supp(Q_j)] >= 2|E|.

In fact every term costs at least its coordinate's graph degree. The
coordinate basis attains the bound, so the joint optimum over this allowed
family is exactly the number of live roots. A fixed nonzero basis can cost
more. Isolated coordinates and zero shear coefficients are included.

This extends the two-interacting-shear obstruction of JoyboyBrian's
[PR5214](https://github.com/CrocSwap/integer-mult-bounds/pull/5214) into the
three-coordinate-cycle case. That package explicitly leaves three interacting
shears open. Its forced identity-minor lemma is a cited predecessor; the new
step is the cycle calculation and its all-graph application. The result
narrows this cycle family to two exceptional product loci for any possible
saving. Neither locus is claimed to save anything.

[PROOF.md](PROOF.md) gives the universal proof and two explicit lost-minor
examples on tsu=+/-1. Those examples explain the proof boundary; a missing
minor alone is not a favorable complete invoice.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/dn-three-cycle-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/dn-three-cycle-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dn-three-cycle-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dn-three-cycle-floor --check-source-history
```

Any other CPython 3.12 executable can replace the local path. The direct
marker is PASS_DN_THREE_CYCLE_FLOOR. Each direct run prints a generated JSON
receipt bound to all six package files. It writes no files, imports no
predecessor executable and works outside a Git checkout. The generic runner
separately validates exact historical source pins.

The finite corroboration checks every nonempty graph on three coordinates
and every coefficient triple in {-2,-1,-1/2,0,1/2,1,2} outside the two excluded
product loci. There are 2,009 exact factorizations and 35,588 complete common
pairing bills, with all admissible directed pairing entries enumerated.
It checks 309,960 identity-minor entries and 106,764 comparisons against a
separately implemented set-of-span rank oracle. The 56 excluded coefficient
triples are counted as excluded, rather than accepted by the theorem.

Another 24 factorizations in dimensions four, five and eight include external
edges, isolated coordinates, zero coefficients and rational coefficients.
They check 168 complete directed-pairing bills and 2,856 minor entries. On
PR5214's actual 12-root D5 graph, t=2,s=u=1 has edge-block bill
(4,3,5,2,2), total 16. This is an explicit complete bill, not its optimized
minimum. Eight rejecting domain, fitting and false-minor controls and two
exceptional-locus witnesses pass. Rational elimination derives the dual
separately from the displayed formula; every Gram entry is checked.

## Scope and provenance

The scientific base is canonical main e54523517d0f03e58352e647c403a5af3e525a57,
priority revision 8, selected #7000. TASK.json records a changed
complex-rank-shape-decoder scope to this algebraic side result. The selected
source-binding first example passed; no selected scientific replay ran.
SOURCES.json pins PR5214's incorporated proof and README as provenance.
No predecessor proof, result or frozen source is changed or scientifically
replayed.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19539403)
records the scope. Live PR and handoff checks, batch reservations, main README
searches and merged-PR searches found no matching cycle theorem in the
checked coverage. The cached overlap report covers 489 open PRs and 7,156
Discussion records with complete pagination, but only 207 of 10,178 tracked
local notes were materialized at its first task scan. Main-tree searches and
the relevant source reads supplemented that sparse coverage. Unpublished
work and arbitrary historical diffs are not covered; global literature
priority is unclaimed.

The theorem concerns rational paired roots and this ordered shear cycle.
Other three-shear patterns, either exceptional product locus, single-sign
deletions, larger basis families, extra terms and factors outside the root
code remain outside it. The physical coefficient arithmetic, producer and
consumer, dirty restoration, frames, native alignment, storage, precision,
tape movement and full recursive bill are unpriced. No new kappa, physical
supplier, complete multiplication theorem, selected-frontier change or
framework-assumption discharge is claimed. No Lean or Docker check ran.

## Open next questions

1. Can tsu=1 or tsu=-1 lower the complete common-pairing bill on an actual
   paired graph? Start with the two lost-minor fixtures and then price all
   terms on a paired D5 graph using one fitting B. The lost minor is the
   current proof gap, not evidence of a saving.
2. Can a different three-shear index pattern or basis family give an actual
   paid decoder improvement? Start with full Gram equality, one common
   fitting pairing and a complete coefficient/restoration/frame invoice.
   The physical producer/consumer and recursive budget remain blockers.

## Credit and implementation constraints

JoyboyBrian #5214 supplies the explicit next question, common-support degree
lemma and two-shear boundary. Nick Petalas #5176 supplies the fixed-split
predecessor; ywz65 #2536/#2719 supplies coordinate pairing and full-Dn
root-code results; Aaron Wang / navinor #2272/#2518 supplies the small-T
screens; DreamingOfClouds supplies the retained Gram/COPY model and root-code
lineage. Their results are cited, not audited here. The new cycle obstruction,
proof and finite checker were produced by Nick Petalas. Classical matrix
multiplication, Gaussian elimination and binary rank retain their status as
classical tools.

The verifier has no recursion, process launch, network access, mutable global
cache or dynamic code. All loops run over fixed finite fixture collections
or dimensions bounded by eight; each binary reduction has a 57-step cap.
Functions are at most 31 physical lines. Explicit exceptions remain enabled
under -O. CPython's managed Fraction, integer and container allocation is a
deviation from fixed allocation. Coordinate matrices have at most eight rows
and columns, root matrices have at most 56 rows and eight columns, and Gram
matrices have at most 56 rows and columns. Actual fixtures have at most 12
root rows. Pairing enumeration uses at most six free bits. The independent
span oracle has at most six rows and 64 states. No allocation-free runtime claim
is made. Warning-strict normal/optimized execution and AST inspection are
the available diagnostics; separate type or lint analysis is unclaimed.

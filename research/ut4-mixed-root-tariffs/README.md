# Exact tariffs for mixed UT4 roots and central twists

**Scoped formal-model theorem; no new kappa.** In the three-adjacent-letter
UT4(F2) register model, arbitrary mixtures of the six noncentral commutator
targets retain their direct paid bill, even with any number of restored dirty
roles and free scalar mixing. Same-role products and central twists are
included; the pure central target is outside the sharpness statement.

Let `a=I+E12`, `b=I+E23`, `c=I+E34`, `u=I+E13`, `v=I+E24`, `z=I+E14`.
Target role i receives `u^s_i v^t_i z^h_i`; let S,T,H be the supports of
s,t,h. Every word satisfies the separate necessary counts

```
n_a >= 2 |S union H|,
n_b >= 2 |S union T union H|,
n_c >= 2 |T union H|.
```

If `H subset S union T` (no pure-z role), all three counts are attained
simultaneously. Nonnegative uniform letter prices therefore give exactly
their weighted sum. The [written proof](PROOF.md) quantifies all finite role
counts and word lengths; the finite checks support its algebraic premise.

| Target on one role | Direct word | Calls (a,b,c) |
|---|---|---|
| u | abab | (2,2,0) |
| v | bcbc | (0,2,2) |
| uv | abacbc | (2,2,2) |
| uz | acbabc | (2,2,2) |
| vz | abcbac | (2,2,2) |
| uvz | acbacb | (2,2,2) |

For example the six-target mixture `(u,v,uv,uz,vz,uvz)` needs exactly
`(10,12,10)` calls, hence32 unit calls, with arbitrary restored dirty
workspace. Applying each displayed word to its coordinate role attains this
bill, including the complete output on all dirty inputs.

## Model and contribution

Work in the **full formal group algebra** F2[UT4(F2)]. A paid factor is
`I+([g]+1)xy^T`, with `g in {a,b,c}` and nonzero binary x,y; both rank-one
idempotent and nilpotent couplings are permitted. Scalar GL maps are
optimistically free and normalized by augmentation. No additional address
maps, clean allocation, copies, erasures, higher-rank unit factors or unpaid
undo are permitted. All paid restoration is counted. This replaces the
rational abelian starting model rather than reducing rational frames mod2.

Adam Gall's [PR1935](https://github.com/CrocSwap/integer-mult-bounds/pull/1935)
already proves the disjoint u/v bound and gives the six-call uv word as a
boundary control. Its methods and that word retain their credit. This package
allows overlapping root supports, heterogeneous target mixtures and central
twists. The latter require the third-degree target coefficient Z.
ToikY's [PR1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662)
supplies the degree-three quotient and middle-span method; Hanson Sun's
[PR1607](https://github.com/CrocSwap/integer-mult-bounds/pull/1607) supplies
the heterogeneous coefficient-tariff approach. This is a new scoped application
and sharp target-family conclusion, not a new rank principle or priority claim.

Each letter's column **and** row spaces must contain the relevant target-space
union. The first-order sum is zero, so rank-nullity adds the two ranks. The
attaining table is checked in the full algebra separately. Quotient equality
alone cannot certify a construction: an explicit four-term formal error is
invisible in the quotient but changes64 dirty input columns.

The pure central z has the eight-call direct word `abcbabcb`; our general
inequalities alone only give six. Stronger central-target predecessors are
explicitly separate. No exact mixed-family tariff with pure-z roles is claimed.

## Evidence and reproduction

Python3.12 and standard library only, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/ut4-mixed-root-tariffs
```

This runs the primary checker, separate checker and eight test groups.
Expect `PASS_UT4_MIXED_ROOT_TARIFFS`, `PASS_UT4_MIXED_ROOT_INDEPENDENT`,
eight passing groups and `PASS_REGISTERED_RESEARCH_PACKAGE`.
Normal verification is read-only; `--write NEW_PATH` explicitly generates
a receipt and refuses occupied paths. Both checkers also support `-I -O -B`.

- All4,096 group products and4,913 quotient associativity equations pass in
  both implementations. The independent quotient uses a rank23 relation space
  on40 truncated words, rather than the primary canonical rewrite routine.
- All20,440 two-role words through length3, with all27 paid factors including
  nilpotents, have identical complete coefficient transcripts. Both separately
  check the column/row implications.
- All399 tuples of length1..3 over the seven sharp labels, each with an extra
  dirty role, attain the counts and full diagonal endpoint. Three additional
  common-conjugate boundary fixtures extend through eight roles. Conjugated
  restored subspaces are explicitly distinguished from coordinate restoration.
- The separate faithful regular action checks all99,264 basis columns of
  those402 operators. The primary uses formal group coefficients; neither
  accepts an endpoint from its nonfaithful quotient image alone.
- Forty omitted-call controls and eight package test groups cover missing
  central charges, overlapping supports, the pure-central exclusion, wrong
  alphabet/rank/order, both spans, legitimate dirty loops, invisible dirty
  errors, source/receipt drift, duplicate/nonfinite JSON, preserved outputs and
  isolated optimized read-only relocation.

[EXPECTED.json](EXPECTED.json) and [INDEPENDENT.json](INDEPENDENT.json)
retain deterministic counts and transcript digests. Actual commands and
environments are recorded in [VALIDATION.json](VALIDATION.json). The code
imports no predecessor implementation. The two mathematical implementations
share only strict receipt I/O, explicit model data and the tested theorem.
They were written in the same AI-assisted session, with no independent human
review or proof-kernel verification.

## Scope and sources

One OS draw `51b93dabe7190b9eb05c31682dd5750a`, priority3
`bit-mechanisms / bit-new-register-model`, scope key `7084092dd726e7ba1f2f`;
base main `ec94fd3d2fcad7ade8e72d6bcd8e223b7fdb3f30`. Coordination:
[Discussion2019](https://github.com/CrocSwap/integer-mult-bounds/discussions/2019).
[TASK.json](TASK.json) records the scope refinement, overlap coverage, exact
nearby heads and remaining obligations. [SOURCES.json](SOURCES.json) binds
three unchanged context/proof inputs and historical catalogue/selected provenance.
The card's source-binding baseline passed; it is not a selected cold replay.

## Open next questions

1. **Mixed pure-central and noncentral roles.** Do central targets' stronger
   middle-span constraints coexist additively with the sharp mixed-root bill?
   Start with one z and one uz role and the degree-three quotient, tracking the
   same middle spans before a bounded word search. A sharp chronological
   construction or a stronger joint lower bound is missing.
2. **Physical realization of the alphabet.** Can any of these formal address
   letters be implemented at a favorable fully charged recursive tariff?
   Start with one concrete letter and its dirty interface, frames, hosting and
   precision invoice. No such compiler or interface bridge is provided here.

The result screens an abstract bit mechanism; the selected construction is
complex-binding. It supplies no physical supplier, rank profile, all-size
compiler, common-label/hosting proof, precision/tape bound, outer analytic
transfer or multiplication improvement. No selected record or frozen source
was changed, and no selected cold replay was run.

## Credit

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance in proof,
implementation, validation and writing; no subagents or independent human
review. Apache-2.0. Credit Adam Gall/PR1935 at
`9bb74ff3597adfe6949d7b988698b06c0c99978b`, ToikY/PR1662 at
`01cc02b164ecc4f9d84df3f56a1fe65b88daf390`, Hanson Sun/PR1607 at
`9d6117918025cee6a0c5b7ef30ff8d936ca0621f`, steph4n-gh/PR1573,
Arham Tahir/PR1589, Cinna Davis/PR1761, juper997/PR1478, woklerx/PR1443,
and the eumemic/PR288, Ali Romman/PR468, David Govea/PR720 and
Gareth Davidson/PR1333 register-model lineage. Predecessor notices are retained
in their unchanged sources; no claim of literature novelty is made.

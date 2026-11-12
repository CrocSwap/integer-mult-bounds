# Arity 24 has an optimal three-query dyadic repair

**Scoped exact result; no new κ.** Prepared by apoursh with substantial
OpenAI Codex assistance. Apache-2.0.

This resolves the r=24 case in Open next question 1 of Nick Petalas's
[PR6653](https://github.com/CrocSwap/integer-mult-bounds/pull/6653).
Its bounded integer-direction search left this arity open. A nonmonic
source form supplies a three-query repair with dyadic coefficients:

```
D24 = -(23/1024)(11A+19B)^3
      +(1679/64)(A+9B)^3
      +(3749/1024)(A+25B)^3.
```

Here D24 is the excess output of the 24 retained children `y += a^3; a += b`
over the eager endpoint `Y+24A^3`. The [proof](PROOF.md) supplies a legal
three-query, five-shear repair that restores both arbitrary dirty sources,
and proves that two queries are impossible even over Q. Thus **three is
the exact query minimum** in the dyadic general-frame contract.

The direction 19/11 is not dyadic, although its actual source row and weight
are. This addresses the general-frame gap in PR6653 rather than just enlarging
its integer search box. It does not prove that monic repairs at r=24 are
impossible. No source snapshot, clean scratch or access to child interiors
is used; reading b is allowed and separately charged in the inherited model.
The five shears are an explicit upper bound, not an optimality claim.

## Evidence and replay

From the repository root, using CPython 3.12 and only the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/cubic-r24-general-frame
python3.12 -I -W error -B research/cubic-r24-general-frame/verify.py
python3.12 -I -W error -B research/cubic-r24-general-frame/independent_check.py
```

The registered replay runs both implementations normally and with `-O`.
Explicit checks remain active in optimized Python.

- [CERTIFICATE.json](CERTIFICATE.json) records the three forms, exact weights
  and complete eight-event repair.
- [verify.py](verify.py) obtains weights by exact elimination, reconstructs
  the target from all 24 literal children, and symbolically checks every
  source frame, the arbitrary-input endpoint and the named-source event bill.
  It authenticates the three live source files and rejects their in-memory
  mutations, plus ten program/domain controls.
- [independent_check.py](independent_check.py) imports neither the certificate
  nor the primary verifier. It directly expands the identity, independently
  replays the symbolic and literal programs, tests 12 dirty rational inputs,
  and rejects eight coefficient, chronology and restoration mutations.
- The written proof, not the finite dirty-input checks, supplies the universal
  identity and rational lower bound. Independent implementation by another
  Codex agent is not independent human or proof-kernel review.

The discovery searched primitive rational slopes b/a with 1<=a<=16 and
|b|<=96, deriving a third slope via PR6653's node equation. Acceptance here
replays only the resulting exact certificate; it does not depend on search
completeness. No negative claim about other arities follows from that search.

## Scope, coordination and next questions

[TASK.json](TASK.json) preserves the original contextual card and declares
this as a changed-scope coefficient/restoration side result. The family
decision is **narrow**: stop at this missing r=24 implication. The proof lists
all retained and appended events; physical event prices, precision, storage,
routing and the complete matched caller bill remain unknown. Three queries
need not be cheaper than 24 eager restoration shears. The selected result
and its five framework assumptions are unchanged.

Upstream was pulled from canonical main at
`e54523517d0f03e58352e647c403a5af3e525a57`. Source-bound baseline orientation
passed; this was not a selected-supplier cold replay. Live all-state PR
searches on 2026-11-12 found no r=24 follow-up to PR6653 (queries included
`cubic 24`, `cubic nonmonic`, `cubic general frames`, and `1679 3749`).
The dedicated overlap helper's remote corpora were unavailable because `gh`
was absent; cached Discussion pages did not establish complete current
coverage. No public advance claim was posted. These are overlap checks,
not a global novelty certificate.

### Open next questions

1. **Remaining arities:** do r=15,22,30,31 admit three dyadic queries in
   general frames? Start from primitive integer source rows and the exact
   node equation; normalized rational slopes must not be required dyadic.
   The blocker is global coefficient integrality; a finite failed search
   supplies no four-query lower bound.
2. **Physical price at r=24:** does the complete eight-event repair beat
   eager restoration under one pinned backend? Start by pricing the query
   on the temporary b row with weight -376832 and the two dyadic b shears,
   using the exact inequality in PROOF.md. Coefficient preparation, routing,
   precision, storage and caller overhead remain unpriced.

These questions and concrete first steps are also recorded in TASK.json.

## Attribution and source binding

Nick Petalas supplies PR6200's reader/defect/rational comparison and PR6653's
node equation and open r=24 question. apoursh's
[PR6212](https://github.com/CrocSwap/integer-mult-bounds/pull/6212) supplies
the dyadic general-frame contract and unrestricted query floor; the r=24
specialization is reproduced in the proof. The earlier original-B,
power-of-two and equal-step families retain apoursh/PR6215,
AAAmirinu/PR6246 and CubeJerry/PR6250's credit. Their inclusion in PR6653's
prior-coverage list is not claimed as new work here.

[SOURCES.json](SOURCES.json) binds the exact main-tree predecessor bytes,
original catalogue and selected record. The PR6653 source head is
`3ea9965e13457fdafc70b784305d026ebfa8faa2`, retained by merge
`2273ea7c7c83d7bc311d0c5805e832eed13f408b`; replay pins the retained files
at the package base. No predecessor or shared infrastructure file is changed.
Classical binary-form decomposition and exact elimination are not claimed
as new general methods.

# C4 root lifting cannot pack four involution outputs into three calls

**Scoped exact negative result; no new kappa.** In the formal group algebra
\(\mathbb F_2[C_4]\) on four registers, the target
\[
  \operatorname{diag}([g^2],[g^2],[g^2],[g^2])
\]
has exact paid-call minimum four in the operation alphabet below. Thus the
candidate root-lifting step from three order-four-labelled calls to four
order-two outputs does not work in this model.

## Model and changed premise

Let \(C_4=\langle g\mid g^4=e\rangle\). Work over the full four-dimensional
group algebra \(\mathbb F_2[C_4]\), not at selected address values. A paid
factor is
\[
  D_N([g^s])=I+([g^s]+[e])N,
  \qquad s\in\{1,2,3\},
\]
where \(N=xy^T\in M_4(\mathbb F_2)\), \(x,y\ne0\), and \(y^Tx=1\). Every
factor costs one call. There are 120 legal rank-one idempotents. There are no
free register or address transformations. The target has four nonidentity
diagonal entries, each equal to the involution \([g^2]\).

This fixes a four-register, finite-torsion model. It differs from the
torsion-free rational-frame, three-register model in
[`bit-three-register-lower-bound`](../bit-three-register-lower-bound/README.md).
The catalogue's comparison points are the #1974 formal GL3 census and #2027
mixed-root UT4(F2) tariff in
[`community-efficient1000-review.md`](../../docs/research/community-efficient1000-review.md);
neither has this C4 alphabet and four-output target. The current open nearby
claims use other objects, including the four-role UT5(Z) target in #2094 and
the three-register GL3(F2) paired-dirty bridge in #2102. The exact overlap
snapshot and its rate-limit caveat are recorded in [`TASK.json`](TASK.json).

## Result and proof

Write \(\varepsilon=[g]+[e]\). In characteristic two,
\[
  \mathbb F_2[C_4]\cong\mathbb F_2[\varepsilon]/(\varepsilon^4),
  \qquad [g^2]+[e]=\varepsilon^2.
\]
The three legal nonidentity labels have increments
\[
  [g]+[e]=\varepsilon,\quad
  [g^2]+[e]=\varepsilon^2,\quad
  [g^3]+[e]=\varepsilon+\varepsilon^2+\varepsilon^3.
\]
The target is \(I+\varepsilon^2 I_4\). Consider any word of length \(k\le3\),
and call a label *odd* when its exponent is 1 or 3. The coefficient of
\(\varepsilon\) in the word minus \(I\) is the sum of the idempotents attached
to the odd labels.

- With one odd label this coefficient is a nonzero rank-one matrix.
- With three odd labels, it can vanish only if \(N_1+N_2=N_3\). A sum of two
  rank-one matrices has rank at most one only when their image vectors or row
  vectors agree. Since both summands are idempotents, that rank-one sum then
  squares to zero, so it cannot be the nonzero idempotent \(N_3\).
- With two odd labels, vanishing forces their idempotents to agree, say both
  are \(N\). Their pair product and their own \(\varepsilon^2\) terms
  contribute \(cN\), where \(c\in\{0,1\}\) depends on whether either label
  is \(g^3\). If there is a third factor, it must be labelled \(g^2\), and
  the full \(\varepsilon^2\) coefficient is \(cN+M\). Neither \(M=I_4\)
  nor \(N+M=I_4\) is possible: these sums have rank at most one or two.
  With only two factors, \(cN\ne I_4\) as well.
- With no odd labels, every factor is labelled \(g^2\). Since
  \(\varepsilon^4=0\), the \(\varepsilon^2\) coefficient is a sum of at
  most three rank-one matrices, so its rank is at most three and cannot equal
  \(I_4\).

These cases exclude every word of length at most three. Four calls suffice:
\[
  \prod_{i=1}^4 (I+\varepsilon^2 E_{ii})
    = I+\varepsilon^2 I_4,
\]
because \(E_{ii}E_{jj}=0\) for \(i\ne j\). The minimum is therefore four.

The proof's finite matrix lemma is checked over all 120 rank-one idempotents
and all 3,606 distinct pair sums. The verifier checks all 39 nonidentity label
patterns of lengths one through three, the exact four-call word, and controls.
It also exactly enumerates the earlier three-register/two-call pilot: all
7,056 ordered two-call words over 28 idempotents and three labels, plus the
shorter lengths, with no witness for \(\operatorname{diag}([g^2]^3)\).

## Cost screen and interpretation

Before the bounded check, the regular-representation rank screen left room for
the proposed saving: multiplication by \(\varepsilon\) on
\(\mathbb F_2[C_4]\) has rank 3, while multiplication by \(\varepsilon^2\)
has rank 2. Four target blocks therefore have rank 8; three order-four-labelled
calls can supply rank budget 9. A three-call word was not ruled out by this
optimistic screen, so the coefficient argument addresses a meaningful
candidate rather than a cost-impossible one.

The abstract invoice counts all calls: four for the direct word and at most
three for the proposed root-lift, with no uncounted register operations. The
model contains no rational source frames, copying, hosting, restoration,
precision, or recursive interfaces. It supplies no conversion to an integer
multiplication circuit and no supplier cost. The current selected result is
still \(\kappa=836330098538459/500000000000000000\), with the complex side
binding; even a success here would have been only bit-side evidence, not a new
\(\kappa\). See the selected record, its review, source manifest, and
certificate pins in [`SOURCES.json`](SOURCES.json).

The selected-record reproduction field is `make frontier1094-verify`. The
cycle ran `python3 -B scripts/research_baseline.py`, which returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` and identified the complex primitive as
binding. That baseline is the intended scope for this side-mechanism work; the
selected cold replay was not run.

## Reproduce

From the repository root:

```sh
python3 -B research/bit-c4-root-lift-seedca46bc/verify.py
python3 scripts/research_package.py --package research/bit-c4-root-lift-seedca46bc --check-only
```

Expected direct-verifier output begins
`PASS_C4_ROOT_LIFT_OBSTRUCTION n=4 labels=3 rank_one_idempotents=120`.
The current local replay uses CPython 3.14.7. The registered generic runner is
pinned to Python 3.12; that interpreter is not installed locally.

## Open next questions

Could a higher 2-power cyclic group or a noncommutative extension use
higher-degree augmentation terms to produce a genuinely shorter root-lifting
word? The next useful step is to derive the degree constraints for C8 and
screen the target rank before any search. Any success would still need a
source-pinned rational-frame/native implementation and complete supplier bill.

## Claim and credit

The local claim is in [`CLAIM.md`](CLAIM.md). GitHub's live GraphQL discussion
refresh hit the authenticated API rate limit; the last complete cached
discussion snapshot and the fresh open-PR scan are described in `TASK.json`.
The claim remains local until posting is available.

Prepared by Cinna Davis (@1337isnot1337), with substantial OpenAI Codex
assistance in the derivation, exact verifier and package. No independent human
review is claimed. New work is Apache-2.0; the cited predecessor is unchanged.

# Shortest S3 single-target words are rigid over every field

Scoped proof. For every field K, every finite number of dirty registers, and
every rank-one idempotent E, exactly three rank-one calls with simple S3 labels
implement the formal target I+([sts]-1)E only when their labels are sts or tst
and all three scalar couplings equal E. Non-idempotent couplings, complex
scalar mixing and more restored dirty registers do not produce another
normalized shortest word. No new kappa or supplier admission is claimed.

This contribution was produced by Nick Petalas. New work: Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## New step and predecessor credit

Brian's [PR #4740](https://github.com/CrocSwap/integer-mult-bounds/pull/4740),
retained at `f2369119c5229405fd8ea8d9477c8f8cf1692f4d`, already proves the
binary shortest-word theorem. Its proof also explicitly supplies the
arbitrary-binary-matrix coefficient criterion, so removing the binary
idempotence restriction alone is inherited. The new result extends the
rigidity conclusion to every coefficient field, including characteristic
zero and odd characteristic. The signed expansion has terms with coefficient
2 which disappear in the predecessor's binary argument. The proof below
retains them and never divides by 2.

Credit unpaidmoon / #4647 for the three-call question and shorter-word support
argument; Riquelme Soares / #4351, Cinna Davis, Wentao Li and the register-model
lineage credited in #4740. Their results are cited, not replayed. David Arias's
[Coxeter tariff theorem #2738](https://github.com/CrocSwap/integer-mult-bounds/pull/2738)
is a binary cost theorem for a much broader group family. It does not supply
this all-field equality classification. No predecessor executable is imported.

## Model

Work in M_n(K[S3]), n >= 1. Set s=(0 1), t=(1 2), z=sts=tst=(0 2),
with group product g h acting as g(h(i)). Define

```text
F_h(A) = I + ([h]-[e]) A,       h in {s,t}.
D_z(E) = I + ([z]-[e]) E,       E^2=E, rank(E)=1.
```

Scalar matrices commute with group basis elements, and need not commute with
one another. Paid couplings A have rank one. They need not be idempotent.
This enlarged algebraic class even permits singular factors, making its
exclusion stronger than one restricted to legal invertible operations.
Non-idempotent factors need not be involutions outside characteristic two.

Equality is coefficientwise in the full group algebra on all n inputs and
outputs. For E=e_j e_j^T, one register receives [z] and every other arbitrary
dirty register is restored. Observing just the target register is insufficient.
Factors are in written product order, with the rightmost acting first.

Arbitrary free GL_n(K) maps are allowed. Move them through paid factors by
conjugating the couplings, which preserves rank. Augmentation [g] maps to 1
and sends each paid factor and the target to I, so the residual free scalar
map is I. The theorem classifies these normalized couplings. It does not
assert uniqueness of the literal interleaved free maps or price those maps.

## Theorem and proof

**Theorem.** F_a(A) F_b(B) F_c(C)=D_z(E), with rank A=rank B=rank C=1,
if and only if (a,b,c) is (s,t,s) or (t,s,t) and A=B=C=E.
Consequently the minimum paid length is three for every n and K.

Every term of an expansion has a group label given by an ordered subword of
the paid labels. No subword of length at most two is z. Among three-letter
words only sts and tst can contribute to [z]. This also excludes all shorter
programs. Interchanging s and t reduces the proof to F_s(A) F_t(B) F_s(C).

The full signed expansion has the following coefficients, over the integers
before specializing to K.

```text
[e]   I-A-B-C+AB+BC+2AC-2ABC
[s]   A+C-AB-BC-2AC+2ABC
[t]   B-AB-BC+ABC
[st]  AB-ABC
[ts]  BC-ABC
[z]   ABC
```

Match [z], [st], [ts], and [t], in that order. They give

```text
ABC=E,       AB=BC=E,       B=E.
```

Thus AE=E and EC=E. The [s] coefficient gives

```text
A+C=2AC.                                            (1)
```

Since rank A=rank E=1 and AE=E, im A=im E. The idempotent E is the
identity on this image, hence EA=A. Left-multiply (1) by E, using EC=E,
to get A+E=2AC. Subtract (1) to get C=E. Now AC=AE=E, so (1) gives
A=E. This uses subtraction only, and remains valid in characteristic two.
The middle coupling already equals E. In fact the argument only needs the
rank-one condition on A; it forces the other two ranks automatically.

For the converse, decompose the register space as im E plus ker E. Each
F_h(E) is [h] on im E and I on ker E. The alternating three-call words
therefore have exactly the claimed full formal endpoint. This proves both
directions and supplies the upper bound without scratch or free mixing.

The same coefficient table gives a useful criterion for arbitrary A,B,C:
the alternating word attains D_z(E) if and only if

```text
B=E,       AE=E,       EC=E,       A+C=2AC.
```

The identity coefficient then equals I-E automatically. Rank restrictions
cannot be discarded from the rigidity theorem: A=C=I and B=E satisfy this
criterion in every field, while A and C have rank n. This example also shows
why a correct lower bound does not imply uniqueness in a larger alphabet.

## Exact evidence and reproduction

`verify.py` independently expands all eight label words with integer
noncommutative scalar coefficients. It checks the entire signed table and
the opposite alternating word. This is an exact coefficient calculation,
not a numerical field sample or a formal proof-kernel check.

The new finite domain is K=F3 and n=2. The verifier enumerates every nonzero
rank-one matrix as an outer product and every three-call word using either
label. It compares every formal group coefficient and every register entry
against all rank-one-idempotent targets. This census includes nilpotents and
singular factors. All 262,144 words yield exactly 24 hits, two for each of the
12 targets. The binary census of #4740 is not rerun.

A separate literal 12 by 12 left regular-action calculation checks a rational
oblique projector. Seven boundary-control groups cover a nilpotent middle
factor, a singular middle factor, wrong labels, an omitted factor, valid
higher-rank nonrigidity, dirty-spectator leakage and the false assumption that
every rank-one factor is an involution in odd characteristic.

From the repository root, using the standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/all-field-s3-shortest-rigidity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/all-field-s3-shortest-rigidity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/all-field-s3-shortest-rigidity/verify.py
```

Use any CPython 3.12 executable at another installation. Every direct run is
read-only and emits a generated JSON receipt with recomputed counts and SHA256
hashes of all five package files. Receipts and logs belong outside the checkout.
`SOURCES.json` pins historical provenance only; there are no live input imports.

## Scope, budget and stopping decision

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
The selected source-binding control passed; it was metadata orientation, not
a supplier replay. The card's historical balanced baseline is superseded by
the current guidance's `research_selected_baseline.py` command.

This changes the bit-new-register-model card to an all-field equality side
result. The changed premise is the scalar coefficient field. It clarifies a
formal complex-mixing alternative to the binary register model without
claiming a physically priced alphabet. The original card's native supplier
acceptance gate remains unmet. Stop at this first verified extension.

Initial searches covered live open PR titles and bodies, this account's recent
work, active Discussions, merged S3 rigidity searches and every main README
for distinctive field/rigidity terms. The cached card search covered 365 open
PRs and 3,819 Discussion records at 21:45-21:46 UTC on 2026-10-22. Sparse local
notes, arbitrary code diffs and unpublished work were not fully searched.
No-match searches do not establish novelty. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133362)
records the intended scope.

No longer-word search, native implementation, paid mixing/hosting, precision,
recursive bill, all-size multiplier, selected frontier update, Lean or Docker
run is supplied. The all-field conclusion rests on the written proof; finite
checks corroborate it. No unbounded computation is used to infer it.

## Open next questions

Can a concrete native complex register interface realize and price these
rank-one calls with free scalar mixing replaced by its actual cost? This
matters before the formal all-field exclusion can be applied to a supplier.
Start with one reflection and an explicit noncoordinate projector, listing
every scalar operation, frame conversion and dirty return. No such native
contract is supplied here. Longer searches in this same three-call model
cannot change the equality theorem and are not a justified next step.

## Verifier implementation limits

The verifier has no recursion, subprocesses, network access, external mutable
state or generated code. Its largest enumeration is the explicit eight label
words times the cube of the 32-matrix ternary alphabet; all other loops use
fixed dimensions at most 12. Functions fit within 60 lines. Explicit exception
checks survive optimized execution. Python allocates tuples and small maps
dynamically; fixed loop domains bound their live sizes. Maximum live formal
state has six 2 by 2 coefficient blocks, with a separate 12 by 12 rational
matrix fixture. The registered runs enable warnings as errors in ordinary
and optimized Python. These are local verifier properties, not properties of
a physical multiplier.

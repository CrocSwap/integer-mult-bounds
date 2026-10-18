# Four-call barrier for a noncentral UT4 root pair

**Exact scoped negative result; no new supplier or kappa.** In the full formal
group algebra F2[UT4(F2)], with paid labels restricted to the three adjacent
transvections, the endpoint

~~~text
diag([xyxy], [yzyz], [1], [1])
~~~

has no realization in at most four calls
D_N(g) = I + ([g]+[1])N, even when every binary rank-one idempotent
N in M4(F2) is allowed on every call. The exact search covers all ordered
words through length four. A direct eight-call word realizes the endpoint, so
the minimum in this fixed formal model is between five and eight. Lengths
five through seven were not searched.

## Model and cost screen

Encode a group element by its six strict-upper entries in the order
(12,13,14,23,24,34). Let x=I+E12, y=I+E23, and z=I+E34; these involutions
generate the 64-element group UT4(F2). Their commutators
u=xyxy=I+E13 and v=yzyz=I+E24 are noncentral. The target is
diag([u],[v],[1],[1]) over the formal group algebra.
Indeed, u and z have commutator I+E14, as do x and v; these nonidentity
commutators are checked in the executable structural validation.

There are 120 rank-one idempotents: each is ab^T for nonzero a,b in F2^4
with b^T a=1. This gives 360 allowed call matrices. Because each paid label
is an involution and N^2=N, every call is itself an involution:
(I+([g]+[1])N)^2=I.

The direct construction uses x,y,x,y on register one and y,z,y,z on
register two, for eight unit-priced formal calls. In the natural
16-dimensional representation of the four-register group-algebra matrix, the
target displacement has rank two. Each allowed call has displacement rank
one, since it is a tensor product of a rank-one idempotent and a rank-one
generator displacement. Thus one call is excluded by rank, while the
optimistic rank floor is two. This formal count assigns one unit per call.
Source, helper, recursive, hosting, restoration, precision, and interface
charges do not exist in this abstract identity model; treating them as zero
would only make a hypothetical short word cheaper. A formal identity alone
would still need a realized supplier and complete interface bill before it
could affect the selected conditional bound.

## Exact search

For each of the 360 allowed factors, form the full 4-by-4 matrix over
F2[G], where a group-algebra coefficient vector is a 64-bit mask. The exact
ordered two-factor table contains 129,600 words and 87,016 distinct matrix
products (42,584 ordered collisions).

The exhaustive split is:

1. Length two: test the target against the complete pair table.
2. Length three: for each of 360 final calls C, test target*C against the
   pair table, using C^-1=C.
3. Length four: for each ordered suffix (C,D) among all 129,600 pairs, test
   target*D*C against the pair table, using (CD)^-1=DC.

The diagonal target makes each right-side multiplication an exact row
translation in the group algebra. The script nevertheless stores and compares
all 16 matrix-entry coefficient masks; it does not project to a representation
or quotient. The certificate records the full pair-table digest and the
complete candidate counts. It also checks the direct eight-call construction,
an omitted-call corruption, and a wrong-label corruption.

## Reproduce

Python 3.10+ and the standard library suffice:

~~~sh
python3 -I -B research/ut4-noncentral-commutator-seedbfe59/verify.py
~~~

Expected output:

~~~text
PASS_UT4_NONCENTRAL_Q4 factors=360 pair_words=129600 distinct_pairs=87016 q3=360 q4=129600 outcome=no_word_of_length_at_most_4 baseline=complex
~~~

To regenerate certificate.json explicitly:

~~~sh
python3 -I -B research/ut4-noncentral-commutator-seedbfe59/search.py --write-certificate
~~~

search.py constructs the group table, all legal factors, full group-algebra
matrix products, and the exhaustive meet-in-the-middle search.
verify.py recomputes the result and requires exact certificate equality.
certificate.json pins the seed, base, selected-record digest, table counts,
rank screen, outcome, and direct/corruption controls. Before searching, the
script cross-checks every one of the 4,096 ordered UT4 group products against
ordinary 4-by-4 binary matrix multiplication. The verifier also reruns the
selected baseline binding control and requires exact equality with BASELINE.json.

## Scope, overlap, and attribution

This refines catalogue task bit-new-register-model to one four-register
nonabelian group, one fixed three-label alphabet, one noncentral two-root
target, and the predeclared q<=4 search. It does not settle q=5..8, arbitrary
nonabelian groups, arbitrary target tuples, or a physical supplier. Closed
PR #1333 established a rank-sum minimum with the full rank-one affine-label
alphabet; this result restricts to three fixed generators and uses a
different noncentral target. Open UT4 PRs #1662, #1680, and #1690 concern
central targets. Active Discussion #1738 concerns a three-register UT3
central pair; #1740 concerns an S4 pair; #1743 concerns helper-star costs.
These are nearby search families, not the target and endpoint proved here.

The live overlap refresh paginated all 434 open PRs and all 392 Discussions
with no warnings. Direct checks of active claims #1738, #1740, and #1743 found
different groups, targets, and mechanisms. The claim was kept local during
the initial GraphQL rate limit, then posted after reset as
[Discussion #1759](https://github.com/CrocSwap/integer-mult-bounds/discussions/1759).
The finding and handoff comment links this package's [PR #1761](https://github.com/CrocSwap/integer-mult-bounds/pull/1761).
TASK.json records exact refresh timestamps, active heads, and limits.

The current selected record is a maintainer-reviewed conditional finite
construction, with kappa 836330098538459/500000000000000000. Its review is
docs/research/community-batch1099-review.md, its selected source manifest is
research/community-frontier1094-audit/SELECTED-SOURCE.json, and its assembly
certificate is research/community-frontier1094-audit/ASSEMBLY.json (SHA-256
1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045). The
selected record names the integration receipt and reproduces with
make frontier1094-verify. Exact base-commit Git blob and SHA-256 pins for
these artifacts and the selected record are in SOURCES.json. No selected
result, upstream source, or pre-existing certificate was changed; this
package adds its own certificate.json.

The task's baseline positive control returned
PASS_RESEARCH_BASELINE_BINDINGS_ONLY: the complex primitive remains binding.
Under the retained planning transfer, the baseline arithmetic reports a
required bit multiplier of 5.827190801985042 for the target kappa 1/100.
This is source-binding and arithmetic evidence only, not a full supplier
replay or a universal transfer bound. The exact output is preserved in
BASELINE.json, and the baseline script is pinned in SOURCES.json. Consequently
this finite bit-model result does not change the selected frontier.

Prepared by Cinna Davis (@1337isnot1337) with substantial OpenAI Codex
assistance in mathematics, implementation, verification, and writing.

## Open next questions

Does this fixed endpoint have a word of length five, six, or seven in the same
full group-algebra alphabet? Start from the q<=4 pair table and use a
three-factor split, with a cost screen before retaining any new construction.
Even a positive formal word would need a complete supplier, recursive-moment,
and assembly argument before any kappa claim.

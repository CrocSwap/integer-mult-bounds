# Exact capped concave tariff for repeated A2 two-letter targets

This is a formal tariff theorem, not a native implementation or supplier bill.
The generator-selective cut method is credited to Adam Gall/PR1941 and Ross
Richardson/PR1966; the model and classical packing lemma follow Benny Zhao /
zhaobenny's PR6817. The contribution is the complete st price for every
remainder, not a new cut or packing principle.

## Model and theorem

Let K be any field, G=S3=<s,t | s²=t²=e,(st)³=e>, and d,b,r positive integers
with finite r≥d. Work coefficientwise in M_r(K[G]). A paid factor is

    F_u(A)=I+([u]−[e])A,   u∈{s,t},   0<rank_K(A)≤b.

The scalar matrix A is arbitrary: it need not be idempotent, and paid factors
are not assumed invertible. Arbitrary interleaved GL_r(K) matrices with scalar
[e] coefficients are free. There are no free address maps, resets, discarded
outputs or clean allocations. The complete endpoint is

    T_d=diag([st],…,[st],[e],…,[e]),
              d copies

so every spectator has arbitrary input and returns exactly, with no leakage.
The product convention is [st]=[s][t]; the rightmost factor acts first.

Let f:{0,…,b}→R be nonnegative, nondecreasing, f(0)=0, with nonincreasing
successive differences. Charge each paid factor f(rank A), identically for
s and t. Define

    P_(b,f)(d)=floor(d/b)f(b)+f(d mod b).

**The exact minimum cost over finite legal words for T_d is**

    2 P_(b,f)(d).                                      (1)

This includes every field characteristic, every finite number of restored
dirty spectators, nondivisible d, b=1 and b>r. It asserts neither a unique
minimizing profile nor a classification/minimum count of calls. Flat or zero
prices are allowed.

## Two credited generator-selective cuts

Use the left regular action λ of G on its six distinct basis labels over K,
and tensor with K^r. A formal matrix word therefore induces a linear map on
V=K[G]⊗K^r, preserving multiplication. This is a lower-bound image; attainment
below will be checked in the full formal algebra.

For a partition V=V_+⊕V_− put q(X)=rank(X_−+). For arbitrary linear X,Y,

    (XY)_−+=X_−+Y_+++X_−−Y_−+,
    q(XY)≤q(X)+q(Y).                                  (2)

No factor's invertibility is needed. Choose V_+=span{e,t}⊗K^r, with the other
four group labels in V_−. Left multiplication by t preserves {e,t}; hence
q(F_t(A))=0. Left multiplication by s sends its two labels to s,st, both
outside the pair. Its crossing matrix consists of two disjoint permutation
entries, tensored with A. Therefore

    q(F_s(A))=2 rank_K(A).

The identity subtraction has no crossing block. Every free scalar GL_r(K)
also has crossing rank zero: it mixes roles within each group label, not
labels across the cut. Finally st sends e,t to st,s, both outside the pair.
The target crosses on precisely its d active roles, giving q(T_d)=2d.
Applying (2) to the entire word yields

    sum_(s-calls) rank A ≥ d.                          (3)

For the other cut take V_+=span{e,s}⊗K^r. Now s preserves the pair, while t
sends it to t,ts and st sends it to st,sts, again outside. The same calculation
gives

    sum_(t-calls) rank A ≥ d.                          (4)

These statements hold even when free maps mix productive and dirty spectator
roles. In characteristic two, minus equals plus in the paid formula, but
the six group labels remain distinct and the two crossing entries remain
independent. The factor 2 is an ordinary dimension count, not a scalar whose
inverse is used. No semisimplicity, root-sign specialization, augmentation,
paid projector or nonsingularity hypothesis enters (2)–(4).

## Classical capped packing

For integers 1≤k_j≤b with sum k_j≥d, the standard concave concentration lemma
gives

    sum_j f(k_j)≥P_(b,f)(d).                           (5)

For completeness, permit zero parts temporarily. If 0<a≤c<b, transfer one
unit from a to c. The cost change is
`[f(c+1)−f(c)]−[f(a)−f(a−1)]≤0`. Continue with this pair until one part is
zero or b, decreasing the number of intermediate parts. Repetition leaves full b-parts and
at most one remainder. For the original total M this gives P_(b,f)(M).
This packed function is nondecreasing: increments within a block are those
of f, and the step into the next full block is f(b)−f(b−1)≥0. Thus M≥d proves
(5). For b=1 the argument is immediate. This is PR6817's cited classical
packing argument, not a new optimization theorem.

Apply (5) separately to the s ranks in (3) and t ranks in (4). Their actual
costs add, proving the lower bound (1), even with singular/nonprojector paid
couplings and arbitrary free scalar interleavings.

## Full formal attainment and boundary

Partition the first d coordinate roles into floor(d/b) disjoint blocks of
size b and, if nonempty, one remainder block of size d mod b. Let E_B be a
block's coordinate projector. The legal factors obey the full algebra identity

    F_s(E_B)F_t(E_B)=I+([st]−[e])E_B.

Indeed they act as [s][t] on that block and as identity on its complement.
Different blocks have disjoint supports. Their products are exactly T_d,
including every spectator column and row. No free basis operation, preparation
or restoration is needed. Each letter's cost is P_(b,f)(d), proving attainment.
If b>r≥d, there are no full b-blocks; the one rank-d remainder is legal, so
the apparently unavailable rank b is never invoked. Empty remainders require
no rank-zero paid call.

PR6817 already covers divisible identical targets, every single-reflection
remainder and d=3,b=2 for st. Formula (1) completes this particular two-letter
target's remainder family. It does not extend to the different longest target
sts, heterogeneous targets, other reflection alphabets or tariffs. In
particular the combined root-orbit packing floor alone must not replace the
two separate letter constraints. The result does not reclassify prior rank-one
st words or claim an unrestricted circuit optimum outside this paid grammar.

## Credit and limits

Credit Adam Gall1941 and Ross Richardson1966 for the established separate-letter
cut/rank-volume method; David Arias2738 and its retained root/model lineage;
Benny Zhao/zhaobenny6817 for the all-field arbitrary-coupling model, concave
packing and existing divisible/single-reflection/three-target st results;
Nick Petalas5083 for the distinct longest-element batching schedule; and
ToikY6550 for the earlier all-field rank-one st classification. Standard rank
subadditivity and tensor-rank multiplication are elementary methods.

Substantial source-aware OpenAI Codex assistance is disclosed. The coordinator
proposed this recipe during source orientation, before expanded review identified
the established separate-cut predecessors; this is not a blind derivation or
literature-priority claim. Finite checks, if provided, corroborate
the written theorem and full formal endpoints, not all possible words. No
native rank primitive, physical price for scalar mixing, owned allocation,
restoration/routing/precision/stock/caller bill, all-size recursion or selected
supplier is supplied. All five framework assumptions and the frontier remain
unchanged. No human or proof-kernel acceptance is claimed.

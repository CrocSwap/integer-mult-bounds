# A common owner code with moving Gaussian stages

Cinna Davis; substantial OpenAI Codex assistance. Apache-2.0.

This is a changed local interface and a rejected direct caller substitution.
It is not a supplier, a multiplication theorem or a kappa improvement.
The normalizer and coded-producer premises are Dillon's PR4933 and
Dugongue's PR4929, respectively. Their complete native word is not replayed
here. The proof below states exactly where those premises are used.

## 1. Stage-local normalizers cannot give a common code

Let the binary label space be a direct sum `Z + V_s + V_t + W`, where
`Z` is the shared central block and `V_s,V_t` are distinct fresh blocks.
At stage s each invertible label map `G_i,s` is supported on `Z+V_s`:
it preserves this subspace and is identity on its displayed complement.
Require `G_i,s Z = L_i,s`, with `L_i,s` distinct for different owners i.
The signed monomial normalizer K_i,s has this label map. Arbitrary
nonzero phases do not change the following necessary condition.

For a fixed scalar owner matrix A, write the physical code block as

    C_s[i,j] = A[i,j] K_i,s^-1 K_j,s.

Suppose `A[i,j] != 0` and `i != j`. If `C_s[i,j]=C_t[i,j]`, equality of
the nonzero monomial matrices implies equality of their label maps:

    H = G_i,s^-1 G_j,s = G_i,t^-1 G_j,t.

The first expression preserves `Z+V_s`; the second preserves `Z+V_t`.
Both inverses have the same properties. Thus H preserves their
intersection Z bijectively. It follows that

    G_j,s Z = G_i,s H Z = G_i,s Z,

contradicting the distinct-line premise. This rules out a common code
within this stage-local monomial class, for any choice of its normalizers.
It does not enumerate just the particular source normalizers. It applies
to arbitrary positive digit-column width by taking Z to have that width
and each fresh block eight times that width.

For the actual 112 source ports the 112 binary lines are distinct and A
has zero diagonal and 5,824 nonzero ordered off-diagonal blocks. All
5,824 therefore obstruct common-code equality. In the pinned source
choice, block (0,1), coefficient -1/2, maps input label 1 to label 22 at
the anchor stage and 5,632 at the fresh stage in the 17-bit embedding.
Different output labels suffice irrespective of phase.

The hypotheses matter. Equal-line owner pairs can have identical
normalizers and hence common identity relative maps. Equal stages have
the same code. The global construction below deliberately moves
spectators and lies outside the stage-local premise.

## 2. A constructive escape by moving coordinates

Add one common eight-axis anchor block V_0, distinct from all fresh stage
blocks V_s. Let P_s exchange V_0 and V_s and fix the central axis and
all other labels. These are real, self-inverse coordinate permutations.
Let K_i,0 be the pinned real signed anchor normalizers. Instead of the
stage-local normalizers `K_i,s=P_s K_i,0 P_s^-1`, use the intertwiners

    K'_i,s = P_s K_i,0.

They still take the central line to the actual stage-s port line, but
move the inactive fresh labels into the anchor. Their relative maps are

    (K'_i,s)^-1 K'_j,s = K_i,0^-1 K_j,0.

Thus they give the same physical owner code C_0 at every stage, including
all signed phases. This is an exact constructive common code once
spectator motion is allowed. It is not a centralizing-normalizer theorem:
the K'_i,s generally intertwine two stage Gaussians rather than commute
with the stage-s Gaussian.

Here is the resulting concrete endpoint without assuming any new native
semantics. Let Q be the central Gaussian, D_0 the product on the eight
anchor axes, `D_s=P_s D_0 P_s^-1`, and
`C_s=P_s C_0 P_s^-1`. All P_s commute with Q. The inherited PR4933 ABI is

    F_s = diag(D_s,D_s) L(C_s Q^-1),
    B_s = diag(D_s,D_s) U(-Q C_s),

where L(T)=[[I,0],[T,I]] and U(T)=[[I,T],[0,I]]. Append P_s to both
main input banks, before this ABI. Direct block multiplication gives

    F_s diag(P_s,P_s) = diag(E_s,E_s) L(C_0 Q^-1),
    B_s diag(P_s,P_s) = diag(E_s,E_s) U(-Q C_0),
    E_s = P_s D_0.

These equations require no commutation of C_0 with Q or P_s. Their
source maps are invertible on every arbitrary main input. They introduce
no CLEAR or claimed independent helper input. The source producer's
autonomous helper outputs remain its inherited premise. The inserted
permutations act on the 224 main fields only. This gives a complete
local input/output contract, not a complete controller.

Every construction here lifts to arbitrary digit-column width: swap
entire blocks columnwise; lift the source signed K_i columnwise with its
correct accumulated phase; execute the owner scalar coefficients once
on the owner factor. No tensor power of a sum of owner blocks is used.

## 3. Noncommuting E_s words retain distinct-stage Gaussian ranks

Consider distinct nonzero stage labels s_1,...,s_k in chronological
order. Write `P_word=P_s_k ... P_s_1`. Moving coordinate permutations
to the left gives the exact formula

    E_s_k ... E_s_1
      = P_word D_0 D_s_1 ... D_s_(k-1).

One proof proceeds inductively. In the normal form P_word D_support,
left multiplication by `P_s D_0` adds the D block at
`P_word^-1(0)`. For distinct previous swaps this block is the most
recent preceding stage label, or 0 for the empty word. This gives the
displayed support and leaves each Gaussian exponent equal to one.
The D blocks commute because their coordinates are disjoint.

After removing the explicit monomial P_word, the word therefore has
8k Gaussian axes; adjoining Q or Q^-1 adds one. This is the exact
Gaussian support rank of this operator, not proof that the operator is
an admitted recursive target. P_word removal, ambient width, spectator
multiplicity and completion still require a supplier bill.

The E_s themselves do not commute. Distinctness also matters: the word
E_1^3 has only eight odd Gaussian axes after monomial removal rather
than 24, since `E_1^2=D_1 D_0` and D_0^2 is monomial. The checker tests
all 1,956 distinct ordered nonempty words on six stages and this
repeat control. Those checks corroborate the induction; they do not
establish arbitrary k by enumeration.

## 4. The direct controller substitution still fails

The inherited relation is `[C_0,D_0 Q]=0`. Since `E_s Q=P_s D_0 Q`,

    [C_0,E_s Q]=0  iff  [C_0,P_s]=0.

Indeed multiply the commutation equation on the right by
`(D_0 Q)^-1`, using its commutation with C_0. But
`P_s C_0 P_s^-1=C_s`, and Section 1 shows `C_s != C_0`.
For the source choice their binary maps differ in every one of the
5,824 nonzero code blocks. This also gives an actual failed block
identity, rather than only an unavailable sufficient hypothesis.
Put `F_standard(E)=diag(E,E)L(Q^-1)` and
`G(C)=diag(C,Q^-1 C Q)`. The proposed forward gauge is

    diag(C,I) F_tilde diag(I,C) = G(C) F_standard(E).

Its lower-left block difference is

    E C Q^-1 - Q^-1 C E = Q^-1 (E Q C - C E Q),

where E commutes with Q. This is nonzero by the preceding argument.
Thus PR4933's local forward gauge identity itself fails for E_s. Their physical
common code and their rank-preserving products do not by themselves
license that caller substitution. A different caller must prove its
own full block identities. This is a stop gate, not a universal
obstruction to moving-coordinate callers or coded recursive families.

## 5. Obligation and cost ledger

| Obligation | Status |
|---|---|
| Source arbitrary-input coded native ABI and helper autonomy | Inherited PR4929/PR4933 premise, exact source pointers retained |
| Stage-local common-code exclusion | Proved above for the stated support/line contract |
| Global common code and transported F/B endpoints | Exact construction and block proof above |
| Distinct-stage product ranks | Proved above; finite independent arithmetic check supplied |
| Extra coordinate permutations | 224 whole-main-field P_s maps per transported FULL; finite-tape price unknown |
| Anchor space | Eight additional label axes, with every added spectator and completion charge unpriced |
| Original native child/helper profiles | Source profiles retained as local premises; no complete new supplier invoice |
| Center deletion | Existing center-free producer property, not new independent credit |
| Complete coded controller, restoration and terminal decoding | Unknown; direct inherited gauge fails Section 4 |
| Precision, routing, recursive compiler, BIT and outer transfer | Unknown for this interface |

For n fresh eight-axis stages plus Q, the original ambient width
8n+1 becomes 8(n+1)+1. Those eight new axes are never free stock or
productive main Gaussian credit. The preserved rank of a target word
does not remove this change in its surrounding width. Unknown costs
are not zero. The next construction must justify its full completed
moment before a larger search or claimed kappa gain.


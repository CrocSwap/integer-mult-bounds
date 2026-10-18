# P112 rational decoder cost floors: 334 at minimum length, 308 within both spans

This is a sharp restriction on the fixed changed-triad mask of PR2757, not a universal rational-decoder obstruction.

## Statement and scope

Use PR2757 head `c8216fca1ed2a301a95e7e0b1e5844d4cfda02c6` and its fixed CANDIDATE.json, SHA256 `dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b`. Keep its 112 ports, 37 orthonormal triads G1,...,G37, residual line G0, and full-group scalar mask. Write E_g for each binary group space. Entries K_pq with p!=q are forced zero unless E_owner(p) is orthogonal to E_owner(q), and all diagonal entries equal one common nonzero rational c.

For a nonzero rational rank-one term u_t v_t^T, charge rho(S_t,T_t), the F2 pairing rank between the sums of all complete group spaces touched by u_t and v_t. Absorb any nonzero scalar coefficient into u_t; this changes no supports or charge.

**Theorem.** Every valid fitting decoder expressed as exactly 57 nonzero rational rank-one terms has total port-space charge at least 334. The indicator decomposition in PR2757 attains 334, so this lower bound is sharp within the exactly-57-term class. Therefore a decoder with total charge at most 296 needs at least 58 nonzero scalar rank-one terms.

The 334 theorem alone does not exclude decompositions with more than 57 terms, even when their sum has matrix rank 57. Section 5 gives a separate 308 bound when both factor families remain in the rank-57 fitting matrix's spans. Neither result excludes fitting matrices of larger rank, altered covers, block-valued factors, or a changed physical tariff. No claim about a native supplier or exponent follows.

## Exact geometric premises

The source-bound standard-library checker `check_rank_tight_floor.py` imports no predecessor executable and recomputes the following from the pinned selected labels. It uses F2 only to compute spaces and their tariff; it never reduces rational decoder coefficients modulo two.

Let I contain all three ports of each odd group G1,G3,...,G37. Every two groups in this list are nonorthogonal, so K_II=I57 after normalization c=1. Let R be the line and the even groups. Among the odd groups, the only allowed neighbors of an even group 2j are {2j-1}, except that group24 has {3,23}. The line has allowed odd neighbors {15,27}. In addition:

- E4 is not orthogonal to E24, and group4 has only odd neighbor3.
- E28 is not orthogonal to E0, and group28 has only odd neighbor27.
- For j=1,...,18, let H_j=E_(2j-1)+E_(2j). The two summands are orthogonal nondegenerate three-spaces, so rho(H_j,H_j)=6.
- Let J=E37. For every ordered pair i,j in {1,...,18}, rho(J+H_i,J+H_j)>=6. The 324 exact ranks have histogram {6:11,7:93,8:171,9:49}.
- E0 is orthogonal to E15 and E16, so rho(E0+H_8,E0+H_8)=7.

The lower bound for J+H_i cannot be replaced by a blanket bound rho(H_i,H_j)>=6. The latter is false: the bare pair ranks have histogram {4:20,5:178,6:126}. This is a useful scope control.

## 1. Normal form of every rank-57 fit

Normalize the common nonzero diagonal c to one by scaling the full fitting matrix and one factor side. Supports and tariffs are unchanged. Order coordinates as I,R and write

    K = [ I57   A ]
        [ B     D ].

The principal identity forces rank(K)>=57. An expression with 57 rank-one terms forces rank(K)<=57. Therefore rank(K)=57, and the Schur complement gives D=BA.

The allowed-neighbor list determines the block supports of A and B. All even groups except24 can interact with only their matching odd group. At group4,

    I3 = D_4,4 = B_4,3 A_3,4,

so B_4,3 and A_3,4 are invertible rational 3-by-3 matrices. The forbidden blocks D_4,24=D_24,4=0 imply

    B_4,3 A_3,24 = 0,    B_24,3 A_3,4 = 0.

Thus A_3,24=B_24,3=0. Group24 also interacts only with its matching odd group23.

Likewise the identity at group28 makes B_28,27 and A_27,28 invertible. Since the line and group28 are not orthogonal, D_0,28=D_28,0=0. Hence

    B_0,27 A_27,28 = 0,    B_28,27 A_27,0 = 0,

and B_0,27=A_27,0=0. The line interacts only with odd group15.

Consequently, for each matched pair (2j-1,2j), A and B contain inverse 3-by-3 maps between the odd and even coordinates. The line is described by a general rational row b=B_0,15 and column a=A_15,0 with ba=1. There is no need to make a or b coordinate vectors. Group37 has no R-neighbor and remains an isolated I3 block. The remaining entries of D are determined by BA. In particular, the extra allowed free edges cannot be used at matrix rank57.

## 2. Consequences for an arbitrary 57-term factorization

Write K=UV^T with U,V of size112-by-57, one column per nonzero term. Set P=U_I and Q=V_I. The identity minor gives

    P Q^T = I57,    Q^T P = I57.

Both P and Q are invertible. Comparing the I,R blocks gives

    U_R = B P,    V_R = A^T Q.

For every factor column, nonzero odd coordinates in any paired group are therefore equivalent to nonzero even coordinates in its partner, on each factor side separately: the associated maps are invertible. A factor vector whose retained coordinates are confined to group37 is physically supported only in group37. Conversely, every nonzero paired component touches both complete three-spaces in that pair for tariff purposes.

For term t, the dual-basis identity gives q_t^T p_t=1. Thus there is at least one retained scalar coordinate where both factor vectors are nonzero.

If a common nonzero retained coordinate lies in a paired group, both full supports include its entire H_j, and monotonicity of pairing rank under enlarging either space gives charge at least6.

Otherwise, every common retained coordinate is in group37, so both factors have nonzero J components. If neither factor is supported only in group37, their supports include J+H_i and J+H_j for some i,j, so the certified 324-case bound again gives charge at least6.

It follows that every term of charge below6 has at least one factor supported only in group37. Such a term has charge exactly3: one side is J, and the other includes J; its pairing rank is at least rho(J,J)=3 and at most dim(J)=3.

## 3. At most three terms can cost below six

Let L_U be the set of column indices for which p_t is supported in the three-coordinate subspace W corresponding to group37. Let L_V be the analogous set for q_t. The previous section places every term of charge below6 in L_U union L_V; conversely every index in that union has charge3.

Put alpha=|L_U|, beta=|L_V|, gamma=|L_U intersection L_V|. Since P and Q are invertible, their indicated columns are independently linearly independent. The restricted pairing matrix Q_(L_V)^T P_(L_U) is the corresponding submatrix of I57, hence has rank gamma.

The beta independent columns of Q_(L_V) lie in the nondegenerate three-coordinate space W. The common annihilator of these columns in W has dimension 3-beta. The kernel of their pairing on the alpha-dimensional span of P_(L_U) has dimension alpha-gamma, so

    alpha-gamma <= 3-beta.

Therefore |L_U union L_V|=alpha+beta-gamma<=3. This uses rational linear algebra and does not assume positivity, symmetric factors, disjoint supports, or an integral reduction.

## 4. The residual line supplies the last unit

The scalar diagonal at the residual port is one, so at least one term has both u_(0,t) and v_(0,t) nonzero. From U_0=b P_15 and V_0=a^T Q_15, that term has nonzero components in odd group15 on both sides, and then in even group16 on both sides by the invertible partner maps. Its two support spaces both contain E0+E15+E16, whose pairing rank is7.

This term is not one of the group37-only terms. If l<=3 terms have charge3, the other57-l terms cost at least6 and at least one costs at least7. Thus

    C >= 3l + 6(57-l) + 1 = 343-3l >= 334.

The PR2757 indicator construction has exactly three group37 singleton terms of charge3, 53 ordinary paired terms of charge6, and one line-bearing term of charge7, attaining334.

## 5. Any number of factors within the fitting matrix's spans costs at least 308

This is a scoped extension of the rank-57 argument for the pinned PR2757 mask.
It does not cover arbitrary higher-rank fitting matrices, or factorizations
whose source or reader factors have components outside the fitting matrix's
column or row space.

Normalize the diagonal to one. Let K be any rank-57 fit on this mask, with
the normal form `K = [I, A; B, BA]` proved above. Assume the columns of U lie
in col(K), and the columns of V lie in col(K^T), for a factorization K=UV^T.
Write P=U_I and Q=V_I. The two span assumptions give

    U = [ P ],    V = [ Q    ],    P Q^T = I57.
        [ BP]        [ A^T Q]

Thus the retained rank-one terms satisfy

    sum_{t=1}^m p_t q_t^T = I57,       m = 57+s, s >= 0.

The invertible paired maps force the same paired group support on each side.
The residual coefficients are b p_(15,t) and a^T q_(15,t); a and b need not be
coordinate vectors. No change of basis or reduction of coefficients modulo two
is needed for this extension.

We charge every term by the full port-space pairing tariff. Scalar entries
and even denominators are unrestricted. Zero terms are discarded before m is
counted.

### Finite geometry premises

Partition the 57 latent coordinates into 19 blocks of size three: eighteen
paired components and J=G37. A nonzero paired component touches its entire
nondegenerate six-space H_i. A nonzero physical residual coefficient also
touches G0; ignoring that extra line only decreases the tariff. A nonzero J
component touches the nondegenerate three-space J.

The independent closure checker reconstructs the pinned labels and proves:

- rho(J,J)=3 and rho(J,H_i)=rho(H_i,J)=3 for every i.
- rho(H_i,H_j)>=4 for all 324 ordered pairs.
- rho(J+H_i,J+H_j)>=6 for all 324 ordered pairs.
- All spans generated by the 19 component spaces form an explicitly closed
  set of 40 subspaces. Among pairs of these spans that each contain a paired
  component and have pairing rank below six, the maximal component-support
  rectangle sizes are as follows:

      rank 4: 1 by 1 only (20 ordered span pairs)
      rank 5: 1 by 1 (178), 1 by 2 and 2 by 1 (33 each),
              1 by 3 and 3 by 1 (4 each).

  No such rectangle has a component on both sides. Taking the maximal closure
  supports is conservative: an actual term can touch fewer components.
- The residual's actual support G0+G15+G16 is nondegenerate of rank seven.

### Discount bound from an acyclic subset

Call a term pure if at least one of p_t,q_t is supported entirely in J. Each
nonzero pure term has tariff exactly three, including when the other side has
no J coordinate. This uses the separate rho(J,H_i)=3 premise; diagonal overlap
is not assumed.

Every nonpure term has tariff at least four. Let L4 and L5 count its terms of
actual tariff four and five. Their component support rectangles are disjoint:
a common paired component would force tariff at least six, and J on both sides
would force at least six by the enlarged-pairing premise.

Choose a uniformly random order of the 19 components, and select a low-tariff
term if every component in its left support precedes every component in its
right support. Its probability is 1/binomial(a+b,a). The finite census shows
this probability is exactly 1/2 for a tariff-four term and at least 1/4 for a
tariff-five term. The census ignores the residual line, so a tariff-five term
may have underlying rank four; that only increases its selection probability.

For any fixed order, the selected terms sum to a strictly block upper triangular
matrix N. Thus I_57-N is invertible, without any positivity or coefficient-size
hypothesis. If k terms were selected, the remaining m-k rank-one terms still
sum to I_57-N, so m-k>=57 and k<=s. Taking expectations yields

    L4/2 + L5/4 <= s,       hence 2 L4 + L5 <= 4s.

### Pure terms and the invoice

Let P be the number of pure terms. Restrict the identity to the other 54 latent
coordinates. Every pure term vanishes in this principal restriction, so its
rank 54 forces m-P>=54 and P<=s+3.

The residual diagonal is one, so some term has nonzero residual entry on both
sides. It is nonpure and has tariff at least seven. Therefore

    C >= 6m - 3P - 2L4 - L5 + 1 >= 334-s.

A second bound uses only the minimum nonpure tariff four and the same residual
term:

    C >= 3P + 4(m-P) + 3 >= 228+3s.

Consequently

    C >= max(334-s, 228+3s) >= 308       for integer s>=0.

The integer minimum of the displayed bound is 308, at s=26. This already
exceeds the necessary positive-saving allowance 2672/9 (integer C<=296).
The weaker first inequality alone would require m>=95 to reach that allowance;
the second inequality eliminates that possibility within this model.

This closes overcomplete scalar decompositions only when BOTH factor spans
remain canonical. The ambient 112-coordinate problem can introduce exterior
components, including components that cancel between terms; those are outside
this proof. Higher-rank fitting matrices are also outside the proof. The
finite geometry check is not a native implementation or a supplier theorem.

## What this changes

Minimum scalar rank57 and a low-charge decoder are different optimization goals. All exactly57-term rational factorizations fail the favorable positive-saving requirement C<2672/9. Any target C<=296 must use at least58 terms, with actual extra directions/cancellation; arbitrary diagonal gauges, groupwise rational changes of basis and asymmetric rank-tight factors cannot suffice. The additional bound of 308 applies to any term count when both factor families remain in the rank-57 fitting matrix's column and row spaces. There is no bound here for arbitrary exterior factors or higher-rank fitting matrices.

The finite geometry was separately recomputed by another AI agent, including the complete 324-case histogram; that agent also audited the normal-form elimination and the pure-factor dimension argument. This is independent AI checking, not independent human review or proof-assistant formalization.

## Replay and credit

From the repository root, Python 3.12 standard library only:

```sh
python3 -I -O -B research/p112-rational-decoder-gate/check_rank_tight_floor.py
python3 -I -O -B research/p112-rational-decoder-gate/independent_cost_floor.py
python3 -I -O -B research/p112-rational-decoder-gate/check_overcomplete_closure.py
```

The first checker authenticates the candidate, selected archive and payload,
then recomputes every finite geometric premise. The second uses independent
binary elimination, checks all 324 pairings, and replays dense rational fixtures
with non-coordinate residual maps and uncancelled even denominators. It rejects
granting either critical forbidden edge, replacing full groups with original
labels for pricing, and corrupting the residual diagonal. These finite checks
support the symbolic proofs above; they do not formally verify its universal
quantifiers. The separate closure checker reconstructs all 40 component spans and rejects both a missing seed and a missing generated span. Its echelon representation is independent of the first checker's explicit vector-set closure.

This proof extends the pending PR2757 construction, whose earlier head is pinned
above. The selected P112 labels, tri-plane endpoint, strict mask and full-space
tariff retain their predecessor attribution in the package [README](README.md).
Prepared by flyingviper with substantial OpenAI Codex assistance and separate
AI-agent checking. New work is Apache-2.0; no independent human review is claimed.

## Sharp any-length refinement

The valid 308 lower bound above is superseded, in exactly the same
both-canonical-spans scope, by [CANONICAL-SHARP-PROOF.md](CANONICAL-SHARP-PROOF.md):
`C >= 334+2s` for `m=57+s`. Keeping the identical pure-J count in the full
and ordinary-coordinate acyclic bounds closes the gap without new geometry.
The historical derivation and its checkers are retained as independent premises.

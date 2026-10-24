# Tight radical rank removes all dirty workspace

## Statement and cited premises

Let `a=(123)`, `b=(124)`, `c=aba^-1b^-1`, and `d=ab` in A4.
For every finite `r>=4`, the exact minimum number of paid factors for
`T_r=diag([a],[b],[c],[d],1,...,1)` is eight in the following model.
Work over `F2[A4]`. A paid factor is `D_N(g)=I+([g]+1)N`, where g is
a or b and `N=xy^T` is a binary rank-one idempotent, so `y^T x=1`.
Scalar `GL_r(F2)` maps are free. All r inputs are arbitrary, and the
complete formal operator must equal `T_r`. There are no clean roles,
COPY, ERASE, other address letters or free inverses. Restoration is paid.

The new assertion is that a hypothetical six-call word on any r roles
restricts to a legal six-call word on four roles. The eight-call conclusion
uses two cited premises, neither audited or replayed here.

* Cinna Davis #2116 excludes words of length at most six on four roles by
  a finite exact group-algebra certificate. Sagar Thakrar #4032 retains
  that exclusion with two further exact joins.
* Sagar Thakrar #4032 proves `n_a,n_b>=3` and `n_a=n_b mod 3` at every
  finite role count. Its twisted-functional decompositions below have
  rank three for each letter. These are written all-role statements.

SOURCES.json pins both packages at the base commit. The six-call exclusion
remains a finite-certificate dependency. No wholly written replacement for
that exclusion is claimed.

## 1. Normalize scalar maps

Binary scalar conjugation preserves rank-one idempotents. Collect all free
scalar maps at one end of the word. Augmentation to F2 sends every paid
factor and `T_r` to `I_r`, so the collected scalar map is `I_r`. We may
therefore use a pure paid word in the original target coordinates.
Let H be the binary span of the first four coordinate vectors.

## 2. Rank saturation

Over any extension K of F2, suppose `D=sum_(j=1)^q x_j v_j`, with binary
columns `x_j`, K-rows `v_j`, and `rank_K D=q`. The column span of D is
contained in the K-span of the q columns `x_j`. Both spaces have dimension
q and hence are equal. Every `x_j` belongs to `col_K D`. If that space is
a coordinate space, all entries outside it vanish in every `x_j`.

## 3. Apply equality to both letters

Assume a six-call word equals `T_r`. The inherited floors force
`n_a=n_b=3`. In #4032's base-a splitting, each paid factor is `B_k E_k`.
The semisimple factor is `B_k=D_(N_k)(a)` for an a-call and
`B_k=D_(N_k)(a^2)` for a b-call. The latter has radical part
`E_k=I+([d]+1)N_k` because `b=a^2 d`. Set `C_k=B_(k+1)...B_L`.

The inherited twisted functional Phi to F4 gives

```text
diag(0,mu(d),mu(c),mu(d),0,...,0)
  = sum_(b calls k) aug(C_k)^-1 mu(d) x_k y_k^T psi(C_k).
```

The three nonzero diagonal entries are nonzero because mu is injective
on the Klein four subgroup. Every `B_k` has augmentation `I_r`, since
`aug([a]+1)=aug([a^2]+1)=0`. Thus `aug(C_k)=I_r`, not an unspecified
invertible map. There are exactly three summands. Section 2 places every
b-call column in `H_b=span_F2(e_2,e_3,e_4)`.

Using base b instead and putting `e=ba`, the inherited defect is
`diag(mu(e),0,mu(c),mu(d),0,...,0)`. Its suffixes again have augmentation
identity. Section 2 places every a-call column in
`H_a=span_F2(e_1,e_3,e_4)`.

Consequently every paid output column `x_k` belongs to H. The rows
`y_k^T` may still read arbitrary extra dirty inputs.

## 4. Restrict each factor

In the split into H and its coordinate complement, write `x_k=(x'_k,0)`
and `y_k=(y'_k,y''_k)`. The column `x'_k` is nonzero and
`(y'_k)^T x'_k=y_k^T x_k=1`. Hence `N'_k=x'_k(y'_k)^T` is a nonzero
binary rank-one idempotent on four roles. Each factor has block form

```text
[ D_(N'_k)(g_k)    * ]
[       0         I ].
```

Taking the upper-left block commutes with multiplication of these block
matrices. The six restricted factors therefore have product `T_4`, in
contradiction to the cited four-role finite exclusion. Dependence on dirty
inputs in the upper-right blocks cannot change this product identity.

## 5. Exact minimum and limits

The inherited floors exclude lengths at most five. At seven calls they
allow only `(3,4)` and `(4,3)`, which violate `n_a=n_b mod 3`.
Section 4 excludes six. Separate-coordinate words `a`, `b`, `abba`, `ab`
use eight calls and extend by identity on every extra role. Eight is thus
exact for every finite r, using the cited certificate and written identities.

This is an abstract register obstruction, not a physical supplier. Other
fields, nilpotent couplings, changed alphabets and different targets are
outside the statement. No new kappa, selected-frontier change, full
multiplication theorem or proof-kernel acceptance is claimed.

## Credit

The compression argument is produced by Nick Petalas. Sagar Thakrar #4032
supplies the radical-rank decompositions, all-role floors and determinant
congruence. Cinna Davis #2116 supplies the model, target, direct word and
finite four-role exclusion. Retain Cinna Davis #2047/#2248/#2085,
juper997 #1478, woklerx #1443, Gareth Davidson #1333, commdata2338 #1414,
eumemic #288, Ali Romman #468 and the register-model lineage credited by
those predecessors. Rank saturation and invariant-subspace restriction
are classical linear algebra. Apache-2.0.

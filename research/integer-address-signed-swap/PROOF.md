# Integer address SWAPs need a separately charged sign

## Exact model

Work in `M_R(F2[GL2(Z)])`. Each of the R scalar roles is an arbitrary dirty
binary stream. Address matrices act on its two integer coordinates; a NEG
below negates one **address coordinate**, not a binary payload value.
The paid labels are

```
a+ = [1 1;0 1],  a- = [1 -1;0 1],
b+ = [1 0;1 1],  b- = [1 0;-1 1],
nx = [-1 0;0 1], ny = [1 0;0 -1].
```

For any binary rank-one idempotent `N=uv^T`, with `v^T u=1`, a call is
`D_N(g)=I_R+([g]+1)N`. The prices of a+/a- are A, those of b+/b- are B,
and those of nx/ny are C. A,B,C are fixed nonnegative real numbers,
independent of role count, projector, state and word position. Arbitrary
scalar GL_R(F2) operations may be interleaved for free. No other address
map, clean input, reset, erasure, higher-rank paid unit or free restoration
is provided. Every actual inverse call is charged.

Let r roles have any mixture of the four signed anti-diagonal targets

```
 S=[0 1;1 0],  -S=[0 -1;-1 0],
 J=[0 1;-1 0], -J=[0 -1;1 0].
```

Let t of them be S or -S (determinant -1). The other r-t targets are J or
-J (determinant +1). The complete endpoint is their diagonal direct sum,
with identity on all R-r spectators and every off-diagonal coupling zero.
Assume finite R>=r>=0. Equality is coefficientwise in the full formal group
algebra, not equality only after applying a nonfaithful representation.

**Theorem.** The exact minimum price is

```
                  r*(2*min(A,B)+max(A,B)) + t*C.
```

At unit prices, this is 4t+3(r-t). The zero-target case is the empty word.
This is a sharp tariff in this specified relaxation, not a physical tape
invoice, primitive elapsed time, recursive supplier or new exponent.

## The credited ADD bounds survive the integer extension

Reduction modulo2 is a group homomorphism `GL2(Z) -> GL2(F2)`. Both signs of
a shear have the same image; nx and ny have identity image. All four targets
map to coordinate SWAP. The induced group-algebra map preserves a formal
identity and the scalar projectors, while deleting every address NEG call.

Thus PR2544's credited individual crossing bounds and PR2415/PR1989's total
bound apply to the remaining word, with the same arbitrary scalar mixing
and restored dirty spectators:

```
                  n_a >= r, n_b >= r, n_a+n_b >= 3r.       (1)
```

For clarity, each individual bound uses the upper/lower crossing block of
the natural two-dimensional representation. In address-major order, a paid
a has image `[I N;0 I]`, a paid b has `[I 0;N I]`, scalar mixing is block
diagonal, and each target has both crossing ranks one per target role.

The total bound acts on the three nonzero binary vectors, ordered
`(1,0),(1,1),(0,1)`. a and b are the two adjacent transpositions. Their
action on ordered distinct pairs splits increasing and decreasing pairs:
each paid shear has crossing rank one; SWAP has crossing rank three.
This is the predecessor's ordered-pair argument, not a new proof principle.

All these crossing ranks are subadditive because for a fixed decomposition
`(UV)_12=U_11 V_12+U_12 V_22`, hence `rank((UV)_12)` is at most the sum of
the two crossing ranks. No intermediate triangularity or commuting
projectors are assumed.

## A disjoint determinant-character charge

Take the homomorphism `det:GL2(Z)->{+1,-1}`, then its two-point permutation
representation over F2. The +1 element acts as I2, while -1 swaps the two
sheets. Extend it linearly to the full group algebra and tensor with roles.

Every ADD has identity image, hence crossing rank zero. Every paid address
NEG has image `[I+N N;N I+N]`, whose crossing block N has rank one. Free
scalar mixing is `[Q 0;0 Q]` and crosses zero. At the endpoint, exactly the
t negative-determinant targets exchange sheets, with crossing rank t.
The same subadditivity therefore proves

```
                              n_NEG >= t.                (2)
```

This is a separate necessary inequality. The ADD cuts charge no NEGs, and
the determinant cut charges no ADDs. Summing their weighted consequences
does not charge one instruction twice. In particular, even when an even
number of target swaps has overall determinant +1, its block crossing rank
is t rather than merely the parity of t. Scalar role mixing cannot hide it.

For A<=B, (1) gives
`A*n_a+B*n_b=A*(n_a+n_b)+(B-A)*n_b >= r*(2A+B)`.
The other ordering is symmetric. Adding C times (2) proves the lower bound,
including zero prices. Negative prices are excluded substantively: for R>=1,
a paid label followed by its charged inverse is a formal identity loop;
if its price is negative, arbitrary repetitions make the cost unbounded below.

## Literal integer attaining words

Use left-to-right matrix multiplication in the displayed words. Direct
integer multiplication gives

```
J  = a+ b- a+ = b- a+ b-,
-J = a- b+ a- = b+ a- b+,
S  = J nx,             -S = J ny.
```

Choose the cheaper three-shear orientation for each target and append the
one indicated NEG exactly for negative-determinant targets. On role j use
N=E_jj. Each factor changes only that role, so the full formal product has
exactly the prescribed monomial there and identity elsewhere. Concatenating
over r roles attains (1) and (2) jointly. It needs no extra role, scalar
preparation, inter-role copying or uncharged restoration. This verifies the
entire dirty endpoint, not only a natural-representation image.

## Uniform address realization and its boundary

Each attaining integer matrix word reduces to the same signed permutation
on `(Z/MZ)^2` for every M>=2. Every label is a unit coordinate ADD or address
NEG; neither whole-SWAP nor free coordinate relabeling is an extra paid label.
This supplies literal uniform upper identities, not their physical compiler,
prefix/suffix layout, word representation or recursively weighted cost.

The lower bound is for formal GL2(Z) identities, equivalently for a fixed
finite word that realizes the complete stream endpoint on integer addresses.
To see faithfulness of the latter implication, for any finite set of distinct
integer matrices choose v=(1,z) outside the finitely many collision values
of z. Each nonzero matrix difference kills at most one such v. The distinct
images then separate all coefficients of every finite group-algebra entry.
The same separation survives reduction modulo any sufficiently large M,
since a fixed finite list of nonzero integer differences cannot all vanish
modulo arbitrarily large M. Thus a fixed finite word valid at every modulus
in an unbounded family also satisfies the formal identity.

This is **not** a lower bound for every separately optimized word at one
finite modulus. At M=2, both address NEG labels become identity and J=S,
so three shears already swap coordinates. Nor does the theorem establish
admission for width-dependent alphabets, varying coefficient labels, changing
role counts, restricted input subspaces or incomplete spectator restoration.

The quotient images are lower-bound witnesses only. For example a+ squared
is a nonidentity integer matrix with identity image in both the mod2 and
determinant quotients. Adding `[I]+[(a+)^2]` to an endpoint entry is therefore
invisible to all four cuts but changes the full formal map. The verifier
uses exact formal coefficients for endpoints and checks this control.

## Credit

PR2544 at `9fb1552f12ca4777ca660461a8b602e709285f99` supplies the asymmetric
GL2(F2) tariff and its individual label counts, crediting Aaron Wang's
PR2444 handoff and Ross Richardson's PR1989/PR2415 total crossing bound.
Those bounds and standard rank subadditivity are reused, not claimed new.
The contribution is their source-bound integer-address extension with a
separately paid determinant-sign requirement, mixed signed endpoints and
the explicit finite-modulus boundary. Prepared for ywz65 with substantial
OpenAI Codex assistance, Apache-2.0. No human or formal-kernel review claimed.

# Binary Schur sharpness with identity pivots

**Written algebraic result with exact finite corroboration; no new kappa.**
Prepared for ssafwann with substantial OpenAI Codex assistance. Apache-2.0.

[PR4634](https://github.com/CrocSwap/integer-mult-bounds/pull/4634) attains
Schur-commutator rank `2d` in dimension `3d` with arbitrary invertible pivots,
and asks what changes if both pivots must be `I_d`. This package proves:

1. **Identity pivots force `n >= ceil(17d/5)`** for Schur-commutator rank
   `2d`. The sharper integer bound is
   `L(d)=min_{t=0,...,d} max(3d+2t,4d-3t)`. In particular `n=3d` is
   impossible for every positive `d`, and **`L(2)=8`**.
2. **Dimension `4d` suffices with identity pivots**, for every `d >= 2`.
   This improves the identity-pivot `5d` construction of
   [PR4617](https://github.com/CrocSwap/integer-mult-bounds/pull/4617).
   Together with the lower bound, **the identity-pivot minimum at `d=2`
   is exactly `n=8`**.
3. In the additional class where `H + H^2` is invertible, with `H` the leading
   block of `PQ`, **`4d` is optimal**. The constructed family lies in this class.

For unrestricted identity-pivot pairs with `d >= 2`, this proves only
`L(d) <= n_min(d) <= 4d`. The first remaining case is **`d=3,n=11`**:
the lower bound is 11 and the construction gives 12. The scalar `d=1`
minimum 5 is predecessor work in PR4609, not a new result.
All matrices below are over `F_2`, act on column vectors, and are algebraic
idempotents; symmetry or orthogonality in an inner product is not assumed.

## 1. The specialized factorization

Write, at one common `d + k` coordinate split,

```text
P = [ I R ],    Q = [ I L ],    PQ = QP = [ H T ],    k = n-d.
    [ C D ]        [ E F ]                 [ W * ]
```

Assume `P^2=P`, `Q^2=Q`, and `PQ=QP`. Their Schur complements are
`S=D+CR` and `Z=F+EL`. Nick Petalas's ordered factorization in
[PR4597](https://github.com/CrocSwap/integer-mult-bounds/pull/4597)
specializes to the following particularly useful pair of identities:

```text
U = C+E,    V = R+L,    J = H+H^2,
A = [ ZC  U ],          B = [ V  ],
                           [ RZ ]

[S,Z] = AB,             BA = [ J 0 ].                 (1)
                             [ J J ]
```

`A` is `k` by `2d` and `B` is `2d` by `k`. In characteristic two the
commutator is `SZ+ZS`. The forward factorization and its `2d` rank bound
are predecessor work; the reverse product is the step used here.

For completeness, all needed block algebra follows. Idempotence gives

```text
RC=LE=0,  DC=RD=FE=LF=0,
D^2=D+CR,  F^2=F+EL.
```

Thus `S^2=S`, `Z^2=Z`, `ZE=0`, and `LZ=0`. Commutation gives
`RE=LC=H+I`, `FC=W+E`, `RF=T+L`, and `DF+FD=CL+ER`.
Expanding the two Schur products with the block equations gives

```text
[S,Z] = W(R+L) + (C+E)T + CHL + EHR
      = (W+EH)(R+L) + (C+E)(T+HL).
```

The factors simplify in the displayed order:

```text
W+EH = FC+E+EH = (F+EL)C = ZC,
T+HL = RF+L+HL = R(F+EL) = RZ.
```

This proves `AB=[S,Z]` without interchanging noncommuting blocks.
For the reverse product,

```text
VZC = RZC,       VU = RC+RE+LC+LE = 0,
RZ^2C = RZC,     RZU = RZC.
```

Finally `P(PQ)=PQ` implies `RW=0`, so

```text
RZC = RFC+RELC
    = R(W+E)+(H+I)^2
    = (H+I)+(H+I)^2
    = H+H^2 = J.
```

This proves all of (1). In particular `rank[S,Z] <= 2d`. If `J` is
invertible, `BA` is invertible, so `A` is injective and `B` is surjective;
therefore `rank(AB)=2d`.

## 2. The dimension obstruction

Suppose `rank[S,Z]=2d`. Both factors in (1) then have rank `2d`.
Put `t=dim ker J`. Elementary block-row elimination in (1) shows
`rank(BA)=2 rank(J)=2(d-t)`. Sylvester's rank inequality gives

```text
2(d-t) = rank(BA) >= rank(B)+rank(A)-k = 4d-(n-d),
so n >= 3d+2t.                                             (3)
```

This inequality can also be read directly: `im A` has dimension `2d`,
and at most `dim ker B=k-2d` of it is lost on applying `B`.

The four joint-sector projectors are

```text
E11 = PQ,       E10 = P(I+Q),
E01 = (I+P)Q,   E00 = (I+P)(I+Q).
```

They are pairwise annihilating idempotents whose sum is `I_n`. Their images
therefore form a direct sum, so their ranks sum to `n`. Their leading
`d` by `d` blocks are respectively `H, I+H, I+H, I+H`.
Let `a=dim ker H` and `b=dim ker(I+H)`. Their ranks give

```text
n >= rank H + 3 rank(I+H) = 4d-a-3b.                       (4)
```

Moreover `ker J = ker H direct-sum ker(I+H)`, so `t=a+b`.
Indeed if `Jx=0`, then `x=(I+H)x+Hx`; the two summands lie respectively
in `ker H` and `ker(I+H)`, and the intersection of those kernels is zero.
Conversely both kernels are killed by `J=H(I+H)`.
Thus (4) implies `n >= 4d-3t`. Combining it with (3) gives

```text
n >= max(3d+2t, 4d-3t) >= L(d).
```

Three times (3) plus twice `n>=4d-3t` gives `5n>=17d`, proving the
simpler bound `n>=ceil(17d/5)`. This strictly excludes `n=3d`.
For `d=2`, the three possible `t=0,1,2` yield lower bounds `8,8,10`,
so `n>=8`; Section 3 attains it. For `d=3`, the four values are
`12,11,13,15`, giving the first remaining dimension 11.

If `J` is invertible, `t=0` and (4) gives `n>=4d`. That extra condition
is essential for this last bound. For rectangular factors, `AB` can have
rank `2d` while `BA` is singular. The credited PR4617 scalar witness has
`n=5`, `d=1`, rank `2`, and `J=0`; the verifier retains it as a control
against replacing (3)-(4) by the unjustified condition that `J` is invertible.

## 3. An identity-pivot construction in dimension 4d

Choose a binary `d` by `d` matrix `H` for which `H` and `I+H` are invertible.
In four blocks of size `d`, put

```text
G = [ I+H  I+H  I+H  H ],       X = [ I ],
                                     [ I ]
                                     [ I ]
                                     [ I ]

W0 = H^-1(I+H),

M = [ I  I   0   0  ],     P0 = diag(0,I,0,I),
    [ I  0   I   0  ]     Q0 = diag(0,0,I,I).
    [ I  0   0   I  ]
    [ I  W0  W0  W0 ]
```

Here `GX=I`. Each of the last three block columns of `M` lies in `ker G`,
and these `3d` columns are independent by their first three block rows.
Since `G` is surjective, they form a basis of `ker G`. The first block
column is `X`, complementary to that kernel. Thus `M` is invertible and
the first block row of `M^-1` is `G`.

Set

```text
P = M^-1 P0 M,          Q = M^-1 Q0 M.                 (2)
```

They commute and are idempotents, each of rank `2d`. Their leading blocks are

```text
G P0 X = (I+H)+H = I,    G Q0 X = (I+H)+H = I,
G P0 Q0 X = H.
```

Therefore (1) applies with this prescribed `H`. Since `J=H(I+H)` is
invertible, the Schur commutator has rank exactly `2d`. The four joint
sectors each have dimension `d`, so (2) attains the lower bound in the
invertible-`J` class.

Such `H` exists for every `d>=2`. Use the same elementary binary seeds as
lee-phys's PR4634 (their use is credited, not claimed as a new seed search):

```text
H2 = [0 1],        H3 = [0 0 1].
     [1 1]             [1 0 1]
                       [0 1 0]
```

`H2^2+H2+I=0`, so `H2` and `I+H2` are mutual inverses.
`H3^3+H3+I=0`, so `H3^-1=H3^2+I` and
`(I+H3)^-1=H3^2+H3`. For even `d=2r`, take `r` copies of `H2`.
For odd `d=3+2r`, take `H3` and `r` copies of `H2`. Direct sums preserve
both invertibility conditions. These identities prove the family for all
`d>=2`; finite checks are corroboration only.

For an immediately inspectable `d=2`, `n=8` instance, each string is one row:

```text
P8          Q8
10110011    10111100
01100010    01101000
10110011    10111100
01100010    01101000
00111011    10111100
00100110    01101000
10110011    00111110
01100010    00101001
```

Both leading blocks are `I_2`; both projector ranks and the six-dimensional
Schur commutator's rank are `4`. Appending zero blocks to both matrices
preserves the pivots and commutator rank, so every `n>=4d` is also attainable.

## 4. Verification and limits

From the repository root, using Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/identity-pivot-schur --check-only
python3.12 -B scripts/research_package.py --package research/identity-pivot-schur
```

The registered commands run `verify.py` in ordinary and optimized (`-O`)
modes, with warnings as errors. The verifier uses explicit exceptions, imports
no predecessor executable, writes no files, and prints
`PASS_IDENTITY_PIVOT_SCHUR` with a deterministic JSON receipt. It checks:

- The literal 8-by-8 witness, (2) for `d=2..12`, zero padding, and a
  mixed `d=3,n=13` fixture with nonzero singular `J` (direct sum with the
  credited scalar witness). All sharp pairs check both dimension inequalities.
- All 16 size-two and 512 size-three seeds; exactly 2 and 48 are admissible,
  and every admissible seed produces the claimed new identity-pivot pair.
- Every ordered commuting identity-pivot idempotent pair in `M3(F2)` at
  `d=1` (253 pairs) and `M4(F2)` at `d=2` (1,219 pairs). These check both
  factorizations, Schur idempotence/ranks, and all four joint sectors.
  Their commutator rank histograms are `{0:241,1:12}` and `{0:1147,1:72}`.
  These small calibration domains are not new minimal-dimension classifications.
- Eleven controls reject nonidentity pivots, broken idempotence, noncommuting
  projectors with the other premises preserved, three invalid seed conditions,
  nonbinary entries, two factor omissions, false sharpness of identical
  projectors, and the invalid rectangular-factor inference from Section 2.

The universal claims rest on the written proofs above. Independent human
review and formal-kernel verification are not claimed. No header-density,
physical execution, supplier, stock, precision or multiplication-exponent
result follows. No selected frontier is changed. Lean, Docker, the selected
cold replay and a global search over intermediate dimensions were not run.

This began on canonical main `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`,
priority revision 7, selected conditional kappa `0.00302015`.
The selected orientation command was attempted but stopped because the sparse
checkout omits `certificates/checkpoints/frontier4359.json`; no baseline pass
is claimed. None of the missing selected inputs is needed by this package.

`SOURCES.json` pins the task catalogue and selected record as historical
provenance only. The four pending predecessors are exact-head citations and
source hashes in `TASK.json`, not replay-time Git dependencies. The two scalar
control matrices are contained in `verify.py`, transcribed from the attributed
PR4617 source. The proof and checker otherwise need no external mathematical
inputs. [Discussion #4653](https://github.com/CrocSwap/integer-mult-bounds/discussions/4653)
is the canonical claim and handoff. The initial overlap snapshot covered all
423 open PR bodies, 3,586 Discussion records and all 5,860 in-scope local
notes; it did not search every code diff, closed PR, or unpublished result.

## Open next questions

**Can singular `H+H^2` attain rank `2d` for `L(d)<=n<4d`?** This is the remaining
minimum-dimension gap under identity pivots. The first instance is `d=3,n=11`.
A useful next step is to combine the two factors in (1) with the four joint
sector dimensions, or enumerate a specified complete sector/header model.
A failed random search would not settle the question. The obstacle is that
full rank of a rectangular product does not imply invertibility of its reverse.
This package stops at the proved boundary; it starts no further search campaign.

## Credit

- **Nick Petalas**, PR4597 at `dfeb8ca729a04aea4aa290438f2ed50a37a9c7cb`:
  ordered block-Schur factorization, `2d` rank bound and idempotent Schur lemma;
  PR4278 and its PR4259/PR4228 predecessors supply the shared-header context.
- **Ryanson Jonathan**, PR4609 at `eb5ccf9288808d973551e6264300d30d2f6e48a0`
  and PR4617 at `96c01a2124e234d798e9e97643c20fb5b430840d`: binary scalar
  witness and identity-pivot `5d` tensor family, with the Claude Code assistance
  disclosed in those packages. Their scalar matrices are reproduced as a control.
- **lee-phys**, PR4634 at `9f053f7051e5fc3327d4337bb4bd8ac52cf5fcd0`:
  optimal unrestricted-pivot `3d` family, the reused binary seeds and the
  explicit identity-pivot question, with OpenAI Codex assistance.
- **Cinna Davis**, PR4100: the earlier BIT request/complete-header setting.
  This side theorem closes no actual-caller or all-size transfer obligation.

The new reverse-product argument, rank-nullity/four-sector obstruction, `4d` change of
basis and self-contained checker were prepared for ssafwann with substantial
OpenAI Codex assistance (gpt-6-astra), by one agent. Repository tooling retains
Douglas Colkitt's and other contributors' attribution. Apache-2.0.

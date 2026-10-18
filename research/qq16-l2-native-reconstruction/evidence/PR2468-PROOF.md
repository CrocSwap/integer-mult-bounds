# Future-X query at the post-B1 cut

## Objects, available frames and extra storage

Use the actual disjoint QQ16 A/T minors and their ordinary complement U of
size 96. Set `C=x2_U` immediately after `B_1_2`. The retained contract gives
each X source p at owner d the completed native frame

```
T_X(d) = F_(d U1),      U1=L+E1.
```

The logical values C are arbitrary; in PR2443 they equal `-y_U^initial`.
No use is made of that equality, of selected endpoint values, or of a later
former-Y hole. The new word owns eight output arrays. It clears them before
use and returns them live in the common query frame. Those arrays are not
claimed to come free from the selected helper bank or to preserve dirty input.

For p in U, let `q_p` be its actual nine-bit normal and let `rho_p=rho_2(p)`.
This involution fixes q_p and exchanges its eight chart axes with E2. Write
`delta_p=q_p+lift_2(beta_p)`. The source's future-Y alignment and inverse are

```
A_p = M(rho_p, delta_p),
A_p^-1 = M(rho_p, rho_p delta_p),
M(g,a) f(d,z_1,...,z_lambda)
   = f(dg,z_1+d a,...,z_lambda+d a).
```

It changes owners and translates every payload layer. It does not apply g
to the payload address. All fields at different owner/port indices remain
independent. Every per-field map is a bijection of its full array.

## The unavailable zero-line shortcut and the exact repair

Let `T_c(d)=F_(d(E1+E2))` and let `D_p=M(rho_p,0)` be the logical route.
The retained bridge identity, for a Y-type source before chart 2, is

```
A_p [F_(d U1) C_(d q_p)^-1] = T_c(d) D_p.
```

Here `C_q=(1+i)I/2+(1-i)T_q/2` is the signed native rank-one line operator.
Since rho_p fixes q_p, omitting that inverse line leaves exactly C_q:

```
after A_p, the X source frame is T_c(d) C_(d q_p).
```

This residual is not the identity. At an identity-owner Fourier character
w with `q_p dot w=1`, its multiplier is i. The receipt supplies such a w for
each of the 96 actual ports. Therefore the future-Y scalar query cannot be
applied directly to these unnormalized X fields in its common output frame.
This does not exclude other physical implementations or other observation cuts.

Normalize source p first with `C_(d q_p)^-1`. Native frames are products of
commuting address translations/line operators, so this changes its frame
to the required Y type while retaining its arbitrary logical value. Applying
A_p then puts it in frame T_c with logical content D_p C_p. All 96 source
fields now have exactly the same native frame at each common owner.

Clear eight owned output arrays. Zero is compatible with T_c, so no native
line preparation of a nonzero dirty output is assumed. For each k, perform
the literal signed scalar additions

```
Q_k += R[k,p] * aligned_C_p,  for p in U with R[k,p] != 0.
```

This yields `Q=R_U D_(2,U) C=B2 C`, in frame T_c. Scalar additions leave
every source field unchanged. Undo every A_p, then apply `C_(d q_p)` to each
source. Both physical and logical source endpoints are exactly restored.
The output arrays are intentionally retained; they are the requested observation.

All normalization, alignment, accumulation, undo and restoration sweeps are
completed in that order before the next sweep. At a fixed owner, all ADDs
use different source and output fields in matching frames. Finishing each
full-cover sweep prevents reads from partially updated other owners. The
word can therefore be inserted before the next source-modifying operation,
subject to separate global scheduling and child-hosting obligations.

## Literal rank-one kernels

For every actual nonzero q in the nine-dimensional local block, choose an
invertible binary G with `G e0=q`. The verifier takes q as its first column
and the other eight coordinate axes except one pivot of q as the remaining
columns. Define P_G by sending the basis vector at address x to the basis
vector at address Gx. Then

```
P_G C_e0 P_G^-1 = C_q,
T_q P_G C_e0 P_G^-1 = C_q^-1.
```

The source rank-one primitive C_e0 has two Gaussian coefficients
`(1+i)/2` and `(1-i)/2`. Both signed words therefore use one rank-one child
and two monomial wrappers. The inverse translation is fused into the left
wrapper, exactly as in the retained QQ16 convention. The checker verifies
both Gaussian coefficients at every one of the 512 local basis addresses
for all 96 ports and both signs: 98,304 exact columns. External axes are
spectators. The identities lift ownerwise and to every positive tensor power.

These are operator recipes and recursive rank counts. They do not themselves
assign available helper owners or bound the physical address implementation.

## Phase and logical verification

A field's Fourier phase is represented as a sum of binary parities with
integer coefficients modulo four. Such a function has a unique multilinear
polynomial of degree at most two modulo four: its linear coefficients are
modulo four and each cross coefficient is zero or two. Equality of these
polynomials is an identity on all 73-bit characters, not a random test.

A native line appends the term `+/- (q dot w)`. A map M(g,a) changes each
phase axis v to gv and adds `2(a dot w)`. The checker applies exactly these
rules after every literal operation and requires matching phases for each
ADD. Alongside the phase it tracks an exact rational linear combination of
104 independent logical input arrays, carrying actual owner matrix products.
Native lines change frames; cover maps apply their logical owner routes.
Final checks require all 96 source rows to be the original independent input
and the eight output rows to be precisely R_U D_(2,U), with no dependence on
the discarded owned inputs. This jointly proves content and frame correctness
under the stated native semantics.

## Complete local invoice and boundary

There are 96 inverse and 96 positive lines, hence 192 rank-one children and
384 native wrapper maps. Each of 96 sources has one full-cover alignment and
one inverse, hence 192 full-cover maps. Each actual ordinary R column has
four signed unit coefficients, so there are 384 ADDs and eight CLEARs.
The retained per-real-component bounds are four primitives per ADD and one
per CLEAR; two components give `2*(384*4+8)=3088`. No SCALE or implicit COPY
is omitted. The eight owned output arrays are additional live storage.

The result is a complete local operator read and an explicit local count,
not the complete PR2443 decoder or a favorable global bill. Other retained
cut arrays, query output conversions, stream/address costs, global child
delivery, storage lifetime, cleanup, precision and all-size supplier admission
remain open. This word alone does not change a moment or an exponent.

# Zero early retention at a two-chart frame

This is a finite alternative to ywz65's PR2540, at exact head
`630d557af5088f66b45c447969cee9576600e50b`. Its README explicitly asks for an
expanded-current-read comparison with zero early retention. Both callers return
all 224 original arrays in F_U1, preserve the 224 current borrowed fields, and
use at most sixteen local scratch arrays. This caller reads after completed B1;
it carries no new owned state across B1. It is an expensive constructive baseline,
not an optimization or a lower bound on other zero-retention implementations.

## 1. Ordered algebra and the changed observation interface

Use the reviewed QQ16 definitions, the actual eight-port sets A and T and their
96-port complement U. In chart s, R_s is the routed query, K_s=R_s^*/4,
P_s=K_(s,T), and L_s=ell_(s,T). The exact orthogonal-minor identities are
R_s P_s=L_s P_s=I and R_s K_(s,U)=12I. Route products are ordered; none are
commuted. See the pinned `JOINT-QUERY-TRANSFER.md` for the original definitions.

Write the original inputs as (x0,y0), the completed F0 pair as (x1,y1), and
the completed B1 pair as (x2,y2). We observe **all** of (x2,y2), including the
ordinary Y entries. This changes PR2511's compressed observation interface;
its sixteen-record retention lower bound does not apply to these full reads.
Invertibility with full reads was already known. The contribution here is the
explicit same-endpoint word, its native frame realization and its invoice.

For B1's conserved version, put a=L_1 x1, b=R_1 E_2 y1, u=E_2 y1. Its output
satisfies R_1 y2=a, and

```
y2_U = y1_U + K_(1,U) a
y2_A = u_A
y2_T = u_T - P_1 (b + 11a)
x2_T = P_1 (b + 12a).
```

All selected pair sums are conserved. Therefore a=R_1 y2 is now readable, and
the inverse can be written without an additional full-cover query bank:

```
u_U = y2_U - K_(1,U) a
u_A = y2_A
u_T = y2_T + x2_T - P_1 a
y1  = E_2^-1 u
x1_U = x2_U + y1_U
x1_V = x2_V + y2_V - y1_V,    V=A union T.
```

Here E_2^-1=I-P_(2,A) R_(2,offA); its correction reads only U union T and
writes A. The actual offA/A support makes its square-zero proof immediate.
This is a direct inverse of the published B1 map, including arbitrary selected
inputs. It does not infer a clean query from selected observations alone.

F0 uses the identity owner chart. Let w=x1_U, f=ell_(0,T)x1, c=ell_(0,A)x1.
Its inverse is

```
x0_U = w + K_(0,U) f = z
x0_A = P_(0,A) (f - c - R_(0,U) z)
x0_T = P_(0,T) c
y0_U = y1_U - w
y0_V = x1_V + y1_V - x0_V.
```

The equivalent formula for the A query is -11f-R_(0,U)w-c. The checker uses
this latter expression as a separate reference; the literal word uses the
updated z expression. Both sides of the complete inverse are checked over all
224 independent array symbols with exact rational coefficients in the group
algebra of the actual 73-bit route matrices. This is a full formal operator
identity, not a constant-payload restriction or random evaluation. The
checked equality implies every owner and every input, since the exact group
relations used are actual operator relations.

## 2. A common frame for both charts

Let C_v have Fourier multiplier i^(character(v)) in each payload layer. Define

```
F_U1 = product_(j=0..16) C_(d e_j)
F_U2 = product_(j=0..24) C_(d e_j).
```

At the inherited B1 endpoint X has F_U1 and Y_p has F_U1 C_(d q_p)^-1.
These endpoint types and the F0/B1 realization are inherited from the reviewed
QQ16 native contract and PR2540; their entire native cores are not replayed here.

Clear owned outputs Z_p,W_p in the respective entry frames and copy X_p,Y_p
into them. One positive intrinsic-line child on each W_p normalizes it to F_U1.
One rank-eight child on each of the 224 outputs then multiplies by
product_(j=17..24) C_(d e_j). All owned fields now have common frame F_U2.
The borrowed fields are never destinations, including during normalization.

Both actual chart involutions g_(1,p),g_(2,p) preserve the 25-axis subspace:
they interchange the port's local eight-plane with the relevant eight-axis
stage block and fix the other coordinates. They are orthogonal over F2.
Consequently the phase polynomials

```
S(z) = sum_(j=0..24) character_(e_j)(z)     (mod 4)
S_g(z) = sum_(j=0..24) character_(g e_j)(z) (mod 4)
```

have the same quadratic terms and their linear differences are even.
Define b_(s,p) by S-S_g=2 character_b (mod 4). The checker derives every one
of the 224 translations and compares the **complete** degree-at-most-two
polynomials on 73 variables. Thus the actual cover map

```
M(g,b): out(d,z1,...,zlambda)
       = in(d*g,z1 XOR d*b,...,zlambda XOR d*b)
```

preserves F_U2 while realizing the logical owner pullback g. Its inverse has
translation g*b; in these cases g*b=b. This follows for every invertible owner
d and every positive payload tensor depth by substitution into the polynomial
identity and tensor products. The translation is required. A wrong-shift
control fails at an actual scalar frame boundary. No payload-only permutation
is substituted for a full-cover owner map.

For the current query, align all 112 W banks and the eight selected Z_T sums
with chart 1. At one owner, form all eight components of a in local scratch
before changing any W. Update W_U and replace W_T by Z_T-Pa. Clear scratch,
finish the owner sweep and undo all maps. For E_2^-1, align all 112 W banks
with chart 2, compute the eight offA query components locally, subtract the
A correction, clear scratch, finish the sweep and undo all maps. These use
240+224=464 complete cover maps. No cover map crosses an owner-private body.

Use the selected sums to finish x1 in Z. Before the F0 inverse, W_U-=Z_U
already gives y0_U and W_V+=Z_V preserves the selected sums. The F0 inverse
uses sixteen local arrays and no cover maps. Finally W_V-=Z_V gives y0_V.
All 224 outputs are downgraded by the inverse rank-eight block to F_U1.

An owned CLEAR discards arbitrary contents and can declare the zero field's
next frame; it is charged. Each scalar instruction outside a private body is
a complete cover sweep. Within a private body the **entire body** runs at one
owner before the next owner. These are finite scheduling semantics, not a tape
implementation or permission to use private scratch between cover sweeps.

## 3. Native child lowering and the complete added local invoice

One canonical positive rank-one child with two invertible monomial wrappers
implements C_q: an invertible binary address basis sends its first coordinate
to q. The verifier checks all 512 input columns for all 112 intrinsic lines.
For the eight-axis block, a coordinate permutation sends e0,...,e7 to
e17,...,e24. Its convolution coefficient at offset v is (-i)^|v|/16.
The inverse coefficient is i^|v|/16, obtained from the positive child by the
translation sum_(j=17..24)e_j, since (-i)^(8-|v|)=i^|v|. All 256 difference
coefficients are checked exactly with Gaussian integer numerators. Translation
invariance and the explicit coordinate permutation cover every basis column;
inactive coordinates factor out. Thus either signed block costs one positive
rank-eight child and two monomial wrappers. These are local child descriptions;
physical child hosting is still an obligation.

| Added local quantity | PR2540 pinned word | This word | Delta |
|---|---:|---:|---:|
| Rank-one children | 224 | 112 | -112 |
| Rank-eight children | 16 | 448 | +432 |
| Native rank mass | 352 | 3696 | +3344 |
| Native monomial wrappers | 480 | 1120 | +640 |
| Full-cover maps | 208 | 464 | +256 |
| Unit ADDs | 856 | 1808 | +952 |
| Quarter ADDs | 832 | 896 | +64 |
| CLEARs | 320 | 312 | -8 |
| Real scalar primitive allowance | 17472 | 25840 | +8368 |
| Owned final output banks | 224 | 224 | 0 |
| Additional owned early banks | 16 | 0 | -16 |
| Owned retained values across B1 | 16 | 0 | -16 |
| Peak local owned scratch | 16 | 16 | 0 |
| Borrowed current fields restored/preserved | 224 | 224 | 0 |

Scalar prices are the pinned QQ16 prices: unit ADD 8, quarter ADD 12, CLEAR 2.
All copy, input normalization, wide-frame upgrades/downgrades, scratch clears,
cover maps and wrappers appear in WORD.json. F0/B1 are historical execution,
outside both added invoices. The word has 4047 records, of which seven are
private-body/checkpoint delimiters rather than gates.

At the same parent width m and exponent 0<=a<=1 the added recursive-child
moment difference is

```
[432 * 8^(1-a) - 112] / m^(1-a) > 0.
```

Its numerator is at least 320. Therefore eliminating early records by **this
specific whole-bank common-frame recipe** does not improve the local native
bill at any such exponent. It is not a lower bound for other direct decoders.
Retention, storage, address, precision and consumer savings could matter in a
completed construction; no credit for those unproved savings is assumed here.

## 4. Decision and remaining obligations

Stop this common-frame candidate after the exact comparison. No larger search
or downstream construction campaign is justified by this local invoice. A
different direct-read realization that avoids most of the 448 block conversions,
or a caller supplying concrete retention/placement costs, could reopen the
comparison. Discussion2617's independently claimed coalescing of early records
into output banks is complementary: it still retains sixteen values across B1.
The table compares the exact published PR2540 word, not that pending variant.

Still open: physical allocation and retention, stream/address costs of all
maps and copies, hosting of signed/nonmonotone frame calls and their wrappers,
child-internal precision and approximate-error restoration, a global output
consumer, all-size/compiler admission and the complete supplier moment. The
precision bounds for the unchanged PR2540 word do not automatically apply here.
This result neither changes the selected frontier nor establishes a complete
integer multiplication theorem or a minimum zero-retention cost.

## Credit

QQ16 maps and ordered inverse: Ali Romman and the credited joint-query team.
Full-current inverse possibility and equal-endpoint comparison request:
ywz65/PR2540 and PR2511, retaining starship-s/PR2443, thakrarsagar/PR2470,
Ross Richardson/PR2480 and PR2456/2468/2492/2512 native geometry lineage.
Source-bound R reconstruction and frame-polynomial methods also follow the
credited reviewed QQ16 and ywz65 checkers; this implementation imports none
of them. The new common-frame word, comparison and checker were prepared by
Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.

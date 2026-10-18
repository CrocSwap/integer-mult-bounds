# A complete local decoder with temporal ownership

This construction composes the pinned PR2511 selected-sum decoder with PR2512's
current-frame native maps. It supplies the entire **added** local decoder,
including early capture and retirement. The inherited F0/B1 calls are premises
of the timeline and retain their own costs. No physical hosting or supplier
admission follows from this local word.

## 1. Exact timeline and output contract

Use the actual 112 ports, eight-port sets A,T and 96-port complement U. Put
V=A union T. The original pair is `(x,y)`, the completed F0 pair is `(x1,y1)`,
and the completed B1 pair is `(x2,y2)`. The source's first two events on pair 0
are F0 and B1, before the next bridge. The unchanged source parser verifies this
binding. Other pairs and all inherited dirty/helper fields are untouched by
the new decoder.

At complete F0, every selected X1 field has physical frame
`F_L=product_(j=0,...,8) C_(d e_j)`. Allocate sixteen **owned** full-cover banks
R_p, clear them and add X1_p into them. These are sixteen paid ADDs and sixteen
paid CLEARs. All source fields are unchanged. R lives outside the inherited
L/C field namespace and is held unchanged across B1; storage and retention are
explicit premises, not supplied for free by the original controller.

After complete B1, each current X_p has frame `F_U1`, and each current Y_p has
frame `F_U1 C_(d q_p)^-1`, where `U1=<e0,...,e16>`. R still has frame F_L and
logical content x1_V. The decoder is allowed to borrow all 224 current physical
X/Y fields. It restores all of them, including every Y temporarily normalized.
It uses selected current X/Y only to form their sums in final Y output banks.

The caller supplies 224 exclusively owned output banks Z_p,W_p. Their prior
contents may be arbitrary and are discarded by charged CLEARs. At exit they
contain **original x_p,y_p in the common physical frame F_U1**. This is a
specified output contract, not a claim that their original pre-F0 physical
frames are restored. R is separately cleared at exit in its old frame F_L;
those sixteen retirement CLEARs are also charged. R never aliases Z or W.

There are at most sixteen owned local scratch arrays at any one cover owner.
The L2 body uses one scratch lifetime C, cleans it, and completes its full owner
sweep. A later F0-inverse body uses sixteen scratch lifetimes F_k,G_k, cleans
all of them, and completes its sweep. Those lifetimes do not overlap, so the
first can reuse a slot of the later sixteen. This is local scratch, not sixteen
additional full-cover banks. Every full-cover map finishes outside both bodies.

The `history_boundary` record in WORD.json denotes the inherited completed B1
call between the two portions of the added word. It is **not** a zero-cost gate.
The checker models 16 earlier X1 symbols and 224 current physical symbols as
independent temporal observations, then checks their actual F0/B1 relationship
through the retained logical decoder. No assertion that those 240 observations
are independent functions of the original 224 inputs is made.

## 2. Native prefix and current L2 query

Copy R_p into the eventual Z_p output for each p in V, after clearing Z in F_L.
Apply positive `F_E1=product_(j=9,...,16) C_(d e_j)` to each of these sixteen Z
banks. This costs sixteen rank-eight children and puts x1_V in frame F_U1.
R is unchanged. In particular Z_T is now the actual eight-record input to L2;
there is no later downgrade because it is an eventual output bank.

For p in U, normalize borrowed Y_p by C_qp, clear Z_p in F_U1, add X_p and Y_p,
then restore Y_p by C_qp^-1. Z_U now contains x2_U+y2_U in frame F_U1.

Use PR2512's actual current-chart maps on Z_U and Z_T:

```
B_p = M(g_p,b_p),       b_p = delta_p + g_p delta_p,
B_p F_U1 = F_U1 D_p,    B_p^-1 = B_p.
```

The added translations are material: old delta_p fails the full-frame identity
for every one of the 104 used ports. Source reconstruction checks the exact
73-bit g_p, original translations and native phase rows. The inherited complete
phase-polynomial checker and a separate zero/singleton/two-bit literal parity
check establish the identity on all characters. The latter uses 281,008
evaluations; parity modulo four has degree at most two, so these determine the
whole identity. Owner pullback and tensor products extend it to arbitrary
owners and payload layers. This is not a constant-slice argument.

After these full-cover maps, at one owner execute the whole private L2 body:
for k=0,...,7, clear C, form `C=sum_(t in T) R[k,t] Z_t`, add
`-R[k,p] C/4` to each ordinary Z_p, and clear C. All fields have the same current
frame. Reverse all 104 maps. The unchanged ordered L2 identity gives

```
Z_U = x2_U+y2_U-K_(1,U) ell_(1,T) x1_T = x1_U.
```

Z_T restores its logical x1_T; Z_A was unaffected. Therefore all 112 Z banks
now contain x1 in common frame F_U1. The ordered matrix product g_p^-1 g_t is
tracked exactly; port-dependent owner actions are not commuted through R.

## 3. Complete F0 inverse and Y outputs

The actual source F0 chart is identity. This is checked in the retained route
parser; the literal F0 program has no cover maps. Its source matrices satisfy
`R_A R_A^T=R_T R_T^T=4I`. At each owner use sixteen local owned scratch arrays
to form

```
F = R_T Z_T = ell_(0,T) x1_T,
G = R_A Z_A = ell_(0,A) x1_A.
```

Then execute in this order:

```
Z_U += R_U^T F/4,
F   -= G + R_U Z_U,
clear Z_A;  Z_A += R_A^T F/4,
clear Z_T;  Z_T += R_T^T G/4,
clear all F,G scratch.
```

The updated Z_U is used in the second line. These equations are precisely
PR2511's credited F0 inverse; the last two selected banks can be overwritten
because F and G already hold the needed old queries. Every operand remains in
F_U1, so no extra native children or owner maps are required here. The complete
owner body finishes before moving to another owner. The exit Z contains the
entire original x in F_U1.

For ordinary ports, source conservation gives original `y_U=-x2_U`. Clear W_U
and add -X_U. For selected ports, normalize current borrowed Y by C_q, clear W,
add current X and normalized Y, restore Y, then subtract Z. The conserved
selected sums give

```
W_V = x2_V+y2_V-x_V = y_V.
```

W itself is the eventual Y output; no separate sixteen-array selected-sum bank
is allocated. Finally clear the owned early R banks. All 224 current borrowed
fields restore physically and logically, the sixteen early banks are retired,
and every local scratch is zero in identity frame at its owner-body boundary.

## 4. Exact local invoice and native lowering

Each signed line C_q or C_q^-1 uses one positive rank-one child and two monomial
wrappers, with `C_q^-1=T_q C_q`. A coordinate permutation sends canonical axes
0,...,7 to E1, so positive F_E1 uses one rank-eight child and two wrappers.
These are the same explicit local child recipes as PR2512. The checker compares
114,688 signed rank-one basis columns over all 112 ports and the inherited
65,536-coefficient rank-eight kernel check, with exact Gaussian integers.

| Added charge, including capture and retirement | Count |
|---|---:|
| Positive rank-one children | 224 |
| Positive rank-eight children | 16 |
| Native rank mass | 352 |
| Native monomial wrappers | 480 |
| Full-cover maps | 208 |
| Unit ADDs | 856 |
| Quarter ADDs | 832 |
| CLEARs | 320 |
| Real scalar primitive allowance | 17,472 |
| Owned full-cover final outputs | 224 |
| Additional owned early full-cover banks | 16 |
| Peak local owned scratch arrays | 16 |
| Current borrowed fields restored | 224 |

The scalar source prices unit ADD at 8, quarter ADD at 12, and CLEAR at 2:
`856*8+832*12+320*2=17472`. The capture portion contributes sixteen unit ADDs
and sixteen CLEARs (160); retirement contributes sixteen CLEARs (32). Both are
included. Rank-one normalization is performed on each current Y field twice;
there are no hidden inverse rank-eight calls. All 208 maps are charged actual
cover operations, with their physical stream cost still unresolved.

The native operator word is checked on 240 independent temporal source symbols
and arbitrary owned-output dirt. Its 224 outputs match the authenticated PR2511
decoder's full routed operators. That retained decoder also passes both inverse
orders on the actual 224 original input arrays and on its 224-coordinate
compressed observation space. Reuse is credited; this is not an independent
second proof of PR2511's operator machinery. Twelve semantic faults, including
capture timing, early-record retirement, phase shifts, F0 inverse sign and
source restoration, must fail. Export tests add ownership chronology and source
authentication failures.

This fills the complete added local decoder/lifetime contract. It does not
price F0/B1 as free, remove their inherited helper/private requirements, restore
original input physical frames, prove a net storage saving, or supply a consumer
for the 224 current-frame outputs. Physical retention, movement, native hosting,
precision, global controller use and all-size admission remain open. No minimum
child count, favorable completed moment or new kappa is claimed.

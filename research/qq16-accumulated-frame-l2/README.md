# Cheaper QQ16 L2 reconstruction through the accumulated frame

**A local native construction; no new supplier or kappa.** The same old-frame
L2 output contract as [PR2492](https://github.com/CrocSwap/integer-mult-bounds/pull/2492)
can be realized with **96 rank-one and 112 rank-eight children**, rank mass
**992 instead of 1,168**, while restoring all 200 source arrays. All 208 cover
maps remain charged. An explicit alternative returns outputs in the accumulated
post-B1 frame for **96 rank-one and 16 rank-eight children**, rank mass **224**.
That alternative changes the output contract; its downstream consumption is open.

The method uses existing registered completed-frame maps. It copies Y into the
owned output before normalizing it, leaves X/Y sources read-only, and aligns
the entire accumulated frame during the correction. This eliminates the
predecessor's per-output alignment lines. It does not contradict that package's
rejection of using the old Y-chart translation on an accumulated frame.

## Boundary, provenance and predecessor delta

Base: canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
[SOURCES.json](SOURCES.json) pins the actual QQ16 packet, scalar allowance and
native contract. [TASK.json](TASK.json) records the original card, the changed
scope, overlap limits and uncompleted global obligations.

Use L=axes 0..8, E1=axes 9..16, S=L+E1 and the packet's disjoint A/T/U sets,
with |T|=8 and |U|=96. Let `F_V` be the product of native positive line factors
on V. At owner d, every axis is conjugated by d. Inputs and outputs are complete
arrays, including arbitrary owner and payload contents and spectator coordinates.

| Input | Arrays | Frame |
| --- | ---: | --- |
| live post-B1 X2_U | 96 | F_S |
| live post-B1 Y2_U | 96 | F_S C_qp^-1 |
| retained post-F0 x1_T | 8 | F_L |

These 200 inputs are independent in the local contract. Their logical contents
and frames are restored. X and Y are never written. There are 96 exclusively
owned output arrays Z whose previous contents may be discarded, and one owned
local scratch array C. C is reused only after the whole body at each owner and
returns to zero/identity. No borrowed dirty input is cleared. Delivery of the
eight older records is assumed and remains an additional obligation.

The output content in either variant is

```
Z_p = X_p + Y_p
      - sum_(t in T) (R_U^T R_T)[p,t]/4 D_p^-1 D_t T_t,  p in U.
```

Here `D_p f(d)=f(d rho1(p))`, with the actual registered noncommuting owner
routes. The order `D_p^-1 D_t` matters. The credited L2 backward identities give
`X2_U=x1_U-y1_U` and `Y2_U=y1_U+K_(1,U) ell_(1,T)x1_T`, so Z represents x1_U.
This information identity is inherited from Ali Romman's PR1969 and Sagar
Thakrar's PR2470, rather than a new decoding theorem.

Consulted pending sources, retained as credit rather than executable inputs:

- **ywz65, PR2492**, head `9cc0d4d60819ddd246c9db9549f8ae4a61b68e45`:
  the precise cross-cut boundary, old-frame construction, 1,168 invoice and
  accumulated-E1 warning. README Git blob `f7729d0e6fe49f9c4226a4a287c75178a00d51ae`.
- **ywz65, PR2468**, head `baa90ee8176931e697d91a9024114ee2e9a189ea`:
  the adjacent native future-X query and line-wrapper methods; no code imported.
- **Sagar Thakrar, PR2470**, head `1b2eee3bf1ec67e68c0b0fa7f47c7b2a66febe56`:
  L2 and its retention census.
- **Ross Richardson, PR2480**: the sharp 24-array information contract, which
  still grants native reads. This package supplies neither its whole decoder
  nor a new information minimum. starship-s/PR2443 and ywz65/PR2456 retain
  the ordered cut-decoder and operator-audit credit.

## An accumulated-frame lift

For a binary orthogonal g preserving the first 17 axes and fixing spectators,
there is a unique translation eta with

```
sum_(j<17) parity((g e_j) dot w) + 2 parity(eta dot w)
    = sum_(j<17) w_j                         (mod 4)
```

for every 73-bit w. To prove this, expand each binary parity modulo four.
The off-diagonal quadratic coefficient for i,k is
`-2 sum_(j<17) g_ij g_kj`, which vanishes modulo four by orthogonality.
The diagonal coefficient has the same parity as `1_(i<17)` since g preserves
the subspace. The difference is therefore twice a linear binary form, uniquely
removed by

```
eta_i = (1_(i<17) - sum_(j<17) g_ij)/2         (mod 2).
```

Use the retained physical convention
`M_(g,eta)f(d,z_l)=f(dg,z_l+d eta)` on every payload layer. At a general owner,
substitute `w=d^T omega` in the character identity. It follows that

```
M_(g,eta) F_S = F_S D_g.
```

This is an operator identity on arbitrary arrays, because binary characters
span the payload space. Tensor layers multiply the same identity; spectators
are fixed. The map includes owner motion and payload translation. It is not
a payload-only permutation or a zero-cost address operation.

For each of the 104 relevant actual rho1(p), the verifier checks all 73-axis
orthogonality/support equations, derives eta, verifies the full Z/4 polynomial
and inverse, and finds an exact matching map already in the frozen registry.
[MAPS.json](MAPS.json) gives its columns, translations and matching names.
The old Y-chart translation is different and fails the required phase check.

## Complete word and ordered proof

[WORD.json](WORD.json) contains every event, including literal map columns and
translations. Each cover sweep completes before the next event or private body.

1. At each ordinary port, clear Z in Y's frame, add Y, apply one positive C_qp
   to Z, then add X. Z now represents X+Y in F_S. X/Y stay read-only throughout.
2. Raise each of the eight retained T arrays from F_L to F_S using F_E1.
3. Align Z_U and T_T with their frame-preserving registered maps. Their common
   physical frame is F_S and their logical values are D_p(X_p+Y_p), D_t T_t.
4. In one complete body per owner, for k=0..7 clear C in F_S, gather
   `C=sum_t R[k,t] D_t T_t`, and add `-R[k,p] C/4` to each indicated Z_p.
   One final clear returns C to zero/identity. A new gather's clear discards
   the previous owned scratch value, so redundant intermediate clears are omitted.
5. Undo every T/Z map and lower the eight T records with F_E1^-1.

Only Z and owned C are scalar targets. The inverse maps restore T's owner view;
its two stage changes restore its frame. For Z, applying D_p^-1 to step 4 gives
exactly the displayed ordered operator. Thus all 200 sources return unchanged,
and Z has frame F_S. No other source observation is required.

To obtain the predecessor's **F_L output contract**, append the 96 negative
rank-eight changes in [OLD-FRAME-TAIL.json](OLD-FRAME-TAIL.json). They act only
on owned Z. The primary verifier replays this full second word and checks both
the same content and the old output frame. The tail is charged, not elided.

## Native lowering and complete local invoices

For nonzero q, choose an invertible binary P sending e0 to q. Then
`C_q=P C_e0 P^-1`, one positive rank-one child and two monomial wrappers.
An explicit permutation exchanging axes 0..7 with 9..16 supplies F_E1 through
one positive rank-eight child. Its inverse is that child followed by translation
on the eight E1 axes, fused into the left wrapper. Both signs therefore cost
one rank-eight child and two wrappers. The identities conjugate at each owner
and tensorize; admitting their recursive children globally is a separate step.

| Local charge | Accumulated F_S outputs | Old F_L outputs | PR2492, F_L outputs |
| --- | ---: | ---: | ---: |
| rank-one children | 96 | 96 | 400 |
| rank-eight children | 16 | 112 | 96 |
| native rank mass | **224** | **992** | **1,168** |
| monomial wrappers | 224 | 416 | 992 |
| full-cover maps | 208 | 208 | 208 |
| real scalar allowance | 6,610 | 6,610 | 6,624 |
| owned outputs / local scratch | 96 / 1 | 96 / 1 | 96 / 1 |

The same-frame saving is 176 rank mass (11/73 of the predecessor bill). These
are constructive upper invoices, with no optimality claim or measured runtime
claim. For any child rank-power price r^q with 0<q<=1, the same-frame child
saving is `304 - 16*8^q >= 176`, before the common width normalization. Thus
the local child comparison does not depend on choosing only the rank-mass
endpoint. It still does not establish a favorable whole supplier moment.
The scalar bill is `224*8 + 384*12 + 105*2 = 6610`, bound to the retained
`scalar_cost` function. Quarter coefficients cost 12. The principal word has
1,035 records including two private-body markers; the old-frame variant has
1,131. Map and wrapper counts are operations, not physical tape time.

## Reproduce and evidence

Python 3.12, standard library and Git for historical metadata checks:

```sh
python3.12 scripts/research_package.py --package research/qq16-accumulated-frame-l2
python3 -I -O -B research/qq16-accumulated-frame-l2/verify.py
python3 -I -B research/qq16-accumulated-frame-l2/independent_check.py
```

The default mathematical replay is read-only and works in a Git-free export
with the declared inputs. It checks all 200 independent source-array symbols,
all 96 output rows and both output-frame variants; source hashes; 104 actual
routes and complete 73-bit phase polynomials; 53,248 rank-one basis columns;
131,072 signed rank-eight kernel coefficients; and ten semantic faults.
No acceptance predicate relies on Python `assert`.

The separately written arithmetic oracle imports no primary verifier code.
It checks **13,631,488** active character assignments by direct weight counts
and **594** scalar basis coordinates plus one fully dirty fixture using
noncommuting rational 2x2 involutions. The latter are algebra fixtures, not a
representation of the actual cover group. Five boundary tests cover optimized,
Git-free, read-only replay; source drift; corrupt word/map/receipt; a missing
receipt; and an accepted equivalent disjoint preparation order.

The written proof supplies the all-owner, arbitrary-array and tensor-layer
implication under the retained native convention. These finite checks supplement
it. Neither code separation nor the proof is independent human review, a proof
assistant result or supplier admission. See [VALIDATION.md](VALIDATION.md) for
the exact executed environment and remaining gates.

## Open next questions

- Can PR2480's complete cut decoder consume F_S outputs directly? Bind its
  next reads to actual frames and lifetimes, then price conversions/retirement.
  Until then, 224 is a changed-output local bill; 992 is the comparable old-frame bill.
- Can retained T records be captured in F_S? Price capture, retention and
  retirement before removing either of the sixteen rank-eight conversions.
- Can a whole controller remain favorable? Supply physical maps, child/output
  owners, storage, precision/tape, all four bank repairs, endpoints and the full
  moment invoice. This package does not establish any of those global claims.

No selected cold replay, full 224-input native decoder, record delivery or
retirement, physical stream/address implementation, complete hosting, recursive
precision, all-size compiler or multiplication theorem is supplied. The selected
record and frozen predecessor evidence remain unchanged.

## Credit and coordination

Prepared by **William Lawyer**, with substantial OpenAI Codex assistance in
derivation, source inspection, implementation, checking and writing. New work
is Apache-2.0. Retain Ali Romman's QQ16/PR1969 and native geometry/compiler
lineage, Sagar Thakrar/PR2470, starship-s/PR2443, ywz65/PR2456/2468/2492,
Ross Richardson/PR2480, and the Rohan Arun/Jeremy Kothe selected supplier lineage.
No pending predecessor verifier is copied, imported or run. The pinned main
branch's scalar_cost function is evaluated in isolation for the stated invoice.

The weighted selection chose recursive interfaces, nonce
`d650c685a88fea5fb302527452e1b3c1`. The original full-controller question is
explicitly changed to this local interface task. Connected live PR searches,
the public discussion pages and exact pending source boundaries were read;
complete live discussion pagination was unavailable. The local helper reported
its missing-gh limitation. The connected attempt to post an advance claim on
PR2492 returned HTTP 403; no public reservation is asserted. Search coverage
does not establish novelty. This package is one independently reviewable local
construction rather than a claim to have completed the catalogue's controller.

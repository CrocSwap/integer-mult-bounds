# A current-frame owner map and two exact L2 endpoints

All operators and fields below use the pinned PR1969 QQ16 contract. This is a
local construction with two explicitly different endpoints, not a full decoder
or a supplier invoice. PR2492's old-frame construction remains valid.

## 1. Native objects and the changed map

Let the common coordinate dimension be 73, `L=<e_0,...,e_8>`,
`E=<e_9,...,e_16>`, and `U=L+E`. At owner d, for any axis vector v, use

```
C_(dv) = ((1+i)I + (1-i)T_(dv))/2,
F_U = product_(j=0,...,16) C_(d e_j).
```

The line's multiplier on a character w is `i^parity(w dot dv)`. Products of
these lines commute. The formulas tensorize over every payload layer.

For each relevant port p, let `g_p=rho_1(p)` be the **actual** current-chart
73-bit owner matrix, and let delta_p be the source's old-cut alignment shift.
The source provides its inverse shift `g_p delta_p`. The verifier reconstructs
g/delta from the pinned phase source, compares them to the current B_1_2 map
registry, and checks `g_p^2=I` and orthogonality. Define the new map

```
b_p = delta_p + g_p delta_p          (binary addition),
B_p = M(g_p,b_p),
(M(g,b) f)(d,z_1,...,z_lambda)
    = f(dg,z_1+d b,...,z_lambda+d b).
```

Thus `g_p b_p=b_p`, so B_p is its own actual inverse, including the payload
translation. This is a different physical map from the old alignment for all
104 ports. The logical owner action is still `D_p f(d,...)=f(dg_p,...)`.

The crucial new identity is

```
B_p F_U = F_U D_p.                                      (1)
```

It does **not** follow by replacing a chart index in the old F_L alignment.
For identity owner and one character w, (1) is exactly

```
sum_(j=0,...,16) parity(w dot g_p e_j)
  + 2 parity(w dot b_p)
  = sum_(j=0,...,16) parity(w dot e_j)    mod 4.           (2)
```

`verify.py` checks every coefficient of (2) for all 104 actual source records
using the retained phase representation. Separately it evaluates the literal
parities on the zero character, all 73 singleton characters and all 2,628
two-bit characters: 281,008 comparisons. This is complete, not sampling:
modulo 4, parity of a subset is its degree-one sum minus twice the sum of its
degree-two products, since all higher terms are divisible by 4. The constant,
linear and quadratic coefficients are determined by these evaluations.

For arbitrary owner d, replace w by its pullback along d. For multiple tensor
layers, multiply the per-layer identities. Fourier characters span arbitrary
payload arrays. This proves (1) on arbitrary arrays and owners under the
retained common-label cover action. Both logical owner change and payload
translation are included. The receipt supplies an actual character witness
rejecting the old delta_p in place of b_p for every port.

## 2. Inputs, outputs and word

There are 200 independent borrowed inputs at the immediate post-B1 cut:

| Fields | Number | Frame | Logical content |
|---|---:|---|---|
| X_p, p in ordinary U_ports | 96 | F_U | X2_p |
| Y_p, p in ordinary U_ports | 96 | F_U C_qp^-1 | Y2_p |
| T_t, t in selected T_ports | 8 | F_L | retained x1_t |

`U_ports` is the 96-port set, distinct from the coordinate subspace U above.
All source arrays are arbitrary. There are 96 exclusively owned output arrays
Z, whose old contents are discarded, and one exclusively owned local scratch
C. Capture, retention and delivery of the eight T inputs are assumed. They are
not proved free or newly supplied by this word.

The literal shared prefix is as follows.

1. Normalize Y with C_q, clear Z in F_U, add X and Y, and restore Y with
   C_q^-1. Each Z now contains X2+Y2 in F_U; X and Y are restored.
2. Apply positive F_E to the eight T inputs. Since `F_E F_L=F_U`, all fields
   used by the correction have the same current frame.
3. Apply B_p to every Z and T. By (1), their physical frame stays F_U and their
   logical content receives D_p. Every complete cover-map sweep finishes.
4. At each owner, execute the entire private body before moving to another
   owner. For k=0,...,7, clear C, form `C=sum_t R[k,t] D_t T_t`, add
   `-R[k,p] C/4` to every relevant Z_p, and clear C. All scalar operands have
   frame F_U. T remains unchanged during the body.
5. Undo B_p on T and Z, then undo F_E on the eight T inputs. The scratch is
   zero and all 200 borrowed sources have their original content and frame.

The physical Z frame is F_U, and its logical content at this named checkpoint is

```
Z_p = X2_p + Y2_p
      - sum_t (R_U^T R_T)[p,t]/4 D_p^-1 D_t x1_t = x1_p. (3)
```

The last equality is PR2470's L2 identity, inherited from the QQ16 backward
contract: `X2_U=x1_U-y1_U` and
`Y2_U=y1_U+K_(1,U) ell_(1,T) x1_T`. We do not claim it as new.
The ordered owner product is essential; actual g_p and g_t are not silently
commuted. The verifier tracks all 200 independent source symbols through the
word with their actual composed owner matrices and checks every output row.

Two fixed epilogues are certified, with the same prefix and ownership:

- **Current-frame consumer:** apply `Z_p -= X_p` for every ordinary port.
  This costs 96 unit ADDs and no new native child because both arrays already
  have frame F_U. The final output is y1_U in F_U. X remains read-only, and
  the same 96 owned Z arrays hold the result; no extra output bank is hidden.
- **Old-frame endpoint:** instead apply F_E^-1 to each Z. The logical result
  remains x1_U and the frame becomes F_L. This exactly matches PR2492's local
  output/source contract and uses the same inherited positive-child grammar.

The staged consumer exposes the x1 checkpoint before consuming it. Its bill is
for that word; no shortest scalar circuit is claimed.

## 3. Native lowering and complete local counts

For each odd local q, the inherited signed line recipes use one positive
rank-one child plus two monomial wrappers. The inverse identity is
`C_q^-1=T_q C_q`. The source-bound Gaussian checker tests both signs on every
512-column local basis for the 104 source port lines; only the 96 Y lines are
used in this new word.

Let P swap axes 0..7 with 9..16 and fix the other 57 axes. Then

```
F_E = P F_8 P^-1,
F_E^-1 = T_(e9+...+e16) P F_8 P^-1.
```

Each sign costs one positive rank-eight child plus two monomial wrappers, with
the inverse translation fused into the left wrapper. At owner d the full
recipe is conjugated by d. The checker compares all 65,536 active inverse
kernel coefficients with eight inverse line factors and checks the full
73-axis wrapper. This is the same local child grammar used by PR2492.

| Charge | Current x1 checkpoint | Current y1 consumer | Old-frame x1 endpoint |
|---|---:|---:|---:|
| positive rank-one children | 192 | 192 | 192 |
| positive rank-eight children | 16 | 16 | 112 |
| native rank mass | 320 | 320 | 1,088 |
| native monomial wrappers | 416 | 416 | 608 |
| full-cover maps | 208 | 208 | 208 |
| unit ADDs | 224 | 320 | 224 |
| quarter ADDs | 384 | 384 | 384 |
| CLEARs | 112 | 112 | 112 |
| real scalar primitive allowance | 6,624 | 7,392 | 6,624 |

The scalar allowance is evaluated from the authenticated source function:
unit ADD=8, quarter ADD=12 and CLEAR=2. All three columns use 96 owned outputs,
one local owned scratch and 200 restored borrowed arrays. The maps are actual
new M(g,b) operations, not free frame annotations; 208 cover operations are
included. Their physical stream/tape costs remain unpriced.

PR2492's old-frame x1 endpoint has 400 rank-one and 96 rank-eight children,
mass 1,168, 992 wrappers, the same 208 cover maps and scalar allowance 6,624.
The old-frame column here reduces native rank mass by exactly 80 and wrappers
by 384 under identical endpoint and child grammar. Comparing 320 with 1,168
instead changes the output frame and consumer contract and must say so.

These are local upper invoices, not global recursive excess costs or complete
physical runtime estimates. New cover-map shifts, child placement, precision,
retained-record lifetimes, output use/retirement and the full controller still
require admission. No storage saving, complete decoder or new kappa follows.

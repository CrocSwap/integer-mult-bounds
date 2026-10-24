# Independent review of the natural D25 clean triple

The stated no-reset endpoint is correct. The 208-positive-line operator
terminal is also correct on arbitrary data inputs, with the stated bank
exchange. There is no material local finding.

This review binds the actual local forward and inverse-adjoint content
maps, and the literal D25 phase views. It does not import either producer
checker. It uses a compact frame proof and a separate free-operator
composition. It does not repeat the producer's large expanded global
column replay or the inherited native child replay.

The producer proof has SHA256
`e968dd64f34f8dd4422145ccea847d329886657e9e209682a49964d7faf60f3c`.
The bound producer freeze has SHA256
`089425bdf431d81456e1c988a1fd21a837baca43e510bc92dee98dc2ee571791`.
The completed `run-terminal-normal/CHECKS.json` has SHA256
`24741af6fabff0e09bc13518f79477a80f32f88bb49aabaf31f40afa070aa543`.
`SOURCE-MANIFEST.json` also binds the imported phase library by its exact
bytes, although this review does not execute that library.

## Actual local maps

Let P be the selected set in its serialized order, and R its complement.
Their sizes are 16 and 96. The selected set is

```text
[0,27,36,111,20,7,57,46,1,3,6,8,17,18,24,23].
```

The review reads H from the P,R block of the row code and D from the
R,P block of the actual response. It checks

```text
C = [[I,H],[0,I]],
D = -H^T,
E_R(a,u) = u + D(a+H u).
```

The row code, response, selected set, and port order agree across the
forward and dual payloads. The port labels also agree with the D25
views.

On all 224 independent local data columns, the stored forward map is

```text
F(a,u,z,v) = (-z,u,alpha,v+u+D alpha),
alpha = a+H u.
```

The review derives its inverse from these equations and checks both
product orders. It then transposes that inverse and applies the actual
selected-wire permutation to both sides. The result agrees with every
column of the stored selected-swap inverse-adjoint:

```text
B(a,u,z,v) = (z+H v,u+D z-v,-a,v).
```

Thus B is bound to the native dual source. It is not an assumed inverse
of the response E.

The I-entry forward word has input `(Q(a,u),z,v)`. The later Q-entry
words have input `(Q(a,u),Q_P z,v)`. Both forward variants have the same
content map. Their physical input types and native invoices differ.

## The natural boundary is a route change

Write `G_s=diag(R_(rho_s,p))`. Every pinned rho is an orthogonal
involution and fixes its own line q_p. At stage zero, G is the identity.
The actual entry and exit views are

```text
Ventry_s,p = T_(rho_s,p(entry_X)) R_(rho_s,p),
Vexit_s,p  = T_(exit_X) R_(rho_s,p).
```

The pinned X and Y translations agree. The review checks, at every port
of stages 1 and 2,

```text
Ventry_s Fprev_s = Fext_s Q G_s,
Ventry_s Fprev_s q = Fext_s G_s,
Vexit_s Fnext_s = Fnext_s G_s,
Vexit_s Fnext_s q = Fnext_s q G_s.
```

There are 896 such identities. The phase checker applies the operator
word from right to left, in input-character coordinates. It reconstructs
the exact degree-two polynomial modulo 4 from its values on the 25
basis vectors and 300 pairs. This is an identity check, not a sampled
character test. The route matrices are checked as well. The result
tensors over every spatial column.

Suppose a previous output has physical type

```text
X=Fprev x,  Y_P=Fprev z,  Y_R=Fprev q_R v.
```

The next entry views give

```text
X=Fext Q G_s x,
Y_P=Fext Q_P G_(s,P) z,
Y_R=Fext G_(s,R) v.
```

Removal of the common exterior and the declared Q-entry input type
therefore leaves exactly G_s times the previous decoded contents.
The exit identities apply G_s to the local output contents. The
complete stage consequently replaces H and D by

```text
H_s = G_(s,P) H G_(s,R),
D_s = G_(s,R) D G_(s,P).
```

No Q is moved through H or D. Only the port's own Q commutes with its
route. In particular, the ordinary Y holes are not treated as FULL.

Omission of the literal entry translations fails all 224 entry
controls. Removal of the ordinary-Y hole from the input type fails
all 192 ordinary-port controls.

## Ordered three-call calculation

Define the initial contents by `X0=Q(a,u)` and `Y0=(z,v)`. These
equations do not add gates. All original physical inputs are arbitrary.

The first call gives

```text
alpha = a+H0 u,
K = v+u+D0 alpha,
Fclean0(a,u,z,v) = (-z,u,alpha,K).
```

Use the actual routed B formula at stage 1. Its output is

```text
(alpha+H1 K, u+D1 alpha-K, z, K)
  = (alpha+H1 K, W, z, K),

W = -v+(D1-D0)alpha.
```

The final forward call gives

```text
(-z,W,beta,K+W+D2 beta),
beta = alpha+H1 K+H2 W.
```

Since `K+W=u+D1 alpha`, put `r=u+D1 alpha+D2 beta`. The exact
physical endpoint is therefore

```text
X_P = -F25 z,
X_R = F25 W,
Y_P = F25 beta,
Y_R = F25 q_R r.
```

`BLOCK-PROOF.json` records a separate calculation in which all six
operators H0,H1,H2,D0,D1,D2 are free symbols. It checks the first,
second, and final stage endpoints and the inverse. It uses no
commutation relation between these operators.

For the inverse, set `t=r-D2 beta=K+W`. Then

```text
alpha = beta-H1 t+(H1-H2)W,
u = t-D1 alpha,
a = alpha-H0 u,
v = -W+(D1-D0)alpha.
```

These are ordered dyadic formulas. They do not require a unit
`I+H1 D2`, an odd division, or an extra independent centre bank.

## The 208-line terminal

The first 96 positive line operations change `F25 q_R r` to `F25 r`.
All fields are then in the common FULL frame. The following in-place
content updates recover the two original contents:

```text
Y_R <- Y_R-D2 Y_P                         # t
Y_P <- Y_P-H1 Y_R
Y_P <- Y_P+(H1-H2)X_R                     # alpha
X_R <- -X_R+(D1-D0)Y_P                    # v
Y_R <- Y_R-D1 Y_P                         # u
Y_P <- Y_P-H0 Y_R                         # a
X_P <- -X_P                              # z
```

The final 112 positive line operations on Y restore Q(a,u). Thus

```text
X=F25 Y0,  Y=F25 X0.
```

This is a bank exchange. A caller that requires the opposite assignment
must include its final permutation. With initial selected Q entry,
the original selected borrowed value is Q_P z. Its restoration needs
16 further positive lines; the 208 count uses initial I entry.

The review checks all 208 line-frame identities. The wrong negative
line on the first ordinary normalization fails at all 96 ports.

For every nonzero stage and every port, the review also checks

```text
Vexit_s,p F25 = F25 R_(rho_s,p),
Vexit_s,p^2 = I.
```

These 224 FULL views include the literal exit translations. They differ
from the J views in the separate reset-defect packet. No reset-packet
translation is substituted here.

`TERMINAL-WORD.json` contains the complete operator word with LINE,
MAP, ADD, and NEG events. It expands every H or D shear into its exact
coefficients and the required FULL views. Each of the eight physical
shear subwords is checked on all 224 independent input symbols. The
free-operator proof then checks their in-place composition. Sources
are restored after each shear; no scratch field or clean baseline is
used.

The exact direct invoice is

```text
positive line operations          208
H or D coefficient ADDs          1728
field negations                  112
old real scalar units          16608
FULL affine map calls           1344
extra fields                       0
odd divisions                      0.
```

Each H or D has 216 coefficients and costs 2,048 scalar units under the
inherited tariff. There are eight shears and 112 complex negations.
Six shears have a nonzero route stage and use at most 224 field maps
each. The two stage-zero shears need no route maps.

The LINE events specify exact positive operators. This review does not
provide their serialized native recipes or their host. The invoice also
omits their side maps and the final bank permutation. Every MAP retains
its stream and address cost.

## Native event invoices and scope

The review recounts native ranks and scalar prices from every stored
local event list, for both providers. This is an invoice check, not
another native replay.

The I-entry F word has mass 1,808. Each Q-entry F or selected-swap B
word has mass 1,792. Each costs 8,600 scalar units. Thus the three-call
local total is mass 5,392 and 25,800 scalar units, with profile

```text
4176 H1 + 192 H2 + 144 H3 + 32 H8 + 16 H9.
```

The local source packets supply restoration of the 416 arbitrary
auxiliary fields. This review inherits that local contract. It does
not replay the global helper host, establish a complete routed native
caller, or prove the recursive precision and supplier costs.

The producer checker uses the correct route product and quadratic
phase substitution. Its physical input decoding and output framing
match the source contracts. Its terminal calculation agrees with the
literal in-place operator word above. The completed producer receipt
is consistent with the independent checks.

Run from the repository root with fresh output directories:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/owner-review/no-reset-triple-review-20261020/check_review.py --out /private/tmp/no-reset-review-normal
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/owner-review/no-reset-triple-review-20261020/check_review.py --out /private/tmp/no-reset-review-optimized
```

Both runs must report `PASS_INDEPENDENT_NATURAL_TRIPLE_REVIEW`.
Their five JSON outputs must agree byte for byte. All input hashes are
checked again at exit. No frozen producer file is changed.

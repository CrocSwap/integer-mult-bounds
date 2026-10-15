# Two initial ordinary queries recover the first QQ16 pair at a recorded cut

This is a **scoped ordered identity**, conditional on the retained logical
QQ16 maps. It answers the two-record handoff in
[PR #2153](https://github.com/CrocSwap/integer-mult-bounds/pull/2153),
head `5646398dcdc01769df83b939c6b3eb5ecb4d5ebd`, on its explicitly granted
post-B1 observation contract. It does not construct a final-only controller.

The new assertion covers arbitrary inputs in all four bank pairs, rather
than just the erased family in that predecessor. The conclusion concerns
the original selected inputs of **pair 0**. It does not restore every bank's
selected inputs from two records on pair 0.

## 1. Precise observation contract

Use Ali Romman's conserved F/B maps from PR #1969, retained in
[CONSERVED-QQ16.md](../joint-query/evidence/CONSERVED-QQ16.md), equations
(1)--(3), and [the ordered proof](../joint-query/evidence/JOINT-QUERY-TRANSFER.md).
The first calls are F0 and B_1_2 on pair 0. Let `B_s=R_s iota_U`,
`K_s=K_(s,U)`, and write the selected sections as `P_(s,A), P_(s,T)`
with inverses `ell_(s,A), ell_(s,T)` on their respective eight-coordinate
spaces. The actual sets A and T have eight ports each; U has 96.

The following logical values are observations:

* **Two added pre-F0 records** `q0=B0 X_(0,U)^initial` and
  `q2=B2 X_(0,U)^initial`, each with eight query coordinates per owner.
  These read the original ordinary X input. Neither is a full-source
  query or a query of the changed post-F0 baseline.
* The four selected outputs of pair 0 **at the cut immediately after
  B_1_2**. We use only their sums `p_A=X_A+Y_A`, `p_T=X_T+Y_T`, and
  `d_A=Y_A` at that cut. Conservation identifies the sums with the
  original selected sums.
* The retained forward histories `f0,f2`. The other three granted
  histories `f4,f6,f8` are unnecessary for this decoder.
* `C=Y_(0,U)^final`, the completed-X descendant of pair 0 after the
  retained terminal `(X,Y)->(Y,-X)`. This is the **named final Y**,
  not the named final X carrying the former-Y hole.

In particular, the transient F0 A output is **not** saved. The decoder
reconstructs it. Nor does it read a query directly from a former-Y hole.
This contract grants logical access; it makes no claim that a physical
implementation can retain or read the observations for free.

Post-B1 selected values are explicit in PR #2153's Section 1 contract.
If only the final selected values of a particular controller are supplied,
one must separately prove that they recover `p_A,p_T,d_A`. That implication
is not supplied here. Arbitrary later selected-only operations may discard
information; this theorem does not give them an unconditional inverse.
Such operations may change later query values, but the identity below
still uses their actual logged values. The ordinary schedule must remain
unchanged, with no new writes to ordinary fields.

## 2. The ordinary tail recovers the initial Y input

Write `z=X_(0,U)^initial`, `w=Y_(0,U)^initial`, and `f=f0`.
After F0 the ordinary pair is

```text
X_U = z-K0 f,
Y_U = w+z-K0 f.
```

The B_1_2 target rule is `X'_U=X_U-Y_U`, so immediately after B1,

```text
X_(0,U)^B1 = -w.                                      (1)
```

This cancellation holds for arbitrary inputs; it is not a consequence of
the old `w=0` witness. The B source update and all selected baselines may
be nonzero.

The pinned [tail receipt](../joint-query/evidence/QQ16-SELECTED-WITNESS.json)
lists sixteen operations followed by the terminal, but omits the pair
field on local calls. We bind those fields to `recipe` in
`t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz` inside the selected
replay archive. The complete recipe also equals the retained PR377
`RECIPE-9.json.gz`, byte-pinned in SOURCES.json. Its local pair sequence
for stages 0 through 8 is **0,0,0,1,1,2,2,3,3**. The retained PR377
`PROOF.txt.gz` specifies `newX=oldY, newY=-oldX`; known physical endpoint
corrections are interpreted through the inherited logical convention.

An ordinary bridge
`src=i,dst=j,coefficient=c` acts by

```text
X_j += c X_i;    Y_i -= c Y_j.
```

The first plus bridge adds `X_1` to `X_0`; F2 acts on **pair 0** and
subtracts `K2 f2` from that sum; the following minus bridge subtracts
the unchanged ordinary `X_1`. Their combined change to `X_0` is exactly
`-K2 f2`. No subsequent bridge targets bank 0, and no subsequent local
call acts on bank 0. In particular, F8 acts on pair 3. Therefore

```text
X_(0,U)^preterminal = -w-K2 f2,
C = w+K2 f2,
w = C-K2 f2.                                         (2)
```

Other bank inputs need not be zero. Their contributions cancel across
the two first bridges, even when F2's source or query is nonzero.
The verifier propagates free operator expressions for all eight initial
ordinary bank variables and independent F histories/B drivers through
every event. It checks (2) without specializing them to the old witness.

## 3. Ordered reconstruction of all four selected inputs

Let `t` denote the transient F0 A output. The forward rule gives

```text
t = P_(0,A) ell_(0,T) X_T^initial,
X_T^F0 = P_(0,T) f,
Y_A^F0 = p_A-t,
Y_T^F0 = p_T-P_(0,T) f.                              (3)
```

The future logger in B_1_2 leaves the ordinary and T source rows alone
and writes

```text
Y_A^B1 = Y_A^F0
       + P_(2,A) [B2 Y_U^F0 + ell_(2,T) Y_T^F0].       (4)
```

Substitute `Y_U^F0=w+z-K0 f`, (3), and `B2 z=q2`. Solving (4)
for t gives the explicit decoder

```text
w = C-K2 f2,

t = p_A-d_A
  + P_(2,A) [B2 w+q2-B2 K0 f
              +ell_(2,T)(p_T-P_(0,T) f)],

X_T^initial = P_(0,T) ell_(0,A) t,
X_A^initial = P_(0,A) [f-q0-ell_(0,T) X_T^initial],
Y_A^initial = p_A-X_A^initial,
Y_T^initial = p_T-X_T^initial.                         (5)
```

Every product is ordered. The first reconstruction uses only the
two-sided selected unit identities. The second uses
`f=B0 z+ell_(0,A)X_A^initial+ell_(0,T)X_T^initial`.
Thus (5) reconstructs the four selected input blocks for every input.
There is no inverse of an ordinary query, centre response, Schur
complement, or changing-chart matrix. No condition `B1 h=0` is needed.

Equivalently, let O be the observation operator in Section 1 on all
original bank inputs and let J select pair 0's original four selected
blocks. Equation (5) is a linear map D with `D O=J`. Hence

```text
ker O is contained in ker J.                          (6)
```

This is the complete kernel implication for this explicit observation
operator, not merely its restriction to a chosen family of inputs.
It is not injectivity on all ordinary bank data: those data need not
be determined by O.

The argument is valid over the ordered logical coefficient ring whenever
the retained maps and selected units exist. In particular it applies to
the actual rational cover operators and their tensor payload actions.
No cover quotient, commutativity assumption, floating-point rank, or
identification of distinct owners is used. Actual physical access to
these operator-valued reads is a separate obligation.

## 4. Independent algebra and finite checks

The free-algebra check uses normalized selected coordinates
`a=ell_(0,A)X_A`, `c=ell_(0,T)X_T`, normalized sums, and
`D=ell_(0,A)P_(2,A)`, `E=ell_(2,T)P_(0,T)`.
It expands (5) with independent noncommuting symbols for D, E, B0,
B2, K0 and K2. The three residuals for w, c and a contain zero
terms. This is a finite symbolic check of the displayed identity;
the link to the QQ16 contract is the source-pinned written derivation.
It is not a proof-assistant formalization.

A separate rational simulator uses the literal three-step forward
source word and the backward E/exchange/H factorization, rather than
the decoder's row formulas. Two noncommuting models have query dimension
2 or 3 and four ordinary bank pairs. All 64 and 96 basis inputs pass.
Independent exact row reduction gives

| Model | rank O | rank [O;J] | rank J |
|---|---:|---:|---:|
| query dimension 2 | 18 | 18 | 8 |
| query dimension 3 | 27 | 27 | 12 |

The fixtures check failure modes, not the universal quantifier or the
actual enormous regular cover. Nine wrong decoders fail, including
discarding initial Y dirt, omitting or reversing the F2 correction,
using the wrong terminal sign, dropping either initial read, dropping
the changed source or T baseline, and reversing selected section roles.
Corrupting a query coefficient, the first negative bridge, or the local
pair assignment also fails. In particular `pair=stage//2 mod 4` is
incorrect: it moves F2 to pair 1 and F8 to pair 0. The old zero-witness
trajectory does not distinguish those choices, which is why this
general-input tail calculation binds the full recipe separately.
The packet check rebinds the actual port partition, ordinary Gram and
both selected two-sided inverses. The local native compiler and helper
restoration remain inherited from PR #1969; they are not rerun here.

## 5. Cost boundary and next implication

The added record has sixteen query coordinates per owner. This is a
storage/interface description, **not** a claim of sixteen independent
directions, sixteen paid rank units, one rank-16 recursive child, or an
optimal transcript width. The 13--15-coordinate question remains open.

Equation (5) additionally uses `B2 C` from a completed-X descendant,
two forward histories, selected endpoint values and their chart
transports. Logical reconstruction does not implement those reads or
restore query storage. A complete bill must charge the two initial
reads, their retention and cleanup, access to the post-B1 selected cut,
the completed-X query, every frame/cover map, writes/restoration,
ownership, tape and recursive precision. No favorable completed bill
has been established, so this session stops at the information lemma.
No construction is promoted from a profile-only screen.

The first useful next task is to choose an actual selected controller
and prove that its available final records recover `p_A,p_T,d_A`, or
price their explicit retention. Then price one legal `B2 C` read and
the two pre-F0 records together. Only a favorable complete budget
would justify extending this to all four pairs and a supplier.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex
assistance. Apache-2.0. Predecessor credit is retained in README.md.

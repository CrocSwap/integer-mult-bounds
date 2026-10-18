# QQ16 shear and initial normalization: exactly sixteen native lines

The paired A-to-T shear from [PR2216](https://github.com/CrocSwap/integer-mult-bounds/pull/2216),
followed by B1's initial eight X_T normalizations, needs **exactly sixteen
single-field native line calls** in the model below. The inherited prefix
uses eight calls, so this boundary-preserving implementation adds eight.
Arbitrary payload-independent scalar resynthesis, extra scalar registers,
copying and clearing do not lower that minimum.

This answers the **initial-prefix** part of
[PR2252's typed-fusion handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/2252).
PR2252 already showed that the eight bare Y subtractions have incompatible
frames. It explicitly supplied no line-count lower bound. The result here
does not exclude fusion with later B1 operations or owner/cover maps.
It gives no full controller, admitted supplier or new κ.

Evidence status: author-checked scoped proof and exact finite certificate;
no independent human review or formal-kernel proof. The selected result is
unchanged. The claim is in [discussion #2205](https://github.com/CrocSwap/integer-mult-bounds/discussions/2205#discussioncomment-18941102).

## Fixed boundary and cost model

The actual selected pairs are

```text
A = [ 0,  7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
q_T = [289, 274, 268, 448, 478, 493, 499, 319].
```

Let `F = completed(0)` and

```text
C_q = ((1+i) I + (1-i) T_q)/2,   (T_q x)(z) = x(z XOR q).
```

The retained F0 output has physical `X_p = F x_p` and
`Y_p = F C_q^-1 y_p`. This is the inherited core boundary in
[CONSERVED-QQ16](../joint-query/evidence/CONSERVED-QQ16.md#cover-action-and-native-phases).
The certificate's first eight `B_1_2` events apply `C_q^-1` to X_T;
the audit binds those exact events and checks that F0's wrappers never
write Y_T. It does not independently re-prove the retained core boundary.

Fix one owner. Factor the common invertible F from **physical** input and
output coordinates; it commutes with every translation line. For pair j,
write `a=F^-1 X_A[j]`, `t=F^-1 X_T[j]`, and `v=F^-1 Y_T[j]`.
Here v is a physical coordinate, equal to `C_q^-1` times logical Y_T.
The required complete prefix is

```text
a' = a
t' = C_q^-1 (t+a)
v' = v - C_q^-1 a.                                      (1)
```

All other data and borrowed helpers are unchanged. One existing **owned**
field C0 may have arbitrary initial contents, which are discarded; it
returns zero/I after each row. No data or borrowed helper is cleared.

The lower-bound model grants any finite number of scalar registers and
arbitrary linear scalar operations for free, including mixing, copying,
clearing and projections. Their coefficients must be independent of the
payload address/frequency. They act at the same owner and address. Each
atomic `C_q` or `C_q^-1` on one field costs one, for any binary label q;
all intermediate and restoring calls count. This relaxation even permits
scalar operations between incompatible frame types, so its lower bound
applies in particular to the legal typed subclass.

There are **no explicit owner/cover maps, payload-address permutations or
translations outside the atomic line recipes, frequency-dependent free
coefficients, multi-field native primitives, or fusion past the initial
normalization block**. Splitting native recipes to share their internal
wrappers is also outside the atomic-line model. Their two wrapper maps
are counted separately in the attaining invoice. This is a native-line
count, not a universal lower bound on recursive rank tariffs.

## Lower bound, including arbitrary scalar scratch

For binary frequency w, let `chi_w(z)=(-1)^(w dot z)`. Every permitted
operation preserves this character subspace. On it,

```text
C_q^epsilon = i^(epsilon * (q dot w)),   epsilon in {+1,-1}.
```

Compare `w=0` with `w=256` (coordinate 8). Every actual q_T above has
bit 8 set, so the eight inverse lines have eigenvalue `c=-i` at 256 and
eigenvalue 1 at zero. In the input order `(a,t,v)`, (1) has matrix

```text
M(c) = [ 1   0  0 ]
       [ c   c  0 ]
       [-c   0  1 ].
```

Select output rows `(t',v')` and input columns `(a,t)` in
`M(-i)-M(1)`. The resulting two-by-two block is

```text
d * [ 1  1 ],   d=-1-i,
    [-1  0 ]
```

and has determinant d². The eight disjoint blocks give a 16-by-16 minor
of determinant `d^16 = 256`. Therefore the difference between the two
required transfer matrices has rank at least 16. In fact it has rank 16,
since no other output rows differ. The verifier checks the actual row and
column indices and computes the determinant independently over Q(i).

For completeness, let `P(w)=G_n(w)...G_1(w)` be any candidate circuit on
a fixed enlarged register set. For its two evaluations, telescoping gives

```text
P(w)-P(0) = sum_k G_n(w)...G_(k+1)(w)
                  (G_k(w)-G_k(0)) G_(k-1)(0)...G_1(0).    (2)
```

A free scalar gate has zero difference. A single-field native line has
difference rank at most one. Multiplication and restriction to the
required input/output coordinates cannot increase rank; subadditivity
in (2) thus gives `rank(P(w)-P(0)) <= number of native lines`.
Nothing uses invertibility of a free gate. Clear, copy and discarded
owned inputs are covered, as are zero-initialized extra fields (restrict
to the original input columns). Padding with unused registers makes any
finite allocation schedule a fixed-size circuit.

The nonzero minor forces at least sixteen lines. This is a proof for all
finite circuits in the stated model, not a search to a bounded depth.
The zero-character restriction alone sees no line cost; that is precisely
why a payload-constant witness cannot certify the proposed native bill.

For positive tensor length, take frequency 256 on one payload layer and
zero on the others. For owner d use the dual frequency that pairs with
dq as 256 pairs with q. With no owner mixing the same proof applies to
each fiber. The upper identity below is linear and holds for the inherited
tensor line operators as well. The finite replay checks the nine active
coordinates at identity owner; the extensions use this written argument.

## Attaining typed prefix and its invoice

For each pair `(a,t)=(A_j,T_j)`, use one owner-serial private sweep:

```text
C0 <- 0                 in F
C0 += X_a               in F
X_t += C0               in F
C0 <- C_q^-1 C0         F -> F C_q^-1
Y_t -= C0               in F C_q^-1
C0 <- 0                 return to I
```

Complete that sweep over all owners, then execute the original
`X_t <- C_q^-1 X_t` normalization. Repeat for the eight disjoint pairs.
Every ADD has exactly equal source/target phase polynomials. The existing
owned C0 is reused, and its row body finishes before the next owner.
No full-cover scratch bank or new field is allocated. All X_A values and
all other fields remain untouched. Direct substitution proves (1).

[PREFIX.json](PREFIX.json) is the complete literal prefix in the retained
event grammar. [RESULT.json](RESULT.json) records the exact local invoice:

| Quantity | Attaining prefix | Inherited normalization prefix |
|---|---:|---:|
| Rank-one native line calls | 16 | 8 |
| Native recipe wrapper maps | 32 | 16 |
| Explicit cover maps | 0 | 0 |
| Complex scalar ADDs | 24 | 0 |
| Owned CLEARs | 16 | 0 |
| Private row sweeps | 8 | 0 |
| Scalar real-primitive bound | 224 | 0 |

The scalar bound uses the pinned QQ16 convention: 8 per unit complex ADD
and 2 per CLEAR. Native children and their wrapper maps are separate
charges, not included in 224. All restoration within this prefix is
included. Replacing the initial eight B1 normalizations by this prefix
preserves the exact frame boundary at which the unchanged suffix starts.
Composition therefore realizes B1 after the logical shear under the
inherited B1 contract; no full B1 replay or global supplier admission is
claimed here.

The initial target was zero additional native children at this boundary.
The sharp extra-eight requirement rules it out in this model, so no
controller synthesis or moment-improvement claim follows. The result
does not price physical stream/address execution, new child hosting,
complete precision growth, or all-size admission. In particular the old
precision guard must not simply be reused for a changed word.

## Exact checks and reproduction

From the repository root, with Python 3.12 and its standard library:

```sh
python3 -I -B scripts/research_package.py --package research/qq16-shear-prefix-cost
```

The main checker prints:

```text
PASS_QQ16_SHEAR_PREFIX_COST minimum_lines=16 inherited=8 additional=8 characters=512 inputs=712 controls=14
```

The registered replay also runs artifact-integrity controls. Direct replay:

```sh
python3 -I -O -B research/qq16-shear-prefix-cost/verify.py
```

Checks comprise:

- all 712 formal input/output fields at every one of the 512 characters
  (364,544 sparse output rows), including arbitrary initial C0 and every
  borrowed helper;
- exact native frame equality, sweep barriers, C0 lifetime and the complete
  event invoice;
- 4,096 computational-basis columns of the eight actual inverse-line
  recipes, checking their monomial wrappers against the translation kernel;
- a separate address-convolution interpreter for the 25 affected input
  fields at address zero, whose translation-equivariant identity covers
  their 12,800 shifted basis inputs; untouched fields are literal identity;
- the Gaussian minor, whose determinant is 256; the difference-rank
  histogram over all characters is `{0:32, 8:448, 16:32}`;
- fourteen controls, including wrong native sign/phase, equal-frame wrong
  source, omitted conversion, uncleared scratch, missing endpoint/lifetime
  obligations and the constant-payload blind spot. Thirteen reject a
  malformed claim; the blind-spot control deliberately passes only on the
  constant subspace.

The verifier imports no predecessor executable and does not regenerate
sources. `--write-results` explicitly regenerates only this package's
PREFIX/RESULT artifacts. Source and receipt corruption checks, typed JSON
changes and a Git-free read-only optimized replay are in
[test_artifacts.py](test_artifacts.py).

## Provenance and scope selection

Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
[SOURCES.json](SOURCES.json) pins every consumed main file by Git blob and
SHA-256. [TASK.json](TASK.json) records priority revision 4 and the scope
change from the suggested centre-path-sharing card to this concrete
native overhead in a centre-free replacement interface. This is a
necessary-interface side result, not completion of that card's supplier
acceptance gate. The original nonce was
`65caf5d8d22a40513a218a490c257348`; no new randomized selection was used.

Predecessors, with exact inspected heads:

- Ali Romman's retained [PR1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969),
  `a6e6ad3936f67b8f63b5b68c5e75d540610a65e7`: QQ16 maps, native grammar,
  line recipes, owned scratch and inherited core/Clifford/owner lineage.
- Cinna Davis's [PR2216](https://github.com/CrocSwap/integer-mult-bounds/pull/2216),
  `b80e9ba43367fb8b20877a97da1cb677c34f9264`: the logical shear and its
  separately scoped payload-constant witness. That rank result is not
  re-certified or refuted here.
- Charles Bethin's [PR2252](https://github.com/CrocSwap/integer-mult-bounds/pull/2252),
  `6dd49c2b186e08ef1f3efd08f62e1add97ff04a3`: the native-frame correction
  and explicit typed-fusion handoff. Its counterexample is credited;
  the new result is a sharp prefix cost and a legal attaining word.
- Cinna Davis's nearby [PR2268](https://github.com/CrocSwap/integer-mult-bounds/pull/2268),
  `daf44bfc752a5e89127defa1cb296210708cf7e6`: a further ordinary-source
  tap. Its observation kernel and full-tail behavior are outside this
  package; no tap search was performed.

Pending PRs supply context, not executable dependencies or supplier
admission. The native semantic and monomial checks follow the credited
retained methods in a separate implementation. All source packages and
their licenses/notices remain unchanged. New material is Apache-2.0.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

## Open next questions

1. Can fusion **past** the first eight normalizations use later B1 native
   operations to realize the shear with no additional calls? It matters
   because those operations are excluded from the fixed endpoint here.
   First choose one later cut and derive its complete physical transfer,
   including arbitrary helper outputs, before searching. The blocker is
   that its later cover maps invalidate the two-character local invariant.
2. Can a different useful controller change avoid this prefix endpoint
   altogether? First demand full selected-input recovery on arbitrary data
   and an explicitly typed boundary; then count children, maps, storage,
   restoration, precision and hosting. Witness separation alone does not
   establish that recovery, and this package supplies neither a controller
   nor its completed budget.

The structured versions and stopping tests are in TASK.json.

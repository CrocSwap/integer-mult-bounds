# Native caller handoff

No PR, commit, push, or publication is authorised. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
Preserve all frozen packets. Use one CPU in this lane.

The phase-coded caller removes the centre-dependent terminal correction.
It leaves a common portwise q factor on both original input banks.
The same common q remains after three such triples through D73.
No recursive consumer for that factor has been admitted.

The current follow-up concerns a different unitary centre code. The
three current scalar stage codes cannot close to a monomial unless
each is monomial. They cannot commute with Q unless each is diagonal.
These statements now have direct common-input spatial witnesses. The
old unverified small-representation independence argument is not used.
Read the closure section below for the precise width and code limits.

## Current phase-coded caller

Read `phase-coded-triple-20261020/PHYSICAL-ENDPOINT.md`.
Its source is the controller lane's frozen phase-coded native word.
For the Q-entry variant, three legal FULL shears give

```text
X = -F25 q Y0,
Y =  F25 q X0.
```

Both X0 and Y0 are arbitrary physical inputs. The first shear is
`X_R-=D1 X_P` after the complete stage-1 sweep. The last two are
`Y_P-=H2 X_R` and `Y_P-=H0 Y_R` after stage 2. The middle and
stage-2 shears use the literal FULL affine views and translations.
No ordinary hole is read by a scalar shear.

The normal and optimized checks pass all 224 data columns and all
1,344 phase identities. The endpoint has exactly 224 stored operator
terms after the shears. The source native replay covers all 640
local columns, including 416 arbitrary helpers; that local replay
is inherited rather than repeated in this caller check.

```text
phase-coded-triple-20261020/FREEZE.json
0ee32fe22f42cffce2a9673f0dc95496a4b4bb8b11a534f77a11f5fe9c7aeb4b
PHYSICAL-ENDPOINT.md
5eb5eba5d3bed38faf9e411ca4a9a6f8e67765966011e93dec96f2300613756f
check_phase_coded_triple.py
82a36b9f258d1aa2d95830502b336eb8aae9e7beff643b1f854c3d87451098f6
run-normal/CHECKS.json
44a1c03836ba47af92965dc7d2bb716d0f94d03dd54cb3122eeaa9f1d08a3cc3
```

The local Q-entry native mass is 5,376. It needs 224 positive
line operations for the direct terminal. The initial I-entry mass
is 5,392 and it needs 208 lines. Both totals are
`5600=224*25`. The three added shears have a direct upper bound
of 6,144 scalar primitives and 448 affine field-map calls.
The existing factored scalar code can give a smaller scalar bound,
but this caller packet uses only the direct coefficient bound.

The signed output convention is explicit. An unsigned convention
adds 112 field signs, at 224 scalar primitives, unless the caller
uses the signed exchange directly.

The independent child review passed with a separate phase engine.
It is in a separate packet; the frozen producer files are unchanged.

```text
owner-review/phase-coded-triple-review-20261020/FREEZE.json
700415b75d8f9d20225ee67371adac8d8d7716369171927612690d0e6a7716b9
REVIEW.md
8342f508f9c2432a01ef196820d5c94b98df012c63f21d560940c8799e337c0c
CHECKS.json
ccdcf2033f575921fc3222017b57bbadcca7f4575cb42139f388718bfb266bb1
```

The coherent-port lane owns the recursive common-q interface.
The new-core lane owns a prospective direct native implementation
of the same local phase-coded map. The current source is the
4,632-scalar local word; do not replace its cost with a prospective
2,912-scalar word before that word is emitted and reviewed.

## Nine-call D73 chain

Read `phase-coded-chain-20261020/CHAIN.md`. Nine calls, grouped as
three triples with their three FULL shears, give

```text
X = F73 q Y0,
Y = -F73 q X0.
```

The q factor does not accumulate once per triple. The native mass is
16,128, and the direct terminal adds 224 lines, for 16,352=224*73.
This is not a strict moment gain. The checker verifies 3,584 natural
boundary phase identities and 1,008 FULL-shear view identities.
The normal and optimized outputs agree.

```text
phase-coded-chain-20261020/FREEZE.json
dd982cc272aa204f8a3d0d82069b7263c21077e03a472a44e59e2bec6fcce47e
CHAIN.md
123ba331ea24a23c0fb775b6e6e3bec2409acdacc938d45f026c54ec0d3bbfa2
GENERAL-VIEWS-REVIEW.md
9e8c73d3bfaade6d9d06f8c472b88ad52cce624fe2e602c143cd1705c8f662b0
```

The general-view review checks the quadratic-refinement proof and
the spectator-axis extension. It does not turn the current response
into a stage-independent scalar matrix or prove a recursive host.

## Current scalar-code closure

Read `unitary-code-closure-20261020/CLOSURE.md` and
`GENERAL-CLOSURE.md`. The exact D25 source and the actual unitary
code are pinned in the checker. There is no native code-C service
or recursive join claim in this packet.

For three invertible scalar codes C0,C1,C2 in their current charts,
the path through j,r has route

```text
M = rho_(2,p) rho_(2,j) rho_(1,j) rho_(1,r).
```

The common logical input `(e2,e1)` separates all 12,544 paths at
width f at least 2. The common physical input `(0,e2,e1)` separates
their literal affine versions at f at least 3. A third Fourier
character gives an exact nonzero Q-commutator witness for any path
that breaks the intrinsic line.

Thus monomial closure holds only when all three scalar codes are
monomial. Q commutation holds only when all are diagonal. Every row
of all eight actual C/C* variants has an explicit nonmonomial basis
witness and a nonzero commutator witness. Both sets have 896 entries.
The bound-normal and bound-optimized outputs are byte-identical.

The direct spatial proof does not assume independent regular owners.
Its covariant lift to the declared regular cover is explicit. No
f=1 conclusion follows from this proof. The separate cover lane has
an additional owner-isolation proof under the full-cover premise.

The general-stage extension uses tags `(e_T,...,e_1)` to recover
all intermediate ports. Logical monomial closure needs f at least T;
physical affine closure and Q commutation use f at least T+1. These
are sufficient bounds, not width optima.

The standalone independent representation review is frozen:

```text
owner-review/unitary-code-closure-review-20261020/FREEZE.json
b3fc9ddc6fdc4cc6c2226b3b9fa101abdb21d22e50ceb3d6c9cefa9280062deb
REVIEW.md
f5bc725b9f14032e5a61341ed73306b45797b90612e256e6e3caa52e6360a3dc
```

The final producer, literal affine binding, and general-stage proof
review are frozen:

```text
unitary-code-closure-20261020/FREEZE.json
ec5d251c2c183fe2fcf5fd51bc9c4806bff6ca0129e08ebaffd4a017503eb160
CLOSURE.md
63c0deeb7e13b359ca410dfb085e1a89866aa87383d6bd1cec02cba688a4ce3e
GENERAL-CLOSURE.md
a9bc32fc805b83c6317cc62b8c5982dee2d15d73a4065a50ab4e797e3c85826a
bound-normal/CHECKS.json
f1e418155b89f8add0f066c80da2ab3a1120e6d78f047753e7e0698daf506a3a
owner-review/unitary-code-closure-binding-20261020/FREEZE.json
7e572942617d880931f52f47849b23174b903f57a199a99134b96ed5cac21ea6
owner-review/general-scalar-closure-review-20261020/FREEZE.json
6f5fbbf6565d2a6078b8ec627722c52c8f94fe0690ae6da1a543e7c3f767022d
```

Do not treat the earlier `run-normal` or `final-normal` receipts as
the final source-bound receipt. The current checker is bound by
`bound-normal/CHECKS.json`. The final review recomputed all literal
affine paths and all 1,792 basis and commutator witnesses. The
general-stage review is a separate proof read, with no new path
enumeration or native cost claim.

The theorem permits different coefficients at each stage and also
permits diagonal terms. It does not cover old-chart controls,
operator-valued codes, changed gathered interfaces, or a paid joint
decoder. Route counts are not native child counts. The root and
coherent-port lanes are investigating a recursive coded consumer.

## Reciprocal response: three actual reader cuts

The actual response E=P R has sixteen-row reflection factor
R-I=U ell. Current-I pre-Y P and raw-FULL post-X P give the
common-P forward and reciprocal backward shears. Keep the
stage order. With

```text
t=y+R0 x,
w=x-(P0^-1 R1 P0)t,
```

the three required readers are

```text
c0=ell0 x,
c1=ell1 P0 t,
c2=ell2(P1 P0)w.
```

Their stored arguments are present at the actual source cuts:
c0 and c2 use raw FULL X before post-P; c1 uses current-I Y
before pre-P1 and all native input adapters. The accumulated
P factors require no extra old-stage query.

The returned record types are F9, F9 q_anchor, and F25. The
middle record is a hole record. Do not call it FULL or omit
its remaining line progression.

Each conditional read has 136 complex signed ADDs, or 1,088
real scalar units, into sixteen independent accumulators in
the stated body frame. The accumulators can be arbitrary,
but their old values remain present. The local prefix row
one-norm is eleven and the word adds no coefficient denominator.
All three formations cost 3,264 units only if those typed
accumulators are supplied.

```text
reciprocal-reader-cuts-20261020/FREEZE.json
4442f8dba6a6940bbc63e52ec17bce96fdcc4879dd5113e0a9ea06067d986992
reciprocal-reader-cuts-20261020/SOURCE-CUTS.md
0da0fb811c2c2841ac63b77ea678fa973000b79408cc2d4d825167d721bf5c02
reciprocal-reader-cuts-20261020/bound-normal/CHECKS.json
bf1722a6ee21a5c14f50db6b848972a4bbc9fc56ec69c301357103cdc02e6c9b
reciprocal-reader-cuts-20261020/bound-normal/READERS.json.gz
decompressed f0a3eb19e09f425fc87e3563af72a7879f9cf64799fee0dcbd059bd297bc8045
owner-review/reciprocal-source-cut-review-20261020/FREEZE.json
03e045189845e0e0bf8722e54cc180f3083d32f752d98f900cfbce9647bc46cc
```

The producer checks all 656 local input columns and 672 exact
phase identities. The separate review reconstructs the model
from mode and pair data, checks 1,792 exact phase identities,
and binds all serialized reader and immediate inverse instructions.
Both normal and optimized outputs match. The independent review
found no material error.

The native source is the frozen reciprocal word with decompressed
hash f528752be6222da2b64522f9a124622acab4413e79d403d58b592d2533307d1e.
The source-cut checker pins its complete entry and exit metadata;
it does not replay that native word. The native contract remains
a separate dependency. Internal unused-cut coalescing does not
change these complete-word source cuts.

No safe accumulator allocation, zero baseline, owner lease,
record transport, or late erase is supplied. An immediate inverse
read restores arbitrary accumulators only while its source stays
unchanged. The complete reciprocal decoder also needs its Q-coded
X scatter. These obligations remain open.

## Earlier clean natural triple

The natural clean F/Bswap/F word is fully checked as a physical
endpoint. It has a direct 208-positive-line operator terminal.
It retains a sixteen-row query through ordinary Y holes before
that terminal. The new phase-coded word changes the local response
and escapes that particular query.

```text
no-reset-triple-20261020/FREEZE.json
089425bdf431d81456e1c988a1fd21a837baca43e510bc92dee98dc2ee571791
owner-review/no-reset-triple-review-20261020/FREEZE.json
65b7bd0119e4dc189a428d604c65dd94cf458ba3a7618d4fb0bb979ade7dd62c
```

The independent review contains a literal operator terminal:

```text
owner-review/no-reset-triple-review-20261020/TERMINAL-WORD.json
e0b356266c026455ddd81e869ff1270fdbe00e342367aac8173026afb446fa88
```

It uses LINE, MAP, ADD, and NEG events. It is not a hosted native
recipe. It costs 208 positive line operations, 16,608 scalar
primitives, and 1,344 affine map calls, before line side maps and
the final bank exchange. Do not emit a duplicate scalar terminal.

The other independent-review lane factors this same terminal as

```text
diag(Q_P,Q_R^2,-I) W^-1 L W,
W = diag(I,Q_R,I).
```

This acts on `(beta,h,R)`, where `h=q_R r`.
Selected X signs and the final bank exchange are separate.
The dyadic unit L has an eight-shear word and a displacement
factor through at most 48 field arrays. No cheaper native
lowering of this conjugation is known.

```text
independent-review-20261017/no-reset-terminal-factor-20261020/FREEZE.json
1b1f191e9de1ef20b88aca6d870f93fe68b0923e8b05a87d9ca7d960e0385963
owner-review/no-reset-terminal-factor-proof-review-20261020/FREEZE.json
80cd2d0c033ba4fa44b78b3335742038d40f71e79ae615d1010874ca2a53bab8
```

Both independent proof reviews found no material error.

## Earlier reset two-call result

The clean F/reset/Bswap word puts the original data in one FULL
bank, but only as `F17 q X0`. Its other bank still has an arbitrary
borrowed baseline. This is not an original-input Fourier endpoint.

```text
coupled-data-split-20261020/FREEZE.json
9ffcc73fe0a8afc34c3a16aec400ab4cdcaa4904213716f48e91c7c79527c308
independent-review-20261017/coupled-two-call-review-20261020/FREEZE.json
4cc4d8ca3c6c63c8c5a77e0e01a613a56910d968c95dc2c5c402ef2526077659
```

The earlier access concern is resolved. Gamma in this packet means
only the literal orthogonal rho. It never means `F0 q`. The
literal translations prove the entry and exit identities.

## Other retained results and limits

The current-I-Y joint reader obstruction, the reset-defect
factorisation, and the exact rational code services remain in
their separate frozen packets. Their scopes do not automatically
apply to the changed phase-coded local response.

The previous `HANDOFF-20261020.md` records the rational code
services. The rank-thirty in-place translation compiler described
there remains an unexecuted draft. It is not a validated service.

An exact FULL-only null family was calculated for the old clean
triple. It uses a sixteen-column ordinary right inverse of H0,
with determinant one eighth and integral inverse. This witness
has not been frozen in a separate packet. The new phase-coded
response escapes it. Do not treat the unfinished witness as a
general native lower bound.

No complete supplier, recursive host, numerical-grid proof, or
complete kappa gain is claimed by these caller results.

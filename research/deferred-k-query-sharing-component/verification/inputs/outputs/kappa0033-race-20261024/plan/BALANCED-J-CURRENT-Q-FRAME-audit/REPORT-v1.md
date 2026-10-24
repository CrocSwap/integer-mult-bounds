# Current source Q: exact physical frame audit

**Decision: `BARE_CENTRAL_Q_SOURCE_BOUND_K_CONJUGATED_ROUTE_REJECTED`.**

On the canonical returned fields of the pinned balanced-J native interface,
the required positive query is the same bare physical central-axis C gate on
every port and mode. It is not the family `K_i^-1 Q K_i`. The supplied K words
centralize full R, but do not in general centralize Q or D separately.
This audit supplies a direct analytical counterexample from the actual mode0
word, with absolute phase, rather than inferring physical failure from a
formal nonzero expression. No scientific engine, emitter, phase checker,
provider replay or test was executed.

## 1. Primary definitions resolve the ambiguity

Use the exact source files under
`swarm-provider-audit-sol-high-20261024/repository/research/`.

* `coded-native-caller/PHYSICAL.md`, line13, defines Q as the central C gate,
  D as the product of the other eight C gates, and R=DQ.
* `native-rank8-helper-provider/verify.py`, line427, constructs
  `R=frame(1)` and `D=ce.fourier(9,range(1,9))`.
* The pinned decompressed `native-center-free-code/SOURCE-WORD.json.gz`
  has `canonical.frames[1]=[256,128,64,32,16,8,4,2,1]`, a full9 frame.
* `coded-native-caller/clifford_exact.py::canonical_frame` returns
  `fourier(n)` when the frame has full rank n. `fourier(9)` is the ordered
  product of positive `cgate(9,1<<i)` for i=0..8. These act on disjoint bits
  and commute exactly, including phase.

Therefore, on the source nine-axis physical array,

```
Qp = Qh = C_(mask1,+)
Dp = Dh = product_(j=1..8) C_(mask(1<<j),+)
Rp = Rh = product_(j=0..8) C_(mask(1<<j),+) = Q D = D Q.
```

The same formula applies to promoted k after its exact whole-job aliases.
Since D is invertible, the required Q is uniquely `R D^-1`; the equations
do not leave a choice of per-owner conjugation family.

In the balanced packet, the source9 axes embed into ambient25 as
`[0,9,10,11,12,13,14,15,16]`. Hence Q remains positive C on physical axis0;
D_s acts on private axes9..16; R_s acts on their union with axis0. The other16
axes are spectators. This is also the packet's explicit stage geometry.

## 2. Actual output boundaries bind these operators

This is not just a convention inferred from a polynomial ring. The provider
verifier uses actual compiled physical boundary words and checks:

```
lines471–473:
  OX final birth^-1 BX = D
  OY finalY BY         = D
  OX final BY          = R

lines478–485:
  actual helper-to-main coupling = R Kp_i^-1 Km_j
  actual main-to-mode coupling   = D Km_j^-1 Kp_i
  N_j F8_j Km_j                 = D.
```

Here the displayed operator products apply rightmost first; source `.then`
executes left operand followed by right operand. The checks compare complete
signed tableaus and exact zero-column states, so their inherited evidence
fixes absolute phase. The exterior source coefficients supply W and Z:

```
W_ij = (M_ij/2) Kp_i^-1 Km_j
Z_ji = (M_ij/2) Km_j^-1 Kp_i.
```

The source separately checks `Kp_i R=R Kp_i` and `Km_j R=R Km_j`
at lines451 and465. These checks explain full-R intertwining of W/Z and J.
They do not turn the diagonal D into `K^-1 D K`, and do not authorize
inserting K around a subsequent physical Q.

The mode-output N has already been applied inside the pinned provider; its
normalized result is D times the stated input combination. There is no
remaining hidden N or Km frame that must be stripped before a Q call.
The returned-mode division by4 is an exterior scalar and changes no address
frame. The current Q occurs after all these output boundaries and aliases.

The promoted H8 alias deserves a separate distinction. Its source canonical
rank8 child acts on axes0..7, whereas the desired D8 acts on axes1..8.
`INVERSE-AND-HELPER-REVIEW.md` explicitly binds the axis0/axis8 permutation
and actual two-sided aliases that make this conversion. After stage lifting,
the result is D_s on axes9..16. This already-paid whole-job conversion is
not a reason to conjugate current source-bank Q by Kp or Km. The current
120-bank query does not act on the promoted k bank at all.

## 3. Actual mode0 counterexample to the proposed K route

`PROVIDER.json.mode_boundaries[0].input_K.literal_word` executes:

```
D(quadratic=0, linear=[2,2,2,2,0,0,0,0,0])
P(rows=[7,13,11,14,16,32,64,128,256])
X(0)
phase(0).
```

Thus its physical operator is `K=P_G Z_15`, with rightmost applying first.
On the first four coordinates the displayed G is symmetric and involutive;
`G(1)=7`, `G(7)=1`. The other coordinates are fixed. Consequently

```
K|0>       = |0>
K^-1|1>   = -|7>
K^-1 X1 K = -X7.
```

The exact source C gate is
`Q=a I+b X1`, where `a=(1+i)/2`, `b=(1-i)/2`. This formula is used here
only for one physical column at width1, not as an all-width shortcut.
The proposed execution `K; Q; K^-1` therefore has

```
(K^-1 Q K)|0> = a|0> - b|7>
Q|0>          = a|0> + b|1>.
```

The unequal addresses and nonzero coefficients are a concrete physical
counterexample, including the minus phase. This follows directly by reading
the pinned literal word and the source C definition; it is not a newly run
test or a claim that arbitrary formal nonzero expressions are physical.
After the stated stage embedding, local7 becomes global mask1537
(`axis0 + axis9 + axis10`), whereas local1 remains global mask1.

Hence Km0 does not commute with Q. Since it commutes with R=QD, it cannot
commute separately with D either. One rejected mode already invalidates the
claimed uniform routed Q120 contract; no broad 120-field phase census is
needed to establish this specific failure.

There is also a direct attainable pre-query input for this discriminant.
The native returned source map is `D_s J_s`, an invertible operator on all120
independent source originals. Choose the returned Vprime bank to contain
only mode0 payload `|0>` and choose original `v=J_s D_s^-1 Vprime`.
Then the bare and routed queries produce exactly the distinct mode0 outputs
above. Arbitrary initial v is allowed by the pinned ABI. This is an existence
argument for a physical counterexample, not execution of that input.

## 4. Why the accepted old-h query and the new query use the same Q

The passed base packet has SHA256
`7f26477b561114e1189d1ac7e00fd5cf5b1aea4881433619c931c12c01eb1ffd`.
Its `QUERY_OLD_H` instruction copies original h before entering any K frame,
then applies `GAUSSIAN_Q` with `rank=1,axis=0,sign=+1`. In the inverse,
it queries the recovered old h only after undoing the common frames.

The independent checker requires that exact raw instruction and models it as
q. Its successful result binds source/alias/native receipts while explicitly
setting `source_phase_replayed=false` and
`optional_current_source_120_queries_installed=false`. Thus the pass is an
independent ordered boundary proof under the retained physical ABI; it did
not independently recertify Q on arbitrary owner charts or install Q120.

The new current query is also on canonical returned fields. Their logical
values differ from old h, but their physical array coordinates have the same
Q axis. The required equation is exactly

```
Vprime = D_s J_s v
E      = Q Vprime = R_s J_s v = J_s R_s v.
```

It uses only `[R_s,J_s]=0`. Inserting a per-owner K conjugation would instead
give `Qhat D_s J_s v`; source guarantees neither `Qhat D_s=R_s` nor the
desired encoded-source interface. The analytical example above proves
failure for the supplied proposed Qhat. No change to the accepted base-T
result is warranted by rejection of this new route.

## 5. Inverse query and all-width phase prescription

The positive source gate satisfies `Q^2=X1`, `Q^4=I` exactly. Therefore

```
Q^-1 = X1 Q = Q X1.
```

Use bare positive Q on central0 plus the ordinary central bit translation;
no K frames surround either operation. PR5411 `verify.py`, lines253–259,
already verifies the general positive-C_r-plus-bit-translation identity
against the actual inverse including absolute phase; rank1 uses mask1.

At width f, lift Q and all monomial words columnwise. The inverse correction
is central bit translation in every payload column. The mode0 K phase is
also lifted per column. Exterior owner coefficients remain exterior once.
One must not write a single global two-term Gaussian formula at width f>1.

The current-query cost is120 paid H1 with **zero K routing maps forward**.
The inverse uses120 paid H1 and120 ordinary central translations. The
additional240 K/K^-1 maps proposed for Q120 do not implement the required
operator and must not appear as its route. This restores the earlier strict
deferred-K external monomial totals1168 forward and1288 inverse, including
the800 inherited alias maps, under that report's stated remaining inventory.
Native internal work, correction frames and separate consumer costs remain
charged. This finding grants no existing thin-query reuse or target credit.

## 6. Actionable gate and scope

Emit the changed packet with120 explicit bare positive central0 calls on the
exact current returned fields. For its inverse, use positive central0 calls
and the120 exact central translations in the stated order after undoing the
K correction. Keep the accepted base packet and receipt immutable.

Include a wrong-K-conjugation rejection control in the new packet review.
The mode0 zero-column calculation above gives its independent physical
oracle. If a registered test is later wanted, the smallest direct phase test
is that one pinned mode0 word on width1 basis0, plus the primitive inverse
identity; it does not require an expanded native replay. This audit does
not request or run such a test. The packet's all-row and ownership check
remains separately necessary after emission.

**Research discussion / PR / artifact:** this report and source-hash manifest;
no external publication.

**Exact commit:** native PR5402
`3348fccea855082786d5f0fc5558b73d4974e745`, actual inverse PR5411
`123ffa6aa7c1866ac60c67739841f71d95b3edf7`; local base packet and passed
receipt are bound by their exact bytes in the manifest; no new commit.

**What is established:** bare central Q is the uniquely source-bound query;
the proposed K-conjugated family is physically different; inverse phase and
stage axes follow from primary definitions and the retained exact checks.

**What remains uncertain:** new packet assembly and its independent local
verification, all global caller/query-reuse economics, target admission and
kappa. No whole-caller search or scientific replay was duplicated.

**Smallest useful next task:** packager emits the raw-Q packet and explicit
wrong-K control; root reviews its separately prepared run request.

**Reproduction command and expected runtime:** none executed or required for
this analytical source audit. Inspect the pinned definitions and the four
literal mode0 gates; source hashes can be checked independently.

**Predecessor credit:** Dugongue's coded physical normalizers and the retained
native/Clifford sources define the operators; the PR5402/5411 provider authors
and independent helper/boundary reviewers supply accepted physical premises.
Root identified the frame ambiguity and the primary prose binding. This
Codex-assisted audit independently joined the executable definitions, output
boundaries, literal phase counterexample and required packet correction.

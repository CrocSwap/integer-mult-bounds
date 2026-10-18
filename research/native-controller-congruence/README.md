# A determinant obstruction for native source-code controllers

**Scoped structural result; no new supplier or kappa.** Ali Romman’s [PR #1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862) supplies exact
local identity transfers that store an eight-coordinate centre query in
existing data fields. Its remaining obstacle is a complete controller that
removes the source code while delivering the required data endpoint. This
package rules out an unbounded class of proposed controllers, rather than
searching words only up to a length cutoff.

For one fixed source code, every completed controller built from [PR #1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862)'s
forward/backward transfers, their inverses, and arbitrary invertible scalar
mixing of whole port banks must have **signed code winding divisible by six**.
The statement allows any number of data banks and restored dirty auxiliary
banks, arbitrary dyadic scales and signs, and arbitrarily long words. It rules
out the inherited nine-call, four-pair scalar skeleton, whose winding is -1,
under this fixed-code substitution. Merely repeating a fixed code until its
sixth power is the identity does not remove this controller constraint.

A complementary result allows a different admissible source code at each of
three calls. In an F-B-F exchange, the unwanted diagonal block has rank at
least eight for **every** choice of those charts with the retained R and K.
Changing the selected rows inside this three-call architecture cannot remove
the defect. This is stronger than testing the predecessor's one fixed chart.

These are controller-interface obstructions. Port-dependent scalar maps,
physical changes of chart, new clean workspace, and paid repairs remain
outside the first theorem. The second theorem does not include interleaved
bank mixing or arbitrary native chart transports. Neither result is a lower
bound for all multiplication algorithms or a rejection of [PR #1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862)'s valid
local construction.

## The pinned local interface

Write a port bank as an n-vector. [PR #1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862) works over the dyadic coefficient
ring with maps R of size r by n, K of size n by r, and maps P,L satisfying

```text
RP = I,    LK = I,    LP = 0.
M = RK,    Z = K - P(M-I),    Q = R-L.
G = (I-PL)(I+ZQ) = I + ZQ - PR.
G^-1 = I + PL - ZR.
```

Its completed local content maps, with the native frames and charges still
required, are

```text
B_G(x,y) = (x-y, Gy),
F_G(x,y) = (G^-1 x, y+G^-1 x).
```

The actual source has n=112, r=8, K=R^T/4 and RK=14I. The selected sets are

```text
A = [0,7,20,27,36,46,57,111],
T = [21,37,47,76,81,87,92,110].
```

The identities QP=LZ=I and QZ=LP=0 split each bank uniquely into

```text
y = w + Pu + Zv,    Qw=Lw=0.
G: (w,u,v) -> (w,-v,u+v).
```

Consequently G fixes a 96-dimensional subspace and acts on eight
two-dimensional sections by `[[0,-1],[1,1]]`. Its minimal polynomial over Q
is exactly

```text
f(t) = (t-1)(t^2-t+1),
```

not just a polynomial that happens to annihilate G. Both summands are
nonzero, and the two factors are coprime. In particular, the algebra Q[G]
is faithfully represented by `A = Q[t]/(f)` and t has order exactly six.
The local construction and these identities retain [PR #1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862)'s attribution.

## Theorem 1: balance for every word in one fixed chart

Take any finite number b of whole n-port banks. Each bank initially has
arbitrary independent contents. An auxiliary bank, if present, must be
restored for every initial value. The permitted controller operations are:

1. A B_G or F_G transfer on any ordered pair of distinct banks, or its true
   inverse, with the same G throughout.
2. Any invertible scalar bank map `S tensor I_n`, where `S` is a b by b
   matrix over Q. This includes the inherited bridges, signs, permutations,
   arbitrary rational scales, and their dyadic special cases. All scalar
   work must still be charged in a physical implementation.

Require the completed map on all banks to be a specified invertible scalar
bank map `T tensor I_n`. Restored auxiliary banks contribute identity blocks
to T. The theorem also permits scalar cross-bank terms if they are explicitly
part of the required endpoint. There is no controller-level CLEAR or
assumption that an auxiliary bank begins clean.

Assign winding +1 to B_G and F_G^-1, and -1 to F_G and B_G^-1. Let w be the
sum over the word. **Then 6 divides w.**

**Proof.** Work with b by b matrices over the commutative algebra A. The
nontrivial two-bank blocks are

```text
B(t) = [[1,-1],[0,t]],       det B = t,
F(t) = [[t^-1,0],[t^-1,1]], det F = t^-1.
```

Inverses have reciprocal determinants. Embedding a block in any pair of
banks leaves its determinant unchanged. Let delta be the product of the
determinants of all scalar operations; delta is a nonzero rational number.
Multiplicativity of determinants gives

```text
det(controller) = delta * t^w = det(T)  in A.
```

Evaluation at t=1 yields delta=det(T). Cancel that nonzero rational number.
Evaluation at a primitive sixth root zeta, which is another homomorphism
from A, now gives zeta^w=1. Therefore w is a multiple of six. This proof is
independent of word length and of the number of banks. It does not use a
finite search as a universal inference.

Every macro occurrence contributes an odd integer, +1 or -1, so **an odd
number of these macro calls cannot have the required scalar endpoint**, even
if inverse calls are allowed. Divisibility is only necessary: a word of
winding zero or six need not be a correct controller.

The ordinary determinant of the full 112b-dimensional rational matrix would
miss this constraint: det(G)=1. The useful determinant is over Q[G], whose
fixed and cyclotomic components must both have the requested endpoint.

**Corollary: coherent changes of basis do not evade the constraint.** At
boundary k let `H_k=diag(U_k,1,...,U_k,b)` be an arbitrary invertible
bankwise change of coordinates. Suppose each physical operation is exactly
`H_k N_k H_(k-1)^-1`, where N_k is one of the normalized operations above.
A local code that keeps its coordinate chart has the form `U_i G U_i^-1`,
and a scalar bridge within a fixed chart has transport `a U_i U_j^-1`.
If the charts also change during the operation, the incoming factors are
instead `U_(k-1),i^-1` and `U_(k-1),j^-1`, respectively, as in the displayed
general formula. A passive change of coordinates has N_k=I. The physical product telescopes to

```text
H_m (N_m ... N_1) H_0^-1.
```

If the required endpoint is `H_m (T tensor I_n) H_0^-1`, including the
specified final gauges and complete source restoration, the same proof
forces 6 to divide w. The matrices U need not commute with G. This is an
exact conjugacy condition, not a claim that the actual native routing maps
satisfy it. A proposed escape must change the normalized operation or its
endpoint contract; relabeling the same code coherently is insufficient.

## Application to the inherited nine-call scalar skeleton

The retained four-pair construction starts with F_0 and then uses
`B_0,F_0,B_1,F_1,B_2,F_2,B_3,F_3`, with scalar bridges and a final signed
exchange. It therefore contains four B calls and five F calls. Bridges and
the signed exchange are scalar whole-bank maps; they cannot change w=-1.

Substituting one fixed [PR #1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862) source code into this skeleton cannot give its
required scalar identity, regardless of how its scalar whole-bank controller
is redesigned. This covers all whole-bank scalar repairs at the same nine
macro calls, not only the displayed bridge constants. More generally, no
odd-call controller in the stated class works.

This is a statement about a fixed-code interpretation of the inherited
scalar skeleton. Actual native stages have port-dependent address routes
and frame changes; the theorem does not identify those different physical
charts with a single G. It also does not establish a lower bound on the
number of children in a successful replacement. In particular, a true
inverse macro may undo native frame progress, so an algebraic cancellation
fixture is not an admitted supplier.

## Theorem 2: a rank-eight defect for every three-chart F-B-F exchange

Now fix R and K but allow each chart s to choose its own P_s,L_s, satisfying
the same three identities. Let G_s be its resulting code. Ordered
multiplication gives, without assuming M=RK is central,

```text
R G_s K = M-I,       R G_s^-1 K = I.
```

For arbitrary admissible charts a,b,c, the exact three-call content matrix is

```text
F_c B_b F_a = [[0,                -G_c^-1],
               [G_b G_a^-1,       G_b-G_c^-1]].
```

The desired signed exchange has zero lower-right block. Let
`D=G_b-G_c^-1`. Then

```text
R D K = M-2I.
```

Over a field, rank(D) is at least rank(M-2I). For the actual RK=14I over Q
or Q(i), this gives **rank(D) >= 8**, independently of all three selected
chart choices. No inverse of M is used. The same statement cannot be
inferred in characteristics that annihilate 12.

Separate invertible input and output gauges on each bank multiply D on its
left and right by invertible maps and preserve its nonzero rank. Thus these
endpoint gauges cannot turn the exchange into a matrix with that block
zero. This observation does not allow interleaved bank mixing, changes to
R,K, operator-valued chart transport, or a paid cancellation of D.

The rank bound concerns the unwanted data map. It is **not** an assertion
that exactly eight native children implement its cancellation, nor a lower
bound of eight for arbitrary physical implementations. An admissible repair
still needs its source access, frame moves, restoration and full invoice.

## Reproduction and evidence boundary

From the repository root:

```sh
python3 -I -B research/native-controller-congruence/verify.py
python3 -I -O -B research/native-controller-congruence/test_verify.py
python3 scripts/research_package.py --package research/native-controller-congruence --check-only
python3.12 scripts/research_package.py --package research/native-controller-congruence
```

The written determinant proof establishes the unbounded statement. The
exact verifier checks its finite algebraic premises and meaningful controls;
these finite checks are not a proof-assistant formalization. The package
records its checked inputs, receipt and failure controls separately. The
source record and predecessor references are bound in [SOURCES.json](SOURCES.json),
and [TASK.json](TASK.json) records the changed scope from `centre-path-sharing`.
The predecessor proof and notice are exact text copies under `references/`,
with their original relative links referring to the pinned upstream package.
No predecessor executable is imported.

The source-bound verifier reads three pinned members of the selected [PR #1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094)
replay archive. Its local word and program payloads are byte-identical to the
[PR #1042](https://github.com/CrocSwap/integer-mult-bounds/pull/1042) inputs consumed by [PR #1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862). It replays the **112 source columns only**
up to the forward centre cut, derives R,K,P,L and the 96+16 decomposition,
and checks `RDK=12I_8` for all four pairs of the actual A/T and swapped T/A
charts. The retained parent `GLOBAL-TEMPLATE` supplies only the exact
`(pair, reverse, stage)` recipe; its older embedded provider program is not
executed. This is not a replay of current helper or native endpoint behavior.

The separate dense rational checker imports neither `verify.py` nor
predecessor code. Its 12 tests include 108 macro/scalar interleavings over
two, three and four banks; inverse and sign/scale controls; a six-call
algebraic exchange; noncentral-M and changed-chart rank fixtures; and
isolated CLI tests that reject changed result, archive-pin and predecessor
text inputs. The six-call example proves that the condition is only
necessary and that legal signs must be included; it does not establish
useful native frame progress or an affordable supplier.

The registered replay passed on CPython 3.12.14. The primary verifier also
passed with `-O`, and the repository research-workflow suite passed 45 tests
with three platform skips. Commands and environment are in
[VALIDATION.json](VALIDATION.json).

No new native words, complete supplier, improved moment, physical runtime
bound or multiplication theorem is certified. Full selected-supplier cold
replay, native routing, hosting, tape and precision admission are not claims
of this package. The selected frontier and frozen source artifacts remain
unchanged.

## Open next questions

- **A code-balanced controller with real frame progress.** The winding
  condition rules out odd call counts but does not build an even one. A
  feasible first step is an exact bank controller whose winding is zero or
  six, followed by a typed native-frame replay and full child profile.
  The blocker is useful coordinate progress: cancellation by a true inverse
  can erase the very transformation the supplier needs to perform.
- **A priced escape through actual chart transport.** [PR #1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862)'s law
  `R_t(G_t^-1 U G_s)=V_R R_s` is conditional on the selected transport.
  Derive one actual stage transition, including its port-dependent address
  maps, and check full-source restoration as well as query transport.
  Such maps need not lie in Q[G], which is precisely why the present
  determinant obstruction does not settle that route.
- **Repair the universal three-chart defect.** The equation `RDK=12I`
  identifies an eight-dimensional unavoidable observable. First factor D
  for one chosen pair of charts and find a legal native cut for a paid
  correction. The blocker is an implementable and affordable correction,
  not the rank computation alone.

Port-dependent scalar mixing or newly admitted clean workspace changes the
first theorem's alphabet. These are explicit reopening conditions, not
operations proved impossible here. No further random seed or longer search
inside the excluded odd-call class can remove its determinant obstruction.

## Predecessors, distinction and credit

- Ali Romman's [PR1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862),
  pinned at `bb29ea73ad9be9a0c3d53cdcb1d22b2ee9ffe42f`, supplies the valid
  ordered-ring source code, native identity transfers, eight-row repair
  bound, exact fixed-chart order six, and its fixed-chart F-B-F failure
  control. This package does not claim any of those as new. Its additions
  are the all-length determinant constraint with arbitrary whole-bank
  scalar mixing, and the three-chart rank bound for all admissible P,L.
- Chafik Boukhalfa's [PR1877](https://github.com/CrocSwap/integer-mult-bounds/pull/1877)
  proves an endpoint-support tradeoff and fixed native-frame obstruction
  for the original clean-J logger. It leaves changed codes and later or paid
  native transitions open. The present contribution concerns the later
  identity-target codes and completed bank controllers, rather than
  reproving its source-support or native-frame statement.
- The retained four-pair scalar chain and native geometry come from the
  split-centres/gauge44 construction and its inherited authors. The pinned
  source lineage includes Jeremy Kothe’s [PR #1042](https://github.com/CrocSwap/integer-mult-bounds/pull/1042)
  and Rohan Arun’s [PR #1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094),
  with Chafik Boukhalfa, Hao Yan, icekylinx, NewBArch and the source-specific
  notices retaining their attribution. No historical
  construction or selected evidence is modified.

Prepared by David Arias with substantial OpenAI Codex assistance in scoping,
proof derivation, exact verification and review. Independent agent review is
not independent human review. New work is Apache-2.0.

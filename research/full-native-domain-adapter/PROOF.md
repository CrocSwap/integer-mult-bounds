# Approximate native calls inside the actual fixed-H Toeplitz program

Prepared for **@CubeJerry**, with substantial OpenAI Codex assistance.
Apache-2.0. Scoped written numerical theorem and source-bound implementation.
**No new κ.**

## 1. Exact boundary and inherited results

Jose Manuel's #4253, retained in `research/rational-fft-fixed-h`, constructs
`FullRoot.lower()` from the actual rational full Toeplitz compiler of #4205.
Its native word has fixed diagonal pages and one-bit stages
`H0 = [[1,1],[1,-1]]/2`. The last paragraph of its `DENSE-PROOF.md` explicitly
leaves additional physical native-call error unfunded. Its executable uses
exact H0 arithmetic followed by the declared data rounding. Its input radius
may exceed a physical native service's unit-disk input domain.

We retain the source's root admission, logical gates, mixed/idle matching
completion, routing orientation, six-H words, compensated coefficient pages,
stored inverse, and proved coefficient/prefix bounds. We add whole-program
rescaling, produce native requests from the actual stored stages, and fund a
possibly nonlinear approximate H0 service on its **actual stored input**.
Our concrete service executes the unchanged integer Gaussian butterfly from
JoyboyBrian's #5485 with explicit phases, normalization and local packing.

The older Schur quotient and prefix question from #1797 is not our result:
#4205 `FULL-PROOF.md` already proves its leading-section, downset and physical
cut consequences. #4755/#4976 further audit physical/partial matching cuts;
#4852/#4977 sharpen and substitute a downset estimate. We do not reprove or
claim their results. The complete #4253 proof remains an explicit dependency.
This closes one numerical caller/service boundary, not the five retained
assumptions of the selected multiplication claim.

All source paths and bytes are pinned at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a` in `SOURCES.json`.

## 2. Source constants and service contract

Consider one unchanged `NativeProgram` from `FullRoot.lower()`, in either
forward or stored-inverse direction. Let N=2^m be its complete field size,
including inactive coordinates; R>=1, target tau=2^-t and incoming grid
2^-F0 its admitted request; J, M, h its actual primitive, diagonal and H0
counts; F its original coefficient/data grid; C its compiled prefix and
inverse-prefix allowance; E0>=1 its stored logical endpoint bound; and e
its upstream operator defect against the exact root or its inverse.

The source has C=2^14 Gamma Pi, where Gamma is the dyadic upper bound for
Pi^2. Put u=2^-F. Its exact reported budget is

```
B0 = e R + 4 E0 M C^2 u R + 4 E0 C J N u,
A  = 4 C(R+1).
```

For the linear program with its stored rounded diagonal pages and unrounded
data, the source proves bounds 2C for prefixes, 2 E0 C for suffixes and
2 C^2 for every segment. Its ordinary rounded execution has norm at most A
at every completed stage and error at most B0. The segment bound already
pays the coefficient perturbation; it is not multiplied afresh per native call.

The actual Full allocation gives a quantitative positive margin:

```
e R                       <= tau R / (2(R+1)),
4 E0 M C^2 u R             <= tau R / (4(R+1)),
4 E0 C J N u               <= tau/4,
Delta := tau-B0            >= 3 tau / (4(R+1)) > 0.       (1)
```

H-free/empty cases have zero native contribution. A generic `NativeProgram`
is also admitted when its explicit margin is positive, but its width bound
then includes log(1/Delta) unless its caller proves a bound such as (1).

A request consists of `(N, bit, incoming_bits, error_bits)`. The service must
return, for every complex vector v on the incoming grid with each |v_i|<=1,
a vector satisfying

```
||service(v) - H0_bit v||_2 <= sigma := 2^-error_bits.      (2)
```

The return may use a finer dyadic grid; the host still rounds at the original
rounding site. The service may depend nonlinearly on v. The promise concerns
the actual perturbed input, and errors from different calls may be correlated.
Sigma is a **whole-field Euclidean** tolerance, not a coordinate tolerance.

## 3. Allocation and actual-input domain invariant

Take

```
s=ceil(log2(8 C(R+1))),   S=2^s,   F'=F+s.
```

Keep all diagonal coefficients on their existing F grid. Start from x/S,
execute the same stages on the F' data grid, and unscale the returned vector
by S. For h>0 choose an integer q>=0 such that

```
sigma=2^-q <= min(Delta/(4 E0 C h S), 1/(8 C^2 h)).        (3)
```

The executable computes q by an exact rational ceiling. Each H stage receives
this bound and its actual bit from the source word. For h=0 it makes no
request and never divides by h.

The source's component rounder is nearest with upward ties:
Q_F(a)=2^-F floor(2^F a+1/2). For positive dyadic S,

```
S Q_(F+s)(a/S) = Q_F(a).                                  (4)
```

Thus a zero-defect service reproduces the original rounded source trajectory
exactly after unscaling, including both signs of a tie. We do not replace this
host rule with the Gaussian kernel's different internal nearest-even rule.

Write each completed H service residual as n_j and each host rounding residual
as d_j. The actual recurrence is

```
z_j = Ahat_j z_(j-1) + n_j + d_j,
```

where n_j=0 at diagonals, ||n_j||_2<=sigma at an admitted H call, and
||d_j||_2<=2N u/S. Ahat_j are the unchanged stored-coefficient linear stages.
This identity holds even for nonlinear services and rounding: their realized
residuals are added at their actual positions. It does not compare two
nonlinear rounded trajectories by an invalid Lipschitz argument.

At every completed stage, in particular at every entrance to the next H,
the inherited linear prefix/segment bounds imply

```
||z_j||_2 <= 2 C R/S + 4 C^2 J N u/S + 2 C^2 h sigma
           <= A/S + 2 C^2 h sigma
           <= 1/2 + 1/4 = 3/4.                            (5)
```

Induct on the stages: preceding H calls were admitted by (5), so their defect
bounds can be used to establish admission of the next call. This avoids
assuming the very domain property under proof. Each coordinate belongs to
the unit disk since it is bounded by the complete vector's Euclidean norm.

The input lies on F' because F>=F0. Forgetting s in the incoming grid can
discard its finest bit before any gate; the verifier includes a 512-bit
representation witness.

## 4. Endpoint error and stored inverse

Each realized native residual propagates through a stored-coefficient suffix
of norm at most 2 E0 C. After unscaling its total contribution is at most

```
2 E0 C h S sigma <= Delta/2.                             (6)
```

The old coefficient defect, upstream root defect and host rounding stay
bounded by B0: coefficients did not change and S 2^-F'=u. Therefore

```
||returned - T_I^(+/-1) x||_2
  <= B0 + 2 E0 C h S sigma <= B0+Delta/2
   = (tau+B0)/2 < tau.                                    (7)
```

I denotes the exact ordered physical wires supplied to Full. The inverse
direction uses the actual stored reverse program with scalar reciprocals;
it is not the adjoint of a nonunitary root. No exactly reversible rounded
forward/inverse round trip follows. The required E0 suffix factor was already
established in #4253 and is retained throughout.

## 5. Concrete Gaussian realization of every requested H stage

The actual #5485 base letter and its required conversion are

```
C0 = ((1+i) I + (1-i) X)/2,
S0 = diag(1,i),   c=(1-i)/2,
H0 = c S0 C0 S0.                                         (8)
```

Direct multiplication gives S0 C0 S0=((1+i)/2)H. Both S0 operations are exact
sign/coordinate changes on Gaussian dyadics. The final multiplication by c
is exact: (a+ib)c=((a+b)+i(b-a))/2. The backend retains integer numerators
with grid exponent P+1, so this normalization adds no unpriced rounding.

The retained whole-call routine has domain 8^f. We do **not** identify this
with an arbitrary field size 2^m. Enumerate the N/2 disjoint pairs on the
requested physical bit, place successive groups of at most four pairs in
eight owned local slots, and invoke the unchanged `call(f=1,axis=0)`. It
executes four independent adjacent butterflies. Copy each real pair back
to its original addresses. No two groups share a public coordinate, so the
result is precisely the direct sum of the requested pair operations.

For N>=8 no padding is needed. N=2 uses three unused zero pair slots; N=4
uses two. These are a single constant-size local work buffer, not an extra
tensor axis or an independent productive field. Zero unused pairs remain
zero at each addition and nearest-even half. Initialization and clearing
of this buffer are charged; no public field value is erased.

Choose

```
P=max(F', q+ceil(log2 N)).                                (9)
```

Lift each F'-grid input integer to P without rounding. Each retained C0
output has complex defect at most 2^-P/sqrt(2), from #5485's four integer
nearest-even halves. The output phase preserves magnitude, and c has
magnitude 1/sqrt(2). Hence every actual H0 coordinate has defect at most
2^(-P-1), and the whole field has error

```
sqrt(N) 2^(-P-1) <= N 2^-P <= 2^-q = sigma.              (10)
```

This proves the implemented service's contract for every dyadic N>=2 and
every selected bit. Finite trajectories exercise deterministic nonzero
kernel roundings; they do not inject artificial Gaussian faults.

On unit-disk inputs, exact real pair sums/differences have magnitude at most
two and all four C0 integer numerators at most 4*2^P. Each final normalization
sum has conservative bound 6*2^P. The signed width P+4 strictly covers them,
including phase negations. The retained kernel checks its numerators before
rounding. Its P+1-grid return is then rounded by the **source host rule** on
F', at the original charged site.

## 6. Uniform widths and complete direct-backend costs

For actual Full, Pi, C and E0 are bounded by fixed polynomials in N, lambda
and Q, and the stage counts are polylogarithmic in N. Write

```
B=F0+t+log N+log lambda+log Q+log R+1.
```

The inherited theorem gives F=O(B), then s=O(B). Equation (1) gives
log(1/Delta)=O(t+log R), so (3) gives q=O(B) and (9) gives P=O(B). Thus
coefficients, data, native numerators, normalization temporaries and addresses
all fit O(B) bits. Arbitrarily fine incoming data is included through F0.

More explicitly, normalized data components fit F'+2 signed bits. Coefficients
retain the source's F+gamma_bits+5 width. Their four real products and two
sums have grid F+F' and magnitude below 16 Gamma, so
F+F'+gamma_bits+7 signed bits suffice. Unscaling restores the original F grid;
the corresponding binary-point change preserves the integer numerator word.
The proof observer's rational matrices are not online data records.

The adapter retains exactly 4MN real diagonal products, JN complex host
roundings and h H requests. It adds two complete rescaling visits, conservatively
4N real-component visits, and a one-time input-radius check with 2N exact
real squares. The latter check is counted separately. The mathematical
caller contract can supply that radius premise, but the executable's check
is not treated as free. Requests are produced one at a time and the source
coefficient pages are shared without another table copy.

For one direct native call put B_N=4 ceil(N/8), the number of executed
Gaussian butterflies including tiny-field padding. The unchanged kernel
uses 28 B_N elementary signed-integer operations before bounded loop/address
work. The wrapper additionally performs 2N input lifting shifts, N phase
negations and 2N exact normalization additions. It initializes and clears
16 real packing cells per batch, hence 32 ceil(N/8) component writes, plus
constant-many reads/writes of each public component. The temporary pack has
eight complex entries, the retained kernel's constant working registers,
and at most four address pairs. No size-N auxiliary productive bank is used.

Per-pair unit-disk norm computations are optional diagnostics, disabled in
the production backend. The universal invariant (5) supplies its domain;
the verifier's observer independently checks the domain at every entrance.
Enabling those diagnostics entails extra rational products and does not
inherit the production operation count.

With safe schoolbook scalar arithmetic, a conservative arithmetic-kernel
bit upper bound for the prepared word, including the input check, is

```
O((M+1) N B^2 + (h N + J N + N) B),
```

plus preparation and delivery of the already-required coefficient pages.
Repeated source/plan/matrix hashing and the optional exact proof observers
are verification work, outside this kernel bound. In particular, the Python
executor's repeated dense-root seal checks are not asserted to run within
the displayed kernel cost. No total Python runtime bound is claimed.
This direct backend is **not** the accelerated selected supplier and does not
improve the overall multiplication bound. Frozen Python code executes the
arithmetic semantics; no fixed-tape implementation, physical register allocator
or erasure implementation is inferred from Python heap behavior. Packing
buffer writes are explicit; physical ownership and erasure remain separate
premises.

## 7. Binding, evidence and remaining interfaces

`sources.py` authenticates the complete declared closure before executing
unchanged source modules with assertions enabled in both Python modes. The
adapter requires the original contract, root, plan, pages and new allocation
to remain sealed. Its concrete backend invokes the actual #5485 `call`, not
a symbolic replacement. The verifier uses separately written complex-pair
arithmetic/elimination for root and inverse endpoints, and direct H/2 pair
formulas for each call comparison. No predecessor verifier is imported.

Seven actual Full roots cover both directions, with complex/non-Hermitian/
indefinite matrices, a tiny scalar, a large scalar, reversed wires, 512-bit
incoming data and size-eight zero-layer shears. Three further programs cover
an empty word, an H-free singleton and mixed oriented gates. A separate
nonlinear bounded service tests the actual-input substitution; its deliberately
injected faults are labelled robustness probes, not reachable Gaussian defects.

Controls include an actual unscaled Full input outside the unit disk,
missing phase/normalization, coordinate versus whole-field tolerance, wrong
native bit, lost incoming height, changed host tie convention, internal
overflow, altered source pages and altered source bytes. Finite execution
corroborates binding; Sections 2–6 carry the universal argument.

An accelerated native service is still a separate obligation. In particular,
the physical #3627 service uses a global address/precision regime
log(global field size)=Theta(precision). A local Toeplitz tile can instead
have log N=O(log p) and precision Theta(p). It cannot inherit that service's
rate merely by invoking it independently on each tile. A global tensor,
direct-sum and coarse-label wrapper must prove the complete field, normalization,
stock, spectator, ownership and tariff contracts. Concurrent global H source
work is complementary, not an automatic substitution. Full Gaussian/core/halo
assembly, physical coefficient delivery and analytic integer recovery remain
outside this package.

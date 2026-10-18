# A ghost-state return screen for the fixed R420 supplier

**Scoped negative result, not a new construction or a general impossibility
theorem.** Allowing this word's source/helper state to remain temporarily
unrestored does not improve its paid recursive profile when its frames,
endpoint contract, copies, children and hosting stay fixed. Even gifting every
scalar cleanup operation leaves the profile unchanged. Moreover, the selected
assembly is already complex-bound, so improving the bit rate alone cannot
improve its recorded exponent on the existing 10^-18 output grid.

## Hypothesis and exact return condition

The motivating Ghost Parametrization idea is to enlarge the working state,
preserve an exact property, and separately establish return to the required
output state. Ishan's `math_prime` work suggested applying that distinction to
dirty auxiliary registers. This note defines the complete application here;
it does not import a theorem, algorithm, or text from that project.

Let z comprise the 120 source and 420 helper registers, and y the 120 targets.
After the word's D, A, scatter and B sections, exact F2 replay has the form

```text
(z, y) -> (U z, y + S z),
```

where S selects the original 120 sources. U has no target dependence. The
ghost property is correctness of the target translation; the return condition
is additionally `U=I` on arbitrary source and helper input, not merely on clean
helpers. Section C restores that condition. This is the scalar state contract;
the frame and compiled child contracts are additional requirements.

The independent bit-packed replay covers every one of the 660 input columns.
Before C, all 120 targets are correct, but all 120 source rows and 420 helper
rows differ from the identity. `rank_F2(U-I)=539`. This rank diagnoses a failed
return condition; it is **not** a lower bound of 539 gates, copies, new helper
registers, or recursive children. With the full word every required row is
correct. Both omitted C and omitted last C gate are rejected. These controls
exercise the endpoint identity directly, independently of source hash checks.

## Favorable cost before implementation

All 2,661 C gates (2,973 scalar XORs) are at the full frame. All z registers
already have that same required final frame. Thus, if C's scalar XORs are
gifted at zero cost, each frame climb previously needed by C is still needed
by the final-frame contract. It moves to the endpoint with the same source
frame, destination frame, and rank. Earlier gates and nine retained helper
copies do not change. Exact replay checks this accounting:

| Child rank | Ordinary count | Cleanup gifted |
|---:|---:|---:|
| 1 | 1,320 | 1,320 |
| 2 | 1,440 | 1,440 |
| 4 | 60 | 60 |
| 5 | 120 | 120 |
| 8 | 9 | 9 |

Both rank masses are 5,112. Every source-access gate, helper, frame change,
retained copy and recursive child outside the gifted scalar cleanup remains
charged. In particular this does not treat the unrestored word as a valid
replacement supplier.

With the selected nine-stage composition and whole-call hosting held fixed,
the inherited full profile is

```text
H = {1:380160, 2:426624, 4:32640, 5:34560,
     6:15360, 7:23040, 8:2592, 42:3456}.
m=64, W=30720, sum(r H[r])=1956096.
```

These values are pinned in `research/e8-bit-r420/EXPECTED.json`. The cleanup
gift changes only the finite scalar overhead in that composition; it leaves
the child profile and inherited bad-class contribution unchanged. Hence the
same bit moment inequality determines the same rate. This is a price-first
rejection of the fixed-interface mechanism, not an unsuccessful large search.
Changing endpoint frames, copied information, or child interfaces is outside
this class and needs a new complete invoice and compatibility proof.

More explicitly, with `E=sum(H[r])=918432`, the complete contraction moment is

```text
Phi(c) = sum_r [r H[r]/(64*30720)] (64/r)^c
         + [9567/1562500000000000] 64^c.
```

The second term is the inherited bad-class charge `32*m*E/(10^16*W)`.
The deficit is 9,984. Gifting C removes at most `288*2973=856224` scalar XORs
from the additive invoice, while leaving every term of Phi unchanged. The
pinned `assemble9.py` sends scalar additions to `unit`/`coefficient`, whereas
the moment depends only on H, m, W and E. This prices the existing complete
recursive profile; it supplies no recurrence for a new ghost compiler.

## Why the same dirty state cannot feed an unchanged next call

There is a concrete obstruction beyond the failed final return condition.
Write P for projection from z onto its original source coordinates. The exact
map above is `G(z,y)=(Uz,y+Pz)`, so two unchanged invocations yield

```text
G^2(z,y) = (U^2 z, y + Pz + PUz).
```

For the fixed word, `rank(PU-P)=120`, and the helper-to-source block of U also
has rank 120. With all sources zero and only helper register **251** set to
one, `(Uz)_0=1`. The second call therefore adds one to target 0, although its
original source was zero. This is an exact counterexample to using the same
readout on carried dirty state; it is not a counterexample to all possible
ghost interfaces. Helper dirt can induce arbitrary source drift.

The pinned nine-stage `global_k.py` requires every z row restored and the
canonical target shear in both orientations. Its retained-copy window also
requires the center to remain unchanged through erase. A new encoding E of
the ghost state would require subsequent children to read `P E^-1`, compatible
bridge and copy operations, and final reconstruction back to E=I. Those
operations and any frame changes or extra children must be priced. No such
construction is supplied here, and the already-favorable fixed-profile price
cannot improve the exponent.

## The other supplier still binds

The consumed assembly is the accepted #626 replay, not the historical kappa
in the #543 supplier's own receipt. Its exact lower endpoints are

```text
b = 65528268492323474503/40000000000000000000000
c = 413456747036699736067/250000000000000000000000
kappa = 51110230636731/31250000000000000
```

Here c is the bit rate and b the complex rate; `c>b`. The screen independently
implements the pinned seven-level arithmetic using exact fractions:

```text
eta = beta = 10^-24
s = min(c, (1-beta)b) - 10^-27
a_0 = 384599/10^10
a_(j+1) = (1-s)s + s a_j,  j=0,...,6
q = (1-2 eta)a_7
margin = (1-eta)q/(1+q)
kappa = largest multiple of 10^-18 strictly below margin.
```

Replacing c by 2c reproduces exactly the same kappa. This is an intentionally
favorable arithmetic control, not a claim that a doubled bit rate is attainable.
The complex moment's next rejected endpoint in the pinned receipt is
`b_plus=b+10^-24`. Inheriting that moment certificate and its monotonicity,
even eliminating outer losses and taking the limiting iteration gives the
favorable ceiling `b_plus/(1+b_plus)`. Its excess over the selected kappa is
exactly

```text
456684945111964070059/1956324622484976732153468750000000000000
```

which is strictly between zero and 10^-18. This excludes the next recorded
grid tick with that complex supplier fixed, within the inherited moment and
outer-assembly framework. It does not exclude every smaller
real-number improvement or a different complex supplier, and does not claim
a universal exponent ceiling.

## Reproduction and boundaries

```sh
python3 -I -B research/r420-exterior-frames/ghost_screen.py
```

Expected: `PASS_R420_GHOST_RETURN_SCREEN: debt rank 539; 2973 gifted XORs; child profile unchanged; selected kappa unchanged; 2 rejected returns`.

[GHOST-SCREEN.json](GHOST-SCREEN.json) contains the exact result, both profiles,
debt-row digest and fraction comparisons. [SOURCE.json](SOURCE.json) pins the
word and selected assembly. The implementation imports this package's exterior
geometry checker, but no producer, original scalar replay or moment engine.
The two ghost tests compare F2 rank against exhaustive image cardinality on
all 512 binary 3x3 row sets and check that target correctness does not satisfy
the restored endpoint. The geometry check has its own separate controls.

The screen does not re-prove the selected moment enclosures or compiler,
common-label, mutable-basis, hosting, precision, tape or analytic assumptions.
The finite F2 replay is exact for this word; the fixed-profile conclusion is
the cost argument above. Neither is a formal proof of the full multiplication
theorem, nor a reason to abandon other ghost-state mechanisms.

Concurrent predecessor credit: #710 already shows that shorter full-frame
scalar cleanup leaves the recursive terms unchanged; this screen extends the
favorable relaxation to all cleanup and tests the actual failed return.
#731's rank-120 helper-to-target compensation matrix is a different map from
the rank-120 helper-to-source drift certified here. #737 independently reached
the supporting exterior-frame result first. See README.md for reviewed heads.

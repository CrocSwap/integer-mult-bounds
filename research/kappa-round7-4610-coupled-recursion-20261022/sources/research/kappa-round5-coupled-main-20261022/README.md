# New coupled main interfaces

Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.

**Result:** two new actual 120-channel native responses, including a dyadic
involution, pass exact arbitrary-input native replay. The recursive consumer
remains open. This package does not claim an increase in kappa.

The ancestor is the byte-pinned `THREE-base` clean-J native word. Its paid
rank mass is 5093, all 632 persistent inputs are arbitrary, and its 408
independent helper endpoints have total rank 3301. This package changes the
main contract rather than assuming that the previous scalar identity
supplier theorem covers it.

## Actual new native constructions

Let R be the authenticated 8 by 112 query matrix. Exact integer computation
gives `R R^t = 56 I`. Put `B=R^t/2`, `C=R/2`, and `J=I-BC`.
Thus `CB=14I`; J has eight eigenvalues -13 and is not a dyadic unit.

Borrow sixteen existing cold full-ended helper fields. Eight become source
auxiliaries Z and eight become target auxiliaries W. Write the source bank
as `(X,Z)` and the target bank as `(Y,W)`. The remaining 392 helpers retain
their independent arbitrary-input endpoints. No field is cleared, owned,
or introduced.

The first construction has response

```
S = [ J  -B ]       S^-1 = [  I    B ]
    [ C   I ]              [ -C  -13I ]
```

Both matrices are dyadic and `S S^-1=S^-1 S=I`. The second construction is
the involution

```
T = [  J   -B ]       T^2=I.
    [ 12C  13I ]
```

For T, the forward extension performs `Y-=BZ` at ZERO, runs the clean-J
word, and performs `W+=12CX+13Z` at FULL. The backward extension performs
`Z-=12CY+13W` at ZERO, runs the backward clean-J word, and performs `X+=BW`
at FULL. Therefore these are exactly lower-T and upper-minus-T shears.
The S extension uses C and I in place of 12C and 13I.

S and T both have in-place dyadic adapters. For T, let `D=C_A`, where A is
the eight selected ports. D is orthogonal and consists of two signed,
permuted four-point Hadamard matrices divided by two. Apply D^t to Z,
form `V=D^t C X`, set `t=V+Z`, then update

```
X_U -= (B_U D) t
Z   += 12t
t    = -t
X_A  = t-Z-(D^t C_U)X_U.
```

Finally apply D to Z. All eight-port basis changes are explicitly emitted
as dyadic ADDs, power-of-two SCALEs, and signed swaps; no odd division or
temporary owned field is hidden. The core uses 1248 half-ADDs, sixteen
unit ADDs, eight ADDs with coefficient 12, and eight negations.

Pre-Y and post-X wrappers give `diag(T,T)` times the corresponding ordinary
identity shear in **both** orientations. For S the backward wrapper uses
S^-1. The retained native operation verifier is run in a fresh module with
the explicitly changed endpoint oracle supplied in memory; its source is
unchanged. A separate new interpreter checks the same 632 endpoint rows.

| Actual native word | Paid rank mass | Scalar allowance |
|---|---:|---:|
| Extended S, either orientation | 5093 | 124406 |
| Wrapped S, either orientation | 5093 | 142326 |
| Extended T, either orientation | 5093 | 126278 |
| Wrapped T, either orientation | 5093 | 152798 |

These scalar allowances are the inherited primitive tariff, not a new
finite-precision transfer theorem. The negative control omitting the new
13Z contribution is rejected. Every T adapter column and its double
application are checked independently.

## Caller ledger and exact boundary issue

The sixteen reclassified helpers transfer rank 144 from independent helper
credit to the coupled main contract. The new main rank is therefore
`112*16+16*9=1936`; the remaining independent helper rank is 3157. Their sum
is exactly 5093. This unconverted zero-deficit ledger supplies no Gaussian
job credit by itself.

An ordinary 120-port contract can be proposed by choosing one authenticated
odd q normal for each auxiliary. Put an inverse rank-one Gaussian before
each source auxiliary, and one after each target auxiliary, with the
conjugated orientation in the backward word. These connect q to ZERO and
FULL to FULL-minus-q. The exact line/reference equations and all 120-port
entry/exit owner phases pass 160 and 1200 checks respectively. This is an
explicit conversion interface, whose complete native word and rounded
recursive admission have not been integrated.

The conversion costs sixteen paid H1 calls and loses sixteen target rank
units: the local deficit is **32**, rather than 16. Its ordinary main mass
is 1920 and paid-minus-independent-helper mass is 1952. Replaying the
retained p1/p2 controller role DAG over free noncommuting stage symbols
gives these conditional first-moment ledgers:

| Controller | Target surplus before boundary closure | Direct individual Q heads | Surplus after those heads |
|---|---:|---:|---:|
| p1 | 144 | 240 H1 | -96 |
| p2, either retained-idle choice | 320 | 480 H1 | -160 |

These are optimistic caller ledgers. In particular, an NC IDLE symbol
requires the coupled stage product, whose admission as a Gaussian-only
idle job has not been proved.

Actual owner routes do not reduce to one stage-independent chart.
Individually `T_s^2=I`, but `T_2 T_1 T_0` is neither I nor T_0 nor T_2,
and successive T_s do not commute. Explicit basis-column witnesses are
stored in `CALLER-PROBES.json.gz`. This excludes a plain two-color parity
identification of the transported matrices; it is not a general
impossibility theorem about typed coupled jobs.

There is a useful positive terminal-contact fact: every T_s in an interval
is free at that interval's positive **and negative** Gaussian target
frame. All 2640 tested exact owner/phase contacts pass. The problematic
negative-bank correction is instead `Q^-1 M Q`, where M is the coupled
chronological product. Its inner T_s operations occur at target-minus-q.
At that intermediate hole frame, ports 0 and 1 have different quadratic
coefficients on axes (0,3); translation cannot repair the mismatch. This
same explicit mismatch is checked for all p1/p2 tested intervals and
their stages. The package does not treat the Gaussian target alignment
as a proof that the conjugated correction is free.

A better terminal compiler could still exploit the rank-eight structure
`T-I=[-B;12I][C,I]`, where `[C,I][-B;12I]=-2I`. It would need an exact arbitrary-input normalizer and the full
recursive paid/helper/target invoice. Neither the direct-head construction
nor this finite set of negative controls proves a lower bound on that
possibility.

## Lean scope and reproduction

`InvolutiveLift.lean` proves the involution on arbitrary additive groups
assuming `CB=14I`. `LiftGram.lean`, generated from the pinned R
data, checks `RR^t=56I` and the literal dimensions. No native-word or
recursive Gaussian-job theorem is asserted by those Lean statements.
`LEAN-LIFT.json` records the successful fresh Gram and generic kernel
checks. `LEAN-VERIFICATION.json` separately records the successful scoped
generic proof, including object and log hashes. Both checks passed.

From the repository root, using the global Python 3.14 interpreter:

```powershell
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round5-coupled-main-20261022/lift_native.py
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round5-coupled-main-20261022/involutive_lift.py
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round5-coupled-main-20261022/caller_probe.py
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round5-coupled-main-20261022/verify_lift_lean.py
```

The installed `py -3.14` launcher does not resolve this interpreter on the
current machine, so these commands name the global interpreter directly.

The local Lean replay uses the ignored pinned Lean 4.21.0/mathlib toolchain
from `research/kappa-lean-verification-20261022`; external users can adapt
that executable location to the same toolchain. The exact packet used by
the new checks is source-identical to the legacy packet at the SHA already
recorded by the old verifier. Its legacy relative path is absent in this
sparse checkout; no old source or receipt is restored or changed.

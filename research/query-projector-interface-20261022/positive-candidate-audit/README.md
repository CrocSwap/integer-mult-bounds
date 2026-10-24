# Independent audit of the changed-G candidate

TL;DR: the frozen candidate passes a separately written literal free-group replay
and profile audit. Its local paid profile changes from
`{1:2237,2:388,3:494,4:147,5:36,8:8}` to
`{1:2201,2:412,3:506,4:135,5:36,8:8}`. The unchanged p16 controller then supports
the reported `kappa = 0.00302152` under the retained physical compiler contracts.
The audit does not replace the separate absolute-phase admission verifier.

## Reproduction and frozen input

Run from the repository root with global Python 3.14:

```powershell
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' -B research/query-projector-interface-20261022/positive-candidate-audit/audit.py
```

The script writes only `audit-result.json` in this directory. It reads the actual
frozen native payload, whose decompressed SHA256 is
`4409d2d9328fffbd276bb03fb800f59a33ec3b2ab15f79a330a7af66e75110cc`.
The compressed payload hash is
`d578875344095047c383ef513e69b9deb9d99d2b75abe14f7359d06365a924ac`.
The receipt pins its own source, the actual payload and freeze file, baseline
constructor, controller, both rational-power engines, and pricing inputs. The
final parent verifier reruns this audit after refreshing its physical and
arithmetic receipts, and binds their hashes together.

## What the independent evaluator checks

The evaluator in `audit.py` does not import the producer's row evaluator. It
tracks rational coefficients in the group algebra of independently numbered
invertible warp symbols. Both directions are replayed with all 632 persistent
data/helper input columns independent. The owned C field starts arbitrary, is
explicitly cleared, and is zero on exit. The forward shear and backward inverse
transpose endpoints are exact, and all 408 persistent helpers are restored.

It also checks every binary transported-frame incidence, all 72 G maps are
invertible, all paid ranks, and unchanged helper profile
`{4:28,7:7,8:47,9:326}`. Original frames remain an unchanged prefix; only new
frames are appended. External ports and boundary frames remain fixed. Obsolete
construction-only A/B/cleanup/edge metadata is absent from the actual payload.

Every logical scalar opcode, coefficient and order, each warp symbol and role,
and every phase/center/adapter marker equals the retained word. There are 422
retimed scalar contacts per direction. Of the 60 maps allowed to change by the
search, **34 G maps actually change**. Forward and backward have identical paid
edge and signed warp-class coverage. The exact per-direction counts are 240
warps, 448 main endpoint adapters, 3290 paid climbs and 8 paid centers. The scalar
allowances recomputed from the rational opcodes are 158120 forward and 158168
backward.

## Why arbitrary new G values preserve the formal identity

The replay proves the endpoint identity in the free group algebra, with no
relations between distinct warp symbols. Each symbol can therefore be replaced
by any consistently used invertible physical operator, and its negative symbol
by the actual inverse. The backward replay has its own conjugated alphabet,
matching the retained inverse-transpose convention. This substitution argument
supplies the additional freedom to change G; the old frame-transport statement
alone had held G fixed.

For a physical G the retained symplectic action is
`S_G(x,z)=(Gx,Gx+G^{-T}(x+z))`, taking the relevant L_U frame to L_GU. The required
native K_G includes its quadratic phase. A plain permutation G, an inverse
binary map with an incorrect scalar phase, or a projective-only Clifford check
would not suffice. This audit checks binary incidence and phase-class coverage;
the separate `warp-interface-20261022/verify_candidate.py` receipt checks new K_G
and paid Gaussian absolute phases and monomial lowerings. Formal replay cannot
infer those phases. The final package must retain both checks.

## Moment improvement and finite compiler arithmetic

The exact local difference is
`old P - new P = 12*(3 H_1 - 2 H_2 - H_3 + H_4)`. It has zero rank mass and
removes 12 recursive calls per full native call, hence 216 over the 18 full
controller calls. Let `g(t)=3+4^t-2*2^t-3^t`. Then `g(1)=0` and

```
g'(t)/3^t = 2 log(2) * ((4/3)^t - (2/3)^t) - log(3).
```

The bracket is increasing on `[0,1]`, and the expression at 1 is
`(4/3)log(2)-log(3)<0` because `16<27`. Thus `g(t)>0` for every `0<t<1`.
This is a uniform improvement of the paid profile, with the target profile and
all idle/query bills retained.

The audit independently rebuilds full T/P directly from the stored p16
controller. Both retained exact rational-power engines agree on positive moment
margin at `0.0030215551`, negative margin at `0.0030215552`, positive margin at
the prior raw upper endpoint `0.0030201659771`, and positive margin at the
strictification test `0.00302153`. It rechecks the completion, tail and integer
compiler inequalities used for `kappa=0.00302152`, including the stated finite
integer witness and its preceding failing integer. This witness is specified by
integers; its enormous circuit has not been materialized.

## Cost and claim boundaries

The 688 routing categories are exactly 240 warp occurrences plus 448 endpoint
adapters. Together with two helper boundaries and the new paid-call count, the
retained 1000-per-category contract gives a local route allowance of 4802000.
Adding the independently counted 158168 scalar allowance remains below the
retained local budget of 10^7. The rebuilt whole controller scalar upper bound
is 181098496, below 10^9. General invertible nine-axis G stays within the same
fixed-size monomial compiler family and Z4 phase coefficient class; the count
does not acquire a new asymptotic category.

These are inherited compiler allowances and exact finite algebra/arithmetic
checks. This audit does not measure fixed-tape movement, replace the existing
movement/precision/BIT proofs, or claim a newly formalized end-to-end theorem.
Any claim in the parent result retains those existing compiler contracts and
the separate physical admission receipt.

All other projector, typed-H, clean-output and Q-head investigations in the
parent directory are frozen negative or limited-scope results. They supply no
extra gain and are not stacked into this candidate.

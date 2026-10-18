# Independent audit of the QQ16 selected-only intervention obstruction

**Independent verification; no new kappa or supplier.** This package corroborates
[PR2306](https://github.com/CrocSwap/integer-mult-bounds/pull/2306) at
`4d6e08099c11ff06a8585d04ed59453dd5a62d7d`. Its added evidence is a reduced
8-by-8 integer transfer certificate and an explicit association of **14,784
emitted alignment references** with their actual stage and port. It imports no
predecessor executable and does not repeat the author's Walsh-polynomial paired
execution implementation. The quantified nonlinear statement rests on the
induction below, not on finitely many nonlinear examples.

The original common-kernel witness is Adam Gall's PR2093 contribution. The
extension to arbitrary deterministic selected-only interventions is PR2306's
contribution. This package independently checks those claims and adds semantic
source-binding coverage; it claims neither result as a new discovery.

## Exact scope and result

Keep Ali Romman's conserved QQ16 F/B maps, the A/T/U partition and the retained
19-event ordinary recipe. Controls begin only **after complete F0**. They may
read/write selected fields, available forward histories and identically
initialized auxiliary state, and may be nonlinear, affine, adaptive or
cross-owner. They cannot read or write ordinary fields, inspect an unfinished
local call, or access distinguishing pre-F0 information. The terminal decoder
gets final selected fields, final completed-X descendants, all five forward
histories and the controller transcript. This is precisely the restricted
observation contract being audited.

Let `r_p` be column p of R and let `chi_v(d)=(-1)^bit_0(d v)` on cover owners.
The fields are constant in payload coordinates, not in owner d. The actual
source has

```
r_2 = r_8 + r_85,
b_(2,0)=37, b_(8,0)=38, b_(85,0)=506.
```

Set `h_2=-chi_37`, `h_8=chi_38`, `h_85=chi_506`, and other ordinary fields zero.
For every positive stage s the port routes send those three axes to the same
stage axis, so `B_s h=0` for s=1,...,8. This is an exact all-owner cancellation:
right routing sends `chi_v` to `chi_(rho_s(p)v)`. It does not require independence
of all character functions on the owner group. At identity owner,

```
B0 h = (2,2,0,0,0,0,2,-2),
-P_(0,A) B0 h = (-1,0,-1,-1,0,1,0,0).
```

Choose the initial pair-0 difference
`X_U=h, Y_U=0, X_A=-P_(0,A)B0h, Y_A=-X_A, X_T=Y_T=0`, with other pairs equal.
The exact A-minor inverse `R_A^T/4` cancels the F0 query. Complete F0 leaves
`X_U=Y_U=h` and zero selected/history difference. The required original
individual A input is nevertheless different. Only restoring selected sums
would be a different problem.

## A small invariant module instead of a large payload replay

Whenever selected differences vanish and a pair has ordinary difference
`(alpha*h,beta*h)`, equations (1) and (3) of the pinned
[conserved contract](../joint-query/evidence/CONSERVED-QQ16.md) imply, at positive
stages,

```
F_s: (alpha,beta) -> (alpha,beta+alpha),
B_s,t: (alpha,beta) -> (alpha-beta,beta).
```

Indeed all current/future query differences vanish, so the selected outputs
also agree. The ordinary bridge is
`alpha_dst += c*alpha_src; beta_src -= c*beta_dst`, and terminal is
`(alpha,beta)->(beta,-alpha)`. These formulas close on an eight-dimensional
space: two ordinary coefficients in each of four banks. They apply to the
difference of arbitrary common backgrounds because the retained local maps are
linear.

Multiplying the actual 18 events after F0 gives, in interleaved bank order,

```
(x0,y0,x1,y1,x2,y2,x3,y3)
  -> (x0,y0-x0,x1,y1,x2,y2,x3,y3).
```

The independently computed matrix and all 19 witness boundary vectors are in
[RESULT.json](RESULT.json). For post-F0 vector `(1,1,0,0,0,0,0,0)`, the final
vector is `(1,0,0,0,0,0,0,0)`. The four preterminal X projections are zero.
After the signed terminal, the nonzero field is the **former-Y** endpoint
`X_(0,U)`, excluded from completed-X observations. The five forward histories
and every selected difference vanish.

At each allowed boundary both executions therefore give a controller the same
selected state, histories and auxiliary state. A deterministic control step
returns equal state/transcript and leaves the ordinary difference unchanged.
Induction alternates these equality-preserving control steps with the fixed
linear event updates above. Adaptation and common random coins do not break
that equality. Consequently no decoder of the permitted observations can
recover both distinct original A inputs. This is a written indistinguishability
proof, not a randomized-algorithm lower bound or a proof-assistant theorem.

**A consequential boundary:** ordinary X immediately after F0 differs by h,
even though it temporarily has a completed-X native frame. Such an intermediate
ordinary read is excluded. The allowed completed-X descendants are the final
named Y fields, not every historical completed-X field. Reading B0h or final
former-Y X0U distinguishes this witness; neither read alone is proved sufficient
for full recovery.

## Added stage/port source-binding audit

PR2306 reconstructs route matrices and checks membership in an unordered map
registry. Its immutable source hashes already reject changed packet bytes;
this is **not a demonstrated wrong route or a hash-validation vulnerability**.
Membership alone, however, does not establish that a particular program event
uses the matrix for that event's stage and port.

`route_binding.py` separately constructs each orthogonal frame swap by exchanging
its projections and checks actual `cover_map` references in the entry and exit
alignment blocks. Coverage is all 37 local cases: 9 forward and 28 backward,
1,008 stage/port matrices, 14,784 references in total, with 2,752 in the nine
cases used by the retained schedule. It also binds case parameters, sweep order
and core stage/orientation. F0's identity alignment is checked separately.

Two mutations preserve the registry itself: swapping the F2 port-2/port-8 map
references, and substituting F4's port-2 reference at F2 port 2. Both fail the
new semantic predicate. An identical matrix under a different registry ID
passes, so the predicate is not just a label comparison. Four further controls
reject a wrong witness sign, wrong F2 pair, missing negative bridge and wrong
terminal sign. The last is checked on the full eight-variable matrix, because
the particular witness alone has zero preterminal X and cannot detect that sign.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/qq16-intervention-independent-audit
```

This runs both normal and optimized checks. Direct replay:

```sh
python3 -I -O -B research/qq16-intervention-independent-audit/verify.py
```

Expected: `PASS_QQ16_INDEPENDENT_INTERVENTION_AUDIT`.
Default verification is read-only and compares the entire stored receipt.
Explicit `--write-result NEW_PATH` refuses to overwrite an existing file.

Base main is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
[SOURCES.json](SOURCES.json) pins live inputs and historical provenance.
The upstream instruction/selected-state refresh and overlap limits are recorded
in [TASK.json](TASK.json). The local task picker was explicitly overridden to the
central QQ16 handoff after live overlap showed its construction follow-ups were
already claimed. This independent audit is a declared change from construction
synthesis, not satisfaction of the catalogue's supplier acceptance gate.

## Limitations

The logical maps, native frame interpretation and bridge convention remain
inherited from the pinned source. This does not rederive R from core scalar
operations, replay private-copy relative maps, native phases, scalar sweep
bodies or recursive child kernels. Payload translations fix the witness fields;
their physical implementation is not reverified. There is no full supplier cold
replay, hosting, precision, all-size or multiplication-theorem claim, and no
selected-frontier change.

## Open next questions

1. Can a legal ordinary read or input-dependent retention before F0 avoid the
   complete kernel? This matters because selected-only controls cannot. Start
   with the active coordinate-tap investigation in Discussion 2205, and test the
   full restoration contract before pricing. Native access, full injectivity
   and the completed bill remain blockers; this audit does not reserve that task.
2. Could the predecessor checker bind each emitted alignment reference directly?
   The two registry-preserving mutation fixtures here are a first regression
   target. This would clarify which source associations it independently checks;
   maintainers decide whether to reuse this separate checker or adapt its method.

## Attribution

Adam Gall (PR2093) supplied the three-port witness; Ali Romman (PR1969) supplied
the QQ16 maps, routes and retained schedule; Cinna Davis (PR2216) supplied the
older-witness shear; PR2306 by @CubeJerry supplies the deterministic intervention
obstruction audited here. @commdata2338's PR2174 is adjacent recovery work with
additional observations. The retained supplier/compiler lineage remains credited
in the unchanged source notices.

Prepared by @EdDiboi with substantial OpenAI Codex assistance in implementation,
mathematical review, verification and writing, including a separate agent review.
This is independent agent verification, not independent human review or maintainer
acceptance. New work is Apache-2.0.

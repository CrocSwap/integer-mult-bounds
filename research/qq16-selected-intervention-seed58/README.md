# QQ16: selected-only interventions cannot repair the complete restoration kernel

**Scoped negative result; No new κ.** A proposed cheap repair changes the
selected A/T registers between QQ16's first forward and backward calls.
[Cinna Davis's PR2216](https://github.com/CrocSwap/integer-mult-bounds/pull/2216)
shows that its shear exposes the earlier eight-direction witness. That local
result does not imply recovery of every input. Applying the different
three-port witness credited to
[Adam Gall's PR2093](https://github.com/CrocSwap/integer-mult-bounds/pull/2093)
shows that the shear still loses an original A input through the complete
retained ordinary schedule.

The added result is a **two-execution invariance proof**: the failure persists
for arbitrary deterministic selected-only interventions beginning **after the
complete F0**, at boundaries between the retained events. They may be affine,
nonlinear, adaptive, cross-bank or cross-owner, and may use auxiliary state
that starts identically in the two executions. Neither linearity nor a zero
auxiliary value is required. This enlarges the earlier homogeneous,
post-B1 controller exclusion to a precisely stated class of first-pair
changes. It does not exclude ordinary reads, changing a local F/B map, or
retaining input-dependent information before F0.

## Exact contract

Keep the conserved local F/B maps of Ali Romman's
[PR1969 package](../joint-query/evidence/CONSERVED-QQ16.md), the actual
`A,T,U96` partition, and the ordinary part of the selected 19-event recipe.
It has nine local calls on pairs `0,0,0,1,1,2,2,3,3`, nine bridges, and the
signed terminal `(X,Y) -> (Y,-X)`. F2 acts on pair 0 and F8 on pair 3.

An intervention may read and change all selected A/T fields and its own
auxiliary state. It may read all forward-query histories already available.
It must leave ordinary U fields unchanged and cannot read them, including
ordinary fields temporarily in a completed-X native frame. It cannot inspect
an unfinished local call, its temporary values, or other unrecorded input
information. It may run after F0 and at subsequent complete-event boundaries,
including after the terminal; there is no intervention before F0.
Adaptive choices and termination must depend only on these permitted values.
Any random bits, if used, are coupled identically in the two runs.

The decoder receives all final selected fields, all completed-X descendants,
all five F histories, and the controller's auxiliary transcript. Even granting
the entire **initial** ordinary-query list `B_s X_(0,U)`, `1 <= s <= 8`,
does not help this witness. An auxiliary value or transcript preloaded with a
distinguishing original input is outside the contract.

The required output includes pair 0's original individual A/T inputs, as in
the preceding QQ16 restoration question. Restoring only their sums is a
different contract. The named final `X_0,U` is the former-Y hole, which is
excluded from the completed-X observations. The named final Y fields are
the completed-X descendants under the retained logical convention.

## A credited common-kernel witness

Write `r_p` for column p of the actual 8-by-112 matrix R and `b_(p,0)` for
the first local chart axis. The authenticated source gives

```text
r_2 = r_8 + r_85,
b_(2,0) = 37, b_(8,0) = 38, b_(85,0) = 506,
rho_s(p) b_(p,0) = e_(9+8(s-1)),  1 <= s <= 8.
```

For an owner d in the retained cover group define the rational-valued
character `chi_v(d)=(-1)^bit_0(d v)`. Fields are constant in every tensor
payload coordinate; this does **not** make them constant in owner d. Define

```text
h_2 = -chi_37, h_8 = chi_38, h_85 = chi_506,
h_p = 0 at every other ordinary port.
```

Right routing sends `chi_v(d)` to `chi_(rho_s(p)v)(d)`. Thus every nonzero
chart query factors as

```text
B_s h = (-r_2+r_8+r_85) chi_(e_(9+8(s-1))) = 0.
```

At identity owner I the three characters are `(-1,1,1)`, so
`B0 h(I)=2 r_2=(2,2,0,0,0,0,2,-2)`, which is nonzero. This is an
all-owner identity from the actual routing law, not an inference from sampled
owners. Payload translations fix these fields. Logical/native interpretation
inherits the source package's phase and frame convention.

PR2093 used the integer-bit functions `f_v=(1-chi_v)/2` with the same signed
three ports. The present h equals minus twice that witness plus the constant
column-dependence vector. That constant vector lies in every B_s kernel.
The different representation makes exact polynomial intervention tests easy;
the witness and its discovery are **not new contributions**.

Let Δ denote the difference of two initial states. All other pairs are
identical, and pair 0 differs by

```text
ΔX_U = h,                  ΔY_U = 0,
ΔX_A = -P_(0,A) B0 h,      ΔY_A = -ΔX_A,
ΔX_T = ΔY_T = 0.
```

At owner I the required original X_A difference, in A-port order, is
`(-1,0,-1,-1,0,1,0,0)`. The initial selected sums agree, but the individual
inputs that must be restored do not.

## Proof through the changed boundary and retained tail

**F0.** The forward query difference is
`Δf0 = B0 h + ell_(0,A)(-P_(0,A) B0 h) = 0`.
Equation (3) of the conserved QQ16 contract therefore gives

```text
after F0: ΔX_U = ΔY_U = h; every selected difference is zero.
```

This holds on top of **any** common background because F0 is linear.
In particular the two selected states are equal, although they need not be
zero. Every permitted intervention, including PR2216's
`X_T += X_A; Y_T -= X_A`, receives the same values and auxiliary state
in the two runs. It produces equal selected values and auxiliary state.
The ordinary difference is unchanged. This is the step that also covers
nonlinear or affine interventions; merely asserting that zero stays zero
would not suffice.

**B_1_2.** Its future encoding has
`Δu_A=P_(2,A) B2 h=0`, `Δu_U=h`, and `Δu_T=0`.
Its driver and current query differences are `Δa=0` and `Δb=B1 h=0`.
The full B map consequently gives

```text
after B1: ΔY_(0,U)=h; every other data difference is zero.
```

The intervening selected operation can have made both runs nonzero. Since
B1 is linear, their difference is still exactly this expression.

**Tail.** The first positive ordinary bridge puts `-h` in `ΔY_(1,U)`.
F2 has zero X-input difference, so its query difference is zero and it
does not change the ordinary difference. The negative bridge cancels `-h`
before B3. Every later local call has zero active-pair difference. The final
three bridges leave `h` only in `ΔY_(0,U)`, and the signed terminal moves
it to the named final `ΔX_(0,U)`.

At every complete-event boundary the selected difference remains zero.
Inductively, any intervening permitted controller step sees equal state and
history, produces equal updates, and leaves the ordinary difference above
unchanged. This induction covers arbitrarily many such steps and adaptive
choices, provided the controller terminates and does not change the retained
ordinary event sequence. All five F-query differences vanish. All completed-X
descendant differences vanish. The allowed initial nonzero-chart reads also
agree by `B_s h=0`.

Thus the complete allowed observation/transcript is identical in the two
runs, while the required original A input differs. **No decoder of those
observations, linear or otherwise, can restore both inputs.** This is a
scoped impossibility argument, not a failed finite search or a general
lower bound for multiplication.

## Favorable cost screen and stopping rule

Grant the proposed interventions, source-independent auxiliary state,
all helpers, copies, frame changes, routing, restoration, recursive children,
hosting and precision **zero additional cost**. The information contract
still fails. There is therefore no correct restoration recurrence to price
in this class, even in this maximally favorable relaxation. Adding a cost
to an unchanged failed observation cannot repair it. Synthesis stops here.

For context only, the retained first F0/B1 pair has native mass 11076 and
real scalar bound 426196. The specific PR2216 shear consists of 16 additional
scalar ADDs per owner. Its same-frame physical admission and reported local
rank-eight effect are predecessor claims, not rerun here. These are local
counts, not a complete supplier invoice. The selected conditional
`κ=0.001672660197076918` and all selected artifacts are unchanged.

## Evidence and reproduction

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/qq16-selected-intervention-seed58
```

The registered replay runs normal and optimized exact verification and the
focused tests. The direct command is

```sh
python3 -I -O -B research/qq16-selected-intervention-seed58/verify.py
```

Expected direct output:

```text
PASS_QQ16_SELECTED_INTERVENTION_OBSTRUCTION
3-port witness; 1008 routes; 19 events; 4 two-run fixtures; 9 rejecting controls; no new kappa
```

The checker authenticates the actual QQ16 packet and archive members,
checks the A/T inverse and ordinary Gram identities, reconstructs and binds
1008 routes to the packet registry, and executes the factored E/exchange/H
backward map. It compares all 17 post-B1 states with the retained witness
receipt and binds the actual call pairs to the complete hosted template.

Four two-run fixtures cover the literal PR2216 shear on zero and nonzero
backgrounds, affine controls using a common nonzero dirty value, and nonlinear
square shears. Each checks 128 selected fields at all 19 boundaries and all
five forward histories. The written induction establishes the universal
claim; these fixtures are exact regressions, not a proof by enumeration.

Nine controls reject a changed dependency sign, changed chart axis, missing
initial cancellation, missing negative bridge, incorrect F2 source binding,
ordinary-reading intervention, mislabelled former-Y endpoint, detecting B0
query, and changed source bytes. The old zero-difference trajectory alone
does not detect a wrong F2 pair; that control deliberately checks the complete
source binding. A B0 read or an ordinary read detects this particular witness
but is not thereby proved sufficient for full recovery.

Default verification is read-only and compares the complete RESULT.json.
`--write` explicitly regenerates it. No native child kernel, full supplier
cold replay, precision bound or proof assistant is run. The actual all-size,
physical, hosting and analytic interfaces remain inherited. This does not
claim independent human review or a hosted CI result.

## Provenance, overlap and credit

Base main: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
OS assignment seed **58** chose recursive interfaces; the repository chooser
nonce is `a66f3520f3c837b194ddee45f8ef43dd`. TASK.json records the three
candidates, local claim, stopping rule, exact pending heads and live-check
limitations. No full GitHub API snapshot or posting access is assumed.
Relevant public PR/discussion pages and Git refs were checked; incomplete
pagination cannot establish absence of overlap.

SOURCES.json binds all consumed repository files by Git blob and SHA256.
The QQ16 packet SHA256 is
`a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7`;
the retained archive SHA256 is
`22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754`.
RESULT.json pins the two archive members. Pending executables are neither
imported nor vendored; their mathematical contributions remain credited:

- **Ali Romman, PR1969**: conserved QQ16 maps, native packet, ordinary
  schedule and selected-observation witness.
- **Adam Gall, PR2093**, head
  `8b21a900eb520e4f11ea177b310f66316f8e8983`: the three-port common-kernel
  witness and nonzero-chart query obstruction. The present work adds its
  implication for changed pre-B1 selected-only control and arbitrary
  equal-state interventions; it does not rediscover that witness.
- **Cinna Davis, PR2216**, head
  `b80e9ba43367fb8b20877a97da1cb677c34f9264`: the specific cheap shear and
  its valid, separately scoped old-witness separation claim. The present
  result answers the full-restoration follow-up, without contradicting it.
- **Adam Gall, PR2086**: the adjacent changed-A-logger obstruction, which
  fixes the T record. The present class allows changing T after F0.
- **@commdata2338, PR2174**: complete two-query recovery under an explicitly
  recorded B1-cut contract and the warning about actual F2/F8 pair binding.
  That interface adds observations and is not excluded here.
- The Rohan Arun, Jeremy Kothe, Hao Yan, Zhihao Chen, DreamingOfClouds and
  retained compiler/supplier lineage is credited in the unchanged
  [source notices](../joint-query/NOTICE.md).

Prepared for **@CubeJerry** with substantial **OpenAI Codex** assistance in
the derivation, implementation, checking and writing. Apache-2.0. The new
proof and checker are author-checked; no independent agent or human review
is claimed.

## Open next questions

1. Can an intervention access a distinguishing old-chart ordinary query
   at a legal frame with a favorable complete bill? First identify its
   exact cut, read and output contract, then test the complete restoration
   kernel before pricing it. Native access, retention and cleanup are open.
2. Can a changed F0 retain an input-dependent record *before* its selected
   outputs become indistinguishable? First derive the whole ordered local
   map and test the credited common kernel. Such a changed source contract
   is outside this result; arbitrary selected-only changes after F0 are not
   a new search class.

Structured questions and their blockers are also in TASK.json.

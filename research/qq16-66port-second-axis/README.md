# The specified QQ16 66-port read set still loses selected inputs

**Scoped obstruction with an exact four-port witness; no new kappa.**
[PR2354](https://github.com/CrocSwap/integer-mult-bounds/pull/2354) proves that
one specified set of 66 ordinary port reads eliminates its common-first-axis
hidden-input family. Its second open question asks whether that same set
fails on other inputs. **It does:** the second local chart axis gives a
counterexample supported on unread ports **44, 49, 58 and 70**.

The complete fixed QQ16 schedule has zero selected observations, zero
completed-X descendants, zero five forward-query histories, and zero
transcripts from all 66 specified ports, but a nonzero original A input.
The A-to-T selected shear also leaves this witness unchanged.

This answers that exact follow-up. It does not contradict PR2354's explicitly
family-only sufficiency statement, establish a minimum tap count, or rule out
every other set of 66 ports. A dense initial old-chart read detects this
witness. Parallel PR2368 studies that dense read with a different hidden-input
family; it is separate from the fixed-coordinate set tested here.

## Contract

Use the actual QQ16 A/T/U partition, fixed first `F0/B_1_2` pair, nine local
stages, and ordinary 19-event recipe. All definitions and local maps are from
the retained [conserved QQ16 contract](../joint-query/evidence/CONSERVED-QQ16.md),
[ordered proof](../joint-query/evidence/JOINT-QUERY-TRANSFER.md), and
[cover action](../joint-query/evidence/QQ16-COVER-ACTION-ADDENDUM.md).

Let J be the following 30 unread ports, and S=U minus J the 66 read ports:

```text
J = [44,45,48,49,50,51,52,53,54,55,56,58,59,60,61,62,
     63,64,65,66,67,68,69,70,71,72,73,74,75,77].
```

This is precisely PR2354's attaining set: J is the set of ordinary ports
whose first local chart axis is the binary vector 2. The verifier reconstructs
that set from the frozen source, rather than assuming a similarly sized set.

After complete F0, allow any homogeneous linear selected-field controls,
including the paired A-to-T shear, arbitrary owner mixing, and arbitrarily
many side-effect-free reads of the entire X/Y owner arrays at ports in S.
These reads may be retained for free. Granting earlier ordinary reads from S
does not help either. Keep ordinary fields and the ordinary schedule unchanged.
There is no earlier retained selected-input record, read of an unread port,
ordinary preprocessing, or additional observation of the final former-Y
endpoint. Private input-dependent records outside this contract are excluded.

The inherited observation contract starts after B1 for completed-X
descendants. The nonzero ordinary X output immediately after F0 is **not**
granted as an additional full ordinary observation. Only its ports in S are
readable. This distinction is necessary.

## A four-column source identity

Write r_p for column p of the actual rational 8-by-112 matrix R and b_p for
the **second** local chart axis (array index 1, not index 0). The source gives:

| p | coefficient c_p | b_p | r_p, in query-coordinate order |
|---|---:|---:|---|
| 44 | -1 | 25 | (0,0,1,-1,0,0,-1,1) |
| 49 | -1 | 145 | (1,0,0,1,0,1,1,0) |
| 58 | -1 | 4 | (0,1,-1,0,1,0,0,-1) |
| 70 | +1 | 4 | (1,1,0,0,1,1,0,0) |

Thus `-r_44-r_49-r_58+r_70=0`. All other coefficients are zero.
The actual registered routes satisfy, for every port and s=1,...,8,

```text
rho_s(p) b_p = e_(10+8(s-1)).
```

Coordinates here start at zero. The verifier binds all 1,008 port/stage
matrices to the native registry and checks all 7,168 positive-stage local-axis
identities, including the 32 used by this witness.

## An identity for every cover owner

For an owner d in the retained regular cover G define

```text
f_v(d) = bit_0(d v), as the rational number 0 or 1;
h_p(d) = c_p f_(b_p)(d), constant in every payload coordinate.
```

The full cover map reads at owner `d rho_s(p)`; payload translations act
trivially on these payload-constant fields. Consequently, with
`B_s=R_s iota_U`, the checked route identities give for **every** d:

```text
B_s h(d) = sum_p r_p c_p bit_0(d rho_s(p) b_p)
         = (sum_p r_p c_p) bit_0(d e_(10+8(s-1)))
         = 0,                       s=1,...,8.
```

This is an identity, not an inference from sampled owners. It requires no
independence assertion about the functions f_v. In the old chart,

```text
H(d) = B0 h(d) = -r_44 f_25(d) - r_49 f_145(d)
                         + (r_70-r_58) f_4(d).
H(I) = (-1,0,-1,0,0,-1,0,-1) != 0.
```

Identity belongs to G, so this evaluation suffices to prove H is nonzero.
Using the first axis instead would give `H=f_2 sum_p r_p c_p=0`: that
old family has no selected defect on this coefficient vector. This is the
changed premise, not a repetition of its 66-port family threshold.

## The ordered hidden-input trajectory

Initialize only pair 0, with all other pair fields and helpers zero:

```text
X_U=h,            Y_U=0,
X_A=-P_(0,A) H,   Y_A=+P_(0,A) H,
X_T=0,           Y_T=0.
```

`P_(0,A)=iota_A R_A^T/4` is a section, since `R_A R_A^T=4I`.
The original selected A input is therefore nonzero. Its identity-owner
value, in A order `[0,7,20,27,36,46,57,111]`, is

```text
(1/2,0,-1/2,0,1/2,0,1/2,0).
```

Every coefficient in the initialized input is integral or half-integral;
multiplying the entire witness by two gives an integral witness.
All selected pair sums vanish. The full F0 query is
`B0 h + ell_(0,A) X_A = H-H=0`, so the exact forward map gives

```text
after F0:  X_U=Y_U=h,  all selected fields zero.
```

Every read at S is zero, since h is supported in J. Any allowed selected
controller therefore keeps selected fields zero. In particular the shear
`X_T += C X_A; Y_T -= C X_A` does nothing, for any homogeneous linear C.

At B1 the future logger query is `B2 h=0`, the old T driver is zero, and
the current query is `B1 h=0`. The exact backward map gives

```text
after B1:  Y_(0,U)=h,  every other ordinary and selected field zero.
```

The first positive bridge puts `-h` in Y_(1,U). F2 has zero X input and
changes nothing. The cancelling negative bridge removes that `-h`.
All remaining active local pairs are zero; the last three bridges also
leave Y_(0,U)=h alone. Terminal rotation moves it to final X_(0,U), the
former-Y native endpoint excluded by the inherited observation contract.
The [receipt](RESULT.json) records every one of the 19 events.

At every allowed read cut, all S arrays and selected fields are identically
zero. All completed-X descendants after B1 and all five forward histories
are zero. Induction therefore covers every permitted homogeneous selected
controller, even with repeated S reads and arbitrary owner mixing. The
zero input has exactly the same permitted observations but a different
original A input. No decoder of those observations can restore both inputs.

## Reproduction and evidence

Python 3.12 standard library only, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/qq16-66port-second-axis
```

The registered hook runs normal and optimized exact replays plus the focused
integrity tests. Expected direct-verifier output:

```text
PASS_QQ16_66PORT_SECOND_AXIS support=4 observed_ports=66 stages=9 controls=8 no_new_kappa
```

The implementation uses rational sums of bit functions and the full ordered
logical F/B formulas. It does not import predecessor Python. Equality to
zero is checked by exact cancellation of identical functions; nonzero
claims use an explicit owner evaluation. The checker authenticates six
source files and two archive members, checks the selected sections, binds
local stage/pair/orientation to the hosted template, and compares the full
typed receipt. Default replay is read-only; `--emit-result NEW_PATH` creates
a fresh receipt exclusively.

Eight controls reject a coefficient sign error, reuse of the ineffective
first axis, a wrong initial cancellation sign, reading port 44, omitted
owner action, a missing cancelling bridge, a wrong F2 bank, and treating the
former-Y endpoint as an allowed zero observation. Positive controls show
that an extra port-44 read and a dense initial B0 query detect this witness.
The integrity tests check relocation and byte-preserving replay, reject an
on-disk receipt type change and source corruption, and reject removal of
proof-relevant receipt fields. Every mathematical check stays active under
`-O`.

This is an author-checked scoped proof with exact finite source evidence.
It does not rerun the literal native child kernels, the selected full cold
replay, or a proof assistant. It inherits the retained local QQ16 contract.
No full-controller rank, alternative read-set optimum, physical read/retention
cost, hosting, recursive precision, all-size admission, or complete supplier
invoice is established. The selected frontier remains unchanged. Granting
all 66 reads and storage zero cost already fails this information screen,
so no favorable completed supplier budget is claimed.

## Provenance and credit

Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
Task `joint-query-controller`, refined from scope key `0e34adbc1dd119161c3a`;
nonce `72c3e793ac4e1a0f869f8e219f301324`, recursive-interfaces track.
Exact source blobs and hashes are in [SOURCES.json](SOURCES.json); the
task card and overlap record are in [TASK.json](TASK.json).
Coordination uses [Discussion #2205](https://github.com/CrocSwap/integer-mult-bounds/discussions/2205).

- **kyzer1023 / PR2354**, inspected head
  `308ebc7405303bb7ed91b012bb705949c6091a16`: first-axis rank-74/defect-66
  certificate, the exact attaining read set, and this follow-up question.
- **Adam Gall / PR2093**, credited head
  `8b21a900eb520e4f11ea177b310f66316f8e8983`: common-axis owner-function
  witness and its A cancellation. **commdata2338 / PR2326**, credited head
  `fb7d64cd4a51c49bc56920305b0aca64011a420c`: coordinate-read contract,
  selected-shear/single-tap obstruction, and threshold question. Those heads
  are recorded in PR2354; neither package is a runtime dependency here.
- **Ali Romman / PR1969**: retained QQ16 local maps, native packet,
  cover semantics and ordinary schedule. Their existing source notices
  remain at [joint-query/NOTICE.md](../joint-query/NOTICE.md).
- **Cinna Davis / PR2216 and PR2268**: selected shear and paired-tap repair.
  **EdDiboi** and kyzer1023: preceding first-axis threshold investigations.
  **@starship-s / [PR2368](https://github.com/CrocSwap/integer-mult-bounds/pull/2368)**,
  head `e5d4d78dcfdd55d323fcbc60df477b9f25c7abff`, reports a separate
  obstruction for the dense old-chart read. Its scope and next questions
  were read at the final overlap check; its verifier was not replayed here.
  The present witness is detected by that dense read, so it does not supply
  PR2368's result or duplicate its different input family.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
OpenAI Codex (GPT-6 Astra) assisted with derivation, implementation, checking
and writing. Author-checked only; no independent human review is claimed.
New work is Apache-2.0. Frozen predecessor files are unchanged.

## Open next questions

1. **Which fixed ordinary read sets eliminate every local-axis family?**
   This matters because a sharp threshold for one family need not repair
   the controller. First form the simultaneous exact constraints from all
   eight local chart axes for one proposed unread set. A surviving defect
   is a falsifier; absence of one still requires testing other input families.
   No new cardinality lower bound is asserted here.
The former dense-B0 follow-up has a separate reported negative answer in
PR2368 at the head credited above. Further dense-record work should start
from its changed-record or final-cut questions, not repeat the closed
old-chart experiment. No independent review of that result is claimed here.

# Event-specific phases in the reached selected word

## Claim and contract

Fix a positive column multiplicity `f`. The selected #6030 scalar word is
`research/p104-helper470-twin-rung-removal/WORD.json.gz`, SHA256
`7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f`.
A MOVE from chart `a` to chart `b` has retained native normal form

```
T_ab = C_b C_a† = i^p S_ab,
```

where `S_ab` is the same literal recipe with its explicit `phase` gates
deleted. All other gates and their order are fixed. Its factorwise width-f
interpretation is `T_ab^(tensor f) = i^(pf) S_ab^(tensor f)`.

Permit a separate scalar gauge `lambda_(r,t)(f)` of modulus one for each
role and each program cut. It may depend on role, event history and width,
but not on the numerical input. The proposed implementation deletes every
MOVE phase tag and leaves every scalar ADD/COPY/SCALE coefficient and every
other operation unchanged. At each cut its role values must equal the original
role values multiplied by these gauges. Public input/output gauges are entirely
free. A zero role may change its gauge freely; an owned reset does not carry a
phase constraint through an absent or identically zero value.

**Theorem.** Such a gatewise gauge equivalence for the selected word exists
if and only if `4 | f`. Necessity already follows from fourteen reached events,
with no public endpoint or owned-lifecycle constraint. It remains true after
all constraints at dependent nonzero ADDs are dropped.

This is an obstruction to a specific gauge remedy, not a defect in the correct
phase-preserving source. Endpoint-only resynthesis, changed native recipes,
changed scalar coefficients, data-dependent recodings and rounded approximate
identities are outside the theorem. No global minimum number of phase tags is
asserted.

## Why an actual independent ADD constrains three gauges

Use canonical-chart coordinates: the original value of a role in chart `a`
is `C_a^(tensor f) sum_j R_j x_j`, for arbitrary independent input arrays `x_j`.
The rational row `R` starts as a coordinate vector. A MOVE changes its chart
and leaves its row unchanged; a common-chart scalar gate performs its indicated
rational row operation. This is the source's exact chart interpretation.

Consider `target += c * source`, `c != 0`, whose two pre-event rows are
linearly independent. The two operand arrays may be chosen independently:
a nonzero two-column minor gives an invertible rational map from two arbitrary
input arrays to those operands, with all other arrays zero. The common chart
is invertible, at any positive tensor width. Let `a,b` be the operand arrays.
Gatewise gauge equivalence requires

```
lambda_after (a + c b) = lambda_before a + c lambda_source b
```

for every `a,b`. Setting either operand to zero proves
`lambda_after = lambda_before = lambda_source`. This proof actually permits
any nonzero complex scalar gauges. Modulus one is retained as the stated phase
contract. Nonzero operands alone are not used as an independence test.

A MOVE on a nonzero row requires
`lambda_after = i^(-pf) lambda_before`. An untouched nonzero role keeps its
gauge, because its actual stored value is unchanged. A nonzero SCALE also keeps
its gauge. These are exact necessary relations; no numerical sampling is used
to extend them to arbitrary inputs or arbitrary `f`.

## Eight reached independence certificates

All event numbers and input-column numbers below are zero-based. The complete
prefix through event 9997 is replayed over rational rows. In every displayed
minor the first row is the pre-ADD target row and the second is the source row.
All eight determinants are `+1` or `-1`.

| Event | Literal ADD | Columns | Two-column minor |
|---:|---|---|---|
| 8255 | `229 -= 227` | 229, 227 | `diag(1,1)` |
| 9031 | `225 += 227` | 225, 227 | `diag(-1,1)` |
| 9034 | `231 += 225` | 231, 225 | `diag(1,-1)` |
| 9916 | `229 += 87` | 229, 87 | `diag(1,1)` |
| 9924 | `231 += 27` | 231, 27 | `diag(1,1)` |
| 9982 | `229 += 238` | 229, 238 | `diag(1,1)` |
| 9983 | `231 += 236` | 231, 7 | `diag(1,1)` |
| 9997 | `231 += 229` | 231, 81 | `diag(1,1)` |

The second checker separately streams nine input columns through all 9,998
prefix events using integer dyadic arithmetic, without the primary row engine
or `Fraction`. It obtains the same minors. These are certificates of the
specific reached rows; they do not assume that every pair of public roles stays
independent at every cut.

## Two actual histories and the closing contact

After event 8255, role 229 has the phase of role 227. Role 227 has no write
between events 8255 and 9031. Event 9031 therefore gives role 225 that same
phase. Role 225 has no write before it is read at event 9034, which gives role
231 the same phase. Call this shared, arbitrary nonzero phase `lambda`.

The only writes to roles 229 and 231 between those acquisition events and
event 9997 are the following. The intervening ADDs are precisely the certified
rank-two contacts above and cannot refresh the receiver's phase.

| Role | Chronological MOVE events | Chart path | Literal phase exponents |
|---:|---|---|---|
| 229 | 9904, 9938, 9994 | `3 -> 81 -> 254 -> 259` | `1, 0, 0` |
| 231 | 9901, 9955, 9987 | `3 -> 25 -> 256 -> 259` | `1, 1, 0` |

Every one of these six native calls has rank one. The literal bases are

```
3:   ()                 25:  (38,)
81:  (493,)             254: (51,478)
256: (21,38)            259: (21,38,459).
```

Consequently immediately before event 9997,

```
lambda_229 = i^(-f) lambda,
lambda_231 = i^(-2f) lambda.
```

The independent ADD at 9997 forces these two phases to coincide. Since
`lambda != 0`, this implies `i^f = 1`, or exactly `4 | f`.
No boundary-normalizer assumption appears in this contradiction. Free initial
phases, free final phases, different phase choices for every role occurrence,
and arbitrary gauge freedom at all omitted dependent ADDs cannot repair it.

Conversely, when `4 | f`, the tensor factor of every explicit native `phase`
gate in the retained alphabet is one. The trivial gauge makes phase deletion
identical to the original factorwise interpretation of every MOVE, with every
scalar gate unchanged. This uses the retained literal integer phase alphabet;
it does not require a new census or physical all-column admission.

## Separate native checks and the local repair boundary

The source compiler lowers the six operators and reports the phase exponents
above. A separate exact Gaussian-dyadic interpreter compares every one of the
512 basis columns of each lowered recipe against its literal chart expression.
For the two three-MOVE paths `A` (role 229) and `B` (role 231), it also checks
all 512 columns of

```
T_A† T_B = I,       S_A† S_B = -i I.
```

This is a check on the MOVE paths as operators; the actual chronological
histories also contain the ADDs and are handled by the row/gauge argument.
It is not presented as a six-MOVE contiguous source subroutine.

Changing the final ADD coefficient from `1` to `i^(-f)` would reconcile these
two local phase labels: in the transformed coordinates its coefficient must
be `lambda_231/lambda_229`. This illustrates why unchanged scalar coefficients
are a substantive hypothesis. It does not repair or price the entire word.
Other contacts and normalizers remain to be checked, and a scalar phase
operation has its own physical and precision contract.

## Scope, credit and remaining assumptions

Nick Petalas's #6298 supplied the shared-frame triangle, its exact width
criterion and the explicit role/history-gauge open question. Unpaidmoon's
#6293 supplied the selected MOVE census and tensor-phase question. This result
adds a reached causal constraint cycle with certified independent operands;
it does not repeat either complete census. Nick Petalas's #6025 classifies
fixed nonlinear role recodings under a different all-independent-input
contract; occurrence-dependent phases and the selected reached graph are the
scope here. The elementary cycle-potential argument is classical.

Credit DreamingOfClouds (#6030/#5907), Ali Romman (#5827/#5599 and the
independent Gaussian interpreter in #1862/#1931), Chafik Boukhalfa's native
channel, icekylinx's retained frame compiler, DLamdata (#5894), Matarener
(#5974/#5442), Rohan Arun (#1972), Adam Gall (#1940), Josie Elliston (#1071),
and the native/controller/compiler/precision lineage retained in those sources.
The exact inputs remain unchanged. Prepared for @CubeJerry with substantial
OpenAI Codex assistance, including separately written row/column checks and
lead review. Apache-2.0.

No new kappa, paid-profile improvement, supplier admission or selected-frontier
change is claimed. The five assumptions `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery` remain. In particular this
scoped theorem uses the exact common-chart and factorwise tensor contract;
it does not independently establish every selected native map, machine tariff,
rounded multiplier, storage bound or outer analytic theorem. No independent
human or proof-kernel verification is claimed.

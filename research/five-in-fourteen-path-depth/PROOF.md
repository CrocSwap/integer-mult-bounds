# No free completion of the stated fresh-input raw-port schedule

Prepared by Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.
This is a written all-width support proof with exact caller corroboration,
not a new κ, formal-kernel proof, or exclusion of every five-in-fourteen word.

## 1. The complete raw architecture under audit

The retained PR4813 claim specifies four three-call ports on original input
pairs `(x1,x2),...,(x4,x5)` and one two-call port on `(x5,x1)`.
Each port's observations are written in terms of those original independent
inputs. Give the decoder every original input as well as all ten raw port
outputs; this is more data than retaining only the displayed observations.
The native port contracts are Dugongue's PR4743, using Yiyang's PR4710
phase repair and lee-phys's PR4688 prefix.

Write `A=C0`, `P=SUS`, `Q=SVS`, and `L_f=P_f+2Q_f`, where each individual
base word is tensorized before scalar mixing. The constructive source ports
have exact outputs

`U2_f(x,y)=(A_f x, A_f y+F_f x)`,
`U3_f(x,y)=(A_f x, D_f y+B_f x)`,

where

`F_f=A_f P_f A_f+2 A_f Q_f A_f`,
`D_f=(Z1 V C2 W C0)_f`, `W=Z0 Z2`,
`B_f=D_f P_f A_f+2 D_f Q_f A_f`.

These are the valid raw ports, before any sector subtraction or dense
reconstruction. The source normalizer/sector issue is addressed separately
by PR5004. The present proof tests whether **any fixed free decoder** could
complete this stated raw snapshot, without relying on that local issue.

If a later port instead receives an earlier updated output as its input,
the raw equations above change. Such a different query chronology is not
excluded by this theorem.

## 2. An honest expansion and the fifth input

PROGRAM.json expands the source's constructive ports on fifteen banks:
five original inputs and ten owned port-copy banks. Each port starts with
copies of the named original inputs. This explicitly permits clean scratch
and free copying rather than assuming a five-bank storage restriction.

The two-call expansion is:

1. Copy x and y into the port's two banks.
2. Apply paid C0_f to the first bank.
3. Add the separately applied P_f and 2Q_f images of that bank into the second.
4. Apply paid C0_f to the second bank.

For a three-call port, additionally apply W_f to the second bank, paid C2_f,
then the free V_f and Z1_f. This is exactly the source's `D=Z1 V C2 W C0`
order. An ADD of a monomial image can be implemented by transforming its
source, adding, then restoring that source; it needs no extra paid call.
The source already supplies this implementation contract.

There are fourteen paid calls, ten copies, ten monomial-image ADDs and eight
additional monomial blocks. The audit checks every raw output column against
the actual source port matrices, keeping the branches separately tensorized.
The paid-depth trace for the five independent original inputs is

`(3,3,3,3,2)`.

Specifically x5 is a target input of U3(x4,x5), so crosses at most two paid
calls there, and a source input of U2(x5,x1), so crosses at most two there.
The copies used by those ports are fresh original copies; their query
paths are not concatenated. Recording-only copies of intermediate values
in this expansion do not add paid depth. Feeding them back into future paid
calls would change the chronology and is a distinct construction.

## 3. The exact support polynomial at the raw endpoint

Set all original inputs except x5 to zero, and let x5 be one address basis
vector. Put z=2^f. A paid direction `C_v^(tensor f)` has z nonzero entries
per column. A monomial address map has one. The nonzero coefficients of
x5 in the complete raw state are exactly:

| Retained field | Coefficient | Column-support bound |
|---|---|---:|
| Original x5 | I | 1 |
| Closing port's t5 | A_f | z |
| Fourth port's raw u4 | D_f | z² |
| Closing port's raw s1 | F_f | 2z² |

Every other retained field has zero x5 coefficient. Therefore the complete
stacked raw state has support at most

`q(z)=1+z+3z²`.                                          (1)

Cancellations can lower these bounds, never increase them. Scalar coefficient
2 does not create two extra paths; the two F branches themselves supply the
two terms. The verifier propagates nonnegative integer support polynomials
through every literal instruction and obtains exactly `(1,1,3)` for (1).
It also traces all prefixes, so the fifth-input degree remains at most two
through the standard implementation's intermediate points.

## 4. Free postprocessing cannot supply a missing exponent

For any fixed finite linear decoder, suppose each of its free steps has
column support bounded uniformly in f. This includes the source engine's
register mixing on a fixed number of banks, shifts, copies, erasures,
monomial address permutations and diagonal phases. Coefficients may even
depend on f, and address permutations need not be columnwise tensor lifts;
these enlargements do not increase a step's column-support bound. What is
fixed is the finite program/bank size, not the scalar values.

If a matrix has at most b nonzero entries per column, applying it to a
vector of support s gives support at most bs. Products multiply these
bounds. Hence the decoder has some finite bound B independent of f, and
its output on the preceding basis input has support at most

`B(1+2^f+3*4^f) <= 5B*4^f`.                             (2)

The required target is `K_f x5`, where K=C0 C1 C2. Every base entry of K
is nonzero; every tensor column has exactly `8^f` nonzero entries. For any
fixed B, choose f with `2^f>5B`. Equations (1)–(2) then contradict the
required support `8^f`. Thus the raw snapshot admits **no fixed free
completion of even the fifth target**, regardless of how the decoder mixes
all the other raw records and original inputs.

This is an elementary support-growth argument, related to the one-array
method credited by Jacob Alan Sussman's PR4628. The method is not claimed
as new; the new application closes the named raw architecture and gives
its actual source-bound degree deficit. An arbitrary finite-width dense
matrix inverse does not have a uniform bounded-column free implementation
merely because its matrix is invertible.

The same argument tolerates any fixed number of recording-only intermediate
taps from the displayed expansion: every such fifth-input coefficient has
degree at most two, so their finite sum is still O(4^f). It does not cover
an alternative internal implementation with new taps, feedback into later
queries, a decoder with added paid calls, a number of decoder operations
growing with f, or a free letter whose column support itself grows with f.

The per-input depth requirement must not be summed into a universal `3W`
call lower bound. Shared calls can lie on paths from multiple inputs. We
exclude this precise deficient-depth caller, not every fourteen-call caller.

## 5. Sector restriction alone does not fix this global gap

There is a counterexample domain even within either chosen swap sector.
For sigma=+1 choose x5=e0 tensor ... tensor e0. It is fixed by T_f, has
input support one, and its K_f image has support 8^f, so the preceding
contradiction applies unchanged.

For sigma=-1 choose

`x5=(e1-e4) tensor e0 tensor ... tensor e0`.

It is a minus eigenvector of T_f and has input support two. A direct base
calculation gives support four for K(e1-e4). Each remaining factor K e0
has support eight, so its target has support `8^f/2`. The raw and decoder
support is at most `2B q(2^f)<=10B*4^f`. Choosing `2^f>20B` gives the
contradiction. The other four original inputs may all be zero, satisfying
any of their chosen sector signs. Thus even a fixed-sector claim needs
more than the displayed raw records and an unpriced free reconstruction.

This is separate from the local sector error proved in PR5004: it remains
after imposing the correct sector premise on the raw input.

## 6. Exact checks and changed-premise controls

The independent primitive interpreter checks all forty original input columns
at width one over Q(i), and all 320 at width two over F17 with i=4. Every
one of the fifteen final banks is compared with a separate oracle built
from the source's raw port matrices. The oracle tensorizes each branch,
not B or F as a whole. The target K support and both sector witnesses are
also checked against an ordinary three-call primitive implementation.
Modular checks corroborate finite identities; the proof above supplies
the all-width conclusion.

Two changed-premise controls prevent an overly broad exclusion:

- Upgrading the closing U2 to U3 gives fifteen calls and fifth-input depth
  three. This removes the present support obstruction; it does not prove
  a completed fifteen-call decoder.
- Feeding the updated fourth-port target into the closing port instead of
  original x5 still uses fourteen calls but gives fifth-input depth four.
  Its actual raw outputs differ from the source's declared snapshot. It is
  a genuine changed chronology left open by this theorem, not a variant
  to which the depth-two conclusion may be silently applied.

The polynomial certificate is exact and reproducible. The paper does not
claim a physical supplier, a better κ, a full native replay, or independent
human/proof-assistant verification. All frozen predecessor files are unchanged.

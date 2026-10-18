# Independent audit: phase order and the required bank bits

**Scoped written theorem and independent finite checks; no new kappa.**
This takes Gareth Davidson / bitplane's released independent-audit handoff in
[Discussion2842](https://github.com/CrocSwap/integer-mult-bounds/discussions/2842).
The inspected predecessor is [PR2850](https://github.com/CrocSwap/integer-mult-bounds/pull/2850),
commit `a007c32f992195ad372806db38c9359dd49382ad`.
Its working reverse-order continuation and its closed-separable-block lower
bound have different hypotheses. We corroborate that distinction and give a
sharp order/bank-bit criterion for the particular open continuation below.

## Contract and result

Take independent binary Fourier labels `u_j,v_j`, for `j=0,...,f-1`.
Column j uses exactly one assigned bank address bit `g(j)`. The bank has
arbitrary joint complex coefficients; no state is prepared, discarded or
assumed separable. On that bank bit define the chronological producer

```text
P_j = X(v_j) Z(u_j): |c> -> (-1)^(u_j c) |c+v_j>.
```

Execute all producers in order `0,1,...,f-1`, followed by the identical
consumers in a permutation `pi` of those indices. The labels are unchanged
throughout this boundary. Let `pos(j)` be j's position in pi. The exact
endpoint is identity on the bank times the phase

```text
E = sum_j u_j v_j
    + sum_{i<j, g(i)=g(j), pos(i)<pos(j)} (u_i v_j + u_j v_i)   in F2.
```

Consequently:

1. The bank returns for **every** consumer permutation, even incorrect ones.
   Bank return alone is not the desired data identity.
2. The endpoint is the desired dot-product phase for all labels iff every
   bank's consumer subsequence reverses its producer subsequence.
3. Among assignments of **one independent tensor-bank bit per column**, the
   minimum number of active bits is the length of a longest strictly
   increasing subsequence of pi. With just one bank bit, only full reverse
   consumer order works. Same-order consumers require f independent bits.

For example, pi=`(2,0,1)` needs two bits; assignment `g=(0,1,0)` works.
There is no three-term increasing subsequence, while `(0,1)` supplies the
necessary two-bit lower witness. The all-size statements concern precisely
this producer-prefix / consumer-permutation contract, not arbitrary open
words, encodings, non-Pauli operations or a general dimension optimum.

## Proof for every f

During either occurrence of P_j, its sign is u_j times the incoming bank
bit. Each v_j flips its bank bit twice, so the bank's final translation is
zero. Each u_j encounters the original arbitrary bit twice, so incoming-bank
terms in the phase cancel. Its own first v_j flip lies before the second
occurrence, leaving the self term `u_j v_j`.

For i<j on distinct bits, there is no interaction. On the same bit, their
producer occurrences appear i,j. If their consumers appear j,i, the pair is
nested: i,j,j,i. The two contributions from each cross label cancel. If
consumers appear i,j, the pair alternates: i,j,i,j. Direct sign accumulation
leaves exactly `u_i v_j + u_j v_i`. This proves the displayed endpoint by
summing over unordered pairs. No cubic or higher term appears because each
sign is one u times a bank bit plus a linear sum of v labels.

The two monomials of an alternating pair cannot cancel against a different
pair, since the labels are independent. If i,j is such a pair, set
`u_i=v_j=1` and all other labels zero. Desired phase is zero and actual phase
is one, for every incoming bank bit. This proves necessity as well as
sufficiency of reversing order within each bank.

An increasing subsequence of pi is a set of indices whose producer and
consumer orders agree. Every two of them must therefore use different bits.
Its length is a lower bound. For the matching construction, assign index j
the rank `L(j)-1`, where L(j) is the length of a longest increasing
subsequence ending at that occurrence in pi. If i<j occurs earlier than j,
then L(j)>=L(i)+1. Thus equal-rank indices occur in decreasing order in pi,
which is exactly a legal bank class. The ranks use no more bits than the
longest increasing subsequence. This elementary decreasing-subsequence
partition argument supplies both bounds; no optimality solver is trusted.

This is the standard permutation-order partition argument applied to the
predecessor's Pauli schedule, not a claim to a new combinatorial method.
The proof does not invoke the closed-separable-commutator dimension bound:
these bank states remain open between distinct child boundaries.

## Independent evidence and controls

`audit.py` imports no predecessor code. It propagates the arbitrary incoming
bank bits as linear polynomials and accumulates exact quadratic sign terms
using integer bitsets. It checks all **5,913** consumer permutations for
f=1,...,7, including constructed bank assignments and increasing-subsequence
lower witnesses. For f<=5 it separately enumerates every set partition:
**6,635** schedule/partition cases and **153** independently minimized
permutations. This checks assignments beyond the constructive choice.

`physical.py` imports none of the symbolic checker. It uses exact rational
physical-array operations: a bank-controlled x translation, H0 on the bank,
a bank-controlled y translation, and literal H0 inverse. The matrices are
`H0=[[1,1],[1,-1]]/2` and `H0^-1=[[1,1],[1,-1]]`. It checks every column in
five f<=3 fixtures, **488 columns / 87,104 coefficients**, against the
closed physical kernel

```text
I_bank tensor Q_f[(x',y'),(x,y)]
    = 2^-f (-1)^((x'+x) dot (y'+y)).
```

Every bank lane is included, including arbitrary nonzero dirty lanes; linearity
then covers arbitrary joint inputs. The physical path does not use the
symbolic order criterion as its reference. Seven symbolic controls reject
three incorrect sharing/order choices, malformed schedules and the aggregate
parity shortcut. Three physical mutations reject same-order sharing, omitted
Hadamard scaling and an omitted consumer. Recorded matrix failure witnesses
are retained in `RESULT.json`. `test_package.py` also verifies read-only,
relocated Git-free replay and rejects receipt/reference-pin corruption.
All checks use explicit exceptions and remain active under `-O`.

The numerical ranges above support the written all-size proof; a finite
census by itself would not establish that theorem. Both implementations were
prepared by the same AI-assisted author in this independent audit session;
this is not independent human review or proof-assistant verification.

## What the result does not save

The displayed unfused word executes 2f producer/consumer words, each with two
one-axis bank basis changes. Using the predecessor's H0-through-C expansion,
that schedule still has **4f one-axis C calls**, before its wrappers. This is
a count for that word, not a lower bound for every implementation. We do not
rerun or recertify its native C expansion, finite machine invoices, C/Q
recursion or two-parent-level implementation.

The bit minimum counts active tensor-bank coordinates. It does not permit
dropping lanes of an existing fixed operand or normalizing a child by half
its actual operand volume. All spectator lanes still count. Moving the
consumer order may also be illegal for an actual caller; no such caller is
admitted here. The predecessor's support gate and failed complete budget
are retained as its scoped claims, not newly proved by this checker.

The family decision is **narrow / stop**: this audit explains the working
state boundary and supplies sharp schedule controls. It does not justify
another construction/search round in the unchanged alphabet. Encoded
caller interfaces, physical movement, hosting, precision, all-size admission
and the selected cold replay remain outside scope. No selected record or
frozen predecessor is changed.

## Sources, replay and publication

Base main: `4865c30d0fb12a475bb6eaaca1c781a1592a3811`, priority revision 5.
`SOURCES.json` pins the base catalogue/selected record and the exact inspected
PR2850 README/model Git blobs and SHA-256 values. Those predecessor files
are **reference context only**: no predecessor is imported, executed, copied
or required at replay. The standalone checker guards the recorded reference
pins against drift; that is not fresh authentication of remote source bytes.
The generic runner authenticates the base provenance through Git. A Git-free
export supports the standalone arithmetic replay, not that provenance check.

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/phase-order-bank-audit
python3.12 -I -O -B research/phase-order-bank-audit/audit.py
python3.12 -I -O -B research/phase-order-bank-audit/test_package.py
```

Normal verification is read-only. `audit.py --emit` prints a regenerated
receipt for deliberate typed comparison; it does not overwrite evidence.
The exact task, original random draw, changed handoff scope, overlap coverage
and remaining obligations are in `TASK.json`.

## Open next questions

Can an actual recursive caller accept a reordered or encoded continuation
that changes the **complete** child bill? First pin that caller's accepted
frames and live data dependencies, pay encoding, movement and restoration,
and check two parent levels. The missing favorable native caller contract
is the blocker. Merely sharing bank bits or retiming this same word has not
supplied a saving. See the structured question in `TASK.json` and the
predecessor's paid-interface handoff rather than treating this audit as a
new reservation.

## Credit

Gareth Davidson / bitplane's PR2850 supplies the exact phase-accumulator
contract, the original shared-bank counterexample, working reverse-order
and tensor-bank controls, its native C/Q experiment and the released audit
request. Those results and standard Pauli/linear-algebra methods retain
credit. The present addition is a separate implementation and the sharp
producer-prefix order/bank-assignment theorem in the restricted model.
Earlier contributor attribution remains in the unchanged predecessor.

Prepared by Dennis / antunishdPursuit with substantial OpenAI Codex assistance
in derivation, source inspection, implementation, execution, self-review and
writing. No subagents or independent human review. New files: Apache-2.0.

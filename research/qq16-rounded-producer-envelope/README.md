# A rounded-operation envelope for the QQ16 producer pair

**Conditional interface lemma and exact finite certificate; no new kappa.**
For the literal F0 followed by B_1_2 producer, the sufficient local relative
tolerance

```text
u <= 2^(-beta-delta-102)
```

implies the two completed-stage data tolerances required by
[Nick Petalas's PR2965](../qq16-producer-defect-transfer/README.md), under the
completed-operation premises below. Original data have norm at most H>0;
the 480 dirty helper inputs have norm at most `2^delta H`, where integers
`beta, delta >= 0`. Scalar, native-child, adapter and cover-map defects are
all permitted. Owned private CLEARs are exact. Helper errors from F0 are
carried into B1's actual operand bounds.

This establishes a sufficient error contract for the source trace, **not an
implementation satisfying that contract**. In particular, 102 is neither a
component width nor a minimum precision. Exact restoration of borrowed helper
bits, native interiors, finite grids, physical hosting and a paid F17 consumer
are not supplied. The selected result and predecessor sources are unchanged.

## Delta and dependencies

PR2965 supplies the completed-output inequality
`49 epsF + 1923 epsB + epsD`, but not producer-interior error bounds.
[PR2995](../qq16-producer-dirty-fault/README.md) and
[PR3017](../qq16-native-dirty-fault/README.md) show why a dirty-input bound is
necessary under a permissive relative-error contract. PR3036/3067 and
[the component-rounding reference](../qq16-native-rounded-components/README.md)
also provide concrete finite rounding failures. We do not rederive those
witnesses.

[PR3181](https://github.com/CrocSwap/integer-mult-bounds/pull/3181), pinned at
`80fc72d14546088e9fce3c06dc12bc67270da0af`, studies signed scalar-projection
cancellation, grids and adjoints. [PR3189](../qq16-noise-lattice-audit/README.md)
shows that ideal input-grid checks do not establish exact scalar arithmetic
after arbitrary approximate child returns. Here scalar errors are charged,
and no signed cancellation between different native routes is used in the
interior error envelope. The new
quantities are positive **relative-defect derivatives** for the complete
native event streams, their verified all-cut maxima, and the noisy two-stage
composition. The old Horner magnitude values are reproduced and credited,
not claimed as new range improvements.

Scientific base: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
The literal source is the retained joint-query commit
`a6e6ad3936f67b8f63b5b68c5e75d540610a65e7`; PR2965 is
`526f2c242202b31b15e09a7502dfb8ff757b2bad`. Ideal native, owner, sweep and
endpoint semantics are inherited from the pinned
[native review](../joint-query/evidence/NATIVE-REVIEW.md),
[bridge review](../joint-query/evidence/BRIDGE-REVIEW.md) and
[conserved word](../joint-query/evidence/CONSERVED-QQ16.md).
No predecessor executable is imported. [SOURCES.json](SOURCES.json) binds
the actual main bytes, exact heads and documentary comparisons. The claim is
in discussion [#2727](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727#discussioncomment-19001931),
following PR2965's producer handoff. [TASK.json](TASK.json) records the scope.

## Norm and completed-operation contract

For each field use `max_owner ||payload(owner)||_2`, then maximize over any
stated field sector. This norm is preserved by the inherited native unitary
operators, their monomial adapters, and full-cover owner/payload maps, at
every positive common tensor depth. The owner action is retained: a cover map
is not identified with a payload permutation at a single owner.

The bound is at **completed event boundaries**. In the literal order, allow
the following destination-local errors, measured using the actual operands:

| Event | Maximum allowed defect |
| --- | --- |
| ADD `d += c s` | `u (||d|| + |c| ||s||)` |
| SCALE `d *= c` | `u |c| ||d||` |
| Completed native child/line, adapter or cover map on d | `u ||d||` |
| Owned private CLEAR | zero |

The same u bounds all categories within one stage. Errors may be coherent,
state-dependent, nonlinear or correlated. Nothing requires independent noise.
No event may change another field. A child implementation must therefore
establish its complete destination and scratch/side-effect contract; a bound
on its central arithmetic alone is insufficient. Native internal rounding,
operand access, sweep barriers and actual finite storage remain implementation
obligations. Serialized phase events are control labels; mathematical phases
inside completed native recipes are covered by their unitary contracts.

Initially L0..L703 have norm at most A. C0..C7 may contain arbitrary private
dirt. The checker rejects every read before its first CLEAR and checks their
exact final zeros. Uninitialized private contents are excluded from magnitude
claims; no bound on their initial norm is needed. There are no CLEARs of
persistent data or helpers. Exact helper endpoint semantics are inherited;
their needed norm consequence is that the ideal returned helper block has
norm at most its entry bound, including its prescribed unitary frames.

The source's owner-local bodies are analyzed per owner, with sweep barriers
retained. In particular, each of the sixteen private bodies across the pair
contains only scalar operations and a native line, with first/last C0 CLEARs;
the checker verifies this. A cut-table row is the virtual aligned cut for
that body. The all-cut maximum bounds unprocessed, active and completed owners
during its physical sweep, and the endpoint bounds apply after the barrier.
This reasoning permits the stated reuse of one C0; it does not allocate a
full private bank or price a physical owner schedule. Core access/embedding
semantics remain inherited, and extra unlisted inexact movements are excluded
from the contract until separately charged.

## Positive recurrence and proof

Attach a polynomial `q_d(z)` with nonnegative rational coefficients to each
initialized field. Persistent entry fields have polynomial 1. At a CLEAR,
set the polynomial to zero. At an ADD set

```text
q_d(z) <- z (q_d(z) + |c| q_s(z));
```

at a SCALE use `z |c| q_d(z)`, and at a native child, adapter or map use
`z q_d(z)`. These are **norm inequalities**, not a replacement of native
operators by identities in a signed-state replay. The largest polynomial
degree is at most the number N of permitted defect sites in the whole stage.

Let `P_d=q_d(1)` and `J_d=q'_d(1)`. Their exact recurrence is inexpensive:
apply the same positive row transfer to P and J, then add the updated P to J
at each inexact event. CLEAR resets both to zero. The verifier separately
accumulates the five derivative categories ADD, SCALE, child, adapter and map.
Their sum is J; [RESULT.json](RESULT.json) records the relevant exact rows.

Induction using the local defect inequalities proves, at every cut,

```text
ideal norm <= A P_d,
actual norm <= A q_d(1+u),
actual-versus-ideal error <= A (q_d(1+u)-q_d(1)).
```

For the third inequality, transfer the previous error by the positive row
map and add the new error bounded by u times the positive combination of
actual operand norms. This is precisely the difference between the q and P
recurrences. CLEAR resets the error. The argument holds for arbitrary native
isometries, including noncommuting ones, and for every allowed error pattern.

For any degree-n nonnegative monomial, with `n<=N` and `u>=0`,

```text
(1+u)^n - 1 <= n u (1+u)^(N-1).
```

Summing the monomials gives
`q_d(1+u)-q_d(1) <= u (1+u)^(N-1) J_d`.
If `N u <= 1/2`, then

```text
(1+u)^N = sum_k binom(N,k) u^k
         <= sum_(k>=0) (N u)^k = 1/(1-Nu) <= 2.
```

Thus the useful finite-trace bounds are

```text
all-cut error <= 2 A u J_d,
all-cut actual norm <= 2 A P_d.                 (2)
```

These constants are sufficient majorants, not asserted attainable physical
norms. The feedback factor cannot simply be omitted: two scalar identity
steps with positive relative errors already give `(1+u)^2-1 > 2u`.
For category tolerances `u_c`, the same path argument gives
`error <= 2 A sum_c u_c J_(d,c)` when `N max_c u_c <= 1/2`.
Different category tolerances require maximizing that weighted sum over the
relevant cuts; the recorded global maxima here use a common u.

## Exact finite ledger

The source has 712 fields: 224 data, 480 persistent helpers and eight private
fields. Indices below are zero-based in the expanded, unfiltered stream.

| Quantity | F0 | B_1_2 |
| --- | ---: | ---: |
| Events / changed-field cuts | 26099 / 26089 | 27019 / 27009 |
| Permitted defect sites N | 26057 | 26977 |
| Exact private CLEARs | 32 | 32 |
| Maximum polynomial degree | 184 | 854 |
| All-cut P maximum | 5413950274051752469/256 | 573411134169296526275133/64 |
| All-cut J maximum | 10632335516156845470267/4096 | 34778728470688788237067911/8 |
| First maximizing event / field for both P and J | 26052 / L132 | 26777 / L86 |

In each stage the displayed J also bounds every completed data and helper
output, and is attained by the positive recurrence at a final data output.
The inequalities `J_F < 2^62`, `J_B < 2^82`, `P_F < 2^55` and `P_B < 2^73`
are exact rational comparisons. The receipt additionally supplies the helper
terminal maxima, category contributions and complete cut-table digests.

## Composition with bounded dirty helpers

Let original data be bounded by H>0 and initial helper norms by `2^delta H`,
where `beta,delta>=0` are integers. Both stages start with arbitrary private
dirt and execute the prescribed exact CLEARs. No additional inexact handoff
operation is silently inserted between stages.

It suffices to choose separate tolerances

```text
u_F <= 2^(-beta-delta-71),
u_B <= 2^(-beta-delta-102).                       (3)
```

Both satisfy `N u <= 1/2`. For F0 take `A_F=2^delta H`. By (2), even its
all-cut error is bounded by

```text
2 A_F u_F J_F < H 2^(-beta-8) = eta_F.
```

The inherited ideal F0 data map has norm at most 58 independently of helper
values. The checker calibrates this bound from the actual R/K row sums,
the A/T section identities and the retained endpoint equations: X bounds on
A/T/U are 4/56/57, and Y bounds are 6/58/58. This is predecessor evidence,
checked here because the handoff uses it. The actual completed data therefore
have norm below `59H`. Ideal
helper endpoints preserve their entry norm, so the actual helpers are bounded
by `2^delta H + eta_F`, not by their original bound alone. Consequently all
persistent B1 entry fields are bounded by the conservative common value
`A_B=2^(delta+6) H`. This explicitly carries the F0 helper error into B1.
Prescribed unitary representation changes preserve these norm bounds; any
extra physical conversion must separately satisfy a charged error contract.

Apply B1's estimate to the actual incoming data and helpers. Its ideal data
endpoint is independent of the arbitrary helper inputs. By (2) and (3),

```text
2 A_B u_B J_B < H 2^(-beta-13) = eta_B.
```

These are exactly sufficient completed-stage defects for PR2965. If the
chosen decoder additionally supplies `epsD <= H 2^(-beta-1)`, that theorem gives

```text
decoded data error <= (49/256 + 1923/8192 + 1/2) H 2^-beta
                   = (7587/8192) H 2^-beta < H 2^-beta.
```

For example, beta=64 and delta=0 permit completed-event tolerances `2^-135`
in F0 and `2^-166` in B1. The single common tolerance in the opening statement
satisfies both. These exponents concern the local norm contract, not floating
significands, fixed-point fractional positions or sufficient register widths.

The noisy all-cut magnitude bounds include data, helpers and initialized
private fields: F0 is below `2^(delta+56) H`; B1 is below `2^(delta+80) H`.
They do not bound intermediates inside an atomic native event.
Relative to the corresponding ideal pair's returned helper block, helper
error is at most `eta_F+eta_B`, using the inherited isometric return map.
This is an approximate return bound; it does not establish exact borrowed-bit
restoration. The eight private fields do return exactly to zero.

## Cost and expansion decision

No word, tariff or selected frontier is changed. The literal producer counts
checked here are:

| Completed operation | F0 | B1 |
| --- | ---: | ---: |
| ADD / SCALE / CLEAR | 20278 / 715 / 32 | 20654 / 715 / 32 |
| Native children, including wrapper lines | 3494 | 3510 |
| Core endpoint/residual adapter events | 1570 | 1570 |
| Full-cover map events | 0 | 528 |

The predecessor's constructive local scalar allowances remain 211210 and
214986 real primitives, with native rank masses 5530 and 5546. Its eight and
24 additional line children also require 16 and 48 native wrapper maps.
These are predecessor abstract allowances, not prices certified for an
implementation of (3). The retained PR2707 decoder further lists 336 rank-one
children, 672 wrappers, 464 cover maps, scalar allowance 25840, 224 owned output
fields and up to sixteen private fields. None is free or implemented here.

The new error implication and norm envelopes are proved under the stated
contracts. Ideal operator semantics and the completed decoder theorem are
inherited. Finite arithmetic realizing the local tolerances, component
representation/grid, child scratch restoration, exact borrowed-state return,
physical allocation/movement, tape/control and subsequent F17 consumption are
unknown. The centre-charge/coverage decision is also not settled by this
numerical lemma. No favorable complete recursive invoice is asserted.
Family decision: **narrow and stop** at this conditional interface; these
unknown costs do not justify another dependent implementation search.

## Reproduce and verification limits

From the repository root, standard-library Python 3.12:

```sh
python3 -Werror -I -B scripts/research_package.py --package research/qq16-rounded-producer-envelope
```

The principal markers are

```text
PASS_QQ16_ROUNDED_PRODUCER_ENVELOPE stages=2 cuts=53098 offset=102 conditional_completed_operations no_new_kappa
PASS_QQ16_PRODUCER_ENVELOPE_INDEPENDENT integer_cuts=53098 reverse_rows=6 categories=5
```

[verify.py](verify.py) authenticates seven live inputs and calculates every
changed-field row using exact rationals, in normal and optimized Python.
[independent.py](independent.py) imports no primary/predecessor implementation:
it checks every P/J row with a separately written integer-grid interpreter,
then uses six reverse covectors to check the five relative-defect categories.
The verifier's oversized exact integer grid is an arithmetic cross-check;
it is not a proposed physical representation for QQ16.

Ten behavioral groups in [test_verify.py](test_verify.py) include actual
noncommuting two-dimensional isometries with coherent state-dependent faults,
explicit positive polynomials, a feedback-factor counterexample, dirty input
and noisy-helper reuse, omitted child/map faults, erased private transients,
illegal CLEARs/uninitialized reads, scalar coefficient changes, exact tolerance
comparisons, endpoint-geometry mutations and pre-execution source corruption. Finite fixtures corroborate
the written arbitrary-dimension proof; they do not replay the complete physical
native operators. No independent human or formal-kernel review is claimed.

Replay is read-only. `verify.py --write PATH` creates an absent receipt and
refuses to overwrite one. The direct three Python commands work in a source
export containing the declared inputs. The primary replay is bounded by two
28000-event words, 712 fields and five error categories; the certificate read
is capped at 16 MB. Python integers/collections allocate dynamically. No solver,
network, third-party package or native toolchain is required. The selected cold
replay and full native proof replay were not run because their source/claims
are unchanged and are explicitly inherited.

## Open next questions

1. Supply one actual native child's complete destination/scratch defect
   contract at a finite grid and dirty range. Begin at a literal child followed
   by a half-ADD, retaining the latter's nonzero rounding allowance. The absence
   of a finite, priced child implementation blocks numerical realization of (3).
2. Decide the required helper return contract. If exact borrowed bits must be
   restored, prove a restoration mechanism or an exact arithmetic invariant;
   the `eta_F+eta_B` estimate is insufficient. Any correction must include its
   error, storage and movement costs.
3. Bind a complete F17 consumer and owner/sweep schedule to the producer and
   decoder. Start with the charged operation/lifetime ledger above, including
   the centre/coverage convention. Unknown physical and recursive tariffs
   currently prevent a favorable complete-cost decision.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New derivation, checker, tests and prose are Apache-2.0. No independent human
review is claimed. Nick Petalas supplies PR2965's completed-output transfer and
PR2736's preceding decoder defect analysis. The positive-majorant method is
standard; its noise-aware application and two-stage dirty-helper composition
for these literal producer words are the contribution here.

Credit Ali Romman and the retained QQ16 team for the words and operator/sweep
contracts; ywz65 for PR2707/2540; Arham Tahir for PR2681/2995/3036; Tekalign for
PR3017/3189; Ross Richardson for PR3067 and earlier rounded/restoration
contracts; Sricharan Vagvala for the native component-rounding reference;
dcharb78 for PR3181's separate scalar-projection study; and starship-s, Sagar
Thakrar, DLamdata, Douglas Colkitt and the source contributors retained in
[the original notice](../joint-query/NOTICE.md). Their frozen files and credit
are unchanged.

# A source-bound precision interface for the native P104 channel

**Finite local precision theorem; no side correction, admitted supplier or new κ.**
For the literal native channel of [PR1991](https://github.com/CrocSwap/integer-mult-bounds/pull/1991),
this package bounds every instruction boundary, including arbitrary dirty
helpers and the eight owned private-copy lifetimes. It supplies the following
missing local implication, rather than another compilation of the channel.

Let `B` bound the Hilbert norm of each of the 280 independent input roles.
All norms below are **the maximum of individual register Hilbert norms**, not
the pointwise maximum over addresses and not a concatenated 280-register norm.

| Exact finite-word quantity | Bound | First attaining location |
|---|---:|---|
| Ideal input-to-prefix row norm | **106** | after event 2464, `D0` |
| Accumulation of independent unit absolute defects at every update | **450** | after event 4057, `Q7` |
| Accumulation with scalar-add weight `1+abs(a)`, other update weights 1 | **668** | after event 4057, `Q7` |

Event numbers are zero-based in the immutable predecessor witness. The first
two bounds are sharp under the stated independent-input/defect contracts.
The third is a sharp *weighted independent-defect* coefficient; its use in
state-relative feedback below is sufficient, not an attained rounding error.
The ideal endpoint bound is only 26, and exact dirty restoration does **not**
mean error-free dirty restoration.

## Native and error contracts

The exact source has 4,058 events: 1,410 positive-child transports, 2,624 scalar
additions, eight copies, eight exact owned-zero allocations and eight owned
discards. Put one independent additive defect immediately after each transport,
addition and copy: **4,042 defect sites**. Allocation is exact zero; discard has
no retained output. Intrinsic monomial adapters and address/phase factors are
exact. A defect inside an actual recursive child must first be bounded at that
child's completed output; this package does not analyze its internal algorithm.

This is a **normalized native** contract, not an assumption that an arbitrary
recursive matrix is contractive. The retained physical primitive is

```
C_q = ((1+i)I + (1-i)X_q)/2,       q != 0,
F_r = C_e0 ... C_e(r-1).
```

`X_q` is a self-adjoint involutive permutation. On its `+1/-1` eigenspaces,
`C_q` has eigenvalues `1` and `i`; its inverse has eigenvalues `1` and `-i`. Hence both
have Hilbert operator norm exactly one. The canonical charts and each native
recipe consist of these normalized factors, invertible binary address
permutations, translations and diagonal Gaussian unit phases. They, and all
of their exact factor prefixes, are unitary. The checker validates their actual
gate domains and binds all **740 transport recipes / 1,410 occurrences** and
**208 monomial adapters** to the source word. It compares signed Pauli actions,
exact scalar phase and **948 normalized Gaussian columns**, using the pinned
independent interpreter, not the Clifford compiler.

These checks establish the concrete operator normalization being used. They
do not prove a numerical implementation of a child meets the error contract.
The normalization control rejects omitting the `1/2`. A separate exact example
`C_1(e_0+i e_1)=(1+i)e_0` shows why these operators are **not** contractions in
the addresswise maximum norm. A phase-only change preserves norms but fails
exact operator equality; a norm estimate cannot authenticate phases.

## Proof of the precision implication

### 1. Frame conjugation reduces defects to the literal scalar word

At a source instruction cut, write the physical value of register `r` as
`Gamma_(W_r) z_r`, where `Gamma_(W_r)` is its actual canonical unitary chart.
The native transport checks give exactly
`Gamma_new Gamma_old^-1`; a transport changes the chart, not the logical row.
An addition uses a common chart and performs `z_dst += a z_src`. A private
copy creates a new logical row from its source; its eight different lifetimes
are never identified. The pinned exact endpoint map is independently checked
against the E8 roots:

```
X_s -> X_s,
Y_t -> Y_t + sum_s <r_t,r_s> X_s/2,
all 72 dirty helpers -> their own arbitrary initial values.
```

For a physical additive error `e_j` after event `j`, define
`eta_j = Gamma_(W_after_j)^-1 e_j`. Unitarity gives
`||eta_j||_2 = ||e_j||_2`. Linearity then gives, at **every** subsequent cut,

```
z_r = sum_s A_(r,s) z_s_initial + sum_j c_(r,j) eta_j.
```

The coefficients are the exact rational rows of the literal scalar program.
They retain signs until each row norm is evaluated. A discard removes its
private current row, but not any error already propagated from that private
row to a delivery or target register. An unrelated later allocation gets fresh
error symbols. No dirty input is assumed zero.

### 2. Exact norms, sharpness and finite coverage

For independent input vectors bounded by `B`, the first sum has norm at most
`B sum_s |A_(r,s)|`. For independent error vectors bounded by `delta_j`, the
second has norm at most `sum_j |c_(r,j)| delta_j`. Both inequalities are sharp
for a fixed row: choose any unit vector `v` and choose each logical input/error
as the sign of its row coefficient times `v` and the permitted magnitude.
Use `Gamma_(W_after_j)` to turn that logical defect into a physical defect of
the same norm. Thus the sharpness assertion is about independent arbitrary
additive vector defects, **not** the correlated errors of a rounding algorithm.

The exact forward replay maintains all input and error symbols after every
update. Initial, zero and discard boundaries cannot increase these maxima;
therefore the 4,042 changed-register rows cover all 4,059 instruction boundaries
including the initial boundary, and every live role at each boundary. Complete
coefficient and norm streams are hashed in `RESULT.json`, not sampled. A reverse
adjoint recurrence, implemented separately, agrees on all **62,867 nonzero
signed endpoint-response coefficients** and on the entire arbitrary-input map.
Constructive forward executions attain the three displayed maxima.

The complete endpoint row table is in [RESULT.json](RESULT.json):

| Final role class | Native defects only | Scalar defects only | Copy defects only | All unit absolute defects | Weighted defects |
|---|---:|---:|---:|---:|---:|
| 104 sources | 7 | 0 | 0 | 7 | 7 |
| 104 targets | 711/4 | 110 | 3/2 | 1153/4 | 1847/4 |
| 72 dirty helpers | 336 | 114 | 1 | 450 | 668 |

Column maxima can have different attaining roles; do not add column maxima to
claim an exact joint maximum. The two rightmost columns are calculated directly
from each complete row. For equal absolute defect bound `delta`, every live
role at every boundary has error at most **450 delta**, sharply. In particular,
`delta <= B 2^(-b-9)` is sufficient for error at most `B 2^-b` everywhere.

There is a concrete endpoint/interior distinction even with scalar arithmetic
exact: native-only defects have sharp **all-cut coefficient 356**, at event
3962 in `Q6`, versus final all-role coefficient **336**. Thus an endpoint-only
native sensitivity understates the interior error required by feedback.

### 3. State-relative errors require feedback, not only endpoint sensitivity

Suppose a common `u >= 0` satisfies the following local hypotheses on the
**actual perturbed operands**, with exact dyadic scalar coefficients:

- transport output defect: at most `u ||actual input||_2`;
- copy output defect: at most `u ||actual source||_2`;
- `dst += a src` defect: at most
  `u (||actual dst before||_2 + |a| ||actual src before||_2)`.

Let `M` be the maximum actual register norm across all instruction boundaries.
The event error bounds are at most `u M w_j`, with `w_j=1+|a|` for additions
and `w_j=1` otherwise. The exact weighted all-cut coefficient 668 gives

```
M <= 106 B + 668 u M.
```

For `668 u < 1`, this proves the finite-word guard

```
M <= 106 B / (1 - 668 u),
max_boundary_error <= 106 * 668 * u * B / (1 - 668 u).
```

There is no unproved bootstrap: the finite execution defines `M`, the
instruction error premises hold at those actual operands, and the inequality
can be rearranged under the explicit strict guard. For a particular final
role replace the numerator's `668` by that role's weighted coefficient, while
keeping **668 in the denominator**. In particular the target numerator is
`106*(1847/4)u B`, but dirty helpers still require `106*668u B`.

For every integer `b >= 0`, **`u <= 2^(-b-17)` suffices** for all-role error
`<= B 2^-b`. Indeed, `668(106*2^b+1) <= 2^(b+17)` since
`106*668=70,808` and `70,808+668 < 131,072`. Sixteen uniform guard bits do not
satisfy this particular all-role sufficient bound even in the limit:
`70,808 > 65,536`. This does **not** establish minimal numerical precision.
Target-only accuracy can use a smaller numerator, but must not be substituted
for arbitrary-dirty restoration or all-cut stability.

The contract is dimension independent once unitary charts and the identical
scalar word are available. Only the concrete nine-coordinate/512-address native
realization is source-checked here. No physical all-size lift follows merely
from the abstract Hilbert-space argument.

## Accounting, scope and predecessors

The local paid profile is unchanged:
`1074 H1 + 58 H2 + 86 H3 + 104 H4 + 48 H5 + 24 H6 + 8 H7 + 8 H8`,
rank mass **2368 = 2312 boundary coverage + COPY56**. No new primitive is
inserted, and no recursive precision charge is removed. Correction, global
idle/owner costs, actual rounded child contracts and all-size/tape admission
are not supplied, so there is no completed supplier moment or κ claim.

[PR1972](https://github.com/CrocSwap/integer-mult-bounds/pull/1972), head
`fd82d172f46933fd253c2c6de4bd5eaff5429cfd`, supplies the entire scalar/frame
channel. PR1991, reviewed at `6e222517e182e98499239bc9a4009f540e1c5520`,
supplies the concrete native recipes and explicitly leaves recursive precision
open. This contribution supplies the **finite local error-transfer premise**,
not the complete recursive-precision obligation. The same channel and all
predecessor attribution are retained unchanged.

This is distinct from [PR2067](https://github.com/CrocSwap/integer-mult-bounds/pull/2067):
that result proves an all-size endpoint recurrence for complete PR628 balanced
word leaves. Here the object is the actual 4,058-event P104 word; native
normalization, every instruction cut, private lifetimes and source/helper/target
error distinctions are essential. The selected1094 wire-prefix and dirty-prefix
monomial audits supply useful norm-method precedents on different words; no
constant or proof from those words is transplanted. Active terminal correction
work in [Discussion2080](https://github.com/CrocSwap/integer-mult-bounds/discussions/2080)
is separate and not consumed or certified here.

## Reproduce

Standard-library CPython 3.12, from the repository root:

```sh
uv run --python 3.12 --no-project python -I -O -B research/p104-native-precision/verify.py
uv run --python 3.12 --no-project python -I -O -B research/p104-native-precision/test_verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/p104-native-precision
```

Default replay is read-only. `verify.py --write /new/path.json` writes a new
receipt exclusively; canonical parsed payloads, not compression headers, are
compared. All external bytes are authenticated **before** interpreter import.
The registered replay includes native/phase/normalization checks, arbitrary-input
and reverse sensitivity identities, constructive sharpness, semantic controls,
a dense rational defect execution, individual native-rank/private-lifetime
impulses and an optimized read-only export with a corrupted-source rejection.
No formal kernel, selected cold replay or hosted CI result is claimed.

Observed locally on CPython 3.12/macOS arm64: the scientific receipt generation
passed, followed by the complete registered replay (13.25 seconds):

```text
PASS_P104_NATIVE_PRECISION input=106 absolute=450 relative=668 guard_bits=17 native_recipes=740 endpoint_coefficients=62867 controls=13 no_new_kappa
PASS_P104_NATIVE_PRECISION_TESTS dense_defects=4042 independent_impulses=18 source_drift=reject read_only_optimized_export=pass
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-native-precision outcome=completed
```

## Provenance and freshness

Scientific base: `564148b82ae9df72163f22106f15e73efca8aff2`; priority revision 4.
Independent chooser nonce: `1be10fd8d275206692a433be1dacd810`, complex-mechanisms.
[SELECTION.json](SELECTION.json) preserves the complete sole draw.
[TASK.json](TASK.json) explicitly records the changed card obligation and limits;
[SOURCES.json](SOURCES.json) pins each consumed source. The latest inspected
canonical checkpoint `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` changes guidance
only; catalogue and scientific inputs are unchanged. The scientific base stays
immutable.

The shared refreshed search at 2026-10-14 19:02:09Z covered 353 open PRs including
drafts, 738 discussion/comment/reply records and 1,536 local records, with
complete remote pagination. Targeted live PR1991/PR2067 and Discussion2080,
and local norm predecessors, were read. These metadata searches do not cover
all code or the literature and do not prove novelty. No separate discussion
post or comment was made for this investigation; its claim/result are in the
package and the self-contained PR.

## Open next questions

1. **Bound an actual rounded recursive child.** The present theorem consumes
   a completed-child Hilbert-norm defect bound. Bind the selected primitive's
   precision convention to that norm and exercise its rounded implementation
   at P104's ranks. The unresolved blocker is that implementation/interface,
   not another scalar norm estimate.
2. **Compose a corrected P104 word.** Once an exact chronological `I-G/2` word
   is available, bind its source and replay the combined prefix/error maps.
   This is necessary because the current channel is only `G/2`; a separate
   correction's endpoint error bound cannot silently replace combined
   interior and dirty-restoration bounds.
3. **Global physical hosting and precision.** Transport actual owner-family
   magnitude bounds through completed calls, keeping helper residual errors.
   A globally admitted corrected owner schedule and its all-size precision/tape
   contracts are still missing.

## Credit

Prepared by Adam Gall with substantial OpenAI Codex assistance in research,
proof, code, verification and writing. No independent human or formal review
is claimed. Rohan Arun/PR1972 supplies the scalar word; Chafik Boukhalfa/PR1991
supplies its native realization; Adam Gall/PR1940 supplies the schedule; Josie
Elliston/PR1071 and Ali Romman/PR1125 supply the fixture/delivery lineage.
The exact compiler descends from icekylinx's Clifford work; the retained
independent Gaussian interpreter is Ali Romman's PR1862/PR1931 lineage.
Existing notices remain in the unchanged predecessor package. New material
is Apache-2.0 under the repository license.

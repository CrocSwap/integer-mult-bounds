# A native counterexample to the projected centre quarter-factor identity

**Scoped native counterexample; no new supplier or κ.** This answers open
question 3 of https://github.com/CrocSwap/integer-mult-bounds/pull/2199 at
`30ec048eedcaca970f94bbec0fdd3c52eacf9fdc`: its scalar D-only relationship
`backward1 centre = forward0 centre / 4` does **not** lift to the actual
cover-owner action for selected replica 0, calls 0 and 4.

There is a stronger obstruction than a different carrier frame. One explicit
input difference makes **all eight first-call centre fields zero at every
cover owner**, both before and after transport. The later channel-0 query is
nevertheless `1/4` at the identity owner. Thus no linear decoder of those
first eight saved fields alone, even with arbitrary owner mixing and native
transport, can recover this later query for arbitrary inputs. Additional
source observations or a changed call/schedule contract remain possible.
This is a query-recovery obstruction, not a bound on the information needed
for a different final-output contract or on the number of recursive calls.

## Exact input and proof

The selected global family IDs for replica 0 are `D_p=p`, `T_p=112+p`.
Let `g=rho_1(0)`, the actual stage-1 route for port 0 in the pinned phase file.
At physical cover owner `g`, take the following initial D-field difference:

```text
port       0   1   6   7
value     +1  -1  -1  -1
```

Each displayed value is constant on **every physical payload address**
(all 73 axes and any tensor/spectator factors). All other cover owners and
families have zero difference. This is one finite cover-supported input
function, not one address-basis column. In two executions, all initial
target and helper contents are the same arbitrary values. Zero difference
on those fields does not impose a clean-workspace construction premise.
Every operation is linear, including private clearing, so this difference
calculation applies to any shared baseline dirt.

1. **The first query cancels.** Independently reconstructing the forward
   source map gives these four columns of its eight-row D block `R`:

   ```text
              ports 0, 1, 6, 7
   row 0        1  0  0  1
   row 1        1  1  1 -1
   row 2        1  1  1 -1
   row 3        1  0  0  1
   row 4        0 -1  1  0
   row 5        0  0  0  0
   row 6        0  0  0  0
   row 7        0 -1  1  0
   ```

   Their product with `(1,-1,-1,-1)` is zero. Scalar cancellation is only
   the proposal: the literal phase-bearing forward word is then executed
   independently, checking all eight actual private inputs and outputs are
   zero across the 512 local addresses. Stage 0 has identity data routes and
   zero entry/exit translations. Only common cover `g` has a nonzero input;
   every other invocation has zero difference. Its entire centre transcript
   therefore vanishes on the full cover, not just at one owner.

2. **The complete first call is retained.** The same literal replay checks
   every one of its 704 ordinary endpoints: D retains the four constants,
   T acquires the same four constants, and every helper difference is zero.
   Private outputs are zero. No centre cut is spliced into an assumed
   endpoint. The first five schedule events are precisely calls 0 through 4;
   calls 1, 2 and 3 touch none of these eight live D/T families. There is no
   intervening bridge or idle event. Their omission from the computation is
   justified by those checked supports, not by a calls-only approximation.

3. **Stage 1 separates the cancelling ports.** Its data view at common
   owner `d` reads physical cover `d*rho_1(p)`. This is a change of cover
   owner, not a payload permutation. From the actual port record, let
   `b_0,...,b_7` be the eight chart columns and `e_9,...,e_16` the first
   external block. Then

   ```text
   s_i = b_i XOR e_(9+i)
   rho_1(p) x = x XOR sum_i ((s_i dot x) mod 2) s_i.
   ```

   The verifier checks orthogonality, both involution orders, the fixed port
   normal, and the actual stage-0/1 entry and exit translation formulas.
   For port 0 the chart columns are `(13,14,7,16,32,64,128,256)` and normal
   is 11. The four active port routes are distinct and `g != I`.
   Consequently B1 at common owner `I` sees the live values only at port 0:
   `D_0=T_0=1`. The other three cancelling ports are at the wrong physical
   cover owners. Hosted helper families are distinct from these data families.
   The entry translations fix this payload-constant input. The common
   exterior frame is a product of native translation roots, which also fixes
   constants; the remaining nine-axis action is executed literally.

4. **The later native query is nonzero.** The complete backward word gives
   `C_0 = (1/4) * constant1` immediately before its transport. After transport,
   its value at local address 0 is `i/4`. Applying the inverse canonical
   carrier frame returns the same nonzero `1/4`. Both orientations contain
   24,767 literal events; all native children, endpoint/residual adapters,
   scalar signs and private clears are executed on this input. The complete
   backward endpoint is checked too. A raw carrier convention cannot explain
   the discrepancy: zero stays zero under every invertible frame transport.

The zero input and this input have the same first-query observations but
different later queries. Therefore a decoder using those observations alone
cannot work on both. No rank extrapolation or physical tariff is needed.

### Why the local replay applies at a nonidentity cover owner

Use the retained local-view semantics, including each role's chart and
spectator-coordinate identification. At common owner `d`, let `E_(d,r)`
embed a nine-coordinate representative for role `r`, tensored with constant
exterior factors, into that role's physical view. An embedded native event
intertwines the coordinate representations:

```text
G_native E_(d,r) = E_(d,r') G_local.
```

For multi-register events such as ADD and COPY, use the direct-sum embeddings
of all involved input and output roles in this identity.

For translation roots this follows by sending each local axis `a` to its
physical axis `d*a`; monomial and coordinate-permutation records are pulled
through the same coordinate identification. Equal-frame scalar operations
use the same view, so their embeddings commute with addition and scaling.
Composing events cancels the intervening identifications. The local replay
therefore gives the physical private values at owner `g` too. In particular,
zero local centre vectors give zero entire embedded fields, and the checked
constant endpoints give the stated physical endpoints. **Intermediate states
at `g` need not be constant.** Constant preservation alone would not justify
this lift; it is used only at the initial, completed and exterior factors.
This argument uses the declared native local-view embedding, not an
independently rebuilt physical stream/address compiler.

## Replay, controls and source binding

Python 3.12, standard library, repository root:

```sh
python3.12 -B scripts/research_package.py --package research/selected-centre-quarter-native --check-only
python3.12 -B scripts/research_package.py --package research/selected-centre-quarter-native
python3.12 -I -O -B research/selected-centre-quarter-native/verify.py
```

Expected status:

```text
PASS_SELECTED_CENTRE_QUARTER_NATIVE_COUNTEREXAMPLE first_transcript=0 later_query=1/4 no_new_kappa
```

[RESULT.json](RESULT.json) records the witness, all 73 columns of `g`, route
digests, native amplitudes and source-member hashes. Acceptance recomputes the
matrices and literal statevectors; a digest is not substituted for equality.
The unpacked Gaussian-dyadic interpreter uses integer real/imaginary arrays
with a shared power-of-two denominator. No floating-point comparison is used.
The pinned exact Clifford kernel supplies only canonical-frame circuits for
inverse normalization. It does not execute the two literal words for us.

Positive controls reproduce the scalar quarter-factor on **all 8×112 D
coefficients**, and show the same four-port cancellation remains valid when
the input is made cover-invariant. Four native controls also remove the
signal by putting the input at the wrong cover owner, reject a backward
transport global-phase change, and reject a changed gather coefficient.
Seven elementary controls check hand-computed root amplitudes, inverse and
square, constant preservation, dyadic addition, owner involution, and
type-preserving canonical JSON. Two CLI tests run under `-I -O -B`, including
fresh witness generation and corrupted/wrong-typed receipt rejection.
`--write NEW_PATH` refuses an existing file; ordinary verification is read-only.

Live inputs and their exact Git blobs/SHA256 values are in
[SOURCES.json](SOURCES.json). Six unique, full-path archive members are
authenticated before decoding; no archive is extracted onto disk. The actual
selected archive is `f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`.
There is no runtime network, pending-PR import, dependency installation or
frozen input modification.

A separate read-only AI review independently reconstructed the four source
columns and all four 73-column routes from the raw archive. Its backward
pre-query causal-slice replay obtained `1/4`; a separate packed evaluator
checked the used centre transport and all eight active endpoint adapters on
all 512 columns, including global phase. It found no code/math defect and
requested the coordinate-covariance clarification above. This is scoped AI
corroboration, not independent human or formal-kernel review.

## Assignment, cost and limits

Track `recursive-interfaces`, card `centre-path-sharing`, nonce
`56c03933c3a237bef454593979c3b883`, catalogue key `184695337cedab03152e`,
priority revision 4, base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
The task is refined to one necessary query-reuse implication, not a sharing
construction. The user approved this pair before implementation. The local
pre-computation card and public claim precede the experiment:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1884#discussioncomment-18942993.
Metadata and open questions are in [TASK.json](TASK.json).

The prescribed packing-ceiling replay and ideal lever table were run:
baseline `a_cap≈0.001690054109089`, ideal two-call sharing about 1.90×.
These are prior planning numbers, not this result. No centre COPY, child or
restoration charge is removed, and no changed moment or κ is proposed.
An eventual repair must still price storage, additional information,
transport, hosting, restoration, precision and all other construction costs.
The unchanged selected complex budget remains binding.

This falsifies an all-input native identity with a valid input in a restricted
subspace. It does not infer general operator equality from that subspace,
compute the full native rank, enumerate other pairs or channels, exclude
every form of centre sharing, or apply the separate-panel transcript lemma
to cumulative outputs. There is no supplier adoption, controller rewrite,
full cold replay, Lean execution, complete physical invoice or new κ.
Inherited all-size/compiler, realization, hosting, precision/tape, analytic
and bit H1–H5 obligations remain untouched.

## Open next questions

Can one additional, precisely specified old-chart observation distinguish
this four-port family while still fitting a complete sharing budget? First
apply the proposed observation to the explicit kernel input here. A nonzero
record is necessary, not sufficient: prove the complete ordered recovery map
and price its native access, storage and restoration. No such repair is supplied.

For a final-output sharing contract, what is the fixed-dirt demanded output
map after overlapping scatters and intervening events? This result concerns
recovery of the later internal query, not that output quotient. Start from
PR2199 open question 2 and declare the physical observation cut; the bridge,
idle and panel-overlap semantics are still required.

## Credit

Sagar Thakrar's PR2199 supplied the scalar identity and explicit native-lift
question. Adam Gall's https://github.com/CrocSwap/integer-mult-bounds/pull/1918
supplied the composed scalar model and transcript context.
commdata2338's https://github.com/CrocSwap/integer-mult-bounds/pull/2048 supplied the separate disjoint-forward-pair
native lift and the unpacked statevector approach; this is the same-replica
mixed-orientation follow-up, not another check of its pair. Sagar Thakrar's
`frontier1094-recipes-exact-seed76` supplies the exact Clifford kernel and
operator conventions. The retained bridge/cover-action proofs supply the
distinction between owner routing and payload permutations. New code is an
independent implementation of the stated literal format, not an independent
derivation of the source semantics.

Retain Rohan Arun's PR1094 packing, Jeremy Kothe's local-word lineage, Hao
Yan's controller, icekylinx's compiler/emitter and DreamingOfClouds' frame
proof lineage, with all original licenses/notices. Prepared by **Aaron Wang /
navinor, with help from chatgpt**, including research, implementation and
writing. New work Apache-2.0. No independent human or formal-kernel review is
claimed.

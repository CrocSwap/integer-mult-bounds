# PR2226 low lenders: exact cleanup and availability certificate

**Finite certificate and scoped proof; no new supplier or κ.** For the
32 low lenders in Cinna Davis's [PR2226](https://github.com/CrocSwap/integer-mult-bounds/pull/2226),
all 48 retained early-tail operations are necessary to restore their original
arbitrary dirty inputs. The fixed cleanup consists of 32 subtractions and
16 negations. Its 32 distinct sources each require a rank-one promotion from
their last rank-three read to the rank-four cleanup frame. Those promotions
are already part of the predecessor's bill; this does not add 32 new charges.

For **exactly k restored lender rows**, the minimum retained-operation count is

\[
 C(k)=k+\max(0,k-16),\qquad 0\leq k\leq32.
\]

This is a minimum within the **fixed 48-operation alphabet**, with the
subtraction before negation on a shared destination. It is not a minimum over
arbitrary circuits, changed coefficients, signed loan references, other
lenders, new observations or rewritten compensation. Partial subsets attain
the stated *row-restoration* contract; they are not asserted to form valid
partial suppliers or to preserve the other 48 loans.

The second result is an exact interval certificate for retiming the **full**
cleanup while retaining the word's monotone frames and withdrawing each
physical operand at its recorded handoff. Five subtractions have a stricter
deadline than the low lender's handoff because their source is borrowed first.
The original earliest schedule and the latest permitted schedule have identical
frame endpoints and identical frame invoices through all 1,846 B events and
all 80 handoffs. Exact free-operator replay also gives identical complete rows
on all 624 arbitrary inputs, with `Y+=X` at the B endpoint. No defect in PR2226's original early schedule was found.

## Reproduce and evidence

Use Python 3.12 and its standard library; no numerical packages or network
access are needed. From the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/anticipatory-lender-cleanup --check-only
python3 -I -B scripts/research_package.py --package research/anticipatory-lender-cleanup
python3 -I -O -B research/anticipatory-lender-cleanup/verify.py
```

Expected direct output:

```text
PASS_ANTICIPATORY_LENDER_CLEANUP lenders=32 subsets=281474976710656 tail_gates=48 rank1=32 source_deadlines=5 no_new_kappa
```

The direct checker takes approximately two seconds on a CPU. It writes no files
unless `--record NEW_PATH` is explicitly requested; that path must not exist.
No predecessor checker is imported. [RESULT.json](RESULT.json) contains:

- All 64 relevant lender/source rows, independently reconstructed by forward
  propagation on the 512 remaining non-target inputs and backward functional
  propagation through the original 704-input prefix. The 112 Y inputs cannot
  affect these non-target rows. The full borrowed word has 624 inputs.
- All 96 local subset outcomes, whose product covers **2^48** global subsets,
  the complete 425-entry cost/restored-row distribution, and all 33 minima.
- Every actual last-read event, both endpoint frame bases, the 32 release
  intervals, five source-limited deadlines, and the number of complete cut
  assignments under the convention below.
- Chronological frame traces for both extreme schedules, including the actual
  virtual-to-physical alias map and all 80 equal-dimensional handoffs. Both
  complete scalar prefixes are also replayed over noncommuting loan operators;
  all 624 output rows agree, all 32 low rows equal their original dirt at
  handoff, and the 112 Y outputs equal `Y+X`.
- 136 rejecting semantic cases: 48 single omissions, 16 reversed subtraction/
  negation pairs, 32 early cuts, five missed source withdrawals, 32
  equal-rank wrong-subspace cases, one input-label mutation, and missing/wrong-sign
  initial compensation. The 37 cut
  mutations also fail the separate raw chronological frame executor.
  Both extreme schedules and 32 equivalent frame-basis changes pass.

`-O` does not disable any check. Source authentication checks SHA256 and Git
blob digests, including the decompressed word payload. Expected receipts use
typed canonical JSON, and duplicate JSON keys are rejected.

## Exact sources and distinction from earlier work

The scientific/task-selection base is main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4. The only
mathematical data dependency is PR2226 head
`dacaf3d81f1936bb55b8454b1244e5d014272754`. Its word, witness, block certificate
and notice are retained byte-for-byte in `inputs/`; [SOURCE-PINS.json](SOURCE-PINS.json)
records original paths, commit, Git blobs and SHA256 hashes. The selected
word and block certificate descend from Ali Romman's
`complex-block-rank-optimum` at `697b00e5d36297563c22aac080dd5dee398c2624`.

PR2226 already provides the 80-alias construction, the 48 early-tail gates,
positive lender-restoration checks, and full logical cleanup. This package
adds the **all-subset necessity proof, sharp partial row-restoration tradeoff,
and the exact pre-handoff retiming intervals**. Its positive checks independently
bind those statements to the original data; the original gate count, `Y+=X`
endpoint and construction are not claimed as new.
The new complete-prefix comparison checks their preservation under the
certified latest cleanup retiming.

[PR2339](https://github.com/CrocSwap/integer-mult-bounds/pull/2339) and this
account's [PR2394](https://github.com/CrocSwap/integer-mult-bounds/pull/2394)
concern later T74 words and native initial compensation. They are context,
not inputs or a transfer of this certificate to those words.
[PR2573](https://github.com/CrocSwap/integer-mult-bounds/pull/2573) excludes
additional loans in a different ordinary retired-lender class; this result
fixes PR2226's low-lender cleanup. Source-partner substitutions and owner
repacking in PR2530/2571/2575/2588 are also different objects.

The task card is [TASK.json](TASK.json): `complex-new-helper-inventory`,
scope key `f3b0895a4f9f1cc62e75`, changed from interface synthesis to this
necessary boundary check. It does not meet or claim the original card's
new-construction/packing-improvement acceptance gate. The selected result and
all predecessor packages remain unchanged. The claim is in
[discussion #2615](https://github.com/CrocSwap/integer-mult-bounds/discussions/2615).

The final refresh found main `b4560d9e7216f72b73c5aa940ac099c05e33ccf9` and
priority revision 5. Its new family-expansion guidance was read; the selected
record and PR2226 source head are unchanged. This package retains historical
revision-4 task provenance and is integrated on the refreshed main. The declared
milestone is **audit**. Decision: conclude this bounded audit, with no dependent
construction expansion inferred from the local result. Native restoration,
consumer/hosting and all-size costs remain unverified here; unknown costs are
not zero. TASK.json records the refresh and obligation ledger.

## Proof of the subset classification

Write `u_d` for lender d's own original arbitrary input and `v_s` for the
current value of its cleanup source s. Direct rational replay gives exactly
two component types:

| Number of lenders | Before cleanup | Retained operations | After both/all operations |
| --- | --- | --- | --- |
| 16 | `u_d + v_s` | `d -= s` | `u_d` |
| 16 | `-u_d + v_s` | `d -= s; d = -d` | `u_d` |

Each `v_s` is a nonzero rational combination of original X inputs, independent
of `u_d`. The coefficients and original input labels are recorded for every
component. No ordinary changed-B instruction writes any of these 64 roles
before its physical withdrawal. All 32 cleanup destinations differ, all
32 sources differ, and no cleanup source is a cleanup destination. The
source *values* need not be mutually independent: disjoint writes and
independence from each corresponding `u_d` suffice.

For a one-operation component, omission leaves `u_d+v_s`, which is not the
required identity for arbitrary inputs. For a two-operation component, the
four retained-order subsets give

\[
 -u_d+v_s,\quad -u_d,\quad u_d-v_s,\quad u_d.
\]

Only the complete pair restores the input. Reversing the two operations gives
`u_d-2v_s`, also incorrect. No omissions in another component can change these
rows, because none of its writes targets d or s. This proves the classification
for all 2^48 subsets without treating successful single-omission tests as an
exhaustive proof.

If x counts retained operations and y counts restored lender rows, the exact
subset enumerator is

\[
 (1+xy)^{16}(1+2x+x^2y)^{16}.
\]

To restore k rows, use at most the 16 one-operation components first. Every
additional restored row requires two operations. This proves the lower bound
`C(k)`, and choosing those complete components attains it. In particular, the
only subset restoring all 32 rows is the full 48-operation set.

## Proof of the frame and deadline certificate

A B cut c means **before B[c]**. All cleanup assigned to c executes first,
then all handoffs at c, then deferred/rewritten ordinary instructions and
B[c]. Within one cleanup component, subtraction precedes negation, including
when they share a cut. Different components commute. Cuts and operation
indices are zero-based.

For each component the lender already has rank-four frame U and has no
ordinary B use. Its source follows a retained nested frame path ending with a
rank-three read in V strictly contained in U. The actual last-read indices
range from 719 to 855. The source row is unchanged by B before borrowing.
The cleanup subtraction requires both operands in U.

Let L be one plus that last-read index. Any subtraction before cut L promotes
its source to U before the retained rank-three read. A monotone continuation
would then require `U ⊆ V`, which is false. Thus L is a **necessary** release
cut, even though the scalar subtraction would commute with ordinary reads.
At L the source can make the one-dimensional transition `V ⊂ U`; the lender
requires no promotion. There are 32 distinct sources, so the full cleanup
contains exactly 32 such rank-one transitions. Delaying the gates does not
merge them or remove their cost.

Let H_d be the lender's handoff cut and H_s the source's handoff cut, with
`H_s = infinity` for a source not borrowed. The retained operand-identity
contract withdraws a field at its handoff. Therefore the subtraction can be
placed at precisely

\[
 L\leq a\leq\min(H_d,H_s).
\]

For a two-operation component, negation can then be placed at any cut

\[
 a\leq b\leq H_d.
\]

These are sufficient as well: there is no intervening write to either
unwithdrawn operand, all ordinary source reads are finished, and the lender
stays in U until its handoff. Once the subtraction has read the source,
negation no longer needs that source. The completed lender is `u_d` at
handoff. The changed source's frame is U in time for its own fixed handoff.
All subsequent source-bound frame transitions are identical. This is a proof
for every cut assignment, with the two extreme executions as source-bound
controls; it is not an inference from testing only two schedules.

Five additions have `H_s < H_d`:

| Lender d | Source s | Earliest addition L | Last addition H_s | Lender handoff H_d |
| --- | --- | --- | --- | --- |
| 277 | 281 | 720 | 1142 | 1150 |
| 282 | 285 | 722 | 1142 | 1150 |
| 346 | 349 | 801 | 1054 | 1070 |
| 357 | 361 | 817 | 1054 | 1142 |
| 362 | 365 | 819 | 1054 | 1070 |

A scheduler checking only the lender's deadline would permit a stale source
read in these five cases. The original schedule satisfies all five bounds.
The remaining 27 addition deadlines equal the lender deadline; all component
rows and intervals are in RESULT.json.

For one-operation components the number of cut assignments is `U-L+1`, where
`U=min(H_d,H_s)`. For two-operation components it is
`sum(a=L..U) (H_d-a+1)`. Their product, computed exactly in the receipt, counts
complete cut assignments with canonical commuting order at a shared cut; it
does not count arbitrary micro-orderings. The frame invoice through the end
of B, including COPY but **before final restoration**, is
`{1:2010,2:347,3:334,4:128,5:26,8:8}` for both extreme schedules. This prefix
profile must not be substituted for PR2226's complete local profile.

## Limits

The result fixes the source word, 48 cleanup gates and coefficients, original
input labels, rank-four cleanup frames, monotone ordinary frame paths, handoff
cuts and the requirement to restore the original signed dirty value. No new
read after physical withdrawal is allowed. More general reference changes,
nonmonotone adapters, alternative source combinations, copied observations,
changed compensation or other lenders are outside the theorem.

The complete B prefix is checked, including `Y+=X`. This does not check final
non-target restoration, exact Gaussian phases, inverse-transpose execution, private inverse-cleanup buffers, full native
lowering, global ownership, precision/tape, all-size recursion or the outer
transfer. The original positive construction remains credited to PR2226;
its full verifier and the selected supplier cold replay were not rerun here.
No new paid-profile saving or κ follows from this scalar gate-count result.

## Open next questions

1. **Escape the fixed source/frame premise.** For one recorded component,
   propose a phase-correct alternative which avoids the rank-four source
   visit, then charge every new read, adapter and restoration operation. This
   could improve the local bill; no such alternative is supplied here.
2. **Bind a complete native word.** Join these intervals with an explicitly
   source-matched native initial-prefix implementation, then check both
   orientations and full cleanup. This account's PR2394 is a starting point
   on different successor words, so source comparison is required. Global
   hosting and a favorable complete bill remain blockers.

Structured next questions are also in TASK.json.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Cinna Davis (@1337isnot1337), PR2226: anticipatory borrowing, the fixed low-lender
construction, compensation and cleanup witness. Ali Romman: fixed-block
extraction and certificate. Thomas DiFiore: block discovery. Jeremy Kothe,
Rohan Arun, Hao Yan, Chafik Boukhalfa, icekylinx, Jonathan Capalbo and the
selected PR1042/1094 provider/frame/controller lineage retain credit.
The original [notice](inputs/NOTICE.md) is preserved; its references to the
predecessor's price engine describe that predecessor, not an imported engine.
New proof and checking code are Apache-2.0. OpenAI Codex performed the
derivation, implementation, checking and writing. No independent human
review, maintainer adoption or complete formal proof is claimed.

## What changed and why

The physical caller work already supports fixed-bank recursion. Binding that
work to the selected finite compiler still requires exact runtime child
widths, stopping control and paid remainder handling. This package supplies a
literal control producer for the final rank-one law, backed by a general
rank-profile lemma and source-pinned cutoff/remainder analysis.

The raw mixed-rank BIT law is r_i floor(e/m), not floor(r_i e/m). The selected
finite-precompilation source instead makes every final paid leaf rank one, so
all P child calls have width floor(e/N). The source binding makes this
distinction explicit and retains the supplied root cutoff L.

## Exact result

For fixed N >= 2 and P >= 1, a four-tape finite controller stops below
max(N,L), generates the ordered rank-one calls and emits pre/post hooks for
e mod N. It restores unary descriptors, the cutoff tape and arbitrary
suspended ancestors. Every return, head rewind and hook dispatch is paid.

- Instruction count: 30N+42+P(69+3N), independent of e and L.
- Complete control time: at most 200(P+1) sum_v e_v.
- Retained backing: at most K0+(4+N/(N-1))e_root+8; K0 includes the entire
  supplied cutoff and preexisting historical backing.
- Cutoff comparison: at most 11 min(e,L)+10, including both head returns.
- Each remainder scan: 6e+7; both scans: 12e+14. B0/A0 explicitly skip
  remainder payload actions, with finite dispatch still paid.

The reusable three-tape lemma supports arbitrary fixed 1 <= r_i < m and
children floor(r_i f/m), with complete time 100(s+1) sum_v f_v and retained
backing K0+(3+1/(1-rho))f_root+6. It requires no supplied tree or depth.

The all-width results are proved by explicit loop and stack invariants.
The conditional node-volume corollary additionally assumes complete-root
factors/row stock and paid payload consumers. It does not establish those
interfaces.

## Novelty and predecessors

#5134 and #5158 already provide literal complete-row parking and dyadic
fixed-bank recursion. #6719 provides the richer supplied-depth delayed-cover
binary-root/grant/payload program; #6722 reviews a particular join. They
retain credit. The present delta is online rank-dependent shape control and
its exact final rank-one cutoff/remainder connection, with no raw mixed-floor
substitution. Classical finite remainder transducers and depth-first stacks
are standard techniques.

Pending #7150 and #7151 cover primitive microcontrol and stratified retained
backing. Their inspected heads are pinned as complementary work, not merged
dependencies. The scientific base is
`e54523517d0f03e58352e647c403a5af3e525a57`; `SOURCES.json` pins the actual
batched-row notes, finite-precompilation source, #7000 review and predecessor
proofs by commit/blob/hash.

## Reproduction and checks

```sh
python3 -B research/selected-rank-control/verify_all.py
```

Expected: `PASS_SELECTED_RANK_CONTROL_PACKAGE`. This runs each bounded suite
normally and under `-O`, requiring byte-identical receipts.

- General: 896 cases, 13,540 nodes, 3,469,732 transitions, nine separate dense
  CPU cases and ten negative controls.
- Selected: 2,400 cases, 10,878 nodes, 3,443,893 transitions, eight separate
  dense CPU cases and eight controls.
- Checks observe actual unary widths as well as labels; they cover cutoff
  equality, restored heads/cells, ancestor locality, historical backing,
  remainder identity/omission, wrong return tags and undercharged execution.

Proofs, finite receipts and validation metadata are included. Finite checks
corroborate universal written proofs; neither interpreter is a formal kernel.
Normal execution and optimized execution are regression checks, not separate
mathematical proofs.


A separate reviewer read both proofs and executed a code-disjoint dense CPU
against an explicit address-tree oracle. It passed 125 cases, 837 nodes,
3,654 events and 488,423 transitions, checking actual widths, full ancestor
stacks, hostile exterior cells and 556 exact remainder-scan charges. Three
semantic mutants were rejected. From this directory run
`python3 -I -W error -B independent_check.py .`; see REVIEW.md and
evidence/independent.json for the complete independent receipt.

## Limitations and kappa status

**No new kappa. All five selected foundational assumptions remain.** The
accepted conditional kappa stays 0.00363005817. This is a control/interface
lemma, not a complete multiplication implementation or unconditional theorem.

The actual selected final word and its owner manifest are not emitted. The
external width/cutoff adapter, row grants, chronological scalar/frame segments,
both BIT remainder consumers and complete native endpoint contracts remain
open. Generating L=ceil(d^beta) is not free. Consumers must preserve descriptor
tapes and pay their work; complex remainder completion and BIT ungathering are
not supplied by the event producer.

## Attribution

Prepared for @CubeJerry with substantial OpenAI assistance. Credit JoyboyBrian,
thu-nmrc, ToikY, commdata2338, Ali Romman, David Arias and all retained native,
physical and compiler contributors. New material is Apache-2.0. Independent
human review and formal-kernel acceptance are not claimed.

# Arbitrary source masks add no helper deletion to the fixed R439 word

**Scoped negative result; no new kappa.** Allowing an arbitrary XOR of current
source registers at each deleted-helper read leaves only helper **470**, the
source77 boundary already constructed by Ali Romman in
[PR1043](https://github.com/CrocSwap/integer-mult-bounds/pull/1043).
The other **429** non-retained helpers are excluded in the class below.

Hanson Sun's [PR1079](https://github.com/CrocSwap/integer-mult-bounds/pull/1079)
tested replacement by **one** current source per read. This package changes that
hypothesis: each replacement may use any source mask, including the empty mask,
different masks at different reads, and cancellation with existing source
operands. Linear-span certificates cover every mask, without a support-size
cutoff or sampled search. This adds a stronger finite obstruction, not a new
construction or a repetition of the one-source census.

| Classification | Helpers |
|---|---:|
| Retained COPY totals, outside the deletion class | 9 |
| Some read fails even the unrestricted source-span test | 65 |
| All reads pass that test, but fixed frame anchors exclude a read | 364 |
| Necessary-condition survivor, already constructed in PR1043 | 1 |
| Total | 439 |

The complete domain is 430 helpers and 2,102 A/B read occurrences. Of those
reads, 2,037 admit a source mask when frames are ignored; only 90 pass the
relaxed frame-access test. Passing one read does not suffice to delete its
helper. [CERTIFICATE.json](CERTIFICATE.json) supplies one explicit separating
parity functional for each of the 429 excluded helpers.

## Exact class and cost boundary

Fix the PR589 tuned word, whose compressed source SHA256 is
`e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`.
Choose one non-retained helper q. Delete every A/B gate writing q. At each
remaining read of q into destination d, replace q and the gate's existing
source-register operands by an arbitrary XOR mask of current source registers.
The other helper operands retain their original coefficients. A mask cannot
read d itself. The replacement block writes only d; its donors are unchanged
during the block. It may split the additions across different rational common
frames, with monotonically increasing frames on every register.

Require equality of the destination's **clean-source response at each replaced
gate boundary**. All other surviving A/B gates retain their order, operands and
frames. Keep register start/final frames, retained totals, COPY frames and
scatter fixed. Compensation D may be rebuilt from the dirty-helper response
using frame-zero helper-to-target gates; cleanup C may be rebuilt as the literal
full-frame reverse of the surviving source/helper writes. These are the same
compensation and restoration obligations as the predecessor class.

This permits arbitrarily many source donors. It excludes changing other helper
coefficients, extra scratch registers, simultaneous helper deletion, source
preparation writes, moving a replacement past a fixed gate, and local errors
that cancel only at a later boundary. Those mechanisms are not settled here.

The screen gives the proposal a favorable budget: extra XORs cost nothing in
the relaxation, other helper operands need not satisfy common-frame access,
and different donor accesses need not fit one consistent joint schedule. Even
this relaxation excludes every additional helper. A paid construction is
therefore unnecessary for these exclusions. The sole survivor is predecessor
evidence: this package does not rerun PR1043's hosted invoice, claim its saving
as new, or infer a supplier gain from deleting eight units of local helper rank.

## Why the exclusion covers all masks and rational frames

Let alpha_r(t) in F2^111 be the response of register r to the independent source
inputs immediately before an original A/B gate. Targets and helpers start at
zero for this necessary-condition calculation. They are not assumed clean in a
potential complete construction.

At a q-read into d, let S be the original source-register operands. The required
net source contribution is

`beta(t) = alpha_q(t) XOR (XOR over s in S of alpha_s(t))`.

This normalization matters: substituting a source already in S cancels that
operand. A replacement source mask M preserves the boundary exactly when
`XOR over s in M of alpha_s(t) = beta(t)`. Delete a q-write and nothing else
changes. Substitute a q-read satisfying this equality and every surviving
clean response is unchanged. Induction over the gates therefore justifies using
the original source trajectories for every read, including mutable B sources.
A correct dirty-input construction must pass this clean specialization.

For each q, omit **all q-incident A/B gates** when computing fixed frame anchors,
including writes and replaced reads. Keep the original COPY anchors, start and
final frames. At a changed read let L_r and U_r be the nearest earlier and later
fixed frames of register r. Omitting the other changed reads relaxes timing
constraints rather than assuming their original frames remain fixed.

If source s is read into d at any rational common frame F, monotonicity requires

`L_d <= F <= U_d` and `L_s <= F <= U_s`.

Consequently `L_d <= U_s` and `L_s <= U_d`. Form E from every source s other
than d satisfying these two inclusions. Every physically read donor belongs
to E, even if additions use different frames. Thus every legal replacement
must satisfy

`beta(t) in span_F2 { alpha_s(t) : s in E }`.

We use this only as a necessary condition. Taking the union E may admit donors
that cannot be scheduled together. This cannot create a false exclusion.
Rational inclusions are checked on the actual eight-dimensional source lines;
the argument does not restrict F to the shipped frame catalogue.

An exclusion witness is a set of input coordinates lambda. Its parity pairing
with beta is one and with every eligible source response is zero. It therefore
annihilates every XOR mask while separating beta. For the 65 clean-span
exclusions, the same condition holds for **all** 111 sources, excluding d.
These exact dual certificates establish non-membership, rather than reporting
failure of a mask search.

For example, helper224 at A[486] needs `beta = x1 XOR x106` at receiver608.
The eligible sources are `[4,31,35,37,77,79,106,109]`; lambda is coordinate 1.
Source1 already occupies frame212, spanned by lines `[1,7]`, after A[483].
Receiver608 must later enter frame323 at A[1749], and that frame excludes line7.
The missing x1 contribution cannot be manufactured by combining the eligible
sources. Every source is still its own input during A, which makes this witness
particularly transparent.

## Reproduce and verification coverage

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 -I -O -B research/bit-source-span-seed02/verify.py
```

Expected:

```text
PASS_SOURCE_SPAN_INDEPENDENT helpers=430 clean_blocked=65 frame_blocked=364 survivor=470 reads=2102 exclusion_witnesses=429 controls=11 no_new_kappa
```

The checker recomputes every read classification and all 636 rational frame
closures. It uses sets of input identifiers, rational nullspace orthogonality
and direct parity pairings. The generator uses packed binary rows and integer
echelon geometry. Neither imports the other's implementation or a predecessor
checker. Both derive their chronological anchors separately.

The registered replay also regenerates the certificate and runs the package
controls:

```sh
python3.12 scripts/research_package.py --package research/bit-source-span-seed02
```

Eleven certificate mutations test the target, annihilator, eligible donors,
read identity, helper partition, coverage, source identity and survivor mask.
Positive controls include two- and three-source spans and the known frame186
access; the old frame79 access is rejected. Package tests compare both binary
engines with all eight literal masks on every triple of four-bit source rows:
65,536 membership decisions. They check 625 rational two-vector cases against
determinants, normalized cancellation, ambiguous JSON, optimized minimal
relocation, missing input pins, corrupt source bytes and missing source files.
See [VALIDATION.json](VALIDATION.json) for commands actually executed.

This is exact finite evidence plus the stated linear-algebra argument. It is
not a formal proof of the full multiplication theorem. No new physical word,
native multistage replay, hosted invoice, selected cold replay or outer assembly
is claimed. All inherited compiler, realization, hosting, precision/tape and
analytic obligations remain. The selected record and `upstream/` are unchanged.

## Provenance and credit

Base: `49b3157d1d89adcef16df8be98445451672be5ba`. At this base the selected
conditional kappa is `0.001672660197076918`, from PR1094 with the PR589/555 bit
supplier; the complex side binds. [SOURCES.json](SOURCES.json) pins the sole
mathematical input and historical context. [TASK.json](TASK.json) records OS
seed **2**, the three task candidates, changed scope, complete stopping rule,
overlap checks and exact predecessor heads.

Credit Ali Romman for PR1043's legal source boundary and full paid invoice;
Hanson Sun for PR1079's one-source class and fixed-anchor exclusions;
DreamingOfClouds for PR589/545/510; eumemic for PR555/543 and the bit interface;
and the retained E8 geometry, mutable-source, compiler and hosting contributors,
including Zhihao Chen, Dylan Crow, chafreaky, DaysSky and Jacob Sussman.
The exact predecessor heads are
`e309e17f83f5759b1ea1fa24a76f24838784cb4d` (1043) and
`bb20dab261884412f2d2a7955cdb2fd8e2e64a16` (1079). Their files are not modified
or vendored. PR933 fixes helper stock; PR1128 changes suffix boundaries;
PR1179 changes the helper basis. None is contradicted by this fixed-word class.

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in research, proof, code, verification and writing. Separate implementations do
not imply independent human review. New material is under Apache-2.0.

## Open next questions

Can a jointly retimed source touch and helper deletion defeat one of these
fixed-anchor witnesses while improving the complete hosted invoice? For the
explicit helper224 witness, a first step is to examine whether source1's A[483]
touch can move past A[486] without breaking dependent reads or monotone frames.
The blocker is precisely the unchanged-order/unchanged-gate premise proved
here. Retiming alone and local rank savings would not establish a gain: any
survivor still needs dirty compensation, literal restoration, returned idle
rank and the complete supplier cost. Increasing the source-mask support limit
alone is no longer an open search direction in this class.

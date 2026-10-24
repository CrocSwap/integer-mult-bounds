# Exact sector-boundary audit of the retained five-in-fourteen claim

**A source-bound correction and counterexample; no new kappa or global exclusion.**

The retained PR4813 package claims a complete five-array/fourteen-call unit.
Its proposed local observation is valid on a chosen swap eigenspace, but fails
on ordinary inputs outside that space. For x=e1 and a nonzero independent y=e2,
both sign choices leave an exact error with squared norm **1/2**.

The all-width defect is

`Delta_sigma(x)=H_(f) M_f T_f C0_f (T_f-sigma I)x`,

with exact squared norm `(1/4)|| (T_f-sigma I)x ||^2`. Thus the observation
holds **if and only if** `T_f x=sigma x`. The plus/minus validity dimensions
are `(8^f+4^f)/2` and `(8^f-4^f)/2`; they do not cover general arrays under a
single sign. [PROOF.md](PROOF.md) derives the formula while keeping the scalar
1/2 outside tensor powers, preserves the underlying source port, and gives the
full actual/declared counterexamples.

The source verifier projects its fixtures into swap sectors and constructs the
observation directly as `K x+E y`, rather than executing the raw port and
subtraction. It then recovers the inputs by a finite dense solve and applies
K in its expected-output arithmetic. No allowed all-width free decoder or
complete charge for that recovery is emitted. Moreover, the retained
`diag(C0,C0,C0,C0,C0)` rows alone already have rank 40, so the displayed full
observation rank cannot certify a saving from the additional ports.

A separate uniform-word argument shows that the missing local correction
`C2_f x` cannot be produced freely from only x and C0_f x using fixed scalar
mixing and finite sums of monomial tensor families. This does not constrain a
different global decoder using additional paid observations. A four-term
width-one correction does exist, but its literal uniform lift has squared
error 3/2 already at width two. A finite dense inverse is not automatically
an allowed uniform operator.

The central ledger records archive retention and incomplete scientific review;
this package changes no selected frontier or prior scientific disposition.
It does not refute Dugongue's underlying triangular ports or prove that every
five-in-fourteen program is impossible. A repair needs an unrestricted actual
caller or explicitly paid sector processing, an allowed decoder and a full bill.
All predecessor files, notices and manifests remain unchanged.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -I -B research/five-in-fourteen-sector-audit/verify.py
python3.12 -I -O -B research/five-in-fourteen-sector-audit/verify.py
python3.12 -B scripts/research_package.py --package research/five-in-fourteen-sector-audit
```

Expected:

```text
PASS_FIVE_IN_FOURTEEN_SECTOR_AUDIT counterexamples=2 squared_error=1/2 retained_rank=40 no_new_kappa
```

Default replay is read-only and compares [RESULT.json](RESULT.json).
`--write-result NEW_PATH` creates a fresh receipt exclusively. The verifier
independently constructs primitive Q(i) matrices, compares every source-factory
matrix, checks both separately lifting residual branches, the exact defect
matrices/norms/ranks, true sector-basis controls, concrete unrestricted failures,
the local free-correction cosets, and the width-one/width-two distinction.
Checks use explicit exceptions and remain active under optimization.

## Separate source-transport status

On the pinned main, the source package wrapper rejects `NOTICE.md` at its own
manifest guard. The full manifest comparison also finds `finite_geometry.py`
drift. The unchanged primary `verify_schedule.py`, run directly, emits its
finite PASS receipt. These transport and finite-replay observations are
separate from the mathematical counterexample; neither is interpreted as
scientific admission or a general lower bound. The audit declares every
source file read by its manifest comparison, including metadata and notices.
The observed commands and primary receipt are preserved in
[SOURCE-REPLAY.json](SOURCE-REPLAY.json); default audit replay does not rerun
the source's finite geometry computation.

No Lean build, selected cold replay, compiler admission or full native suite
was run. The source's finite geometry is not re-proved here.

## Assignment, exact inputs and overlap

Scientific base: `bee95ce88f9f19802f0613f92838895cd0e14a1f`, priority revision 7.
OS seed: `832fc58b2d79de5b163798ed76ab317d`; adversarial-audit track,
`uniform-transfer-audit` card changed from the historical #4100 example to this
specific claimed all-width implication. [TASK.json](TASK.json) records the
scope change, evidence and stop rule. [SOURCES.json](SOURCES.json) pins all
consumed source bytes. [OVERLAP.json](OVERLAP.json) states coverage and limits.

The originating claim is Pierre-Loic Doulcet / hexapode's
[PR4813](https://github.com/CrocSwap/integer-mult-bounds/pull/4813), scientific
head `f982ecc06826e7087e69b9468d3ff52589fd0822`. The retained main source last
changed at `9e33ecf009d36118f49ac86e9a0ee36e38dca44f`. It was also retained in
the PR4841 archival lineage; this is not a claim of independent scientific
acceptance or attribution of the original schedule to its archive integrator.

## Open next questions

- Can a repaired global word use the actual raw ports, with all initial owners,
  unrestricted inputs and allowed all-width decoder operations accounted for?
  Start by emitting the literal word and checking all input columns. The
  present finite observation recovery does not supply it.
- If explicit sector processing is used, can its complete paid/copy/return bill
  still meet the claimed call count? Start from both projectors and both
  sector inputs for one port; do not identify a sector oracle with a free
  arbitrary-input Gaussian correction.

## Credit

Pierre-Loic Doulcet / hexapode supplies the PR4813 schedule claim under audit.
Dugongue supplies PR4743's valid arbitrary-input ports and sector-completion
interface. Yiyang / PR4710 supplies the phase repair and residual identities;
lee-phys / PR4688 supplies the prefix and hook-rank work. Jacob Alan Sussman /
PR4628 supplies the engine and small-unit bound, retaining eumemic and Swapnil
Jain credit. The uniform tensor-family separation method is standard and is
also used by JoyboyBrian's retained
[staggered-prefix work](../staggered-single-owner-obstruction/README.md); this audit binds it
to the actual named local correction. Source notices and AI disclosures remain.

Prepared by Cinna Davis with substantial OpenAI Codex assistance in research,
proof explanation, implementation, verification and writing. Apache-2.0.
No proof-assistant or independent human verification is claimed.

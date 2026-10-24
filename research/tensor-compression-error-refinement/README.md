# Original-coordinate compression error refinement

This independently audits PR3935's compression suffix, keeping the original
Core numerical program and PR3851's local analytic guarantees. It binds the
all-halos-first physical schedule, mixed-radix spectator lines, unequal source
cores and their zero-padded slots to a complete original-coordinate nonlinear
map. It does not repeat the already-proved scalar error sum.

With inherited local defect delta_i<2*2^-p and exact global compression norm
at most1/8, the computed inputs stay in the local unit-disk domain. The written
source argument gives

    r_(i+1) <= r_i/8 + delta_i,
    e_(i+1) <= e_i/8 + delta_i.

For common precision the final error is strictly below
`8^-D e_0 + (16/7)(1-8^-D)2^-p`. Each defect is evaluated on the computed
input; no linearity or Lipschitz property of rounded Core is assumed.
[PROOF.md](PROOF.md) states the original-axis provenance, analytic/locality,
primitive and storage premises separately. Exact final restoration still
multiplies all errors by2^gamma. No precision or cost saving is installed.

The finite checker authenticates and extracts the six original compression
statements from `Tensor.run`, starts at its post-chirp target-box boundary,
and stops before restoration. Every numerical owner runs its original code.
It compares all actual Core returns to an independent signed staged model
and the final output to a natural-coordinate model. This is a suffix execution,
not a successful full Tensor invocation. The reused p48/P80 catalogue has
boundary-only cells and reduced halos: it establishes finite conformance,
not production locality, norm or Fourier accuracy.

```sh
python3.12 -B scripts/research_package.py --package research/tensor-compression-error-refinement
python3.12 -B scripts/check_research_commit.py --package research/tensor-compression-error-refinement --check-source-history
```

## Open next questions

1. Independently audit PR3851's uniform local defect from the original old-H
   construction and exact stored-value guards. Start at the completed local
   composition, distinguishing rounded Schur factors from the true N inverse.
   Our tensor recurrence retains this as an explicit premise.
2. Bind the complete CRT entrance/product/return and both S factors. Start at
   PR4024 and PR3935's R F_s convention; this is assigned separately in round8
   and is not supplied by a compression invariant.
3. Validate the production native and exact word/interval premises under a
   separately budgeted execution or formal refinement. Reduced finite pages
   cannot replace these premises or amortize setup by themselves.

## Sources, distinction and credit

Canonical base4c0a359d88f22f05189d51f48387750b801a45d4, priority7.
Claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/3664#discussioncomment-19141159.
Scout covered320 openPRs at07:41:25UTC,4168 Discussion records at07:42:18UTC
and6760 tracked notes, complete within that scope. Arbitrary diffs and
unpublished work remain unsearched. PR5056 audits expansion and stops before
chirp. PR5059 supplies a different boundary-page ABI; it is not substituted
here. `compression-error-sum` already proves the scalar delta<2h comparison.

Credit Jose Manuel/jmbarrancoml PR3935 and3851, Chafik Boukhalfa PR489 and
its boundary/halo lineage, Dugongue, RaD/hipotures, retained Gaussian/chirp/
word/Harvey–van der Hoeven and manuscript contributors. The retained catalogue
grammar parser is reused; independent numerical arithmetic and coordinate
assembly are new checker code. Frozen inputs and notices are unchanged.
Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Informal
proof and AI-assisted checks are not independent human or proof-kernel
acceptance. Apache-2.0. No selected-frontier change.

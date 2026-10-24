# Strict finite-block descent of the projection recurrence

For the source block-four seed `(0,27456,48576,68320,86592)`, the unchanged
projection recurrence satisfies **T_(m+1)<T_m for every m≥4**. Its exact
infimum is **439277/149175**, approached but never attained at a finite block.
This closes the finite-block question explicitly left open by Nick Petalas's
[PR5151](https://github.com/CrocSwap/integer-mult-bounds/pull/5151).

[PROOF.md](PROOF.md) proves a weighted profile ordering with weight
`h(r)=1−3/2^(r+1)`. Interior weighted rows dominate in every upper tail.
The two low-index comparisons use 22 exact rational inequalities through
block14 and an explicit summable error bound for all subsequent blocks.
This ordering gives a strict sign for every adjacent top-ratio difference.
The infimum then follows from the pinned predecessor's exact limit theorem,
retained in [limit-predecessor.md](limit-predecessor.md).

The written argument supplies the infinite quantifier. The replay checks
source bytes, the finite certificate, algebraic identity calibrations,
actual first ratios, negative controls and a mandatory typed complete
[RESULT.json](RESULT.json). [independent.py](independent.py) uses a separate
normalized Fraction recurrence and Gaussian-binomial limit calculation.
Neither replay is a proof-kernel verification.

The result is unconditional for this numerical recurrence. Using it as an
engine lower bound still inherits the representation and hook premises of
PR4628/4643, particularly the uncertified block-four rank inputs 48576 and
68320. No hook-rank census, Lean run, physical supplier, global multiplication
theorem or selected κ change is claimed. Optional triangle/max strengthening
and arbitrary other seeds are outside scope.

## Sources and reproduction

The actual recurrence/seed input is Maximilian Lutz's retained
`research/projection-recursion-check/README.md` (PR4643), which credits Jacob
Alan Sussman's PR4628. The exact limit proof is retained byte-for-byte from
PR5151 head `e6c8e945a47dcc4a6f08974682090fc7f5e221a3`, path
`research/projection-recursion-limit/PROOF.md`. Its external origin is recorded
in SOURCES; the live retained copy is pinned to the first local source commit.
This pin is for reproducible bytes, not a claim that the predecessor was
merged or independently accepted. Source history checks authenticate both.

```sh
python3.12 -B research/projection-recursion-finite-infimum/verify.py
python3.12 -B research/projection-recursion-finite-infimum/independent.py
python3.12 scripts/research_package.py --package research/projection-recursion-finite-infimum
```

Standard library only; each direct check is below one second on the development
machine. Controls reject removal of the block-three seed demand and exhibit a
monotone concave seed whose top ratio increases, ruling out an overbroad claim.
Cold mutation checks also exercise source, receipt and boundary-rule corruption.

## Open next questions

1. Certify the two unresolved block-four hook ranks with stored minors and a
   separate checker; this is needed to discharge the cited engine premises.
2. Characterize seed profiles with finite descent. The weighted boundary
   conditions here offer a sufficient criterion; ordinary concavity alone
   does not. No new construction round follows from this arithmetic result.

Structured questions are recorded in TASK.json.

## Credit

Prepared by JoyboyBrian with substantial OpenAI Codex (Astra) assistance.
Jacob Alan Sussman supplies the recurrence and hook seed (PR4628); Maximilian
Lutz supplies the independent projection audit (PR4643); Nick Petalas supplies
the exact limit and convergence theorem (PR5151). Eumemic and Swapnil Jain
retain the predecessor certificate-method credit. Classical summation by parts
and stochastic ordering retain their mathematical attribution. New work is
Apache-2.0. This is an AI-assisted written proof, not human or kernel approval.

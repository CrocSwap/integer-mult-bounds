# A dyadic oblique section for the resonant channel

The frozen resonant coefficient A from [PR #4797](https://github.com/CrocSwap/integer-mult-bounds/pull/4797)
has a fixed dyadic decoder B with **A_f B_f A_f=A_f at every positive tensor
width**. It uses 1,920 free monomials, denominator 2048 and a uniform operator
norm upper bound 113/32. No odd scalar division is required in this module.

Given a channel observation z, B_f z is an exact representative of its input
coset. The idempotent E_f=B_f A_f has exactly the kernel of A_f, so the changed
representative retains all accessible information. It is genuinely oblique:
at width two E(9,0)=1/2 while E(0,9)=0. It is not the canonical orthogonal
projection whose recovery requires primes 3,5,7 in [PR #4980](https://github.com/CrocSwap/integer-mult-bounds/pull/4980).
That output contract is essential to the predecessor theorem; the new section
answers its explicit oblique-recovery question without contradicting it.

This is an exact linear interface result, not a complete consumer, restored
paid supplier, call saving or new kappa. The 1,920 passes may be unaffordable
in a complete consumer. No selected record or frozen predecessor is modified.

## Certificate and reproduction

[PROOF.md](PROOF.md) derives the result from a finite integer identity.
[SECTION.json](SECTION.json) has 30 signed-double-coset recipe terms.
The checker reconstructs the 128-term even target quotient, its signed
stabilizers (sizes 32 and 16), and the 1,920-term section. It checks the entire
coefficient table of C D C=C, with A=a C/8 and B=8 D a^-1. Actual central
quarter phases are retained; only [-I]=[I] is used at even widths. The source
itself proves odd-width cancellation. All output words are checked against
the source's affine/quadratic free alphabet.

From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/resonant-oblique-section
python3.12 -B scripts/check_research_commit.py --package research/resonant-oblique-section --check-source-history
```

Direct normal and optimized replay use `verify.py` and
`independent_tensor.py` in this package. The latter uses a separate packed
column-action engine: all 64 width-two columns, a non-Hermitian projection
witness, literal odd-width cancellation and a 4,096-coordinate width-four
Gaussian-integer dirty input. It rejects loss of actual central quarter phases. Explicit
checks reject a changed section coefficient, a wrong denominator, loss of the
central quarter phase and an inadmissible cubic phase. These are deterministic
exact checks with no solver, network, dependency, Lean or Docker requirement.

The logical decoder retains its observation and uses an owned accumulator and
one owned monomial temporary. Initialization and erasure scans are required.
It has 1,920 logical monomial/accumulation passes; every scalar is dyadic with
eleven extra fractional bits and at most two extra integer magnitude bits.
The full physical read/routing/tape cost remains unknown. The complete
[obligation ledger](PROOF.md#arithmetic-and-complete-obligation-ledger) marks
the missing canonical jobs, complement, original-owner restoration, compiler,
stock and outer costs explicitly. Unknown costs are not zero.

## Open next questions

1. Can a chronological complete consumer use these changed representatives
   to encode named independent Gaussian jobs? First bind a canonical encoder,
   the missing target complement, arbitrary owners and the eventual restored
   outputs. No useful paid moment is inferred from image rank or this section.
2. Does the resulting completed consumer afford all 1,920 monomial passes,
   dyadic arithmetic, two owned buffers, legal reads, routing, initialization,
   erasure, precision, compiler and outer reserve? Price that complete invoice
   before extending the mechanism or optimizing the section.

The family decision is **NARROW** to this changed output contract. It removes
odd division from one explicit formal module. A missing physical consumer is
not an invitation to treat its cost as zero or to launch a chain of local
optimizations.

## Sources and credit

Scientific base: canonical main `bee95ce88f9f19802f0613f92838895cd0e14a1f`,
priority revision 7. The source TARGET is byte-pinned by SHA256 and Git blob in
[SOURCES.json](SOURCES.json). The selected result remains conditional
kappa 0.00302015. Overlap at 06:08 UTC covered 310 open PRs (06:05:59),
4,096 Discussion records (06:06:48), and all 6,690 tracked local notes.
The oblique match was the predecessor's explicit open question. No novelty
guarantee follows; arbitrary diffs and unpublished work are outside coverage.

Credit JoyboyBrian #4797 for the channel; Dugongue #4885 for all-width rank,
orthogonal projection and rational recovery; JoyboyBrian #4980 for the scalar
criterion and oblique open question; Nick Petalas #4825 for the existing
width-four dyadic minor. Retain Yiyang/Lyy-iiis #4710, lee-phys #4688,
Jacob Alan Sussman #4628 with eumemic and Swapnil Jain and the source lineage.
Signed stabilizer averaging, generalized inverses and oblique projections are
standard algebra; no literature-priority claim is made. Prepared for
JoyboyBrian with substantial OpenAI Codex assistance. Exact automated checks
are not independent human or proof-assistant acceptance. Apache-2.0.

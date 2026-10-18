# The T740 phase normal form covers every actual owner and port

All **82,880** literal T740 owner/port contexts reduce to PR3297's same
20-variable residual-phase normal form. This covers 740 owners and 112 ports,
including every placement changed by the 145-row exchange journal. The new
step is a source-bound hosting implication, not another inverse calculation.

For every context, every character `x` in `F_2^73`, and every tuple of nonzero
complex residual multipliers `z`, its normalized eight-stream operator is

```text
i^(-popcount(x)) M_owner,port(z; x) = F(z; g_port(x))
g_port(x) = i^(-parity(q_port & x)).
```

`F` is exactly the 72-term matrix retained from
[PR3297](https://github.com/CrocSwap/integer-mult-bounds/pull/3297), head
`bab1899ce1c6fd43d073ac7c3a8e7c3e69008c0e`. Its published inverse therefore
applies to every actual context, not only owner 0 / port 0. Conditional on that
inherited inverse, operator-preserving independent residual replacements retain
each residual rank separately in every context. This rules out an escape based
only on choosing a different original owner or port. It does not rule out a
changed hosting, chart, insertion cut or data word.

## What the checker establishes

[verify.py](verify.py) reconstructs all 2,717,280 expanded fill rows from the
canonical base fill and exact journal. It checks every journal preimage and
reproduces the full payload SHA256
`8f4d6965ba573ff2b71fd7bf6b552643e086739d90bd73c55889502077638e00`.
Every owner/port has between 28 and 45 hosted rows. Every hosted slice is
in range, disjoint, on the same physical stream as its residual phase, and in
a no-shear interval ending at that residual phase. Every hosted union is the
literal compact prefix used by the source contract.

The no-shear check is structural. It does not sample characters. Hosted phase
factors commute forward to their residual site, so the hosted prefix and
unchanged residual list combine into the full child basis. The resulting word
no longer depends on owner, helper widths or the hosting split.

[algebra.py](algebra.py) replays that full-child word for all 112 actual port
recipes using exact Z4 character polynomials and formal residual multipliers.
All 112 results equal the retained 72-term matrix, with each port's own `q`.
The all-one assignment is the identity coefficient by coefficient. The full
receipt, including 74 distinct original residual profiles, is [RESULT.json](RESULT.json).
[PROOF.md](PROOF.md) states the commutation argument and its precise boundary.

## Reproduction and source closure

From the repository root, with standard-library CPython 3.12:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/t740-all-context-normalization
```

The complete registered replay passes on CPython 3.12.15 / Linux x86_64,
including source coverage and eleven behavioral control groups. Controls reject an early or late host crossing a shear, a changed
physical stream, duplicate axes, a newly inserted touching shear, an early
terminal permutation, a corrupt journal preimage, a corrupt source hash, a
rank-changing full-child phase and a corrupt reference matrix. Positive controls
include legal transport and the last nonzero port. Controls also run under `-O`.
Checks use explicit exceptions rather than removable assertions.

The eight live inputs are pinned at canonical main
`463113d675af7410ac91d53a4fed51ec6494eb9a` in [SOURCES.json](SOURCES.json).
The exact PR3297 proof and result bytes are committed under `reference/`, with
original hashes, blob IDs and source paths. They are used as the inherited
inverse proof and comparison certificate. No unmerged Git object, peer output,
network lookup or executable predecessor is needed by the standalone replay.
These retained source records are not new authorship or a second independent
proof of PR3297's inverse.

## Limits and expansion decision

This package proves the hosting-to-normal-form implication for the pinned finite
T740 source and all characters and nonzero residual multipliers. It inherits
PR3297's rational inverse and rank-average argument, and the completed-call
Fourier phase contract. It does not independently audit that inverse, execute
native calls, validate physical ownership or movement costs, price a changed
consumer, discharge all-size/compiler or precision hypotheses, replay the
selected supplier, admit a supplier, or improve kappa.

Decision: close the uncovered owner/port application of this fixed-interface
argument. Do not expand a rank-redistribution search within this interface.
A new construction must identify a changed interface and pay its complete
native, hosting, restoration and consumer bill. Unknown costs remain unknown.

## Open next questions

- Can one specified changed hosting or insertion cut avoid the no-shear
  normalization while preserving the complete operator? First write its actual
  event word and compare its full operator. Its physical legality and complete
  bill are blockers; this theorem does not cover it.
- Can an equal-rank, equal-phase basis replacement save a paid implementation
  cost? First exhibit the basis replacement and its actual producer/consumer
  invoice. Phase equality by itself supplies no saving.

## Sources and credit

thakrarsagar's PR3297 supplies the complete 20-site matrix, inverse and
rank-average implication. PR3272 supplies its preceding five-site phase method.
The new character algebra adapts PR3297's bitset representation and source
operation formulas, with attribution retained here. No independent inverse
audit is an input to this package. Ross Richardson's related twenty-slot normalization handoff in
[Discussion2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18999338)
was public before this work. Its evidence was local-only and is not inspected
or claimed as a new method here. This package adds exact all-context source
coverage and an executable no-shear certificate.

Retain Nick Petalas/PR3187 and Gareth Davidson/PR1387 for the physical-stream
criterion, Tekalign/PR3204 and Gonzalo Mier/PR3196/3199/3263 for the fixed-word
work, Jeremy Diviney/PR3148 for the T740 fill and journal, dcharb78/PR3133 for
the retained providers and notices, Rohan Arun for the audited rank-transfer
context, Marius-Paul Dumitrean/PR2979 and the selected geometry/native lineage.
Canonical PR3133 notice and credits remain unchanged under
`research/idle-star-paired-axis-census/vendor/`.

Task `uniform-transfer-audit`, refined to the actual hosting implication.
Priority revision 6. Initial complete snapshots covered 344 open PRs and 2,143
Discussion records at 2026-10-17T21:12 UTC; exact freshness is in TASK.json.
A pre-submission refresh covered 353 open PRs at 21:24:55 UTC and 2,151
Discussion records at 21:25:28 UTC, with complete pagination and no warnings.
No matching all-context source certificate was found; this is not proof of
novelty. Human-directed Discussion posts are restricted for this session;
its finding draft is local only.

Nick Petalas. Apache-2.0.

## Engineering constraints

Build the Lever produced the rerunnable all-row transport checker instead of
82,880 separate symbolic replays. Prove It Works requires full source-payload
binding, all 112 symbolic port words and rejection controls.

Power-of-Ten rule 3 has a managed-runtime deviation. Python allocates bounded
fixture objects and exact polynomial dictionaries. Decoded input files are at
most 32 MB each; there are eight authenticated live inputs, 82,880 contexts,
20 child slots and at most 256 symbolic terms per matrix. Rule 8's `cache`
decorator memoizes only phase axes from these bounded recipes; it does not
construct code. Rule 9's ordinary dictionary and method dispatch is bounded to
these explicit standard-library representations. No dynamic source execution,
recursion or subprocess is used by the standalone checker. Frozen predecessor
bytes are retained rather than refactored. Functions stay within 60 lines;
static diagnostics and normal/optimized behavioral checks are recorded with
the contribution. A lower-allocation rewrite is warranted only if this fixed
fixture exceeds its registered resource bound, without weakening coverage.

# Eight fewer ADDs in the translated Gaussian reader

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: finite explicit factor construction with a scoped algebraic proof.
After the translated reader basis of [PR6677](https://github.com/CrocSwap/integer-mult-bounds/pull/6677),
one new rational shear, in zero-based mode indices,

```text
L0 -= (1/5) L1,          J1 += (1/5) J0,
```

reduces the complete four-shear bill from 20,320 to **20,312 coefficient
ADDs**. Every factor translation is charged. The axis-by-axis translation
invoice falls from 91,924 to 91,852 units. Thirty arbitrary dirty borrowed
fields are still exactly restored. The maximum absolute coefficient and
factor norm bounds stay at 9/8, 43/16 and 72.

The common coefficient denominator rises from 960 to **4,800**. The saving
is in coefficient instructions and the declared translation invoice; a
complete physical or arithmetic saving is unproved. No new kappa, productive
helper credit, admitted supplier or selected-frontier change is claimed.

The question is Ali Romman's [PR5646](https://github.com/CrocSwap/integer-mult-bounds/pull/5646)
broader-basis question. The new step is this further rational shear after
PR6677, not a replay or audit of its construction. [PROOF.md](PROOF.md)
gives the factor identity and the arbitrary-input dirty-bank argument.

## Evidence and reproduction

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/translated-reader-step/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/translated-reader-step/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/translated-reader-step
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/translated-reader-step --check-source-history
```

Another CPython 3.12 executable can replace the local interpreter. The direct
checker prints `PASS_TRANSLATED_READER_STEP` in a generated JSON receipt
bound to all package files. It writes nothing. The registered runner prints
`PASS_REGISTERED_RESEARCH_PACKAGE`; the publication check prints
`PASS_RESEARCH_COMMIT_BYTES`.

The new checks compare the entire changed-pair product in Q[C2^9], including
all 14,320 nonzero baseline coefficients and any possible new positions.
They check the inverse basis, every untouched factor vector, all coefficient,
translation, denominator and magnitude metrics, and one literal dense
512-address four-shear execution. That execution compares all 57,344 data
coordinates and restores all 15,360 dirty-bank coordinates. Eight controls
reject omitted factor updates, a wrong sign or translation, invalid shifts,
inexact coefficients and a missing mode. The written proof supplies the
universal input and representation quantifiers; the payload is corroboration.

## Scope and credit

Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8,
selected #7000. The `complex-new-helper-inventory` card changes scope to an
ordinary reader-interface side result. Its new productive-helper and complete
physical-invoice gates are unmet. All five selected assumptions remain.
[TASK.json](TASK.json) records the exact card and changed scope.

Ali Romman / PR5646 supplies the actual factors, constant dyadic basis and
broader-basis question. Nick Petalas / PR6677 supplies the translated input
basis and the reconstruction and word code adapted here; PR5919 supplies
the earlier rational escape and factor-reconstruction lineage. David Ganz /
Dugongue / PR5634 supplies the reader substitution and four-shear identity;
Ali Romman / PR5640 supplies the borrowed-space contract. Centre-code-services,
reciprocal-native-responses, native-centre-capture, centre-metric-encoders,
PR3133, PR3148, PR2588, PR2226 and their individual native, numerical and
compiler contributors retain their attribution. Their files and credit lines
are unchanged. The source identities and null-product premise are cited inputs,
not new verification claims. Independent human and formal proof-kernel review
are unclaimed.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19539321)
followed live PR/account lists, recent handoffs, active Discussions, reservation
checks and main/merged searches for the actual Gaussian reader and general
translated bases. The cached local note search covers 194 of 10,178 HEAD
records; explicit main-tree searches supplement that sparse inventory.
Unpublished work and arbitrary historical diffs remain outside coverage.
Discovery stopped at the first verified new step. No local or global optimum
is asserted.

## Open next questions

- Does the eight-ADD saving survive a complete rational arithmetic and physical
  routing bill? Start with both factor pairs in the same priced kernel,
  charging multiplication, rounding, source-layout return, storage and returned
  ownership. The full caller and arithmetic backend are missing.
- Can a further basis improve a fixed complete physical objective? Define that
  objective before another cancellation search. This witness supplies no optimum;
  physical prices and a consumer contract remain the blockers.

Structured relevance, first steps and blockers are in TASK.json.

## Implementation bounds and limits

The fixed reconstruction uses 112 ports, 30 modes and 512 addresses, ten supplied
constant basis operations, one cited translated operation and one new rational
operation. Kernel vectors contain at most 57,344 entries; decoded source files
have a 16 MiB bound. Literal states contain at most 142 arrays of 512 entries,
with one exact integer scale per shear. Functions stay below sixty physical
lines. New code uses no recursion, network, subprocess, dynamic evaluation or
mutable shared research state. Explicit exception checks remain active under
optimization. Warning-strict normal/optimized execution and AST compilation
supply the available diagnostics; no separate type/lint analyzer is claimed.

Power of Ten rule 3 has a managed-runtime deviation. Python allocates integers,
Fractions, lists and dictionaries dynamically. Fixed source bytes, dimensions,
operations and fixture counts bound the mathematical data, but no fixed pool
or byte-exact heap bound is claimed. A future variable-size arithmetic backend
must provide its own capacity and cleanup contract.

Native source correctness, the section's own thirty-field bank, arithmetic
interiors, tape movement, whole-caller precision, stock, owned erasure, uniform
compilation and outer use remain separate obligations. Selected cold replay,
predecessor scientific suites, Lean, Docker and a materialized rounded multiplier
are unrun. This package proves no complete multiplication theorem.

# Two contact-block output contractions

The complete conditional claim is **kappa = 0.00315087**, up from PR6353's
**0.00315057**. The gain is **0.00000030**, about **0.00952 percent**.
This is a small, source-bound improvement.

A joint helper basis contracts outputs 224 and 227. Both outputs change from
rank nine to rank eight. Two paid transports change from rank five to rank
four. All 770 public inputs remain independent. The main interface and fixed
PR6348 caller remain unchanged.

The earlier search held this contact block fixed. This was a scope restriction,
not a proved cost floor. This construction changes those contacts and checks
the complete word again. It does not reuse an unchanged-contact assertion.
The joint basis and native transpose extend PR6353's mechanism.

For `H_r = r^(1-kappa)`, the exact local changes are

```text
paid:       2H4 - 2H5
productive: 2H8 - 2H9.
```

The margin increases by `2[(H5-H4)-(H9-H8)]`. This is positive for every
strictly concave power tariff. The complete rational crossing is in
`(0.00315087900390, 0.00315087900391)`.

Read [PROOF.md](PROOF.md), [BASIS.json](BASIS.json) and [RESULT.json](RESULT.json).
The word has 17,757 events, 29 owned labels, 43 owned lifetimes and peak owned
storage 13. The full caller has 70,656 paid jobs, 14,214 productive jobs and
rank-mass surplus 808. The two added lifetimes and all ordinary operations are
charged. No owned field receives productive credit.

## Reproduce

Use Python 3.12 with no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/p104-contact-block-contraction --check-only
python3.12 -B scripts/research_package.py --package research/p104-contact-block-contraction
```

The registered normal and optimized commands check the source pins, both
bases, both zero rows in the dual preparation, every word field, all 799 scalar columns,
native absolute phases, all 7,904 caller contacts, two rational price engines,
completion, compiler bounds and all 54 strict plus four functional outer
predicates. [VALIDATION.md](VALIDATION.md) records the checks actually run.

## Sources, coordination and limits

Base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. Source: PR6353 at `db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3`.
The two files retained from that head have exact Git and SHA256 pins in this
branch's own history. A cold replay does not need the pending PR's Git objects.
The thirteen main inputs and both retained files appear in SOURCES.json and
VERIFY.json.

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5645#discussioncomment-19205459)
records the investigation. This construction and PR6355's independent audit
are separate. Current open PRs and adjacent claims were checked. Cached phrase
searches have sparse local coverage and do not prove novelty.

The historical packing caps do not apply to this changed source and fixed
binary-tree caller without a model-equivalence proof. This package instead
checks its complete caller bill. It claims no global optimum or family ceiling.
The admitted BIT budget remains 0.0034; this construction stays below that cap.

All five inherited assumptions remain: `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery`. The uniform large word
and rounded multiplier are not materialized. No practical speedup, independent
scientific acceptance, formal-kernel acceptance or selected-frontier change is
claimed.

## Open next questions

An independent reviewer can check the two unit pairings, the zero temporary
rows and the exact target debit. Further construction work must use a changed
mechanism and a full bill; the bounded continuation screen found no further
accepted equal-target contraction. That screen is not a global obstruction.
Structured questions are in [TASK.json](TASK.json).

## Credit

Ali Romman, with substantial OpenAI Codex assistance. No subagents. Apache-2.0.
PR6353 supplies the joint basis method, source word and native transpose.
PR6349, PR6348 and their full source chains retain their credit, including
DreamingOfClouds, Cinna Davis and all native, helper, recursion, compiler, BIT
and analytic authors. [NOTICE](NOTICE) preserves the predecessor notices.

# Application review for conditional κ = 0.003644407895539

[PR #7156](https://github.com/CrocSwap/integer-mult-bounds/pull/7156) supplies the
chart-306 continuation of [#7155](https://github.com/CrocSwap/integer-mult-bounds/pull/7155).
This review supplies an exact-head cold replay, separate checks of the
affected application, and a written transfer of the five selected #7000
premises. The proposed bound is **κ = 0.003644407895539**, an increase of
0.000014349725539 over the selected #7000/#7001 record and 0.000000140810139 over
#7155. Selection requires maintainer mathematical review under the
[repository's frontier lane](../../docs/research/research-archive-intake.md).

The exact proposed parameters, both uniform savings, all nine outer savings
and the limiting slack are in the `proposed` object of [RESULT.json](RESULT.json).
[APPLICATION.md](APPLICATION.md) gives the proof and its scope. The application
uses the unchanged signed [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113),
with 17 native invocations on ambient 145. The complete invoice has 110,502
paid positions, 22,410 productive fields and rank surplus 1,424 with zero
empty-root credit. The proof retains the compiler's conservative ambient
cap of 153.

## Reproduce

```sh
python3.12 -I -B research/p104-frontier-7156-application-review/verify.py
python3.12 scripts/research_package.py --package research/p104-frontier-7156-application-review
```

The registered review check matches the complete receipt. It uses Python
3.12 and the standard library. It independently recomputes the temporal
certificate, literal rank invoice, fixed-tape counts, directed numerical
bounds and exact outer predicates. It invokes the pinned selected
carry/remainder implementation on all literal coefficients. The cold supplier
check is a separate replay.

```sh
# In an isolated checkout of PR #7156 at b44944c3058d522cbff17836e16240d40d77a927
python3.12 scripts/research_package.py --package research/p104-temporal-chart306-continuation
```

The supplier replay exited zero in 819.98 seconds and used 662,444 KiB peak
RSS. It checked the complete normalized native and signed caller endpoints,
all 3,037 catalogue maps, all 104 main boundary pairs, precision, physical
binding and the outer gates. See the
[cold replay](evidence/CANDIDATE-REGISTERED-COLD.log) and
[exact commit check](evidence/CANDIDATE-GIT-CHECK.log). The exact-head
[hosted supplier job](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/42947927760/job/130286697795)
also passed. Its sibling
[historical replay](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/42947927760/job/130286697696)
failed on the historical package's Makefile source pin.

[SOURCES.json](SOURCES.json) pins selected main inputs.
[INPUTS.json](INPUTS.json) binds the small frozen PR review inputs by commit,
path, Git blob, SHA256 and length. The registered check authenticates the
vendored bytes offline. To verify their provenance, fetch the named
`refs/pull/<number>/head` refs separately, ensure the recorded commits are
available, and compare each row against
`git --no-replace-objects ls-tree <commit> -- <path>` and
`git --no-replace-objects cat-file blob <git_blob>`. The local cold review
compared the complete 32-member #7155 archive and the 30-member #7113
review slice against the directly fetched PR trees. The
[source audit](evidence/SOURCE-AUTHENTICATION.json) also binds the selected
BIT data and the selected physical checker by byte equality. The
[closure comparison](evidence/SELECTED-CLOSURE-DELTA.json) and
[recorded-evidence check](evidence/SELECTED-RECORDED-EVIDENCE.log) bind the
unchanged selected 220-path scientific closure and its 18 recorded executions.

## Open next questions

- Review this application for conditional frontier selection. The next step
  is a maintainer's reading of the common-grid, stock and outer proof
  against the pinned source and the preserved receipts. The five inherited
  framework assumptions remain. This package gives finite evidence and a
  mathematical application argument. A materialized uniform word, literal
  multiplier execution and independent human or formal proof remain outside
  this contribution.

## Credit

Rohan Arun supplied #7156 and the #7113 signed caller. Clear1nsight supplied
#7155 and this exact-source application review with substantial OpenAI Codex
and ChatGPT Pro assistance. The [notice](NOTICE) records the inherited work.
Coordination is in the [P104 board](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19533717).

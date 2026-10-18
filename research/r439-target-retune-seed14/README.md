# Retune one target step after R439 helper mixing

**Local finite bit-circuit construction; no new kappa.** One target
transvection selected on PR967's mixed compensation matrix saves three
fully paid ADDs: **11,783 -> 11,780**. Both positive full-word bounds stay
unchanged, `F=72,847` and `B=10,394,084`.

The new step is `target[24] += target[35]` (register `135 += 146`) after
the frozen PR915 target preparation and before middle injections. Its
literal inverse is paid before target restoration. The changed middle
row has 107 entries instead of 112, giving `5 - 2 = 3` saved ADDs.

This is a coupled compensation step: before PR967 helper mixing, the
same target operation would **add 18 ADDs**. It becomes useful on
`E K H^-1`. No helper is omitted or reselected. It therefore differs from
the helper-star search, omission atlas and common-frame resynthesis work.

All `111 * 110 = 12,210` directed choices were scored. Twelve improve the
fully paid count, ten pass the exact local and nine-stage prefix bounds,
and the unique best saves three. Thus 11,780 is the exact minimum in
the **fixed one-target-insertion class** defined in [PROOF.md](PROOF.md).
No unrestricted circuit, multi-step or joint-basis optimum is claimed.

| Complete local resource | PR967 | This candidate |
| --- | ---: | ---: |
| Helper preparation/restoration, each | 221 | 221 |
| Target preparation/restoration, each | 306 | 307 |
| Middle injections | 4,509 | 4,504 |
| D ADDs | 5,563 | 5,560 |
| All ADDs, including scatter and cleanup | 11,783 | 11,780 |
| Exported records | 14,712 | 14,709 |
| Helpers / copied totals / rank mass | 439 / 9 / 5,129 | unchanged |

From the repository root, Python 3.10+ and the standard library suffice:

```text
python research/r439-target-retune-seed14/verify.py
```

Expected final line:

```text
PASS_R439_TARGET_RETUNE_S14 pairs=12210 positive=12 admitted=10 ADDs=11783->11780 F=72847 B=10394084 columns=661 controls=14
```

The verifier imports no search code. It reconstructs PR967's recipe from
the selected PR589 compensation matrix, PR915 target steps and PR967
helper steps using sets; checks every directed score and each improving
nominee's literal full-word bounds; replays all 661 arbitrary input columns
in both directions; and calls the unchanged owning geometry checker and
record exporter. The entire MOVE/COPY/ERASE sequence remains identical.
Fourteen negative controls and a fully paid neutral-pair control pass.

`search.py` regenerates the bounded search; `--write` writes its certificate
and compressed candidate. Normal search replay compares the complete
decoded word, not gzip container bytes. `verify.py --write-receipt` records
the independent receipt; normal verification compares every receipt field.
Immutable source inputs are pinned in `SOURCES.json`, with an exact
required inventory and no dependency on the moving selected record.

The original syntactic H2 and literal K extraction remain false, as for
PR915/926/967. The semantic D boundary is checked exactly. Native 5/9/11
stage replay, changed whole-hosted emission, full invoices and assembly
adoption remain unperformed here. Local prefix admission does not establish
those obligations or a new exponent. The selected PR942/PR589 construction
is unchanged.

See [VALIDATION.md](VALIDATION.md), [OVERLAP.json](OVERLAP.json) and
[NOTICE.md](NOTICE.md). Prepared for @woklerx with substantial OpenAI Codex
assistance, Apache-2.0.

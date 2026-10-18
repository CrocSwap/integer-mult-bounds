# V45 drops four widths and keeps the predecessor call order

**Partial. No new exponent.**

Both providers charge helpers 249, 251, 265 and 267 at width 8 in the parent and
width 7 in the shipped words. Six helpers drop from width 8 to 7; these four are
that drop together with helpers 299 and 331. The recorded idle histogram moves at
stage 1 and then stays put from stage 2 through the final certificate. The shipped
order and dispatch files are the predecessor chronology, byte for byte.

## What was executed

Width is the end-frame length minus the start-extra length. For each of the four
helpers the start-extra list is empty, so the width is the end-frame length.
Across every live helper, the parent-to-shipped width changes are 16 drops from
7 to 6, the six drops from 8 to 7, and five drops from 9 to 8. The five are the
later extractions 226, 228, 230, 363 and 395. Both providers agree.

Each stored basis pattern contributes its unused capacity, multiplied by its
recorded count. Those sums reproduce the idle histograms in the stage certificates
and in the final cap certificate. The parent histogram differs from stage 1. Stage
2 and the final certificate have the same histogram. Rank-1 idle stays 234 in all
four. The histogram belongs to the joint inventory, so this check does not split
out the four V45 width units.

The shipped `ORDER.json` and `DISPATCH.json` have the same bytes as
`research/paired-helper-extension`. The order has 666 calls. The package baseline
order is a different file.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to this width
and chronology reading. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the words, the certificates, both order files
and the predecessor chronology. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/rank7-v45-idle-chronology/verify.py
python3.12 -B research/rank7-v45-idle-chronology/test_verify.py
python3.12 -B scripts/research_package.py --package research/rank7-v45-idle-chronology
```

Both commands finish in under a second.

## Open next questions

The stage-1 idle move includes every joint lowering. Separating the four V45
width drops needs a relaxation on that smaller inventory. The call order itself
does not change.

## Credit

Dugongue supplied the shipped words, the relaxation certificates and the
allocation files. The call order compared here is the one stored in
`research/paired-helper-extension`.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.

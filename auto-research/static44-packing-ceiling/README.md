# Exact packing ceiling for the fixed static44 complex word

**No improved multiplication bound is claimed.** For PR544's fixed local word,
helper widths, nine-stage chain, eight replicas and retained bad-class charge,
every whole-helper packing in the stated model has

```
b < 0.001593251957517.
```

The admitted value is `0.001593245593667524834350`. Even allowing arbitrary
fractional pooling and ignoring chronology and owner identity, the retained
balanced conversion therefore gives

```
kappa < 0.001590717543676681.
```

Compared with PR547's pinned `079c86c` checkpoint, `0.001590711200057236`, the remaining packing headroom is
**less than 6.344e-9 in kappa, or 0.000399%**. This is a scoped reason to seek
another local construction or chain rather than expect a substantial gain from
repacking this word. It does not bound other constructions or integer
multiplication in general.

Run the self-contained, standard-library verifier:

```sh
python -B verify.py /absolute/new/receipt.json
```

The verifier uses no optimizer or network. It regenerates every relaxed packing
pattern, derives stock and demand from pinned PR544 artifacts, and checks a
frozen dual with two independent rational moment engines. Both must prove all
pattern inequalities and a strictly positive exclusion margin. The current
admitted rate and an inflated dual weight are negative controls and must reject.

`CERTIFICATE.json` contains only the excluded endpoint and seven rational dual
weights. Their order is stock ranks `(8,16,32,48)`, then helper widths `(5,8,9)`.
`SOURCES.json` binds the original Git blobs; all inherited engines and notices
are unchanged. `MANIFEST.json` covers every file. See [PROOF.md](PROOF.md).

The model partitions each original idle child into whole helper widths and a
remainder, serving exactly 72 copies of each local helper. Its relaxation drops
integer, call, owner, chart and temporal restrictions. Splitting a remainder
further cannot improve the retained moment at this endpoint. Changed local
programs, helper widths, stage count, replica count, banks, bad-class charges or
outer proofs are outside this ceiling.

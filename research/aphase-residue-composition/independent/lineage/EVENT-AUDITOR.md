# Independent three-bin residue audit

`verify.py` is a standalone standard-library checker. Supply the immutable
PR2848 package and the five candidate files (`ORDER.json`, `DISPATCH.json`,
`FILL.json.gz`, `PROFILE.json`, `CANDIDATE.json`), with a fresh external output:

```sh
python3 -I -S -B verify.py --predecessor /path/to/t248-dirtentry-residue \
  --candidate /path/to/h23-data --out /tmp/fresh-event-audit.json
```

Fourteen predecessor files are authenticated against embedded SHA256 and Git
blob pins at PR2848 head `c50d12e4720cd1fef2b5a65e337e37de9731879a`.
The checker imports or executes no predecessor checker or candidate generator.
It expands the actual source events, including every bridge, and checks all
910,656 roles against open event windows, active data families, unique physical
families, complete helper sets, capacity, nonoverlap and compact prefixes.
The baseline is recounted separately. Only the five declared row changes are
accepted; the order and dispatch must remain byte-identical.

The complete delta is `H23-H16-H5-H2`, with rank mass unchanged. Strict
subadditivity gives a negative delta for every `0<a<1`. A local adaptation of
PR2848's credited rational atanh/Taylor routine brackets the new complex root
and compares the exact full PR2848 claim. This arithmetic is reused methodology,
not an additional independent implementation.

Nine geometry/profile controls bypass only the declared-edit guard, reaching
their named predicates: active family, duplicate physical family, capacity,
overlap, internal gap, strict source window, duplicate helper, missing role and
wrong complete profile. A tenth control rejects an overstated endpoint.
Normal and optimized execution retain all checks.

The event-clock method credits Yiyang/Lyy-iiis's PR2848 independent owner
auditor. Jeremy Kothe's PR2833 supplies the words, provider inventory and source
template; Marius-Paul Dumitrean's PR2843 supplies the T124 allocation ancestry.
The original source notices and license remain pinned and are read from the
predecessor package. New checker code is Apache-2.0, prepared with substantial
OpenAI Codex assistance.

This is a finite geometry/profile/arithmetic audit. Native normalization,
block-norm hypotheses, precision, physical costs and complete modern outer
admission are separate obligations. This receipt alone does not admit a new κ.

# Validation, reproduction and limitations

Base: `2921874911956718fcaaaf9396fe8267b3cfa9f0`. OS-random seed **95** was
drawn at `2026-10-13T17:24:49.071299+00:00`. This is a bounded consolidation
of two fixed archived queries, not a search over additional punctures or
decoder families. Both solver calls finished within the 600-second per-case
limit; no timeout or failed search is presented as an impossibility proof.

The complete canonical receipt is identical on CPython **3.14.4** and
**3.12.3**:

```
ab65ab6dba482fb9c9741f7ff10235c972ed03052197ea1795374fd539a67d84
```

This SHA-256 hashes sorted compact ASCII JSON without a trailing newline.
The secondary run used `/usr/bin/python3.12 -B -O`, a relocated copy of only
this package, read-only files and directories, and an unrelated working
directory. It passed in 4.06 seconds. All guards remain enabled under Python
optimization. No optional producer, numerical or native dependency was present
on the cold-replay path.

Both the new encoder and the original PR620 clause-construction methods
produce these complete deterministic DIMACS hashes:

| Instance | SHA-256 |
| --- | --- |
| c=8 | `39fbb377a7d824bbf1e2c262dc126a7dbeb3ce2df099937182c24db978610246` |
| c=9, unequal to B0 | `69886e262ba3c66c087dc4aa02f0e344f137f8dd9f02566babfb6aea1f64ece1` |

The original numerical geometry module was also run during preparation and
agreed on the pattern and formula. Cold comparison replaces only two unused
optional-library imports in memory and intercepts solver creation. Source
bytes are checked before this execution. The archived README is pinned at
the base; five other consumed PR620 files are byte-identical at both base
and its current head `8f0150e0d0a8a02370907be35cccd3ca69cdd941`.
Later README additions and the separate ADE erratum are outside the audit.

Independent finite checks include:

- Every original formula clause and every one of the **37,044** retained
  proof additions, using **1,409,475** explicit propagation hints.
- All **12,321** entries of a literal positive rank-nine Gram factor. Its
  full CNF extension satisfies every clause except the final disequality.
- All eight undirected forced-zero patterns on three vertices, dimensions
  one and two, with and without the disequality condition. **250** direct
  matrix candidates and **992** factor-assignment/mode cases give exactly
  the same admitted matrix sets. This independently checks the distinction
  between asymmetric factorizations and fitting matrices, including the gauge.
- **16** exhaustive AND/XOR gate truth cases. These test the clauses as
  Boolean formulas, including incorrect output values.
- **15** mathematical/model/proof rejection controls: a negated learned
  unit, omitted/reversed hints, a self reference, reused ID, out-of-range
  variable, missing premise, unsupported RAT/deletion records, missing empty
  conclusion, a false refutation of a satisfiable unit, nonunit/satisfied
  hints, a nonclique gauge and a changed root order. A separate tiny valid
  refutation is accepted as a positive checker control.
- **22** package rejections: all nine retained source files, all seven new
  implementation files, both decoded proofs, three receipt changes and a
  duplicate manifest key. Integer-to-float substitution is rejected.
- Both proof payloads remain accepted after changing gzip compression level
  and timestamp. Cold mathematical equality uses decoded contents, not
  reproducible container headers.

The independent native checker at DRAT-trim commit
`2e3b2dc0ecf938addbd779d42877b6ed69d9a985` accepted both full formulas and
deletion-free proofs. It was compiled with GCC 15.2.0 using
`-D_DEFAULT_SOURCE -std=c99 -DLONGTYPE -O2`. `PRODUCTION.json` records its
outputs, source digest, solver version/statistics and the checked input hashes.
The default Makefile build needed `_DEFAULT_SOURCE` for `getc_unlocked` on
this compiler; no upstream source bytes were edited.

Optional regeneration requires a compiler and an isolated
`python-sat==1.9.dev15` installation. The committed converter source is under
its retained MIT license. For example, after installing that package into
an isolated Python environment and compiling the converter:

```sh
cc -D_DEFAULT_SOURCE -std=c99 -O2 \
  research/p111-minrank-proof-reconciliation/vendor/drat-trim/drat-trim.c \
  -o /tmp/p111-drat-trim
python3 -B research/p111-minrank-proof-reconciliation/produce.py \
  --work /tmp/p111-regenerated --converter /tmp/p111-drat-trim --dimension 8
python3 -B research/p111-minrank-proof-reconciliation/produce.py \
  --work /tmp/p111-regenerated --converter /tmp/p111-drat-trim --dimension 9
```

The producer writes its solver and converter evidence into the supplied work
directory, and preserves a model if a future run unexpectedly reports SAT.
A different solver build can produce a different valid trace; it must be
checked, not compared by compressed bytes alone. The committed proofs already
replay offline and do not need to be regenerated to check the claims.

The proof traces establish propositional unsatisfiability for the bound
formulas. The matrix-to-formula equivalence and gauge justification are written
proofs supported by exhaustive small-domain checks, not proof-assistant
formalizations. The new Python checker is small and independently tested; it
is not itself formally verified. No full multiplication-theorem audit follows.

The result remains confined to the archived root order. PR757/761's separate
supplier-order correction and cost-floor results are credited, not re-proved.
Higher-rank decoders, other punctures, all other PR620 reports, physical
COPY/source access, phases, frames, restoration, hosting, all-size compilation,
precision/tape and analytic transfer remain outside scope or inherited.
The selected frontier and original packages are unchanged.

Final refresh: upstream advanced to
`abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`. All six retained PR620 source
files and the selected record remain byte-identical to the base. PR620's
current head also remains unchanged. The refreshed 758-PR queue through
PR1091 has no competing proof-carrying archived P111 uniqueness result.
PR1084 concerns puncture-dependent costs within a fixed label-decoder model;
PR1077 concerns an eight-term complex decoder, not this asymmetric F2 fitting
class. Neither is a consumed source. `make selected-record-check` passes.
The unrelated repository-wide suite and selected-supplier cold replay were
not run; hosted CI status is reported separately at publication.

Clean patch application passes. New material passes the staged whitespace
check. The full check reports one pre-existing trailing space at line 14 of
the retained `vendor/pr620/geo.py`; it is kept deliberately so the original
source bytes and Git blob remain exact. No source was silently normalized.
